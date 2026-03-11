from ixoncdkingress.cbc.context import FunctionResource
from ixoncdkingress.function.context import FunctionContext
import functions.notes as sut
from tests.conftest import set_time


def test_add_ok(function_context: FunctionContext):
    set_time(174540181.000)
    assert function_context.user

    function_context.user.public_id = "user00000001"
    function_context.user.name = "Test User"

    result = sut.add(function_context, model={"text": "Test Note"})

    assert True is result["success"]

    data = result["data"]

    assert None is data["user"]

    assert "Test Note" == data["text"]
    assert 174540181000 == data["created_on"]
    assert "user00000001" == data["author_id"]
    assert "Test User" == data["author_name"]

    assert None is data["editor_id"]
    assert None is data["editor_name"]
    assert None is data["updated_on"]
    assert None is data["subject"]
    assert None is data["category"]


def test_add_with_category_and_subject(function_context: FunctionContext):
    result = sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    assert True is result["success"]

    data = result["data"]

    assert "Test Subject" == data["subject"]
    assert 0 == data["category"]


def test_get_ok(function_context: FunctionContext):
    sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    sut.add(
        function_context,
        model={
            "text": "Test Note 2",
            "subject": "Test Subject 2",
            "category": 1,
        },
    )

    result = sut.get(function_context)

    assert True is result["success"]

    [note_0, note_1] = result["data"]

    assert "Test Note" == note_0["text"]
    assert "Test Subject" == note_0["subject"]
    assert 0 == note_0["category"]

    assert "Test Note 2" == note_1["text"]
    assert "Test Subject 2" == note_1["subject"]
    assert 1 == note_1["category"]


def test_get_all_notes_ok(function_context: FunctionContext):
    sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    sut.add(
        function_context,
        model={
            "text": "Test Note 2",
            "subject": "Test Subject 2",
            "category": 1,
        },
    )

    result = sut.get_all_notes(function_context)

    assert True is result["success"]

    [note_0, note_1] = result["data"]

    assert "Test Note" == note_0["text"]
    assert "Test Subject" == note_0["subject"]
    assert 0 == note_0["category"]

    assert "Test Note 2" == note_1["text"]
    assert "Test Subject 2" == note_1["subject"]
    assert 1 == note_1["category"]


def test_edit_ok(function_context: FunctionContext):
    set_time(174540182.000)

    result = sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    sut.add(
        function_context,
        model={
            "text": "Test Note 2",
            "subject": "Test Subject 2",
            "category": 1,
        },
    )

    set_time(174540181.000)

    result = sut.edit(
        function_context,
        model={
            "note_id": result["data"]["_id"],
            "text": "Edited Note",
            "subject": "Edited Subject",
            "category": 2,
        },
    )

    assert result["success"]
    result = sut.get(function_context)

    [note_0, note_1] = result["data"]

    assert "Edited Note" == note_0["text"]
    assert "Edited Subject" == note_0["subject"]
    assert 2 == note_0["category"]
    assert 174540182000 == note_0["created_on"]
    assert 174540181000 == note_0["updated_on"]
    assert "user00000000" == note_0["author_id"]
    assert "test_user" == note_0["author_name"]

    assert "user00000000" == note_0["editor_id"]
    assert "test_user" == note_0["editor_name"]

    # Check that the other note wasn't changed
    assert "Test Note 2" == note_1["text"]
    assert "Test Subject 2" == note_1["subject"]
    assert 1 == note_1["category"]
    assert None is note_1["updated_on"]


def test_edit_other_user(
    function_context: FunctionContext,
    user: FunctionResource,
    asset: FunctionResource,
):
    set_time(174540182.000)

    result = sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    set_time(174540181.000)
    user.name = "Editor"
    user.public_id = "user00000001"
    asset.permissions = {"MANAGE_AGENT"}

    result = sut.edit(
        function_context,
        model={
            "note_id": result["data"]["_id"],
            "text": "Edited Note",
            "subject": "Edited Subject",
            "category": 2,
        },
    )

    assert result["success"]
    result = sut.get(function_context)

    [note_0] = result["data"]

    assert "Edited Note" == note_0["text"]
    assert "Edited Subject" == note_0["subject"]
    assert 2 == note_0["category"]
    assert 174540182000 == note_0["created_on"]
    assert 174540181000 == note_0["updated_on"]
    assert "user00000000" == note_0["author_id"]
    assert "test_user" == note_0["author_name"]

    assert "user00000001" == note_0["editor_id"]
    assert "Editor" == note_0["editor_name"]


def test_edit_other_user_no_permission(
    function_context: FunctionContext,
    user: FunctionResource,
    asset: FunctionResource,
):
    set_time(174540182.000)

    result = sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    set_time(174540181.000)
    user.name = "Editor"
    user.public_id = "user00000001"
    asset.permissions = set()

    result = sut.edit(
        function_context,
        model={
            "note_id": result["data"]["_id"],
            "text": "Edited Note",
            "subject": "Edited Subject",
            "category": 2,
        },
    )

    assert not result["success"]
    result = sut.get(function_context)

    [note_0] = result["data"]

    assert "Test Note" == note_0["text"]
    assert "Test Subject" == note_0["subject"]
    assert 0 == note_0["category"]
    assert 174540182000 == note_0["created_on"]
    assert None is note_0["updated_on"]
    assert "user00000000" == note_0["author_id"]
    assert "test_user" == note_0["author_name"]

    assert None is note_0["editor_id"]
    assert None is note_0["editor_name"]


def test_remove_ok(function_context: FunctionContext):
    result = sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    sut.remove(function_context, model={"note_id": result["data"]["_id"]})

    result = sut.get(function_context)

    assert result["success"]
    assert 0 == len(result["data"])


def test_remove_no_permission(
    function_context: FunctionContext,
    user: FunctionResource,
    asset: FunctionResource,
):
    result = sut.add(
        function_context,
        model={
            "text": "Test Note",
            "subject": "Test Subject",
            "category": 0,
        },
    )

    user.public_id = "user00000001"
    user.name = "User"
    asset.permissions = set()

    result = sut.remove(function_context, model={"note_id": result["data"]["_id"]})
    assert not result["success"]

    result = sut.get(function_context)

    assert result["success"]
    assert 1 == len(result["data"])
