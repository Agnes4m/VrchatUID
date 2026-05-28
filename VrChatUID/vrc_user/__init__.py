from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.data_store import get_res_path

from ..utils.api.client import (
    LoginInfo,
    NotLoggedInError,
    # get_client,
    get_login_info,
    save_login_info,
)
from ..utils.database.models import VrChatBind

sv = SV("vrc登录")
DATA_DIR = get_res_path() / "vrchat"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@sv.on_command(("vrc登录", "vrcl"))
async def vrc_login(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        login_info = get_login_info(user_id, bot_id)
        if login_info.username:
            await bot.send(
                f"您已登录账号: {login_info.display_name or login_info.username}\n如需重新登录，请先发送【vrc注销】"
            )
            return
    except NotLoggedInError:
        pass

    text = ev.text.strip()
    if not text:
        await bot.send("请发送用户名和密码，格式：\nvrc登录 用户名 密码\n\n例如：vrc登录 example@email.com mypassword")
        return

    parts = text.split()
    if len(parts) != 2:
        await bot.send("格式错误！请发送：\nvrc登录 用户名 密码\n\n例如：vrc登录 example@email.com mypassword")
        return

    username, password = parts

    try:
        await bot.send("正在登录...")
        save_login_info(user_id, bot_id, LoginInfo(username=username, password=password))

        await VrChatBind.insert_data(
            user_id=user_id,
            bot_id=bot_id,
            uid=username,
            vrc_username=username,
            vrc_password=password,
        )

        await bot.send(f"登录信息已保存！\n用户名：{username}\n\n注意：如果VRChat需要验证码登录，请使用完整登录流程。")

    except Exception as e:
        logger.error(f"VRChat 登录失败: {e}")
        await bot.send(f"登录失败：{str(e)}")


@sv.on_fullmatch(("vrc注销", "vrc退出登录"))
async def vrc_logout(bot: Bot, ev: Event) -> None:
    from ..utils.api.client import remove_login_info

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        remove_login_info(user_id, bot_id)
    except Exception:
        pass

    await VrChatBind.delete_data(user_id, bot_id)
    await bot.send("已成功注销 VRChat 账号")
