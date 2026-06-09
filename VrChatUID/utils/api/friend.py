import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import FriendsApi


def get_all_friends(client: ApiClient, max_size: int = 100):
    """获取所有好友列表（同步生成器）"""
    api = FriendsApi(client)
    offset = 0
    while True:
        friends = api.get_friends(offset=offset, n=100)
        if not friends:
            break
        yield from friends
        if len(friends) < 100:
            break
        offset += 100
        if offset >= max_size:
            break


async def get_friends(client: ApiClient, offset: int = 0, n: int = 100):
    """获取好友列表（在线/离线，async 版本）"""
    api = FriendsApi(client)
    return await asyncio.to_thread(api.get_friends, offset=offset, n=n)
