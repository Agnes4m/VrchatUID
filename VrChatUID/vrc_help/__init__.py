from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

sv = SV("vrc帮助")


@sv.on_fullmatch(("vrc帮助", "vrchelp"))
async def vrc_help(bot: Bot, ev: Event) -> None:
    msg = """【VRChat 帮助信息】

【登录/账号】
vrc登录 - 登录 VRChat 账号
vrc注销/vrc退出登录 - 注销账号
vrc我的信息/vrc状态 - 查看账号信息

【好友】
vrc好友/vrcfl - 查看好友列表
vrc搜索用户/vrcus/vrcsu - 搜索VRChat用户
添加 序号 - 向搜索结果发送好友请求
好友状态 序号 - 查看与用户的好友状态

【通知】
vrc显示通知/vrcsn - 显示通知列表
接受 序号 - 接受好友请求
忽略 序号 - 忽略通知
删除通知 序号 - 删除通知

【世界】
vrc搜索世界/vrcws - 搜索世界

【收藏】
vrc收藏列表/vrcfl 类型 - 查看收藏列表(avatar/world/friend)
vrc收藏组列表/vrcfgl - 查看收藏组列表
vrc收藏限制/vrcflim - 查看收藏容量限制
vrc添加收藏/vrcfav 类型 ID [标签] - 添加收藏
vrc删除收藏/vrcfdel 收藏ID - 删除收藏
vrc收藏组详情/vrcfg 类型 名称 - 查看收藏组详情
vrc清空收藏组/vrcfcg 类型 名称 - 清空收藏组

【群组】
vrc搜索群组/vrcsg 关键词 - 搜索群组
vrc群组信息/vrcgi 群组ID - 查看群组信息
vrc群组成员/vrcgm 群组ID - 查看群组成员
vrc群组角色/vrcgr 群组ID - 查看群组角色
vrc群组公告/vrcga 群组ID - 查看群组公告
vrc群组实例/vrcgi2 群组ID - 查看群组实例
vrc加入群组 序号 - 加入搜索到的群组
vrc离开群组/vrclg 群组ID - 离开群组
vrc群组请求/vrcgreq 群组ID - 查看入群请求
vrc处理请求 序号 accept/reject - 审批请求
vrc邀请用户/vrcgui 群组ID 用户ID - 邀请用户
vrc踢出成员/vrcgmk 群组ID 用户ID - 踢出成员
vrc封禁列表/vrcgb 群组ID - 查看封禁列表
vrc封禁成员/vrcgbm 群组ID 用户ID - 封禁成员
vrc解除封禁/vrcgub 群组ID 用户ID - 解除封禁
vrc审计日志/vrcgal 群组ID - 查看审计日志
vrc我的群组信息/vrcmgm 群组ID - 查看我的成员信息
vrc更新群组代表/vrcugr 群组ID [取消] - 设置代表群组
vrc创建公告/vrcgca 群组ID 标题 [内容] - 创建公告
vrc帖子列表/vrcgpl 群组ID - 查看帖子列表
vrc创建帖子/vrcgcp 群组ID 标题 [内容] - 创建帖子

【经济】
vrc余额/vrcbalance - 查询余额
vrc账户/vrceconomy - 查询经济账户
vrc订阅/vrcsubs - 查询订阅信息
vrctilia - 查询Tilia状态
vrc收益/vrcearnings - 查询收益信息

【帮助】
vrc帮助/vrchelp - 显示此帮助信息"""
    await bot.send(msg)
