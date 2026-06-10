from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.client import get_client_or_notify
from ..utils.api.favorites import (
    add_favorite,
    clear_favorite_group,
    get_favorite_group,
    get_favorite_groups,
    get_favorite_limits,
    get_favorites,
    remove_favorite,
)
from ..utils.database import get_user_credentials
from ..utils.render import build_favorite_card, render_template
from ..utils.session_state import get_state, has_state, set_state

sv = SV("收藏")


def format_datetime(dt):
    if not dt:
        return "未知"
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


@sv.on_command(("收藏列表", "fl"))
async def vrc_favorite_list(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip().lower()
    fav_type = text if text in ["avatar", "world", "friend"] else "world"

    try:
        await bot.send(f"正在获取{fav_type}收藏列表...")
        favorites = list(get_favorites(client, fav_type, max_size=20))

        if not favorites:
            await bot.send(f"没有{fav_type}类型的收藏")
            return

        set_state(ev.session_id, "_favorites", favorites)
        set_state(ev.session_id, "_favorite_type", fav_type)

        # 降级文本
        fallback = f"【{fav_type}收藏列表】共 {len(favorites)} 个：\n\n"
        for i, fav in enumerate(favorites[:20], 1):
            fav_id_ref = getattr(fav, "favorite_id_ref", "Unknown")
            group = getattr(fav, "group", "default")
            tags = getattr(fav, "tags", [])
            updated_at = format_datetime(getattr(fav, "updated_at", None))

            fallback += f"{i}. ID: {fav_id_ref}\n"
            fallback += f"   收藏组: {group}\n"
            if tags:
                fallback += f"   标签: {', '.join(tags)}\n"
            fallback += f"   更新时间: {updated_at}\n\n"

        fallback += "发送【详情 序号】查看收藏详情\n"
        fallback += "发送【删除 序号】删除收藏"

        # 渲染图片
        try:
            fav_cards = "".join(build_favorite_card(i, f) for i, f in enumerate(favorites, 1))
            image_bytes = await render_template(
                "favorite_list.html",
                fav_type=fav_type,
                total_count=len(favorites),
                fav_cards=fav_cards,
            )
            await bot.send(image_bytes)
        except Exception as e:
            logger.warning(f"收藏列表图片渲染失败，降级到文本: {e}")
            await bot.send(fallback)

    except Exception as e:
        logger.error(f"获取收藏列表失败: {e}")
        await bot.send(f"获取收藏列表失败：{str(e)}")


@sv.on_command(("收藏组列表", "fgl"))
async def vrc_favorite_group_list(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在获取收藏组列表...")
        groups = list(get_favorite_groups(client, max_size=50))

        if not groups:
            await bot.send("没有收藏组")
            return

        avatar_groups = [g for g in groups if getattr(g, "type", "") == "avatar"]
        world_groups = [g for g in groups if getattr(g, "type", "") == "world"]
        friend_groups = [g for g in groups if getattr(g, "type", "") == "friend"]

        msg = f"【收藏组列表】共 {len(groups)} 个：\n\n"

        if avatar_groups:
            msg += f"【Avatar】{len(avatar_groups)} 个\n"
            for i, group in enumerate(avatar_groups[:10], 1):
                display_name = getattr(group, "display_name", "Unknown")
                name = getattr(group, "name", "")
                owner_id = getattr(group, "owner_id", "")
                visibility = getattr(group, "visibility", "")
                msg += f"  {i}. {display_name} ({name})\n"
                msg += f"     所有者: {owner_id}\n"
                msg += f"     可见性: {visibility}\n\n"
            if len(avatar_groups) > 10:
                msg += f"  ... 还有 {len(avatar_groups) - 10} 个\n"
            msg += "\n"

        if world_groups:
            msg += f"【World】{len(world_groups)} 个\n"
            for i, group in enumerate(world_groups[:10], 1):
                display_name = getattr(group, "display_name", "Unknown")
                name = getattr(group, "name", "")
                owner_id = getattr(group, "owner_id", "")
                visibility = getattr(group, "visibility", "")
                msg += f"  {i}. {display_name} ({name})\n"
                msg += f"     所有者: {owner_id}\n"
                msg += f"     可见性: {visibility}\n\n"
            if len(world_groups) > 10:
                msg += f"  ... 还有 {len(world_groups) - 10} 个\n"
            msg += "\n"

        if friend_groups:
            msg += f"【Friend】{len(friend_groups)} 个\n"
            for i, group in enumerate(friend_groups[:10], 1):
                display_name = getattr(group, "display_name", "Unknown")
                name = getattr(group, "name", "")
                owner_id = getattr(group, "owner_id", "")
                visibility = getattr(group, "visibility", "")
                msg += f"  {i}. {display_name} ({name})\n"
                msg += f"     所有者: {owner_id}\n"
                msg += f"     可见性: {visibility}\n\n"
            if len(friend_groups) > 10:
                msg += f"  ... 还有 {len(friend_groups) - 10} 个\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取收藏组列表失败: {e}")
        await bot.send(f"获取收藏组列表失败：{str(e)}")


@sv.on_command(("收藏限制", "flim"))
async def vrc_favorite_limits(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在获取收藏限制信息...")
        limits = await get_favorite_limits(client)

        msg = "【收藏限制信息】\n\n"

        default_max_groups = getattr(limits, "default_max_favorite_groups", 0)
        default_max_per_group = getattr(limits, "default_max_favorites_per_group", 0)

        msg += f"默认收藏组数量: {default_max_groups}\n"
        msg += f"默认每组收藏数: {default_max_per_group}\n"

        max_groups = getattr(limits, "max_favorite_groups", None)
        max_per_group = getattr(limits, "max_favorites_per_group", None)

        if max_groups:
            msg += "\n【最大收藏组】\n"
            msg += f"  Avatar: {getattr(max_groups, 'avatar', 'N/A')}\n"
            msg += f"  World: {getattr(max_groups, 'world', 'N/A')}\n"
            msg += f"  Friend: {getattr(max_groups, 'friend', 'N/A')}\n"

        if max_per_group:
            msg += "\n【最大每组收藏数】\n"
            msg += f"  Avatar: {getattr(max_per_group, 'avatar', 'N/A')}\n"
            msg += f"  World: {getattr(max_per_group, 'world', 'N/A')}\n"
            msg += f"  Friend: {getattr(max_per_group, 'friend', 'N/A')}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取收藏限制失败: {e}")
        await bot.send(f"获取收藏限制失败：{str(e)}")


@sv.on_command(("添加收藏", "fav"))
async def vrc_add_favorite(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    if not text:
        await bot.send("格式：vrc添加收藏 类型 引用ID [标签]\n例如：vrc添加收藏 world wrld_abc123 group1")
        return

    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式错误！请发送：vrc添加收藏 类型 引用ID [标签]\n例如：vrc添加收藏 world wrld_abc123 group1")
        return

    fav_type = parts[0].lower()
    if fav_type not in ["avatar", "world", "friend"]:
        await bot.send("类型必须是 avatar、world 或 friend")
        return

    fav_id = parts[1]
    tags = parts[2:] if len(parts) > 2 else []

    try:
        await bot.send("正在添加收藏...")
        await add_favorite(client, fav_type, fav_id, tags)
        await bot.send(f"已成功添加收藏：{fav_id}")

    except Exception as e:
        logger.error(f"添加收藏失败: {e}")
        await bot.send(f"添加收藏失败：{str(e)}")


@sv.on_command(("删除收藏", "fdel"))
async def vrc_remove_favorite(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送要删除的收藏ID\n格式：vrc删除收藏 收藏ID")
        return

    try:
        await bot.send("正在删除收藏...")
        await remove_favorite(client, text)
        await bot.send("已成功删除收藏")

    except Exception as e:
        logger.error(f"删除收藏失败: {e}")
        await bot.send(f"删除收藏失败：{str(e)}")


@sv.on_command(("收藏组详情", "fg"))
async def vrc_favorite_group_detail(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    if not text:
        await bot.send("格式：vrc收藏组详情 类型 收藏组名称\n例如：vrc收藏组详情 world mygroup")
        return

    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式错误！请发送：vrc收藏组详情 类型 收藏组名称")
        return

    fav_type = parts[0].lower()
    group_name = parts[1]

    try:
        cred = await get_user_credentials(user_id, bot_id)
        owner_id = cred.vrc_uid if cred else ""
    except Exception:
        owner_id = ""

    if not owner_id:
        await bot.send("无法获取用户ID，请先登录")
        return

    try:
        await bot.send("正在获取收藏组详情...")
        group = await get_favorite_group(client, fav_type, group_name, owner_id)

        msg = "【收藏组详情】\n\n"
        msg += f"名称: {getattr(group, 'display_name', 'Unknown')} ({getattr(group, 'name', '')})\n"
        msg += f"类型: {getattr(group, 'type', '')}\n"
        msg += f"所有者: {getattr(group, 'owner_id', '')}\n"
        msg += f"可见性: {getattr(group, 'visibility', '')}\n"
        tags = getattr(group, "tags", [])
        if tags:
            msg += f"标签: {', '.join(tags)}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取收藏组详情失败: {e}")
        await bot.send(f"获取收藏组详情失败：{str(e)}")


@sv.on_command(("清空收藏组", "fcg"))
async def vrc_clear_favorite_group(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    if not text:
        await bot.send("格式：vrc清空收藏组 类型 收藏组名称\n例如：vrc清空收藏组 world mygroup")
        return

    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式错误！请发送：vrc清空收藏组 类型 收藏组名称")
        return

    fav_type = parts[0].lower()
    group_name = parts[1]

    try:
        cred = await get_user_credentials(user_id, bot_id)
        owner_id = cred.vrc_uid if cred else ""
    except Exception:
        owner_id = ""

    if not owner_id:
        await bot.send("无法获取用户ID，请先登录")
        return

    try:
        await bot.send("正在清空收藏组...")
        await clear_favorite_group(client, fav_type, group_name, owner_id)
        await bot.send("已清空收藏组")

    except Exception as e:
        logger.error(f"清空收藏组失败: {e}")
        await bot.send(f"清空收藏组失败：{str(e)}")
