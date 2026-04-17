# GitHub 模板仓库设置指南

本文档说明如何配置 GitHub 模板功能，让用户可以通过"Use this template"按钮或下载模板包来使用此模板。

## 🎯 目标功能

1. **GitHub 原生模板功能** - 用户点击"Use this template"创建新仓库
2. **自动发布模板包** - 通过 GitHub Actions 自动生成纯净的模板压缩包

## 📋 设置步骤

### 步骤 1: 启用模板仓库功能

1. 进入 GitHub 仓库页面
2. 点击 **Settings** → **General**
3. 找到 **Template repository** 部分
4. 勾选 **Template repository** 选项
5. 点击 **Save**

启用后，仓库主页会显示绿色的 **"Use this template"** 按钮。

### 步骤 2: 配置 GitHub Actions

创建以下工作流文件：

#### `.github/workflows/release-template.yml`

此工作流会在以下情况触发：
- 推送版本标签（如 `v1.0.0`）
- 手动触发（workflow_dispatch）

功能：
- 生成纯净的模板压缩包（tar.gz 和 zip）
- 自动创建 GitHub Release
- 上传模板包到 Release 附件

### 步骤 3: 创建仓库变量（可选）

如果需要自定义发布行为，可以在仓库设置中添加：

- `TEMPLATE_NAME` - 模板包名称前缀（默认: gsuid-plugin-template）

### 步骤 4: 测试工作流

1. 推送一个测试标签：
   ```bash
   git tag v0.1.0-test
   git push origin v0.1.0-test
   ```

2. 检查 Actions 页面，确认工作流成功运行

3. 查看 Releases 页面，确认模板包已上传

## 📦 用户使用方式

### 方式一：GitHub 模板按钮（保留 Git 历史）

1. 访问模板仓库主页
2. 点击 **"Use this template"** 按钮
3. 选择 **"Create a new repository"**
4. 填写新仓库信息
5. 点击 **Create repository**

### 方式二：下载模板包（纯净模板，无 Git 历史）

1. 访问仓库的 **Releases** 页面
2. 下载最新版本的模板压缩包
3. 解压到 `gsuid_core/plugins/` 目录
4. 重命名为你的插件名称
5. 运行初始化脚本

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

### 自动发布（推荐）

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

### 手动发布

1. 进入仓库的 **Actions** 页面
2. 选择 **Release Template Package** 工作流
3. 点击 **Run workflow**
4. 输入版本号
5. 点击 **Run workflow**

## 🎨 README 徽章

在 README.md 中添加以下徽章：

```markdown
[![Use this Template](https://img.shields.io/badge/GitHub-Use%20this%20template-blue?style=flat-square&logo=github)](https://github.com/YOUR_ORG/YOUR_REPO/generate)
[![Download Template](https://img.shields.io/badge/Download-Template%20Package-green?style=flat-square)](https://github.com/YOUR_ORG/YOUR_REPO/releases/latest)
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
