from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo, VipPlanRepo, RoomRepo
from bot.db.models import GenderEnum, User
from bot.i18n import T
from bot.keyboards.inline import (
    main_menu_keyboard,
    profile_keyboard,
    gender_keyboard,
    age_keyboard,
    country_keyboard,
    interests_keyboard,
    pref_gender_keyboard,
    pref_age_keyboard,
    pref_country_keyboard,
    vip_plans_keyboard,
    rooms_keyboard,
)
from bot.services.chat import ChatService
from bot.states.registration import RegistrationStates, SearchSettingsStates

router = Router()

GENDER_SEARCH_DAILY_LIMIT = 5
TON_WALLET = "UQC3jIhtlOtu6PIKf-oiuuqVVTK0hVypjxhrJ8RmdI86Qb-D"


def _format_profile(user: User, interests: list[str]) -> str:
    gender_text = T["gender_male_short"] if user.gender and user.gender.value == "male" else T["gender_female_short"]
    age_text = f"{user.age_min}-{user.age_max}" if user.age_min is not None else "—"
    interests_text = ", ".join(interests) if interests else T["interests_none"]
    vip_line = ""
    if user.is_vip and user.vip_until:
        vip_line = T["vip_active_line"].format(until=user.vip_until.strftime("%d.%m.%Y %H:%M"))
    else:
        vip_line = T["vip_inactive_line"]

    return T["profile_text"].format(
        tid=user.telegram_id,
        gender=gender_text,
        age_min=user.age_min or "—",
        age_max=user.age_max or "—",
        country=user.country or "—",
        interests=interests_text,
        chats=user.chats_count,
        messages=user.messages_count,
        likes=user.karma_likes,
        dislikes=user.karma_dislikes,
        vip_line=vip_line,
    )


async def _gender_search(message: Message, session: AsyncSession, bot: Bot, gender: GenderEnum):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    if not user.is_vip:
        can_search, remaining = await user_repo.check_gender_search_limit(
            message.from_user.id, GENDER_SEARCH_DAILY_LIMIT
        )
        if not can_search:
            await message.answer(
                T["gender_search_limit"].format(limit=GENDER_SEARCH_DAILY_LIMIT),
                reply_markup=main_menu_keyboard(),
            )
            return
        await user_repo.increment_gender_search(message.from_user.id)
        remaining -= 1

    await user_repo.update_preferences(telegram_id=message.from_user.id, pref_gender=gender)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user)

    limit_text = ""
    if not user.is_vip:
        _, remaining = await user_repo.check_gender_search_limit(
            message.from_user.id, GENDER_SEARCH_DAILY_LIMIT
        )
        limit_text = "\n" + T["gender_search_left"].format(remaining=remaining)

    await message.answer(f"{result}{limit_text}", reply_markup=main_menu_keyboard())


# ─── Reply keyboard button handlers ───

@router.message(F.text == T["btn_find_girl"])
async def btn_find_female(message: Message, session: AsyncSession, bot: Bot):
    await _gender_search(message, session, bot, GenderEnum.FEMALE)


@router.message(F.text == T["btn_find_boy"])
async def btn_find_male(message: Message, session: AsyncSession, bot: Bot):
    await _gender_search(message, session, bot, GenderEnum.MALE)


@router.message(F.text == T["btn_random"])
async def btn_random(message: Message, session: AsyncSession, bot: Bot):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return
    await user_repo.update_preferences(telegram_id=message.from_user.id, pref_gender=None)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user)
    await message.answer(result, reply_markup=main_menu_keyboard())


# ─── VIP ───

@router.message(F.text == T["btn_vip"])
async def btn_vip(message: Message, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    plan_repo = VipPlanRepo(session)
    plans = await plan_repo.get_all_active()
    plan_data = [
        (p.id, p.name, p.price_stars, p.duration_days, p.discount_text, p.emoji)
        for p in plans
    ]

    await message.answer(T["vip_title"], reply_markup=vip_plans_keyboard(plan_data, TON_WALLET))


@router.callback_query(F.data.startswith("vip_buy:"))
async def vip_buy(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    plan_id = int(callback.data.split(":")[1])
    plan_repo = VipPlanRepo(session)
    plan = await plan_repo.get_by_id(plan_id)
    if not plan:
        await callback.answer("❌", show_alert=True)
        return

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"VIP — {plan.name}",
        description=f"👑 VIP {plan.name}",
        payload=f"vip_plan:{plan.id}:{plan.duration_days}",
        currency="XTR",
        prices=[LabeledPrice(label=f"VIP {plan.name}", amount=plan.price_stars)],
    )
    await callback.answer()


@router.callback_query(F.data == "vip_free")
async def vip_free(callback: CallbackQuery, bot_username: str):
    ref_link = f"https://t.me/{bot_username}?start={callback.from_user.id}"
    await callback.message.answer(
        T["vip_free_title"].format(ref_link=ref_link, wallet=TON_WALLET)
    )
    await callback.answer()


# ─── Rooms ───

@router.message(F.text == T["btn_rooms"])
async def btn_rooms(message: Message, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    room_repo = RoomRepo(session)
    rooms = await room_repo.get_all_active()
    if not rooms:
        await message.answer(T["no_rooms"], reply_markup=main_menu_keyboard())
        return

    room_data = [(r.id, r.name, r.emoji, r.description) for r in rooms]
    await message.answer(T["rooms_title"], reply_markup=rooms_keyboard(room_data))


@router.callback_query(F.data.startswith("room:"))
async def room_select(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    room_id = int(callback.data.split(":")[1])
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user or not user.is_registered:
        await callback.answer(T["register_first"], show_alert=True)
        return

    room_repo = RoomRepo(session)
    room = await room_repo.get_by_id(room_id)
    if not room:
        await callback.answer("❌", show_alert=True)
        return

    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user, room_id=room_id)
    await callback.message.answer(
        f"{room.emoji} {room.name}\n\n{result}",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


# ─── Profile ───

@router.message(F.text == T["btn_profile"])
async def btn_profile(message: Message, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    interests = [i.interest for i in user.interests] if user.interests else []
    text = _format_profile(user, interests)
    await message.answer(text, reply_markup=profile_keyboard())


# ─── Profile edit callbacks ───

@router.callback_query(F.data == "edit:gender")
async def edit_gender(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(T["search_choose_gender"], reply_markup=gender_keyboard())
    await state.set_state(RegistrationStates.waiting_gender)
    await state.update_data(edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "edit:age")
async def edit_age(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(T["choose_age"], reply_markup=age_keyboard())
    await state.set_state(RegistrationStates.waiting_age)
    await state.update_data(edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "edit:country")
async def edit_country(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(T["choose_country"], reply_markup=country_keyboard())
    await state.set_state(RegistrationStates.waiting_country)
    await state.update_data(edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "edit:interests")
async def edit_interests(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    current = [i.interest for i in user.interests] if user and user.interests else []

    selected = ", ".join(current) if current else T["nothing_selected"]
    await callback.message.edit_text(
        T["choose_interests"] + "\n\n" + T["choose_interests_selected"].format(selected=selected),
        reply_markup=interests_keyboard(selected=current),
    )
    await state.update_data(interests=current, edit_mode=True)
    await state.set_state(RegistrationStates.waiting_interests)
    await callback.answer()


@router.callback_query(F.data == "edit:search")
async def edit_search(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("❌", show_alert=True)
        return

    if not user.is_vip:
        await callback.answer(T["search_vip_only"], show_alert=True)
        return

    await callback.message.edit_text(
        T["search_settings_title"] + "\n\n" + T["search_choose_gender"],
        reply_markup=pref_gender_keyboard(),
    )
    await state.set_state(SearchSettingsStates.waiting_pref_gender)
    await callback.answer()
