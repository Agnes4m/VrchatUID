# GSUID Plugin Template

基于 [GenshinUID Core](https://github.com/Genshin-bots/gsuid_core) 的标准插件开发模板

<p align="center">
  <a href="https://github.com/Genshin-bots/gsuid_core">
    <img src="https://img.shields.io/badge/Based%20on-GenshinUID%20Core-blue?style=flat-square" alt="Based on">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python" alt="Python">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/Package%20Manager-UV-purple?style=flat-square&logo=python" alt="UV">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/Linter-Ruff-orange?style=flat-square" alt="Ruff">
  </a>
  <br>
  <a href="./docs/method-github-template.md">
    <img src="https://img.shields.io/badge/Use-GitHub%20Template-green?style=flat-square&logo=github" alt="Use GitHub Template">
  </a>
  <a href="./docs/method-template-package.md">
    <img src="https://img.shields.io/badge/Download-Template%20Package-blue?style=flat-square&logo=download" alt="Download Template">
  </a>
  <a href="./docs/method-git-clone.md">
    <img src="https://img.shields.io/badge/Clone-Git%20Repository-yellow?style=flat-square&logo=git" alt="Git Clone">
  </a>
</p>

## 📖 简介

这是一个为 GenshinUID Core 框架设计的通用插件模板，提供了标准化的插件结构和最佳实践。无论你是开发游戏查询插件还是其他功能插件，都可以使用此模板快速开始。

## ✨ 特性

- 🚀 **快速开始** - 交互式初始化脚本，一键生成插件
- 🏗️ **标准结构** - 遵循 GenshinUID Core 最佳实践
- 📝 **多种命令** - 支持前缀、后缀、完全匹配、正则等多种触发方式
- 🗄️ **数据库集成** - 内置用户绑定、签到等数据模型
- ⚙️ **配置管理** - 统一的配置系统，支持热重载
- 🎨 **帮助系统** - 自动生成帮助图片，集成核心帮助
- 🔧 **Web控制台** - 自动注册数据库管理页面
- 🐍 **代码质量** - 内置 pre-commit 代码格式检查

## 🚀 使用模板

我们提供了 **三种方式** 来使用此模板，选择最适合你的：

| 方式 | 适用场景 | 特点 |
|------|---------|------|
| **[方式一：GitHub 模板按钮](./docs/method-github-template.md)** | 需要版本控制 | 点击按钮创建新仓库，保留 Git 历史 |
| **[方式二：下载模板包](./docs/method-template-package.md)** | 快速开始 | 下载纯净模板包，无 Git 历史 |
| **[方式三：Git 克隆复制](./docs/method-git-clone.md)** | 熟悉 Git | 手动克隆清理，完全可控 |

### 推荐选择

- 🔰 **新手推荐**：使用 [方式二：下载模板包](./docs/method-template-package.md)，简单直接
- 💻 **开发者推荐**：使用 [方式一：GitHub 模板按钮](./docs/method-github-template.md)，便于版本管理
- 🔧 **高级用户**：使用 [方式三：Git 克隆复制](./docs/method-git-clone.md)，完全自定义

---

## 🚀 快速开始（方式三：Git 克隆）

### 1. 克隆模板

```bash
cd gsuid_core/plugins
git clone https://github.com/你的组织/gsuid_plugin_template.git
cd gsuid_plugin_template

# 清理 Git 历史（重要！）
rm -rf .git
git init
git add .
git commit -m "Initial commit"

# 重命名为你的插件
cd ..
mv gsuid_plugin_template MyPlugin
cd MyPlugin
```

### 2. 安装 UV（推荐）

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows
```

### 3. 初始化插件

```bash
python init_plugin.py
```

**步骤 0：选择生成模式**
- **覆盖本地** - 在当前目录直接生成插件（覆盖现有文件）
  - 适用于：基于模板修改开发自己的插件
- **生成新插件** - 在父目录创建新的插件目录
  - 适用于：创建全新的插件项目

**步骤 1-3：配置插件**
- 插件英文名称（用于类名）
- 插件短名（用于命令前缀）
- 插件中文名称
- 游戏名称
- 作者、邮箱、版本等信息
- 额外的命令前缀（可选，支持多前缀）

### 4. 安装依赖（使用 UV）

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 或安装完整依赖
uv pip install -e ".[full]"
```

### 5. 配置插件

编辑生成的配置文件：

```python
# MyPlugin/utils/config.py
API_URL = config.add_config(
    "API_URL",
    GsStrConfig(
        title="API地址",
        desc="第三方API的基础地址",
        data="https://api.example.com",  # 修改为你的API地址
    ),
)
```

### 6. 实现功能

在 `MyPlugin/__init__.py` 中添加你的命令：

```python
@sv.on_command("我的命令")
async def my_command(bot: Bot, event: Event):
    await bot.send("命令执行成功！")
```

### 7. 运行测试

启动 GenshinUID Core，测试你的插件：

```
mp帮助      # 显示帮助
mp绑定UID   # 绑定账号
mp查询      # 查询信息
mp签到      # 每日签到
```

## 📦 UV 常用命令

```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -e ".[dev]"

# 同步依赖（根据 pyproject.toml）
uv pip compile pyproject.toml -o requirements.txt
uv pip sync requirements.txt

# 导出当前依赖
uv pip freeze > requirements.txt

# 运行命令
uv run python -m myplugin

# 更新依赖
uv pip install --upgrade -e ".[dev]"
```

## � 目录结构

```
MyPlugin/
├── __init__.py              # 插件入口（Plugins配置）
├── __full__.py              # 完整导入
├── version.py               # 版本信息
├── README.md                # 插件说明
├── init_plugin.py           # 初始化脚本
└── MyPlugin/                # 主模块
    ├── __init__.py          # 命令注册（SV实例）
    ├── version.py           # 版本信息
    ├── utils/
    │   ├── __init__.py
    │   ├── config.py        # 配置管理
    │   ├── database/
    │   │   ├── __init__.py
    │   │   └── models.py    # 数据库模型
    │   └── api/
    │       ├── __init__.py
    │       ├── client.py    # API客户端
    │       └── models.py    # API数据模型
    └── help/
        ├── __init__.py
        └── get_help.py      # 帮助图片生成
```

## 📝 命令触发方式

| 装饰器 | 说明 | 示例 |
|--------|------|------|
| `on_fullmatch` | 完全匹配 | `mp帮助` |
| `on_prefix` | 前缀匹配 | `mp绑定UID 123456` |
| `on_suffix` | 后缀匹配 | `我的信息mp` |
| `on_command` | 命令匹配 | `mp签到` |
| `on_regex` | 正则匹配 | `mp查询(.+)` |

## ⚙️ 配置项

模板内置以下配置项：

| 配置名 | 类型 | 说明 |
|--------|------|------|
| `API_URL` | 字符串 | API基础地址 |
| `API_KEY` | 字符串 | API密钥 |
| `API_TIMEOUT` | 整数 | 请求超时时间 |
| `EnableSign` | 布尔 | 启用签到功能 |
| `EnableQuery` | 布尔 | 启用查询功能 |
| `EnableBind` | 布尔 | 启用绑定功能 |
| `SignPoints` | 整数 | 签到基础积分 |
| `MaxBindUID` | 整数 | 最大绑定UID数 |

## 🗄️ 数据库模型

模板提供三个基础模型：

- **`MyPluginBind`** - 用户UID绑定表
- **`MyPluginUser`** - 用户Cookie表
- **`MyPluginSign`** - 签到记录表

自动注册到 Web 控制台，可在网页端管理数据。

## 🛠️ 开发指南

### 添加新命令

```python
@sv.on_fullmatch(("新命令",))
async def new_command(bot: Bot, event: Event):
    """命令说明"""
    await bot.send("执行结果")
```

### 使用数据库

```python
from .utils.database.models import MyPluginBind

# 绑定UID
await MyPluginBind.set_uid(event.user_id, "123456")

# 查询用户
user = await MyPluginBind.get_user(event.user_id)
```

### 发送消息

```python
# 文本
await bot.send("消息内容")

# 图片
from gsuid_core.segment import MessageSegment
await bot.send(MessageSegment.image("path/to/image.png"))
```

### 日志输出

```python
from gsuid_core.logger import logger

logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

## 🔧 代码规范

项目使用 pre-commit 进行代码格式检查：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

## 📚 参考文档

- [GenshinUID Core 文档](https://github.com/Genshin-bots/gsuid_core)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 [MIT](LICENSE) 许可证开源。

---

<p align="center">
  Made with ❤️ for GenshinUID Core
</p>
