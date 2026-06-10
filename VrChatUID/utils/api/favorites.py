import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import FavoritesApi
from vrchatapi.models import AddFavoriteRequest, UpdateFavoriteGroupRequest

from ._helpers import log_api_response


def get_favorites(client: ApiClient, favorite_type: str, tag: str = "", max_size: int = 20):
    """获取收藏列表（同步生成器）"""
    api = FavoritesApi(client)
    page_size = 100
    offset = 0
    yielded = 0
    while yielded < max_size:
        favorites = api.get_favorites(type=favorite_type, tag=tag, offset=offset, n=page_size)
        log_api_response(f"get_favorites(type={favorite_type}, offset={offset})", favorites)
        if not favorites:
            break
        for fav in favorites:
            if yielded >= max_size:
                return
            yield fav
            yielded += 1
        if len(favorites) < page_size:
            break
        offset += page_size


def get_favorite_groups(client: ApiClient, max_size: int = 50):
    """获取收藏组列表（同步生成器）"""
    api = FavoritesApi(client)
    page_size = 100
    offset = 0
    yielded = 0
    while yielded < max_size:
        groups = api.get_favorite_groups(offset=offset, n=page_size)
        log_api_response(f"get_favorite_groups(offset={offset})", groups)
        if not groups:
            break
        for group in groups:
            if yielded >= max_size:
                return
            yield group
            yielded += 1
        if len(groups) < page_size:
            break
        offset += page_size


async def add_favorite(client: ApiClient, favorite_type: str, favorite_id: str, tags: list[str] | None = None):
    """添加收藏"""
    api = FavoritesApi(client)
    request = AddFavoriteRequest(
        type=favorite_type,
        favorite_id=favorite_id,
        tags=tags or [],
    )
    result = await asyncio.to_thread(api.add_favorite, add_favorite_request=request)
    log_api_response(f"add_favorite({favorite_type}, {favorite_id})", result)
    return result


async def remove_favorite(client: ApiClient, favorite_id: str):
    """删除收藏"""
    api = FavoritesApi(client)
    result = await asyncio.to_thread(api.remove_favorite, favorite_id=favorite_id)
    log_api_response(f"remove_favorite({favorite_id})", result)
    return result


async def get_favorite_group(client: ApiClient, favorite_group_type: str, favorite_group_name: str, user_id: str):
    """获取收藏组详情"""
    api = FavoritesApi(client)
    result = await asyncio.to_thread(
        api.get_favorite_group,
        favorite_group_type=favorite_group_type,
        favorite_group_name=favorite_group_name,
        user_id=user_id,
    )
    log_api_response(f"get_favorite_group({favorite_group_type}, {favorite_group_name})", result)
    return result


async def update_favorite_group(
    client: ApiClient,
    favorite_group_type: str,
    favorite_group_name: str,
    user_id: str,
    update_data: dict,
):
    """更新收藏组"""
    api = FavoritesApi(client)
    request = UpdateFavoriteGroupRequest(**update_data)
    result = await asyncio.to_thread(
        api.update_favorite_group,
        favorite_group_type=favorite_group_type,
        favorite_group_name=favorite_group_name,
        user_id=user_id,
        update_favorite_group_request=request,
    )
    log_api_response(f"update_favorite_group({favorite_group_type}, {favorite_group_name})", result)
    return result


async def clear_favorite_group(client: ApiClient, favorite_group_type: str, favorite_group_name: str, user_id: str):
    """清空收藏组"""
    api = FavoritesApi(client)
    result = await asyncio.to_thread(
        api.clear_favorite_group,
        favorite_group_type=favorite_group_type,
        favorite_group_name=favorite_group_name,
        user_id=user_id,
    )
    log_api_response(f"clear_favorite_group({favorite_group_type}, {favorite_group_name})", result)
    return result


async def get_favorite_limits(client: ApiClient):
    """获取收藏限制信息"""
    api = FavoritesApi(client)
    result = await asyncio.to_thread(api.get_favorite_limits)
    log_api_response("get_favorite_limits", result)
    return result
