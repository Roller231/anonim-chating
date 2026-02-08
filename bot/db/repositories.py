from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

_UNSET = object()

from bot.db.models import (
    Chat,
    ChatStatus,
    InterestOption,
    MessageLog,
    Rating,
    RatingValue,
    Referral,
    Room,
    SearchQueue,
    User,
    UserInterest,
    VipPlan,
)


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, telegram_id: int, **kwargs) -> User:
        stmt = select(User).options(selectinload(User.interests)).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, **kwargs)
            self.session.add(user)
            await self.session.flush()
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).options(selectinload(User.interests)).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_telegram_ids(self, exclude_vip: bool = False) -> list[int]:
        """Get all registered user telegram_ids. If exclude_vip, skip VIP users."""
        stmt = select(User.telegram_id).where(User.is_registered == True)
        if exclude_vip:
            stmt = stmt.where(User.is_vip == False)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_profile(
        self,
        telegram_id: int,
        gender=None,
        age_min=None,
        age_max=None,
        country=None,
        is_registered=None,
        username=None,
        first_name=None,
    ) -> None:
        values = {}
        if gender is not None:
            values["gender"] = gender
        if age_min is not None:
            values["age_min"] = age_min
        if age_max is not None:
            values["age_max"] = age_max
        if country is not None:
            values["country"] = country
        if is_registered is not None:
            values["is_registered"] = is_registered
        if username is not None:
            values["username"] = username
        if first_name is not None:
            values["first_name"] = first_name
        if values:
            stmt = update(User).where(User.telegram_id == telegram_id).values(**values)
            await self.session.execute(stmt)

    async def update_preferences(
        self,
        telegram_id: int,
        pref_gender=_UNSET,
        pref_age_min=_UNSET,
        pref_age_max=_UNSET,
        pref_country=_UNSET,
    ) -> None:
        values = {}
        if pref_gender is not _UNSET:
            values["pref_gender"] = pref_gender
        if pref_age_min is not _UNSET:
            values["pref_age_min"] = pref_age_min
        if pref_age_max is not _UNSET:
            values["pref_age_max"] = pref_age_max
        if pref_country is not _UNSET:
            values["pref_country"] = pref_country
        if values:
            stmt = update(User).where(User.telegram_id == telegram_id).values(**values)
            await self.session.execute(stmt)

    async def set_interests(self, user_id: int, interests: list[str]) -> None:
        await self.session.execute(
            delete(UserInterest).where(UserInterest.user_id == user_id)
        )
        for interest in interests:
            self.session.add(UserInterest(user_id=user_id, interest=interest.strip()))
        await self.session.flush()

    async def increment_messages(self, telegram_id: int) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(messages_count=User.messages_count + 1)
        )
        await self.session.execute(stmt)

    async def increment_chats(self, telegram_id: int) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(chats_count=User.chats_count + 1)
        )
        await self.session.execute(stmt)

    async def add_karma(self, telegram_id: int, is_like: bool) -> None:
        if is_like:
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(karma_likes=User.karma_likes + 1)
            )
        else:
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(karma_dislikes=User.karma_dislikes + 1)
            )
        await self.session.execute(stmt)

    async def top_by_karma(self, limit: int = 10) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_registered == True)
            .order_by((User.karma_likes - User.karma_dislikes).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def top_by_referrals(self, limit: int = 10) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_registered == True)
            .order_by(User.referral_count.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def top_by_activity(self, limit: int = 10) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_registered == True)
            .order_by(User.messages_count.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_referral(self, referrer_telegram_id: int) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == referrer_telegram_id)
            .values(
                referral_count=User.referral_count + 1,
                referral_points=User.referral_points + 1,
            )
        )
        await self.session.execute(stmt)

    async def exchange_points(self, telegram_id: int, points: int) -> bool:
        user = await self.get_by_telegram_id(telegram_id)
        if user is None or user.referral_points < points:
            return False
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(referral_points=User.referral_points - points)
        )
        await self.session.execute(stmt)
        return True

    async def check_gender_search_limit(self, telegram_id: int, limit: int = 5) -> tuple[bool, int]:
        """Check if user can do gender search. Returns (can_search, remaining)."""
        from datetime import date as date_cls
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return False, 0
        today = date_cls.today()
        if user.gender_searches_date != today:
            # New day — reset
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(gender_searches_today=0, gender_searches_date=today)
            )
            await self.session.execute(stmt)
            return True, limit
        remaining = limit - user.gender_searches_today
        return remaining > 0, max(remaining, 0)

    async def increment_gender_search(self, telegram_id: int) -> None:
        from datetime import date as date_cls
        today = date_cls.today()
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return
        if user.gender_searches_date != today:
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(gender_searches_today=1, gender_searches_date=today)
            )
        else:
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(gender_searches_today=User.gender_searches_today + 1)
            )
        await self.session.execute(stmt)

    async def deactivate_expired_vip(self) -> int:
        """Set is_vip=False for users whose vip_until has passed. Returns count."""
        now = datetime.now()
        stmt = (
            update(User)
            .where(User.is_vip == True, User.vip_until != None, User.vip_until <= now)
            .values(is_vip=False)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def activate_vip(self, telegram_id: int, days: int) -> datetime:
        """Activate or extend VIP. Returns new vip_until datetime."""
        from datetime import timedelta
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        now = datetime.now()
        if user.vip_until and user.vip_until > now:
            new_until = user.vip_until + timedelta(days=days)
        else:
            new_until = now + timedelta(days=days)
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_vip=True, vip_until=new_until)
        )
        await self.session.execute(stmt)
        return new_until


class ChatRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_chat(self, telegram_id: int) -> Chat | None:
        stmt = select(Chat).where(
            Chat.status == ChatStatus.ACTIVE,
            (Chat.user1_id == telegram_id) | (Chat.user2_id == telegram_id),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_chat(self, user1_id: int, user2_id: int, room_id: int | None = None) -> Chat:
        chat = Chat(user1_id=user1_id, user2_id=user2_id, status=ChatStatus.ACTIVE, room_id=room_id)
        self.session.add(chat)
        await self.session.flush()
        return chat

    async def end_chat(self, chat_id: int) -> None:
        stmt = (
            update(Chat)
            .where(Chat.id == chat_id)
            .values(status=ChatStatus.ENDED, ended_at=func.now())
        )
        await self.session.execute(stmt)

    async def increment_messages(self, chat_id: int) -> None:
        stmt = (
            update(Chat)
            .where(Chat.id == chat_id)
            .values(messages_count=Chat.messages_count + 1)
        )
        await self.session.execute(stmt)

    def get_partner_id(self, chat: Chat, my_telegram_id: int) -> int:
        return chat.user2_id if chat.user1_id == my_telegram_id else chat.user1_id


class SearchQueueRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_to_queue(self, user: User, room_id: int | None = None) -> SearchQueue:
        existing = await self.get_from_queue(user.telegram_id)
        if existing:
            return existing
        entry = SearchQueue(
            telegram_id=user.telegram_id,
            gender=user.gender,
            age_min=user.age_min,
            age_max=user.age_max,
            country=user.country,
            pref_gender=user.pref_gender,
            pref_age_min=user.pref_age_min,
            pref_age_max=user.pref_age_max,
            pref_country=user.pref_country,
            is_vip=user.is_vip,
            room_id=room_id,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_from_queue(self, telegram_id: int) -> SearchQueue | None:
        stmt = select(SearchQueue).where(SearchQueue.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def remove_from_queue(self, telegram_id: int) -> None:
        stmt = delete(SearchQueue).where(SearchQueue.telegram_id == telegram_id)
        await self.session.execute(stmt)

    ROOM_FALLBACK_SECONDS = 10

    async def find_match(self, user: User, room_id: int | None = None) -> SearchQueue | None:
        if room_id is not None:
            # Room search: match same room, ignore gender/age/country
            result = await self._find_room_match(user, room_id)
            if result:
                return result
            # Fallback: global search (anyone, including room users >10s)
            return await self._find_global_match(user, strict=False)
        else:
            # Global search
            result = await self._find_global_match(user, strict=True)
            if result:
                return result
            return await self._find_global_match(user, strict=False)

    async def _find_room_match(self, user: User, room_id: int) -> SearchQueue | None:
        """Match within same room — no gender/age/country filter."""
        stmt = (
            select(SearchQueue)
            .where(SearchQueue.telegram_id != user.telegram_id)
            .where(SearchQueue.room_id == room_id)
            .order_by(SearchQueue.is_vip.desc(), SearchQueue.joined_at.asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _find_global_match(self, user: User, strict: bool = True) -> SearchQueue | None:
        """Global match. Also picks up room users who waited >10s."""
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(seconds=self.ROOM_FALLBACK_SECONDS)

        stmt = (
            select(SearchQueue)
            .where(SearchQueue.telegram_id != user.telegram_id)
        )

        conditions = []

        # Include: users with no room, OR room users waiting >10s
        conditions.append(
            (SearchQueue.room_id == None) | (SearchQueue.joined_at <= cutoff)
        )

        # Gender — strict both directions
        if user.pref_gender is not None:
            conditions.append(SearchQueue.gender == user.pref_gender)
        conditions.append(
            (SearchQueue.pref_gender == None) | (SearchQueue.pref_gender == user.gender)
        )

        if strict:
            # Country — only in strict pass
            if user.pref_country is not None:
                conditions.append(SearchQueue.country == user.pref_country)
            conditions.append(
                (SearchQueue.pref_country == None) | (SearchQueue.pref_country == user.country)
            )

        stmt = stmt.where(*conditions)
        stmt = stmt.order_by(SearchQueue.is_vip.desc(), SearchQueue.joined_at.asc())
        stmt = stmt.limit(1)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def queue_size(self) -> int:
        stmt = select(func.count()).select_from(SearchQueue)
        result = await self.session.execute(stmt)
        return result.scalar_one()


class RatingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_rating(
        self, chat_id: int, from_tg_id: int, to_tg_id: int, value: RatingValue
    ) -> Rating:
        rating = Rating(
            chat_id=chat_id,
            from_telegram_id=from_tg_id,
            to_telegram_id=to_tg_id,
            value=value,
        )
        self.session.add(rating)
        await self.session.flush()
        return rating

    async def has_rated(self, chat_id: int, from_tg_id: int) -> bool:
        stmt = select(Rating).where(
            Rating.chat_id == chat_id, Rating.from_telegram_id == from_tg_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


class ReferralRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, referrer_tg_id: int, referred_tg_id: int) -> Referral:
        ref = Referral(
            referrer_telegram_id=referrer_tg_id,
            referred_telegram_id=referred_tg_id,
        )
        self.session.add(ref)
        await self.session.flush()
        return ref

    async def get_by_referred(self, referred_tg_id: int) -> Referral | None:
        stmt = select(Referral).where(Referral.referred_telegram_id == referred_tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class VipPlanRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> list[VipPlan]:
        stmt = (
            select(VipPlan)
            .where(VipPlan.is_active == True)
            .order_by(VipPlan.sort_order.asc(), VipPlan.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, plan_id: int) -> VipPlan | None:
        stmt = select(VipPlan).where(VipPlan.id == plan_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def seed_defaults(self) -> None:
        stmt = select(func.count()).select_from(VipPlan)
        result = await self.session.execute(stmt)
        if result.scalar_one() > 0:
            return
        defaults = [
            ("1 день", 1, 15, None, None, "⭐", 1),
            ("7 дней", 7, 150, None, None, "⭐", 2),
            ("1 месяц", 30, 250, None, "(-60%)", "⭐", 3),
            ("12 месяцев", 365, 400, None, None, "🎉", 4),
        ]
        for name, days, stars, ton, discount, emoji, order in defaults:
            self.session.add(VipPlan(
                name=name, duration_days=days, price_stars=stars,
                price_ton=ton, discount_text=discount, emoji=emoji, sort_order=order,
            ))
        await self.session.flush()


class RoomRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> list[Room]:
        stmt = (
            select(Room)
            .where(Room.is_active == True)
            .order_by(Room.sort_order.asc(), Room.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, room_id: int) -> Room | None:
        stmt = select(Room).where(Room.id == room_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def seed_defaults(self) -> None:
        stmt = select(func.count()).select_from(Room)
        result = await self.session.execute(stmt)
        if result.scalar_one() > 0:
            return
        defaults = [
            ("Флирт", "❤️", "Романтическое общение и знакомства", 1),
            ("Дружба", "🤝", "Найти новых друзей", 2),
            ("Игры", "🎮", "Обсуждение игр и поиск тиммейтов", 3),
            ("Музыка", "🎵", "Обсуждение музыки и обмен треками", 4),
            ("IT", "💻", "Технические разговоры и кодинг", 5),
            ("Кино", "🎬", "Обсуждение фильмов и сериалов", 6),
            ("18+", "🔞", "Только для совершеннолетних", 7),
        ]
        for name, emoji, desc, order in defaults:
            self.session.add(Room(name=name, emoji=emoji, description=desc, sort_order=order))
        await self.session.flush()


class MessageLogRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        chat_id: int,
        sender_id: int,
        receiver_id: int,
        content_type: str,
        text: str | None = None,
        file_id: str | None = None,
        caption: str | None = None,
    ) -> None:
        entry = MessageLog(
            chat_id=chat_id,
            sender_telegram_id=sender_id,
            receiver_telegram_id=receiver_id,
            content_type=content_type,
            text=text,
            file_id=file_id,
            caption=caption,
        )
        self.session.add(entry)
        await self.session.flush()


class InterestRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> list[InterestOption]:
        stmt = (
            select(InterestOption)
            .where(InterestOption.is_active == True)
            .order_by(InterestOption.sort_order.asc(), InterestOption.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def seed_defaults(self) -> None:
        """Seed default interests if table is empty."""
        stmt = select(func.count()).select_from(InterestOption)
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        if count > 0:
            return

        defaults = [
            ("Общение", "💬", 1),
            ("Флирт", "❤️", 2),
            ("Игры", "🎮", 3),
            ("Музыка", "🎵", 4),
            ("Книги", "📚", 5),
            ("Кино", "🎬", 6),
            ("Спорт", "⚽", 7),
            ("IT", "💻", 8),
            ("Путешествия", "✈️", 9),
            ("Еда", "🍕", 10),
            ("Искусство", "🎨", 11),
            ("Наука", "🔬", 12),
            ("Фото", "📷", 13),
            ("Мода", "👗", 14),
            ("Авто", "🚗", 15),
            ("Природа", "🌿", 16),
        ]
        for name, emoji, order in defaults:
            self.session.add(InterestOption(name=name, emoji=emoji, sort_order=order))
        await self.session.flush()
