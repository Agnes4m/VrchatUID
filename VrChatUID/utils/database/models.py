from gsuid_core.utils.database.base_models import Bind, User, with_session
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.webconsole.mount_app import GsAdminModel, PageSchema, site
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field

# VRChat 账号在数据库中用 | 分隔（不能用 _，因为 uid 内部含 _）
VRC_UID_SEPARATOR = "|"

exec_list.extend(
    [
        "ALTER TABLE vrchatbind ADD COLUMN uid VARCHAR",
        # 旧版字段保留，标记废弃
        "ALTER TABLE vrchatbind ADD COLUMN vrc_username VARCHAR",
        "ALTER TABLE vrchatbind ADD COLUMN vrc_password VARCHAR",
        "ALTER TABLE vrchatbind ADD COLUMN vrc_cookie VARCHAR",
        "ALTER TABLE vrchatbind ADD COLUMN vrc_display_name VARCHAR",
        # VrChatUser 表的新增字段（兼容老数据库）
        "ALTER TABLE vrchatuser ADD COLUMN vrc_uid VARCHAR",
        "ALTER TABLE vrchatuser ADD COLUMN vrc_username VARCHAR",
        "ALTER TABLE vrchatuser ADD COLUMN vrc_password VARCHAR",
        "ALTER TABLE vrchatuser ADD COLUMN vrc_cookie VARCHAR",
        "ALTER TABLE vrchatuser ADD COLUMN vrc_display_name VARCHAR",
        "ALTER TABLE vrchatuser ADD COLUMN vrc_user_id VARCHAR",
    ]
)


class VrChatBind(Bind):
    """单用户对多 VRChat 账号的绑定关系

    `uid` 字段为 | 分隔的字符串，记录该用户绑定的所有 VRChat 账号 ID。
    第一个为当前活跃账号。使用自定义的 multi-uid 方法管理（不能用 _ 分隔因为 uid 内部含 _）。
    """

    model_config = {"table": True}  # type: ignore

    uid: str | None = Field(default=None, title="VRChat 用户ID（多账号用 | 分隔）")

    @classmethod
    @with_session
    async def get_vrc_uid_list(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
    ) -> list[str]:
        """获取用户绑定的所有 VRChat 账号 uid 列表（按 | 分隔）"""
        bind = await cls.base_select_data(user_id=user_id, bot_id=bot_id)
        if not bind or not bind.uid:
            return []
        return [u for u in bind.uid.split(VRC_UID_SEPARATOR) if u]

    @classmethod
    @with_session
    async def get_current_vrc_uid(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
    ) -> str | None:
        """获取当前活跃的 VRChat uid（列表中的第一个）"""
        bind = await cls.base_select_data(user_id=user_id, bot_id=bot_id)
        if not bind or not bind.uid:
            return None
        first = bind.uid.split(VRC_UID_SEPARATOR)[0]
        return first or None

    @classmethod
    @with_session
    async def add_vrc_uid(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
        vrc_uid: str,
    ) -> int:
        """添加一个 VRChat 账号到绑定列表（去重，置为当前活跃）"""
        bind = await cls.base_select_data(user_id=user_id, bot_id=bot_id)
        if not bind:
            # 新建绑定记录，uid 字段为单一 vrc_uid
            new_bind = cls(user_id=user_id, bot_id=bot_id, uid=vrc_uid)
            session.add(new_bind)
            return 0

        if not bind.uid:
            bind.uid = vrc_uid
            return 0

        uid_list = [u for u in bind.uid.split(VRC_UID_SEPARATOR) if u]
        if vrc_uid in uid_list:
            return -2  # 已存在
        uid_list.insert(0, vrc_uid)
        bind.uid = VRC_UID_SEPARATOR.join(uid_list)
        return 0

    @classmethod
    @with_session
    async def remove_vrc_uid(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
        vrc_uid: str,
    ) -> int:
        """从绑定列表中移除一个 VRChat 账号"""
        bind = await cls.base_select_data(user_id=user_id, bot_id=bot_id)
        if not bind or not bind.uid:
            return -1

        uid_list = [u for u in bind.uid.split(VRC_UID_SEPARATOR) if u]
        if vrc_uid not in uid_list:
            return -1

        uid_list.remove(vrc_uid)
        bind.uid = VRC_UID_SEPARATOR.join(uid_list) if uid_list else None
        return 0

    @classmethod
    @with_session
    async def switch_vrc_uid(
        cls,
        session: AsyncSession,
        user_id: str,
        bot_id: str,
        vrc_uid: str,
    ) -> int:
        """切换当前活跃 VRChat 账号（移动到列表第一位）"""
        bind = await cls.base_select_data(user_id=user_id, bot_id=bot_id)
        if not bind or not bind.uid:
            return -1

        uid_list = [u for u in bind.uid.split(VRC_UID_SEPARATOR) if u]
        if vrc_uid not in uid_list:
            return -2
        if uid_list[0] == vrc_uid:
            return 0  # 已经是当前活跃

        uid_list.remove(vrc_uid)
        uid_list.insert(0, vrc_uid)
        bind.uid = VRC_UID_SEPARATOR.join(uid_list)
        return 0


@site.register_admin
class VrChatBindAdmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(label="VRChat 绑定管理", icon="fa fa-gamepad")  # type: ignore
    model = VrChatBind


class VrChatUser(User):
    """单个 VRChat 账号的完整凭证与登录信息

    字段：
    - vrc_uid: VRChat 用户ID（与 VrChatBind.uid 对应）
    - vrc_username: 登录邮箱
    - vrc_password: 登录密码（明文，建议未来加密）
    - vrc_cookie: VRChat Cookie（登录后保存）
    - vrc_display_name: VRChat 显示名称
    - vrc_user_id: VRChat 内部 user_id
    """

    model_config = {"table": True}  # type: ignore

    vrc_uid: str | None = Field(default=None, title="VRChat 用户ID", sa_column=Column("vrc_uid", String, index=True))
    vrc_username: str | None = Field(default=None, title="VRChat 登录邮箱")
    vrc_password: str | None = Field(default=None, title="VRChat 登录密码")
    vrc_cookie: str | None = Field(default=None, title="VRChat Cookie")
    vrc_display_name: str | None = Field(default=None, title="VRChat 显示名称")
    vrc_user_id: str | None = Field(default=None, title="VRChat 内部 user_id")


@site.register_admin
class VrChatUserAdmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(label="VRChat 账号凭证管理", icon="fa fa-user-secret")  # type: ignore
    model = VrChatUser
