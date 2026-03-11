import functools
import inspect
from typing import Any, Callable, Concatenate, Optional, ParamSpec, TypeVar, overload

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails
from functions.utils.client import NotesClient

from functions.utils.types import ErrorResponse, Response
from ixoncdkingress.function.context import FunctionContext as CbcContext

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T", bound=BaseModel)


def parse_arguments(
    parse_func: Callable[..., T],
) -> Callable[
    [Callable[[CbcContext, T], R | ErrorResponse[list[ErrorDetails]]]],
    Callable[Concatenate[CbcContext, P], R | ErrorResponse[list[ErrorDetails]]],
]:
    """ "
    Takes the given kwargs of the function (except for the CbcContext) and parses them into a
    pydantic model and adds this to the new function by giving a kwarg `model` with the new pydantic
    model. Can also be used with a normal function rather than a pydantic model.

    Example:
    In order to typecheck this:
    ```python
    def add(context: CbcContext, note_id: str, text: str):
    ```

    We can use this:
    ```python
    @parse_arguments(NoteEdit)
    def add(context: CbcContext, model: NoteEdit):
        assert model.note_id and model.text
    ```

    Which actually works like this:
    ```python
    @parse_arguments(lambda note_id, text: NoteEdit(note_id=note_id, text=text))
    def add(context: CbcContext, model: NoteEdit):
        assert model.note_id and model.text
    ```
    """

    def decorator(
        func: Callable[[CbcContext, T], R | ErrorResponse[list[ErrorDetails]]],
    ) -> Callable[Concatenate[CbcContext, P], R | ErrorResponse[list[ErrorDetails]]]:
        def wrapper(
            context: CbcContext, /, *_: P.args, **func_args: P.kwargs
        ) -> R | ErrorResponse[list[ErrorDetails]]:
            try:
                return func(context, parse_func(**func_args))
            except ValidationError as e:
                return ErrorResponse(data=e.errors(), message="Exception parsing input")

        return wrapper

    return decorator


def json_response(func: Callable[P, Response[T]]) -> Callable[P, dict[str, Any]]:
    """
    Ensures that a function that returns a pydantic `Response` object is turned into a JSON
    serializable object.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        return func(*args, **kwargs).model_dump(mode="json", by_alias=True)

    return wrapper


@overload
def notes_endpoint(
    parse_func: None = None,
) -> Callable[
    [Callable[Concatenate[CbcContext, NotesClient, P], Response[Any]]],
    Callable[Concatenate[CbcContext, P], dict[str, Any]],
]: ...


@overload
def notes_endpoint(
    parse_func: Callable[..., T],
) -> Callable[
    [Callable[[CbcContext, NotesClient, T], Response[Any]]],
    Callable[Concatenate[CbcContext, P], dict[str, Any]],
]: ...


def notes_endpoint(
    parse_func: Callable[..., T] | None = None,
) -> Callable[
    [Callable[..., Response[Any]]],
    Callable[Concatenate[CbcContext, P], dict[str, Any]],
]:
    """
    Merges the functionality of `json_response`, `parse_arguments` and injects the notes client
    into the given function. When a parse function is given the kwargs `notes_client` and `model`
    will both be set. Without a parse function only the `notes_client` is set.

    Example:
    ```python
    @notes_endpoint(NoteAdd)
    def add(context: CbcContext, notes_client: NotesClient, model: NoteAdd):
    ````
    """

    def decorator(
        func: Callable[..., Response[Any]],
    ) -> Callable[Concatenate[CbcContext, P], dict[str, Any]]:
        @functools.wraps(func)
        def wrapper(context: CbcContext, /, *args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
            try:
                if parse_func:
                    return json_response(parse_arguments(parse_func)(NotesClient.inject(func)))(
                        context, *args, **kwargs
                    )
                else:
                    return json_response(
                        (NotesClient.inject(func)),
                    )(context, *args, **kwargs)
            except BaseException as e:
                return ErrorResponse(data=str(e)).model_dump(by_alias=True)

        try:
            wrapper.__signature__ = inspect.signature(func)
        except (ValueError, TypeError):
            pass

        return wrapper

    return decorator


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
