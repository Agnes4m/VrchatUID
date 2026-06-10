"""API 调用工具函数

提供统一的 logger 初始化和 JSON 响应 debug 输出
"""

import json
from typing import Any

from gsuid_core.logger import logger


def log_api_response(api_name: str, response: Any) -> None:
    """将 API 响应对象转为 JSON 并以 DEBUG 级别记录

    Args:
        api_name: API 调用名称（如 "search_users", "get_group"）
        response: 任意 API 返回值（通常为 Pydantic 模型或 dict）
    """
    try:
        if hasattr(response, "to_dict"):
            data = response.to_dict()
        elif isinstance(response, (list, tuple)):
            data = [item.to_dict() if hasattr(item, "to_dict") else item for item in response]
        else:
            data = response

        if not isinstance(data, str):
            data = json.dumps(data, ensure_ascii=False, default=str)

        logger.debug(f"[VRChat API] {api_name} 返回: {data[:2000]}")
    except Exception as e:
        logger.debug(f"[VRChat API] {api_name} 返回（序列化失败: {e}）: {str(response)[:500]}")
