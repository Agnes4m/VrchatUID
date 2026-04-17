# 方式二：下载模板包

从 GitHub Releases 下载纯净的模板压缩包，解压后即可使用。

## ✨ 特点

- ✅ 纯净的模板文件，无 Git 历史
- ✅ 无需 Git 操作，简单直接
- ✅ 文件体积更小
- ✅ 适合不熟悉 Git 的用户

## 🚀 使用步骤

### 步骤 1：下载模板包

1. 访问仓库的 **Releases** 页面
   - 链接：`https://github.com/你的组织/gsuid_plugin_template/releases`

2. 找到最新版本（Latest）

3. 下载适合你系统的压缩包：
   - **Windows 用户**：下载 `.zip` 文件
   - **Linux/Mac 用户**：下载 `.tar.gz` 文件

### 步骤 2：解压文件

#### Windows

```powershell
# 使用 PowerShell 解压
Expand-Archive -Path "gsuid-plugin-template-x.x.x.zip" -DestinationPath "gsuid_core/plugins/"

# 或者使用 7-Zip
7z x gsuid-plugin-template-x.x.x.zip -ogsuid_core/plugins/
```

#### Linux/Mac

```bash
# 解压 tar.gz
tar -xzf gsuid-plugin-template-x.x.x.tar.gz -C gsuid_core/plugins/

# 或者解压 zip
unzip gsuid-plugin-template-x.x.x.zip -d gsuid_core/plugins/
```

### 步骤 3：重命名目录

```bash
cd gsuid_core/plugins/

# 将模板目录重命名为你的插件名称
mv gsuid-plugin-template-x.x.x MyPluginUID
```

### 步骤 4：初始化插件

```bash
cd MyPluginUID

# 运行初始化脚本
python init_plugin.py
```

**选择生成模式：**

由于是下载的模板包，推荐选择 **"覆盖本地"** 模式：

```
选择生成模式
============================================================
  [1] 覆盖本地 - 在当前目录直接生成插件（覆盖现有文件）
       适用于：基于模板修改开发自己的插件

  [2] 生成新插件 - 在父目录创建新的插件目录
       适用于：创建全新的插件项目

------------------------------------------------------------

请选择 [1/2] (默认: 2): 1
  → 选择: 覆盖本地模式
```

**配置插件信息：**
- 插件英文名称（如：`MyPluginUID`）
- 插件短名（如：`mp`）
- 插件中文名称（如：`我的插件`）
- 游戏名称（如：`Game`）
- 作者信息、版本等

### 步骤 5：安装依赖

```bash
# 使用 uv（推荐）
uv pip install -e ".[dev]"

# 或者使用 pip
pip install -e ".[dev]"
```

### 步骤 6：初始化 Git 仓库（可选）

如果你想使用版本控制：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: 基于 GSUID Plugin Template"

# 添加远程仓库（如果你创建了 GitHub 仓库）
git remote add origin https://github.com/你的用户名/你的仓库.git
git push -u origin main
```

## 📦 模板包内容

下载的模板包包含以下文件：

```
gsuid-plugin-template-x.x.x/
├── __init__.py          # 插件入口配置
├── __full__.py          # 完整功能示例
├── init_plugin.py       # 初始化脚本
├── version.py           # 版本信息
├── pyproject.toml       # 项目配置
├── README.md            # 插件说明
├── ARCHITECTURE.md      # 架构文档
└── docs/                # 文档目录
    ├── method-github-template.md
    ├── method-template-package.md
    └── method-git-clone.md
```

**不包含的文件：**
- `.git/` - Git 历史记录
- `.github/` - GitHub Actions 工作流
- `__pycache__/` - Python 缓存
- `.uv-cache/` - UV 缓存
- 其他临时文件

## 🔗 相关链接

- [GitHub Releases 页面](https://github.com/你的组织/gsuid_plugin_template/releases)
- [返回主 README](../README.md)
- [查看其他使用方式](./README.md)

## ❓ 常见问题

### Q: 模板包多久更新一次？

每次推送版本标签（如 `v1.0.0`）时，GitHub Actions 会自动构建并发布新的模板包。

### Q: 如何获取最新版本的模板包？

始终从 Releases 页面的 **Latest** 标签下载，或者订阅仓库的发布通知。

### Q: 模板包和 GitHub 模板功能有什么区别？

| 特性 | 模板包下载 | GitHub 模板按钮 |
|------|-----------|----------------|
| Git 历史 | ❌ 无 | ✅ 有 |
| 文件大小 | ✅ 更小 | 较大 |
| 上手难度 | ✅ 简单 | 需要 Git 基础 |
| 版本控制 | 需手动初始化 | ✅ 自动保留 |
| 更新模板 | 重新下载 | 拉取更新 |

### Q: 可以修改模板包的内容吗？

当然可以！下载后模板包就是你的了，可以随意修改。
