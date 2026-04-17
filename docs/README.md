# 使用文档索引

本文档汇总了使用 GSUID Plugin Template 的所有方式和相关设置指南。

## 🚀 使用模板的方式

我们提供了 **三种方式** 来使用此模板，根据你的需求选择最适合的：

### 方式一：GitHub 模板按钮 ⭐ 推荐

**适用场景：** 需要版本控制、计划长期维护插件

**特点：**
- ✅ 保留完整的 Git 历史记录
- ✅ 自动复制所有分支和标签
- ✅ 直接在新仓库中开始开发
- ✅ 可以与原模板仓库保持关联

**快速开始：**
1. 访问模板仓库主页
2. 点击 **"Use this template"** 按钮
3. 配置新仓库信息
4. 创建并开始开发

**详细文档：** [method-github-template.md](./method-github-template.md)

---

### 方式二：下载模板包 🔰 新手友好

**适用场景：** 快速开始、不熟悉 Git

**特点：**
- ✅ 纯净的模板文件，无 Git 历史
- ✅ 无需 Git 操作，简单直接
- ✅ 文件体积更小
- ✅ 适合不熟悉 Git 的用户

**快速开始：**
1. 访问 [Releases 页面](https://github.com/你的组织/gsuid_plugin_template/releases)
2. 下载最新版本的模板压缩包
3. 解压到 `gsuid_core/plugins/` 目录
4. 重命名并运行初始化脚本

**详细文档：** [method-template-package.md](./method-template-package.md)

---

### 方式三：Git 克隆复制 🔧 高级

**适用场景：** 熟悉 Git、需要完全控制

**特点：**
- ✅ 完全控制复制过程
- ✅ 可以选择性保留文件
- ✅ 适合熟悉 Git 的开发者
- ✅ 可以查看模板更新历史

**快速开始：**
```bash
cd gsuid_core/plugins/
git clone https://github.com/你的组织/gsuid_plugin_template.git
cd gsuid_plugin_template
rm -rf .git && git init && git add . && git commit -m "Initial commit"
cd .. && mv gsuid_plugin_template MyPlugin && cd MyPlugin
python init_plugin.py
```

**详细文档：** [method-git-clone.md](./method-git-clone.md)

---

## 📊 方式对比

| 特性 | 方式一：GitHub 模板 | 方式二：模板包 | 方式三：Git 克隆 |
|------|------------------|--------------|---------------|
| Git 历史 | ✅ 保留 | ❌ 无 | ✅ 可控制 |
| 上手难度 | 中等 | ✅ 简单 | 较复杂 |
| 文件大小 | 较大 | ✅ 最小 | 较大 |
| 版本控制 | ✅ 自动 | 需手动初始化 | ✅ 手动控制 |
| 更新模板 | 拉取更新 | 重新下载 | 拉取更新 |
| 适合人群 | 开发者 | 新手 | 高级用户 |

---

## 🔧 维护者指南

如果你是模板维护者，以下文档帮助你配置 GitHub 仓库：

### [GITHUB_SETUP.md](./GITHUB_SETUP.md)

**内容：**
- 启用 GitHub 模板功能
- 配置 GitHub Actions 工作流
- 设置自动发布模板包
- 管理 Releases

---

## 📁 文档结构

```
docs/
├── README.md                      # 本文档 - 使用指南索引
├── GITHUB_SETUP.md                # GitHub 仓库设置指南（维护者）
├── method-github-template.md      # 方式一：GitHub 模板按钮
├── method-template-package.md     # 方式二：下载模板包
└── method-git-clone.md            # 方式三：Git 克隆复制
```

---

## 🔗 相关链接

### 模板文档
- [主 README](../README.md) - 模板概览和快速开始
- [架构说明](../ARCHITECTURE.md) - 插件架构设计

### 核心框架文档
- [GsCore 消息流转与命令触发机制](../../docs/message_flow.md) - 了解消息如何在框架中流转
- [GsCore 项目启动与插件载入](../../docs/startup.md) - 了解框架启动和插件加载流程

### 外部链接
- [GenshinUID Core](https://github.com/Genshin-bots/gsuid_core) - 核心框架

---

## ❓ 常见问题

### Q: 我应该选择哪种方式？

- **如果你是 Git/GitHub 新手** → 选择 [方式二：下载模板包](./method-template-package.md)
- **如果你需要版本控制** → 选择 [方式一：GitHub 模板按钮](./method-github-template.md)
- **如果你熟悉 Git 且需要完全控制** → 选择 [方式三：Git 克隆复制](./method-git-clone.md)

### Q: 使用模板后如何更新？

不同方式的更新方法：
- **方式一**：添加模板仓库为 upstream，拉取更新后合并
- **方式二**：下载新版本的模板包，手动对比更新
- **方式三**：添加模板仓库为 upstream，拉取更新

### Q: 可以修改模板内容吗？

当然可以！下载或克隆后，模板就是你的了，可以随意修改。

### Q: 遇到问题怎么办？

1. 查看对应方式的详细文档
2. 检查 [GITHUB_SETUP.md](./GITHUB_SETUP.md) 的配置说明
3. 在 GitHub Issues 中提问

---

**返回主文档：** [README.md](../README.md)
