from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.request_log import RequestLog
from app.Repositories.base_repository import BaseRepository

class RequestLogRepository(BaseRepository[RequestLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RequestLog)
