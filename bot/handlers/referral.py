from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo
from bot.i18n import T

router = Router()


@router.message(Command("ref"))
async def cmd_ref(
    message: Message,
    session: AsyncSession,
    bot_username: str,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    ref_link = f"https://t.me/{bot_username}?start={message.from_user.id}"
    await message.answer(
        T["ref_title"].format(
            points=user.referral_points,
            count=user.referral_count,
            ref_link=ref_link,
        )
    )


@router.message(Command("exchange"))
async def cmd_exchange(
    message: Message,
    session: AsyncSession,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    if user.referral_points < 10:
        await message.answer(T["exchange_not_enough"].format(points=user.referral_points))
        return

    success = await user_repo.exchange_points(message.from_user.id, 10)
    if success:
        new_vip = await user_repo.activate_vip(message.from_user.id, days=1)
        await session.commit()
        await message.answer(
            T["exchange_success"].format(
                until=new_vip.strftime("%d.%m.%Y %H:%M"),
                remaining=user.referral_points - 10,
            )
        )
    else:
        await message.answer(T["exchange_fail"])
