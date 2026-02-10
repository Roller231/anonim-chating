import enum
from datetime import datetime, date

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.engine import Base


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class ChatStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"


class RatingValue(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)
    age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Stats
    messages_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    chats_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    karma_likes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    karma_dislikes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # VIP
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    vip_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Referrals
    referral_points: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Registration
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    # Search preferences
    pref_gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)
    pref_age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pref_age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pref_country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Daily gender search tracking (non-VIP limit)
    gender_searches_today: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    gender_searches_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    interests: Mapped[list["UserInterest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_is_registered", "is_registered"),
    )


class UserInterest(Base):
    __tablename__ = "user_interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    interest: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped["User"] = relationship(back_populates="interests")

    __table_args__ = (
        Index("ix_user_interests_user_id", "user_id"),
    )


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user2_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    status: Mapped[ChatStatus] = mapped_column(
        Enum(ChatStatus), default=ChatStatus.ACTIVE, nullable=False
    )
    room_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=True)
    messages_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_chats_active", "status", "user1_id"),
        Index("ix_chats_active2", "status", "user2_id"),
    )


class SearchQueue(Base):
    __tablename__ = "search_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)
    age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pref_gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)
    pref_age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pref_age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pref_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    room_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_search_queue_matching", "gender", "country"),
    )


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    from_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    to_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[RatingValue] = mapped_column(Enum(RatingValue), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_ratings_to_user", "to_telegram_id"),
        Index("ix_ratings_unique", "chat_id", "from_telegram_id", unique=True),
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    referred_telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class InterestOption(Base):
    __tablename__ = "interest_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False, server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class VipPlan(Base):
    __tablename__ = "vip_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    price_ton: Mapped[float | None] = mapped_column(Float, nullable=True)
    discount_text: Mapped[str | None] = mapped_column(String(50), nullable=True)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False, server_default="⭐")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class MessageLog(Base):
    __tablename__ = "message_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    sender_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    receiver_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), nullable=False)  # text, photo, video, sticker, voice, video_note, document
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_msglog_chat", "chat_id"),
        Index("ix_msglog_sender", "sender_telegram_id"),
        Index("ix_msglog_created", "created_at"),
    )


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False, server_default="")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
