import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
from http.cookiejar import LWPCookieJar
from typing import TYPE_CHECKING, Optional

from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from vrchatapi import ApiClient, Configuration
from vrchatapi.exceptions import ApiException, UnauthorizedException

if TYPE_CHECKING:
    from vrchatapi.models.current_user import CurrentUser

_c = Configuration()
_c.client_side_validation = False
Configuration.set_default(_c)

DATA_DIR = get_res_path() / "vrchat"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PLAYER_PATH = DATA_DIR / "player"
PLAYER_PATH.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class NotLoggedInError(Exception):
    pass


class TwoFactorAuthError(Exception):
    """2FA验证异常，保存验证函数供后续调用"""

    def __init__(self, verify_func: Callable[[str], Awaitable["CurrentUser"]]) -> None:
        super().__init__()
        self.verify_func = verify_func


def save_client_cookies(client: ApiClient, bot_id: str, user_id: str, vrc_uid: str):
    path = PLAYER_PATH / f"{bot_id}_{user_id}_{vrc_uid}.cookies"
    cookie_jar = LWPCookieJar(filename=str(path))
    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)
    cookie_jar.save()


def load_cookies_to_client(client: ApiClient, user_id: str, bot_id: str, vrc_uid: str):
    path = PLAYER_PATH / f"{bot_id}_{user_id}_{vrc_uid}.cookies"
    if not path.exists():
        raise NotLoggedInError("未找到登录信息，请先登录！")
    cookie_jar = LWPCookieJar(filename=str(path))
    cookie_jar.load()
    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


def remove_cookies(bot_id: str, user_id: str, vrc_uid: str):
    path = PLAYER_PATH / f"{bot_id}_{user_id}_{vrc_uid}.cookies"
    if path.exists():
        path.unlink()


def _create_client(username: str, password: str) -> ApiClient:
    """创建API客户端"""
    configuration = Configuration(
        username=username,
        password=password,
    )
    configuration.client_side_validation = False
    client = ApiClient(configuration)
    client.user_agent = USER_AGENT
    return client


async def get_client(user_id: str, bot_id: str) -> ApiClient:
    """从 VrChatUser 表读取当前活跃账号的凭证，创建 API 客户端"""
    from ..database import get_user_credentials

    cred = await get_user_credentials(user_id, bot_id)
    if cred is None:
        raise NotLoggedInError("未找到登录信息，请先登录！")
    if not cred.username or not cred.password:
        raise NotLoggedInError("凭证不完整，请重新登录！")

    client = _create_client(cred.username, cred.password)
    with suppress(NotLoggedInError):
        load_cookies_to_client(client, user_id, bot_id, cred.vrc_uid)
    return client


async def get_client_or_notify(bot, user_id: str, bot_id: str):
    """获取 API 客户端；未登录时自动发送提示并返回 None。

    Usage:
        client = await get_client_or_notify(bot, user_id, bot_id)
        if client is None:
            return
    """
    try:
        return await get_client(user_id, bot_id)
    except NotLoggedInError:
        await bot.send("您还没有登录 VRChat！请先发送【vrc登录 用户名 密码】")
        return None


async def verify_login(user_id: str, bot_id: str) -> bool:
    """验证登录状态"""
    try:
        client = await get_client(user_id, bot_id)
        from vrchatapi.api import NotificationsApi

        api = NotificationsApi(client)
        await asyncio.to_thread(api.get_notifications, n=1)
        return True
    except UnauthorizedException:
        return False
    except Exception:
        return False


async def login_via_password(
    user_id: str,
    bot_id: str,
    username: str,
    password: str,
) -> "CurrentUser":
    """
    通过用户名密码登录VRChat
    如果需要2FA，会抛出TwoFactorAuthError
    """
    from vrchatapi.api import AuthenticationApi
    from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
    from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

    client = _create_client(username, password)
    api = AuthenticationApi(client)

    async def _save_user_info(current_user: "CurrentUser"):
        """保存用户信息：提取 cookies + 写文件 + 写数据库"""
        from ..database import extract_cookies_from_client, save_credentials

        vrc_uid = str(current_user.id) if current_user.id else ""
        display_name = str(current_user.display_name) if current_user.display_name else ""

        # 从已认证的 client 提取 cookie 字符串
        cookie_str = extract_cookies_from_client(client)
        logger.info(f"VRC 登录成功: vrc_uid={vrc_uid}, display_name={display_name}, cookie_len={len(cookie_str)}")

        await save_credentials(
            user_id=user_id,
            bot_id=bot_id,
            vrc_uid=vrc_uid,
            username=username,
            password=password,
            cookie=cookie_str,
            display_name=display_name,
            vrc_user_id=vrc_uid,
        )
        if vrc_uid:
            save_client_cookies(client, bot_id, user_id, vrc_uid)

    # 尝试获取当前用户信息
    try:
        current_user = await asyncio.to_thread(api.get_current_user)
        from ._helpers import log_api_response

        log_api_response("login_via_password.get_current_user", current_user)
        await _save_user_info(current_user)
        return current_user

    except UnauthorizedException as e:
        # 检查是否是2FA验证
        if e.status == 200 and isinstance(e.reason, str) and "2 Factor Authentication" in e.reason:
            two_fa_email = "Email 2 Factor Authentication" in e.reason
            logger.info(f"检测到2FA验证，类型: {'邮箱' if two_fa_email else 'APP'}")

            async def verify_two_fa(auth_code: str) -> "CurrentUser":
                """验证2FA验证码"""
                if two_fa_email:
                    await asyncio.to_thread(
                        api.verify2_fa_email_code,
                        two_factor_email_code=TwoFactorEmailCode(auth_code),
                    )
                else:
                    await asyncio.to_thread(
                        api.verify2_fa,
                        two_factor_auth_code=TwoFactorAuthCode(auth_code),
                    )
                current_user = await asyncio.to_thread(api.get_current_user)
                from ._helpers import log_api_response

                log_api_response("login_via_password.verify_two_fa", current_user)
                await _save_user_info(current_user)
                return current_user

            raise TwoFactorAuthError(verify_two_fa) from e

        # 其他Unauthorized异常 - 账号密码错误
        logger.error(f"登录失败: {e}")
        raise ApiException(401, "用户名或密码错误") from e


async def get_current_user_info(user_id: str, bot_id: str) -> Optional["CurrentUser"]:
    """获取当前登录用户信息"""
    try:
        client = await get_client(user_id, bot_id)
        from vrchatapi.api import AuthenticationApi

        api = AuthenticationApi(client)
        return await asyncio.to_thread(api.get_current_user)
    except Exception:
        return None


def check_client_usable(client: ApiClient) -> bool:
    from vrchatapi.api import NotificationsApi

    api = NotificationsApi(client)
    try:
        api.get_notifications(n=1)
    except UnauthorizedException:
        return False
    return True
