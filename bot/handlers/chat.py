import time
from collections import defaultdict

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo, ChatRepo, RatingRepo
from bot.db.models import RatingValue
from bot.keyboards.inline import rating_keyboard
from bot.services.chat import ChatService

router = Router()

MEDIA_LIMIT = 2
MEDIA_WINDOW_SECONDS = 15

# In-memory rate limiter: {telegram_id: [timestamp, timestamp, ...]}
_media_timestamps: dict[int, list[float]] = defaultdict(list)


async def _check_media_allowed(message: Message, session: AsyncSession) -> bool:
    """Non-VIP: max 2 media per 15 seconds. VIP: unlimited."""
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if user and user.is_vip:
        return True

    uid = message.from_user.id
    now = time.time()

    # Clean old timestamps outside the window
    _media_timestamps[uid] = [
        t for t in _media_timestamps[uid] if now - t < MEDIA_WINDOW_SECONDS
    ]

    if len(_media_timestamps[uid]) >= MEDIA_LIMIT:
        oldest = _media_timestamps[uid][0]
        wait = int(MEDIA_WINDOW_SECONDS - (now - oldest)) + 1
        await message.answer(
            f"⏳ Лимит медиа: {MEDIA_LIMIT} шт. за {MEDIA_WINDOW_SECONDS} сек.\n"
            f"Подождите {wait} сек.\n"
            f"👑 VIP пользователи отправляют медиа без ограничений!"
        )
        return False

    _media_timestamps[uid].append(now)
    return True


@router.message(Command("stop"))
async def cmd_stop(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    chat_service = ChatService(bot, session)
    result, partner_id, chat_id = await chat_service.stop_chat(message.from_user.id)

    if chat_id:
        await message.answer(result, reply_markup=rating_keyboard(chat_id))
    else:
        await message.answer(result)


@router.message(Command("next"))
async def cmd_next(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    chat_service = ChatService(bot, session)
    result = await chat_service.next_chat(user)
    await message.answer(result)


@router.message(Command("lnk"))
async def cmd_lnk(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)

    if not partner_id:
        await message.answer("❌ У вас нет активного чата.")
        return

    username = message.from_user.username
    if username:
        link = f"👤 Собеседник отправил вам ссылку на свой профиль:\n👉 @{username}"
    else:
        link = f"👤 Собеседник отправил вам ссылку на свой профиль:\n👉 tg://user?id={message.from_user.id}"

    try:
        await bot.send_message(partner_id, link)
        await message.answer("✅ Ссылка на ваш профиль отправлена собеседнику!")
    except Exception:
        await message.answer("❌ Не удалось отправить ссылку.")


# --- Rating callback ---

@router.callback_query(F.data.startswith("rate:"))
async def process_rating(
    callback: CallbackQuery,
    session: AsyncSession,
):
    parts = callback.data.split(":")
    chat_id = int(parts[1])
    action = parts[2]

    if action == "skip":
        await callback.message.edit_text("⏭ Вы пропустили оценку.")
        await callback.answer()
        return

    rating_repo = RatingRepo(session)
    user_repo = UserRepo(session)

    already = await rating_repo.has_rated(chat_id, callback.from_user.id)
    if already:
        await callback.answer("Вы уже оценили этого собеседника!", show_alert=True)
        return

    from bot.db.models import Chat
    from sqlalchemy import select
    stmt = select(Chat).where(Chat.id == chat_id)
    result = await session.execute(stmt)
    chat = result.scalar_one_or_none()

    if not chat:
        await callback.answer("Чат не найден.", show_alert=True)
        return

    partner_id = chat.user2_id if chat.user1_id == callback.from_user.id else chat.user1_id

    value = RatingValue.LIKE if action == "like" else RatingValue.DISLIKE
    await rating_repo.add_rating(chat_id, callback.from_user.id, partner_id, value)
    await user_repo.add_karma(partner_id, is_like=(action == "like"))

    emoji = "👍" if action == "like" else "👎"
    await callback.message.edit_text(f"{emoji} Вы поставили {'лайк' if action == 'like' else 'дизлайк'} собеседнику.")
    await callback.answer()


# --- Message relay (must be last!) ---

@router.message(F.text & ~F.text.startswith("/"))
async def relay_text_message(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.relay_message(message.from_user.id, message.text)

    if partner_id is None:
        await message.answer(
            "💤 У вас нет активного чата.\nНажмите /start чтобы найти собеседника."
        )
        return

    try:
        await bot.send_message(partner_id, message.text)
    except Exception:
        await message.answer("❌ Не удалось доставить сообщение.")


@router.message(F.photo)
async def relay_photo(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    if not await _check_media_allowed(message, session):
        return
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)
    if not partner_id:
        await message.answer("💤 У вас нет активного чата.")
        return
    try:
        fid = message.photo[-1].file_id
        await bot.send_photo(partner_id, fid, caption=message.caption)
        await chat_service.relay_message(
            message.from_user.id, "[photo]",
            content_type="photo", file_id=fid, caption=message.caption,
        )
    except Exception:
        await message.answer("❌ Не удалось доставить фото.")


@router.message(F.sticker)
async def relay_sticker(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    if not await _check_media_allowed(message, session):
        return
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)
    if not partner_id:
        await message.answer("💤 У вас нет активного чата.")
        return
    try:
        fid = message.sticker.file_id
        await bot.send_sticker(partner_id, fid)
        await chat_service.relay_message(
            message.from_user.id, "[sticker]",
            content_type="sticker", file_id=fid,
        )
    except Exception:
        await message.answer("❌ Не удалось доставить стикер.")


@router.message(F.voice)
async def relay_voice(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    if not await _check_media_allowed(message, session):
        return
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)
    if not partner_id:
        await message.answer("💤 У вас нет активного чата.")
        return
    try:
        fid = message.voice.file_id
        await bot.send_voice(partner_id, fid)
        await chat_service.relay_message(
            message.from_user.id, "[voice]",
            content_type="voice", file_id=fid,
        )
    except Exception:
        await message.answer("❌ Не удалось доставить голосовое сообщение.")


@router.message(F.video)
async def relay_video(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    if not await _check_media_allowed(message, session):
        return
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)
    if not partner_id:
        await message.answer("💤 У вас нет активного чата.")
        return
    try:
        fid = message.video.file_id
        await bot.send_video(partner_id, fid, caption=message.caption)
        await chat_service.relay_message(
            message.from_user.id, "[video]",
            content_type="video", file_id=fid, caption=message.caption,
        )
    except Exception:
        await message.answer("❌ Не удалось доставить видео.")


@router.message(F.video_note)
async def relay_video_note(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    if not await _check_media_allowed(message, session):
        return
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)
    if not partner_id:
        await message.answer("💤 У вас нет активного чата.")
        return
    try:
        fid = message.video_note.file_id
        await bot.send_video_note(partner_id, fid)
        await chat_service.relay_message(
            message.from_user.id, "[video_note]",
            content_type="video_note", file_id=fid,
        )
    except Exception:
        await message.answer("❌ Не удалось доставить видеосообщение.")


@router.message(F.document)
async def relay_document(
    message: Message,
    session: AsyncSession,
    bot: Bot,
):
    if not await _check_media_allowed(message, session):
        return
    chat_service = ChatService(bot, session)
    partner_id = await chat_service.get_active_partner(message.from_user.id)
    if not partner_id:
        await message.answer("💤 У вас нет активного чата.")
        return
    try:
        fid = message.document.file_id
        await bot.send_document(partner_id, fid, caption=message.caption)
        await chat_service.relay_message(
            message.from_user.id, "[document]",
            content_type="document", file_id=fid, caption=message.caption,
        )
    except Exception:
        await message.answer("❌ Не удалось доставить документ.")
