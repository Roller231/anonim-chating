from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo
from bot.keyboards.inline import top_keyboard

router = Router()


@router.message(Command("top"))
async def cmd_top(message: Message):
    await message.answer(
        "🏆 Рейтинги чата\n\n"
        "Выберите вид рейтинга:",
        reply_markup=top_keyboard(),
    )


@router.callback_query(F.data.startswith("top:"))
async def process_top(callback: CallbackQuery, session: AsyncSession):
    top_type = callback.data.split(":")[1]
    user_repo = UserRepo(session)

    if top_type == "karma":
        users = await user_repo.top_by_karma(10)
        title = "👁️ Топ-10 по карме"
        lines = []
        for i, u in enumerate(users, 1):
            karma = u.karma_likes - u.karma_dislikes
            name = u.first_name or u.username or str(u.telegram_id)
            vip = " 👑" if u.is_vip else ""
            lines.append(f"{i}. {name}{vip} — 👍 {u.karma_likes} 👎 {u.karma_dislikes} (={karma})")

    elif top_type == "referrals":
        users = await user_repo.top_by_referrals(10)
        title = "🎪 Топ-10 по рефералам"
        lines = []
        for i, u in enumerate(users, 1):
            name = u.first_name or u.username or str(u.telegram_id)
            vip = " 👑" if u.is_vip else ""
            lines.append(f"{i}. {name}{vip} — {u.referral_count} приглашённых")

    else:  # activity
        users = await user_repo.top_by_activity(10)
        title = "📧 Топ-10 по активности"
        lines = []
        for i, u in enumerate(users, 1):
            name = u.first_name or u.username or str(u.telegram_id)
            vip = " 👑" if u.is_vip else ""
            lines.append(f"{i}. {name}{vip} — {u.messages_count} сообщений")

    if not lines:
        text = f"🏆 {title}\n\nПока никого нет в рейтинге."
    else:
        text = f"🏆 {title}\n\n" + "\n".join(lines)

    await callback.message.edit_text(text)
    await callback.answer()
