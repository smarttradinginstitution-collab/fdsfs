import asyncio
import os
import sys
import json
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# --- Path Setup ---
# Add the project root and backend directory to the Python path to resolve imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# --- Environment Loading ---
# Load environment variables from the .env file in the backend directory
from dotenv import load_dotenv
env_path = os.path.join(backend_path, '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("Loaded environment variables from backend/.env")
else:
    print("Warning: backend/.env file not found. Script may fail if env vars are not set.")

# --- Database and Model Imports ---
# Must be imported after the path and env are set up
from backend.app.Infrastructure.db import get_db, engine

async def migrate_legacy_rules():
    """
    Reads old playbook rules from `rules_groups_playbook` and `rules_playbook`,
    transforms them into a structured format, and inserts them into the new
    `playbook_blocks` table with the type 'LEGACY_RULES'.
    """
    print("Starting legacy playbook rule migration...")
    db_session: AsyncSession | None = None

    try:
        # --- Database Connection ---
        async_session_factory = await get_db()
        db_session = async_session_factory()

        # --- Data Extraction ---
        # 1. Fetch all legacy rules and their groups, ordered for correct processing
        query = text("""
            SELECT
                r.playbook_id,
                rgp.name_group,
                rp.rule,
                rgp."order" as group_order,
                rp."order" as rule_order
            FROM public.rules_groups_playbook rgp
            JOIN public.rules_playbook rp ON rgp.id = rp.rules_groups_playbook_id
            JOIN public.playbooks r ON rgp.playbook_id = r.id
            ORDER BY r.playbook_id, group_order, rule_order;
        """)
        result = await db_session.execute(query)
        legacy_rules = result.fetchall()

        if not legacy_rules:
            print("No legacy rules found to migrate. Exiting.")
            return

        print(f"Found {len(legacy_rules)} legacy rule entries to process.")

        # --- Data Transformation ---
        # 2. Group rules by playbook, preserving their structure
        playbook_rules_map = defaultdict(lambda: defaultdict(list))
        for rule in legacy_rules:
            playbook_id = str(rule.playbook_id)
            group_name = rule.name_group
            rule_text = rule.rule
            playbook_rules_map[playbook_id][group_name].append(rule_text)

        print(f"Aggregated rules for {len(playbook_rules_map)} playbooks.")

        # --- Data Insertion ---
        # 3. Insert the transformed data into the new `playbook_blocks` table
        async with db_session.begin():
            insert_count = 0
            for playbook_id, groups in playbook_rules_map.items():
                # Convert the defaultdict to a regular dict for JSON serialization
                content_json = json.dumps(dict(groups))

                insert_statement = text("""
                    INSERT INTO public.playbook_blocks (playbook_id, block_type, content, "order")
                    VALUES (:playbook_id, 'LEGACY_RULES', :content, 999);
                """)
                await db_session.execute(
                    insert_statement,
                    {"playbook_id": playbook_id, "content": content_json}
                )
                insert_count += 1

        await db_session.commit()
        print(f"Successfully created {insert_count} LEGACY_RULES blocks in the playbook_blocks table.")

    except Exception as e:
        print(f"An error occurred during the migration: {e}")
        if db_session:
            await db_session.rollback()
            print("Transaction rolled back.")
    finally:
        if db_session:
            await db_session.close()
        await engine.dispose()
        print("Database connection closed.")


if __name__ == "__main__":
    print("Running the legacy rule migration script...")
    asyncio.run(migrate_legacy_rules())
    print("Script finished.")
