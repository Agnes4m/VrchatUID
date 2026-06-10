from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.client import get_client_or_notify
from ..utils.api.friend import get_all_friends
from ..utils.api.world import search_worlds
from ..utils.render import build_friend_section, build_world_card, render_template

sv = SV("信息")


@sv.on_command(("好友", "fl"))
async def vrc_friend_list(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在获取好友列表...")
        friends = list(get_all_friends(client, max_size=50))

        if not friends:
            await bot.send("您的好友列表为空")
            return

        online_friends = []
        offline_friends = []

        for friend in friends:
            status = getattr(friend, "status", "offline")
            if status == "online":
                online_friends.append(friend)
            else:
                offline_friends.append(friend)

        # 构建降级文本
        fallback = f"【好友列表】共 {len(friends)} 位好友\n\n"
        if online_friends:
            fallback += f"【在线】{len(online_friends)} 位\n"
            for i, friend in enumerate(online_friends[:10], 1):
                fallback += f"  {i}. {getattr(friend, 'display_name', 'Unknown')}\n"
            if len(online_friends) > 10:
                fallback += f"  ... 还有 {len(online_friends) - 10} 位在线好友\n"
            fallback += "\n"
        if offline_friends:
            fallback += f"【离线】{len(offline_friends)} 位\n"
            for i, friend in enumerate(offline_friends[:10], 1):
                fallback += f"  {i}. {getattr(friend, 'display_name', 'Unknown')}\n"
            if len(offline_friends) > 10:
                fallback += f"  ... 还有 {len(offline_friends) - 10} 位离线好友\n"

        # 渲染图片
        try:
            online_section = build_friend_section("在线", online_friends, start_idx=1)
            offline_section = build_friend_section("离线", offline_friends, start_idx=len(online_friends) + 1)
            image_bytes = await render_template(
                "friend_list.html",
                total_count=len(friends),
                online_section=online_section,
                offline_section=offline_section,
            )

            await bot.send(image_bytes)
        except Exception as e:
            logger.warning(f"好友列表图片渲染失败，降级到文本: {e}")
            await bot.send(fallback)

    except Exception as e:
        logger.error(f"获取好友列表失败: {e}")
        await bot.send(f"获取好友列表失败：{str(e)}")


@sv.on_command(("搜索世界", "ws", "sw"))
async def vrc_search_world(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    search_term = ev.text.strip()
    if not search_term:
        await bot.send("请输入搜索关键词！\n格式：vrc搜索世界 关键词\n例如：vrc搜索世界 Japan")
        return

    try:
        await bot.send(f"正在搜索「{search_term}」...")
        worlds = list(search_worlds(client, search_term))

        if not worlds:
            await bot.send(f"未找到与「{search_term}」相关的世界")
            return

        # 构建降级文本
        fallback = f"【世界搜索结果】找到 {len(worlds)} 个世界：\n\n"
        for i, world in enumerate(worlds, 1):
            fallback += (
                f"{i}. {getattr(world, 'name', 'Unknown')}\n"
                f"   作者：{getattr(world, 'author_name', 'Unknown')}\n"
                f"   在线：{getattr(world, 'occupants', 0)} 人 | 收藏：{getattr(world, 'favorites', 0)}\n"
                f"   ID：{getattr(world, 'id', '')}\n\n"
            )

        # 渲染图片
        try:
            world_cards = "".join(build_world_card(i, w) for i, w in enumerate(worlds, 1))
            image_bytes = await render_template(
                "world_search.html",
                keyword=search_term,
                total_count=len(worlds),
                world_cards=world_cards,
            )

            await bot.send(image_bytes)
        except Exception as e:
            logger.warning(f"世界搜索图片渲染失败，降级到文本: {e}")
            await bot.send(fallback)

    except Exception as e:
        logger.error(f"搜索世界失败: {e}")
        await bot.send(f"搜索世界失败：{str(e)}")
