"""VRChatUID 帮助图模块

参考 GenshinUID-docs/docs/CodePlugins/PluginsHelp.md 实现：
- 通过 help.json 定义命令
- 使用 gsuid_core.help.draw_new_plugin_help.get_new_help 渲染图片
- 通过 register_help 注册到全局帮助系统
"""

import json
from pathlib import Path

from gsuid_core.bot import Bot
from gsuid_core.help.draw_new_plugin_help import get_new_help
from gsuid_core.help.model import PluginHelp
from gsuid_core.help.utils import register_help
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from PIL import Image

ICON = Path(__file__).parent.parent.parent / "ICON.png"
HELP_DATA = Path(__file__).parent / "help.json"
ICON_PATH = Path(__file__).parent / "icon_path"
TEXT_PATH = Path(__file__).parent / "texture2d"
PLUGIN_NAME = "VrChatUID"

sv = SV("帮助")


async def get_help_data() -> dict[str, PluginHelp]:
    """读取 help.json"""
    with open(HELP_DATA, encoding="utf-8") as f:
        return json.load(f)


async def get_vrc_help(user_pm: int = 6) -> bytes:
    """生成 VRChatUID 帮助图"""
    plugin_help = await get_help_data()
    plugin_icon = Image.open(ICON)
    return await get_new_help(
        plugin_name=PLUGIN_NAME,
        plugin_info={"v1.0": ""},
        plugin_icon=plugin_icon,
        plugin_help=plugin_help,
        plugin_prefix="",
        help_mode="dark",
        banner_sub_text="💫 VRChat 账号管理插件",
        banner_bg=Image.open(TEXT_PATH / "banner_bg_dark.jpg"),
        help_bg=Image.open(TEXT_PATH / "bg_dark.jpg"),
        cag_bg=Image.open(TEXT_PATH / "cag_bg_dark.png"),
        item_bg=Image.open(TEXT_PATH / "item_bg_dark.png"),
        icon_path=ICON_PATH,
        enable_cache=True,
        pm=user_pm,
    )


# 注册到全局帮助系统（参考文档 register_help）
register_help(PLUGIN_NAME, "帮助", Image.open(ICON))


@sv.on_command(("帮助", "help"))
async def send_help_img(bot: Bot, ev: Event) -> None:
    """发送帮助图（带降级到文本）"""
    logger.info("开始执行[vrc帮助]")
    user_pm = getattr(ev, "user_pm", 6)
    try:
        image_bytes = await get_vrc_help(user_pm)

        await bot.send(image_bytes)
    except Exception as e:
        logger.warning(f"帮助图渲染失败，降级到文本: {e}")
        await bot.send(_fallback_text())


def _fallback_text() -> str:
    """图片渲染失败时的纯文本降级"""
    return """【VRChatUID 帮助】

【认证】vrc登录 / vrc注销 / vrc解绑 <uid> / vrc切换uid / vrc我的信息
【好友】vrc好友
【用户】vrc搜索用户 <关键词> / 添加 <序号> / 好友状态 <序号>
【通知】vrc显示通知 / 接受 / 忽略 / 删除通知
【世界】vrc搜索世界 <关键词>
【收藏】vrc收藏列表 / vrc收藏组列表 / vrc收藏限制 / vrc添加收藏 / vrc删除收藏
【群组】vrc搜索群组 / vrc群组信息 / vrc群组成员 / vrc加入群组 / vrc踢出成员
【经济】vrc余额 / vrc账户 / vrc订阅 / vrctilia / vrc收益

发送 vrc帮助 <分类> 查看详细命令（即将支持）
"""
