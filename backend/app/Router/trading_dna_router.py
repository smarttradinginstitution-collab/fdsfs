from __future__ import annotations

from fastapi import APIRouter, Depends

from app.Controllers.trading_dna_controller import TradingDnaController
from app.Schemas.trading_dna import TradingDnaReport
from app.Router.dependencies import get_current_user

# --- Controller Instance ---
trading_dna_controller = TradingDnaController()

# --- Router Definition ---
router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_user)],
)

router.get(
    "/trading-dna",
    response_model=TradingDnaReport,
    summary="Get Trading DNA Analysis Report"
)(trading_dna_controller.get_trading_dna_report)