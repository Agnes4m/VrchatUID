"""会话状态管理模块

由于部分 gsuid_core 版本 Event 对象没有 state 属性，
本模块提供基于 session_id 的轻量级状态管理。
"""

from typing import Any


class SessionStateStore:
    """简单的内存字典式会话状态存储

    用途：在多步交互命令（如搜索-选择-操作）间保存数据。
    注意：进程重启后状态会丢失，符合 gsuid_core 既有插件的预期。
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        """获取会话状态"""
        return self._store.get(session_id, {}).get(key, default)

    def set(self, session_id: str, key: str, value: Any) -> None:
        """设置会话状态"""
        if session_id not in self._store:
            self._store[session_id] = {}
        self._store[session_id][key] = value

    def has(self, session_id: str, key: str) -> bool:
        """检查会话是否有指定 key"""
        return key in self._store.get(session_id, {})

    def clear(self, session_id: str) -> None:
        """清除会话所有状态"""
        self._store.pop(session_id, None)


# 全局单例
store = SessionStateStore()


# 便捷函数
def get_state(session_id: str, key: str, default: Any = None) -> Any:
    return store.get(session_id, key, default)


def set_state(session_id: str, key: str, value: Any) -> None:
    store.set(session_id, key, value)


def has_state(session_id: str, key: str) -> bool:
    return store.has(session_id, key)


def clear_state(session_id: str) -> None:
    store.clear(session_id)
