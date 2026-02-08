from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.menu import router as menu_router
from bot.handlers.chat import router as chat_router
from bot.handlers.search import router as search_router
from bot.handlers.referral import router as referral_router
from bot.handlers.top import router as top_router
from bot.handlers.payment import router as payment_router


def get_all_routers() -> list[Router]:
    return [
        payment_router,
        start_router,
        menu_router,
        search_router,
        referral_router,
        top_router,
        chat_router,
    ]
