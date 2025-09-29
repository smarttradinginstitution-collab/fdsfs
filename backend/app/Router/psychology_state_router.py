from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.psychology_state_controller import PsychologyStateController
from app.Schemas.psychology_state import PsychologyStateRead, PsychologyStateCreate, PsychologyStateUpdate, PsychologyStateAdminRead
from app.Router.auth import require_roles
from app.Router.dependencies import get_current_user

# ------------------------------------------------------------------------------
# Istanze Controller (stateless)
# ------------------------------------------------------------------------------
psychology_states = PsychologyStateController()

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------
# Rotte Admin
# ------------------------------------------------------------------------------
router.get(
    "/admin/psychology-states",
    response_model=List[PsychologyStateAdminRead],
    tags=["PsychologyStates", "Admin"],
    summary="[Admin] Lista tutti gli stati psicologici di tutti gli account",
    dependencies=[Depends(require_roles(["admin"]))],
)(psychology_states.list_all_psychology_states_for_admin)

# ------------------------------------------------------------------------------
# Rotte Utente Autenticato (/me)
# ------------------------------------------------------------------------------
router.get(
    "/me/psychology-states",
    response_model=List[PsychologyStateRead],
    tags=["PsychologyStates"],
    summary="Lista i miei stati psicologici",
    dependencies=[Depends(get_current_user)],
)(psychology_states.list_my_psychology_states)

router.post(
    "/me/psychology-states",
    response_model=PsychologyStateRead,
    status_code=status.HTTP_201_CREATED,
    tags=["PsychologyStates"],
    summary="Crea un nuovo stato psicologico",
    dependencies=[Depends(get_current_user)],
)(psychology_states.create_psychology_state)

# ------------------------------------------------------------------------------
# Rotte per ID specifico (con controllo di ownership)
# ------------------------------------------------------------------------------
router.get(
    "/psychology-states/{psychology_state_id}",
    response_model=PsychologyStateRead,
    tags=["PsychologyStates"],
    summary="Recupera uno stato psicologico per ID",
)(psychology_states.get_psychology_state)

router.put(
    "/psychology-states/{psychology_state_id}",
    response_model=PsychologyStateRead,
    tags=["PsychologyStates"],
    summary="Aggiorna uno stato psicologico per ID",
)(psychology_states.update_psychology_state)

router.delete(
    "/psychology-states/{psychology_state_id}",
    status_code=status.HTTP_200_OK,
    tags=["PsychologyStates"],
    summary="Elimina uno stato psicologico per ID",
)(psychology_states.delete_psychology_state)