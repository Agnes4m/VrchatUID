from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api import ActionResult, api_action
from ..utils.api.client import get_client_or_notify_with_retry as get_client_or_notify
from ..utils.api.users import friend as send_friend_request
from ..utils.api.users import get_friend_status, search_users
from ..utils.render import build_user_card, render_template
from ..utils.session_state import get_state, has_state, set_state

sv = SV("搜索用户")


@sv.on_command(("搜索用户", "us", "su"))
@api_action("搜索用户")
async def vrc_search_user(bot: Bot, ev: Event) -> ActionResult:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return ActionResult.info("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")

    search_term = ev.text.strip()
    if not search_term:
        return ActionResult.warn("请输入搜索关键词！\n格式：vrc搜索用户 关键词\n例如：vrc搜索用户 Tom")

    await bot.send(f"正在搜索用户「{search_term}」...")
    users = list(search_users(client, search_term))

    if not users:
        return ActionResult.info(f"未找到与「{search_term}」相关的用户")

    fallback = f"【用户搜索结果】找到 {len(users)} 位用户：\n\n"
    for i, user in enumerate(users, 1):
        display_name = getattr(user, "display_name", "Unknown")
        user_id_str = getattr(user, "id", getattr(user, "user_id", ""))
        status = getattr(user, "status", "offline")
        status_description = getattr(user, "status_description", "")

        fallback += f"{i}. {display_name}\n"
        fallback += f"   ID: {user_id_str}\n"
        fallback += f"   状态: {status}"
        if status_description:
            fallback += f" - {status_description}"
        fallback += "\n\n"

    fallback += "发送【添加 序号】发送好友请求\n"
    fallback += "发送【好友 序号】查看好友状态\n"
    fallback += "发送【详情 序号】查看用户详情"

    try:
        user_cards = "".join(build_user_card(i, u) for i, u in enumerate(users, 1))
        image_bytes = await render_template(
            "user_search.html",
            keyword=search_term,
            total_count=len(users),
            user_cards=user_cards,
        )
        await bot.send(image_bytes)
    except Exception as e:
        logger.warning(f"用户搜索图片渲染失败，降级到文本: {e}")
        await bot.send(fallback)

    set_state(ev.session_id, "_search_users", users)
    return ActionResult.success()


@sv.on_command(("添加", "add"))
@api_action("添加好友")
async def vrc_add_friend(bot: Bot, ev: Event) -> ActionResult:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return ActionResult.info("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")

    if not has_state(ev.session_id, "_search_users"):
        return ActionResult.warn("请先使用【vrc搜索用户】搜索用户")

    text = ev.text.strip()
    if not text:
        return ActionResult.warn("请发送【添加 序号】来添加好友\n例如：添加 1")

    index = int(text) - 1
    users = get_state(ev.session_id, "_search_users")
    if index < 0 or index >= len(users):
        return ActionResult.warn(f"序号超出范围，请发送 1-{len(users)} 之间的数字")

    target_user = users[index]
    target_user_id = getattr(target_user, "id", getattr(target_user, "user_id", ""))

    await bot.send("正在发送好友请求...")

    fq_msg = await get_friend_status(client, target_user_id)

    if fq_msg.is_friend:
        return ActionResult.info("该用户已经是您的好友了")
    if fq_msg.incoming_request and not fq_msg.outgoing_request:
        return ActionResult.info("该用户已经向您发送了好友请求，请先接受")
    if fq_msg.outgoing_request and not fq_msg.incoming_request:
        return ActionResult.info("您已经向该用户发送过好友请求了")

    await send_friend_request(client, target_user_id)
    display_name = getattr(target_user, "display_name", target_user_id)
    await bot.send(f"已成功向 {display_name} 发送好友请求！")
    return ActionResult.success()


@sv.on_command(("好友状态", "friend_status"))
@api_action("查询好友状态")
async def vrc_friend_status(bot: Bot, ev: Event) -> ActionResult:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return ActionResult.info("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")

    if not has_state(ev.session_id, "_search_users"):
        return ActionResult.warn("请先使用【vrc搜索用户】搜索用户")

    text = ev.text.strip()
    if not text:
        return ActionResult.warn("请发送【好友 序号】来查看好友状态\n例如：好友 1")

    index = int(text) - 1
    users = get_state(ev.session_id, "_search_users")
    if index < 0 or index >= len(users):
        return ActionResult.warn(f"序号超出范围，请发送 1-{len(users)} 之间的数字")

    target_user = users[index]
    target_user_id = getattr(target_user, "id", getattr(target_user, "user_id", ""))

    fq_msg = await get_friend_status(client, target_user_id)
    display_name = getattr(target_user, "display_name", target_user_id)

    if fq_msg.is_friend:
        return ActionResult.info(f"{display_name} 是您的好友")
    if fq_msg.incoming_request and not fq_msg.outgoing_request:
        return ActionResult.info(f"{display_name} 向您发送了好友请求")
    if fq_msg.outgoing_request and not fq_msg.incoming_request:
        return ActionResult.info(f"您已向 {display_name} 发送了好友请求，等待对方接受")
    return ActionResult.info(f"{display_name} 与您还不是好友关系")
