"""API 调用工具函数

提供统一的 logger 初始化、JSON 响应 debug 输出、友好的异常信息格式化
以及基于 ActionResult 的统一命令装饰器
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from functools import wraps
from typing import Any

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from vrchatapi.exceptions import ApiException, ForbiddenException, NotFoundException, UnauthorizedException


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


def _extract_error_message(exc: ApiException) -> str:
    """从 ApiException.body 中解析 VRChat 错误消息

    VRChat 错误体形如 {"error":{"message":"...","status_code":401}}
    """
    if not exc.body:
        return ""
    try:
        raw = exc.body.decode("utf-8", errors="replace") if isinstance(exc.body, (bytes, bytearray)) else str(exc.body)
        data = json.loads(raw)
        if isinstance(data, dict):
            err = data.get("error")
            if isinstance(err, dict):
                msg = err.get("message")
                if isinstance(msg, str):
                    return msg.strip().strip('"')
            if isinstance(err, str):
                return err.strip().strip('"')
    except (ValueError, TypeError):
        return str(exc.body).strip().strip('"')[:200]
    return ""


def format_api_error(exc: ApiException) -> str:
    """将 VRChat ApiException 转换为对用户友好的中文提示

    Args:
        exc: 任意 VRChat SDK 抛出的 ApiException 子类

    Returns:
        适合直接发送给用户的简短中文错误说明
    """
    status = getattr(exc, "status", None)
    server_msg = _extract_error_message(exc)

    if isinstance(exc, UnauthorizedException):
        if "Missing Credentials" in server_msg or status == 401:
            return "登录凭证已失效（cookie 过期），请重新发送【vrc登录 用户名 密码】"
        return "身份验证失败，请重新登录后重试"
    if isinstance(exc, ForbiddenException):
        return "没有访问权限，可能账号被风控或功能未开放"
    if isinstance(exc, NotFoundException):
        return "请求的资源不存在"
    if status == 429:
        return "请求过于频繁，请稍后再试"
    if status and 500 <= int(status) < 600:
        return "VRChat 服务端异常，请稍后再试"
    if status and 400 <= int(status) < 500:
        return f"请求被拒绝（HTTP {status}）"
    return f"操作失败（HTTP {status}）" if status else "操作失败"


class StatusCode(StrEnum):
    """命令执行结果状态码

    数值越大越异常，方便日志聚合时按范围判断
    """

    SUCCESS = "0"
    INFO = "1"  # 一般性提示（如"未找到"）
    WARN = "2"  # 用户操作相关提示（如"请先搜索"）
    ERROR = "3"  # API 错误（凭证失效、服务异常等）
    FATAL = "4"  # 未知异常
    CANCELLED = "5"  # 用户主动取消


@dataclass
class ActionResult:
    """命令执行结果

    Usage:
        return ActionResult.success("获取成功", data=friends)
        return ActionResult.info("未找到相关用户")
        return ActionResult.warn("请先使用【vrc搜索用户】")
        return ActionResult.error("登录凭证已失效")
    """

    status: StatusCode
    msg: str
    data: Any = field(default=None, repr=False)

    @classmethod
    def success(cls, msg: str = "操作成功", data: Any = None) -> "ActionResult":
        return cls(StatusCode.SUCCESS, msg, data)

    @classmethod
    def info(cls, msg: str, data: Any = None) -> "ActionResult":
        return cls(StatusCode.INFO, msg, data)

    @classmethod
    def warn(cls, msg: str, data: Any = None) -> "ActionResult":
        return cls(StatusCode.WARN, msg, data)

    @classmethod
    def error(cls, msg: str, data: Any = None) -> "ActionResult":
        return cls(StatusCode.ERROR, msg, data)

    @classmethod
    def fatal(cls, msg: str, data: Any = None) -> "ActionResult":
        return cls(StatusCode.FATAL, msg, data)

    @property
    def ok(self) -> bool:
        return self.status in (StatusCode.SUCCESS, StatusCode.INFO, StatusCode.WARN)


type _ActionFunc = Callable[..., Awaitable[ActionResult | None]]
type _DecoratedFunc = Callable[..., Awaitable[None]]


def api_action(action_name: str) -> Callable[[_ActionFunc], _DecoratedFunc]:
    """命令装饰器：自动捕获异常并向用户发送友好提示

    被装饰的函数应返回 ActionResult 或 None。装饰器会:
    1. 捕获 ApiException → 调用 format_api_error → 提示
    2. 捕获其他 Exception → 通用提示
    3. SUCCESS 状态下不发送消息（由命令自行控制成功时的输出）

    Usage:
        @api_action("获取好友列表")
        async def vrc_friend_list(bot: Bot, ev: Event) -> ActionResult:
            friends = list(get_all_friends(client))
            if not friends:
                return ActionResult.info("您的好友列表为空")
            await bot.send(build_friend_image(friends))
            return ActionResult.success()
    """

    def decorator(func: _ActionFunc) -> _DecoratedFunc:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> None:
            bot: Bot | None = None
            for arg in args:
                if isinstance(arg, Bot):
                    bot = arg
                    break
            if bot is None:
                bot = kwargs.get("bot")

            user_id: str | None = kwargs.get("user_id")
            if user_id is None:
                for arg in args:
                    uid = getattr(arg, "user_id", None)
                    if isinstance(uid, str):
                        user_id = uid
                        break
            bot_id: str | None = kwargs.get("bot_id")
            if bot_id is None:
                for arg in args:
                    bid = getattr(arg, "bot_id", None)
                    if isinstance(bid, str):
                        bot_id = bid
                        break

            for attempt in range(2):
                try:
                    result = await func(*args, **kwargs)
                except ApiException as e:
                    if attempt == 0 and isinstance(e, UnauthorizedException) and user_id and bot_id:
                        logger.warning(f"{action_name} 命中 401，尝试自动重登后重试一次")
                        if await _try_relogin(user_id, bot_id, bot):
                            continue
                    logger.error(f"{action_name}失败 (API): {e}")
                    if bot is not None:
                        await bot.send(f"{action_name}失败：{format_api_error(e)}")
                    return
                except Exception as e:
                    logger.exception(f"{action_name}失败 (未知): {e}")
                    if bot is not None:
                        detail = str(e) or type(e).__name__
                        await bot.send(f"{action_name}失败：{detail}")
                    return

                if result is None or bot is None:
                    return

                if result.status == StatusCode.SUCCESS:
                    return
                await bot.send(result.msg)
                return

        return wrapper

    return decorator


async def _try_relogin(user_id: str, bot_id: str, bot: Bot | None) -> bool:
    """尝试用已存储密码重登一次，返回是否成功（成功则调用方可重试）"""
    from .client import relogin_via_password

    try:
        await relogin_via_password(user_id, bot_id)
        if bot is not None:
            await bot.send("🔄 检测到登录已过期，已自动用保存的密码刷新登录态，正在重试…")
        return True
    except Exception as e:
        logger.warning(f"自动重登失败: {e}")
        return False
