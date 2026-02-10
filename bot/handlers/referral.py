from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo

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
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    ref_link = f"https://t.me/{bot_username}?start={message.from_user.id}"

    await message.answer(
        f"💼 Реферальный кабинет\n\n"
        f"    🔮 Баллов: {user.referral_points}\n"
        f"    🎪 Приглашено: {user.referral_count}\n\n"
        f"💱 Обмен баллов:\n"
        f"Обменять 10 баллов на 1 день VIP статуса 👑 — /exchange\n\n"
        f"Для получения баллов распространяйте свою персональную ссылку:\n"
        f"👉 {ref_link}\n\n"
        f"Пример рассылки:\n\n"
        f"Бот для анонимного общения в Telegram! 🎭\n"
        f"Поиск по полу, возрасту и стране 😻\n\n"
        f"Скорее регистрируйся по моей ссылке, чтобы получить VIP статус!\n\n"
        f"👉 {ref_link}"
    )


@router.message(Command("exchange"))
async def cmd_exchange(
    message: Message,
    session: AsyncSession,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    if user.referral_points < 10:
        await message.answer(
            f"❌ Недостаточно баллов!\n\n"
            f"У вас: {user.referral_points} баллов\n"
            f"Необходимо: 10 баллов\n\n"
            f"Приглашайте друзей по реферальной ссылке: /ref"
        )
        return

    success = await user_repo.exchange_points(message.from_user.id, 10)
    if success:
        new_vip = await user_repo.activate_vip(message.from_user.id, days=1)
        await session.commit()

        await message.answer(
            f"✅ Обмен успешен!\n\n"
            f"👑 VIP статус активирован до {new_vip.strftime('%d.%m.%Y %H:%M')}\n"
            f"🔮 Осталось баллов: {user.referral_points - 10}"
        )
    else:
        await message.answer("❌ Ошибка при обмене. Попробуйте позже.")
