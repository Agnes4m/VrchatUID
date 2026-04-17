# 方式一：使用 GitHub 模板按钮

通过 GitHub 的 "Use this template" 功能，快速创建基于本模板的新仓库。

## ✨ 特点

- ✅ 保留完整的 Git 历史记录
- ✅ 自动复制所有分支和标签
- ✅ 直接在新仓库中开始开发
- ✅ 可以与原模板仓库保持关联

## 🚀 使用步骤

### 步骤 1：点击模板按钮

1. 访问模板仓库主页：`https://github.com/Agnes4m/gsuid_core_plugin_template`
2. 点击页面右上角的绿色按钮 **"Use this template"**
3. 在下拉菜单中选择 **"Create a new repository"**

### 步骤 2：配置新仓库

在创建页面填写以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| **Repository name** | 你的插件仓库名称 | `MyGameUID` |
| **Description** | 插件描述 | `原神游戏查询插件` |
| **Public/Private** | 仓库可见性 | 建议选择 Public |

### 步骤 3：创建仓库

点击 **"Create repository"** 按钮，GitHub 会自动：
- 复制模板的所有文件
- 保留 Git 提交历史
- 创建新的独立仓库

### 步骤 4：本地开发

```bash
# 1. 克隆你刚创建的仓库
git clone https://github.com/你的用户名/MyGameUID.git
cd MyGameUID

# 2. 运行初始化脚本
python init_plugin.py
```

**选择生成模式：**

由于你是通过 GitHub 模板创建的新仓库，推荐选择 **"覆盖本地"** 模式：

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
- 作者信息等

```bash
# 3. 安装依赖
uv pip install -e ".[dev]"

# 4. 开始开发！
```

## 📋 后续操作

### 修改远程仓库地址（可选）

如果你想完全断开与原模板的关联：

```bash
# 查看当前远程地址
git remote -v

# 移除原模板远程地址
git remote remove origin

# 添加你自己的远程地址
git remote add origin https://github.com/你的用户名/你的仓库名.git
```

### 清理 Git 历史（可选）

如果你想清除所有历史提交，重新开始：

```bash
# 1. 创建孤立分支
git checkout --orphan new-main

# 2. 添加所有文件
git add -A

# 3. 提交
git commit -m "Initial commit"

# 4. 删除旧分支
git branch -D main

# 5. 重命名新分支
git branch -m main

# 6. 强制推送到远程
git push -f origin main
```

## 🔗 相关链接

- [GitHub 模板仓库官方文档](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
- [返回主 README](../README.md)
- [查看其他使用方式](./README.md)

## ❓ 常见问题

### Q: 使用模板后，如何更新模板内容？

模板仓库的更新不会自动同步到你的仓库。你可以：
1. 手动对比模板仓库的更新
2. 使用 `git remote add template <模板仓库地址>` 添加模板远程
3. 定期拉取模板更新并合并

### Q: 可以修改仓库名称吗？

可以！创建后随时可以在 Settings 中修改仓库名称，不会影响功能。

### Q: 私有仓库可以使用模板吗？

可以，但模板仓库本身必须是 Public 或你拥有访问权限的 Private 仓库。
