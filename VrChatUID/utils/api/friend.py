import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import FriendsApi

from ._helpers import log_api_response


def get_all_friends(client: ApiClient, max_size: int = 100):
    """获取所有好友列表（同步生成器）"""
    api = FriendsApi(client)
    page_size = 100
    offset = 0
    yielded = 0
    while yielded < max_size:
        friends = api.get_friends(offset=offset, n=page_size)
        log_api_response(f"get_friends(offset={offset})", friends)
        if not friends:
            break
        for friend in friends:
            if yielded >= max_size:
                return
            yield friend
            yielded += 1
        if len(friends) < page_size:
            break
        offset += page_size


async def get_friends(client: ApiClient, offset: int = 0, n: int = 100):
    """获取好友列表（在线/离线，async 版本）"""
    api = FriendsApi(client)
    result = await asyncio.to_thread(api.get_friends, offset=offset, n=n)
    log_api_response(f"get_friends(offset={offset}, n={n})", result)
    return result
