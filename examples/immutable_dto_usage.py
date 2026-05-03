from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString

from base_pydantic_schemas import ImmutableDTO


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class CityName(BaseTypedString):
    """City name shown in user profile."""


class ProfileVersion(BaseTypedInt):
    """Read model profile version."""


class UserProfileReadModel(ImmutableDTO):
    """
    Immutable read model.

    Useful for query results, API responses, and stable snapshots returned from
    application services.
    """

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion


def main() -> None:
    read_model: UserProfileReadModel = UserProfileReadModel(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
        profile_version=ProfileVersion(7),
    )

    response_payload: dict[str, object] = read_model.model_dump(mode="json")

    print(response_payload)


if __name__ == "__main__":
    main()
