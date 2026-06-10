from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.client import get_client_or_notify
from ..utils.api.notifications import (
    accept_friend_request,
    delete_notification,
    get_notifications,
    mark_notification_as_read,
)
from ..utils.render import build_notification_card, render_template
from ..utils.session_state import get_state, has_state, set_state

sv = SV("通知")


@sv.on_command(("显示通知", "sn", "通知"))
async def vrc_show_notifications(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    n = 60
    if text and text.isdigit():
        num = int(text)
        if 0 < num <= 100:
            n = num

    try:
        await bot.send("正在获取通知列表...")
        notifications = list(get_notifications(client, n=n))

        if not notifications:
            await bot.send("没有通知")
            return

        set_state(ev.session_id, "_notifications", notifications)

        friend_requests = []
        other_notifications = []

        for i, notif in enumerate(notifications[:30], 1):
            notif_type = getattr(notif, "type", "unknown")
            if notif_type == "friendRequest":
                friend_requests.append((i, notif))
            else:
                other_notifications.append((i, notif))

        # 降级文本
        fallback = f"【通知列表】共 {len(notifications)} 条通知：\n\n"
        if friend_requests:
            fallback += f"【好友请求】{len(friend_requests)} 条\n"
            for idx, req in friend_requests[:10]:
                sender_name = getattr(req, "sender_username", getattr(req, "sender_display_name", "Unknown"))
                sender_id = getattr(req, "sender_user_id", "")
                created_at = getattr(req, "created_at", "")
                fallback += f"  {idx}. {sender_name}\n"
                fallback += f"     ID: {sender_id}\n"
                fallback += f"     时间: {created_at}\n\n"

        if other_notifications:
            fallback += f"【其他通知】{len(other_notifications)} 条\n"
            for idx, notif in other_notifications[:10]:
                notif_type = getattr(notif, "type", "unknown")
                message = getattr(notif, "message", "")[:30]
                created_at = getattr(notif, "created_at", "")
                fallback += f"  {idx}. [{notif_type}] {message}...\n"
                fallback += f"     时间: {created_at}\n\n"

        if len(notifications) > 30:
            fallback += f"... 还有 {len(notifications) - 30} 条通知\n"

        fallback += "\n发送【接受 序号】接受好友请求\n"
        fallback += "发送【忽略 序号】忽略好友请求\n"
        fallback += "发送【删除 序号】删除通知"

        # 渲染图片
        try:
            request_section = (
                f'<div class="section-header"><span class="section-title">好友请求</span>'
                f'<span class="section-count">{len(friend_requests)} 条</span></div>'
                f'<div class="grid">{"".join(build_notification_card(i, n) for i, n in friend_requests)}</div>'
                if friend_requests
                else ""
            )
            other_section = (
                f'<div class="section-header"><span class="section-title">其他通知</span>'
                f'<span class="section-count">{len(other_notifications)} 条</span></div>'
                f'<div class="grid">{"".join(build_notification_card(i, n) for i, n in other_notifications)}</div>'
                if other_notifications
                else ""
            )
            image_bytes = await render_template(
                "notification.html",
                total_count=len(notifications),
                request_section=request_section,
                other_section=other_section,
            )
            await bot.send(image_bytes)
        except Exception as e:
            logger.warning(f"通知列表图片渲染失败，降级到文本: {e}")
            await bot.send(fallback)

    except Exception as e:
        logger.error(f"获取通知列表失败: {e}")
        await bot.send(f"获取通知列表失败：{str(e)}")


@sv.on_command(("接受", "accept"))
async def vrc_accept_friend_request(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    if not has_state(ev.session_id, "_notifications"):
        await bot.send("请先使用【vrc显示通知】查看通知列表")
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送【接受 序号】来接受好友请求\n例如：接受 1")
        return

    try:
        index = int(text) - 1
        notifications = get_state(ev.session_id, "_notifications")
        if index < 0 or index >= len(notifications):
            await bot.send(f"序号超出范围，请发送 1-{len(notifications)} 之间的数字")
            return

        notif = notifications[index]
        notif_type = getattr(notif, "type", "")

        if notif_type != "friendRequest":
            await bot.send("该通知不是好友请求")
            return

        notif_id = getattr(notif, "id", "")
        await accept_friend_request(client, notif_id)
        await bot.send("已接受好友请求！")

    except Exception as e:
        logger.error(f"接受好友请求失败: {e}")
        await bot.send(f"接受好友请求失败：{str(e)}")


@sv.on_command(("忽略", "ignore"))
async def vrc_ignore_notification(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    if not has_state(ev.session_id, "_notifications"):
        await bot.send("请先使用【vrc显示通知】查看通知列表")
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送【忽略 序号】来忽略通知\n例如：忽略 1")
        return

    try:
        index = int(text) - 1
        notifications = get_state(ev.session_id, "_notifications")
        if index < 0 or index >= len(notifications):
            await bot.send(f"序号超出范围，请发送 1-{len(notifications)} 之间的数字")
            return

        notif = notifications[index]
        notif_id = getattr(notif, "id", "")
        await mark_notification_as_read(client, notif_id)
        await bot.send("已忽略该通知")

    except Exception as e:
        logger.error(f"忽略通知失败: {e}")
        await bot.send(f"忽略通知失败：{str(e)}")


@sv.on_command(("删除通知", "delete_notif"))
async def vrc_delete_notification(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    if not has_state(ev.session_id, "_notifications"):
        await bot.send("请先使用【vrc显示通知】查看通知列表")
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送【删除通知 序号】来删除通知\n例如：删除通知 1")
        return

    try:
        index = int(text) - 1
        notifications = get_state(ev.session_id, "_notifications")
        if index < 0 or index >= len(notifications):
            await bot.send(f"序号超出范围，请发送 1-{len(notifications)} 之间的数字")
            return

        notif = notifications[index]
        notif_id = getattr(notif, "id", "")
        await delete_notification(client, notif_id)
        await bot.send("已删除该通知")

    except Exception as e:
        logger.error(f"删除通知失败: {e}")
        await bot.send(f"删除通知失败：{str(e)}")
