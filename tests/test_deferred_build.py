"""Construction lifecycle and compatibility of the opt-in deferred namespace."""

import subprocess
import sys
import textwrap
from typing import ClassVar

import pytest
from pydantic import (
    BaseModel,
    ConfigDict,
    PydanticSchemaGenerationError,
    create_model,  # pyright: ignore[reportUnknownVariableType]
)
from pydantic_core import SchemaSerializer, SchemaValidator

import base_pydantic_schemas as eager
from base_pydantic_schemas import deferred
from tests.testing_types import RuntimeDatabaseSession

MODEL_PAIRS: list[tuple[type[BaseModel], type[BaseModel]]] = [
    (deferred.BaseSchema, eager.BaseSchema),
    (deferred.MutableDTO, eager.MutableDTO),
    (deferred.ImmutableDTO, eager.ImmutableDTO),
    (deferred.ArbitraryMutableDTO, eager.ArbitraryMutableDTO),
    (deferred.ArbitraryImmutableDTO, eager.ArbitraryImmutableDTO),
    (deferred.PersistentDocument, eager.PersistentDocument),
    (deferred.BaseDocument, eager.BaseDocument),
    (deferred.UnixNanosecondTimestampedMixin, eager.UnixNanosecondTimestampedMixin),
    (deferred.UnixMicrosecondTimestampedMixin, eager.UnixMicrosecondTimestampedMixin),
    (deferred.UnixMillisecondTimestampedMixin, eager.UnixMillisecondTimestampedMixin),
    (deferred.VersionedMixin, eager.VersionedMixin),
]


def test_deferred_public_api_and_schema_version_identity() -> None:
    assert deferred.__all__ == eager.__all__
    assert len(deferred.__all__) == 12
    assert deferred.SchemaVersion is eager.SchemaVersion
    for name in deferred.__all__:
        assert hasattr(deferred, name)


@pytest.mark.parametrize(("deferred_base", "eager_base"), MODEL_PAIRS)
def test_deferred_bases_preserve_inheritance_config_and_fields(
    deferred_base: type[BaseModel], eager_base: type[BaseModel]
) -> None:
    assert deferred_base is not eager_base
    assert issubclass(deferred_base, eager_base)
    assert issubclass(deferred_base, deferred.BaseSchema)
    assert deferred_base.__mro__.index(eager_base) <= deferred_base.__mro__.index(
        eager.BaseSchema
    )
    assert deferred_base.model_config == {
        **eager_base.model_config,
        "defer_build": True,
    }
    assert deferred_base.model_fields.keys() == eager_base.model_fields.keys()
    for name, field in deferred_base.model_fields.items():
        original = eager_base.model_fields[name]
        assert field.annotation is original.annotation
        assert field.default == original.default
        assert field.default_factory is original.default_factory


@pytest.mark.parametrize(("deferred_base", "eager_base"), MODEL_PAIRS)
@pytest.mark.parametrize("first_use", ["construct", "validate", "rebuild"])
def test_fresh_descendants_build_only_when_used(
    deferred_base: type[BaseModel], eager_base: type[BaseModel], first_use: str
) -> None:
    child = create_model("FreshDeferredChild", __base__=deferred_base)
    assert not child.__pydantic_complete__
    assert not isinstance(child.__pydantic_validator__, SchemaValidator)
    assert not isinstance(child.__pydantic_serializer__, SchemaSerializer)

    if first_use == "construct":
        child()
    elif first_use == "validate":
        child.model_validate({})
    else:
        assert child.model_rebuild(force=True) is True

    assert child.__pydantic_complete__
    assert isinstance(child.__pydantic_validator__, SchemaValidator)
    assert isinstance(child.__pydantic_serializer__, SchemaSerializer)
    assert issubclass(child, eager_base)
    validator = child.__pydantic_validator__
    assert child.model_rebuild(force=True) is True
    assert child.__pydantic_validator__ is not validator
    instance = child()
    assert (
        child.model_validate(instance.model_dump()).model_dump()
        == instance.model_dump()
    )


def test_config_inheritance_and_explicit_eager_override() -> None:
    class TitledChild(deferred.MutableDTO):
        model_config: ClassVar[ConfigDict] = ConfigDict(title="Application command")
        quantity: int

    class EagerChild(deferred.MutableDTO):
        model_config: ClassVar[ConfigDict] = ConfigDict(defer_build=False)
        quantity: int

    assert TitledChild.model_config.get("defer_build") is True
    assert TitledChild.model_config.get("strict") is True
    assert not TitledChild.__pydantic_complete__
    assert TitledChild.model_json_schema()["title"] == "Application command"
    assert EagerChild.__pydantic_complete__
    assert isinstance(EagerChild.__pydantic_validator__, SchemaValidator)
    assert isinstance(EagerChild.__pydantic_serializer__, SchemaSerializer)
    assert EagerChild(quantity=3).quantity == 3


def test_invalid_runtime_type_fails_at_deferred_build_instead_of_definition() -> None:
    with pytest.raises(PydanticSchemaGenerationError):

        class InvalidEagerDTO(eager.MutableDTO):
            session: RuntimeDatabaseSession

        _ = InvalidEagerDTO

    class InvalidDeferredDTO(deferred.MutableDTO):
        session: RuntimeDatabaseSession

    assert not InvalidDeferredDTO.__pydantic_complete__
    with pytest.raises(PydanticSchemaGenerationError):
        InvalidDeferredDTO.model_rebuild(force=True)


def test_import_does_not_mutate_eager_models_in_isolated_process() -> None:
    script = textwrap.dedent(
        """
        import base_pydantic_schemas as eager
        from pydantic import BaseModel, create_model
        from pydantic_core import SchemaSerializer, SchemaValidator

        models = [getattr(eager, name) for name in eager.__all__
                  if name != "SchemaVersion"]
        snapshots = [(model, dict(model.model_config),
                      model.__pydantic_validator__, model.__pydantic_serializer__,
                      model.__pydantic_complete__) for model in models]

        import base_pydantic_schemas.deferred as deferred

        for model, config, validator, serializer, complete in snapshots:
            assert model.model_config == config
            assert model.__pydantic_validator__ is validator
            assert model.__pydantic_serializer__ is serializer
            assert model.__pydantic_complete__ is complete is True
            child = create_model("FreshEagerChild", __base__=model)
            assert child.__pydantic_complete__
            assert isinstance(child.__pydantic_validator__, SchemaValidator)
            assert isinstance(child.__pydantic_serializer__, SchemaSerializer)

        for name in deferred.__all__:
            if name == "SchemaVersion":
                continue
            model = getattr(deferred, name)
            assert issubclass(model, BaseModel)
            assert not model.__pydantic_complete__
            assert not isinstance(model.__pydantic_validator__, SchemaValidator)
            assert not isinstance(model.__pydantic_serializer__, SchemaSerializer)
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
