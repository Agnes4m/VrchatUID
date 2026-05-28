from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

sv = SV("vrc帮助")


@sv.on_fullmatch(("vrc帮助", "vrchelp"))
async def vrc_help(bot: Bot, ev: Event) -> None:
    msg = """【VRChat 查询 帮助】

【登录】
vrc登录 - 登录 VRChat 账号

【好友】
vrc好友 - 查看好友列表

【世界】
vrc搜索世界 - 搜索 VRChat 世界

【其他】
vrc帮助 - 显示帮助信息
vrc我的信息 - 查看已登录账号"""
    await bot.send(msg)
