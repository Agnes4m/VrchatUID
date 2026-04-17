#!/usr/bin/env python3
"""
GSUID 插件模板 - 交互式初始化脚本

根据用户选择的功能模块生成定制化的 GSUID Core 插件。

用法:
    python init_plugin.py

脚本将引导你完成:
    1. 基础配置（名称、前缀、作者等）
    2. 功能模块选择（帮助、绑定、查询、签到等）
    3. 配置预览和确认
    4. 插件生成

示例:
    $ python init_plugin.py
    步骤 1/3 - 基础配置
    ...
    步骤 2/3 - 选择功能模块
    请选择要包含的功能模块: 1,2,4
    ...
    步骤 3/3 - 配置预览
    ...
    插件生成位置: ../MyPlugin
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# 默认配置值
DEFAULTS: dict[str, str] = {
    "PluginName": "PluginNameUID",
    "plugin_short": "mp",
    "plugin_cn_name": "My Plugin",
    "GameName": "Game",
    "author": "YourName",
    "version": "0.1.0",
    "description": "A GSUID Core plugin",
    "prefix": "mp",
    "force_prefix": "mp",
    "additional_prefixes": "",
    "email": "your.email@example.com",
}

# 基础配置项
CONFIG_ITEMS: list[dict[str, str]] = [
    {"key": "PluginName", "name": "插件英文名称", "desc": "用于类名，如 MyPlugin"},
    {"key": "plugin_short", "name": "插件短名", "desc": "用于命令前缀"},
    {"key": "plugin_cn_name", "name": "插件中文名称", "desc": "显示名称"},
    {"key": "GameName", "name": "游戏名称", "desc": "用于数据库字段"},
    {"key": "author", "name": "作者名称", "desc": "插件作者"},
    {"key": "version", "name": "版本号", "desc": "初始版本"},
    {"key": "description", "name": "插件描述", "desc": "简短描述"},
    {"key": "email", "name": "作者邮箱", "desc": "联系邮箱"},
    {"key": "additional_prefixes", "name": "额外命令前缀", "desc": "多个用逗号分隔，如: 原神,ys,genshin"},
]

# 可选功能模块
FEATURE_MODULES: list[dict[str, Any]] = [
    {"id": "help", "name": "帮助功能", "desc": "显示插件命令列表", "config": True},
    {"id": "bind", "name": "UID绑定", "desc": "绑定游戏账号UID", "config": True, "database": True},
    {"id": "query", "name": "信息查询", "desc": "查询用户游戏信息", "config": True, "api": True},
    {"id": "sign", "name": "每日签到", "desc": "签到领取奖励", "config": True, "database": True},
]


def parse_selection(input_str: str, max_num: int) -> set[int]:
    """解析用户输入的选择。支持: 1,3,5 | 1-4 | all | 空

    Args:
        input_str: 用户输入字符串
        max_num: 最大有效数字

    Returns:
        选中的索引集合（1-based）
    """
    selected: set[int] = set()
    input_clean = input_str.strip().lower()

    if input_clean == "all":
        return set(range(1, max_num + 1))

    if not input_clean or input_clean == "0":
        return selected

    for part in input_clean.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                selected.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                num = int(part)
                if 1 <= num <= max_num:
                    selected.add(num)
            except ValueError:
                continue

    return {n for n in selected if 1 <= n <= max_num}


def show_basic_config() -> dict[str, str]:
    """显示基础配置提示并收集用户输入。"""
    print("=" * 60)
    print("步骤 1/3 - 基础配置")
    print("=" * 60)
    print()

    config = DEFAULTS.copy()

    for item in CONFIG_ITEMS:
        key = item["key"]
        default_val = config.get(key, DEFAULTS.get(key, ""))

        if key == "plugin_short" and config.get("PluginName"):
            default_val = config["PluginName"].lower()

        prompt = f"{item['name']} ({key}) [默认: {default_val}]: "
        value = input(prompt).strip()
        config[key] = value if value else default_val

    # 自动设置前缀字段
    if config.get("plugin_short"):
        config["prefix"] = config["plugin_short"]
        config["force_prefix"] = config["plugin_short"]

    return config


def _getch() -> str:
    """获取单个字符输入（跨平台）。"""
    try:
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except Exception:
        return ""


def _show_simple_feature_menu() -> set[int]:
    """简单输入方式（不支持交互式终端时使用）。"""
    print()
    print("=" * 60)
    print("步骤 2/3 - 选择功能模块")
    print("=" * 60)
    print()

    for i, module in enumerate(FEATURE_MODULES, 1):
        tags = []
        if module.get("config"):
            tags.append("配置")
        if module.get("database"):
            tags.append("数据库")
        if module.get("api"):
            tags.append("API")
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        print(f"  [{i}] {module['name']:<12} - {module['desc']}{tag_str}")

    print()
    print("-" * 60)
    print("  提示: 输入数字选择 (如: 1,3,5 或 1-4 或 all)")
    print("        直接回车 = 最小功能集（仅帮助）")
    print("-" * 60)
    print()

    while True:
        choice = input("请选择要包含的功能模块: ").strip()

        if not choice:
            print("  → 使用最小功能集")
            return {1}

        selected = parse_selection(choice, len(FEATURE_MODULES))

        if selected:
            selected.add(1)  # 始终包含帮助功能
            print(f"  → 已选择: {sorted(selected)}")
            return selected

        print("  ⚠ 无效选择，请重新输入")


def show_feature_menu() -> set[int]:
    """显示交互式功能选择菜单。

    使用方向键上下移动，空格选择/取消，回车确认。
    """
    # 检查是否支持交互式终端
    if not sys.stdin.isatty():
        return _show_simple_feature_menu()

    # 帮助功能始终选中且不可取消
    selected = {1}
    current = 0

    def draw_menu():
        """绘制菜单。"""
        # 清屏并移动光标到顶部
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        print("=" * 60)
        print("步骤 2/3 - 选择功能模块")
        print("=" * 60)
        print()
        print("  操作: ↑↓ 移动 | 空格 选择/取消 | 回车 确认")
        print("-" * 60)
        print()

        for i, module in enumerate(FEATURE_MODULES, 1):
            tags = []
            if module.get("config"):
                tags.append("配置")
            if module.get("database"):
                tags.append("数据库")
            if module.get("api"):
                tags.append("API")
            tag_str = f" [{', '.join(tags)}]" if tags else ""

            # 当前选中项高亮
            cursor = "→" if i - 1 == current else " "

            # 选择状态
            if i == 1:  # 帮助功能强制选中
                checkbox = "[✓]"
                status = " (必选)"
            elif i in selected:
                checkbox = "[✓]"
                status = ""
            else:
                checkbox = "[ ]"
                status = ""

            print(f"  {cursor} {checkbox} {module['name']:<12} - {module['desc']}{tag_str}{status}")

        print()
        print("-" * 60)
        selected_names = [FEATURE_MODULES[i - 1]["name"] for i in sorted(selected)]
        print(f"  已选择: {', '.join(selected_names)}")

    # 主循环
    while True:
        draw_menu()

        ch = _getch()

        # 非交互式环境，回退到简单输入方式
        if not ch:
            return _show_simple_feature_menu()

        # 处理特殊键（转义序列）
        if ch == "\x1b":  # ESC
            ch2 = _getch()
            if ch2 == "[":
                ch3 = _getch()
                if ch3 == "A":  # 上箭头
                    current = (current - 1) % len(FEATURE_MODULES)
                elif ch3 == "B":  # 下箭头
                    current = (current + 1) % len(FEATURE_MODULES)
        elif ch == " ":  # 空格 - 切换选择
            idx = current + 1
            if idx != 1:  # 帮助功能不能取消
                if idx in selected:
                    selected.remove(idx)
                else:
                    selected.add(idx)
        elif ch == "\r" or ch == "\n":  # 回车 - 确认
            # 清屏
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            print(f"  → 已选择: {sorted(selected)}")
            return selected
        elif ch == "q" or ch == "Q":  # Q - 退出
            # 清屏
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            print("  → 使用最小功能集")
            return {1}


def preview_config(config: dict[str, str], selected: set[int]) -> None:
    """显示配置和功能预览。"""
    print()
    print("=" * 60)
    print("步骤 3/3 - 配置预览")
    print("=" * 60)
    print()

    print("  [基础信息]")
    print(f"    {config['PluginName']} ({config['plugin_cn_name']})")
    print(f"    默认前缀: {config['force_prefix']}")
    print()

    print("  [功能模块]")
    for i, module in enumerate(FEATURE_MODULES, 1):
        status = "✓" if i in selected else "✗"
        print(f"    [{status}] {module['name']}")
    print()

    files = ["__init__.py", "config.py"]
    for i in selected:
        module = FEATURE_MODULES[i - 1]
        files.extend(module.get("files", []))

    if any(FEATURE_MODULES[i - 1].get("database") for i in selected):
        files.append("database/models.py")
    if any(FEATURE_MODULES[i - 1].get("api") for i in selected):
        files.append("api/client.py")

    print("  [将生成的文件]")
    for f in sorted(set(files)):
        print(f"    • {f}")
    print()


def confirm() -> bool:
    """请求用户确认。"""
    response = input("确认以上配置并继续? (y/n) [默认: y]: ").strip().lower()
    return response in ("y", "yes", "")


def generate_prefix_list(additional: str, quote: str = '"') -> str:
    """将逗号分隔的前缀转换为 Python 列表格式。"""
    if not additional:
        return ""

    prefixes = [p.strip() for p in additional.split(",") if p.strip()]
    if not prefixes:
        return ""

    items = ", ".join(f"{quote}{p}{quote}" for p in prefixes)
    return f", {items}"


def generate_init_py(config: dict[str, str], selected: set[int]) -> str:
    """生成插件 __init__.py 内容。"""
    additional = config.get("additional_prefixes", "")
    additional_list = generate_prefix_list(additional, quote='"')

    return f'''"""
{config['PluginName']} - {config['description']}

Author: {config['author']}
Version: {config['version']}
"""

from gsuid_core.sv import Plugins

Plugins(
    name="{config['PluginName']}",
    pm=6,
    priority=5,
    enabled=True,
    area="ALL",
    prefix=["{config['prefix']}", "{config['plugin_short']}"{additional_list}],
    force_prefix=["{config['force_prefix']}"{additional_list}],
    allow_empty_prefix=False,
    disable_force_prefix=False,
    alias=["{config['plugin_short']}", "{config['plugin_cn_name']}"],
)
'''


def generate_config_py(config: dict[str, str], selected: set[int]) -> str:
    """根据选择的功能生成 config.py 内容。"""
    lines = [
        '"""Plugin configuration."""',
        "",
        "from gsuid_core.utils.plugins_config.models import (",
        "    GsIntConfig,",
        "    GsStrConfig,",
        "    GsBoolConfig,",
        ")",
        "from gsuid_core.utils.plugins_config.gs_config import PluginsConfig",
        "",
        f'config = PluginsConfig("{config["plugin_short"]}")',
        "",
        "# API Configuration",
        'API_URL = config.add_config(',
        '    "API_URL",',
        '    GsStrConfig(title="API URL", desc="Base API endpoint", data=""),',
        ")",
        'API_KEY = config.add_config(',
        '    "API_KEY",',
        '    GsStrConfig(title="API Key", desc="API authentication key", data=""),',
        ")",
    ]

    # 根据功能添加特定配置
    if 4 in selected:  # sign
        lines.extend([
            "",
            "# Sign-in Configuration",
            'ENABLE_SIGN = config.add_config(',
            '    "EnableSign",',
            '    GsBoolConfig(title="Enable Sign", desc="Enable daily sign-in", data=True),',
            ")",
            'SIGN_POINTS = config.add_config(',
            '    "SignPoints",',
            '    GsIntConfig(title="Sign Points", desc="Points per sign-in", data=100),',
            ")",
        ])

    if 3 in selected:  # query
        lines.extend([
            "",
            "# Query Configuration",
            'ENABLE_QUERY = config.add_config(',
            '    "EnableQuery",',
            '    GsBoolConfig(title="Enable Query", desc="Enable info query", data=True),',
            ")",
        ])

    if 2 in selected:  # bind
        lines.extend([
            "",
            "# Bind Configuration",
            'ENABLE_BIND = config.add_config(',
            '    "EnableBind",',
            '    GsBoolConfig(title="Enable Bind", desc="Enable UID binding", data=True),',
            ")",
        ])

    lines.extend([
        "",
        "# Welcome Message",
        'WELCOME_MSG = config.add_config(',
        '    "WelcomeMsg",',
        f'    GsStrConfig(title="Welcome", desc="Welcome message", data="Welcome to {config["plugin_short"]}!"),',
        ")",
    ])

    return "\n".join(lines)


def generate_main_py(config: dict[str, str], selected: set[int]) -> str:
    """生成主插件模块内容。"""
    short = config["plugin_short"]
    name = config["PluginName"]

    lines = [
        '"""Main plugin module."""',
        "",
        "from gsuid_core.sv import SV",
        "from gsuid_core.bot import Bot",
        "from gsuid_core.models import Event",
        "",
        f"from .version import __version__",
    ]

    # 导入配置
    imports = []
    if 4 in selected:
        imports.extend(["ENABLE_SIGN", "SIGN_POINTS"])
    if 3 in selected:
        imports.append("ENABLE_QUERY")
    if 2 in selected:
        imports.append("ENABLE_BIND")

    if imports:
        lines.append(f"from .utils.config import {', '.join(imports)}, WELCOME_MSG")
    else:
        lines.append("from .utils.config import WELCOME_MSG")

    lines.extend([
        "",
        f'sv = SV("{short}", pm=6, priority=5, enabled=True, area="ALL")',
        "",
        "# Help command (always included)",
        '@sv.on_fullmatch(("help", "menu"))',
        "async def help_handler(bot: Bot, event: Event) -> None:",
        '    """Display help message."""',
        f'    msg = f"""🎮 {short} v{{__version__}}',
        "━━━━━━━━━━━━━━",
    ])

    # 根据功能构建帮助内容
    help_items = []
    if 2 in selected:
        help_items.append(f"• {short}bind <UID> - 绑定游戏账号")
    if 3 in selected:
        help_items.append(f"• {short}query - 查询用户信息")
    if 4 in selected:
        help_items.append(f"• {short}sign - 每日签到")
    help_items.append(f"• {short}help - 显示帮助菜单")

    for item in help_items:
        lines.append(f"    {item}")

    lines.extend([
        '"""',
        "    await bot.send(msg)",
        "",
    ])

    # 添加功能处理器
    if 2 in selected:  # bind
        lines.extend([
            '@sv.on_prefix("bind")',
            "async def bind_handler(bot: Bot, event: Event) -> None:",
            '    """Handle UID binding."""',
            "    if not ENABLE_BIND.data:",
            '        await bot.send("⚠️ 绑定功能已禁用")',
            "        return",
            "",
            "    uid = event.text.strip()",
            "    if not uid or not uid.isdigit():",
            '        await bot.send("❌ 无效的UID")',
            "        return",
            "",
            f"    from .utils.database.models import {name}Bind",
            f"    await {name}Bind.set_uid(event.user_id, uid)",
            '    await bot.send(f"✅ UID {uid} 绑定成功")',
            "",
        ])

    if 3 in selected:  # query
        lines.extend([
            '@sv.on_suffix("query")',
            "async def query_handler(bot: Bot, event: Event) -> None:",
            '    """Handle info query."""',
            "    if not ENABLE_QUERY.data:",
            '        await bot.send("⚠️ 查询功能已禁用")',
            "        return",
            "",
            f"    from .utils.database.models import {name}Bind",
            f"    user = await {name}Bind.get_user(event.user_id)",
            "    if not user or not user.uid:",
            f'        await bot.send("❌ 未绑定账号。使用: {short}bind <UID>")',
            "        return",
            "",
            '    await bot.send(f"📊 UID: {user.uid}")',
            "",
        ])

    if 4 in selected:  # sign
        lines.extend([
            '@sv.on_command("sign")',
            "async def sign_handler(bot: Bot, event: Event) -> None:",
            '    """Handle daily sign-in."""',
            "    if not ENABLE_SIGN.data:",
            '        await bot.send("⚠️ 签到功能已禁用")',
            "        return",
            "",
            f"    from .utils.database.models import {name}Bind, {name}Sign",
            f"    user = await {name}Bind.get_user(event.user_id)",
            "    if not user or not user.uid:",
            f'        await bot.send("❌ 未绑定账号。使用: {short}bind <UID>")',
            "        return",
            "",
            f"    points = SIGN_POINTS.data",
            f"    await {name}Sign.sign(event.user_id, user.uid, points)",
            '    await bot.send(f"🎉 签到成功！获得 {points} 积分")',
            "",
        ])

    return "\n".join(lines)


def generate_database_models(config: dict[str, str], selected: set[int]) -> str:
    """生成数据库模型。"""
    name = config["PluginName"]
    short = config["plugin_short"]

    lines = [
        '"""Database models."""',
        "",
        "from typing import Optional",
        "from datetime import datetime",
        "",
        "from sqlmodel import Field",
        "from gsuid_core.utils.database.base_models import BaseModel, with_session, insert_or_update",
        "",
        f"class {name}Bind(BaseModel, table=True):",
        f'    """User binding table for {short}."""',
        f'    __tablename__ = "{short}_bind"',
        "",
        '    user_id: str = Field(primary_key=True, description="User ID")',
        '    uid: Optional[str] = Field(default=None, description="Game UID")',
        '    bot_id: str = Field(default="", description="Bot ID")',
        "",
        "    @classmethod",
        "    @with_session",
        "    async def set_uid(cls, session, user_id: str, uid: str) -> bool:",
        '        """Set user UID."""',
        "        try:",
        '            await insert_or_update(session, cls, {"user_id": user_id, "uid": uid})',
        "            return True",
        "        except Exception:",
        "            return False",
        "",
        "    @classmethod",
        "    @with_session",
        "    async def get_user(cls, session, user_id: str):",
        '        """Get user by ID."""',
        "        from sqlalchemy import select",
        "        result = await session.execute(select(cls).where(cls.user_id == user_id))",
        "        return result.scalar_one_or_none()",
        "",
    ]

    if 4 in selected:  # sign
        lines.extend([
            f"class {name}Sign(BaseModel, table=True):",
            f'    """Sign-in record table for {short}."""',
            f'    __tablename__ = "{short}_sign"',
            "",
            '    user_id: str = Field(primary_key=True, description="User ID")',
            '    uid: str = Field(default="", description="Game UID")',
            '    sign_date: datetime = Field(default_factory=datetime.now)',
            '    points: int = Field(default=0)',
            "",
            "    @classmethod",
            "    @with_session",
            "    async def sign(cls, session, user_id: str, uid: str, points: int) -> bool:",
            '        """Record sign-in."""',
            "        try:",
            '            await insert_or_update(session, cls, {',
            '                "user_id": user_id, "uid": uid, "points": points',
            "            })",
            "            return True",
            "        except Exception:",
            "            return False",
            "",
        ])

    return "\n".join(lines)


def generate_api_client(config: dict[str, str]) -> str:
    """生成 API 客户端。"""
    return '''"""API client for external requests."""

import httpx
from typing import Optional, Any

from gsuid_core.logger import logger
from .config import API_URL, API_KEY


class APIClient:
    """HTTP client for API requests."""

    def __init__(self) -> None:
        self.base_url = API_URL.data.rstrip("/")
        self.api_key = API_KEY.data

    async def request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[dict[str, Any]]:
        """Send HTTP request."""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    async def get_user_info(self, uid: str) -> Optional[str]:
        """Get user info by UID."""
        data = await self.request("GET", f"/user/{uid}")
        return str(data) if data else None
'''


def create_plugin(base_path: Path, config: dict[str, str], selected: set[int]) -> None:
    """创建插件目录结构并生成文件。"""
    name = config["PluginName"]
    short = config["plugin_short"]

    # 创建目录
    dirs = [base_path / name, base_path / name / "utils"]
    if any(FEATURE_MODULES[i - 1].get("database") for i in selected):
        dirs.append(base_path / name / "utils" / "database")
    if any(FEATURE_MODULES[i - 1].get("api") for i in selected):
        dirs.append(base_path / name / "utils" / "api")

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  创建目录: {d.relative_to(base_path)}")

    plugin_dir = base_path / name

    # 生成文件
    files_to_write = [
        (plugin_dir / "__init__.py", generate_init_py(config, selected)),
        (plugin_dir / "version.py", f'__version__ = "{config["version"]}"\n'),
        (plugin_dir / "utils" / "__init__.py", ""),
        (plugin_dir / "utils" / "config.py", generate_config_py(config, selected)),
        (plugin_dir / f"{short}.py", generate_main_py(config, selected)),
        (plugin_dir / "__full__.py", f'from . import *\nfrom .{short} import *\n'),
    ]

    if any(FEATURE_MODULES[i - 1].get("database") for i in selected):
        files_to_write.extend([
            (plugin_dir / "utils" / "database" / "__init__.py", ""),
            (plugin_dir / "utils" / "database" / "models.py", generate_database_models(config, selected)),
        ])

    if any(FEATURE_MODULES[i - 1].get("api") for i in selected):
        files_to_write.extend([
            (plugin_dir / "utils" / "api" / "__init__.py", ""),
            (plugin_dir / "utils" / "api" / "client.py", generate_api_client(config)),
        ])

    for path, content in files_to_write:
        path.write_text(content, encoding="utf-8")
        print(f"  生成文件: {path.relative_to(base_path)}")


def show_generation_mode() -> str:
    """选择生成模式：覆盖本地或生成新插件。"""
    print("=" * 60)
    print("选择生成模式")
    print("=" * 60)
    print()
    print("  [1] 覆盖本地 - 在当前目录直接生成插件（覆盖现有文件）")
    print("       适用于：基于模板修改开发自己的插件")
    print()
    print("  [2] 生成新插件 - 在父目录创建新的插件目录")
    print("       适用于：创建全新的插件项目")
    print()
    print("-" * 60)
    print()
    
    while True:
        choice = input("请选择 [1/2] (默认: 2): ").strip()
        
        if not choice:
            choice = "2"
        
        if choice == "1":
            print("  → 选择: 覆盖本地模式")
            print()
            return "local"
        elif choice == "2":
            print("  → 选择: 生成新插件模式")
            print()
            return "new"
        else:
            print("  ⚠ 无效选择，请输入 1 或 2")


def main() -> int:
    """主入口函数。"""
    print("=" * 60)
    print("GSUID 插件模板 - 交互式生成器")
    print("=" * 60)
    print()

    # 步骤 0: 选择生成模式
    generation_mode = show_generation_mode()

    # 步骤 1: 基础配置
    config = show_basic_config()

    # 步骤 2: 功能选择
    selected = show_feature_menu()

    # 步骤 3: 预览
    preview_config(config, selected)

    # 确认
    if not confirm():
        print("\n已取消。")
        return 1

    # 生成
    print()
    print("=" * 60)
    print("开始生成插件...")
    print("=" * 60)
    print()

    # 根据模式确定输出目录
    script_dir = Path(__file__).parent
    if generation_mode == "local":
        # 覆盖本地：在当前目录生成
        output_dir = script_dir
        print(f"模式: 覆盖本地 ({output_dir})")
        print("⚠️  警告: 这将覆盖当前目录中的现有文件！")
        print()
        
        # 再次确认覆盖操作
        confirm_overwrite = input("确认覆盖? [y/N]: ").strip().lower()
        if confirm_overwrite not in ("y", "yes"):
            print("\n已取消。")
            return 1
    else:
        # 生成新插件：在父目录创建新目录
        output_dir = script_dir.parent
        print(f"模式: 生成新插件 ({output_dir})")

    create_plugin(output_dir, config, selected)

    print()
    print("=" * 60)
    print("✅ 插件生成完成！")
    print("=" * 60)
    print()
    print(f"插件位置: {output_dir / config['PluginName']}")
    print()
    
    if generation_mode == "local":
        print("下一步:")
        print("1. 检查生成的代码并根据需要修改")
        print("2. 编辑 utils/config.py 配置API地址")
        print("3. 编辑 utils/api/client.py 实现API请求逻辑")
        print("4. 运行 gsuid_core 测试插件")
        print()
        print("提示: 当前目录已更新为插件代码，可以直接开始开发")
    else:
        print("下一步:")
        print("1. 检查生成的代码并根据需要修改")
        print("2. 编辑 utils/config.py 配置API地址")
        print("3. 编辑 utils/api/client.py 实现API请求逻辑")
        print("4. 将插件复制到 gsuid_core/plugins/ 目录")
        print()
        print("提示: 模板目录保持不变，可以继续使用 init_plugin.py 生成更多插件")

    return 0


if __name__ == "__main__":
    sys.exit(main())
