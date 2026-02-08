from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo
from bot.db.models import GenderEnum
from bot.keyboards.inline import pref_gender_keyboard, pref_age_keyboard, pref_country_keyboard
from bot.states.registration import SearchSettingsStates

router = Router()


@router.message(Command("search"))
async def cmd_search(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer("❌ Сначала зарегистрируйтесь: /start")
        return

    if not user.is_vip:
        await message.answer(
            "🔒 Команда /search доступна только VIP пользователям!\n\n"
            "👑 Купите VIP подписку, чтобы настраивать поиск по возрасту и стране.\n"
            "Нажмите «VIP статус 🔥» для покупки."
        )
        return

    current_prefs = []
    if user.pref_gender:
        g = "👨 Мужской" if user.pref_gender.value == "male" else "👩 Женский"
        current_prefs.append(f"👫 Пол: {g}")
    else:
        current_prefs.append("👫 Пол: 🔀 Любой")

    if user.pref_age_min and user.pref_age_max:
        current_prefs.append(f"🔞 Возраст: {user.pref_age_min}-{user.pref_age_max}")
    else:
        current_prefs.append("🔞 Возраст: 🔀 Любой")

    if user.pref_country:
        current_prefs.append(f"🌎 Страна: {user.pref_country}")
    else:
        current_prefs.append("🌎 Страна: 🔀 Любая")

    prefs_text = "\n".join(current_prefs)

    await message.answer(
        f"⚙️ Настройки поиска\n\n"
        f"Текущие предпочтения:\n{prefs_text}\n\n"
        f"👫 Выберите предпочитаемый пол собеседника:",
        reply_markup=pref_gender_keyboard(),
    )
    await state.set_state(SearchSettingsStates.waiting_pref_gender)


@router.callback_query(SearchSettingsStates.waiting_pref_gender, F.data.startswith("pref_gender:"))
async def process_pref_gender(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    value = callback.data.split(":")[1]
    if value == "any":
        await state.update_data(pref_gender=None)
    else:
        await state.update_data(pref_gender=value)

    await callback.message.edit_text(
        "🔞 Выберите предпочитаемый возраст собеседника:",
        reply_markup=pref_age_keyboard(),
    )
    await state.set_state(SearchSettingsStates.waiting_pref_age)
    await callback.answer()


@router.callback_query(SearchSettingsStates.waiting_pref_age, F.data.startswith("pref_age:"))
async def process_pref_age(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    value = callback.data.split(":")
    if value[1] == "any":
        await state.update_data(pref_age_min=None, pref_age_max=None)
    else:
        await state.update_data(pref_age_min=int(value[1]), pref_age_max=int(value[2]))

    await callback.message.edit_text(
        "🌎 Выберите предпочитаемую страну собеседника:",
        reply_markup=pref_country_keyboard(),
    )
    await state.set_state(SearchSettingsStates.waiting_pref_country)
    await callback.answer()


@router.callback_query(SearchSettingsStates.waiting_pref_country, F.data.startswith("pref_country:"))
async def process_pref_country(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    value = callback.data.split(":")[1]
    data = await state.get_data()

    user_repo = UserRepo(session)

    pref_gender = data.get("pref_gender")
    if pref_gender:
        pref_gender = GenderEnum.MALE if pref_gender == "male" else GenderEnum.FEMALE

    await user_repo.update_preferences(
        telegram_id=callback.from_user.id,
        pref_gender=pref_gender,
        pref_age_min=data.get("pref_age_min"),
        pref_age_max=data.get("pref_age_max"),
        pref_country=value if value != "any" else None,
    )

    await state.clear()

    summary = []
    if data.get("pref_gender"):
        g = "👨 Мужской" if data["pref_gender"] == "male" else "👩 Женский"
        summary.append(f"👫 Пол: {g}")
    else:
        summary.append("👫 Пол: 🔀 Любой")

    if data.get("pref_age_min"):
        summary.append(f"🔞 Возраст: {data['pref_age_min']}-{data['pref_age_max']}")
    else:
        summary.append("🔞 Возраст: 🔀 Любой")

    if value != "any":
        summary.append(f"🌎 Страна: {value}")
    else:
        summary.append("🌎 Страна: 🔀 Любая")

    await callback.message.edit_text(
        f"✅ Настройки поиска сохранены!\n\n"
        + "\n".join(summary)
        + "\n\nНажмите /start чтобы начать поиск 🔍"
    )
    await callback.answer("✅ Сохранено!")
