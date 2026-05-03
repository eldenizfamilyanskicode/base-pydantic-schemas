from __future__ import annotations

import pytest
from pydantic import ValidationError
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds

from base_pydantic_schemas import SchemaVersion
from tests.runtime_boundary import assign_runtime_value
from tests.testing_types import (
    CityName,
    DisplayName,
    MillisecondAuditDocument,
    NanosecondAuditDocument,
    PlainPersistentUserProfileDocument,
    ProfileVersion,
    RetryCount,
    UserId,
    UserProfileDocument,
    create_user_profile_document,
)


def test_base_document_adds_microsecond_timestamps_and_schema_version() -> None:
    document: UserProfileDocument = create_user_profile_document()

    assert isinstance(document.created_at, Microseconds)
    assert isinstance(document.updated_at, Microseconds)
    assert isinstance(document.schema_version, SchemaVersion)
    assert document.schema_version == SchemaVersion("1")
    assert document.profile_version == ProfileVersion(1)

    payload: dict[str, object] = document.model_dump(mode="json")

    assert isinstance(payload["created_at"], int)
    assert isinstance(payload["updated_at"], int)
    assert payload["schema_version"] == "1"
    assert payload["user_id"] == "user_marty_mcfly"
    assert payload["profile_version"] == 1


def test_base_document_roundtrip_restores_typed_runtime_values() -> None:
    payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456,
        "updated_at": 1_700_000_000_654_321,
        "schema_version": "3",
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "city_name": "NewAmsterdam",
        "profile_version": 9,
    }

    document: UserProfileDocument = UserProfileDocument.model_validate(payload)
    restored_payload: dict[str, object] = document.model_dump(mode="json")

    assert restored_payload == payload
    assert isinstance(document.created_at, Microseconds)
    assert isinstance(document.updated_at, Microseconds)
    assert isinstance(document.schema_version, SchemaVersion)
    assert isinstance(document.user_id, UserId)
    assert isinstance(document.display_name, DisplayName)
    assert isinstance(document.city_name, CityName)
    assert isinstance(document.profile_version, ProfileVersion)


def test_base_document_validates_assignment_and_preserves_typed_values() -> None:
    document: UserProfileDocument = create_user_profile_document()

    assign_runtime_value(
        target_object=document,
        field_name="updated_at",
        field_value=1_700_000_000_777_777,
    )
    assign_runtime_value(
        target_object=document,
        field_name="schema_version",
        field_value="4",
    )
    assign_runtime_value(
        target_object=document,
        field_name="profile_version",
        field_value=10,
    )

    assert document.updated_at == Microseconds(1_700_000_000_777_777)
    assert document.schema_version == SchemaVersion("4")
    assert document.profile_version == ProfileVersion(10)

    assert isinstance(document.updated_at, Microseconds)
    assert isinstance(document.schema_version, SchemaVersion)
    assert isinstance(document.profile_version, ProfileVersion)


def test_base_document_rejects_invalid_assignment_values() -> None:
    document: UserProfileDocument = create_user_profile_document()

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=document,
            field_name="updated_at",
            field_value="1_700_000_000_777_777",
        )

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=document,
            field_name="schema_version",
            field_value=4,
        )

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=document,
            field_name="profile_version",
            field_value=True,
        )

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=document,
            field_name="unexpected_field",
            field_value="not_allowed",
        )


def test_persistent_document_is_storage_neutral_without_default_metadata() -> None:
    document: PlainPersistentUserProfileDocument = PlainPersistentUserProfileDocument(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
    )

    payload: dict[str, object] = document.model_dump(mode="json")

    assert "created_at" not in PlainPersistentUserProfileDocument.model_fields
    assert "updated_at" not in PlainPersistentUserProfileDocument.model_fields
    assert "schema_version" not in PlainPersistentUserProfileDocument.model_fields

    assert payload == {
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "city_name": "NewAmsterdam",
    }


def test_persistent_document_rejects_extra_fields() -> None:
    payload: dict[str, object] = {
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "city_name": "NewAmsterdam",
        "unexpected_field": "not_allowed",
    }

    with pytest.raises(ValidationError):
        PlainPersistentUserProfileDocument.model_validate(payload)


def test_custom_document_can_choose_millisecond_timestamp_precision() -> None:
    document: MillisecondAuditDocument = MillisecondAuditDocument(
        user_id=UserId("user_marty_mcfly"),
        retry_count=RetryCount(2),
    )

    assert isinstance(document.created_at, Milliseconds)
    assert isinstance(document.updated_at, Milliseconds)
    assert document.retry_count == RetryCount(2)

    payload: dict[str, object] = document.model_dump(mode="json")

    assert isinstance(payload["created_at"], int)
    assert isinstance(payload["updated_at"], int)
    assert payload["schema_version"] == "1"
    assert payload["retry_count"] == 2


def test_custom_document_can_choose_nanosecond_timestamp_precision() -> None:
    document: NanosecondAuditDocument = NanosecondAuditDocument(
        user_id=UserId("user_marty_mcfly"),
        retry_count=RetryCount(3),
    )

    assert isinstance(document.created_at, Nanoseconds)
    assert isinstance(document.updated_at, Nanoseconds)
    assert document.retry_count == RetryCount(3)

    payload: dict[str, object] = document.model_dump(mode="json")

    assert isinstance(payload["created_at"], int)
    assert isinstance(payload["updated_at"], int)
    assert payload["schema_version"] == "1"
    assert payload["retry_count"] == 3
