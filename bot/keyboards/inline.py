from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


# ─── Main reply keyboard (under input field) ───

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Найти 👩"),
                KeyboardButton(text="🎪 Рандом"),
                KeyboardButton(text="Найти 🧑"),
            ],
            [
                KeyboardButton(text="VIP статус 🔥"),
                KeyboardButton(text="🏠 Комнаты"),
                KeyboardButton(text="👤 Профиль"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


# ─── Inline keyboards ───

def gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨 Мужской", callback_data="gender:male"),
            InlineKeyboardButton(text="👩 Женский", callback_data="gender:female"),
        ]
    ])


def age_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="до 18", callback_data="age:0:17"),
            InlineKeyboardButton(text="18-21", callback_data="age:18:21"),
        ],
        [
            InlineKeyboardButton(text="22-25", callback_data="age:22:25"),
            InlineKeyboardButton(text="26-30", callback_data="age:26:30"),
        ],
        [
            InlineKeyboardButton(text="31-40", callback_data="age:31:40"),
            InlineKeyboardButton(text="40+", callback_data="age:40:99"),
        ],
    ])


def country_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Россия", callback_data="country:Россия"),
            InlineKeyboardButton(text="🇺🇦 Украина", callback_data="country:Украина"),
        ],
        [
            InlineKeyboardButton(text="🇧🇾 Беларусь", callback_data="country:Беларусь"),
            InlineKeyboardButton(text="🇰🇿 Казахстан", callback_data="country:Казахстан"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 Узбекистан", callback_data="country:Узбекистан"),
            InlineKeyboardButton(text="🌍 Другая", callback_data="country:Другая"),
        ],
    ])


def interests_keyboard(
    options: list[tuple[str, str]],
    selected: list[str] | None = None,
) -> InlineKeyboardMarkup:
    """Build interests keyboard dynamically from DB options.
    options: list of (name, emoji) tuples
    selected: list of currently selected interest names
    """
    if selected is None:
        selected = []
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for name, emoji in options:
        check = "✅ " if name in selected else ""
        btn = InlineKeyboardButton(
            text=f"{check}{emoji} {name}",
            callback_data=f"interest:{name}",
        )
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="✅ Готово", callback_data="interest:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="� Изменить пол", callback_data="edit:gender"),
            InlineKeyboardButton(text="🔞 Изменить возраст", callback_data="edit:age"),
        ],
        [
            InlineKeyboardButton(text="🌎 Изменить страну", callback_data="edit:country"),
            InlineKeyboardButton(text="🎯 Изменить интересы", callback_data="edit:interests"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки поиска", callback_data="edit:search"),
        ],
    ])


def rating_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Лайк", callback_data=f"rate:{chat_id}:like"),
            InlineKeyboardButton(text="👎 Дизлайк", callback_data=f"rate:{chat_id}:dislike"),
        ],
        [
            InlineKeyboardButton(text="⏭ Пропустить", callback_data=f"rate:{chat_id}:skip"),
        ],
    ])


def top_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁️ По карме", callback_data="top:karma")],
        [InlineKeyboardButton(text="🎪 По рефералам", callback_data="top:referrals")],
        [InlineKeyboardButton(text="📧 По активности", callback_data="top:activity")],
    ])


def pref_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨 Мужской", callback_data="pref_gender:male"),
            InlineKeyboardButton(text="👩 Женский", callback_data="pref_gender:female"),
        ],
        [
            InlineKeyboardButton(text="🔀 Любой", callback_data="pref_gender:any"),
        ],
    ])


def pref_age_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="до 18", callback_data="pref_age:0:17"),
            InlineKeyboardButton(text="18-21", callback_data="pref_age:18:21"),
        ],
        [
            InlineKeyboardButton(text="22-25", callback_data="pref_age:22:25"),
            InlineKeyboardButton(text="26-30", callback_data="pref_age:26:30"),
        ],
        [
            InlineKeyboardButton(text="31-40", callback_data="pref_age:31:40"),
            InlineKeyboardButton(text="40+", callback_data="pref_age:40:99"),
        ],
        [
            InlineKeyboardButton(text="🔀 Любой", callback_data="pref_age:any"),
        ],
    ])


def pref_country_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Россия", callback_data="pref_country:Россия"),
            InlineKeyboardButton(text="🇺🇦 Украина", callback_data="pref_country:Украина"),
        ],
        [
            InlineKeyboardButton(text="🇧🇾 Беларусь", callback_data="pref_country:Беларусь"),
            InlineKeyboardButton(text="🇰🇿 Казахстан", callback_data="pref_country:Казахстан"),
        ],
        [
            InlineKeyboardButton(text="🔀 Любая", callback_data="pref_country:any"),
        ],
    ])


def vip_plans_keyboard(
    plans: list[tuple[int, str, int, int, str | None, str]],
    ton_wallet: str | None = None,
) -> InlineKeyboardMarkup:
    """plans: list of (id, name, price_stars, duration_days, discount_text, emoji)"""
    rows: list[list[InlineKeyboardButton]] = []
    for plan_id, name, price_stars, duration_days, discount, emoji in plans:
        discount_str = f" {discount}" if discount else ""
        text = f"{price_stars} ⭐ / {name}{discount_str} {emoji}"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"vip_buy:{plan_id}")])
    rows.append([InlineKeyboardButton(
        text="🎁 Получить VIP статус бесплатно",
        callback_data="vip_free",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def rooms_keyboard(
    rooms: list[tuple[int, str, str, str | None]],
) -> InlineKeyboardMarkup:
    """rooms: list of (id, name, emoji, description)"""
    rows: list[list[InlineKeyboardButton]] = []
    for room_id, name, emoji, desc in rooms:
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"room:{room_id}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)
