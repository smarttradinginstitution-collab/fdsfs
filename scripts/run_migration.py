import asyncio
import os
import sys
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Add the project root and backend directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Load environment variables from the .env file in the backend directory
env_path = os.path.join(backend_path, '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("Loaded environment variables from backend/.env")
else:
    print("Warning: backend/.env file not found. Script may fail if env vars are not set.")

from backend.app.Infrastructure.db import get_db, engine

async def run_migration(sql_file_path: str):
    """
    Runs a SQL migration file against the database.
    """
    print(f"Starting migration from file: {sql_file_path}...")

    db_session: AsyncSession | None = None
    try:
        # Get a database session
        async_session_factory = await get_db()
        db_session = async_session_factory()

        # Read the SQL file
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()

        # Execute the entire SQL script within a transaction
        async with db_session.begin():
            await db_session.execute(text(sql_content))

        print("Migration script executed successfully.")
        await db_session.commit()
        print("Commit successful.")

    except FileNotFoundError:
        print(f"Error: The file '{sql_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred during the migration: {e}")
        if db_session:
            await db_session.rollback()
    finally:
        if db_session:
            await db_session.close()
        await engine.dispose()

if __name__ == "__main__":
    # The SQL file to execute is passed as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_migration <path_to_sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    asyncio.run(run_migration(sql_file))
