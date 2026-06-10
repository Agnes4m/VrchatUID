"""VRChat 凭证管理模块

将登录凭证（邮箱、密码、cookie、display_name）存储在 VrChatUser 表中，
通过 VrChatBind 表的 uid 字段（|分隔多账号）实现多账号绑定与切换。
"""

from pathlib import Path

from gsuid_core.logger import logger

from .models import VrChatBind, VrChatUser


class VrcCredential:
    """VRChat 账号凭证集合"""

    def __init__(
        self,
        vrc_uid: str = "",
        username: str = "",
        password: str = "",
        cookie: str = "",
        display_name: str = "",
        user_id: str = "",
    ):
        self.vrc_uid = vrc_uid
        self.username = username
        self.password = password
        self.cookie = cookie
        self.display_name = display_name
        self.user_id = user_id

    def to_dict(self) -> dict:
        return {
            "vrc_uid": self.vrc_uid,
            "username": self.username,
            "password": self.password,
            "cookie": self.cookie,
            "display_name": self.display_name,
            "user_id": self.user_id,
        }


async def get_current_uid(user_id: str, bot_id: str) -> str | None:
    """获取当前用户绑定的活跃 VRChat 账号 uid"""
    result = await VrChatBind.get_current_vrc_uid(user_id=user_id, bot_id=bot_id)
    print(f"[VRC] get_current_uid: user_id={user_id}, bot_id={bot_id}, result={result}")
    return result


async def get_user_credentials(user_id: str, bot_id: str, vrc_uid: str | None = None) -> VrcCredential | None:
    """从 VrChatUser 表读取凭证。

    如果未指定 vrc_uid，则使用 Bind 表中当前活跃的 uid。
    """
    if vrc_uid is None:
        vrc_uid = await get_current_uid(user_id, bot_id)
        if vrc_uid is None:
            print(f"[VRC] get_user_credentials: 未找到当前 uid, user_id={user_id}")
            return None

    cred = await VrChatUser.select_data_by_uid(vrc_uid, "vrc")
    if cred is None:
        print(f"[VRC] get_user_credentials: VrChatUser 表中未找到 vrc_uid={vrc_uid} 的记录")
        return None

    credential = VrcCredential(
        vrc_uid=cred.vrc_uid or "",
        username=cred.vrc_username or "",
        password=cred.vrc_password or "",
        cookie=cred.cookie or cred.vrc_cookie or "",
        display_name=cred.vrc_display_name or "",
        user_id=cred.vrc_user_id or "",
    )
    print(
        f"[VRC] get_user_credentials 成功获取: "
        f"vrc_uid={credential.vrc_uid}, "
        f"username={credential.username}, "
        f"display_name={credential.display_name}, "
        f"cookie_len={len(credential.cookie)}, "
        f"password_len={len(credential.password)}"
    )
    return credential


async def save_credentials(
    user_id: str,
    bot_id: str,
    vrc_uid: str,
    username: str,
    password: str,
    cookie: str = "",
    display_name: str = "",
    vrc_user_id: str = "",
) -> None:
    """保存凭证到 VrChatUser 表，并更新 Bind 表的 uid 列表

    Args:
        user_id: 平台用户ID（如QQ号）
        bot_id: 平台标识
        vrc_uid: VRChat 账号ID
        username: 登录邮箱
        password: 登录密码
        cookie: 登录后的 cookie（可选）
        display_name: VRChat 显示名称
        vrc_user_id: VRChat 内部 user_id
    """
    print(
        f"[VRC] save_credentials 开始: "
        f"user_id={user_id}, bot_id={bot_id}, "
        f"vrc_uid={vrc_uid}, username={username}, "
        f"display_name={display_name}, "
        f"password_len={len(password)}, cookie_len={len(cookie)}"
    )

    # 1. 写入 VrChatUser 表（按 vrc_uid 索引）
    #    - User 基类自带 cookie 字段用于存放 session 凭据
    #    - vrc_cookie 字段用于存放完整 cookie 字符串
    user_data = await VrChatUser.select_data_by_uid(vrc_uid, "vrc")
    print(f"[VRC] VrChatUser.select_data_by_uid 旧记录: {'存在' if user_data else '不存在'}")
    if user_data is None:
        await VrChatUser.full_insert_data(
            user_id=user_id,
            bot_id=bot_id,
            cookie=cookie,  # User 基类的 cookie 字段
            stoken=None,
            vrc_uid=vrc_uid,
            vrc_username=username,
            vrc_password=password,
            vrc_cookie=cookie,
            vrc_display_name=display_name,
            vrc_user_id=vrc_user_id,
        )
        print(f"[VRC] VrChatUser.full_insert_data 完成: vrc_uid={vrc_uid}")
    else:
        await VrChatUser.update_data_by_uid(
            vrc_uid,
            bot_id=None,
            game_name="vrc",
            cookie=cookie,  # 同步更新 User 基类的 cookie 字段
            vrc_username=username,
            vrc_password=password,
            vrc_cookie=cookie,
            vrc_display_name=display_name,
            vrc_user_id=vrc_user_id,
        )
        print(f"[VRC] VrChatUser.update_data_by_uid 完成: vrc_uid={vrc_uid}")

    # 验证数据已写入
    verify_cred = await VrChatUser.select_data_by_uid(vrc_uid, "vrc")
    if verify_cred:
        print(
            f"[VRC] 验证 VrChatUser 写入: "
            f"vrc_uid={verify_cred.vrc_uid}, "
            f"vrc_username={verify_cred.vrc_username}, "
            f"vrc_password_len={len(verify_cred.vrc_password or '')}, "
            f"vrc_cookie_len={len(verify_cred.vrc_cookie or '')}, "
            f"cookie_len={len(verify_cred.cookie or '')}"
        )
    else:
        print(f"[VRC] ⚠️ 验证失败: VrChatUser 中找不到 vrc_uid={vrc_uid}")

    # 2. 更新 Bind 表的 uid 列表（用 | 分隔，去重 + 当前活跃账号置首位）
    bind_code = await VrChatBind.add_vrc_uid(
        user_id=user_id,
        bot_id=bot_id,
        vrc_uid=vrc_uid,
    )
    print(f"[VRC] VrChatBind.add_vrc_uid 返回: {bind_code}")

    # 验证 Bind 表状态
    bind_data = await VrChatBind.select_data(user_id, bot_id)
    if bind_data:
        print(f"[VRC] 验证 VrChatBind: user_id={bind_data.user_id}, bot_id={bind_data.bot_id}, uid='{bind_data.uid}'")

    logger.info(f"VRC 凭证已保存: user_id={user_id}, vrc_uid={vrc_uid}")


async def list_binds(user_id: str, bot_id: str) -> list[str]:
    """获取用户绑定的所有 VRChat 账号 uid 列表"""
    result = await VrChatBind.get_vrc_uid_list(user_id=user_id, bot_id=bot_id)
    print(f"[VRC] list_binds: user_id={user_id}, bot_id={bot_id}, result={result}")
    return result


async def switch_uid(user_id: str, bot_id: str, vrc_uid: str) -> int:
    """切换当前活跃 VRChat 账号

    Returns:
        0: 成功
        -1: 没有绑定记录
        -2: uid 不在绑定列表中
    """
    code = await VrChatBind.switch_vrc_uid(user_id=user_id, bot_id=bot_id, vrc_uid=vrc_uid)
    print(f"[VRC] switch_uid: user_id={user_id}, bot_id={bot_id}, vrc_uid={vrc_uid}, code={code}")
    return code


async def remove_bind(user_id: str, bot_id: str, vrc_uid: str) -> int:
    """解绑某个 VRChat 账号（同时从 User 表删除凭证）"""
    print(f"[VRC] remove_bind 开始: user_id={user_id}, bot_id={bot_id}, vrc_uid={vrc_uid}")
    code = await VrChatBind.remove_vrc_uid(user_id=user_id, bot_id=bot_id, vrc_uid=vrc_uid)
    if code == 0:
        # 删除对应的凭证记录
        cred = await VrChatUser.select_data_by_uid(vrc_uid, "vrc")
        if cred is not None:
            await VrChatUser.delete_data(cred.user_id, cred.bot_id)
            print(f"[VRC] 已删除 VrChatUser 记录: vrc_uid={vrc_uid}")
        else:
            print(f"[VRC] 未找到 VrChatUser 记录: vrc_uid={vrc_uid}")
    print(f"[VRC] remove_bind 完成: code={code}")
    return code


async def clear_all_binds(user_id: str, bot_id: str) -> None:
    """清除用户所有 VRChat 绑定与凭证"""
    print(f"[VRC] clear_all_binds 开始: user_id={user_id}, bot_id={bot_id}")
    uid_list = await list_binds(user_id, bot_id)
    for vrc_uid in uid_list:
        cred = await VrChatUser.select_data_by_uid(vrc_uid, "vrc")
        if cred is not None:
            await VrChatUser.delete_data(cred.user_id, cred.bot_id)
            print(f"[VRC] 已删除 VrChatUser 记录: vrc_uid={vrc_uid}")
    bind_data = await VrChatBind.select_data(user_id, bot_id)
    if bind_data is not None:
        await VrChatBind.delete_data(user_id, bot_id)
        print("[VRC] 已删除 VrChatBind 记录")
    print("[VRC] clear_all_binds 完成")


# ----- Cookie 文件同步 -----

# 旧的 cookie 文件位置，保留向后兼容
_PLAYER_PATH = Path.home() / ".local" / "share" / "GsCore" / "vrchat" / "player"


def _cookie_file_path(bot_id: str, user_id: str, vrc_uid: str) -> Path:
    """生成 cookie 文件路径（按 vrc_uid 区分多账号）"""
    return _PLAYER_PATH / f"{bot_id}_{user_id}_{vrc_uid}.cookies"


async def save_cookie_file(bot_id: str, user_id: str, vrc_uid: str, cookie_text: str) -> Path:
    """保存 cookie 字符串到文件"""
    _PLAYER_PATH.mkdir(parents=True, exist_ok=True)
    path = _cookie_file_path(bot_id, user_id, vrc_uid)
    path.write_text(cookie_text, encoding="utf-8")
    return path


def extract_cookies_from_client(client) -> str:
    """从 VRChat ApiClient 提取 cookie 字符串

    格式：name1=value1; name2=value2; ...
    """
    parts: list[str] = []
    try:
        for cookie in client.rest_client.cookie_jar:
            parts.append(f"{cookie.name}={cookie.value}")
    except Exception as e:
        print(f"[VRC] 提取 cookie 失败: {e}")
    return "; ".join(parts)


def get_current_vrc_uid(bot_id: str, user_id: str) -> str | None:
    """同步版本：用于非 async 上下文"""
    # 目前未使用，保留以备后用
    return None
