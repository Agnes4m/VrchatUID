"""
{{PluginName}}
基于 GenshinUID Core 的标准插件模板

作者: {{author}}
版本: {{version}}
"""

from gsuid_core.sv import Plugins

# ========== 插件基础配置 ==========
# 这是插件的入口配置，会在框架加载时自动执行

Plugins(
    # 插件显示名称（建议用中文或英文）
    name="{{PluginName}}",
    # 插件默认权限等级
    # 0=Master, 1=SuperUser, 2=群主/管理员, 3=普通用户, 4-6=更宽松
    pm=6,
    # 优先级（1-9，越小越早触发）
    priority=5,
    # 插件默认启用状态
    enabled=True,
    # 作用域: ALL(全部)/GROUP(群聊)/DIRECT(私聊)/SV(跟随上级)
    area="ALL",
    # 可选命令前缀列表（用户可以用这些开头）
    # 支持多前缀，用逗号分隔，如: "原神,ys,genshin"
    prefix=["{{prefix}}", "{{plugin_short}}"{{additional_prefixes_list}}],
    # 强制前缀列表（命令必须以此开头，优先级高于prefix）
    # 支持多前缀，用逗号分隔
    force_prefix=["{{force_prefix}}"{{additional_force_prefixes_list}}],
    # 是否允许空前缀（即不需要前缀直接匹配）
    allow_empty_prefix=False,
    # 禁用强制前缀时，只使用prefix
    disable_force_prefix=False,
    # 插件别名（用于帮助系统搜索）
    alias=["{{plugin_short}}", "{{plugin_cn_name}}"],
    # 白名单/黑名单配置（留空表示不限制）
    white_list=[],
    black_list=[],
)
