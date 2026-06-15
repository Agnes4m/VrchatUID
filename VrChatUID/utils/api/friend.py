import asyncio

from gsuid_core.logger import logger
from vrchatapi import ApiClient
from vrchatapi.api import FriendsApi

from ._helpers import log_api_response


def get_all_friends(client: ApiClient, max_size: int = 200):
    """获取全部好友（在线+离线），同步生成器

    VRChat ``/auth/user/friends`` 端点行为：
    - ``offline=True``   只返回离线
    - ``offline=False``  只返回在线+活跃
    - 不传 offline 时服务端按 active 过滤，会漏掉离线好友

    因此分别用两种 offline 取一次，按 id 去重合并。
    """
    api = FriendsApi(client)
    page_size = 100
    seen_ids: set[str] = set()
    total_yielded = 0

    for offline_flag in (False, True):
        label = "online" if offline_flag is False else "offline"
        offset = 0
        sub_yielded = 0
        while total_yielded < max_size:
            try:
                friends = api.get_friends(offset=offset, n=page_size, offline=offline_flag)
            except Exception:
                logger.exception(f"[get_all_friends] {label} offset={offset} 请求失败")
                raise
            recv = len(friends) if friends else 0
            log_api_response(f"get_friends(offset={offset}, n={page_size}, offline={offline_flag})", friends)
            if not friends:
                break
            for f in friends:
                fid = getattr(f, "id", None) or getattr(f, "user_id", None)
                if fid is None or fid in seen_ids or total_yielded >= max_size:
                    continue
                seen_ids.add(fid)
                sub_yielded += 1
                total_yielded += 1
                yield f
            if recv < page_size:
                break
            offset += page_size
        logger.info(f"[get_all_friends] {label} 子查询完成: {sub_yielded} 人")

    logger.info(f"[get_all_friends] 总计: {total_yielded} 位好友")


async def get_friends(client: ApiClient, offset: int = 0, n: int = 100, offline: bool | None = None):
    """异步获取好友列表（按 offline 过滤）

    Args:
        offline: None=不传(走服务端默认), True=仅离线, False=仅在线+活跃
    """
    api = FriendsApi(client)
    kwargs: dict = {"offset": offset, "n": n}
    if offline is not None:
        kwargs["offline"] = offline
    result = await asyncio.to_thread(api.get_friends, **kwargs)
    log_api_response(f"get_friends(offset={offset}, n={n}, offline={offline})", result)
    return result
