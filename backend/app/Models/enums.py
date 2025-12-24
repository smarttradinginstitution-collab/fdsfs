# backend/app/Models/enums.py
import enum

class TradeDirection(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class TradeStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    cancelled = "cancelled"

class ImportSourceType(str, enum.Enum):
    CSV = "csv"
    HTML = "html"
    XML = "xml"
    API = "api"
    MANUAL = "manual"

class FolderType(str, enum.Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"

class SystemFolderIdentifier(str, enum.Enum):
    """Specific identifiers for system folders with unique frontend behavior."""
    NONE = "NONE"
    TRADE_NOTES = "TRADE_NOTES"
    DAILY_JOURNAL = "DAILY_JOURNAL"
    SESSION_RECAP = "SESSION_RECAP"

class PlaybookBlockType(str, enum.Enum):
    THESIS = "THESIS"
    GALLERY = "GALLERY"
    CONDITIONS = "CONDITIONS"
    PSYCHOLOGY = "PSYCHOLOGY"
    LEGACY_RULES = "LEGACY_RULES"