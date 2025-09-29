from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.tag_controller import TagController
from app.Schemas.tag import TagRead, TagCreate, TagUpdate, TagAdminRead
from app.Router.auth import require_roles
from app.Router.dependencies import get_current_user

# ------------------------------------------------------------------------------
# Istanze Controller (stateless)
# ------------------------------------------------------------------------------
tags = TagController()

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------
# Rotte Admin
# ------------------------------------------------------------------------------
router.get(
    "/admin/tags",
    response_model=List[TagAdminRead],
    tags=["Tags", "Admin"],
    summary="[Admin] Lista tutti i tag di tutti gli account",
    dependencies=[Depends(require_roles(["admin"]))],
)(tags.list_all_tags_for_admin)

# ------------------------------------------------------------------------------
# Rotte Utente Autenticato (/me)
# ------------------------------------------------------------------------------
router.get(
    "/me/tags",
    response_model=List[TagRead],
    tags=["Tags"],
    summary="Lista i miei tag",
    dependencies=[Depends(get_current_user)],
)(tags.list_my_tags)

router.post(
    "/me/tags",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Tags"],
    summary="Crea un nuovo tag",
    dependencies=[Depends(get_current_user)],
)(tags.create_tag)

# ------------------------------------------------------------------------------
# Rotte per ID specifico (con controllo di ownership)
# ------------------------------------------------------------------------------
router.get(
    "/tags/{tag_id}",
    response_model=TagRead,
    tags=["Tags"],
    summary="Recupera un tag per ID",
)(tags.get_tag)

router.put(
    "/tags/{tag_id}",
    response_model=TagRead,
    tags=["Tags"],
    summary="Aggiorna un tag per ID",
)(tags.update_tag)

router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_200_OK,
    tags=["Tags"],
    summary="Elimina un tag per ID",
)(tags.delete_tag)