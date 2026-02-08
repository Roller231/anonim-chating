from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.db.repositories import SearchQueueRepo


class MatchingService:
    """
    MySQL-backed search queue for matching users.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SearchQueueRepo(session)

    async def add_to_queue(self, user: User, room_id: int | None = None) -> None:
        await self.repo.add_to_queue(user, room_id=room_id)

    async def remove_from_queue(self, telegram_id: int) -> None:
        await self.repo.remove_from_queue(telegram_id)

    async def is_in_queue(self, telegram_id: int) -> bool:
        entry = await self.repo.get_from_queue(telegram_id)
        return entry is not None

    async def find_match(self, user: User, room_id: int | None = None) -> int | None:
        match = await self.repo.find_match(user, room_id=room_id)
        if match:
            matched_id = match.telegram_id
            await self.repo.remove_from_queue(matched_id)
            await self.repo.remove_from_queue(user.telegram_id)
            return matched_id
        return None

    async def queue_size(self) -> int:
        return await self.repo.queue_size()
