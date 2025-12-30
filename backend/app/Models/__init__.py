# app/Models/__init__.py

# This file is crucial for SQLAlchemy's ability to correctly
# discover and map all the ORM models. By importing them here,
# we ensure that the Base metadata is populated before any
# application logic or test tries to use them.

from .auth_user import AuthUser
from .Bridge.user_role import UserRole
from .Bridge.broker_platform import BrokerPlatform
from .Bridge.trades_mistakes import TradesMistakes
from .Bridge.trades_news_impacts import TradesNewsImpacts
from .Bridge.trades_psychology import TradesPsychology
from .Bridge.trades_tags import TradesTags
from .Bridge.notes_note_templates import notes_note_templates_association
from .Bridge.broker_asset import BrokerAsset
from .Bridge.trades_rules import TradesRules

from .role import Role
from .general_account import GeneralAccount
from .asset_market import AssetMarket
from .asset_class import AssetClass
from .mistake import Mistake
from .news_impact import NewsImpact
from .rules_group_playbook import RulesGroupPlaybook
from .rule_playbook import RulePlaybook
from .playbook import Playbook
from .psychology_state import PsychologyState
from .tags_group import TagsGroup
from .news_impacts_group import NewsImpactsGroup
from .tag import Tag
from .user_dashboard_layout import UserDashboardLayout
from .image import Image

# New models
from .instrument import Instrument
from .playbook_block import PlaybookBlock
from .request_log import RequestLog
from .trading_account_daily_balance import TradingAccountDailyBalance
from .trade_journal_v2 import TradeJournalV2
from .business_audit_log import BusinessAuditLog

# New or modified models with dependencies
from .platform import Platform
from .broker import Broker
from .trading_account import TradingAccount
from .asset import Asset
from .asset_alias import AssetAlias
from .import_run import ImportRun
from .trade import Trade
from .notebook_folder import NotebookFolder
from .note import Note
from .note_template import NoteTemplate

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
    "RulesGroupPlaybook",
    "RulePlaybook",
    "PsychologyState",
    "TagsGroup",
    "NewsImpactsGroup",
    "Tag",
    "UserDashboardLayout",
    "Image",
    "NotebookFolder",
    "Note",
    "NoteTemplate",
    "BrokerPlatform",
    "TradesMistakes",
    "TradesNewsImpacts",
    "TradesPsychology",
    "TradesTags",
    "notes_note_templates_association",
    "Instrument",
    "PlaybookBlock",
    "RequestLog",
    "TradingAccountDailyBalance",
    "TradeJournalV2",
    "BusinessAuditLog",
    "BrokerAsset",
    "TradesRules",
]
