import asyncio
import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo
from bot.i18n import LANG
from bot.states.registration import BroadcastStates

router = Router()
logger = logging.getLogger(__name__)

ADMIN_ID = 1008871802

# Temporary storage for album collection: {media_group_id: [messages]}
_album_buf: dict[str, list[Message]] = {}
_album_lock = asyncio.Lock()


def _is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


# ─── /send and /sendvip commands ───

@router.message(Command("send"))
async def cmd_send(message: Message, state: FSMContext):
    if not _is_admin(message):
        return
    await state.set_state(BroadcastStates.waiting_content)
    await state.update_data(exclude_vip=False)
    await message.answer("📢 Отправьте сообщение для рассылки ВСЕМ пользователям.\n\n/cancel — отмена")


@router.message(Command("sendvip"))
async def cmd_sendvip(message: Message, state: FSMContext):
    if not _is_admin(message):
        return
    await state.set_state(BroadcastStates.waiting_content)
    await state.update_data(exclude_vip=True)
    await message.answer(
        "📢 Отправьте сообщение для рассылки пользователям БЕЗ VIP подписки.\n\n/cancel — отмена"
    )


@router.message(BroadcastStates.waiting_content, Command("cancel"))
async def cmd_cancel_broadcast(message: Message, state: FSMContext):
    if not _is_admin(message):
        return
    await state.clear()
    await message.answer("❌ Рассылка отменена.")


# ─── Handle album (media_group) ───

@router.message(BroadcastStates.waiting_content, F.media_group_id)
async def collect_album(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if not _is_admin(message):
        return

    group_id = message.media_group_id

    async with _album_lock:
        if group_id not in _album_buf:
            _album_buf[group_id] = []
            # Schedule processing after a short delay to collect all parts
            asyncio.create_task(_process_album_delayed(group_id, state, session, bot, message))
        _album_buf[group_id].append(message)


async def _process_album_delayed(
    group_id: str,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    trigger_msg: Message,
):
    """Wait for all album parts to arrive, then broadcast."""
    await asyncio.sleep(1.0)  # wait for all parts

    async with _album_lock:
        messages = _album_buf.pop(group_id, [])

    if not messages:
        return

    # Sort by message_id to preserve order
    messages.sort(key=lambda m: m.message_id)

    # Build media group
    media_group = []
    for i, msg in enumerate(messages):
        caption = msg.caption if i == 0 else None
        entities = msg.caption_entities if i == 0 else None
        if msg.photo:
            item = InputMediaPhoto(
                media=msg.photo[-1].file_id,
                caption=caption,
                caption_entities=entities,
            )
        elif msg.video:
            item = InputMediaVideo(
                media=msg.video.file_id,
                caption=caption,
                caption_entities=entities,
            )
        else:
            continue
        media_group.append(item)

    if not media_group:
        return

    data = await state.get_data()
    exclude_vip = data.get("exclude_vip", False)
    await state.clear()

    user_repo = UserRepo(session)
    user_ids = await user_repo.get_all_telegram_ids(exclude_vip=exclude_vip, locale=LANG)

    success, fail = 0, 0
    for uid in user_ids:
        try:
            await bot.send_media_group(uid, media=media_group)
            success += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)  # rate limit

    label = f"{LANG}/no-vip" if exclude_vip else f"{LANG}/all"
    await trigger_msg.answer(f"✅ Альбом отправлен ({label}):\n📨 {success} доставлено, ❌ {fail} ошибок")
    logger.info(f"Broadcast album ({label}): {success} ok, {fail} fail")


# ─── Handle single message (text / photo / video) ───

@router.message(BroadcastStates.waiting_content)
async def broadcast_single(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if not _is_admin(message):
        return

    data = await state.get_data()
    exclude_vip = data.get("exclude_vip", False)
    await state.clear()

    user_repo = UserRepo(session)
    user_ids = await user_repo.get_all_telegram_ids(exclude_vip=exclude_vip, locale=LANG)

    success, fail = 0, 0
    for uid in user_ids:
        try:
            await _send_copy(bot, uid, message)
            success += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)

    label = f"{LANG}/no-vip" if exclude_vip else f"{LANG}/all"
    await message.answer(f"✅ Рассылка завершена ({label}):\n📨 {success} доставлено, ❌ {fail} ошибок")
    logger.info(f"Broadcast single ({label}): {success} ok, {fail} fail")


async def _send_copy(bot: Bot, chat_id: int, msg: Message):
    """Send a copy of the message preserving formatting, media, and captions."""
    if msg.text:
        await bot.send_message(
            chat_id,
            msg.text,
            entities=msg.entities,
        )
    elif msg.photo:
        await bot.send_photo(
            chat_id,
            msg.photo[-1].file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
        )
    elif msg.video:
        await bot.send_video(
            chat_id,
            msg.video.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
        )
    elif msg.document:
        await bot.send_document(
            chat_id,
            msg.document.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
        )
    elif msg.sticker:
        await bot.send_sticker(chat_id, msg.sticker.file_id)
    elif msg.voice:
        await bot.send_voice(
            chat_id,
            msg.voice.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
        )
    elif msg.video_note:
        await bot.send_video_note(chat_id, msg.video_note.file_id)
    elif msg.animation:
        await bot.send_animation(
            chat_id,
            msg.animation.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
        )
    else:
        # Fallback: copy as-is
        await msg.copy_to(chat_id)
