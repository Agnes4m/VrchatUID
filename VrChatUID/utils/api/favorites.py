import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import FavoritesApi
from vrchatapi.models import AddFavoriteRequest, UpdateFavoriteGroupRequest


def get_favorites(client: ApiClient, favorite_type: str, tag: str = "", max_size: int = 20):
    """获取收藏列表（同步生成器）"""
    api = FavoritesApi(client)
    offset = 0
    count = 0
    while count < max_size:
        favorites = api.get_favorites(type=favorite_type, tag=tag, offset=offset, n=100)
        if not favorites:
            break
        for fav in favorites:
            yield fav
            count += 1
            if count >= max_size:
                break
        if len(favorites) < 100:
            break
        offset += 100


def get_favorite_groups(client: ApiClient, max_size: int = 50):
    """获取收藏组列表（同步生成器）"""
    api = FavoritesApi(client)
    offset = 0
    count = 0
    while count < max_size:
        groups = api.get_favorite_groups(offset=offset, n=100)
        if not groups:
            break
        for group in groups:
            yield group
            count += 1
            if count >= max_size:
                break
        if len(groups) < 100:
            break
        offset += 100


async def add_favorite(client: ApiClient, favorite_type: str, favorite_id: str, tags: list[str] | None = None):
    """添加收藏"""
    api = FavoritesApi(client)
    request = AddFavoriteRequest(
        type=favorite_type,
        favorite_id=favorite_id,
        tags=tags or [],
    )
    return await asyncio.to_thread(api.add_favorite, add_favorite_request=request)


async def remove_favorite(client: ApiClient, favorite_id: str):
    """删除收藏"""
    api = FavoritesApi(client)
    return await asyncio.to_thread(api.remove_favorite, favorite_id=favorite_id)


async def get_favorite_group(client: ApiClient, favorite_group_type: str, favorite_group_name: str, user_id: str):
    """获取收藏组详情"""
    api = FavoritesApi(client)
    return await asyncio.to_thread(
        api.get_favorite_group,
        favorite_group_type=favorite_group_type,
        favorite_group_name=favorite_group_name,
        user_id=user_id,
    )


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
    return await asyncio.to_thread(
        api.update_favorite_group,
        favorite_group_type=favorite_group_type,
        favorite_group_name=favorite_group_name,
        user_id=user_id,
        update_favorite_group_request=request,
    )


async def clear_favorite_group(client: ApiClient, favorite_group_type: str, favorite_group_name: str, user_id: str):
    """清空收藏组"""
    api = FavoritesApi(client)
    return await asyncio.to_thread(
        api.clear_favorite_group,
        favorite_group_type=favorite_group_type,
        favorite_group_name=favorite_group_name,
        user_id=user_id,
    )


async def get_favorite_limits(client: ApiClient):
    """获取收藏限制信息"""
    api = FavoritesApi(client)
    return await asyncio.to_thread(api.get_favorite_limits)
