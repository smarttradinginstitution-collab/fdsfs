# app/Models/__init__.py

# This file is crucial for SQLAlchemy's ability to correctly
# discover and map all the ORM models. By importing them here,
# we ensure that the Base metadata is populated before any
# application logic or test tries to use them.

# The order of imports can be important to resolve dependencies,
# especially for relationships and foreign keys. We import models
# with fewer dependencies first.

# Base models without dependencies on other new models
from .auth_user import AuthUser
from .role import Role
from .user_role import UserRole
from .general_account import GeneralAccount
from .asset_market import AssetMarket
from .asset_class import AssetClass
from .mistake import Mistake
from .news_impact import NewsImpact
from .playbook import Playbook
from .psychology_state import PsychologyState
from .tag import Tag
from .user_dashboard_layout import UserDashboardLayout
from .image import Image

# New or modified models with dependencies
from .platform import Platform
from .broker import Broker
from .trading_account import TradingAccount
from .asset import Asset
from .asset_alias import AssetAlias
from .import_run import ImportRun
from .trade import Trade

# Association tables
from .broker_platform import BrokerPlatform
from .trades_mistakes import TradesMistakes
from .trades_news_impacts import TradesNewsImpacts
from .trades_psychology import TradesPsychology
from .trades_tags import TradesTags

__all__ = [
    "AuthUser",
    "Role",
    "UserRole",
    "GeneralAccount",
    "AssetMarket",
    "Platform",
    "Broker",
    "TradingAccount",
    "AssetClass",
    "Asset",
    "AssetAlias",
    "ImportRun",
    "Trade",
    "Mistake",
    "NewsImpact",
    "Playbook",
    "PsychologyState",
    "Tag",
    "UserDashboardLayout",
    "Image",
    "BrokerPlatform",
    "TradesMistakes",
    "TradesNewsImpacts",
    "TradesPsychology",
    "TradesTags",
]