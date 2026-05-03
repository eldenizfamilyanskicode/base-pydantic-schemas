from __future__ import annotations

import pytest
from pydantic import ValidationError

from base_pydantic_schemas import SchemaVersion
from base_pydantic_schemas._base_schema import BaseSchema
from base_pydantic_schemas.mixins.versioned import (
    DEFAULT_SCHEMA_VERSION,
    VersionedMixin,
)
from tests.testing_types import (
    ExplicitVersionDocument,
    MicrosecondAuditDocument,
    UserId,
)


def test_default_schema_version_is_typed_string() -> None:
    assert DEFAULT_SCHEMA_VERSION == SchemaVersion("1")
    assert isinstance(DEFAULT_SCHEMA_VERSION, SchemaVersion)


def test_versioned_mixin_adds_schema_version_field() -> None:
    document: MicrosecondAuditDocument = MicrosecondAuditDocument(
        user_id=UserId("user_marty_mcfly"),
    )

    assert document.schema_version == SchemaVersion("1")
    assert isinstance(document.schema_version, SchemaVersion)

    payload: dict[str, object] = document.model_dump(mode="json")

    assert payload["schema_version"] == "1"


def test_schema_version_can_be_provided_at_validation_boundary() -> None:
    payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456,
        "updated_at": 1_700_000_000_123_457,
        "schema_version": "5",
        "user_id": "user_marty_mcfly",
        "retry_count": 2,
    }

    document: MicrosecondAuditDocument = MicrosecondAuditDocument.model_validate(
        payload,
    )

    assert document.schema_version == SchemaVersion("5")
    assert isinstance(document.schema_version, SchemaVersion)


def test_schema_version_can_be_provided_at_construction_boundary() -> None:
    document: ExplicitVersionDocument = ExplicitVersionDocument(
        user_id=UserId("user_marty_mcfly"),
        schema_version=SchemaVersion("2"),
    )

    assert document.schema_version == SchemaVersion("2")
    assert isinstance(document.schema_version, SchemaVersion)


def test_versioned_mixin_is_base_schema_subclass() -> None:
    assert issubclass(VersionedMixin, BaseSchema)


def test_versioned_mixin_field_description_is_exposed() -> None:
    schema_version_field = ExplicitVersionDocument.model_fields["schema_version"]

    assert schema_version_field.description == (
        "Persistence schema version. This is not the package version or "
        "application release version."
    )


def test_schema_version_rejects_non_string_values() -> None:
    payload: dict[str, object] = {
        "schema_version": 2,
        "user_id": "user_marty_mcfly",
    }

    with pytest.raises(ValidationError):
        ExplicitVersionDocument.model_validate(payload)
