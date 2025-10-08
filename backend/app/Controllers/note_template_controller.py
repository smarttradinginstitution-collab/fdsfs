from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.Services.note_template_service import NoteTemplateService
from app.Schemas.note_template import (
    NoteTemplateRead,
    NoteTemplateCreate,
    NoteTemplateUpdate,
)
from app.Schemas.notebook import NoteRead
from app.Router.dependencies import get_current_user, CurrentUser

router = APIRouter(
    prefix="/note-templates",
    tags=["Note Templates"],
    dependencies=[Depends(get_current_user)],
)

note_association_router = APIRouter(
    tags=["Notes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[NoteTemplateRead])
async def list_my_templates(
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """List all note templates for the current user."""
    return await service.get_all_templates(user_id=current_user.id)


@router.post("/", response_model=NoteTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_in: NoteTemplateCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """Create a new note template."""
    return await service.create_template(template_in=template_in, user_id=current_user.id)


@router.get("/{template_id}", response_model=NoteTemplateRead)
async def get_template(
    template_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """Get a specific note template by its ID."""
    return await service.get_template(template_id=template_id, user_id=current_user.id)


@router.put("/{template_id}", response_model=NoteTemplateRead)
async def update_template(
    template_id: UUID,
    template_in: NoteTemplateUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """Update a note template."""
    return await service.update_template(
        template_id=template_id, template_in=template_in, user_id=current_user.id
    )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """Delete a note template."""
    await service.delete_template(template_id=template_id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Association endpoints ---

@note_association_router.post("/notes/{note_id}/templates/{template_id}", response_model=NoteRead)
async def add_template_to_note(
    note_id: UUID,
    template_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """Associate a note template with a note."""
    return await service.add_template_to_note(
        note_id=note_id, template_id=template_id, user_id=current_user.id
    )


@note_association_router.delete("/notes/{note_id}/templates/{template_id}", response_model=NoteRead)
async def remove_template_from_note(
    note_id: UUID,
    template_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: NoteTemplateService = Depends(),
):
    """Disassociate a note template from a note."""
    return await service.remove_template_from_note(
        note_id=note_id, template_id=template_id, user_id=current_user.id
    )