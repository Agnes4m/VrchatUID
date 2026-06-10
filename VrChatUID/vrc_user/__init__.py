from typing import Optional

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api._helpers import log_api_response
from ..utils.api.client import (
    NotLoggedInError,
    TwoFactorAuthError,
    login_via_password,
)
from ..utils.database import (
    list_binds,
    remove_bind,
    switch_uid,
)

sv = SV("vrc登录")

MSG_PREFIX = "[VRC]"


def _response_msg(retcode: int, success_msg: str = "", uid: str = "") -> str:
    """根据返回码获取响应消息"""
    if retcode == 0:
        return success_msg
    if retcode == -1:
        return f"{MSG_PREFIX} 没有找到该绑定记录"
    if retcode == -2:
        return f"{MSG_PREFIX} 账号 {uid} 不在已绑定列表中"
    if retcode == -3:
        return f"{MSG_PREFIX} 当前只绑定了一个账号，无法切换"
    return f"{MSG_PREFIX} 操作失败，错误码: {retcode}"


async def _login_account(bot: Bot, ev: Event):
    """执行登录流程，返回 (success, vrc_uid, message)"""
    user_id = ev.user_id
    bot_id = ev.bot_id

    text = ev.text.strip()
    if not text:
        await bot.send(
            "请发送用户名和密码，格式：\n登录 用户名 密码\n\n"
            "例如：登录 example@email.com mypassword\n\n"
            "注意：VRChat需要使用邮箱+密码登录"
        )
        return None

    parts = text.split()
    if len(parts) != 2:
        await bot.send("格式错误！请发送：\n登录 用户名 密码\n\n例如：登录 example@email.com mypassword")
        return None

    username, password = parts

    async def _do_login(login_func) -> dict | None:
        try:
            await bot.send("正在验证登录信息...")
            current_user = await login_func()
            if not current_user:
                return None
            log_api_response("_do_login.current_user", current_user)
            vrc_uid = str(getattr(current_user, "id", "") or "")
            display_name = str(getattr(current_user, "display_name", "") or "")
            # 注意：client.py 的 _save_user_info 已自动调用 save_credentials 写入数据库与 cookie 文件
            # 这里不再重复调用，避免 double-save
            return {
                "vrc_uid": vrc_uid,
                "display_name": display_name,
            }
        except TwoFactorAuthError as e:
            resp = await bot.receive_resp(
                "⚠️ 需要2FA验证\n\n请查收验证码后直接回复验证码（5-6位数字）\n超时时间：60秒",
                timeout=60,
            )
            if resp is None:
                await bot.send("❌ 验证码输入超时，请重新发送【登录 用户名 密码】")
                return None
            verify_code = resp.text.strip()
            if not verify_code.isdigit():
                await bot.send("❌ 验证码格式错误，请输入纯数字验证码")
                return None
            try:
                await bot.send("正在验证验证码...")
                current_user = await e.verify_func(verify_code)
                if not current_user:
                    return None
                log_api_response("_do_login.verify_two_fa", current_user)
                vrc_uid = str(getattr(current_user, "id", "") or "")
                display_name = str(getattr(current_user, "display_name", "") or "")
                # 2FA 路径同样由 client.py 的 verify_two_fa 自动保存
                return {"vrc_uid": vrc_uid, "display_name": display_name}
            except Exception as verify_error:
                logger.error(f"VRChat 验证码验证失败: {verify_error}")
                await bot.send("❌ 验证码验证失败，请检查验证码是否正确后重试")
                return None
        except Exception as exc:
            error_msg = str(exc)
            logger.error(f"VRChat 登录失败: {exc}")
            if "401" in error_msg or "Unauthorized" in error_msg:
                await bot.send("❌ 登录失败：用户名或密码错误\n\n请检查您的账号信息后重试")
            else:
                await bot.send("❌ 登录失败，请查看终端日志")
            return None

    return await _do_login(lambda: login_via_password(user_id, bot_id, username, password))


@sv.on_command(
    (
        "登录",
        "绑定",
        "切换",
        "删除",
    ),
    block=True,
)
async def vrc_account(bot: Bot, ev: Event):
    """统一处理登录/绑定/切换/删除账号（参考 DeltaUID 写法）"""
    logger.info(f"{MSG_PREFIX} 开始执行[账号管理]")
    user_id = ev.user_id
    text = ev.text.strip()
    logger.info(f"{MSG_PREFIX} UserID: {user_id}")

    if "登录" in ev.command:
        result = await _login_account(bot, ev)
        if result is None:
            return
        vrc_uid = result["vrc_uid"]
        display_name = result["display_name"]
        binds = await list_binds(user_id, ev.bot_id)
        binds_text = "、".join(binds) if binds else vrc_uid
        await bot.send(
            f"✅ 登录成功！\n\n"
            f"显示名称: {display_name}\n"
            f"用户ID: {vrc_uid}\n\n"
            f"已绑定账号: {binds_text}\n\n"
            f"使用【切换 <序号/uid>】可在多账号间切换\n"
            f"使用【我的信息】查看当前账号"
        )

    elif "绑定" in ev.command:
        # 绑定模式：从已有凭证中获取绑定的账号
        binds = await list_binds(user_id, ev.bot_id)
        if not binds:
            await bot.send(f"{MSG_PREFIX} 您尚未登录任何账号，请先使用【登录 用户名 密码】")
            return
        if len(binds) == 1:
            await bot.send(f"{MSG_PREFIX} 您当前只绑定了 1 个账号：{binds[0]}")
            return
        await bot.send(f"{MSG_PREFIX} 已绑定账号: {', '.join(binds)}\n使用【切换 <序号/uid>】切换当前账号")

    elif "切换" in ev.command:
        if not text:
            binds = await list_binds(user_id, ev.bot_id)
            if not binds:
                await bot.send(f"{MSG_PREFIX} 您尚未绑定任何 VRChat 账号")
                return
            if len(binds) == 1:
                await bot.send(f"{MSG_PREFIX} 您当前只绑定了 1 个账号：{binds[0]}\n如需切换请先登录其他账号")
                return
            msg = "【已绑定的 VRChat 账号】\n\n"
            for i, uid in enumerate(binds, 1):
                msg += f"{i}. {uid}\n"
            msg += "\n发送【切换 <序号/uid>】切换账号"
            await bot.send(msg)
            return

        binds = await list_binds(user_id, ev.bot_id)
        target = text

        if target.isdigit() and 1 <= int(target) <= len(binds):
            target = binds[int(target) - 1]

        if target not in binds:
            await bot.send(f"{MSG_PREFIX} 未找到绑定的账号: {target}\n当前已绑定: {', '.join(binds)}")
            return

        retcode = await switch_uid(user_id, ev.bot_id, target)
        await bot.send(_response_msg(retcode, f"✅ 已切换到账号: {target}", target))

    elif "删除" in ev.command:
        target = text
        if not target:
            current = await list_binds(user_id, ev.bot_id)
            if not current:
                await bot.send(f"{MSG_PREFIX} 您尚未绑定任何 VRChat 账号")
                return
            target = current[0]

        retcode = await remove_bind(user_id, ev.bot_id, target)
        await bot.send(_response_msg(retcode, f"✅ 已解绑账号: {target}", target))


@sv.on_fullmatch(("注销", "退出登录"))
async def vrc_clear_all_binds(bot: Bot, ev: Event) -> None:
    """注销所有 VRChat 账号"""
    from ..utils.database import clear_all_binds

    await clear_all_binds(ev.user_id, ev.bot_id)
    await bot.send(f"{MSG_PREFIX} 已成功注销所有 VRChat 账号")


@sv.on_fullmatch(("我的信息", "状态", "账号列表"))
async def vrc_my_info(bot: Bot, ev: Event) -> None:
    """查看当前账号与已绑定列表"""
    from ..utils.api.client import get_client
    from ..utils.database import get_user_credentials

    user_id = ev.user_id
    bot_id = ev.bot_id

    cred = await get_user_credentials(user_id, bot_id)
    if cred is None:
        await bot.send("您还没有登录 VRChat！请先发送【登录 用户名 密码】")
        return

    binds = await list_binds(user_id, bot_id)
    current = cred.vrc_uid

    # 尝试通过 client 获取最新信息
    try:
        client = await get_client(user_id, bot_id)
        from vrchatapi.api import AuthenticationApi

        api = AuthenticationApi(client)
        current_user = await __import__("asyncio").to_thread(api.get_current_user)
        display_name = getattr(current_user, "display_name", cred.display_name or "未获取")
        online_status = "在线 ✅"
    except Exception:
        display_name = cred.display_name or "未获取"
        online_status = "离线/已过期 ❌"

    msg = "【VRChat 账号信息】\n\n"
    msg += f"当前账号: {display_name}\n"
    msg += f"用户ID: {current}\n"
    msg += f"状态: {online_status}\n"
    msg += f"邮箱: {cred.username}\n\n"

    if len(binds) > 1:
        msg += f"已绑定账号: {', '.join(binds)}\n"
        msg += f"（当前为: {current}）\n"
        msg += "\n使用【切换】切换其他账号"
    else:
        msg += "您当前只绑定了 1 个账号"

    await bot.send(msg)
