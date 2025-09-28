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
from app.Controllers.user_dashboard_layout_controller import UserDashboardLayoutController

# 📦 Schemi response (opzionali ma utili in Swagger)
from app.Schemas.auth_user import AuthUserRead
from app.Schemas.role import RoleRead
from app.Schemas.auth_session import LoginResponse, RegisterResponse, LogoutResponse, LoginMfaChallenge
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
router_auth.post("/login", response_model=LoginResponse | LoginMfaChallenge)(auth.login)
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


# ──────────────────────────────────────────────────────────────────────────────
# 🔐 MFA (Multi-Factor Authentication)
# ──────────────────────────────────────────────────────────────────────────────
# Le rotte MFA sono protette da token, eccetto la verifica che usa un token AAL1 speciale
from app.Schemas.auth_session import (
    VerifyMfaResponse,
    TotpEnrollResponse,
    ListFactorsResponse,
)

router_mfa = APIRouter(
    prefix="/mfa",
    tags=["Auth-MFA"],
)

# VERIFY (pubblico nel senso che non richiede un token AAL2, ma un AAL1 valido)
router_mfa.post("/verify", response_model=VerifyMfaResponse)(auth.verify_mfa)

# ENROLL, LIST, DELETE (richiedono token valido)
router_mfa.post(
    "/enroll-totp",
    response_model=TotpEnrollResponse,
    dependencies=[Depends(get_current_claims)],
)(auth.enroll_totp)

router_mfa.get(
    "/factors",
    response_model=ListFactorsResponse,
    dependencies=[Depends(get_current_claims)],
)(auth.list_factors)

router_mfa.delete(
    "/factors/{factor_id}",
    response_model=LogoutResponse, # Ritorna {ok: true}
    dependencies=[Depends(get_current_claims)],
)(auth.delete_factor)

router_mfa.post(
    "/disable",
    response_model=VerifyMfaResponse,
    dependencies=[Depends(get_current_claims)],
)(auth.disable_mfa)

# Monta le rotte MFA dentro al router di autenticazione (es. /api/v1/auth/mfa/...)
router_auth.include_router(router_mfa)


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
# 💼 GENERAL ACCOUNTS (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import general_account_controller

router.include_router(
    general_account_controller.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_claims)],
)

# ──────────────────────────────────────────────────────────────────────────────
# 🏷️ TAGS (protetto: user/admin)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import tag_router

router.include_router(
    tag_router.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_claims)],
)

# ──────────────────────────────────────────────────────────────────────────────
# 📥 IMPORT (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import import_controller

router.include_router(
    import_controller.router,
    dependencies=[Depends(get_current_claims)],
)

# ──────────────────────────────────────────────────────────────────────────────
# 📖 PLAYBOOKS (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import playbook_router

router.include_router(
    playbook_router.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_claims)],
)

# ──────────────────────────────────────────────────────────────────────────────
# 🏢 BROKERS (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import broker_controller

router.include_router(
    broker_controller.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_claims)],
)

# ──────────────────────────────────────────────────────────────────────────────
# 📈 TRADING ACCOUNTS (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import trading_account_controller

router.include_router(
    trading_account_controller.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_claims)],
)


# ──────────────────────────────────────────────────────────────────────────────
# 💹 TRADES (protetto: user)
# ──────────────────────────────────────────────────────────────────────────────
from app.Controllers import trades_controller

router.include_router(
    trades_controller.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_claims)],
)
