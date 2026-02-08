from aiogram import Router, F
from aiogram.types import PreCheckoutQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo

router = Router()


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Always approve — Telegram Stars payments are instant."""
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, session: AsyncSession):
    payment = message.successful_payment
    payload = payment.invoice_payload  # "vip_plan:{id}:{days}"

    if not payload.startswith("vip_plan:"):
        return

    parts = payload.split(":")
    duration_days = int(parts[2])

    user_repo = UserRepo(session)
    new_until = await user_repo.activate_vip(message.from_user.id, duration_days)
    await session.commit()

    await message.answer(
        f"✅ Оплата прошла успешно!\n\n"
        f"👑 VIP статус активирован до {new_until.strftime('%d.%m.%Y %H:%M')} UTC\n\n"
        f"Наслаждайтесь преимуществами VIP! 🎉"
    )
