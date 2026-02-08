from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo, ReferralRepo, InterestRepo
from bot.db.models import GenderEnum
from bot.keyboards.inline import (
    gender_keyboard,
    age_keyboard,
    country_keyboard,
    interests_keyboard,
    main_menu_keyboard,
)
from bot.states.registration import RegistrationStates
from bot.services.chat import ChatService

router = Router()


async def _get_interest_options(session: AsyncSession) -> list[tuple[str, str]]:
    repo = InterestRepo(session)
    options = await repo.get_all_active()
    return [(o.name, o.emoji) for o in options]


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    # Handle referral link: /start <referrer_id>
    if command.args and command.args.isdigit():
        referrer_id = int(command.args)
        if referrer_id != message.from_user.id:
            ref_repo = ReferralRepo(session)
            existing = await ref_repo.get_by_referred(message.from_user.id)
            if not existing:
                try:
                    await ref_repo.create(referrer_id, message.from_user.id)
                    await user_repo.increment_referral(referrer_id)
                    user.referred_by = referrer_id
                    await session.commit()
                except Exception:
                    pass

    if not user.is_registered:
        await state.clear()
        await message.answer(
            "👋 Добро пожаловать в Анонимный чат!\n\n"
            "Давайте заполним вашу анкету.\n\n"
            "👫 Выберите ваш пол:",
            reply_markup=gender_keyboard(),
        )
        await state.set_state(RegistrationStates.waiting_gender)
        return

    # User already registered — start search
    chat_service = ChatService(bot, session)
    result = await chat_service.start_search(user)
    await message.answer(result, reply_markup=main_menu_keyboard())


# --- Registration flow ---

@router.callback_query(RegistrationStates.waiting_gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    gender_val = callback.data.split(":")[1]
    data = await state.get_data()

    if data.get("edit_mode"):
        user_repo = UserRepo(session)
        gender = GenderEnum.MALE if gender_val == "male" else GenderEnum.FEMALE
        await user_repo.update_profile(telegram_id=callback.from_user.id, gender=gender)
        await state.clear()
        g = "Мужской" if gender_val == "male" else "Женский"
        await callback.message.edit_text(f"✅ Пол изменён на: {g}")
        await callback.answer("✅ Сохранено!")
        return

    await state.update_data(gender=gender_val)
    await callback.message.edit_text(
        "🔞 Выберите ваш возраст:",
        reply_markup=age_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_age)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_age, F.data.startswith("age:"))
async def process_age(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    parts = callback.data.split(":")
    age_min, age_max = int(parts[1]), int(parts[2])
    data = await state.get_data()

    if data.get("edit_mode"):
        user_repo = UserRepo(session)
        await user_repo.update_profile(
            telegram_id=callback.from_user.id, age_min=age_min, age_max=age_max
        )
        await state.clear()
        await callback.message.edit_text(f"✅ Возраст изменён на: {age_min}-{age_max}")
        await callback.answer("✅ Сохранено!")
        return

    await state.update_data(age_min=age_min, age_max=age_max)
    await callback.message.edit_text(
        "🌎 Выберите вашу страну:",
        reply_markup=country_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_country)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_country, F.data.startswith("country:"))
async def process_country(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    country = callback.data.split(":")[1]
    data = await state.get_data()

    if data.get("edit_mode"):
        user_repo = UserRepo(session)
        await user_repo.update_profile(telegram_id=callback.from_user.id, country=country)
        await state.clear()
        await callback.message.edit_text(f"✅ Страна изменена на: {country}")
        await callback.answer("✅ Сохранено!")
        return

    await state.update_data(country=country)
    options = await _get_interest_options(session)
    await callback.message.edit_text(
        "🎯 Выберите ваши интересы (можно несколько), затем нажмите ✅ Готово:",
        reply_markup=interests_keyboard(options),
    )
    await state.update_data(interests=[])
    await state.set_state(RegistrationStates.waiting_interests)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_interests, F.data.startswith("interest:"))
async def process_interest(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    value = callback.data.split(":")[1]

    if value == "done":
        data = await state.get_data()
        user_repo = UserRepo(session)
        interests = data.get("interests", [])

        if data.get("edit_mode"):
            user = await user_repo.get_by_telegram_id(callback.from_user.id)
            if user:
                await user_repo.set_interests(user.id, interests)
            await state.clear()
            await callback.message.edit_text(
                f"✅ Интересы обновлены!\n\n"
                f"🎯 {', '.join(interests) if interests else 'Не указаны'}"
            )
            await callback.answer("✅ Сохранено!")
            return

        gender = GenderEnum.MALE if data["gender"] == "male" else GenderEnum.FEMALE

        await user_repo.update_profile(
            telegram_id=callback.from_user.id,
            gender=gender,
            age_min=data["age_min"],
            age_max=data["age_max"],
            country=data["country"],
            is_registered=True,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
        )

        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if interests and user:
            await user_repo.set_interests(user.id, interests)

        await state.clear()
        await callback.message.edit_text(
            "✅ Регистрация завершена!\n\n"
            f"#️⃣ ID — {callback.from_user.id}\n"
            f"👫 Пол — {'Мужской' if data['gender'] == 'male' else 'Женский'}\n"
            f"🔞 Возраст — от {data['age_min']} до {data['age_max']}\n"
            f"🌎 Страна — {data['country']}\n"
            f"🎯 Интересы — {', '.join(interests) if interests else 'Не указаны'}\n\n"
            "Используйте кнопки меню для навигации 👇"
        )
        await callback.message.answer(
            "🔍 Нажмите кнопку ниже чтобы начать поиск!",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer("✅ Регистрация завершена!")
        return

    data = await state.get_data()
    interests = data.get("interests", [])
    if value in interests:
        interests.remove(value)
        await callback.answer(f"❌ {value} убран")
    else:
        interests.append(value)
        await callback.answer(f"✅ {value} добавлен")
    await state.update_data(interests=interests)

    options = await _get_interest_options(session)
    selected = ", ".join(interests) if interests else "ничего не выбрано"
    await callback.message.edit_text(
        f"🎯 Выберите ваши интересы (можно несколько), затем нажмите ✅ Готово:\n\n"
        f"Выбрано: {selected}",
        reply_markup=interests_keyboard(options, interests),
    )
