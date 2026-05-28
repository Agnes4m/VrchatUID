import json
from http.cookiejar import LWPCookieJar

from vrchatapi import ApiClient, Configuration
from vrchatapi.exceptions import UnauthorizedException

from gsuid_core.data_store import get_res_path

_c = Configuration()
_c.client_side_validation = False
Configuration.set_default(_c)

DATA_DIR = get_res_path() / "vrchat"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PLAYER_PATH = DATA_DIR / "player"
PLAYER_PATH.mkdir(parents=True, exist_ok=True)


class NotLoggedInError(Exception):
    pass


class LoginInfo:
    def __init__(
        self,
        username: str = "",
        password: str = "",
        user_id: str = "",
        display_name: str = "",
    ):
        self.username = username
        self.password = password
        self.user_id = user_id
        self.display_name = display_name

    def to_json(self) -> str:
        return json.dumps(
            {
                "username": self.username,
                "password": self.password,
                "user_id": self.user_id,
                "display_name": self.display_name,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "LoginInfo":
        data = json.loads(json_str)
        return cls(**data)


def save_client_cookies(client: ApiClient, user_id: str, bot_id: str):
    path = PLAYER_PATH / f"{bot_id}_{user_id}.cookies"
    cookie_jar = LWPCookieJar(filename=str(path))
    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)
    cookie_jar.save()


def load_cookies_to_client(client: ApiClient, user_id: str, bot_id: str):
    path = PLAYER_PATH / f"{bot_id}_{user_id}.cookies"
    if not path.exists():
        raise NotLoggedInError("未找到登录信息，请先登录！")
    cookie_jar = LWPCookieJar(filename=str(path))
    cookie_jar.load()
    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


def remove_cookies(user_id: str, bot_id: str):
    path = PLAYER_PATH / f"{bot_id}_{user_id}.cookies"
    if path.exists():
        path.unlink()


def save_login_info(user_id: str, bot_id: str, login_info: LoginInfo):
    info_path = PLAYER_PATH / f"{bot_id}_{user_id}.json"
    info_path.write_text(login_info.to_json(), encoding="utf-8")


def get_login_info(user_id: str, bot_id: str) -> LoginInfo:
    info_path = PLAYER_PATH / f"{bot_id}_{user_id}.json"
    if not info_path.exists():
        raise NotLoggedInError("未找到登录信息，请先登录！")
    return LoginInfo.from_json(info_path.read_text(encoding="utf-8"))


def remove_login_info(user_id: str, bot_id: str):
    info_path = PLAYER_PATH / f"{bot_id}_{user_id}.json"
    if info_path.exists():
        info_path.unlink()
    remove_cookies(user_id, bot_id)


async def get_client(user_id: str, bot_id: str) -> ApiClient:
    login_info = get_login_info(user_id, bot_id)
    configuration = Configuration(
        username=login_info.username,
        password=login_info.password,
    )
    configuration.client_side_validation = False
    client = ApiClient(configuration)
    try:
        load_cookies_to_client(client, user_id, bot_id)
    except NotLoggedInError:
        pass
    return client


def check_client_usable(client: ApiClient) -> bool:
    from vrchatapi.api import NotificationsApi

    api = NotificationsApi(client)
    try:
        api.get_notifications(n=1)
    except UnauthorizedException:
        return False
    return True
