from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from tests.runtime_boundary import assign_runtime_value
from tests.testing_types import (
    CompletionRatio,
    ImmutableMeasurementDTO,
    MeasurementDocument,
    MutableMeasurementDTO,
    TemperatureCelsius,
)


def test_mutable_dto_restores_typed_floats_and_serializes_plain_values() -> None:
    payload: dict[str, object] = {
        "temperature_celsius": 21.5,
        "completion_ratio": 0.75,
    }

    measurement: MutableMeasurementDTO = MutableMeasurementDTO.model_validate(
        payload,
    )

    assert type(measurement.temperature_celsius) is TemperatureCelsius
    assert type(measurement.completion_ratio) is CompletionRatio
    assert measurement.model_dump(mode="json") == payload


def test_mutable_dto_validates_typed_float_assignment() -> None:
    measurement: MutableMeasurementDTO = MutableMeasurementDTO.model_validate(
        {
            "temperature_celsius": 21.5,
            "completion_ratio": 0.75,
        },
    )

    assign_runtime_value(
        target_object=measurement,
        field_name="temperature_celsius",
        field_value=-3.5,
    )
    assign_runtime_value(
        target_object=measurement,
        field_name="completion_ratio",
        field_value=0.8,
    )

    assert measurement.temperature_celsius == TemperatureCelsius(-3.5)
    assert measurement.completion_ratio == CompletionRatio(0.8)
    assert type(measurement.temperature_celsius) is TemperatureCelsius
    assert type(measurement.completion_ratio) is CompletionRatio

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=measurement,
            field_name="completion_ratio",
            field_value=1.1,
        )


@pytest.mark.parametrize(
    "invalid_temperature",
    [21, math.nan, math.inf, -math.inf],
)
def test_typed_float_field_rejects_invalid_or_non_finite_values(
    invalid_temperature: object,
) -> None:
    payload: dict[str, object] = {
        "temperature_celsius": invalid_temperature,
        "completion_ratio": 0.75,
    }

    with pytest.raises(ValidationError):
        MutableMeasurementDTO.model_validate(payload)


def test_immutable_dto_preserves_typed_float_fields() -> None:
    payload: dict[str, object] = {
        "temperature_celsius": 36.5,
        "completion_ratio": 1.0,
    }

    measurement: ImmutableMeasurementDTO = ImmutableMeasurementDTO.model_validate(
        payload,
    )

    assert type(measurement.temperature_celsius) is TemperatureCelsius
    assert type(measurement.completion_ratio) is CompletionRatio
    assert measurement.model_dump(mode="json") == payload

    with pytest.raises(ValidationError):
        measurement.completion_ratio = CompletionRatio(0.5)


def test_document_roundtrip_restores_typed_float_fields() -> None:
    payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456,
        "updated_at": 1_700_000_000_654_321,
        "schema_version": "1",
        "temperature_celsius": -12.25,
        "completion_ratio": 0.25,
    }

    document: MeasurementDocument = MeasurementDocument.model_validate(payload)
    restored_payload: dict[str, object] = document.model_dump(mode="json")

    assert restored_payload == payload
    assert type(document.temperature_celsius) is TemperatureCelsius
    assert type(document.completion_ratio) is CompletionRatio


def test_constrained_typed_float_exposes_json_schema_range() -> None:
    model_schema: dict[str, object] = MutableMeasurementDTO.model_json_schema()
    properties: object = model_schema["properties"]

    assert isinstance(properties, dict)
    assert properties["completion_ratio"] == {
        "maximum": 1.0,
        "minimum": 0.0,
        "title": "Completion Ratio",
        "type": "number",
    }
