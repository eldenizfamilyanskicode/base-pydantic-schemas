from __future__ import annotations

import pytest
from pydantic import Field, ValidationError

from base_pydantic_schemas import MutableDTO
from tests.runtime_boundary import assign_runtime_value
from tests.testing_types import (
    Biography,
    DisplayName,
    MutableUserProfileDTO,
    ProfileVersion,
    UserId,
    create_immutable_user_profile,
    create_mutable_user_profile,
)


class ExternalUserRecord:
    """Attribute-based source object used for from_attributes validation."""

    def __init__(
        self,
        external_user_id: UserId,
    ) -> None:
        self.external_user_id: UserId = external_user_id


class UserAliasDTO(MutableDTO):
    """DTO used to verify alias and field-name population."""

    user_id: UserId = Field(alias="external_user_id")


def test_mutable_dto_accepts_typed_values_and_serializes_to_plain_json() -> None:
    mutable_profile: MutableUserProfileDTO = create_mutable_user_profile()

    payload: dict[str, object] = mutable_profile.model_dump(mode="json")

    expected_payload: dict[str, object] = {
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "biography": None,
        "profile_version": 7,
    }

    assert payload == expected_payload
    assert isinstance(mutable_profile.user_id, UserId)
    assert isinstance(mutable_profile.display_name, DisplayName)
    assert isinstance(mutable_profile.profile_version, ProfileVersion)


def test_mutable_dto_validates_assignment_and_preserves_typed_values() -> None:
    mutable_profile: MutableUserProfileDTO = create_mutable_user_profile()

    assign_runtime_value(
        target_object=mutable_profile,
        field_name="display_name",
        field_value="Emmett Brown",
    )
    assign_runtime_value(
        target_object=mutable_profile,
        field_name="biography",
        field_value="Inventor from Hill Valley",
    )
    assign_runtime_value(
        target_object=mutable_profile,
        field_name="profile_version",
        field_value=8,
    )

    assert mutable_profile.display_name == DisplayName("Emmett Brown")
    assert mutable_profile.biography == Biography("Inventor from Hill Valley")
    assert mutable_profile.profile_version == ProfileVersion(8)

    assert isinstance(mutable_profile.display_name, DisplayName)
    assert isinstance(mutable_profile.biography, Biography)
    assert isinstance(mutable_profile.profile_version, ProfileVersion)


def test_mutable_dto_rejects_invalid_assignment_values() -> None:
    mutable_profile: MutableUserProfileDTO = create_mutable_user_profile()

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=mutable_profile,
            field_name="profile_version",
            field_value=True,
        )

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=mutable_profile,
            field_name="display_name",
            field_value=123,
        )

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=mutable_profile,
            field_name="unexpected_field",
            field_value="value",
        )

    assert mutable_profile.profile_version == ProfileVersion(7)
    assert mutable_profile.display_name == DisplayName("Marty McFly")


def test_mutable_dto_rejects_extra_fields_at_validation_boundary() -> None:
    payload: dict[str, object] = {
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "profile_version": 7,
        "unexpected_field": "not_allowed",
    }

    with pytest.raises(ValidationError):
        MutableUserProfileDTO.model_validate(payload)


def test_mutable_dto_rejects_non_strict_integer_coercion() -> None:
    payload: dict[str, object] = {
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "profile_version": "7",
    }

    with pytest.raises(ValidationError):
        MutableUserProfileDTO.model_validate(payload)


def test_immutable_dto_serializes_to_plain_json_values() -> None:
    immutable_profile = create_immutable_user_profile()

    payload: dict[str, object] = immutable_profile.model_dump(mode="json")

    expected_payload: dict[str, object] = {
        "user_id": "user_marty_mcfly",
        "display_name": "Marty McFly",
        "city_name": "NewAmsterdam",
        "profile_version": 7,
    }

    assert payload == expected_payload
    assert isinstance(immutable_profile.user_id, UserId)
    assert isinstance(immutable_profile.display_name, DisplayName)
    assert isinstance(immutable_profile.profile_version, ProfileVersion)


def test_immutable_dto_rejects_assignment() -> None:
    immutable_profile = create_immutable_user_profile()

    with pytest.raises(ValidationError):
        immutable_profile.display_name = DisplayName("Emmett Brown")

    assert immutable_profile.display_name == DisplayName("Marty McFly")


def test_dto_supports_alias_population_by_alias() -> None:
    payload: dict[str, object] = {
        "external_user_id": "user_marty_mcfly",
    }

    alias_model: UserAliasDTO = UserAliasDTO.model_validate(payload)

    assert alias_model.user_id == UserId("user_marty_mcfly")
    assert isinstance(alias_model.user_id, UserId)


def test_dto_supports_alias_population_by_field_name() -> None:
    payload: dict[str, object] = {
        "user_id": "user_marty_mcfly",
    }

    alias_model: UserAliasDTO = UserAliasDTO.model_validate(payload)

    assert alias_model.user_id == UserId("user_marty_mcfly")
    assert isinstance(alias_model.user_id, UserId)


def test_dto_supports_attribute_based_validation() -> None:
    external_record: ExternalUserRecord = ExternalUserRecord(
        external_user_id=UserId("user_doc_brown"),
    )

    alias_model: UserAliasDTO = UserAliasDTO.model_validate(external_record)

    assert alias_model.user_id == UserId("user_doc_brown")
    assert isinstance(alias_model.user_id, UserId)
