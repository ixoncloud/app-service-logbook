from datetime import datetime
from typing import Iterable
from functions.utils.client import NotesClient

from functions.utils.types import (
    ErrorResponse,
    NoteAdd,
    NoteBasic,
    NoteEdit,
    NoteRemove,
    SuccessResponse,
    Note,
)
from functions.utils.utils import notes_endpoint, permission_check
from ixoncdkingress.function.context import FunctionContext
from ixoncdkingress.types import AppDescription

AppDescription(
    short_name="service-logbook",
    description=(
        "The service logbook allows you to record service operations. "
        "You can make notes on anything relevant to the operation of "
        "your machine. Think about configuration changes, maintenance "
        "work carried out and problems encountered. This gives you and "
        "your colleagues a central overview of all service interactions "
        "on your machine.\n"
        "Any user can add notes, edit and delete their own notes. "
        "Platform administrators and users with Manage Devices permissions "
        "can also edit and delete other users' notes. If a note is edited "
        "by someone other than the creator of the note, the last editor name "
        "is stored in the editor name field. \n"
        "You can get all the service logbook notes without any restrictions. "
        "In order to add new notes, edit existing notes and remove notes, "
        "you need human permission. "
    ),
)


@FunctionContext.expose(
    is_agentic=True, requires_human_permission=True, exclude_param_types={NotesClient}
)
@notes_endpoint
def add(
    _: FunctionContext,
    notes_client: NotesClient,
    model: NoteAdd,
) -> ErrorResponse[None] | SuccessResponse[Note]:
    """Add a new note to the database."""

    note = notes_client.add(model)

    if isinstance(note, ErrorResponse):
        return note

    return SuccessResponse(message=f"Added Note #{note.id}", data=note)


@FunctionContext.expose
@notes_endpoint
def get(
    _: FunctionContext,
    notes_client: NotesClient,
) -> SuccessResponse[Iterable[Note]]:
    return SuccessResponse(data=notes_client.get())


@FunctionContext.expose(
    is_agentic=True, requires_human_permission=False, exclude_param_types={NotesClient}
)
@notes_endpoint
def get_all_notes(
    _: FunctionContext,
    notes_client: NotesClient,
) -> SuccessResponse[Iterable[NoteBasic]]:
    """Add all the notes in the database."""
    return SuccessResponse(
        data=[
            NoteBasic(
                _id=note.id,
                text=note.text,
                created_on=datetime.fromtimestamp(note.created_on / 1000),
                author_name=note.author_name,
                editor_name=note.editor_name,
                updated_on=datetime.fromtimestamp(note.updated_on / 1000)
                if note.updated_on
                else None,
                subject=note.subject,
                category=note.category,
            )
            for note in notes_client.get()
        ]
    )


@FunctionContext.expose(
    is_agentic=True, requires_human_permission=True, exclude_param_types={NotesClient}
)
@notes_endpoint
def edit(
    context: FunctionContext,
    notes_client: NotesClient,
    model: NoteEdit,
) -> ErrorResponse[None] | SuccessResponse[Note]:
    """Edit a note in the database."""
    if context.user is None or not permission_check(
        context, notes_client, model.note_id
    ):
        return ErrorResponse(
            message="You do not have the rights to perform this action"
        )

    note = notes_client.edit(model)

    if isinstance(note, ErrorResponse):
        return note

    return SuccessResponse(message=f"Updated Note #{note.id}", data=note)


@FunctionContext.expose(
    is_agentic=True, requires_human_permission=True, exclude_param_types={NotesClient}
)
@notes_endpoint
def remove(
    context: FunctionContext,
    notes_client: NotesClient,
    model: NoteRemove,
) -> ErrorResponse[None] | SuccessResponse[None]:
    """Remove a note from the database."""
    if context.user is None or not permission_check(
        context, notes_client, model.note_id
    ):
        return ErrorResponse(
            message="You do not have the rights to perform this action"
        )

    error = notes_client.remove(model.note_id)

    if error is not None:
        return error

    return SuccessResponse(message="Removed Note")
