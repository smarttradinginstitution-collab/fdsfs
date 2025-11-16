
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.playbook_controller import PlaybookController
from app.Schemas.playbook import PlaybookRead, PlaybookCreate, PlaybookUpdate, PlaybookAdminRead, PlaybookAnalytics
from app.Schemas.trade import TradeRead
from app.Router.auth import require_roles
from app.Router.dependencies import get_current_user
from app.Schemas.playbook_block import PlaybookBlockRead, PlaybookBlockCreate, PlaybookBlockUpdate

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

router.get(
    "/playbooks/{playbook_id}/analytics",
    response_model=PlaybookAnalytics,
    tags=["Playbooks"],
    summary="Recupera i dati analitici di un playbook",
)(playbooks.get_playbook_analytics)

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

router.get(
    "/playbooks/{playbook_id}/trades",
    response_model=List[TradeRead],
    tags=["Playbooks"],
    summary="Recupera i trade eseguiti per un playbook",
)(playbooks.list_trades_for_playbook)

# ------------------------------------------------------------------------------
# Rotte per la gestione dei Blocchi di un Playbook
# ------------------------------------------------------------------------------

router.post(
    "/playbooks/{playbook_id}/blocks",
    response_model=PlaybookBlockRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Playbooks"],
    summary="Crea un nuovo blocco per un playbook",
)(playbooks.create_block)

router.put(
    "/playbooks/{playbook_id}/blocks/{block_id}",
    response_model=PlaybookBlockRead,
    tags=["Playbooks"],
    summary="Aggiorna un blocco specifico di un playbook",
)(playbooks.update_block)

router.delete(
    "/playbooks/{playbook_id}/blocks/{block_id}",
    status_code=status.HTTP_200_OK,
    tags=["Playbooks"],
    summary="Elimina un blocco specifico di un playbook",
)(playbooks.delete_block)
