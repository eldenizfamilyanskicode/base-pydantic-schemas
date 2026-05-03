from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString

from base_pydantic_schemas import MutableDTO


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class Biography(BaseTypedString):
    """Optional user biography."""


class ProfileVersion(BaseTypedInt):
    """Optimistic concurrency version for profile updates."""


class UpdateUserProfileCommand(MutableDTO):
    """
    Mutable command DTO.

    Useful when application code enriches or normalizes request data before
    passing it into a use case.
    """

    user_id: UserId
    display_name: DisplayName
    biography: Biography | None = None
    expected_profile_version: ProfileVersion


def main() -> None:
    command: UpdateUserProfileCommand = UpdateUserProfileCommand(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        expected_profile_version=ProfileVersion(7),
    )

    command.biography = Biography("Backend developer living in NewAmsterdam.")

    command_payload: dict[str, object] = command.model_dump(mode="json")

    print(command_payload)


if __name__ == "__main__":
    main()
