import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import WorldsApi

from ...vrc_config import get_search_world_max_size
from ._helpers import log_api_response


def search_worlds(client: ApiClient, search: str, max_size: int | None = None):
    """搜索世界（同步生成器）

    Args:
        max_size: 最大返回数；为 None 时从 vrc_config 读取
    """
    if max_size is None:
        max_size = get_search_world_max_size()
    api = WorldsApi(client)
    page_size = 20
    offset = 0
    yielded = 0
    while yielded < max_size:
        worlds = api.search_worlds(search=search, offset=offset, n=page_size)
        log_api_response(f"search_worlds(search={search}, offset={offset})", worlds)
        if not worlds:
            break
        for world in worlds:
            if yielded >= max_size:
                return
            yield world
            yielded += 1
        if len(worlds) < page_size:
            break
        offset += page_size


async def get_world(client: ApiClient, world_id: str):
    """通过世界ID获取世界信息"""
    api = WorldsApi(client)
    result = await asyncio.to_thread(api.get_world, world_id=world_id)
    log_api_response(f"get_world({world_id})", result)
    return result
