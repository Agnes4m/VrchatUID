# 方式三：Git 克隆复制

使用 Git 命令克隆模板仓库，然后手动清理和初始化。

## ✨ 特点

- ✅ 完全控制复制过程
- ✅ 可以选择性保留文件
- ✅ 适合熟悉 Git 的开发者
- ✅ 可以查看模板更新历史

## 🚀 使用步骤

### 步骤 1：克隆模板仓库

```bash
# 进入 gsuid_core/plugins 目录
cd gsuid_core/plugins/

# 克隆模板仓库
git clone https://github.com/你的组织/gsuid_plugin_template.git

# 进入模板目录
cd gsuid_plugin_template
```

### 步骤 2：清理 Git 历史

这是关键步骤，确保你的插件是全新的：

#### 方法 A：完全清除 Git 历史（推荐）

```bash
# 1. 删除 .git 目录
rm -rf .git

# 2. 重新初始化 Git
git init

# 3. 添加所有文件
git add .

# 4. 首次提交
git commit -m "Initial commit: 基于 GSUID Plugin Template"
```

#### 方法 B：保留模板历史但修改远程

```bash
# 1. 查看当前远程
git remote -v
# 输出：origin  https://github.com/你的组织/gsuid_plugin_template.git

# 2. 移除模板远程
git remote remove origin

# 3. 添加你自己的远程仓库（如果已创建）
git remote add origin https://github.com/你的用户名/你的插件仓库.git

# 4. 强制推送（会覆盖远程历史）
git push -f origin main
```

### 步骤 3：重命名目录

```bash
# 返回上级目录
cd ..

# 重命名为你的插件名称
mv gsuid_plugin_template MyPluginUID

# 进入新目录
cd MyPluginUID
```

### 步骤 4：运行初始化脚本

```bash
# 运行交互式初始化
python init_plugin.py
```

**选择生成模式：**

由于你是通过 Git 克隆的方式使用模板，推荐选择 **"覆盖本地"** 模式：

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
- 插件英文名称
- 插件短名（命令前缀）
- 插件中文名称
- 游戏名称
- 作者、邮箱、版本等

### 步骤 5：安装依赖

```bash
# 使用 uv（推荐）
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

uv pip install -e ".[dev]"
```

### 步骤 6：清理不需要的文件（可选）

```bash
# 删除模板相关文档（如果你不需要）
rm -f docs/method-*.md
rm -f TEMPLATE_SETUP.md

# 删除示例文件（如果你从 __full__.py 开始）
rm -f __init__.py
mv __full__.py __init__.py
```

## 📋 完整命令速查

```bash
# 一键完成所有步骤
cd gsuid_core/plugins/ && \
git clone https://github.com/你的组织/gsuid_plugin_template.git && \
cd gsuid_plugin_template && \
rm -rf .git && \
git init && \
git add . && \
git commit -m "Initial commit" && \
cd .. && \
mv gsuid_plugin_template MyPluginUID && \
cd MyPluginUID && \
python init_plugin.py
```

## 🔧 高级用法

### 只克隆特定分支

```bash
# 克隆特定分支
git clone --branch main --single-branch https://github.com/你的组织/gsuid_plugin_template.git
```

### 浅克隆（更快）

```bash
# 只克隆最新提交，速度更快
git clone --depth 1 https://github.com/你的组织/gsuid_plugin_template.git
```

### 选择性复制文件

```bash
# 不克隆，直接下载特定文件
curl -O https://raw.githubusercontent.com/你的组织/gsuid_plugin_template/main/__init__.py
curl -O https://raw.githubusercontent.com/你的组织/gsuid_plugin_template/main/init_plugin.py
# ... 其他文件
```

## 🔄 与模板仓库保持同步

如果你想跟踪模板的更新：

```bash
# 1. 添加模板仓库作为 upstream
git remote add upstream https://github.com/你的组织/gsuid_plugin_template.git

# 2. 获取模板更新
git fetch upstream

# 3. 查看模板更新
git log upstream/main --oneline

# 4. 合并模板更新（谨慎操作）
git merge upstream/main --allow-unrelated-histories
```

## 🔗 相关链接

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub Git 指南](https://docs.github.com/en/get-started/quickstart/set-up-git)
- [返回主 README](../README.md)
- [查看其他使用方式](./README.md)

## ❓ 常见问题

### Q: 为什么需要清理 Git 历史？

如果不清理，你的插件仓库会包含模板的所有提交历史，这会导致：
- 仓库体积较大
- 提交历史混乱
- 可能包含模板开发者的敏感信息

### Q: 如何验证 Git 历史已清除？

```bash
# 查看提交历史，应该只有你的提交
git log

# 查看远程地址，应该指向你的仓库
git remote -v
```

### Q: 克隆后如何推送到自己的仓库？

```bash
# 1. 先在 GitHub 创建空仓库（不要初始化）

# 2. 添加远程地址
git remote add origin https://github.com/你的用户名/你的仓库.git

# 3. 推送
git push -u origin main
```

### Q: 三种方式推荐哪种？

| 场景 | 推荐方式 |
|------|---------|
| 熟悉 Git，需要版本控制 | 方式一：GitHub 模板按钮 |
| 不熟悉 Git，快速开始 | 方式二：下载模板包 |
| 需要完全控制，查看历史 | 方式三：Git 克隆 |
