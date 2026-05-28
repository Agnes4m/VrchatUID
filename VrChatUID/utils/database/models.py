from typing import Optional

from sqlmodel import Field

from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.utils.database.base_models import Bind

exec_list.extend(
    [
        "ALTER TABLE vrchatbind ADD COLUMN user_id VARCHAR",
        "ALTER TABLE vrchatbind ADD COLUMN group_id VARCHAR",
        "ALTER TABLE vrchatbind ADD COLUMN uid VARCHAR",
    ]
)


class VrChatBind(Bind):
    model_config = {"table": True}  # type: ignore

    uid: Optional[str] = Field(default=None, title="VRChat 用户ID")
    vrc_username: Optional[str] = Field(default=None, title="VRChat 用户名")
    vrc_password: Optional[str] = Field(default=None, title="VRChat 密码")
    vrc_cookie: Optional[str] = Field(default=None, title="VRChat Cookie")
    vrc_display_name: Optional[str] = Field(default=None, title="VRChat 显示名称")


@site.register_admin
class VrChatBindAdmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(label="VRChat 绑定管理", icon="fa fa-gamepad")  # type: ignore
    model = VrChatBind
