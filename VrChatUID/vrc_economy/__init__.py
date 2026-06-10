from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api.client import get_client_or_notify
from ..utils.api.economy import (
    get_balance,
    get_balance_earnings,
    get_current_subscriptions,
    get_current_user_id,
    get_economy_account,
    get_tilia_status,
)

sv = SV("经济")


@sv.on_command(("余额", "balance"))
async def vrc_balance(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在查询余额信息...")
        user_id_str = await get_current_user_id(client)
        balance = await get_balance(client, user_id_str)
        earnings = await get_balance_earnings(client, user_id_str)

        msg = "【VRChat 余额信息】\n\n"

        balance_val = getattr(balance, "balance", 0)
        pending = getattr(balance, "pending", 0)
        last_payout = getattr(balance, "last_payout", None)

        msg += f"当前余额: {balance_val}\n"
        msg += f"待处理: {pending}\n"
        if last_payout:
            msg += f"上次支付: {last_payout}\n"

        if isinstance(earnings, dict):
            balance_from_earnings = earnings.get("balance", "0")
            no_transactions = earnings.get("noTransactions")
            msg += f"\n收益余额: {balance_from_earnings}\n"
            if no_transactions is not None:
                msg += f"交易数量: {no_transactions}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"查询余额失败: {e}")
        await bot.send(f"查询余额失败：{str(e)}")


@sv.on_command(("账户", "economy"))
async def vrc_economy_account(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在查询账户信息...")
        user_id_str = await get_current_user_id(client)
        account = await get_economy_account(client, user_id_str)

        msg = "【VRChat 经济账户信息】\n\n"

        if isinstance(account, dict):
            account_id = account.get("id", "")
            status = account.get("status", "")
            created_at = account.get("created_at", "")
            updated_at = account.get("updated_at", "")

            msg += f"账户ID: {account_id}\n"
            msg += f"状态: {status}\n"
            if created_at:
                msg += f"创建时间: {created_at}\n"
            if updated_at:
                msg += f"更新时间: {updated_at}\n"
        else:
            account_id = getattr(account, "id", "")
            status = getattr(account, "status", "")
            msg += f"账户ID: {account_id}\n"
            msg += f"状态: {status}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"查询账户信息失败: {e}")
        await bot.send(f"查询账户信息失败：{str(e)}")


@sv.on_command(("订阅", "subs"))
async def vrc_subscriptions(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在查询订阅信息...")
        current_subs = await get_current_subscriptions(client)

        current_count = 0
        total_count = 0
        subs_list = []

        if isinstance(current_subs, dict):
            subs = current_subs.get("subscriptions", [])
            current_count = len(subs) if isinstance(subs, list) else 0

        if isinstance(current_subs, dict):
            all_subs = current_subs.get("subscriptions", [])
            if isinstance(all_subs, list):
                total_count = len(all_subs)
                subs_list = all_subs

        msg = "【VRChat 订阅信息】\n\n"
        msg += f"当前订阅数: {current_count}\n"
        msg += f"总订阅数: {total_count}\n\n"

        if subs_list:
            msg += "订阅列表：\n"
            for i, sub in enumerate(subs_list[:10], 1):
                if isinstance(sub, dict):
                    sub_type = sub.get("type", "未知")
                    status = sub.get("status", "未知")
                    msg += f"  {i}. 类型: {sub_type}, 状态: {status}\n"
                else:
                    sub_type = getattr(sub, "type", "未知")
                    status = getattr(sub, "status", "未知")
                    msg += f"  {i}. 类型: {sub_type}, 状态: {status}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"查询订阅信息失败: {e}")
        await bot.send(f"查询订阅信息失败：{str(e)}")


@sv.on_command(("tilia", "tilia状态"))
async def vrc_tilia_status(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在查询Tilia状态...")
        status = await get_tilia_status(client)

        msg = "【Tilia 状态信息】\n\n"

        if isinstance(status, dict):
            user_id_val = status.get("user_id", "")
            status_val = status.get("status", "")
            created_at = status.get("created_at", "")
            updated_at = status.get("updated_at", "")

            msg += f"用户ID: {user_id_val}\n"
            msg += f"状态: {status_val}\n"
            if created_at:
                msg += f"创建时间: {created_at}\n"
            if updated_at:
                msg += f"更新时间: {updated_at}\n"
        else:
            user_id_val = getattr(status, "user_id", "")
            status_val = getattr(status, "status", "")
            msg += f"用户ID: {user_id_val}\n"
            msg += f"状态: {status_val}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"查询Tilia状态失败: {e}")
        await bot.send(f"查询Tilia状态失败：{str(e)}")


@sv.on_command(("收益", "earnings"))
async def vrc_earnings(bot: Bot, ev: Event) -> None:
    user_id = ev.user_id
    bot_id = ev.bot_id

    client = await get_client_or_notify(bot, user_id, bot_id)
    if client is None:
        return

    try:
        await bot.send("正在查询收益信息...")
        user_id_str = await get_current_user_id(client)
        earnings = await get_balance_earnings(client, user_id_str)

        msg = "【VRChat 收益信息】\n\n"

        if isinstance(earnings, dict):
            balance = earnings.get("balance", "0")
            no_transactions = earnings.get("noTransactions")
            tilia_response = earnings.get("tilia_response")

            msg += f"余额: {balance}\n"
            if no_transactions is not None:
                msg += f"交易数量: {no_transactions}\n"
            if tilia_response:
                msg += f"Tilia响应: {tilia_response}\n"
        else:
            balance = getattr(earnings, "balance", "0")
            msg += f"余额: {balance}\n"

        await bot.send(msg)

    except Exception as e:
        logger.error(f"查询收益信息失败: {e}")
        await bot.send(f"查询收益信息失败：{str(e)}")
