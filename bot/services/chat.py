from datetime import datetime

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.db.repositories import ChatRepo, UserRepo, MessageLogRepo
from bot.i18n import T
from bot.services.matching import MatchingService
from bot.keyboards.inline import rating_keyboard


class ChatService:
    def __init__(
        self,
        bot: Bot,
        session: AsyncSession,
    ):
        self.bot = bot
        self.session = session
        self.matching = MatchingService(session)
        self.chat_repo = ChatRepo(session)
        self.user_repo = UserRepo(session)
        self.msg_log = MessageLogRepo(session)

    async def cancel_search(self, telegram_id: int) -> bool:
        """Remove user from search queue. Returns True if was in queue."""
        in_queue = await self.matching.is_in_queue(telegram_id)
        if in_queue:
            await self.matching.remove_from_queue(telegram_id)
        return in_queue

    async def start_search(self, user: User, room_id: int | None = None) -> str:
        active_chat = await self.chat_repo.get_active_chat(user.telegram_id)
        if active_chat:
            return T["in_chat"]

        # Cancel previous search if any
        await self.cancel_search(user.telegram_id)

        match_id = await self.matching.find_match(user, room_id=room_id)

        if match_id:
            return await self._connect_users(user.telegram_id, match_id, room_id=room_id)
        else:
            await self.matching.add_to_queue(user, room_id=room_id)
            queue_size = await self.matching.queue_size()
            return T["searching"].format(count=queue_size)

    async def _connect_users(self, user1_id: int, user2_id: int, room_id: int | None = None) -> str:
        chat = await self.chat_repo.create_chat(user1_id, user2_id, room_id=room_id)

        await self.user_repo.increment_chats(user1_id)
        await self.user_repo.increment_chats(user2_id)
        await self.session.commit()

        partner = await self.user_repo.get_by_telegram_id(user2_id)
        my_user = await self.user_repo.get_by_telegram_id(user1_id)

        # Build messages for each user
        msg_for_user1 = self._build_connect_message(partner, viewer_is_vip=bool(my_user and my_user.is_vip))
        msg_for_user2 = self._build_connect_message(my_user, viewer_is_vip=bool(partner and partner.is_vip))

        try:
            await self.bot.send_message(user2_id, msg_for_user2)
        except Exception:
            pass

        return msg_for_user1

    def _build_connect_message(self, partner: User | None, viewer_is_vip: bool = False) -> str:
        vip_badge = " 👑" if partner and partner.is_vip else ""
        header = f"{T['connected_title']}{vip_badge}\n\n"

        info = self._format_partner_info(partner, detailed=viewer_is_vip)
        commands = "\n/next — /stop — /lnk"
        return f"{header}{info}{commands}"

    def _format_partner_info(self, user: User | None, detailed: bool = False) -> str:
        if not user:
            return ""
        parts = []
        if user.is_vip:
            parts.append("👑 VIP")

        if user.gender:
            g = T["gender_male_short"] + " ♂️" if user.gender.value == "male" else T["gender_female_short"] + " ♀️"
            parts.append(f"{T['partner_gender']}: {g}")

        if detailed:
            if user.age_min is not None and user.age_max is not None:
                parts.append(f"{T['partner_age']}: {user.age_min}-{user.age_max}")
            if user.country:
                parts.append(f"{T['partner_country']}: {user.country}")
            interests = [i.interest for i in user.interests] if user.interests else []
            if interests:
                parts.append(f"{T['partner_interests']}: {', '.join(interests)}")
        else:
            if user.is_vip:
                parts.append(T["partner_vip_yes"])

        return "\n".join(parts)

    async def stop_chat(self, telegram_id: int) -> tuple[str, int | None, int | None]:
        """Returns (message, partner_id, chat_id)"""
        # Also cancel any pending search
        was_searching = await self.cancel_search(telegram_id)

        active_chat = await self.chat_repo.get_active_chat(telegram_id)
        if not active_chat:
            if was_searching:
                return T["search_cancelled"], None, None
            return T["no_active_chat"], None, None

        partner_id = self.chat_repo.get_partner_id(active_chat, telegram_id)
        chat_id = active_chat.id

        await self.chat_repo.end_chat(active_chat.id)
        await self.session.commit()

        try:
            await self.bot.send_message(
                partner_id,
                T["partner_left"],
                reply_markup=rating_keyboard(chat_id),
            )
        except Exception:
            pass

        return (
            T["chat_stopped"],
            partner_id,
            chat_id,
        )

    async def next_chat(self, user: User, room_id: int | None = None) -> str:
        active_chat = await self.chat_repo.get_active_chat(user.telegram_id)
        if active_chat:
            partner_id = self.chat_repo.get_partner_id(active_chat, user.telegram_id)
            chat_id = active_chat.id
            await self.chat_repo.end_chat(active_chat.id)
            await self.session.commit()
            try:
                await self.bot.send_message(
                    partner_id,
                    T["partner_left_next"],
                    reply_markup=rating_keyboard(chat_id),
                )
            except Exception:
                pass

        return await self.start_search(user, room_id=room_id)

    async def relay_message(
        self,
        telegram_id: int,
        text: str,
        content_type: str = "text",
        file_id: str | None = None,
        caption: str | None = None,
    ) -> int | None:
        """Relay message to partner. Logs it. Returns partner_id or None."""
        active_chat = await self.chat_repo.get_active_chat(telegram_id)
        if not active_chat:
            return None

        partner_id = self.chat_repo.get_partner_id(active_chat, telegram_id)

        await self.chat_repo.increment_messages(active_chat.id)
        await self.user_repo.increment_messages(telegram_id)

        # Log message
        await self.msg_log.log(
            chat_id=active_chat.id,
            sender_id=telegram_id,
            receiver_id=partner_id,
            content_type=content_type,
            text=text if content_type == "text" else None,
            file_id=file_id,
            caption=caption,
        )

        return partner_id

    async def get_active_partner(self, telegram_id: int) -> int | None:
        active_chat = await self.chat_repo.get_active_chat(telegram_id)
        if not active_chat:
            return None
        return self.chat_repo.get_partner_id(active_chat, telegram_id)

    async def get_active_chat_start_time(self, telegram_id: int) -> datetime | None:
        """Get chat started_at for media delay check."""
        active_chat = await self.chat_repo.get_active_chat(telegram_id)
        if not active_chat:
            return None
        return active_chat.started_at
