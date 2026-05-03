from typing import Protocol

from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString

from base_pydantic_schemas import BaseDocument, ImmutableDTO, MutableDTO


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class CityName(BaseTypedString):
    """City name stored in profile."""


class ProfileVersion(BaseTypedInt):
    """Profile version for optimistic concurrency."""


class CreateUserProfileCommand(MutableDTO):
    """Command DTO accepted by application use case."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName


class UserProfileReadModel(ImmutableDTO):
    """Read model returned by application use case."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion


class UserProfileDocument(BaseDocument):
    """Persistence document stored by repository implementation."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion = ProfileVersion(1)


class UserProfileRepositoryInterface(Protocol):
    """Repository contract used by application service."""

    def find_by_user_id(
        self,
        user_id: UserId,
    ) -> UserProfileDocument | None:
        raise NotImplementedError

    def save(
        self,
        profile_document: UserProfileDocument,
    ) -> None:
        raise NotImplementedError


class InMemoryUserProfileRepository:
    """
    Example repository implementation.

    Real applications would implement the same protocol using MongoDB,
    PostgreSQL, Redis, or another persistence adapter.
    """

    def __init__(self) -> None:
        self._documents_by_user_id: dict[UserId, UserProfileDocument] = {}

    def find_by_user_id(
        self,
        user_id: UserId,
    ) -> UserProfileDocument | None:
        profile_document: UserProfileDocument | None = self._documents_by_user_id.get(
            user_id,
        )

        return profile_document

    def save(
        self,
        profile_document: UserProfileDocument,
    ) -> None:
        self._documents_by_user_id[profile_document.user_id] = profile_document


class CreateUserProfileUseCase:
    """Application service with constructor dependency injection."""

    def __init__(
        self,
        user_profile_repository: UserProfileRepositoryInterface,
    ) -> None:
        self._user_profile_repository: UserProfileRepositoryInterface = (
            user_profile_repository
        )

    def create_user_profile(
        self,
        command: CreateUserProfileCommand,
    ) -> UserProfileReadModel:
        existing_document: UserProfileDocument | None = (
            self._user_profile_repository.find_by_user_id(
                user_id=command.user_id,
            )
        )

        if existing_document is not None:
            raise ValueError("User profile already exists.")

        profile_document: UserProfileDocument = UserProfileDocument(
            user_id=command.user_id,
            display_name=command.display_name,
            city_name=command.city_name,
        )

        self._user_profile_repository.save(profile_document=profile_document)

        read_model: UserProfileReadModel = UserProfileReadModel(
            user_id=profile_document.user_id,
            display_name=profile_document.display_name,
            city_name=profile_document.city_name,
            profile_version=profile_document.profile_version,
        )

        return read_model


def main() -> None:
    user_profile_repository: InMemoryUserProfileRepository = (
        InMemoryUserProfileRepository()
    )

    create_user_profile_use_case: CreateUserProfileUseCase = CreateUserProfileUseCase(
        user_profile_repository=user_profile_repository,
    )

    command: CreateUserProfileCommand = CreateUserProfileCommand(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
    )

    read_model: UserProfileReadModel = create_user_profile_use_case.create_user_profile(
        command=command
    )

    response_payload: dict[str, object] = read_model.model_dump(mode="json")

    print(response_payload)


if __name__ == "__main__":
    main()
