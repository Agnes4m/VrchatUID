"""HTML 渲染工具模块

封装 gsuid_core 的 HTML 渲染能力，提供：
- HTML 字符串 -> PNG bytes
- 模板加载 + 变量替换
- 渲染失败时自动降级到纯文本发送
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
STYLES_DIR = Path(__file__).parent / "styles"


def _load_template(name: str) -> str:
    """加载 HTML 模板文件"""
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"模板文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def _load_style(name: str = "common.css") -> str:
    """加载 CSS 样式文件"""
    path = STYLES_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _format_value(value: Any) -> str:
    """将 Python 值格式化为 HTML 安全的字符串（转义特殊字符）"""
    if value is None:
        return ""
    s = str(value)
    # 基础 HTML 转义
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s


def _render_template_simple(template: str, **variables: Any) -> str:
    """简单的模板变量替换（支持 {{ var }} 语法）

    为避免双重转义问题：
    - 卡片构建器（build_user_card 等）输出的是已包含 HTML 标签的字符串
    - 模板引擎对这些"原始 HTML"变量直接插入，不做转义
    - 简单文本变量（keyword、total_count 等）由 _format_value 转义

    使用约定：
    - 简单文本字段（keyword, total_count, fav_type, etc.）：正常传递
    - 卡片 HTML 变量（user_cards, world_cards, fav_cards, etc.）：已转义过，直接插入
    """
    # 这些 key 包含已转义的 HTML（卡片构建器输出）
    raw_html_keys = {
        "user_cards",
        "world_cards",
        "fav_cards",
        "request_section",
        "other_section",
        "online_section",
        "offline_section",
    }
    result = template
    for key, value in variables.items():
        placeholder = "{{ " + key + " }}"
        if key in raw_html_keys:
            result = result.replace(placeholder, str(value) if value is not None else "")
        else:
            result = result.replace(placeholder, _format_value(value))
    return result


async def render_html(html: str, *, max_width: float = 800.0) -> bytes:
    """将 HTML 字符串渲染为 PNG 图片字节

    Args:
        html: 完整的 HTML 字符串
        max_width: 图片最大宽度

    Returns:
        PNG 格式的图片字节

    Raises:
        RuntimeError: 如果渲染失败
    """
    try:
        from gsuid_core.utils.html_render import render_html_to_bytes
    except ImportError as e:
        raise RuntimeError("HTML 渲染需要 htmlkit 库，请确认 gsuid_core 已正确安装") from e

    return await render_html_to_bytes(html, max_width=max_width)


async def render_template(
    template_name: str,
    *,
    css: str = "",
    max_width: float = 800.0,
    **variables: Any,
) -> bytes:
    """加载模板并渲染为 PNG 图片

    Args:
        template_name: 模板文件名（如 "friend_list.html"）
        css: 可选的额外 CSS，会嵌入到 <style> 标签
        max_width: 图片宽度
        **variables: 模板变量
    """
    template = _load_template(template_name)
    style = _load_style()
    if css:
        style = f"{style}\n{css}"

    # 将 CSS 注入到模板的 </head> 之前
    if style and "</head>" in template:
        template = template.replace("</head>", f"<style>{style}</style></head>")

    html = _render_template_simple(template, **variables)
    return await render_html(html, max_width=max_width)


async def send_image(bot, image_bytes: bytes) -> None:
    """将图片字节发送给用户"""

    await bot.send(image_bytes)


async def send_or_fallback(bot, html: str, fallback_text: str) -> None:
    """尝试发送 HTML 渲染的图片，失败时降级到纯文本

    Args:
        bot: Bot 实例
        html: HTML 字符串
        fallback_text: 渲染失败时发送的纯文本
    """
    try:
        image_bytes = await render_html(html)
        await send_image(bot, image_bytes)
    except Exception as e:
        logger.warning(f"HTML 渲染失败，降级到纯文本: {e}")
        await bot.send(fallback_text)


async def send_template_or_fallback(
    bot,
    template_name: str,
    fallback_text: str,
    **variables: Any,
) -> None:
    """渲染模板并发送，失败时降级到纯文本"""
    try:
        image_bytes = await render_template(template_name, **variables)
        await send_image(bot, image_bytes)
    except Exception as e:
        logger.warning(f"模板渲染失败 ({template_name})，降级到纯文本: {e}")
        await bot.send(fallback_text)


# ===== 卡片构建器 =====

_STATUS_DOT_MAP = {
    "online": "online",
    "active": "active",
    "join me": "joinme",
    "busy": "busy",
    "ask me": "askme",
    "offline": "offline",
}

_STATUS_BADGE_MAP = {
    "online": "online",
    "active": "active",
    "join me": "joinme",
    "busy": "busy",
    "ask me": "askme",
    "offline": "offline",
}


def _status_key(status: str) -> str:
    return _STATUS_DOT_MAP.get((status or "").lower(), "offline")


def _badge_class(status: str) -> str:
    key = _STATUS_BADGE_MAP.get((status or "").lower(), "offline")
    return f"badge-{key}"


def _dot_class(status: str) -> str:
    key = _STATUS_DOT_MAP.get((status or "").lower(), "offline")
    return f"dot-{key}"


def build_friend_card(idx: int, friend) -> str:
    """构建好友卡片 HTML"""
    name = _format_value(getattr(friend, "display_name", "Unknown"))
    user_id = _format_value(getattr(friend, "id", ""))
    status = _format_value(getattr(friend, "status", "offline"))
    status_desc = _format_value(getattr(friend, "status_description", "")) or status
    avatar_url = getattr(friend, "current_avatar_thumbnail_image_url", "")

    avatar_html = (
        f'<img class="card-avatar" src="{_format_value(avatar_url)}" alt="avatar">'
        if avatar_url
        else '<div class="card-avatar-placeholder">👤</div>'
    )

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    {avatar_html}
    <div class="card-body">
        <div class="card-name">{name}</div>
        <div class="card-id">{user_id}</div>
        <div class="card-row">
            <span class="status-dot {_dot_class(status)}"></span>
            <span class="badge {_badge_class(status)}">{status_desc}</span>
        </div>
    </div>
</div>
"""


def build_friend_section(title: str, friends: list, start_idx: int = 1) -> str:
    """构建好友分组 HTML"""
    if not friends:
        return ""
    cards = "".join(build_friend_card(start_idx + i, f) for i, f in enumerate(friends))
    return f"""
<div class="section-header">
    <span class="section-title">{_format_value(title)}</span>
    <span class="section-count">{len(friends)} 人</span>
</div>
<div class="grid">{cards}</div>
"""


def build_user_card(idx: int, user) -> str:
    """构建用户搜索卡片 HTML"""
    name = _format_value(getattr(user, "display_name", "Unknown"))
    user_id = _format_value(getattr(user, "id", ""))
    status = _format_value(getattr(user, "status", "offline"))
    status_desc = _format_value(getattr(user, "status_description", "")) or status
    avatar_url = getattr(user, "current_avatar_thumbnail_image_url", "")
    trust = _format_value(getattr(user, "trust", None)) or "visitor"

    avatar_html = (
        f'<img class="card-avatar" src="{_format_value(avatar_url)}" alt="avatar">'
        if avatar_url
        else '<div class="card-avatar-placeholder">👤</div>'
    )

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    {avatar_html}
    <div class="card-body">
        <div class="card-name">{name}</div>
        <div class="card-id">{user_id}</div>
        <div class="card-row">
            <span class="status-dot {_dot_class(status)}"></span>
            <span class="badge {_badge_class(status)}">{status_desc}</span>
        </div>
        <div class="card-row">
            <span class="badge badge-info">信任: {trust}</span>
        </div>
    </div>
</div>
"""


def build_world_card(idx: int, world) -> str:
    """构建世界搜索卡片 HTML"""
    name = _format_value(getattr(world, "name", "Unknown"))
    author = _format_value(getattr(world, "author_name", "Unknown"))
    occupants = _format_value(getattr(world, "occupants", 0))
    favorites = _format_value(getattr(world, "favorites", 0))
    world_id = _format_value(getattr(world, "id", ""))
    thumbnail = getattr(world, "thumbnail_image_url", "")

    thumb_html = (
        f'<img class="card-avatar" src="{_format_value(thumbnail)}" alt="world">'
        if thumbnail
        else '<div class="card-avatar-placeholder">🌐</div>'
    )

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    {thumb_html}
    <div class="card-body">
        <div class="card-name">{name}</div>
        <div class="card-id">作者: {author}</div>
        <div class="card-row">
            <span class="badge badge-online">👥 {occupants} 在线</span>
        </div>
        <div class="card-row">
            <span class="badge badge-info">⭐ {favorites} 收藏</span>
        </div>
        <div class="card-row">
            <span style="font-size: 10px; color: #6a6a7e;">{world_id}</span>
        </div>
    </div>
</div>
"""


def build_notification_card(idx: int, notif) -> str:
    """构建通知卡片 HTML"""
    notif_type = getattr(notif, "type", "unknown")
    sender_name = _format_value(getattr(notif, "sender_username", getattr(notif, "sender_display_name", "Unknown")))
    sender_id = _format_value(getattr(notif, "sender_user_id", ""))
    message = _format_value(getattr(notif, "message", ""))[:100]
    created_at = _format_value(getattr(notif, "created_at", ""))

    icon = "📨" if notif_type == "friendRequest" else "🔔"
    badge_text = "好友请求" if notif_type == "friendRequest" else notif_type
    badge_class = "badge-info" if notif_type == "friendRequest" else "badge-active"

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    <div class="card-avatar-placeholder">{icon}</div>
    <div class="card-body">
        <div class="card-name">{sender_name}</div>
        <div class="card-id">{sender_id}</div>
        <div class="card-row">
            <span class="badge {badge_class}">{badge_text}</span>
        </div>
        {f'<div class="card-row">{message}</div>' if message else ""}
        {f'<div class="card-row" style="font-size: 10px; color: #6a6a7e;">{created_at}</div>' if created_at else ""}
    </div>
</div>
"""


def build_favorite_card(idx: int, fav) -> str:
    """构建收藏卡片 HTML"""
    fav_id_ref = _format_value(getattr(fav, "favorite_id_ref", "Unknown"))
    group = _format_value(getattr(fav, "group", "default"))
    tags = getattr(fav, "tags", [])
    updated_at = _format_value(getattr(fav, "updated_at", ""))

    tags_html = ""
    if tags:
        tag_badges = " ".join(f'<span class="badge badge-info">{_format_value(t)}</span>' for t in tags[:3])
        tags_html = f'<div class="card-row">{tag_badges}</div>'

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    <div class="card-avatar-placeholder">⭐</div>
    <div class="card-body">
        <div class="card-name">{fav_id_ref}</div>
        <div class="card-id">组: {group}</div>
        {tags_html}
        {f'<div class="card-row" style="font-size: 10px; color: #6a6a7e;">更新: {updated_at}</div>' if updated_at else ""}
    </div>
</div>
"""


def text_to_html(text: str, title: str = "VRChat") -> str:
    """将纯文本包装为简单的 HTML 页面

    用于降级时仍有可读性，或作为模板开发的基础。
    """
    import html as html_lib

    escaped = html_lib.escape(text)
    # 简单换行转 <br>
    body = escaped.replace("\n", "<br>\n")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{html_lib.escape(title)}</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #1a1a1a;
    color: #e0e0e0;
    padding: 20px;
    line-height: 1.6;
    font-size: 14px;
}}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{body}</pre>
</body>
</html>"""
