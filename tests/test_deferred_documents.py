"""Metadata factories, custom composition, and typed deferred roundtrips."""

import json

import pytest
from pydantic import (
    BaseModel,
    ValidationError,
    create_model,  # pyright: ignore[reportUnknownVariableType]
)
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds, WallClock

import base_pydantic_schemas as eager
import base_pydantic_schemas._factories as factories  # pyright: ignore[reportPrivateUsage]
from base_pydantic_schemas import deferred
from tests.testing_types import (
    CompletionRatio,
    ProfileVersion,
    TemperatureCelsius,
    UserId,
)

TIMESTAMP_BASES: list[tuple[type[BaseModel], type[BaseModel], type[int], int]] = [
    (
        deferred.UnixNanosecondTimestampedMixin,
        eager.UnixNanosecondTimestampedMixin,
        Nanoseconds,
        1,
    ),
    (
        deferred.UnixMicrosecondTimestampedMixin,
        eager.UnixMicrosecondTimestampedMixin,
        Microseconds,
        1_000,
    ),
    (
        deferred.UnixMillisecondTimestampedMixin,
        eager.UnixMillisecondTimestampedMixin,
        Milliseconds,
        1_000_000,
    ),
    (deferred.BaseDocument, eager.BaseDocument, Microseconds, 1_000),
]


@pytest.mark.parametrize(("base", "eager_base", "unit", "divisor"), TIMESTAMP_BASES)
def test_timestamp_factories_remain_typed_independent_and_lazy(
    monkeypatch: pytest.MonkeyPatch,
    base: type[BaseModel],
    eager_base: type[BaseModel],
    unit: type[int],
    divisor: int,
) -> None:
    timestamps = iter(
        [
            1_700_000_000_100_000_000,
            1_700_000_000_200_000_000,
            1_700_000_000_300_000_000,
            1_700_000_000_400_000_000,
        ]
    )
    calls: list[int] = []

    def next_timestamp() -> int:
        value = next(timestamps)
        calls.append(value)
        return value

    clock = WallClock(
        preferred_time_unit_type=Microseconds, unix_nanosecond_factory=next_timestamp
    )
    monkeypatch.setattr(factories, "_default_wall_clock", clock)
    child = create_model("TimestampChild", __base__=base)
    assert calls == []
    child.model_rebuild(force=True)
    assert calls == []
    first = child()
    second = child()
    assert len(calls) == 4
    assert first.model_dump()["created_at"] == unit(calls[0] // divisor)
    assert first.model_dump()["updated_at"] == unit(calls[1] // divisor)
    assert second.model_dump()["created_at"] == unit(calls[2] // divisor)
    assert second.model_dump()["updated_at"] == unit(calls[3] // divisor)
    for name in ("created_at", "updated_at"):
        assert isinstance(getattr(first, name), unit)
        assert (
            child.model_fields[name].default_factory
            is eager_base.model_fields[name].default_factory
        )


def test_custom_document_composes_deferred_mixins_and_preserves_metadata() -> None:
    class CustomDocument(
        deferred.UnixMillisecondTimestampedMixin,
        deferred.VersionedMixin,
        deferred.PersistentDocument,
    ):
        quantity: int

    assert not CustomDocument.__pydantic_complete__
    document = CustomDocument(quantity=3)
    assert isinstance(document.created_at, Milliseconds)
    assert isinstance(document.updated_at, Milliseconds)
    assert document.schema_version == deferred.SchemaVersion("1")
    original_updated_at = document.updated_at
    document.quantity = 4
    assert document.updated_at == original_updated_at
    document.schema_version = deferred.SchemaVersion("2")
    assert isinstance(document.schema_version, eager.SchemaVersion)
    with pytest.raises(ValidationError):
        CustomDocument.model_validate({"quantity": "3"})


def test_base_document_has_deferred_semantic_parents_and_no_auto_update() -> None:
    class Document(deferred.BaseDocument):
        quantity: int

    for base in (
        deferred.UnixMicrosecondTimestampedMixin,
        deferred.VersionedMixin,
        deferred.PersistentDocument,
        eager.BaseDocument,
    ):
        assert issubclass(Document, base)
    document = Document(quantity=1)
    assert isinstance(document.created_at, Microseconds)
    assert isinstance(document.updated_at, Microseconds)
    assert isinstance(document.schema_version, eager.SchemaVersion)
    assert document.schema_version == "1"
    previous = document.updated_at
    document.quantity = 2
    assert document.updated_at == previous


def test_nested_python_and_json_roundtrips_preserve_typed_values() -> None:
    class Measurement(deferred.ImmutableDTO):
        user_id: UserId
        revision: ProfileVersion
        temperature: TemperatureCelsius
        ratio: CompletionRatio

    class Document(deferred.BaseDocument):
        measurement: Measurement

    class Envelope(deferred.MutableDTO):
        document: Document

    payload: dict[str, object] = {
        "document": {
            "created_at": 1_700_000_000_123_456,
            "updated_at": 1_700_000_000_654_321,
            "schema_version": "7",
            "measurement": {
                "user_id": "user_1",
                "revision": 3,
                "temperature": 24.5,
                "ratio": 0.75,
            },
        }
    }
    envelope = Envelope.model_validate(payload)
    assert envelope.model_dump(mode="json") == payload
    assert json.loads(envelope.model_dump_json()) == payload
    restored_models = (
        Envelope.model_validate(envelope.model_dump()),
        Envelope.model_validate(envelope.model_dump(mode="json")),
        Envelope.model_validate_json(envelope.model_dump_json()),
    )
    for restored in restored_models:
        measurement = restored.document.measurement
        assert restored == envelope
        assert isinstance(restored.document.created_at, Microseconds)
        assert isinstance(restored.document.updated_at, Microseconds)
        assert isinstance(restored.document.schema_version, eager.SchemaVersion)
        assert isinstance(measurement.user_id, UserId)
        assert isinstance(measurement.revision, ProfileVersion)
        assert isinstance(measurement.temperature, TemperatureCelsius)
        assert isinstance(measurement.ratio, CompletionRatio)
