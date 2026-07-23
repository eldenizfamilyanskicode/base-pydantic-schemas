from base_typed_string import BaseConstrainedTypedString, BaseTypedString

from base_pydantic_schemas import ImmutableDTO


class DisplayName(BaseTypedString):
    """Unconstrained semantic display name."""


class UserHandle(BaseConstrainedTypedString):
    """Lowercase public handle with intrinsic format constraints."""

    min_length = 3
    max_length = 32
    pattern = r"^[a-z][a-z0-9_]*$"


class PublicProfileDTO(ImmutableDTO):
    """Read model combining ordinary and constrained typed strings."""

    display_name: DisplayName
    user_handle: UserHandle


def main() -> None:
    profile: PublicProfileDTO = PublicProfileDTO.model_validate(
        {
            "display_name": "Marty McFly",
            "user_handle": "marty_mcfly",
        },
    )

    assert type(profile.display_name) is DisplayName
    assert type(profile.user_handle) is UserHandle

    print(profile.model_dump(mode="json"))


if __name__ == "__main__":
    main()
