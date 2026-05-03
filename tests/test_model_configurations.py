from __future__ import annotations

from pydantic import BaseModel

from base_pydantic_schemas import (
    ArbitraryImmutableDTO,
    ArbitraryMutableDTO,
    BaseDocument,
    BaseSchema,
    ImmutableDTO,
    MutableDTO,
    PersistentDocument,
)
from tests.testing_types import PlainBaseSchemaExample


def assert_model_configuration_contains(
    model_type: type[BaseModel],
    expected_settings: tuple[tuple[str, object], ...],
) -> None:
    for setting_name, expected_value in expected_settings:
        actual_value: object = model_type.model_config.get(setting_name)
        assert actual_value == expected_value


def test_base_schema_does_not_define_package_level_model_config() -> None:
    assert BaseSchema.model_config == {}

    payload: dict[str, object] = {
        "quantity": "10",
        "unexpected_value": "ignored_by_default_pydantic_policy",
    }

    schema_instance: PlainBaseSchemaExample = PlainBaseSchemaExample.model_validate(
        payload,
    )

    assert schema_instance.quantity == 10
    assert schema_instance.model_dump() == {"quantity": 10}


def test_mutable_dto_model_configuration_is_strict_and_mutable() -> None:
    expected_settings: tuple[tuple[str, object], ...] = (
        ("from_attributes", True),
        ("populate_by_name", True),
        ("extra", "forbid"),
        ("validate_assignment", True),
        ("validate_default", True),
        ("strict", True),
    )

    assert_model_configuration_contains(
        model_type=MutableDTO,
        expected_settings=expected_settings,
    )


def test_immutable_dto_model_configuration_is_strict_and_frozen() -> None:
    expected_settings: tuple[tuple[str, object], ...] = (
        ("from_attributes", True),
        ("populate_by_name", True),
        ("extra", "forbid"),
        ("frozen", True),
        ("validate_default", True),
        ("strict", True),
    )

    assert_model_configuration_contains(
        model_type=ImmutableDTO,
        expected_settings=expected_settings,
    )


def test_arbitrary_mutable_dto_model_configuration_allows_runtime_objects() -> None:
    expected_settings: tuple[tuple[str, object], ...] = (
        ("from_attributes", True),
        ("populate_by_name", True),
        ("extra", "forbid"),
        ("arbitrary_types_allowed", True),
        ("validate_assignment", True),
        ("validate_default", True),
        ("frozen", False),
        ("strict", True),
    )

    assert_model_configuration_contains(
        model_type=ArbitraryMutableDTO,
        expected_settings=expected_settings,
    )


def test_arbitrary_immutable_dto_model_configuration_is_frozen() -> None:
    expected_settings: tuple[tuple[str, object], ...] = (
        ("from_attributes", True),
        ("populate_by_name", True),
        ("extra", "forbid"),
        ("arbitrary_types_allowed", True),
        ("frozen", True),
        ("validate_default", True),
        ("strict", True),
    )

    assert_model_configuration_contains(
        model_type=ArbitraryImmutableDTO,
        expected_settings=expected_settings,
    )


def test_persistent_document_model_configuration_is_storage_neutral() -> None:
    expected_settings: tuple[tuple[str, object], ...] = (
        ("from_attributes", True),
        ("populate_by_name", True),
        ("extra", "forbid"),
        ("validate_assignment", True),
        ("validate_default", True),
        ("strict", True),
    )

    assert_model_configuration_contains(
        model_type=PersistentDocument,
        expected_settings=expected_settings,
    )


def test_base_document_inherits_persistent_document_configuration() -> None:
    expected_settings: tuple[tuple[str, object], ...] = (
        ("from_attributes", True),
        ("populate_by_name", True),
        ("extra", "forbid"),
        ("validate_assignment", True),
        ("validate_default", True),
        ("strict", True),
    )

    assert issubclass(BaseDocument, PersistentDocument)

    assert_model_configuration_contains(
        model_type=BaseDocument,
        expected_settings=expected_settings,
    )
