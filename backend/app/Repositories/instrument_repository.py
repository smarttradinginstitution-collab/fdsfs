from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.instrument import Instrument
from app.Repositories.base_repository import BaseRepository

class InstrumentRepository(BaseRepository[Instrument]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Instrument)
