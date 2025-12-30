from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.Bridge.trades_rules import TradesRules
from app.Repositories.base_repository import BaseRepository

class TradesRulesRepository(BaseRepository[TradesRules]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TradesRules)
