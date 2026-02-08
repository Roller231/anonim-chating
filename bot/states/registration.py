from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_gender = State()
    waiting_age = State()
    waiting_country = State()
    waiting_interests = State()


class SearchSettingsStates(StatesGroup):
    waiting_pref_gender = State()
    waiting_pref_age = State()
    waiting_pref_country = State()


class BroadcastStates(StatesGroup):
    waiting_content = State()
