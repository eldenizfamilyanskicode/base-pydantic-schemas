"""Deferred schemas retain the validation policies of their eager counterparts."""

from collections.abc import Callable

import pytest
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    create_model,  # pyright: ignore[reportUnknownVariableType]
)

from base_pydantic_schemas import deferred
from tests.runtime_boundary import assign_runtime_value
from tests.testing_types import RuntimeDatabaseSession, SourceName

POLICY_BASES: list[type[BaseModel]] = [
    deferred.MutableDTO,
    deferred.ImmutableDTO,
    deferred.ArbitraryMutableDTO,
    deferred.ArbitraryImmutableDTO,
    deferred.PersistentDocument,
    deferred.BaseDocument,
]


@pytest.mark.parametrize("base", POLICY_BASES)
@pytest.mark.parametrize(
    ("field_type", "valid", "invalid"),
    [
        (int, 3, "3"),
        (int, 3, True),
        (int, 3, 3.5),
        (str, "three", 3),
        (bool, True, 1),
        (float, 3.5, "3.5"),
    ],
)
def test_strict_primitives_and_extra_fields(
    base: type[BaseModel], field_type: type[object], valid: object, invalid: object
) -> None:
    child = create_model("StrictChild", __base__=base, value=(field_type, ...))
    with pytest.raises(ValidationError):
        child.model_validate({"value": invalid})
    with pytest.raises(ValidationError):
        child.model_validate({"value": valid, "unexpected": True})
    assert child.model_validate({"value": valid}).model_dump()["value"] == valid


@pytest.mark.parametrize("base", POLICY_BASES)
def test_defaults_are_validated(base: type[BaseModel]) -> None:
    child = create_model("InvalidDefault", __base__=base, quantity=(int, "3"))
    with pytest.raises(ValidationError):
        child()


@pytest.mark.parametrize("base", POLICY_BASES)
def test_aliases_and_attribute_population(base: type[BaseModel]) -> None:
    child = create_model(
        "AliasedChild", __base__=base, quantity=(int, Field(alias="external_quantity"))
    )

    class ExternalRecord:
        external_quantity: int = 3

    for payload in ({"quantity": 3}, {"external_quantity": 3}, ExternalRecord()):
        instance = child.model_validate(payload)
        assert instance.model_dump()["quantity"] == 3
        assert instance.model_dump(by_alias=True)["external_quantity"] == 3


@pytest.mark.parametrize("base", POLICY_BASES)
def test_assignment_validation_and_frozen_policy(base: type[BaseModel]) -> None:
    child = create_model("AssignmentChild", __base__=base, quantity=(int, ...))
    instance = child.model_validate({"quantity": 3})
    if base.model_config.get("frozen"):
        with pytest.raises(ValidationError, match="frozen_instance"):
            assign_runtime_value(instance, "quantity", 4)
    else:
        assign_runtime_value(instance, "quantity", 4)
        assert instance.model_dump()["quantity"] == 4
    with pytest.raises(ValidationError):
        assign_runtime_value(instance, "quantity", "5")


def test_base_schema_remains_policy_neutral_except_for_deferred_build() -> None:
    class PlainSchema(deferred.BaseSchema):
        quantity: int

    assert PlainSchema.model_config == {"defer_build": True}
    assert PlainSchema.model_validate({"quantity": "3", "ignored": True}).quantity == 3


def test_arbitrary_runtime_objects_and_callbacks_preserve_identity() -> None:
    class MutableBoundary(deferred.ArbitraryMutableDTO):
        session: RuntimeDatabaseSession
        callback: Callable[[], str]

    class ImmutableBoundary(deferred.ArbitraryImmutableDTO):
        session: RuntimeDatabaseSession
        callback: Callable[[], str]

    def callback() -> str:
        return "completed"

    session = RuntimeDatabaseSession(SourceName("initial"))
    mutable = MutableBoundary(session=session, callback=callback)
    immutable = ImmutableBoundary(session=session, callback=callback)
    for instance in (mutable, immutable):
        assert instance.session is session
        assert instance.callback is callback
        assert instance.callback() == "completed"
        with pytest.raises(ValidationError):
            type(instance).model_validate({"session": object(), "callback": callback})

    replacement = RuntimeDatabaseSession(SourceName("replacement"))
    mutable.session = replacement
    assert mutable.session is replacement
    with pytest.raises(ValidationError):
        assign_runtime_value(mutable, "session", object())
    with pytest.raises(ValidationError):
        assign_runtime_value(mutable, "callback", "not callable")
    with pytest.raises(ValidationError, match="frozen_instance"):
        immutable.session = replacement
