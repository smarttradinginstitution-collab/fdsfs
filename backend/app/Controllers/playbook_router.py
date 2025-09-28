from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.playbook_controller import PlaybookController
from app.Schemas.playbook import PlaybookRead, PlaybookCreate, PlaybookUpdate, PlaybookAdminRead
from app.Router.auth import require_roles
from app.Router.dependencies import get_current_user

# ------------------------------------------------------------------------------
# Istanze Controller (stateless)
# ------------------------------------------------------------------------------
playbooks = PlaybookController()

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------
# Rotte Admin
# ------------------------------------------------------------------------------
router.get(
    "/admin/playbooks",
    response_model=List[PlaybookAdminRead],
    tags=["Playbooks", "Admin"],
    summary="[Admin] Lista tutti i playbook di tutti gli account",
    dependencies=[Depends(require_roles(["admin"]))],
)(playbooks.list_all_playbooks_for_admin)

# ------------------------------------------------------------------------------
# Rotte Utente Autenticato (/me)
# ------------------------------------------------------------------------------
router.get(
    "/me/playbooks",
    response_model=List[PlaybookRead],
    tags=["Playbooks"],
    summary="Lista i miei playbook",
    dependencies=[Depends(get_current_user)],
)(playbooks.list_my_playbooks)

router.post(
    "/me/playbooks",
    response_model=PlaybookRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Playbooks"],
    summary="Crea un nuovo playbook",
    dependencies=[Depends(get_current_user)],
)(playbooks.create_playbook)

# ------------------------------------------------------------------------------
# Rotte per ID specifico (con controllo di ownership)
# ------------------------------------------------------------------------------
router.get(
    "/playbooks/{playbook_id}",
    response_model=PlaybookRead,
    tags=["Playbooks"],
    summary="Recupera un playbook per ID",
)(playbooks.get_playbook)

router.put(
    "/playbooks/{playbook_id}",
    response_model=PlaybookRead,
    tags=["Playbooks"],
    summary="Aggiorna un playbook per ID",
)(playbooks.update_playbook)

router.delete(
    "/playbooks/{playbook_id}",
    status_code=status.HTTP_200_OK,
    tags=["Playbooks"],
    summary="Elimina un playbook per ID",
)(playbooks.delete_playbook)