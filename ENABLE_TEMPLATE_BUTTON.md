# 启用 "Use this template" 按钮

要实现类似 https://github.com/fllesser/nonebot-plugin-template 的效果，在仓库 stars 右边显示绿色的 **"Use this template"** 按钮，需要完成以下设置：

## 🎯 目标效果

```
[Code] [Issues] [Pull requests] [Actions] [Projects] [Wiki] [Security] [Insights] [Settings]

⭐ 0 stars | 🍴 0 forks | 🔔 Watching | 🍃 main | 🏷️ 0 tags | 📦 0 packages
                                                    [🟢 Use this template]
```

## 📋 设置步骤

### 步骤 1：进入仓库设置

1. 打开你的 GitHub 仓库页面
2. 点击顶部导航栏的 **Settings** 标签

### 步骤 2：启用模板功能

1. 在左侧边栏选择 **General**（默认就是）
2. 向下滚动到 **Template repository** 部分
3. 勾选 ☑️ **Template repository** 选项
4. 点击 **Save** 按钮

```
Template repository
☑️ Template repository  ← 勾选这个！

Template repositories let users generate new repositories with the same 
directory structure and files. Learn more about template repositories.

[Save]  ← 点击保存
```

### 步骤 3：验证效果

保存后，返回仓库主页，你会看到：

1. 在 stars 数量右边出现绿色的 **"Use this template"** 按钮
2. 按钮旁边有一个下拉箭头，点击后有两个选项：
   - **Create a new repository** - 创建新仓库（最常用）
   - **Open in a codespace** - 在 Codespace 中打开

## 🖼️ 截图示意

启用前：
```
⭐ 0 stars    🍴 0 forks    🔔 Watching    🍃 main    🏷️ 0 tags
```

启用后：
```
⭐ 0 stars    🍴 0 forks    🔔 Watching    🍃 main    🏷️ 0 tags    [🟢 Use this template]
```

## ⚠️ 注意事项

1. **必须是仓库 Owner 或 Admin** 才能看到设置选项
2. **Public 仓库** - 任何人都可以使用你的模板
3. **Private 仓库** - 只有有权限的人才能看到模板按钮
4. **组织仓库** - 需要组织管理员权限

## 🔗 相关链接

- [GitHub 官方文档 - 创建模板仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [GitHub 官方文档 - 从模板创建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)

## ❓ 常见问题

### Q: 为什么我看不到 "Template repository" 选项？

可能原因：
- 你不是仓库的 Owner 或 Admin
- 你正在查看的是别人的仓库
- 浏览器缓存问题，尝试刷新页面

### Q: 启用后按钮没有立即出现？

尝试：
1. 刷新页面（F5 或 Ctrl+R）
2. 清除浏览器缓存
3. 等待几分钟（GitHub 可能有延迟）

### Q: 可以关闭模板功能吗？

可以，取消勾选 **Template repository** 选项并保存即可。

### Q: 模板仓库和普通仓库有什么区别？

| 特性 | 模板仓库 | 普通仓库 |
|------|---------|---------|
| Use this template 按钮 | ✅ 有 | ❌ 无 |
| Fork 功能 | ✅ 有 | ✅ 有 |
| 被使用时保留 Git 历史 | ✅ 是 | - |
| 用于生成新仓库 | ✅ 是 | ❌ 否 |

## ✅ 完成检查清单

- [ ] 进入 Settings → General
- [ ] 勾选 Template repository
- [ ] 点击 Save
- [ ] 返回主页查看绿色按钮
- [ ] 点击按钮测试下拉菜单

完成以上步骤后，你的仓库就会显示 **"Use this template"** 按钮了！
