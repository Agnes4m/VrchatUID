from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.api.client import NotLoggedInError, get_client

sv = SV("vrc搜索用户")


@sv.on_command(("vrc搜索用户", "vrcus", "vrcsu"))
async def vrc_search_user(bot: Bot, ev: Event) -> None:
    from ..utils.api.users import search_users

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        client = await get_client(user_id, bot_id)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
        return

    search_term = ev.text.strip()
    if not search_term:
        await bot.send("请输入搜索关键词！\n格式：vrc搜索用户 关键词\n例如：vrc搜索用户 Tom")
        return

    try:
        await bot.send(f"正在搜索用户「{search_term}」...")
        users = [x async for x in search_users(client, search_term, max_size=10)]

        if not users:
            await bot.send(f"未找到与「{search_term}」相关的用户")
            return

        msg = f"【用户搜索结果】找到 {len(users)} 位用户：\n\n"

        for i, user in enumerate(users, 1):
            display_name = getattr(user, "display_name", "Unknown")
            user_id_str = getattr(user, "id", getattr(user, "user_id", ""))
            avatar_url = getattr(user, "avatar_url", "")
            status = getattr(user, "status", "offline")
            status_description = getattr(user, "status_description", "")

            msg += f"{i}. {display_name}\n"
            msg += f"   ID: {user_id_str}\n"
            msg += f"   状态: {status}"
            if status_description:
                msg += f" - {status_description}"
            msg += "\n"
            if avatar_url:
                msg += f"   头像: {avatar_url}\n"
            msg += "\n"

        msg += "发送【添加 序号】发送好友请求\n"
        msg += "发送【好友 序号】查看好友状态\n"
        msg += "发送【详情 序号】查看用户详情"

        await bot.send(msg)
        ev.state["vrc_search_users"] = users

    except Exception as e:
        logger.error(f"搜索用户失败: {e}")
        await bot.send(f"搜索用户失败：{str(e)}")


@sv.on_command(("添加", "add"))
async def vrc_add_friend(bot: Bot, ev: Event) -> None:
    from ..utils.api.users import friend as send_friend_request, get_friend_status

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        client = await get_client(user_id, bot_id)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
        return

    if "vrc_search_users" not in ev.state:
        await bot.send("请先使用【vrc搜索用户】搜索用户")
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送【添加 序号】来添加好友\n例如：添加 1")
        return

    try:
        index = int(text) - 1
        users = ev.state["vrc_search_users"]
        if index < 0 or index >= len(users):
            await bot.send(f"序号超出范围，请发送 1-{len(users)} 之间的数字")
            return

        target_user = users[index]
        target_user_id = getattr(target_user, "id", getattr(target_user, "user_id", ""))

        await bot.send("正在发送好友请求...")

        fq_msg = await get_friend_status(client, target_user_id)

        if fq_msg.is_friend:
            await bot.send("该用户已经是您的好友了")
            return
        if fq_msg.incoming_request and not fq_msg.outgoing_request:
            await bot.send("该用户已经向您发送了好友请求，请先接受")
            return
        if fq_msg.outgoing_request and not fq_msg.incoming_request:
            await bot.send("您已经向该用户发送过好友请求了")
            return

        await send_friend_request(client, target_user_id)
        display_name = getattr(target_user, "display_name", target_user_id)
        await bot.send(f"已成功向 {display_name} 发送好友请求！")

    except Exception as e:
        logger.error(f"添加好友失败: {e}")
        await bot.send(f"添加好友失败：{str(e)}")


@sv.on_command(("好友状态", "friend_status"))
async def vrc_friend_status(bot: Bot, ev: Event) -> None:
    from ..utils.api.users import get_friend_status

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        client = await get_client(user_id, bot_id)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
        return

    if "vrc_search_users" not in ev.state:
        await bot.send("请先使用【vrc搜索用户】搜索用户")
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送【好友 序号】来查看好友状态\n例如：好友 1")
        return

    try:
        index = int(text) - 1
        users = ev.state["vrc_search_users"]
        if index < 0 or index >= len(users):
            await bot.send(f"序号超出范围，请发送 1-{len(users)} 之间的数字")
            return

        target_user = users[index]
        target_user_id = getattr(target_user, "id", getattr(target_user, "user_id", ""))

        fq_msg = await get_friend_status(client, target_user_id)
        display_name = getattr(target_user, "display_name", target_user_id)

        if fq_msg.is_friend:
            await bot.send(f"{display_name} 是您的好友")
            return
        if fq_msg.incoming_request and not fq_msg.outgoing_request:
            await bot.send(f"{display_name} 向您发送了好友请求")
            return
        if fq_msg.outgoing_request and not fq_msg.incoming_request:
            await bot.send(f"您已向 {display_name} 发送了好友请求，等待对方接受")
            return
        await bot.send(f"{display_name} 与您还不是好友关系")

    except Exception as e:
        logger.error(f"查询好友状态失败: {e}")
        await bot.send(f"查询好友状态失败：{str(e)}")
