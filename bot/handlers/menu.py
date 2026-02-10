from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo, InterestRepo, VipPlanRepo, RoomRepo
from bot.db.models import GenderEnum, User
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

COUNTRIES = {
    "Россия": "🇷🇺",
    "Украина": "🇺🇦",
    "Беларусь": "🇧🇾",
    "Казахстан": "🇰🇿",
    "Узбекистан": "🇺🇿",
    "Другая": "🌍",
}


def _format_profile(user: User, interests: list[str]) -> str:
    gender_text = "Мужской" if user.gender and user.gender.value == "male" else "Женский"
    country_flag = COUNTRIES.get(user.country or "", "🌍")
    karma = user.karma_likes - user.karma_dislikes
    vip_text = "👑 Да" if user.is_vip else "Нет"
    vip_until = ""
    if user.is_vip and user.vip_until:
        vip_until = f" (до {user.vip_until.strftime('%d.%m.%Y')})"

    age_text = "Не указан"
    if user.age_min is not None and user.age_max is not None:
        age_text = f"от {user.age_min} до {user.age_max}"

    interests_text = ", ".join(interests) if interests else "Не указаны"

    return (
        f"📋 Ваш профиль\n\n"
        f"#️⃣ ID — {user.telegram_id}\n\n"
        f"👫 Пол — {gender_text}\n"
        f"🔞 Возраст — {age_text}\n"
        f"🌎 Страна — {country_flag} {user.country or 'Не указана'}\n\n"
        f"🎯 Интересы — {interests_text}\n\n"
        f"🎪 Приглашено пользователей — {user.referral_count}\n"
        f"📧 Сообщений — {user.messages_count}\n"
        f"💬 Чатов — {user.chats_count}\n"
        f"👁️ Карма — 👍 {user.karma_likes} 👎 {user.karma_dislikes} (= {karma})\n"
        f"👑 VIP статус — {vip_text}{vip_until}"
    )


async def _get_interest_options(session: AsyncSession) -> list[tuple[str, str]]:
    repo = InterestRepo(session)
    options = await repo.get_all_active()
    return [(o.name, o.emoji) for o in options]


async def _gender_search(message: Message, session: AsyncSession, bot: Bot, gender: GenderEnum):
    """Shared logic for gender-based search with daily limit check."""
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    # VIP — unlimited. Non-VIP — 5/day
    if not user.is_vip:
        can_search, remaining = await user_repo.check_gender_search_limit(
            message.from_user.id, GENDER_SEARCH_DAILY_LIMIT
        )
        if not can_search:
            await message.answer(
                f"� Лимит поиска по полу исчерпан на сегодня ({GENDER_SEARCH_DAILY_LIMIT}/{GENDER_SEARCH_DAILY_LIMIT}).\n\n"
                f"👑 Купите VIP для безлимитного поиска!\n"
                f"Или используйте 🎪 Рандом — он без ограничений.",
                reply_markup=main_menu_keyboard(),
            )
            return
        await user_repo.increment_gender_search(message.from_user.id)
        remaining -= 1

    await user_repo.update_preferences(telegram_id=message.from_user.id, pref_gender=gender)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user)

    gender_icon = "👩" if gender == GenderEnum.FEMALE else "🧑"
    limit_text = ""
    if not user.is_vip:
        _, remaining = await user_repo.check_gender_search_limit(
            message.from_user.id, GENDER_SEARCH_DAILY_LIMIT
        )
        limit_text = f"\n🔍 Осталось поисков по полу: {remaining}/{GENDER_SEARCH_DAILY_LIMIT}"

    await message.answer(
        f"{gender_icon} Ищем...\n\n{result}{limit_text}",
        reply_markup=main_menu_keyboard(),
    )


# ─── Reply keyboard button handlers ───

@router.message(F.text == "Найти 👩")
async def btn_find_female(message: Message, session: AsyncSession, bot: Bot):
    await _gender_search(message, session, bot, GenderEnum.FEMALE)


@router.message(F.text == "Найти 🧑")
async def btn_find_male(message: Message, session: AsyncSession, bot: Bot):
    await _gender_search(message, session, bot, GenderEnum.MALE)


@router.message(F.text == "🎪 Рандом")
async def btn_random(message: Message, session: AsyncSession, bot: Bot):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return
    await user_repo.update_preferences(telegram_id=message.from_user.id, pref_gender=None)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user)
    await message.answer(result, reply_markup=main_menu_keyboard())


# ─── VIP ───

@router.message(F.text == "VIP статус 🔥")
async def btn_vip(message: Message, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    vip_status = "✅ Активен" if user.is_vip else "❌ Не активен"
    vip_until = ""
    if user.is_vip and user.vip_until:
        vip_until = f"\n⏳ Действует до: {user.vip_until.strftime('%d.%m.%Y %H:%M')} UTC"

    # Load plans from DB
    plan_repo = VipPlanRepo(session)
    plans = await plan_repo.get_all_active()
    plan_data = [
        (p.id, p.name, p.price_stars, p.duration_days, p.discount_text, p.emoji)
        for p in plans
    ]

    await message.answer(
        f"Преимущества VIP-подписки �\n\n"
        f"🧷 Никакой рекламы\n"
        f"🧷 Первое место в поиске 🔥\n"
        f"🧷 Отсутствие ограничений на отправку фото/видео/стикеров и ссылок\n"
        f"🧷 Подробная информация о собеседнике (возраст, страна, расстояние 🚩)\n"
        f"🧷 Поиск по полу без ограничений 👫\n"
        f"🧷 Поиск по возрасту и стране (/search)\n"
        f"🧷 Другие участники чата увидят твой статус 👑 вначале диалога\n"
        f"🧷 Да блин, это просто круто, выделяешься из серой массы\n\n"
        f"🏩 Поддержка чата — самое главное, ведь мы молоды и постоянно развиваемся 🏩\n\n"
        f"✅ Автоснятий нет!\n\n"
        f"👑 VIP статус — {vip_status}{vip_until}",
        reply_markup=vip_plans_keyboard(plan_data, TON_WALLET),
    )


@router.callback_query(F.data.startswith("vip_buy:"))
async def vip_buy(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    plan_id = int(callback.data.split(":")[1])
    plan_repo = VipPlanRepo(session)
    plan = await plan_repo.get_by_id(plan_id)
    if not plan:
        await callback.answer("Тариф не найден.", show_alert=True)
        return

    # Send Telegram Stars invoice
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"VIP подписка — {plan.name}",
        description=(
            f"👑 VIP статус на {plan.name}\n"
            f"Безлимитный поиск по полу, подробная информация о собеседнике, "
            f"приоритет в очереди и многое другое!"
        ),
        payload=f"vip_plan:{plan.id}:{plan.duration_days}",
        currency="XTR",
        prices=[LabeledPrice(label=f"VIP {plan.name}", amount=plan.price_stars)],
    )
    await callback.answer()


@router.callback_query(F.data == "vip_free")
async def vip_free(callback: CallbackQuery, bot_username: str):
    ref_link = f"https://t.me/{bot_username}?start={callback.from_user.id}"
    await callback.message.answer(
        f"🎁 Получить VIP статус бесплатно\n\n"
        f"Приглашайте друзей и получайте баллы!\n"
        f"Обменять 10 баллов на 1 день VIP 👑 — /exchange\n\n"
        f"Ваша реферальная ссылка:\n👉 {ref_link}\n\n"
        f"Также вы можете оплатить VIP через TON:\n"
        f"💎 Кошелек: <code>{TON_WALLET}</code>\n"
        f"После перевода напишите в поддержку для активации."
    )
    await callback.answer()


# ─── Rooms ───

@router.message(F.text == "🏠 Комнаты")
async def btn_rooms(message: Message, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    room_repo = RoomRepo(session)
    rooms = await room_repo.get_all_active()
    if not rooms:
        await message.answer(
            "🏠 Комнаты\n\n🚧 Пока нет доступных комнат.",
            reply_markup=main_menu_keyboard(),
        )
        return

    room_data = [(r.id, r.name, r.emoji, r.description) for r in rooms]
    text = "🏠 Тематические комнаты\n\nВыберите комнату для поиска собеседника:\n\n"
    for r in rooms:
        desc = f" — {r.description}" if r.description else ""
        text += f"{r.emoji} {r.name}{desc}\n"

    await message.answer(text, reply_markup=rooms_keyboard(room_data))


@router.callback_query(F.data.startswith("room:"))
async def room_select(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    room_id = int(callback.data.split(":")[1])
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user or not user.is_registered:
        await callback.answer("❌ Сначала зарегистрируйтесь", show_alert=True)
        return

    room_repo = RoomRepo(session)
    room = await room_repo.get_by_id(room_id)
    if not room:
        await callback.answer("Комната не найдена.", show_alert=True)
        return

    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user, room_id=room_id)
    await callback.message.answer(
        f"{room.emoji} Комната «{room.name}»\n\n{result}",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


# ─── Profile ───

@router.message(F.text == "👤 Профиль")
async def btn_profile(message: Message, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    interests = [i.interest for i in user.interests] if user.interests else []
    text = _format_profile(user, interests)
    await message.answer(text, reply_markup=profile_keyboard())


# ─── Profile edit callbacks ───

@router.callback_query(F.data == "edit:gender")
async def edit_gender(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "👫 Выберите новый пол:",
        reply_markup=gender_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_gender)
    await state.update_data(edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "edit:age")
async def edit_age(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔞 Выберите новый возраст:",
        reply_markup=age_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_age)
    await state.update_data(edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "edit:country")
async def edit_country(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌎 Выберите новую страну:",
        reply_markup=country_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_country)
    await state.update_data(edit_mode=True)
    await callback.answer()


@router.callback_query(F.data == "edit:interests")
async def edit_interests(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    current = [i.interest for i in user.interests] if user and user.interests else []

    options = await _get_interest_options(session)
    await callback.message.edit_text(
        "🎯 Выберите ваши интересы (можно несколько), затем нажмите ✅ Готово:\n\n"
        f"Выбрано: {', '.join(current) if current else 'ничего не выбрано'}",
        reply_markup=interests_keyboard(options, current),
    )
    await state.update_data(interests=current, edit_mode=True)
    await state.set_state(RegistrationStates.waiting_interests)
    await callback.answer()


@router.callback_query(F.data == "edit:search")
async def edit_search(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка", show_alert=True)
        return

    # Only VIP can use /search age/country filters
    if not user.is_vip:
        await callback.answer(
            "🔒 Настройки поиска по возрасту и стране доступны только VIP пользователям!",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "⚙️ Настройки поиска\n\n"
        "👫 Выберите предпочитаемый пол собеседника:",
        reply_markup=pref_gender_keyboard(),
    )
    await state.set_state(SearchSettingsStates.waiting_pref_gender)
    await callback.answer()
