# backend/app/Models/enums.py
import enum

class TradeDirection(str, enum.Enum):
    LONG = "long"
    SHORT = "short"

class TradeStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class ImportSourceType(str, enum.Enum):
    CSV = "csv"
    HTML = "html"
    XML = "xml"
    API = "api"
    MANUAL = "manual"