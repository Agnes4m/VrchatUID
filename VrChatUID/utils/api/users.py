from vrchatapi import ApiClient
from vrchatapi.api import UsersApi


async def search_users(client: ApiClient, keyword: str, max_size: int = 10):
    """搜索用户"""
    api = UsersApi(client)
    offset = 0
    count = 0
    while count < max_size:
        users = api.search_users(search=keyword, offset=offset, n=20)
        if not users:
            break
        for user in users:
            yield user
            count += 1
            if count >= max_size:
                break
        if len(users) < 20:
            break
        offset += 20


async def get_user(client: ApiClient, user_id: str):
    """通过用户ID获取用户信息"""
    api = UsersApi(client)
    return api.get_user(user_id=user_id)


async def get_user_by_name(client: ApiClient, username: str):
    """通过用户名获取用户信息"""
    api = UsersApi(client)
    return api.get_user_by_name(username=username)


async def get_friend_status(client: ApiClient, user_id: str):
    """获取好友状态"""
    api = UsersApi(client)
    return api.get_friend_status(user_id=user_id)


async def friend(client: ApiClient, user_id: str):
    """发送好友请求"""
    api = UsersApi(client)
    return api.friend(user_id=user_id)


async def get_user_groups(client: ApiClient, user_id: str):
    """获取用户加入的群组列表"""
    api = UsersApi(client)
    return api.get_user_groups(user_id=user_id)
