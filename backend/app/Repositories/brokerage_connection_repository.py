# app/Repositories/brokerage_connection_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.brokerage_connection import BrokerageConnection
import uuid

class BrokerageConnectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: uuid.UUID) -> list[BrokerageConnection]:
        """
        Lists all non-deleted brokerage connections for a given user.
        """
        result = await self.db.execute(
            select(BrokerageConnection)
            .where(BrokerageConnection.user_id == user_id)
            .where(BrokerageConnection.deleted_at.is_(None))
        )
        return result.scalars().all()

    async def get_by_id(self, connection_id: uuid.UUID) -> BrokerageConnection | None:
        """
        Gets a single brokerage connection by its primary key.
        """
        return await self.db.get(BrokerageConnection, connection_id)

    async def soft_delete(self, connection: BrokerageConnection) -> BrokerageConnection:
        """
        Soft-deletes a brokerage connection by setting its deleted_at timestamp.
        """
        from datetime import datetime, timezone

        connection.deleted_at = datetime.now(timezone.utc)
        self.db.add(connection)
        await self.db.commit()
        await self.db.refresh(connection)
        return connection
