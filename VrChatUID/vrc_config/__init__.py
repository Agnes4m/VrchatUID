"""VRChatUID 配置模块

通过 gsuid_core 的 plugins_config 系统注册可由 web 控制台修改的配置项。
"""

from gsuid_core.utils.plugins_config.gs_config import all_config_list
from gsuid_core.utils.plugins_config.models import GsIntConfig

from .config_default import CONFIG_DEFAULT

# 关键配置项默认值（同时被代码与 web 控制台读取）
VRC_SEARCH_USER_MAX_SIZE = 20
VRC_SEARCH_WORLD_MAX_SIZE = 20
VRC_SEARCH_GROUP_MAX_SIZE = 10


def register_config() -> None:
    """注册 VRChatUID 配置项到全局配置系统

    幂等：多次调用不会重复注册。
    """
    for name, config in CONFIG_DEFAULT.items():
        if name not in all_config_list:
            all_config_list[name] = config


# 模块导入时自动注册
register_config()


def get_search_user_max_size() -> int:
    """获取搜索用户最大结果数（可由 web 控制台修改）"""
    config = all_config_list.get("VrcSearchUserMaxSize")
    if isinstance(config, GsIntConfig):
        return int(config.data)
    return VRC_SEARCH_USER_MAX_SIZE


def get_search_world_max_size() -> int:
    """获取搜索世界最大结果数（可由 web 控制台修改）"""
    config = all_config_list.get("VrcSearchWorldMaxSize")
    if isinstance(config, GsIntConfig):
        return int(config.data)
    return VRC_SEARCH_WORLD_MAX_SIZE


def get_search_group_max_size() -> int:
    """获取搜索群组最大结果数（可由 web 控制台修改）"""
    config = all_config_list.get("VrcSearchGroupMaxSize")
    if isinstance(config, GsIntConfig):
        return int(config.data)
    return VRC_SEARCH_GROUP_MAX_SIZE
