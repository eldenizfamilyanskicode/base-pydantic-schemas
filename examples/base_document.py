from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString

from base_pydantic_schemas import BaseDocument


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class CityName(BaseTypedString):
    """City name stored in user profile."""


class ProfileVersion(BaseTypedInt):
    """Persistence document version."""


class UserProfileDocument(BaseDocument):
    """
    Default persisted document.

    Includes:
    - created_at
    - updated_at
    - schema_version
    """

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion = ProfileVersion(1)


def main() -> None:
    document: UserProfileDocument = UserProfileDocument(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
    )

    persistence_payload: dict[str, object] = document.model_dump(mode="json")

    restored_document: UserProfileDocument = UserProfileDocument.model_validate(
        persistence_payload,
    )

    restored_payload: dict[str, object] = restored_document.model_dump(mode="json")

    print(restored_payload)
    print(type(restored_document.created_at).__name__)
    print(type(restored_document.schema_version).__name__)


if __name__ == "__main__":
    main()
