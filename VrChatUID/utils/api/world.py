from vrchatapi import ApiClient
from vrchatapi.api import WorldsApi


async def search_worlds(client: ApiClient, search: str, max_size: int = 10):
    api = WorldsApi(client)
    offset = 0
    count = 0
    while count < max_size:
        worlds = api.search_worlds(search=search, offset=offset, n=20)
        if not worlds:
            break
        for world in worlds:
            yield world
            count += 1
            if count >= max_size:
                break
        if len(worlds) < 20:
            break
        offset += 20


async def get_world(client: ApiClient, world_id: str):
    api = WorldsApi(client)
    return api.get_world(world_id=world_id)
