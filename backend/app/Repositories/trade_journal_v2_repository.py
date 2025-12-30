from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.trade_journal_v2 import TradeJournalV2
from app.Repositories.base_repository import BaseRepository

class TradeJournalV2Repository(BaseRepository[TradeJournalV2]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TradeJournalV2)
