# backend/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import JSON
from sqlalchemy.ext.compiler import compiles
from fastapi.testclient import TestClient

from app.main import app
from app.Infrastructure.db import Base, get_db
from app.Router.auth import get_current_claims
# Import all models to ensure they are registered with Base
from app.Models import (
    auth_user, role, tag, trade, trades_tags, user_dashboard_layout, user_role,
    general_account, trading_account, broker, asset, asset_class, mistake,
    playbook, news_impact, psychology_state, trades_mistakes, trades_playbooks,
    trades_news_impacts, trades_psychology
)
from app.Models.auth_user import AuthUser

# This is a hack to make the tests work with SQLite
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return "JSON"


# --- Fixtures for Sync Tests ---

SYNC_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def sync_engine():
    return create_engine(SYNC_TEST_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)

@pytest.fixture(scope="session")
def sync_tables(sync_engine):
    for table in Base.metadata.tables.values():
        table.schema = None
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)

@pytest.fixture(scope="function")
def db_session_sync(sync_engine, sync_tables):
    """Fixture for a sync db session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def test_client_sync(db_session_sync):
    """
    Creates a sync test client, overriding dependencies for db and auth.
    """
    def override_get_db():
        yield db_session_sync

    mock_user_id = uuid.uuid4()
    mock_user_email = "test@example.com"

    def override_get_current_claims():
        # Ensure the user exists in the DB for foreign key constraints
        user = db_session_sync.query(AuthUser).filter_by(id=mock_user_id).first()
        if not user:
            # The auth.users table has many columns, but for tests, id and email are sufficient
            user_data = {
                'id': mock_user_id,
                'email': mock_user_email,
                'is_sso_user': False,
                'is_anonymous': False,
            }
            user = AuthUser(**user_data)
            db_session_sync.add(user)
            db_session_sync.commit()
        return {"sub": str(mock_user_id), "email": mock_user_email}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_claims] = override_get_current_claims

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()