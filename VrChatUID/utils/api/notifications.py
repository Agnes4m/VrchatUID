from vrchatapi import ApiClient
from vrchatapi.api import NotificationsApi


async def get_notifications(client: ApiClient, n: int = 60):
    """获取通知列表"""
    api = NotificationsApi(client)
    offset = 0
    count = 0
    while count < n:
        notifications = api.get_notifications(offset=offset, n=100)
        if not notifications:
            break
        for notif in notifications:
            yield notif
            count += 1
            if count >= n:
                break
        if len(notifications) < 100:
            break
        offset += 100


async def get_notification(client: ApiClient, notification_id: str):
    """获取指定通知详情"""
    api = NotificationsApi(client)
    return api.get_notification(notification_id=notification_id)


async def accept_friend_request(client: ApiClient, notification_id: str):
    """接受好友请求"""
    api = NotificationsApi(client)
    return api.accept_friend_request(notification_id=notification_id)


async def mark_notification_as_read(client: ApiClient, notification_id: str):
    """将通知标记为已读"""
    api = NotificationsApi(client)
    return api.mark_notification_as_read(notification_id=notification_id)


async def delete_notification(client: ApiClient, notification_id: str):
    """删除通知"""
    api = NotificationsApi(client)
    return api.delete_notification(notification_id=notification_id)
