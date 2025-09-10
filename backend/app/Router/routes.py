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

# 📦 Schemi response (opzionali ma utili in Swagger)
from app.Schemas.auth_user import AuthUserRead
from app.Schemas.role import RoleRead
from app.Schemas.auth_session import LoginResponse, RegisterResponse, LogoutResponse
from app.Schemas.trade import TradeRead
from app.Schemas.stats import ProcessedStats, EquityCurveData, TradeSummary, VantageScore

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
@router_auth.get("/me", tags=["Auth"])
async def who_am_i(claims=Depends(get_current_claims)):
    return {"sub": claims.get("sub")}

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
# 💹 TRADES (pubblici a livello router; user_id via query per swagger)
#    → se vuoi proteggerli con token in futuro, aggiungi get_current_claims
# ──────────────────────────────────────────────────────────────────────────────
router_trades = APIRouter(prefix="/api/v1/trades", tags=["Trades"])

# --- Ordine corretto: prima le rotte specifiche, poi quelle con parametri ---
router_trades.get("/", response_model=list[TradeRead])(trades.list_trades)
router_trades.get("/setups", response_model=List[str])(trades.list_setups)
router_trades.get("/calendar/data")(trades.calendar_data)
router_trades.get("/performance/metrics")(trades.get_performance_metrics)
router_trades.get("/processed-stats", response_model=ProcessedStats)(trades.get_processed_stats)
router_trades.get("/equity-curve", response_model=EquityCurveData)(trades.get_equity_curve)
router_trades.get("/summary", response_model=TradeSummary)(trades.get_trade_summary)
router_trades.get("/vantage-score", response_model=VantageScore)(trades.get_vantage_score)
router_trades.get("/{trade_id}", response_model=TradeRead)(trades.get_trade)
router_trades.post("/", response_model=TradeRead, status_code=201)(trades.create_trade)
router_trades.put("/{trade_id}", response_model=TradeRead)(trades.update_trade)
router_trades.delete("/{trade_id}")(trades.delete_trade)

router.include_router(router_trades)
