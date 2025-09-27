# app/Services/trading_account_service.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.trading_account import TradingAccountCreate, TradingAccountRead
from app.Models.trading_account import TradingAccount
from app.Infrastructure.db import get_db


class TradingAccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = TradingAccountRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)

    async def create_trading_account_for_user(
        self, claims: dict, account_data: TradingAccountCreate
    ) -> TradingAccountRead:
        """
        Crea un TradingAccount per l'utente corrente.
        Verifica prima che l'utente abbia un GeneralAccount.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente non ha un General Account. Creane uno prima.",
            )

        db_account = await self.repo.create_trading_account(
            general_account_id=general_account.id,
            account_data=account_data,
        )

        # Dopo la creazione, ricarica l'account con la relazione del broker per
        # garantire che la risposta API sia completa e non causi errori.
        stmt = (
            select(TradingAccount)
            .where(TradingAccount.id == db_account.id)
            .options(selectinload(TradingAccount.broker))
        )
        result = await self.db.execute(stmt)
        refreshed_account = result.scalar_one()

        # Costruisce la risposta arricchita, come nella funzione di elenco
        account_read = TradingAccountRead.from_orm(refreshed_account)
        if refreshed_account.broker:
            account_read.broker = refreshed_account.broker
            account_read.broker_name = refreshed_account.broker.name

        return account_read

    async def get_trading_accounts_for_user(
        self, claims: dict
    ) -> List[TradingAccountRead]:
        """
        Elenca tutti i TradingAccount per l'utente corrente, includendo i dati del broker.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            return []

        db_accounts = await self.repo.list_by_general_account_id(general_account.id)

        # Arricchisce i dati con il nome del broker
        accounts_with_broker_info = []
        for acc in db_accounts:
            account_read = TradingAccountRead.from_orm(acc)
            if acc.broker:
                # Popola sia l'oggetto broker che il campo broker_name per flessibilità nel frontend
                account_read.broker = acc.broker
                account_read.broker_name = acc.broker.name
            accounts_with_broker_info.append(account_read)

        return accounts_with_broker_info

    async def get_trading_account_by_id(
        self, account_id: UUID, claims: dict
    ) -> Optional[TradingAccountRead]:
        """
        Recupera un singolo TradingAccount per ID, verificando che appartenga all'utente.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            return None

        db_account = await self.repo.get_by_id(account_id)
        if db_account and db_account.general_account_id == general_account.id:
            return TradingAccountRead.from_orm(db_account)

        return None