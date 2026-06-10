<!-- markdownlint-disable MD033 -->

# VrChatUID

<p align="center">
  <a href="https://vrchat.com/"><img src="./ICON.png" width="256" height="256" alt="VrChatUID"></a>
</p>
<h1 align = "center">VrChatUID</h1>
<h4 align = "center">基于 gsuid_core 的 VRChat 查询 Bot 插件</h4>

> [早柚核心 (gsuid_core)](https://github.com/Genshin-bots/gsuid_core) 扩展插件

## 安装

```
core安装插件VrChatUID
core重启
```

## 使用

```
vrc登录 用户名 密码       # 登录（支持 2FA、多账号绑定）
vrc切换uid <序号/uid>     # 切换当前活跃账号
vrc解绑 <uid>             # 解绑指定账号
vrc我的信息               # 查看当前账号
vrc帮助                  # 查看完整命令
vrc帮助 <分类>           # 查看指定分类命令
vrc注销                  # 注销所有账号
```

## 功能（按 SDK 模块分类）

| 分类 | 命令 | 说明 |
|------|------|------|
| **认证** | `vrc登录` / `vrc注销` / `vrc解绑` / `vrc切换uid` / `vrc我的信息` | 登录、注销、解绑、切换、账号信息（支持 2FA、多账号） |
| **好友** | `vrc好友` | 查看好友列表 |
| **用户** | `vrc搜索用户` / `添加` / `好友状态` | 搜索用户、发送好友请求 |
| **通知** | `vrc显示通知` / `接受` / `忽略` / `删除通知` | 通知列表、接受/忽略好友请求 |
| **世界** | `vrc搜索世界` | 搜索世界 |
| **收藏** | `vrc收藏列表` / `vrc收藏组列表` / `vrc收藏限制` / `vrc添加收藏` / `vrc删除收藏` / `vrc收藏组详情` / `vrc清空收藏组` | 收藏全功能管理 |
| **群组** | `vrc搜索群组` / `vrc群组信息` / `vrc群组成员` / `vrc群组角色` / `vrc群组公告` / `vrc群组实例` / `vrc加入群组` / `vrc离开群组` / `vrc群组请求` / `vrc处理请求` / `vrc邀请用户` / `vrc踢出成员` / `vrc封禁列表` / `vrc封禁成员` / `vrc解除封禁` / `vrc审计日志` / `vrc我的群组信息` / `vrc更新群组代表` / `vrc创建公告` / `vrc帖子列表` / `vrc创建帖子` | 群组全功能管理 |
| **经济** | `vrc余额` / `vrc账户` / `vrc订阅` / `vrctilia` / `vrc收益` | 余额、订阅、Tilia |

发送 `vrc帮助 <分类>` 获取分类详细命令，例如 `vrc帮助 群组`。

## 管理员

- [x] Web 控制台绑定管理（`VrChatBindAdmin`）
- [x] Web 控制台账号凭证管理（`VrChatUserAdmin`）

## 数据模型

- `VrChatBind` (Bind) - 单用户对多 VRChat 账号绑定，`uid` 字段用 `_` 分隔
- `VrChatUser` (User) - 单个 VRChat 账号的完整凭证（vrc_uid、邮箱、密码、cookie、display_name）
- 支持 `vrc切换uid` 在多账号间自由切换

## 开发

- Python 3.12+（与 gsuid_core 主框架一致）
- 依赖：`vrchatapi`
- 使用 `uv` 管理依赖，`ruff` 格式化

## 说明

- 本项目仅供学习使用，请勿用于商业用途
- 数据来源于 VRChat API
