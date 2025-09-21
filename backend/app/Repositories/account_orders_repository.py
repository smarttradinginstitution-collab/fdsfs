from __future__ import annotations
import uuid
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Models.account_order import AccountOrder
from app.Schemas.snaptrade import AccountOrderCreate

class AccountOrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_orders_and_options(self, orders_data: List[Dict[str, Any]]):
        """
        Upserts a list of orders and handles their related options using a
        "delete-then-insert" strategy for the options.
        The entire operation is performed within a single transaction.
        """
        async with self.db.begin():
            for order_data in orders_data:
                option_data = order_data.pop("option_symbol", None)
                order_id = order_data.get("id")

                if not order_id:
                    continue

                await self.db.execute(
                    text("DELETE FROM public.account_order_options WHERE account_order_id = :order_id"),
                    {"order_id": order_id}
                )

                upsert_order_stmt = text("""
                    INSERT INTO public.account_orders (
                        id, account_id, symbol, action, status, total_quantity, filled_quantity,
                        execution_price, limit_price, time_placed, open_quantity, canceled_quantity,
                        stop_price, order_type, time_in_force, time_updated, time_executed, expiry_date,
                        take_profit_order_id, stop_loss_order_id, quote_universal_symbol, quote_currency,
                        universal_symbol
                    ) VALUES (
                        :id, :account_id, :symbol, :action, :status, :total_quantity, :filled_quantity,
                        :execution_price, :limit_price, :time_placed, :open_quantity, :canceled_quantity,
                        :stop_price, :order_type, :time_in_force, :time_updated, :time_executed, :expiry_date,
                        :take_profit_order_id, :stop_loss_order_id, :quote_universal_symbol, :quote_currency,
                        :universal_symbol
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        account_id = EXCLUDED.account_id,
                        symbol = EXCLUDED.symbol,
                        action = EXCLUDED.action,
                        status = EXCLUDED.status,
                        total_quantity = EXCLUDED.total_quantity,
                        filled_quantity = EXCLUDED.filled_quantity,
                        execution_price = EXCLUDED.execution_price,
                        limit_price = EXCLUDED.limit_price,
                        time_placed = EXCLUDED.time_placed,
                        open_quantity = EXCLUDED.open_quantity,
                        canceled_quantity = EXCLUDED.canceled_quantity,
                        stop_price = EXCLUDED.stop_price,
                        order_type = EXCLUDED.order_type,
                        time_in_force = EXCLUDED.time_in_force,
                        time_updated = EXCLUDED.time_updated,
                        time_executed = EXCLUDED.time_executed,
                        expiry_date = EXCLUDED.expiry_date,
                        take_profit_order_id = EXCLUDED.take_profit_order_id,
                        stop_loss_order_id = EXCLUDED.stop_loss_order_id,
                        quote_universal_symbol = EXCLUDED.quote_universal_symbol,
                        quote_currency = EXCLUDED.quote_currency,
                        universal_symbol = EXCLUDED.universal_symbol,
                        updated_at = now();
                """)
                await self.db.execute(upsert_order_stmt, order_data)

                if option_data:
                    insert_option_stmt = text("""
                        INSERT INTO public.account_order_options (
                            account_order_id, option_ticker, option_type, strike_price,
                            expiration_date, is_mini_option, underlying_security_id
                        ) VALUES (
                            :account_order_id, :ticker, :option_type, :strike_price,
                            :expiration_date, :is_mini_option, :underlying_security_id
                        )
                    """)
                    option_params = {
                        "account_order_id": order_id,
                        "ticker": option_data.get("ticker"),
                        "option_type": option_data.get("option_type"),
                        "strike_price": option_data.get("strike_price"),
                        "expiration_date": option_data.get("expiration_date"),
                        "is_mini_option": option_data.get("is_mini_option"),
                        "underlying_security_id": option_data.get("underlying_security_id")
                    }
                    await self.db.execute(insert_option_stmt, option_params)

    async def get_orders_by_ids(self, order_ids: List[str]) -> List[AccountOrder]:
        """
        Fetches a list of AccountOrder objects from the database by their IDs.
        """
        if not order_ids:
            return []

        result = await self.db.execute(
            text("SELECT * FROM public.account_orders WHERE id = ANY(:order_ids)"),
            {"order_ids": order_ids}
        )
        return result.mappings().all()

    @staticmethod
    def build_orders_from_schemas(account_id: uuid.UUID, orders: list[AccountOrderCreate]) -> list[AccountOrder]:
        """
        Constructs a list of AccountOrder ORM objects from schemas.
        This method does not interact with the database.
        """
        return [
            AccountOrder(
                account_id=account_id,
                **order.model_dump()
            ) for order in orders
        ]
