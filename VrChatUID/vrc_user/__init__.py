from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.data_store import get_res_path

from ..utils.api.client import (
    # LoginInfo,
    NotLoggedInError,
    TwoFactorAuthError,
    get_login_info,
    remove_login_info,
    login_via_password,
    get_current_user_info,
)
from ..utils.database.models import VrChatBind

sv = SV("vrc登录")
DATA_DIR = get_res_path() / "vrchat"
DATA_DIR.mkdir(parents=True, exist_ok=True)


async def _complete_login(
    bot: Bot, user_id: str, bot_id: str, username: str, password: str, current_user
) -> None:
    """完成登录，保存用户信息"""
    # 更新数据库
    await VrChatBind.insert_data(
        user_id=user_id,
        bot_id=bot_id,
        uid=username,
        vrc_username=username,
        vrc_password=password,
        vrc_display_name=current_user.display_name,
    )

    await bot.send(
        f"✅ 登录成功！\n\n"
        f"显示名称: {current_user.display_name}\n"
        f"用户ID: {current_user.id}\n\n"
        f"现在您可以使用以下功能：\n"
        f"• vrc好友 - 查看好友列表\n"
        f"• vrc搜索用户 - 搜索VRChat用户\n"
        f"• vrc搜索世界 - 搜索世界"
    )


@sv.on_command(("vrc登录", "vrcl"))
async def vrc_login(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    text = ev.text.strip()
    if not text:
        await bot.send(
            "请发送用户名和密码，格式：\nvrc登录 用户名 密码\n\n"
            "例如：vrc登录 example@email.com mypassword\n\n"
            "注意：VRChat需要使用邮箱+密码登录"
        )
        return

    parts = text.split()
    if len(parts) != 2:
        await bot.send(
            "格式错误！请发送：\nvrc登录 用户名 密码\n\n例如：vrc登录 example@email.com mypassword"
        )
        return

    username, password = parts

    try:
        await bot.send("正在验证登录信息...")

        # 直接调用API进行登录
        current_user = await login_via_password(user_id, bot_id, username, password)

        # 登录成功
        await _complete_login(bot, user_id, bot_id, username, password, current_user)

    except TwoFactorAuthError as e:
        # 2FA验证 - 使用receive_resp等待用户输入验证码
        logger.info("检测到2FA验证，等待用户输入验证码")

        resp = await bot.receive_resp(
            "⚠️ 需要2FA验证\n\n请查收验证码后直接回复验证码（5-6位数字）\n超时时间：60秒",
            timeout=60,
        )

        if resp is None:
            await bot.send("❌ 验证码输入超时，请重新发送【vrc登录 用户名 密码】")
            return

        verify_code = resp.text.strip()

        # 验证码格式检查
        if not verify_code.isdigit():
            await bot.send("❌ 验证码格式错误，请输入纯数字验证码")
            return

        try:
            await bot.send("正在验证验证码...")

            # 调用2FA验证函数
            current_user = await e.verify_func(verify_code)

            # 登录成功
            await _complete_login(
                bot, user_id, bot_id, username, password, current_user
            )

        except Exception as verify_error:
            logger.error(f"VRChat 验证码验证失败: {verify_error}")
            await bot.send("❌ 验证码验证失败，请检查验证码是否正确后重试")

    except Exception as e:
        error_msg = str(e)
        # 错误信息输出到终端
        logger.error(f"VRChat 登录失败: {e}")
        if "401" in error_msg or "Unauthorized" in error_msg:
            await bot.send("❌ 登录失败：用户名或密码错误\n\n请检查您的账号信息后重试")
        else:
            await bot.send("❌ 登录失败，请查看终端日志")


@sv.on_fullmatch(("vrc注销", "vrc退出登录"))
async def vrc_logout(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        remove_login_info(user_id, bot_id)
    except Exception:
        pass

    await VrChatBind.delete_data(user_id, bot_id)
    await bot.send("已成功注销 VRChat 账号")


@sv.on_fullmatch(("vrc我的信息", "vrc状态"))
async def vrc_my_info(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        login_info = get_login_info(user_id, bot_id)

        # 获取最新用户信息
        current_user = await get_current_user_info(user_id, bot_id)

        msg = "【VRChat 账号信息】\n\n"
        msg += f"用户名：{login_info.username}\n"

        if current_user:
            msg += f"显示名称：{current_user.display_name}\n"
            msg += f"用户ID：{current_user.id}\n"
            msg += "状态：在线 ✅\n"
        else:
            msg += f"显示名称：{login_info.display_name or '未获取'}\n"
            msg += f"用户ID：{login_info.user_id or '未获取'}\n"
            msg += "状态：离线/已过期 ❌\n"
            msg += "\n提示：登录状态可能已过期，请重新登录"

        await bot.send(msg)

    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
