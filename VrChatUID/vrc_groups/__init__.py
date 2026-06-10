from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.client import get_client_or_notify
from ..utils.api.groups import (
    ban_group_member,
    create_group_announcement,
    create_group_post,
    get_group,
    get_group_announcements,
    get_group_audit_logs,
    get_group_bans,
    get_group_instances,
    get_group_members,
    get_group_permissions,
    get_group_posts,
    get_group_requests,
    get_group_roles,
    get_my_group_member,
    invite_user_to_group,
    join_group,
    kick_group_member,
    leave_group,
    respond_to_group_join_request,
    search_groups,
    unban_group_member,
    update_group_representation,
)
from ..utils.render import render_template
from ..utils.session_state import get_state, has_state, set_state

sv = SV("群组")


def format_datetime(dt):
    if not dt:
        return "未知"
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


@sv.on_command(("搜索群组", "sg"))
async def vrc_search_group(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    search_term = ev.text.strip()
    if not search_term:
        await bot.send("请输入搜索关键词！\n格式：vrc搜索群组 关键词\n例如：vrc搜索群组 VRChat")
        return

    try:
        await bot.send(f"正在搜索群组「{search_term}」...")
        groups = list(search_groups(client, search_term))

        if not groups:
            await bot.send(f"未找到与「{search_term}」相关的群组")
            return

        set_state(ev.session_id, "_groups", groups)

        msg = f"【群组搜索结果】找到 {len(groups)} 个群组：\n\n"

        for i, group in enumerate(groups, 1):
            name = getattr(group, "name", "Unknown")
            group_id = getattr(group, "group_id", "")
            member_count = getattr(group, "member_count", 0)
            description = getattr(group, "description", "")[:50]

            msg += f"{i}. {name}\n"
            msg += f"   ID: {group_id}\n"
            msg += f"   成员数: {member_count}\n"
            msg += f"   描述: {description}...\n\n"

        msg += "发送【加入 序号】加入第N个群组\n"
        msg += "发送【详情 序号】查看群组详情"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"搜索群组失败: {e}")
        await bot.send(f"搜索群组失败：{str(e)}")


@sv.on_command(("加入群组", "join_group"))
async def vrc_join_group(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    if not has_state(ev.session_id, "_groups"):
        await bot.send("请先使用【vrc搜索群组】搜索群组")
        return

    text = ev.text.strip()
    if not text:
        await bot.send("请发送【加入 序号】来加入群组\n例如：加入 1")
        return

    try:
        index = int(text) - 1
        groups = get_state(ev.session_id, "_groups")
        if index < 0 or index >= len(groups):
            await bot.send(f"序号超出范围，请发送 1-{len(groups)} 之间的数字")
            return

        group = groups[index]
        group_id = getattr(group, "group_id", "")

        await bot.send("正在申请加入群组...")
        await join_group(client, group_id)
        await bot.send("已成功申请加入群组！")

    except Exception as e:
        logger.error(f"加入群组失败: {e}")
        await bot.send(f"加入群组失败：{str(e)}")


@sv.on_command(("群组信息", "gi"))
async def vrc_group_info(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc群组信息 群组ID")
        return

    try:
        await bot.send("正在获取群组信息...")
        group = await get_group(client, group_id)

        name = getattr(group, "name", "Unknown")
        grp_id = getattr(group, "group_id", "")
        short_code = getattr(group, "short_code", "")
        discriminator = getattr(group, "discriminator", "")
        member_count = getattr(group, "member_count", 0)
        online_count = getattr(group, "online_member_count", 0)
        description = getattr(group, "description", "") or "无"
        privacy = getattr(group, "privacy", "未知")
        join_state = getattr(group, "join_state", "未知")
        languages = ", ".join(getattr(group, "languages", []) or []) or "未知"

        # 降级文本
        fallback = "【群组信息】\n\n"
        fallback += f"名称: {name}\n"
        fallback += f"ID: {grp_id}\n"
        if short_code and discriminator:
            fallback += f"短代码: {short_code}#{discriminator}\n"
        fallback += f"成员数: {member_count}\n"
        fallback += f"在线成员: {online_count}\n"
        if description:
            fallback += f"描述: {description}\n"
        fallback += f"隐私: {privacy}\n"
        fallback += f"加入状态: {join_state}\n"
        if languages:
            fallback += f"语言: {languages}\n"

        try:
            image_bytes = await render_template(
                "group_info.html",
                name=name,
                group_id=grp_id,
                short_code=short_code or "----",
                discriminator=discriminator or "----",
                member_count=member_count,
                online_count=online_count,
                privacy=privacy,
                join_state=join_state,
                languages=languages,
                description=description[:200],
            )
            await bot.send(image_bytes)
        except Exception as e:
            logger.warning(f"群组信息图片渲染失败，降级到文本: {e}")
            await bot.send(fallback)

    except Exception as e:
        logger.error(f"获取群组信息失败: {e}")
        await bot.send(f"获取群组信息失败：{str(e)}")


@sv.on_command(("群组成员", "gm"))
async def vrc_group_members(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc群组成员 群组ID")
        return

    try:
        await bot.send("正在获取群组成员...")
        members = await get_group_members(client, group_id, n=20)

        if not members:
            await bot.send("该群组没有成员或获取失败")
            return

        msg = f"【群组成员列表】共 {len(members)} 人：\n\n"

        for i, member in enumerate(members[:20], 1):
            if isinstance(member, dict):
                user_data = member.get("user", {})
                user_id_val = user_data.get("user_id", "未知")
                display_name = user_data.get("display_name", "未知")
                joined_at = format_datetime(member.get("joined_at"))
                membership_status = member.get("membership_status", "未知")
                is_representing = member.get("is_representing", False)
            else:
                user_id_val = getattr(member, "user_id", getattr(member, "id", "未知"))
                display_name = getattr(member, "display_name", "未知")
                joined_at = format_datetime(getattr(member, "joined_at", None))
                membership_status = getattr(member, "membership_status", "未知")
                is_representing = getattr(member, "is_representing", False)

            msg += f"{i}. 昵称: {display_name}\n"
            msg += f"   用户ID: {user_id_val}\n"
            msg += f"   加入时间: {joined_at}\n"
            msg += f"   成员状态: {membership_status}\n"
            if is_representing:
                msg += "   正在代表群组\n"
            msg += "\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取群组成员失败: {e}")
        await bot.send(f"获取群组成员失败：{str(e)}")


@sv.on_command(("群组角色", "gr"))
async def vrc_group_roles(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc群组角色 群组ID")
        return

    try:
        await bot.send("正在获取群组角色...")
        roles = await get_group_roles(client, group_id)

        if not roles:
            await bot.send("该群组没有角色或获取失败")
            return

        msg = f"【群组角色列表】共 {len(roles)} 个：\n\n"

        for i, role in enumerate(roles[:20], 1):
            if isinstance(role, dict):
                name = role.get("name", "未知")
                role_id = role.get("id", "未知")
                description = role.get("description", "无")
                created_at = format_datetime(role.get("created_at"))
                updated_at = format_datetime(role.get("updated_at"))
                is_self_assignable = role.get("is_self_assignable", False)
                is_management_role = role.get("is_management_role", False)
                requires_two_factor = role.get("requires_two_factor", False)
                requires_purchase = role.get("requires_purchase", False)
            else:
                name = getattr(role, "name", "未知")
                role_id = getattr(role, "id", "未知")
                description = getattr(role, "description", "无")
                created_at = format_datetime(getattr(role, "created_at", None))
                updated_at = format_datetime(getattr(role, "updated_at", None))
                is_self_assignable = getattr(role, "is_self_assignable", False)
                is_management_role = getattr(role, "is_management_role", False)
                requires_two_factor = getattr(role, "requires_two_factor", False)
                requires_purchase = getattr(role, "requires_purchase", False)

            msg += f"{i}. {name}\n"
            msg += f"   ID: {role_id}\n"
            msg += f"   描述: {description}\n"
            msg += f"   创建时间: {created_at}\n"
            if updated_at:
                msg += f"   更新时间: {updated_at}\n"

            tags = []
            if is_self_assignable:
                tags.append("可自由加入")
            if is_management_role:
                tags.append("管理角色")
            if requires_two_factor:
                tags.append("需要二步验证")
            if requires_purchase:
                tags.append("需要购买")
            if tags:
                msg += f"   标签: {', '.join(tags)}\n"
            msg += "\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取群组角色失败: {e}")
        await bot.send(f"获取群组角色失败：{str(e)}")


@sv.on_command(("群组公告", "ga"))
async def vrc_group_announcement(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc群组公告 群组ID")
        return

    try:
        await bot.send("正在获取群组公告...")
        announcement = await get_group_announcements(client, group_id)

        if not announcement:
            await bot.send("该群组没有公告")
            return

        msg = "【群组公告】\n\n"

        if isinstance(announcement, dict):
            msg += f"标题: {announcement.get('title', '无标题')}\n"
            msg += f"作者: {announcement.get('author_id', '未知')}\n"
            text = announcement.get("text", "")
            if text:
                msg += f"内容: {text[:200]}...\n"
            image_url = announcement.get("image_url", "")
            if image_url:
                msg += f"图片: {image_url}\n"
            updated_at = format_datetime(announcement.get("updated_at"))
            if updated_at:
                msg += f"更新时间: {updated_at}\n"
        else:
            msg += f"标题: {getattr(announcement, 'title', '无标题')}\n"
            msg += f"作者: {getattr(announcement, 'author_id', '未知')}\n"
            text = getattr(announcement, "text", "")
            if text:
                msg += f"内容: {text[:200]}...\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取群组公告失败: {e}")
        await bot.send(f"获取群组公告失败：{str(e)}")


@sv.on_command(("离开群组", "lg"))
async def vrc_leave_group(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc离开群组 群组ID")
        return

    try:
        await bot.send("正在离开群组...")
        await leave_group(client, group_id)
        await bot.send("已成功离开群组")

    except Exception as e:
        logger.error(f"离开群组失败: {e}")
        await bot.send(f"离开群组失败：{str(e)}")


@sv.on_command(("群组请求", "greq"))
async def vrc_group_requests(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc群组请求 群组ID")
        return

    try:
        await bot.send("正在获取群组请求...")
        requests = await get_group_requests(client, group_id, n=20)

        if not requests:
            await bot.send("该群组没有待处理的请求")
            return

        msg = f"【群组请求列表】共 {len(requests)} 个：\n\n"

        for i, req in enumerate(requests[:20], 1):
            if isinstance(req, dict):
                user_id_val = req.get("user_id", "未知")
                created_at = format_datetime(req.get("created_at"))
                membership_status = req.get("membership_status", "未知")
                has_joined_from_purchase = req.get("has_joined_from_purchase", False)
            else:
                user_id_val = getattr(req, "user_id", "未知")
                created_at = format_datetime(getattr(req, "created_at", None))
                membership_status = getattr(req, "membership_status", "未知")
                has_joined_from_purchase = getattr(req, "has_joined_from_purchase", False)

            msg += f"{i}. 用户ID: {user_id_val}\n"
            msg += f"   请求时间: {created_at}\n"
            msg += f"   成员状态: {membership_status}\n"
            if has_joined_from_purchase:
                msg += "   通过购买加入\n"
            msg += "\n"

        msg += "\n发送【处理请求 序号 accept/reject】审批请求"
        await bot.send(msg)

        set_state(ev.session_id, "_group_requests", requests)

    except Exception as e:
        logger.error(f"获取群组请求失败: {e}")
        await bot.send(f"获取群组请求失败：{str(e)}")


@sv.on_command(("处理请求", "gpjr"))
async def vrc_process_join_request(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    if not has_state(ev.session_id, "_group_requests"):
        await bot.send("请先使用【vrc群组请求】查看请求列表")
        return

    text = ev.text.strip()
    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式：处理请求 序号 accept/reject\n例如：处理请求 1 accept")
        return

    try:
        index = int(parts[0]) - 1
        action = parts[1].lower()
        accept = action == "accept"

        requests = get_state(ev.session_id, "_group_requests")
        if index < 0 or index >= len(requests):
            await bot.send(f"序号超出范围，请发送 1-{len(requests)} 之间的数字")
            return

        req = requests[index]
        target_user_id = req.get("user_id", "") if isinstance(req, dict) else getattr(req, "user_id", "")

        if not target_user_id:
            await bot.send("无法获取用户ID")
            return

        await bot.send("正在处理请求...")
        await respond_to_group_join_request(client, get_state(ev.session_id, "_group_id", ""), target_user_id, accept)

        action_text = "接受" if accept else "拒绝"
        await bot.send(f"已{action_text}用户 {target_user_id} 的加入请求")

    except Exception as e:
        logger.error(f"处理请求失败: {e}")
        await bot.send(f"处理请求失败：{str(e)}")


@sv.on_command(("邀请用户", "gui"))
async def vrc_invite_user(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式：vrc邀请用户 群组ID 用户ID\n例如：vrc邀请用户 grp_abc123 usr_def456")
        return

    group_id = parts[0]
    target_user_id = parts[1]

    try:
        await bot.send("正在邀请用户...")
        await invite_user_to_group(client, group_id, target_user_id)
        await bot.send(f"已邀请用户 {target_user_id} 加入群组")

    except Exception as e:
        logger.error(f"邀请用户失败: {e}")
        await bot.send(f"邀请用户失败：{str(e)}")


@sv.on_command(("踢出成员", "gmk"))
async def vrc_kick_member(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式：vrc踢出成员 群组ID 用户ID\n例如：vrc踢出成员 grp_abc123 usr_def456")
        return

    group_id = parts[0]
    target_user_id = parts[1]

    try:
        await bot.send("正在踢出成员...")
        await kick_group_member(client, group_id, target_user_id)
        await bot.send(f"已将用户 {target_user_id} 踢出群组")

    except Exception as e:
        logger.error(f"踢出成员失败: {e}")
        await bot.send(f"踢出成员失败：{str(e)}")


@sv.on_command(("封禁成员", "gbm"))
async def vrc_ban_member(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式：vrc封禁成员 群组ID 用户ID\n例如：vrc封禁成员 grp_abc123 usr_def456")
        return

    group_id = parts[0]
    target_user_id = parts[1]

    try:
        await bot.send("正在封禁成员...")
        await ban_group_member(client, group_id, target_user_id)
        await bot.send(f"已封禁用户 {target_user_id}")

    except Exception as e:
        logger.error(f"封禁成员失败: {e}")
        await bot.send(f"封禁成员失败：{str(e)}")


@sv.on_command(("解除封禁", "gub"))
async def vrc_unban_member(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split()
    if len(parts) < 2:
        await bot.send("格式：vrc解除封禁 群组ID 用户ID\n例如：vrc解除封禁 grp_abc123 usr_def456")
        return

    group_id = parts[0]
    target_user_id = parts[1]

    try:
        await bot.send("正在解除封禁...")
        await unban_group_member(client, group_id, target_user_id)
        await bot.send(f"已解除封禁用户 {target_user_id}")

    except Exception as e:
        logger.error(f"解除封禁失败: {e}")
        await bot.send(f"解除封禁失败：{str(e)}")


@sv.on_command(("封禁列表", "gb"))
async def vrc_group_bans(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc封禁列表 群组ID")
        return

    try:
        await bot.send("正在获取封禁列表...")
        bans = await get_group_bans(client, group_id, n=20)

        if not bans:
            await bot.send("该群组没有封禁记录")
            return

        msg = f"【群组封禁列表】共 {len(bans)} 个：\n\n"

        for i, ban in enumerate(bans[:20], 1):
            if isinstance(ban, dict):
                user_id_val = ban.get("user_id", "未知")
                created_at = format_datetime(ban.get("created_at"))
                reason = ban.get("reason", "无")
            else:
                user_id_val = getattr(ban, "user_id", "未知")
                created_at = format_datetime(getattr(ban, "created_at", None))
                reason = getattr(ban, "reason", "无")

            msg += f"{i}. 用户ID: {user_id_val}\n"
            msg += f"   封禁时间: {created_at}\n"
            msg += f"   原因: {reason}\n\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取封禁列表失败: {e}")
        await bot.send(f"获取封禁列表失败：{str(e)}")


@sv.on_command(("审计日志", "gal"))
async def vrc_group_audit_logs(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc审计日志 群组ID")
        return

    try:
        await bot.send("正在获取审计日志...")
        logs = await get_group_audit_logs(client, group_id, n=20)

        if not logs:
            await bot.send("该群组没有审计日志")
            return

        msg = f"【群组审计日志】共 {len(logs)} 条：\n\n"

        for i, log in enumerate(logs[:20], 1):
            if isinstance(log, dict):
                action = log.get("action", "未知")
                actor = log.get("actor", {})
                target = log.get("target", {})
                created_at = format_datetime(log.get("created_at"))

                actor_name = actor.get("display_name", "未知") if isinstance(actor, dict) else "未知"
                target_name = target.get("display_name", "未知") if isinstance(target, dict) else "未知"
            else:
                action = getattr(log, "action", "未知")
                created_at = format_datetime(getattr(log, "created_at", None))
                actor_name = "未知"
                target_name = "未知"

            msg += f"{i}. 操作: {action}\n"
            msg += f"   执行者: {actor_name}\n"
            msg += f"   目标: {target_name}\n"
            msg += f"   时间: {created_at}\n\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取审计日志失败: {e}")
        await bot.send(f"获取审计日志失败：{str(e)}")


@sv.on_command(("群组实例", "gi2"))
async def vrc_group_instances(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc群组实例 群组ID")
        return

    try:
        await bot.send("正在获取群组实例...")
        instances = await get_group_instances(client, group_id)

        if not instances:
            await bot.send("该群组当前没有活跃的实例")
            return

        msg = f"【群组实例列表】共 {len(instances)} 个：\n\n"

        for i, inst in enumerate(instances[:20], 1):
            if isinstance(inst, dict):
                instance_id = inst.get("instance_id", "未知")
                location = inst.get("location", "未知")
                member_count = inst.get("member_count", 0)
                world = inst.get("world", {})
                world_name = world.get("name", "未知") if isinstance(world, dict) else "未知"
            else:
                instance_id = getattr(inst, "instance_id", "未知")
                location = getattr(inst, "location", "未知")
                member_count = getattr(inst, "member_count", 0)
                world_name = "未知"

            msg += f"{i}. 实例ID: {instance_id}\n"
            msg += f"   位置: {location}\n"
            msg += f"   成员数: {member_count}\n"
            msg += f"   世界名称: {world_name}\n\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取群组实例失败: {e}")
        await bot.send(f"获取群组实例失败：{str(e)}")


@sv.on_command(("我的群组信息", "mgm"))
async def vrc_my_group_member(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc我的群组信息 群组ID")
        return

    try:
        await bot.send("正在获取我的群组成员信息...")
        member_info = await get_my_group_member(client, group_id)

        if not member_info:
            await bot.send("无法获取我的群组成员信息")
            return

        msg = "【我的群组成员信息】\n\n"

        if isinstance(member_info, dict):
            user_data = member_info.get("user", {})
            user_id_val = user_data.get("id", "未知") if isinstance(user_data, dict) else "未知"
            membership_status = member_info.get("membership_status", "未知")
            created_at = format_datetime(member_info.get("created_at"))
            updated_at = format_datetime(member_info.get("updated_at"))
            is_representing = member_info.get("is_representing", False)
            roles = member_info.get("roles", [])
        else:
            user_id_val = getattr(member_info, "user_id", "未知")
            membership_status = getattr(member_info, "membership_status", "未知")
            created_at = format_datetime(getattr(member_info, "created_at", None))
            updated_at = format_datetime(getattr(member_info, "updated_at", None))
            is_representing = getattr(member_info, "is_representing", False)
            roles = []

        msg += f"用户ID: {user_id_val}\n"
        msg += f"成员状态: {membership_status}\n"
        msg += f"加入时间: {created_at}\n"
        msg += f"更新时间: {updated_at}\n"
        if is_representing:
            msg += "正在代表群组\n"
        if roles:
            role_names = []
            for r in roles:
                if isinstance(r, dict):
                    role_names.append(r.get("name", "未知"))
                else:
                    role_names.append(getattr(r, "name", "未知"))
            msg += f"角色列表: {', '.join(role_names)}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取我的群组成员信息失败: {e}")
        await bot.send(f"获取我的群组成员信息失败：{str(e)}")


@sv.on_command(("更新群组代表", "ugr"))
async def vrc_update_group_rep(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split()

    if len(parts) < 1:
        await bot.send(
            "格式：vrc更新群组代表 群组ID [取消]\n"
            "例如：vrc更新群组代表 grp_abc123\n"
            "取消代表：vrc更新群组代表 grp_abc123 取消"
        )
        return

    group_id = parts[0]
    represent = len(parts) < 2 or parts[1].lower() not in ["取消", "false", "0", "no"]

    try:
        await bot.send("正在更新群组代表身份...")
        await update_group_representation(client, group_id, represent)
        status = "代表群组" if represent else "取消代表群组"
        await bot.send(f"已{status}")

    except Exception as e:
        logger.error(f"更新群组代表身份失败: {e}")
        await bot.send(f"更新群组代表身份失败：{str(e)}")


@sv.on_command(("创建公告", "gca"))
async def vrc_create_announcement(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split(maxsplit=2)

    if len(parts) < 2:
        await bot.send("格式：vrc创建公告 群组ID 标题 [内容]\n例如：vrc创建公告 grp_abc123 公告标题 公告内容")
        return

    group_id = parts[0]
    title = parts[1]
    content = parts[2] if len(parts) > 2 else ""

    try:
        await bot.send("正在创建公告...")
        await create_group_announcement(client, group_id, title, content)
        await bot.send(f"公告创建成功：{title}")

    except Exception as e:
        logger.error(f"创建公告失败: {e}")
        await bot.send(f"创建公告失败：{str(e)}")


@sv.on_command(("帖子列表", "gpl"))
async def vrc_group_posts(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    group_id = ev.text.strip()
    if not group_id:
        await bot.send("请发送群组ID！\n格式：vrc帖子列表 群组ID")
        return

    try:
        await bot.send("正在获取帖子列表...")
        posts = await get_group_posts(client, group_id, n=20)

        if not posts:
            await bot.send("该群组没有帖子")
            return

        msg = f"【群组帖子列表】共 {len(posts)} 个：\n\n"

        for i, post in enumerate(posts[:20], 1):
            if isinstance(post, dict):
                title = post.get("title", "无标题")
                author = post.get("author", {})
                author_name = author.get("display_name", "未知") if isinstance(author, dict) else "未知"
                created_at = format_datetime(post.get("created_at"))
                text = post.get("text", "")[:50]
            else:
                title = getattr(post, "title", "无标题")
                author_name = "未知"
                created_at = format_datetime(getattr(post, "created_at", None))
                text = getattr(post, "text", "")[:50]

            msg += f"{i}. {title}\n"
            msg += f"   作者: {author_name}\n"
            msg += f"   创建时间: {created_at}\n"
            msg += f"   内容: {text}...\n\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"获取帖子列表失败: {e}")
        await bot.send(f"获取帖子列表失败：{str(e)}")


@sv.on_command(("创建帖子", "gcp"))
async def vrc_create_post(bot: Bot, ev: Event) -> None:

    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    text = ev.text.strip()
    parts = text.split(maxsplit=2)

    if len(parts) < 2:
        await bot.send("格式：vrc创建帖子 群组ID 标题 [内容]\n例如：vrc创建帖子 grp_abc123 帖子标题 帖子内容")
        return

    group_id = parts[0]
    title = parts[1]
    content = parts[2] if len(parts) > 2 else ""

    try:
        await bot.send("正在创建帖子...")
        await create_group_post(client, group_id, title, content)
        await bot.send(f"帖子创建成功：{title}")

    except Exception as e:
        logger.error(f"创建帖子失败: {e}")
        await bot.send(f"创建帖子失败：{str(e)}")
