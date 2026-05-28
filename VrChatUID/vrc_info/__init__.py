from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.api.client import NotLoggedInError, get_client

# from ..utils.database.models import VrChatBind

sv = SV("vrc信息")


@sv.on_fullmatch(("vrc我的信息", "vrc状态"))
async def vrc_my_info(bot: Bot, ev: Event) -> None:
    from ..utils.api.client import get_login_info

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        login_info = get_login_info(user_id, bot_id)
        msg = "【VRChat 账号信息】\n\n"
        msg += f"用户名：{login_info.username}\n"
        msg += f"显示名称：{login_info.display_name or '未设置'}\n"
        msg += f"用户ID：{login_info.user_id or '未获取'}\n"
        await bot.send(msg)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")


@sv.on_command(("vrc好友", "vrcfl"))
async def vrc_friend_list(bot: Bot, ev: Event) -> None:
    from ..utils.api.friend import get_all_friends

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        client = await get_client(user_id, bot_id)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
        return

    try:
        await bot.send("正在获取好友列表...")
        friends = [x async for x in get_all_friends(client, max_size=50)]

        if not friends:
            await bot.send("您的好友列表为空")
            return

        msg = f"【好友列表】共 {len(friends)} 位好友：\n\n"

        online_friends = []
        offline_friends = []

        for friend in friends:
            status = getattr(friend, "status", "offline")
            if status == "online":
                online_friends.append(friend)
            else:
                offline_friends.append(friend)

        if online_friends:
            msg += f"【在线】{len(online_friends)} 位\n"
            for i, friend in enumerate(online_friends[:10], 1):
                name = getattr(friend, "display_name", "Unknown")
                msg += f"  {i}. {name}\n"
            if len(online_friends) > 10:
                msg += f"  ... 还有 {len(online_friends) - 10} 位在线好友\n"
            msg += "\n"

        if offline_friends:
            msg += f"【离线】{len(offline_friends)} 位\n"
            for i, friend in enumerate(offline_friends[:10], 1):
                name = getattr(friend, "display_name", "Unknown")
                msg += f"  {i}. {name}\n"
            if len(offline_friends) > 10:
                msg += f"  ... 还有 {len(offline_friends) - 10} 位离线好友\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取好友列表失败: {e}")
        await bot.send(f"获取好友列表失败：{str(e)}")


@sv.on_command(("vrc搜索世界", "vrcws", "vrcsw"))
async def vrc_search_world(bot: Bot, ev: Event) -> None:
    from ..utils.api.world import search_worlds

    user_id = ev.user_id
    bot_id = ev.bot_id

    try:
        client = await get_client(user_id, bot_id)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
        return

    search_term = ev.text.strip()
    if not search_term:
        await bot.send("请输入搜索关键词！\n格式：vrc搜索世界 关键词\n例如：vrc搜索世界 Japan")
        return

    try:
        await bot.send(f"正在搜索「{search_term}」...")
        worlds = [x async for x in search_worlds(client, search_term, max_size=10)]

        if not worlds:
            await bot.send(f"未找到与「{search_term}」相关的世界")
            return

        msg = f"【世界搜索结果】找到 {len(worlds)} 个世界：\n\n"

        for i, world in enumerate(worlds, 1):
            name = getattr(world, "name", "Unknown")
            author = getattr(world, "author_name", "Unknown")
            occupants = getattr(world, "occupants", 0)
            favorites = getattr(world, "favorites", 0)
            world_id = getattr(world, "id", "")

            msg += f"{i}. {name}\n"
            msg += f"   作者：{author}\n"
            msg += f"   在线：{occupants} 人 | 收藏：{favorites}\n"
            msg += f"   ID：{world_id}\n\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"搜索世界失败: {e}")
        await bot.send(f"搜索世界失败：{str(e)}")
