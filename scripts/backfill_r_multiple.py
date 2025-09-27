import asyncio
import os
import sys
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.Infrastructure.db import get_db, engine
from app.Models.trade import Trade
from app.Services.trade_service import TradeService

async def main():
    """
    Backfills the r_multiple for existing trades in the database.
    """
    print("Starting backfill process for r_multiple...")

    db_session: Optional[AsyncSession] = None
    try:
        # Get a database session
        async_session_factory = await get_db()
        db_session = async_session_factory()

        # Instantiate the service that contains the calculation logic
        trade_service = TradeService(db=db_session)

        # 1. Fetch all trades where r_multiple is NULL
        query = select(Trade).where(Trade.r_multiple.is_(None))
        result = await db_session.execute(query)
        trades_to_update = result.scalars().all()

        if not trades_to_update:
            print("No trades found that require r_multiple backfilling. Exiting.")
            return

        print(f"Found {len(trades_to_update)} trades to process.")

        updated_count = 0
        for i, trade in enumerate(trades_to_update):
            # 2. Use the central calculation logic
            r_multiple_value = trade_service._calculate_r_multiple(
                pnl=trade.p_l,
                entry_price=trade.entry_price,
                stop_loss_price=trade.stop_loss_price,
                position_size=trade.position_size
            )

            # 3. Update the trade if a value was calculated
            if r_multiple_value is not None:
                trade.r_multiple = r_multiple_value
                updated_count += 1

            # Log progress every 100 trades
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(trades_to_update)} trades...")

        # 4. Commit all changes to the database
        if updated_count > 0:
            print(f"Committing updates for {updated_count} trades...")
            await db_session.commit()
            print("Commit successful.")
        else:
            print("No trades were updated as required data was missing.")

        print(f"Backfill process complete. Total trades processed: {len(trades_to_update)}. Total trades updated: {updated_count}.")

    except Exception as e:
        print(f"An error occurred during the backfill process: {e}")
        if db_session:
            await db_session.rollback()
    finally:
        if db_session:
            await db_session.close()
        await engine.dispose()

if __name__ == "__main__":
    # This script needs to be run in an environment where the application's
    # database connection can be established.
    # Example command from the project root:
    # python -m scripts.backfill_r_multiple
    asyncio.run(main())