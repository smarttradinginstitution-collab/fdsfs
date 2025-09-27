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
    TRADOVATE_CSV = "tradovate_csv"
    MT5_HTML = "mt5_html"
    API = "api"
    MANUAL = "manual"