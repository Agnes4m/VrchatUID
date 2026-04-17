# GitHub 仓库设置指南

本文档说明如何在 GitHub 上配置模板仓库，启用"Use this template"功能并设置自动发布工作流。

## 🎯 设置目标

1. ✅ 启用 GitHub 原生模板功能（"Use this template"按钮）
2. ✅ 配置 GitHub Actions 自动发布模板包
3. ✅ 设置 Releases 页面供用户下载

## 📋 设置步骤

### 步骤 1：启用模板仓库功能

1. 进入 GitHub 仓库页面：`https://github.com/你的组织/gsuid_plugin_template`
2. 点击 **Settings** → **General**
3. 找到 **Template repository** 部分
4. 勾选 **Template repository** 选项
5. 点击 **Save**

启用后，仓库主页会显示绿色的 **"Use this template"** 按钮。

### 步骤 2：验证 Actions 工作流

本模板已包含 GitHub Actions 工作流文件：

- `.github/workflows/release-template.yml` - 自动发布模板包

**工作流功能：**
- 推送版本标签（如 `v1.0.0`）时自动触发
- 生成纯净的模板压缩包（tar.gz 和 zip）
- 自动创建 GitHub Release
- 上传模板包到 Release 附件

### 步骤 3：配置仓库权限

确保 Actions 有写入权限：

1. 进入 **Settings** → **Actions** → **General**
2. 找到 **Workflow permissions**
3. 选择 **Read and write permissions**
4. 勾选 **Allow GitHub Actions to create and approve pull requests**（可选）
5. 点击 **Save**

### 步骤 4：测试发布流程

#### 方法 A：推送标签（自动触发）

```bash
# 1. 更新版本号（在 version.py 中）
# 2. 提交更改
git add .
git commit -m "Release v1.0.0"

# 3. 创建标签
git tag v1.0.0

# 4. 推送标签
git push origin v1.0.0
```

推送后，GitHub Actions 会自动：
- 构建模板包
- 创建 Release
- 上传附件

#### 方法 B：手动触发

1. 进入仓库的 **Actions** 页面
2. 选择 **Release Template Package** 工作流
3. 点击 **Run workflow**
4. 输入版本号（如 `1.0.0`）
5. 点击 **Run workflow**

### 步骤 5：验证结果

1. 查看 **Actions** 页面，确认工作流成功运行（绿色勾号）
2. 查看 **Releases** 页面，确认：
   - Release 已创建
   - 包含两个附件：`.tar.gz` 和 `.zip`
   - 发布说明正确显示

## 🔧 工作流详细说明

### release-template.yml

**触发条件：**
- `push.tags`: 推送以 `v` 开头的标签（如 `v1.0.0`）
- `workflow_dispatch`: 手动触发，可指定版本号

**执行步骤：**
1. 检出代码
2. 设置 Python 环境
3. 确定版本号
4. 创建模板包（排除 .git、__pycache__ 等）
5. 生成发布说明
6. 创建 GitHub Release 并上传附件

**输出文件：**
- `gsuid-plugin-template-{VERSION}.tar.gz`
- `gsuid-plugin-template-{VERSION}.zip`

## 📝 发布流程

### 标准发布流程

```bash
# 1. 确保所有更改已提交
git status

# 2. 更新版本号（编辑 version.py）
echo '__version__ = "1.0.0"' > version.py

# 3. 提交版本更新
git add version.py
git commit -m "Bump version to 1.0.0"

# 4. 创建标签
git tag v1.0.0

# 5. 推送标签（触发 Actions）
git push origin v1.0.0
```

### 紧急修复流程

```bash
# 1. 创建修复分支
git checkout -b hotfix/v1.0.1

# 2. 修复问题并提交
git add .
git commit -m "Fix critical bug"

# 3. 合并到主分支
git checkout main
git merge hotfix/v1.0.1

# 4. 创建新版本标签
git tag v1.0.1
git push origin v1.0.1
```

## 🎨 README 徽章

在 README.md 中添加以下徽章：

```markdown
<p align="center">
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
```

## 🔗 相关链接

- [GitHub 模板仓库文档](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Releases 文档](https://docs.github.com/en/repositories/releasing-projects-on-github)

## ❓ 常见问题

### Q: 模板包和 GitHub 模板功能有什么区别？

**GitHub 模板功能：**
- 保留完整的 Git 历史
- 复制所有分支和标签
- 适合需要版本控制的开发

**模板包下载：**
- 纯净的模板文件
- 无 Git 历史
- 适合直接开始开发

### Q: 如何更新已发布的模板？

推送新的版本标签即可触发重新发布：
```bash
git tag v1.1.0
git push origin v1.1.0
```

### Q: 工作流失败了怎么办？

1. 检查 Actions 日志，查看错误信息
2. 确认仓库有正确的权限设置
3. 检查 `secrets.GITHUB_TOKEN` 是否有写入权限

### Q: 可以修改模板包的内容吗？

可以！编辑 `.github/workflows/release-template.yml` 文件中的 `rsync` 命令，添加或排除特定文件。

### Q: 如何删除已发布的 Release？

1. 进入 **Releases** 页面
2. 点击要删除的 Release
3. 点击右上角的 **Delete** 按钮
4. 确认删除

注意：删除 Release 不会删除标签，如需删除标签：
```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0
```
