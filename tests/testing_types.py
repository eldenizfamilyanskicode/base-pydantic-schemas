from __future__ import annotations

from collections.abc import Callable

from base_typed_float import BaseConstrainedTypedFloat, BaseTypedFloat
from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds

from base_pydantic_schemas import (
    ArbitraryImmutableDTO,
    ArbitraryMutableDTO,
    BaseDocument,
    BaseSchema,
    ImmutableDTO,
    MutableDTO,
    PersistentDocument,
    UnixMicrosecondTimestampedMixin,
    UnixMillisecondTimestampedMixin,
    UnixNanosecondTimestampedMixin,
    VersionedMixin,
)


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class CityName(BaseTypedString):
    """City name stored in a profile."""


class Biography(BaseTypedString):
    """Optional user biography."""


class SourceName(BaseTypedString):
    """External import source name."""


class ProfileVersion(BaseTypedInt):
    """Optimistic concurrency profile version."""


class RetryCount(BaseTypedInt):
    """Outbox or import retry count."""


class TemperatureCelsius(BaseTypedFloat):
    """Finite temperature measured in degrees Celsius."""


class CompletionRatio(BaseConstrainedTypedFloat):
    """Completion ratio in the inclusive range from zero to one."""

    ge = 0.0
    le = 1.0


class RuntimeDatabaseSession:
    """Runtime-only object that Pydantic cannot model as pure data."""

    def __init__(
        self,
        session_name: SourceName,
    ) -> None:
        self._session_name: SourceName = session_name

    @property
    def session_name(self) -> SourceName:
        return self._session_name


class ImportedUserEvent(ImmutableDTO):
    """Event produced by an import boundary."""

    user_id: UserId
    display_name: DisplayName


def publish_imported_user_event(
    imported_user_event: ImportedUserEvent,
) -> None:
    """No-op callable dependency used by arbitrary DTO tests."""
    _ = imported_user_event


class PlainBaseSchemaExample(BaseSchema):
    """BaseSchema should not impose DTO or persistence policy."""

    quantity: int


class MutableUserProfileDTO(MutableDTO):
    """Mutable command-like profile DTO."""

    user_id: UserId
    display_name: DisplayName
    biography: Biography | None = None
    profile_version: ProfileVersion


class ImmutableUserProfileDTO(ImmutableDTO):
    """Immutable read-model-like profile DTO."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion


class MutableMeasurementDTO(MutableDTO):
    """Mutable measurement DTO with typed float fields."""

    temperature_celsius: TemperatureCelsius
    completion_ratio: CompletionRatio


class ImmutableMeasurementDTO(ImmutableDTO):
    """Immutable measurement DTO with typed float fields."""

    temperature_celsius: TemperatureCelsius
    completion_ratio: CompletionRatio


class ArbitraryMutableImportJobDTO(ArbitraryMutableDTO):
    """Mutable boundary DTO with runtime-only dependencies."""

    source_name: SourceName
    database_session: RuntimeDatabaseSession
    publish_imported_user_event: Callable[[ImportedUserEvent], None]


class ArbitraryImmutableImportJobDTO(ArbitraryImmutableDTO):
    """Immutable boundary DTO with runtime-only dependencies."""

    source_name: SourceName
    database_session: RuntimeDatabaseSession
    publish_imported_user_event: Callable[[ImportedUserEvent], None]


class UserProfileDocument(BaseDocument):
    """Default persisted document using microsecond timestamps."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion = ProfileVersion(1)


class MeasurementDocument(BaseDocument):
    """Persisted measurement document with typed float fields."""

    temperature_celsius: TemperatureCelsius
    completion_ratio: CompletionRatio


class PlainPersistentUserProfileDocument(PersistentDocument):
    """Persistence-neutral document without default metadata mixins."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName


class NanosecondAuditDocument(
    UnixNanosecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """Custom document with nanosecond timestamp precision."""

    user_id: UserId
    retry_count: RetryCount = RetryCount(0)


class MicrosecondAuditDocument(
    UnixMicrosecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """Custom document with microsecond timestamp precision."""

    user_id: UserId
    retry_count: RetryCount = RetryCount(0)


class MillisecondAuditDocument(
    UnixMillisecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """Custom document with millisecond timestamp precision."""

    user_id: UserId
    retry_count: RetryCount = RetryCount(0)


class ExplicitVersionDocument(
    VersionedMixin,
    PersistentDocument,
):
    """Document using explicit schema version at construction boundary."""

    user_id: UserId


class ManualNanosecondDocument(PersistentDocument):
    """Document with manual nanosecond fields for roundtrip checks."""

    created_at: Nanoseconds
    updated_at: Nanoseconds
    user_id: UserId


class ManualMicrosecondDocument(PersistentDocument):
    """Document with manual microsecond fields for roundtrip checks."""

    created_at: Microseconds
    updated_at: Microseconds
    user_id: UserId


class ManualMillisecondDocument(PersistentDocument):
    """Document with manual millisecond fields for roundtrip checks."""

    created_at: Milliseconds
    updated_at: Milliseconds
    user_id: UserId


def create_mutable_user_profile() -> MutableUserProfileDTO:
    return MutableUserProfileDTO(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        profile_version=ProfileVersion(7),
    )


def create_immutable_user_profile() -> ImmutableUserProfileDTO:
    return ImmutableUserProfileDTO(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
        profile_version=ProfileVersion(7),
    )


def create_user_profile_document() -> UserProfileDocument:
    return UserProfileDocument(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
    )


def create_runtime_database_session() -> RuntimeDatabaseSession:
    return RuntimeDatabaseSession(
        session_name=SourceName("new_amsterdam_import"),
    )


def create_arbitrary_mutable_import_job() -> ArbitraryMutableImportJobDTO:
    return ArbitraryMutableImportJobDTO(
        source_name=SourceName("NewAmsterdam"),
        database_session=create_runtime_database_session(),
        publish_imported_user_event=publish_imported_user_event,
    )


def create_arbitrary_immutable_import_job() -> ArbitraryImmutableImportJobDTO:
    return ArbitraryImmutableImportJobDTO(
        source_name=SourceName("NewAmsterdam"),
        database_session=create_runtime_database_session(),
        publish_imported_user_event=publish_imported_user_event,
    )
