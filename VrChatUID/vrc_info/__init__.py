from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api import ActionResult, api_action
from ..utils.api.client import get_client_or_notify_with_retry as get_client_or_notify
from ..utils.api.friend import get_all_friends
from ..utils.api.world import search_worlds
from ..utils.render import build_friend_section, build_world_card, render_template

sv = SV("信息")


@sv.on_command(("好友", "fl"))
@api_action("获取好友列表")
async def vrc_friend_list(bot: Bot, ev: Event) -> ActionResult:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return ActionResult.info("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")

    await bot.send("正在获取好友列表...")
    friends = list(get_all_friends(client, max_size=100))

    if not friends:
        return ActionResult.info("您的好友列表为空")

    online_friends = []
    web_friends = []
    offline_friends = []

    for friend in friends:
        # VRChat 用户的 `status` 字段是用户自定义文案（"join me" / "working" 等），
        # 不能作为在线判定；正确判定依据是 `platform` 字段：
        #   - platform 为空或 "unknownplatform" → 离线
        #   - platform == "web"                  → Web 在线
        #   - 其余（standalonewindows / android / ios / standalonequest 等）→ 正常在线
        platform = (getattr(friend, "platform", "") or "").lower()
        if not platform or platform == "unknownplatform":
            offline_friends.append(friend)
        elif platform == "web":
            web_friends.append(friend)
        else:
            online_friends.append(friend)

    fallback = f"【好友列表】共 {len(friends)} 位好友\n\n"
    if online_friends:
        fallback += f"【在线】{len(online_friends)} 位\n"
        for i, friend in enumerate(online_friends[:10], 1):
            fallback += f"  {i}. {getattr(friend, 'display_name', 'Unknown')}\n"
        if len(online_friends) > 10:
            fallback += f"  ... 还有 {len(online_friends) - 10} 位在线好友\n"
        fallback += "\n"
    if web_friends:
        fallback += f"【Web 在线】{len(web_friends)} 位\n"
        for i, friend in enumerate(web_friends[:10], 1):
            fallback += f"  {i}. {getattr(friend, 'display_name', 'Unknown')}\n"
        if len(web_friends) > 10:
            fallback += f"  ... 还有 {len(web_friends) - 10} 位 Web 在线好友\n"
        fallback += "\n"
    if offline_friends:
        fallback += f"【离线】{len(offline_friends)} 位\n"
        for i, friend in enumerate(offline_friends[:10], 1):
            fallback += f"  {i}. {getattr(friend, 'display_name', 'Unknown')}\n"
        if len(offline_friends) > 10:
            fallback += f"  ... 还有 {len(offline_friends) - 10} 位离线好友\n"

    try:
        online_section = build_friend_section("在线", online_friends, start_idx=1)
        web_section = build_friend_section("Web 在线", web_friends, start_idx=len(online_friends) + 1)
        offline_section = build_friend_section(
            "离线", offline_friends, start_idx=len(online_friends) + len(web_friends) + 1
        )
        image_bytes = await render_template(
            "friend_list.html",
            total_count=len(friends),
            online_section=online_section,
            web_section=web_section,
            offline_section=offline_section,
        )

        await bot.send(image_bytes)
    except Exception as e:
        logger.warning(f"好友列表图片渲染失败，降级到文本: {e}")
        await bot.send(fallback)

    return ActionResult.success()


@sv.on_command(("搜索世界", "ws", "sw"))
@api_action("搜索世界")
async def vrc_search_world(bot: Bot, ev: Event) -> ActionResult:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return ActionResult.info("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")

    search_term = ev.text.strip()
    if not search_term:
        return ActionResult.warn("请输入搜索关键词！\n格式：vrc搜索世界 关键词\n例如：vrc搜索世界 Japan")

    await bot.send(f"正在搜索「{search_term}」...")
    worlds = list(search_worlds(client, search_term))

    if not worlds:
        return ActionResult.info(f"未找到与「{search_term}」相关的世界")

    fallback = f"【世界搜索结果】找到 {len(worlds)} 个世界：\n\n"
    for i, world in enumerate(worlds, 1):
        fallback += (
            f"{i}. {getattr(world, 'name', 'Unknown')}\n"
            f"   作者：{getattr(world, 'author_name', 'Unknown')}\n"
            f"   在线：{getattr(world, 'occupants', 0)} 人 | 收藏：{getattr(world, 'favorites', 0)}\n"
            f"   ID：{getattr(world, 'id', '')}\n\n"
        )

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

    return ActionResult.success()
