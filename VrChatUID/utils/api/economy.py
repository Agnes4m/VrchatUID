import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import AuthenticationApi, EconomyApi


async def get_current_user_id(client: ApiClient) -> str:
    """获取当前登录用户的ID"""
    api = AuthenticationApi(client)
    current_user = await asyncio.to_thread(api.get_current_user)
    if hasattr(current_user, "id"):
        return current_user.id
    if hasattr(current_user, "to_dict"):
        return current_user.to_dict().get("id", "")
    return ""


async def get_balance(client: ApiClient, user_id: str):
    """获取用户余额信息"""
    api = EconomyApi(client)
    return await asyncio.to_thread(api.get_balance, user_id=user_id)


async def get_balance_earnings(client: ApiClient, user_id: str):
    """获取用户收益信息"""
    api = EconomyApi(client)
    return await asyncio.to_thread(api.get_balance_earnings, user_id=user_id)


async def get_economy_account(client: ApiClient, user_id: str):
    """获取经济账户信息"""
    api = EconomyApi(client)
    return await asyncio.to_thread(api.get_economy_account, user_id=user_id)


async def get_current_subscriptions(client: ApiClient):
    """获取当前订阅信息"""
    api = EconomyApi(client)
    return await asyncio.to_thread(api.get_current_subscriptions)


async def get_subscriptions(client: ApiClient):
    """获取订阅列表"""
    api = EconomyApi(client)
    return await asyncio.to_thread(api.get_current_subscriptions)


async def get_tilia_status(client: ApiClient):
    """获取Tilia状态信息"""
    api = EconomyApi(client)
    return await asyncio.to_thread(api.get_tilia_status)
