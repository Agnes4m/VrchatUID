from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

sv = SV("vrc帮助")


@sv.on_fullmatch(("vrc帮助", "vrchelp"))
async def vrc_help(bot: Bot, ev: Event) -> None:
    msg = """【VRChat 帮助信息】

> 按 SDK 模块分类，使用 `vrc帮助 <分类>` 查看详情
> 可用分类：认证、好友、用户、通知、世界、收藏、群组、经济

【认证 (Authentication)】
vrc登录 - 登录 VRChat 账号
vrc注销/vrc退出登录 - 注销账号
vrc我的信息/vrc状态 - 查看账号信息

【好友 (Friends)】
vrc好友/vrcfl - 查看好友列表

【用户 (Users)】
vrc搜索用户/vrcus/vrcsu - 搜索VRChat用户
添加 序号 - 向搜索结果发送好友请求
好友状态 序号 - 查看与用户的好友状态

【通知 (Notifications)】
vrc显示通知/vrcsn - 显示通知列表
接受 序号 - 接受好友请求
忽略 序号 - 忽略通知
删除通知 序号 - 删除通知

【世界 (Worlds)】
vrc搜索世界/vrcws - 搜索世界

【收藏 (Favorites)】
vrc收藏列表/vrcfl 类型 - 查看收藏列表(avatar/world/friend)
vrc收藏组列表/vrcfgl - 查看收藏组列表
vrc收藏限制/vrcflim - 查看收藏容量限制
vrc添加收藏/vrcfav 类型 ID [标签] - 添加收藏
vrc删除收藏/vrcfdel 收藏ID - 删除收藏
vrc收藏组详情/vrcfg 类型 名称 - 查看收藏组详情
vrc清空收藏组/vrcfcg 类型 名称 - 清空收藏组

【群组 (Groups)】
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

【经济 (Economy)】
vrc余额/vrcbalance - 查询余额
vrc账户/vrceconomy - 查询经济账户
vrc订阅/vrcsubs - 查询订阅信息
vrctilia - 查询Tilia状态
vrc收益/vrcearnings - 查询收益信息

【帮助】
vrc帮助/vrchelp - 显示此帮助信息
vrc帮助 <分类> - 查看指定分类的详细命令"""
    await bot.send(msg)


@sv.on_command(("vrc帮助", "vrchelp"))
async def vrc_help_category(bot: Bot, ev: Event) -> None:
    category = ev.text.strip()

    help_data = {
        "认证": {
            "name": "认证 (Authentication)",
            "module": "vrchatapi.AuthenticationApi / client.py",
            "commands": [
                ("vrc登录 用户名 密码", "登录 VRChat 账号（支持 2FA）"),
                ("vrc注销 / vrc退出登录", "注销账号"),
                ("vrc我的信息 / vrc状态", "查看账号信息"),
            ],
        },
        "好友": {
            "name": "好友 (Friends)",
            "module": "vrchatapi.FriendsApi / friend.py",
            "commands": [
                ("vrc好友 / vrcfl", "查看好友列表（在线/离线）"),
            ],
        },
        "用户": {
            "name": "用户 (Users)",
            "module": "vrchatapi.UsersApi / users.py",
            "commands": [
                ("vrc搜索用户 关键词 / vrcus / vrcsu", "搜索VRChat用户"),
                ("添加 序号", "向搜索结果发送好友请求"),
                ("好友状态 序号", "查看与用户的好友状态"),
            ],
        },
        "通知": {
            "name": "通知 (Notifications)",
            "module": "vrchatapi.NotificationsApi / notifications.py",
            "commands": [
                ("vrc显示通知 / vrcsn [数量]", "显示通知列表"),
                ("接受 序号", "接受好友请求"),
                ("忽略 序号", "忽略通知"),
                ("删除通知 序号", "删除通知"),
            ],
        },
        "世界": {
            "name": "世界 (Worlds)",
            "module": "vrchatapi.WorldsApi / world.py",
            "commands": [
                ("vrc搜索世界 关键词 / vrcws", "搜索VRChat世界"),
            ],
        },
        "收藏": {
            "name": "收藏 (Favorites)",
            "module": "vrchatapi.FavoritesApi / favorites.py",
            "commands": [
                ("vrc收藏列表 类型 / vrcfl", "查看收藏列表(avatar/world/friend)"),
                ("vrc收藏组列表 / vrcfgl", "查看收藏组列表"),
                ("vrc收藏限制 / vrcflim", "查看收藏容量限制"),
                ("vrc添加收藏 类型 ID [标签] / vrcfav", "添加收藏"),
                ("vrc删除收藏 收藏ID / vrcfdel", "删除收藏"),
                ("vrc收藏组详情 类型 名称 / vrcfg", "查看收藏组详情"),
                ("vrc清空收藏组 类型 名称 / vrcfcg", "清空收藏组"),
            ],
        },
        "群组": {
            "name": "群组 (Groups)",
            "module": "vrchatapi.GroupsApi / groups.py",
            "commands": [
                ("vrc搜索群组 关键词 / vrcsg", "搜索群组"),
                ("vrc群组信息 群组ID / vrcgi", "查看群组信息"),
                ("vrc群组成员 群组ID / vrcgm", "查看群组成员"),
                ("vrc群组角色 群组ID / vrcgr", "查看群组角色"),
                ("vrc群组公告 群组ID / vrcga", "查看群组公告"),
                ("vrc群组实例 群组ID / vrcgi2", "查看群组实例"),
                ("加入 序号", "加入搜索到的群组"),
                ("vrc离开群组 群组ID / vrclg", "离开群组"),
                ("vrc群组请求 群组ID / vrcgreq", "查看入群请求"),
                ("处理请求 序号 accept/reject", "审批请求"),
                ("vrc邀请用户 群组ID 用户ID / vrcgui", "邀请用户"),
                ("vrc踢出成员 群组ID 用户ID / vrcgmk", "踢出成员"),
                ("vrc封禁列表 群组ID / vrcgb", "查看封禁列表"),
                ("vrc封禁成员 群组ID 用户ID / vrcgbm", "封禁成员"),
                ("vrc解除封禁 群组ID 用户ID / vrcgub", "解除封禁"),
                ("vrc审计日志 群组ID / vrcgal", "查看审计日志"),
                ("vrc我的群组信息 群组ID / vrcmgm", "查看我的成员信息"),
                ("vrc更新群组代表 群组ID [取消] / vrcugr", "设置代表群组"),
                ("vrc创建公告 群组ID 标题 [内容] / vrcgca", "创建公告"),
                ("vrc帖子列表 群组ID / vrcgpl", "查看帖子列表"),
                ("vrc创建帖子 群组ID 标题 [内容] / vrcgcp", "创建帖子"),
            ],
        },
        "经济": {
            "name": "经济 (Economy)",
            "module": "vrchatapi.EconomyApi / economy.py",
            "commands": [
                ("vrc余额 / vrcbalance", "查询余额"),
                ("vrc账户 / vrceconomy", "查询经济账户"),
                ("vrc订阅 / vrcsubs", "查询订阅信息"),
                ("vrctilia", "查询Tilia状态"),
                ("vrc收益 / vrcearnings", "查询收益信息"),
            ],
        },
    }

    if not category or category == "全部":
        await vrc_help(bot, ev)
        return

    if category not in help_data:
        available = "、".join(help_data.keys())
        await bot.send(f"未找到分类「{category}」\n\n可用分类：{available}\n\n发送 `vrc帮助` 查看完整列表")
        return

    info = help_data[category]
    msg = f"【{info['name']}】\n"
    msg += f"SDK 模块: {info['module']}\n\n"

    for cmd, desc in info["commands"]:
        msg += f"• {cmd}\n  {desc}\n\n"

    msg += "发送 `vrc帮助` 返回完整列表"
    await bot.send(msg)
