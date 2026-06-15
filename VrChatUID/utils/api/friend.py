import asyncio

from vrchatapi import ApiClient
from vrchatapi.api import FriendsApi

from ._helpers import log_api_response


def get_all_friends(client: ApiClient, max_size: int = 200):
    """获取所有好友列表（在线+离线），同步生成器

    VRChat API 行为（已通过文档+实测验证）：
    - ``offline=True``   只返回离线用户
    - ``offline=False``  只返回在线+活跃用户
    - 不传 ``offline``   服务端默认按"active"过滤，会漏掉大量离线好友

    实现策略：分别用 ``offline=True`` 和 ``offline=False`` 各拉一次，
    按 ``id`` 去重合并，再 yield。

    翻页策略：每个子查询每页 100（API 上限），翻到 len < page_size 为止。
    """
    from gsuid_core.logger import logger

    api = FriendsApi(client)
    page_size = 100
    logger.info(f"[get_all_friends] START: max_size={max_size}, page_size={page_size}")

    seen_ids: set[str] = set()
    total_yielded = 0

    for offline_flag in (False, True):
        sub_label = "online" if offline_flag is False else "offline"
        offset = 0
        sub_no = 0
        sub_yielded = 0
        logger.info(f"[get_all_friends] [{sub_label}] START")
        while total_yielded < max_size:
            sub_no += 1
            try:
                friends = api.get_friends(offset=offset, n=page_size, offline=offline_flag)
            except Exception as e:
                logger.exception(f"[get_all_friends] [{sub_label}] page#{sub_no} EXCEPTION: {type(e).__name__}: {e}")
                raise
            recv_count = len(friends) if friends is not None else 0
            logger.info(
                f"[get_all_friends] [{sub_label}] page#{sub_no} "
                f"offset={offset} received={recv_count} total={total_yielded}/{max_size}"
            )
            log_api_response(f"get_friends(offset={offset}, n={page_size}, offline={offline_flag})", friends)
            if not friends:
                break
            for _friend in friends:
                fid = getattr(_friend, "id", None) or getattr(_friend, "user_id", None)
                if fid is None or fid in seen_ids:
                    continue
                if total_yielded >= max_size:
                    logger.info(f"[get_all_friends] REACHED max_size={max_size} -> STOP")
                    return
                seen_ids.add(fid)
                sub_yielded += 1
                total_yielded += 1
                yield _friend
            if recv_count < page_size:
                break
            offset += page_size
        logger.info(f"[get_all_friends] [{sub_label}] END: sub_yielded={sub_yielded}")

    logger.info(f"[get_all_friends] END: total_yielded={total_yielded}")


async def get_friends(client: ApiClient, offset: int = 0, n: int = 100, offline: bool | None = None):
    """获取好友列表（按 offline 过滤），async 版本

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
