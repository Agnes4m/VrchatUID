from vrchatapi import ApiClient
from vrchatapi.api import FriendsApi


async def get_all_friends(client: ApiClient, max_size: int = 100):
    api = FriendsApi(client)
    offset = 0
    while True:
        friends = api.get_friends(offset=offset, n=100)
        if not friends:
            break
        for friend in friends:
            yield friend
        if len(friends) < 100:
            break
        offset += 100
        if offset >= max_size:
            break


async def get_friends(client: ApiClient, offset: int = 0, n: int = 100):
    api = FriendsApi(client)
    return api.get_friends(offset=offset, n=n)
