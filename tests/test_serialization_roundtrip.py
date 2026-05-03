from __future__ import annotations

import json
from typing import cast

from typed_time_provider import Microseconds

from base_pydantic_schemas import ImmutableDTO, SchemaVersion
from tests.testing_types import (
    ImmutableUserProfileDTO,
    UserId,
    UserProfileDocument,
    create_immutable_user_profile,
)


class UserProfileEnvelope(ImmutableDTO):
    """Nested model used to verify full JSON roundtrip behavior."""

    profile: ImmutableUserProfileDTO
    document: UserProfileDocument


def test_nested_models_dump_and_validate_restore_typed_values() -> None:
    profile: ImmutableUserProfileDTO = create_immutable_user_profile()

    document_payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456,
        "updated_at": 1_700_000_000_654_321,
        "schema_version": "7",
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "city_name": "NewAmsterdam",
        "profile_version": 12,
    }

    document: UserProfileDocument = UserProfileDocument.model_validate(
        document_payload,
    )

    envelope: UserProfileEnvelope = UserProfileEnvelope(
        profile=profile,
        document=document,
    )

    payload: dict[str, object] = envelope.model_dump(mode="json")
    restored_envelope: UserProfileEnvelope = UserProfileEnvelope.model_validate(
        payload,
    )

    assert restored_envelope.profile.user_id == UserId("user_marty_mcfly")
    assert restored_envelope.document.created_at == Microseconds(
        1_700_000_000_123_456,
    )
    assert restored_envelope.document.schema_version == SchemaVersion("7")

    assert isinstance(restored_envelope.profile.user_id, UserId)
    assert isinstance(restored_envelope.document.created_at, Microseconds)
    assert isinstance(restored_envelope.document.schema_version, SchemaVersion)


def test_model_dump_json_outputs_plain_json_scalars() -> None:
    document_payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456,
        "updated_at": 1_700_000_000_654_321,
        "schema_version": "7",
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "city_name": "NewAmsterdam",
        "profile_version": 12,
    }

    document: UserProfileDocument = UserProfileDocument.model_validate(
        document_payload,
    )

    json_payload_text: str = document.model_dump_json()
    loaded_payload: dict[str, object] = cast(
        dict[str, object],
        json.loads(json_payload_text),
    )

    assert loaded_payload == document_payload
    assert isinstance(loaded_payload["created_at"], int)
    assert isinstance(loaded_payload["updated_at"], int)
    assert isinstance(loaded_payload["schema_version"], str)
    assert isinstance(loaded_payload["user_id"], str)
