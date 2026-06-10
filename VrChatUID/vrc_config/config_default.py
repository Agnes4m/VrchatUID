from gsuid_core.utils.plugins_config.models import GSC, GsIntConfig

CONFIG_DEFAULT: dict[str, GSC] = {
    "VrcSearchUserMaxSize": GsIntConfig(
        "搜索用户最大结果数",
        "单次搜索用户时最多返回的结果数（默认 20，最大 100）",
        20,
        max_value=100,
    ),
    "VrcSearchWorldMaxSize": GsIntConfig(
        "搜索世界最大结果数",
        "单次搜索世界时最多返回的结果数（默认 20，最大 100）",
        20,
        max_value=100,
    ),
    "VrcSearchGroupMaxSize": GsIntConfig(
        "搜索群组最大结果数",
        "单次搜索群组时最多返回的结果数（默认 10，最大 50）",
        10,
        max_value=50,
    ),
}
