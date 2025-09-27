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