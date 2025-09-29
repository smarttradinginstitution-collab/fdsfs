from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.mistake_controller import MistakeController
from app.Schemas.mistake import MistakeRead, MistakeCreate, MistakeUpdate, MistakeAdminRead
from app.Router.auth import require_roles
from app.Router.dependencies import get_current_user

# ------------------------------------------------------------------------------
# Istanze Controller (stateless)
# ------------------------------------------------------------------------------
mistakes = MistakeController()

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------
# Rotte Admin
# ------------------------------------------------------------------------------
router.get(
    "/admin/mistakes",
    response_model=List[MistakeAdminRead],
    tags=["Mistakes", "Admin"],
    summary="[Admin] Lista tutti i mistakes di tutti gli account",
    dependencies=[Depends(require_roles(["admin"]))],
)(mistakes.list_all_mistakes_for_admin)

# ------------------------------------------------------------------------------
# Rotte Utente Autenticato (/me)
# ------------------------------------------------------------------------------
router.get(
    "/me/mistakes",
    response_model=List[MistakeRead],
    tags=["Mistakes"],
    summary="Lista i miei mistakes",
    dependencies=[Depends(get_current_user)],
)(mistakes.list_my_mistakes)

router.post(
    "/me/mistakes",
    response_model=MistakeRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Mistakes"],
    summary="Crea un nuovo mistake",
    dependencies=[Depends(get_current_user)],
)(mistakes.create_mistake)

# ------------------------------------------------------------------------------
# Rotte per ID specifico (con controllo di ownership)
# ------------------------------------------------------------------------------
router.get(
    "/mistakes/{mistake_id}",
    response_model=MistakeRead,
    tags=["Mistakes"],
    summary="Recupera un mistake per ID",
)(mistakes.get_mistake)

router.put(
    "/mistakes/{mistake_id}",
    response_model=MistakeRead,
    tags=["Mistakes"],
    summary="Aggiorna un mistake per ID",
)(mistakes.update_mistake)

router.delete(
    "/mistakes/{mistake_id}",
    status_code=status.HTTP_200_OK,
    tags=["Mistakes"],
    summary="Elimina un mistake per ID",
)(mistakes.delete_mistake)