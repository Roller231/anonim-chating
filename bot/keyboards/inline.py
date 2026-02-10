from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.i18n import T


# ─── Main reply keyboard (under input field) ───

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=T["btn_find_girl"]),
                KeyboardButton(text=T["btn_random"]),
                KeyboardButton(text=T["btn_find_boy"]),
            ],
            [
                KeyboardButton(text=T["btn_vip"]),
                KeyboardButton(text=T["btn_rooms"]),
                KeyboardButton(text=T["btn_profile"]),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


# ─── Inline keyboards ───

def gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["gender_male"], callback_data="gender:male"),
            InlineKeyboardButton(text=T["gender_female"], callback_data="gender:female"),
        ]
    ])


def age_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["age_under_18"], callback_data="age:0:17"),
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
    countries = T["countries"]
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for label, value in countries:
        row.append(InlineKeyboardButton(text=label, callback_data=f"country:{value}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def interests_keyboard(
    options: list[tuple[str, str]] | None = None,
    selected: list[str] | None = None,
) -> InlineKeyboardMarkup:
    if options is None:
        options = T["interests"]
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
    rows.append([InlineKeyboardButton(text=T["interests_done"], callback_data="interest:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["edit_gender"], callback_data="edit:gender"),
            InlineKeyboardButton(text=T["edit_age"], callback_data="edit:age"),
        ],
        [
            InlineKeyboardButton(text=T["edit_country"], callback_data="edit:country"),
            InlineKeyboardButton(text=T["edit_interests"], callback_data="edit:interests"),
        ],
        [
            InlineKeyboardButton(text=T["edit_search"], callback_data="edit:search"),
        ],
    ])


def rating_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["rate_like"], callback_data=f"rate:{chat_id}:like"),
            InlineKeyboardButton(text=T["rate_dislike"], callback_data=f"rate:{chat_id}:dislike"),
        ],
        [
            InlineKeyboardButton(text=T["rate_skip"], callback_data=f"rate:{chat_id}:skip"),
        ],
    ])


def top_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["top_karma"], callback_data="top:karma")],
        [InlineKeyboardButton(text=T["top_referrals"], callback_data="top:referrals")],
        [InlineKeyboardButton(text=T["top_activity"], callback_data="top:activity")],
    ])


def pref_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["gender_male"], callback_data="pref_gender:male"),
            InlineKeyboardButton(text=T["gender_female"], callback_data="pref_gender:female"),
        ],
        [
            InlineKeyboardButton(text=T["gender_any"], callback_data="pref_gender:any"),
        ],
    ])


def pref_age_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["age_under_18"], callback_data="pref_age:0:17"),
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
            InlineKeyboardButton(text=T["age_any"], callback_data="pref_age:any"),
        ],
    ])


def pref_country_keyboard() -> InlineKeyboardMarkup:
    countries = T["countries"]
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for label, value in countries:
        row.append(InlineKeyboardButton(text=label, callback_data=f"pref_country:{value}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=T["country_any"], callback_data="pref_country:any")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def vip_plans_keyboard(
    plans: list[tuple[int, str, int, int, str | None, str]],
    ton_wallet: str | None = None,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for plan_id, name, price_stars, duration_days, discount, emoji in plans:
        discount_str = f" {discount}" if discount else ""
        text = f"{price_stars} ⭐ / {name}{discount_str} {emoji}"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"vip_buy:{plan_id}")])
    rows.append([InlineKeyboardButton(
        text=T["vip_free_btn"],
        callback_data="vip_free",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def rooms_keyboard(
    rooms: list[tuple[int, str, str, str | None]],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for room_id, name, emoji, desc in rooms:
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"room:{room_id}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)
