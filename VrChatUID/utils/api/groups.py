from vrchatapi import ApiClient
from vrchatapi.api import GroupsApi
from vrchatapi.models import JoinGroupRequest


async def search_groups(client: ApiClient, keyword: str, max_size: int = 10):
    """搜索群组"""
    api = GroupsApi(client)
    offset = 0
    count = 0
    while count < max_size:
        groups = api.search_groups(query=keyword, offset=offset, n=20)
        if not groups:
            break
        for group in groups:
            yield group
            count += 1
            if count >= max_size:
                break
        if len(groups) < 20:
            break
        offset += 20


async def get_group(client: ApiClient, group_id: str):
    """获取群组信息"""
    api = GroupsApi(client)
    return api.get_group(group_id=group_id)


async def get_group_members(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组成员列表"""
    api = GroupsApi(client)
    return api.get_group_members(group_id=group_id, n=n, offset=offset)


async def get_group_roles(client: ApiClient, group_id: str):
    """获取群组角色列表"""
    api = GroupsApi(client)
    return api.get_group_roles(group_id=group_id)


async def get_group_announcements(client: ApiClient, group_id: str):
    """获取群组公告"""
    api = GroupsApi(client)
    return api.get_group_announcements(group_id=group_id)


async def join_group(client: ApiClient, group_id: str):
    """加入群组"""
    api = GroupsApi(client)
    api.join_group(group_id=group_id, confirm_override_block=True, join_group_request=JoinGroupRequest())
    return True


async def leave_group(client: ApiClient, group_id: str):
    """离开群组"""
    api = GroupsApi(client)
    api.leave_group(group_id=group_id)
    return True


async def get_group_invites(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组邀请列表"""
    api = GroupsApi(client)
    return api.get_group_invites(group_id=group_id, n=n, offset=offset)


async def get_group_requests(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组请求列表"""
    api = GroupsApi(client)
    return api.get_group_requests(group_id=group_id, n=n, offset=offset)


async def get_group_instances(client: ApiClient, group_id: str):
    """获取群组实例列表"""
    api = GroupsApi(client)
    return api.get_group_instances(group_id=group_id)


async def get_group_permissions(client: ApiClient, group_id: str):
    """获取群组权限信息"""
    api = GroupsApi(client)
    return api.get_group_permissions(group_id=group_id)


async def kick_group_member(client: ApiClient, group_id: str, user_id: str):
    """踢出群组成员"""
    api = GroupsApi(client)
    api.kick_group_member(group_id=group_id, user_id=user_id)
    return True


async def add_member_role(client: ApiClient, group_id: str, user_id: str, role_id: str):
    """给群组成员添加角色"""
    api = GroupsApi(client)
    api.add_member_role(group_id=group_id, user_id=user_id, role_id=role_id)
    return True


async def remove_member_role(client: ApiClient, group_id: str, user_id: str, role_id: str):
    """从群组成员移除角色"""
    api = GroupsApi(client)
    api.remove_member_role(group_id=group_id, user_id=user_id, role_id=role_id)
    return True


async def create_group_announcement(
    client: ApiClient, group_id: str, title: str, text: str, image_url: str | None = None
):
    """创建群组公告"""
    from vrchatapi.models import CreateGroupAnnouncementRequest

    api = GroupsApi(client)
    request = CreateGroupAnnouncementRequest(title=title, text=text, image_url=image_url)
    return api.create_group_announcement(group_id=group_id, create_group_announcement_request=request)


async def delete_group_announcement(client: ApiClient, group_id: str, announcement_id: str):
    """删除群组公告"""
    api = GroupsApi(client)
    api.delete_group_announcement(group_id=group_id, announcement_id=announcement_id)
    return True


async def get_group_posts(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组帖子列表"""
    api = GroupsApi(client)
    return api.get_group_posts(group_id=group_id, n=n, offset=offset)


async def create_group_post(client: ApiClient, group_id: str, title: str, text: str):
    """创建群组帖子"""
    from vrchatapi.models import CreateGroupPostRequest

    api = GroupsApi(client)
    request = CreateGroupPostRequest(title=title, text=text)
    return api.create_group_post(group_id=group_id, create_group_post_request=request)


async def delete_group_post(client: ApiClient, group_id: str, post_id: str):
    """删除群组帖子"""
    api = GroupsApi(client)
    api.delete_group_post(group_id=group_id, post_id=post_id)
    return True


async def get_group_gallery(client: ApiClient, group_id: str):
    """获取群组画廊信息"""
    api = GroupsApi(client)
    return api.get_group_gallery(group_id=group_id)


async def get_group_gallery_images(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组画廊图片列表"""
    api = GroupsApi(client)
    return api.get_group_gallery_images(group_id=group_id, n=n, offset=offset)


async def invite_user_to_group(client: ApiClient, group_id: str, user_id: str):
    """邀请用户加入群组"""
    from vrchatapi.models import GroupInviteRequest

    api = GroupsApi(client)
    api.invite_user_to_group(group_id=group_id, group_invite_request=GroupInviteRequest(user_id=user_id))
    return True


async def delete_group_invite(client: ApiClient, group_id: str, user_id: str):
    """删除群组邀请"""
    api = GroupsApi(client)
    api.delete_group_invite(group_id=group_id, user_id=user_id)
    return True


async def respond_to_group_join_request(client: ApiClient, group_id: str, user_id: str, accept: bool):
    """响应群组加入请求"""
    api = GroupsApi(client)
    api.respond_to_group_join_request(group_id=group_id, user_id=user_id, accept=accept)
    return True


async def cancel_group_join_request(client: ApiClient, group_id: str):
    """取消群组加入请求"""
    api = GroupsApi(client)
    api.cancel_group_join_request(group_id=group_id)
    return True


async def get_group_bans(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组封禁列表"""
    api = GroupsApi(client)
    return api.get_group_bans(group_id=group_id, n=n, offset=offset)


async def ban_group_member(client: ApiClient, group_id: str, user_id: str):
    """封禁群组成员"""
    api = GroupsApi(client)
    api.ban_group_member(group_id=group_id, user_id=user_id)
    return True


async def unban_group_member(client: ApiClient, group_id: str, user_id: str):
    """解除封禁群组成员"""
    api = GroupsApi(client)
    api.unban_group_member(group_id=group_id, user_id=user_id)
    return True


async def get_group_audit_logs(client: ApiClient, group_id: str, n: int = 20, offset: int = 0):
    """获取群组审计日志"""
    api = GroupsApi(client)
    return api.get_group_audit_logs(group_id=group_id, n=n, offset=offset)


async def update_group_representation(client: ApiClient, group_id: str, represent: bool):
    """更新群组代表身份"""
    api = GroupsApi(client)
    api.update_group_representation(group_id=group_id, represent=represent)
    return True


async def get_my_group_member(client: ApiClient, group_id: str):
    """获取当前用户在群组中的成员信息"""
    api = GroupsApi(client)
    return api.get_my_group_member(group_id=group_id)
