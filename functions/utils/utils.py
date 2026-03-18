import functools
import inspect
from typing import Any, Callable, Concatenate, Optional, ParamSpec, TypeVar

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails
from functions.utils.client import NotesClient

from functions.utils.types import ErrorResponse, Response
from ixoncdkingress.function.context import FunctionContext as CbcContext

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T", bound=BaseModel)


def json_response(func: Callable[P, Response[T]]) -> Callable[P, dict[str, Any]]:
    """
    Ensures that a function that returns a pydantic `Response` object is turned into a JSON
    serializable object.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        return func(*args, **kwargs).model_dump(mode="json", by_alias=True)

    return wrapper


def notes_endpoint(
    func: Callable[Concatenate[CbcContext, NotesClient, P], Response[Any]],
) -> Callable[Concatenate[CbcContext, P], dict[str, Any]]:
    """
    Merges the functionality of `json_response`, pydantic parsing and injects the notes client
    into the given function. It will set `notes_client` and parse any pydantic models.

    Example:
    ```python
    @notes_endpoint
    def add(context: CbcContext, notes_client: NotesClient, model: NoteAdd):
    ````
    """

    @functools.wraps(func)
    def wrapper(
        context: CbcContext, /, *args: P.args, **kwargs: P.kwargs
    ) -> dict[str, Any]:
        try:
            signature = inspect.signature(func)
            pydantic_params = {
                name: param.annotation
                for name, param in signature.parameters.items()
                if (
                    isinstance(param.annotation, type)
                    and issubclass(param.annotation, BaseModel)
                )
            }
            try:
                for key, value in kwargs.items():
                    if (
                        key in pydantic_params
                        and not isinstance(value, pydantic_params[key])
                        and isinstance(value, dict)
                    ):
                        kwargs[key] = pydantic_params[key](**value)
            except ValidationError as e:
                return ErrorResponse[list[ErrorDetails]](
                    message="Exception parsing input", data=e.errors()
                ).model_dump(mode="json", by_alias=True)

            return json_response(NotesClient.inject(func))(context, *args, **kwargs)

        except BaseException as e:
            return ErrorResponse(data=str(e)).model_dump(by_alias=True)

    return wrapper


def permission_check(
    context: CbcContext, notes_client: NotesClient, note_id: Optional[str] = None
) -> bool:
    """
    Checks whether or not a user is allowed to edit/remove notes or a specific note when given.
    """
    if (
        (context.asset or context.agent) is not None
        and context.agent_or_asset.permissions is not None
        and (
            "MANAGE_AGENT" in context.agent_or_asset.permissions
            or "COMPANY_ADMIN" in context.agent_or_asset.permissions
        )
    ):
        return True

    if note_id and (note := notes_client.find_one_note(note_id)):
        if context.user and (
            context.user.public_id == note.user  # Old messages
            or context.user.public_id == note.author_id  # New messages
        ):
            return True

    return False
