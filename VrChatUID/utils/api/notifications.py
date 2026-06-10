import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import NotificationsApi

from ._helpers import log_api_response


def get_notifications(client: ApiClient, n: int = 60):
    """获取通知列表（同步生成器）

    Args:
        n: 最大返回数
    """
    api = NotificationsApi(client)
    page_size = 100
    offset = 0
    yielded = 0
    while yielded < n:
        notifications = api.get_notifications(offset=offset, n=page_size)
        log_api_response(f"get_notifications(offset={offset})", notifications)
        if not notifications:
            break
        for notif in notifications:
            if yielded >= n:
                return
            yield notif
            yielded += 1
        if len(notifications) < page_size:
            break
        offset += page_size


async def get_notification(client: ApiClient, notification_id: str):
    """获取指定通知详情"""
    api = NotificationsApi(client)
    result = await asyncio.to_thread(api.get_notification, notification_id=notification_id)
    log_api_response(f"get_notification({notification_id})", result)
    return result


async def accept_friend_request(client: ApiClient, notification_id: str):
    """接受好友请求"""
    api = NotificationsApi(client)
    result = await asyncio.to_thread(api.accept_friend_request, notification_id=notification_id)
    log_api_response(f"accept_friend_request({notification_id})", result)
    return result


async def mark_notification_as_read(client: ApiClient, notification_id: str):
    """将通知标记为已读"""
    api = NotificationsApi(client)
    result = await asyncio.to_thread(api.mark_notification_as_read, notification_id=notification_id)
    log_api_response(f"mark_notification_as_read({notification_id})", result)
    return result


async def delete_notification(client: ApiClient, notification_id: str):
    """删除通知"""
    api = NotificationsApi(client)
    result = await asyncio.to_thread(api.delete_notification, notification_id=notification_id)
    log_api_response(f"delete_notification({notification_id})", result)
    return result
