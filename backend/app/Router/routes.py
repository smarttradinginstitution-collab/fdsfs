# app/Router/routes.py

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

# 🔒 Dipendenze/guardie
from app.Router.auth import require_roles, get_current_claims
from app.Infrastructure.db import get_db

# 📦 Controller applicativi
from app.Controllers.auth_controller import AuthController
from app.Controllers.users_controller import UsersController
from app.Controllers.roles_controller import RolesController
from app.Controllers.user_roles_controller import UserRolesController
from app.Controllers.trades_controller import TradesController
from app.Controllers.user_dashboard_layout_controller import UserDashboardLayoutController

# 📦 Schemi response (opzionali ma utili in Swagger)
from app.Schemas.auth_user import AuthUserRead
from app.Schemas.role import RoleRead
from app.Schemas.auth_session import LoginResponse, RegisterResponse, LogoutResponse
from app.Schemas.trade import TradeRead
from app.Schemas.user_dashboard_layout import UserDashboardLayoutRead, UserDashboardLayoutUpdate
from app.Schemas.stats import ProcessedStats, EquityCurveData, TradeSummary
from app.Schemas.vantage_score import VantageScoreData

# Repo per diagnostica ruoli
from app.Repositories.user_role_repository import UserRoleRepository


# ──────────────────────────────────────────────────────────────────────────────
# Istanze controller (stateless)
# ──────────────────────────────────────────────────────────────────────────────
auth = AuthController()
users = UsersController()
roles = RolesController()
user_roles = UserRolesController()
trades = TradesController()
dashboard_layout = UserDashboardLayoutController()

# ──────────────────────────────────────────────────────────────────────────────
# Router principale aggregatore
# ──────────────────────────────────────────────────────────────────────────────
router = APIRouter()

# ──────────────────────────────────────────────────────────────────────────────
# 🔐 AUTH (pubblico login/register; protetto logout)
# ──────────────────────────────────────────────────────────────────────────────
router_auth = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# LOGIN/REGISTER pubblici
router_auth.post("/login", response_model=LoginResponse)(auth.login)
router_auth.post("/register", response_model=RegisterResponse)(auth.register)

# LOGOUT protetto: richiede un token valido
router_auth.post(
    "/logout",
    response_model=LogoutResponse,
    dependencies=[Depends(get_current_claims)],
)(auth.logout)

# (Facoltativo ma utile) Rotte diagnostiche per capire rapidamente chi è l'utente e i suoi ruoli
@router_auth.get("/me", tags=["Auth"], response_model=AuthUserRead)
async def who_am_i(
    claims=Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the complete data for the currently authenticated user,
    including their profile and brokerage connections.
    """
    from app.Repositories.auth_user_repository import AuthUserRepository

    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

    user_repo = AuthUserRepository(db)
    user = await user_repo.get(UUID(user_id_str))

    if not user:
        raise HTTPException(status_code=404, detail="Authenticated user not found in database.")

    return AuthUserRead.model_validate(user)

@router_auth.get("/me/roles", tags=["Auth"])
async def my_roles(
    claims=Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRoleRepository(db)
    user_id = UUID(claims["sub"])
    roles_list = await repo.list_user_roles(user_id)
    return {"roles": [r.name for r in roles_list]}

# monta il blocco auth nel router principale
router.include_router(router_auth)

# ──────────────────────────────────────────────────────────────────────────────
# 👥 USERS (protetto: admin)
# ──────────────────────────────────────────────────────────────────────────────
router_users = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
    dependencies=[Depends(require_roles(["admin"]))],  # protezione group-level
)

router_users.get("/", response_model=list[AuthUserRead])(users.list_users)
router_users.get("/{user_id}", response_model=AuthUserRead)(users.get_user)
router_users.post("/", response_model=AuthUserRead)(users.create_user)
router_users.put("/{user_id}", response_model=AuthUserRead)(users.update_user)
router_users.delete("/{user_id}")(users.delete_user)

router.include_router(router_users)

# ──────────────────────────────────────────────────────────────────────────────
# 🛂 ROLES (protetto: admin)
# ──────────────────────────────────────────────────────────────────────────────
router_roles = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_roles.get("/", response_model=list[RoleRead])(roles.list_roles)
router_roles.get("/{role_id}", response_model=RoleRead)(roles.get_role)
router_roles.post("/", response_model=RoleRead)(roles.create_role)
router_roles.put("/{role_id}", response_model=RoleRead)(roles.update_role)
router_roles.delete("/{role_id}")(roles.delete_role)

router.include_router(router_roles)

# ──────────────────────────────────────────────────────────────────────────────
# 🔗 USER ↔ ROLES (protetto: admin)
# ──────────────────────────────────────────────────────────────────────────────
router_user_roles = APIRouter(
    prefix="/api/v1",
    tags=["User-Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

# Ritorna direttamente i RUOLI (RoleRead) assegnati all'utente
router_user_roles.get(
    "/users/{user_id}/roles",
    response_model=list[RoleRead],
)(user_roles.list_user_roles)

# Assegna un ruolo a un utente, e restituisce il ruolo assegnato
router_user_roles.post(
    "/users/assign-role",
    response_model=RoleRead,
)(user_roles.assign_role)

# Rimuove un ruolo da un utente
router_user_roles.delete(
    "/users/{user_id}/roles/{role_id}",
)(user_roles.unassign_role)

router.include_router(router_user_roles)

# ──────────────────────────────────────────────────────────────────────────────
# 📊 DASHBOARD (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
router_dashboard = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_claims)],
)

router_dashboard.get("/layout", response_model=UserDashboardLayoutRead)(
    dashboard_layout.get_user_layout
)
router_dashboard.put("/layout", response_model=UserDashboardLayoutRead)(
    dashboard_layout.save_user_layout
)

router.include_router(router_dashboard)


# ──────────────────────────────────────────────────────────────────────────────
# 💹 TRADES (pubblici a livello router; user_id via query per swagger)
#    → se vuoi proteggerli con token in futuro, aggiungi get_current_claims
# ──────────────────────────────────────────────────────────────────────────────
router_trades = APIRouter(prefix="/api/v1/trades", tags=["Trades"])

# --- Ordine corretto: prima le rotte specifiche, poi quelle con parametri ---
router_trades.get("/", response_model=list[TradeRead])(trades.list_trades)
router_trades.get("/vantage-score", response_model=VantageScoreData)(trades.get_vantage_score)
router_trades.get("/setups", response_model=List[str])(trades.list_setups)
router_trades.get("/calendar/data")(trades.calendar_data)
router_trades.get("/performance/metrics")(trades.get_performance_metrics)
router_trades.get("/processed-stats", response_model=ProcessedStats)(trades.get_processed_stats)
router_trades.get("/equity-curve", response_model=EquityCurveData)(trades.get_equity_curve)
router_trades.get("/summary", response_model=TradeSummary)(trades.get_trade_summary)
router_trades.get("/{trade_id}", response_model=TradeRead)(trades.get_trade)
router_trades.post("/", response_model=TradeRead, status_code=201)(trades.create_trade)
router_trades.put("/{trade_id}", response_model=TradeRead)(trades.update_trade)
router_trades.delete("/{trade_id}")(trades.delete_trade)

router.include_router(router_trades)

# ──────────────────────────────────────────────────────────────────────────────
# 🔗 SNAPTRADE (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers.snaptrade_controller import SnapTradeController
from app.Schemas.connection import ConnectionSchema
from app.Schemas.brokerage_account import AccountListResponse
snaptrade = SnapTradeController()

router_snaptrade = APIRouter(
    prefix="/api/v1/snaptrade",
    tags=["SnapTrade"],
    dependencies=[Depends(get_current_claims)],
)

router_snaptrade.post("/register")(snaptrade.handle_register_user)
router_snaptrade.post("/generate-connection-link")(snaptrade.handle_generate_connection_link)
router_snaptrade.post("/reconnect-link")(snaptrade.handle_reconnect_link)
router_snaptrade.get("/connections", response_model=list[ConnectionSchema])(snaptrade.list_connections)
router_snaptrade.get("/accounts", response_model=AccountListResponse)(snaptrade.get_accounts)
router_snaptrade.get(
    "/connections/{connection_id}",
    response_model=ConnectionSchema,
    summary="Get and refresh a single brokerage connection",
)(snaptrade.handle_get_connection_details)
router_snaptrade.delete(
    "/connections/{connection_id}",
    status_code=204,
    summary="Delete a brokerage connection",
)(snaptrade.handle_delete_connection)

router_snaptrade.post(
    "/connections/{connection_id}/refresh",
    summary="Refresh a brokerage connection's holdings",
)(snaptrade.handle_refresh_connection)

router.include_router(router_snaptrade)


# ──────────────────────────────────────────────────────────────────────────────
# 💼 ACCOUNTS (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Schemas.snaptrade import AccountHoldingsRead

router_accounts = APIRouter(
    prefix="/api/v1/accounts",
    tags=["Accounts"],
    dependencies=[Depends(get_current_claims)],
)

router_accounts.get(
    "/{account_id}/holdings",
    response_model=AccountHoldingsRead,
    summary="Get all holdings for a specific trading account",
)(snaptrade.get_account_holdings)

router.include_router(router_accounts)

# ──────────────────────────────────────────────────────────────────────────────
# 👑 ADMIN (protetto: admin)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers.admin_controller import router as admin_router

router_admin = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_admin.include_router(admin_router)

router.include_router(router_admin)
