"""HTML 渲染：模板加载、Jinja2 替换、Playwright 截图、卡片构建。"""

import html as html_lib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
STYLES_DIR = Path(__file__).parent / "styles"

_RAW_HTML_KEYS = frozenset(
    {
        "user_cards",
        "world_cards",
        "fav_cards",
        "request_section",
        "other_section",
        "online_section",
        "offline_section",
    }
)

_PLATFORM_ICON = {
    "android": "🤖",
    "ios": "🍎",
    "standalonewindows": "🖥️",
    "standalonequest": "🥽",
    "web": "🌐",
    "unknownplatform": "❓",
}

_STATUS_KEY = {
    "online": "online",
    "active": "active",
    "join me": "joinme",
    "busy": "busy",
    "ask me": "askme",
    "offline": "offline",
}

_STATUS_LABEL = {
    "online": "在线",
    "active": "活跃",
    "join me": "求加入",
    "busy": "忙碌",
    "ask me": "可私聊",
    "offline": "离线",
}


def _esc(value: Any) -> str:
    if value is None:
        return ""
    s = str(value)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _attr(name: str, value: Any) -> str:
    return f'{name}="{_esc(value)}"'


def _avatar(url: str, placeholder: str) -> str:
    return (
        f'<img class="card-avatar" src="{_esc(url)}" alt="">'
        if url
        else f'<div class="card-avatar-placeholder">{placeholder}</div>'
    )


def _status_class(status: str) -> str:
    return f"dot-{_STATUS_KEY.get((status or '').lower(), 'offline')}"


def _badge_class(status: str) -> str:
    return f"badge-{_STATUS_KEY.get((status or '').lower(), 'offline')}"


def _platform_icon(platform: str) -> str:
    return _PLATFORM_ICON.get((platform or "").lower(), "❓")


def _status_label(status: str) -> str:
    return _STATUS_LABEL.get((status or "").lower(), status or "未知")


def _load(name: str, base: Path) -> str:
    path = base / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _render(template: str, **variables: Any) -> str:
    try:
        from jinja2 import Environment, Markup, select_autoescape
    except ImportError:
        return _render_fallback(template, **variables)

    env = Environment(autoescape=select_autoescape(default_for_string=False))
    env.finalize = lambda x: "" if x is None else x
    processed = {
        k: (Markup(str(v)) if v is not None else v) if k in _RAW_HTML_KEYS else v for k, v in variables.items()
    }
    return env.from_string(template).render(**processed)


def _render_fallback(template: str, **variables: Any) -> str:
    for k, v in variables.items():
        placeholder = "{{ " + k + " }}"
        replacement = str(v) if v is not None else ""
        if k not in _RAW_HTML_KEYS:
            replacement = _esc(replacement)
        template = template.replace(placeholder, replacement)
    return template


async def render_html(html: str, *, max_width: float = 1500.0) -> bytes:
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError("HTML 渲染需要 playwright") from e

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                page = await browser.new_page(viewport={"width": int(max_width), "height": 800})
                await page.set_content(html, wait_until="networkidle", timeout=10000)
                return await page.screenshot(full_page=True, type="png")
            finally:
                await browser.close()
    except Exception as e:
        raise RuntimeError(f"Playwright 渲染失败: {e}") from e


async def render_template(
    template_name: str,
    *,
    css: str = "",
    max_width: float = 1500.0,
    **variables: Any,
) -> bytes:
    template = _load(template_name, TEMPLATES_DIR)
    style = _load("common.css", STYLES_DIR) + ("\n" + css if css else "")
    if style and "</head>" in template:
        template = template.replace("</head>", f"<style>{style}</style></head>")
    return await render_html(_render(template, **variables), max_width=max_width)


async def send_image(bot, image_bytes: bytes) -> None:
    await bot.send(image_bytes)


async def send_or_fallback(bot, html: str, fallback_text: str) -> None:
    try:
        await send_image(bot, await render_html(html))
    except Exception as e:
        logger.warning("HTML 渲染失败，降级到纯文本: %s", e)
        await bot.send(fallback_text)


async def send_template_or_fallback(
    bot,
    template_name: str,
    fallback_text: str,
    **variables: Any,
) -> None:
    try:
        await send_image(bot, await render_template(template_name, **variables))
    except Exception as e:
        logger.warning("模板 %s 渲染失败，降级到纯文本: %s", template_name, e)
        await bot.send(fallback_text)


def build_friend_card(idx: int, friend) -> str:
    name = _esc(getattr(friend, "display_name", "Unknown"))
    user_id = _esc(getattr(friend, "id", ""))
    status = getattr(friend, "status", "offline")
    status_desc = getattr(friend, "status_description", "") or status
    avatar = _avatar(getattr(friend, "current_avatar_thumbnail_image_url", ""), "👤")

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    {avatar}
    <div class="card-body">
        <div class="card-name">{name}</div>
        <div class="card-id">{user_id}</div>
        <div class="card-row">
            <span class="status-dot {_status_class(status)}"></span>
            <span class="badge {_badge_class(status)}">{_esc(status_desc)}</span>
        </div>
    </div>
</div>
"""


def build_friend_section(title: str, friends: list, start_idx: int = 1) -> str:
    if not friends:
        return ""
    cards = "".join(build_friend_card(start_idx + i, f) for i, f in enumerate(friends))
    return f"""
<div class="section-header">
    <span class="section-title">{_esc(title)}</span>
    <span class="section-count">{len(friends)} 人</span>
</div>
<div class="grid">{cards}</div>
"""


def build_user_card(idx: int, user) -> str:
    name = _esc(getattr(user, "display_name", "Unknown"))
    user_id = _esc(getattr(user, "id", ""))
    status = getattr(user, "status", "offline")
    last_platform = getattr(user, "last_platform", "unknown")
    status_desc = getattr(user, "status_description", "")
    avatar = _avatar(getattr(user, "current_avatar_thumbnail_image_url", ""), "👤")

    desc_html = (
        f'<div class="card-status-desc" {_attr("title", status_desc)}>💬 {_esc(status_desc)}</div>'
        if status_desc
        else ""
    )

    return f"""
<div class="card card-compact">
    <div class="card-index">{idx}</div>
    {avatar}
    <div class="card-body">
        <div class="card-name">{name}</div>
        <div class="card-id">{user_id}</div>
        <div class="card-row">
            <span class="status-dot {_status_class(status)}"></span>
            <span class="status-text">{_status_label(status)}</span>
            <span class="platform-icon" {_attr("title", last_platform)}>{_platform_icon(last_platform)}</span>
        </div>
        {desc_html}
    </div>
</div>
"""


def build_world_card(idx: int, world) -> str:
    name = _esc(getattr(world, "name", "Unknown"))
    author = _esc(getattr(world, "author_name", "Unknown"))
    occupants = _esc(getattr(world, "occupants", 0))
    favorites = _esc(getattr(world, "favorites", 0))
    world_id = _esc(getattr(world, "id", ""))
    thumb = _avatar(getattr(world, "thumbnail_image_url", ""), "🌐")

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    {thumb}
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
    notif_type = getattr(notif, "type", "unknown")
    is_friend_req = notif_type == "friendRequest"
    icon = "📨" if is_friend_req else "🔔"
    badge_text = "好友请求" if is_friend_req else notif_type
    badge_class = "badge-info" if is_friend_req else "badge-active"

    sender = _esc(getattr(notif, "sender_username", getattr(notif, "sender_display_name", "Unknown")))
    sender_id = _esc(getattr(notif, "sender_user_id", ""))
    message = _esc(getattr(notif, "message", "")[:100])
    created_at = _esc(getattr(notif, "created_at", ""))

    extra = ""
    if message:
        extra += f'<div class="card-row">{message}</div>'
    if created_at:
        extra += f'<div class="card-row" style="font-size: 10px; color: #6a6a7e;">{created_at}</div>'

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    <div class="card-avatar-placeholder">{icon}</div>
    <div class="card-body">
        <div class="card-name">{sender}</div>
        <div class="card-id">{sender_id}</div>
        <div class="card-row">
            <span class="badge {badge_class}">{badge_text}</span>
        </div>
        {extra}
    </div>
</div>
"""


def build_favorite_card(idx: int, fav) -> str:
    fav_ref = _esc(getattr(fav, "favorite_id_ref", "Unknown"))
    group = _esc(getattr(fav, "group", "default"))
    tags = getattr(fav, "tags", [])
    updated_at = _esc(getattr(fav, "updated_at", ""))

    if tags:
        tag_badges = " ".join(f'<span class="badge badge-info">{_esc(t)}</span>' for t in tags[:3])
        tags_html = f'<div class="card-row">{tag_badges}</div>'
    else:
        tags_html = ""
    updated_html = (
        f'<div class="card-row" style="font-size: 10px; color: #6a6a7e;">更新: {updated_at}</div>' if updated_at else ""
    )

    return f"""
<div class="card">
    <div class="card-index">{idx}.</div>
    <div class="card-avatar-placeholder">⭐</div>
    <div class="card-body">
        <div class="card-name">{fav_ref}</div>
        <div class="card-id">组: {group}</div>
        {tags_html}
        {updated_html}
    </div>
</div>
"""


def text_to_html(text: str, title: str = "VRChat") -> str:
    body = html_lib.escape(text).replace("\n", "<br>\n")
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
