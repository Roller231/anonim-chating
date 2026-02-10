from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import UserRepo
from bot.db.models import GenderEnum
from bot.i18n import T
from bot.keyboards.inline import pref_gender_keyboard, pref_age_keyboard, pref_country_keyboard
from bot.states.registration import SearchSettingsStates

router = Router()


def _pref_summary(data: dict, country_val: str) -> str:
    lines = []
    if data.get("pref_gender"):
        g = T["gender_male"] if data["pref_gender"] == "male" else T["gender_female"]
        lines.append(f"{T['pref_gender_label']}: {g}")
    else:
        lines.append(f"{T['pref_gender_label']}: {T['any_label']}")
    if data.get("pref_age_min"):
        lines.append(f"{T['pref_age_label']}: {data['pref_age_min']}-{data['pref_age_max']}")
    else:
        lines.append(f"{T['pref_age_label']}: {T['any_age_label']}")
    if country_val != "any":
        lines.append(f"{T['pref_country_label']}: {country_val}")
    else:
        lines.append(f"{T['pref_country_label']}: {T['any_f_label']}")
    return "\n".join(lines)


@router.message(Command("search"))
async def cmd_search(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    user_repo = UserRepo(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(T["register_first"])
        return

    if not user.is_vip:
        await message.answer(T["search_vip_only"])
        return

    await message.answer(
        T["search_settings_title"] + "\n\n" + T["search_choose_gender"],
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
        T["search_choose_age"],
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
        T["search_choose_country"],
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

    summary = _pref_summary(data, value)
    await callback.message.edit_text(T["search_saved"].format(summary=summary))
    await callback.answer(T["saved"])
