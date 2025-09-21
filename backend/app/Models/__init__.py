"""
This module serves as the single point of entry for all SQLAlchemy models.

Importing all models here and defining __all__ ensures that SQLAlchemy's
declarative base is aware of all tables and their relationships when the
application starts, preventing `NoReferencedTableError` issues due to
implicit import order.
"""
from .auth_user import AuthUser
from .profile import Profile
from .role import Role
from .brokerage_connection import BrokerageConnection
from .brokerage_account import BrokerageAccount
from .security import Security
from .option_symbol import OptionSymbol
from .account_balance import AccountBalance
from .account_position import AccountPosition
from .account_order import AccountOrder
from .account_order_option import AccountOrderOption
from .account_activity import AccountActivity
from .tag import Tag
from .trade import Trade
from .trades_tags import TradesTags
from .user_dashboard_layout import UserDashboardLayout
from .user_role import UserRole

__all__ = [
    "AuthUser",
    "Profile",
    "Role",
    "BrokerageConnection",
    "BrokerageAccount",
    "Security",
    "OptionSymbol",
    "AccountBalance",
    "AccountPosition",
    "AccountOrder",
    "AccountOrderOption",
    "AccountActivity",
    "Tag",
    "Trade",
    "TradesTags",
    "UserDashboardLayout",
    "UserRole",
]
