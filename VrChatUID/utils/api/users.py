import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import UsersApi

from ...vrc_config import get_search_user_max_size
from ._helpers import log_api_response


def search_users(client: ApiClient, keyword: str, max_size: int | None = None):
    """搜索用户（同步生成器）

    Args:
        max_size: 最大返回数；为 None 时从 vrc_config 读取
    """
    if max_size is None:
        max_size = get_search_user_max_size()
    api = UsersApi(client)
    page_size = 20
    offset = 0
    yielded = 0
    while yielded < max_size:
        users = api.search_users(search=keyword, offset=offset, n=page_size)
        log_api_response(f"search_users(keyword={keyword}, offset={offset})", users)
        if not users:
            break
        for user in users:
            if yielded >= max_size:
                return
            yield user
            yielded += 1
        if len(users) < page_size:
            break
        offset += page_size


async def get_user(client: ApiClient, user_id: str):
    """通过用户ID获取用户信息"""
    api = UsersApi(client)
    result = await asyncio.to_thread(api.get_user, user_id=user_id)
    log_api_response(f"get_user({user_id})", result)
    return result


async def get_user_by_name(client: ApiClient, username: str):
    """通过用户名获取用户信息"""
    api = UsersApi(client)
    result = await asyncio.to_thread(api.get_user_by_name, username=username)
    log_api_response(f"get_user_by_name({username})", result)
    return result


async def get_friend_status(client: ApiClient, user_id: str):
    """获取好友状态"""
    api = UsersApi(client)
    result = await asyncio.to_thread(api.get_friend_status, user_id=user_id)
    log_api_response(f"get_friend_status({user_id})", result)
    return result


async def friend(client: ApiClient, user_id: str):
    """发送好友请求"""
    api = UsersApi(client)
    result = await asyncio.to_thread(api.friend, user_id=user_id)
    log_api_response(f"friend({user_id})", result)
    return result


async def get_user_groups(client: ApiClient, user_id: str):
    """获取用户加入的群组列表"""
    api = UsersApi(client)
    result = await asyncio.to_thread(api.get_user_groups, user_id=user_id)
    log_api_response(f"get_user_groups({user_id})", result)
    return result
