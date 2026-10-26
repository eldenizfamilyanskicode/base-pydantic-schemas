# base-pydantic-schemas

Small opinionated Pydantic v2 base schemas for semantic DTOs and persistence
documents.

The main idea is simple: model class name should communicate behavior.

When you see:

- `MutableDTO`
- `ImmutableDTO`
- `ArbitraryMutableDTO`
- `ArbitraryImmutableDTO`
- `BaseDocument`
- `PersistentDocument`

you immediately understand the model contract: mutability, strictness, arbitrary
runtime object support, and persistence intent.

This package is for projects where schemas are not just validation containers,
but explicit semantic boundaries between API, application, domain, infrastructure,
and persistence layers.

## Installation

```bash
pip install base-pydantic-schemas
```

## Requirements

```text
Python >= 3.10
Pydantic >= 2.6,<3
```

Release 0.3.0 checks Python 3.10–3.14 with Pydantic 2.14.1, the current stable
release, and separately checks Python 3.10 with the minimum Pydantic 2.6.0.
The dependency range remains `pydantic>=2.6,<3`; upstream wheels are not available
for every Python/Pydantic combination allowed by that range.

Runtime dependencies:

```text
base-typed-string
base-typed-int
base-typed-float
typed-time-provider
```

## Core idea

Instead of using raw `BaseModel` everywhere:

```python
from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: str
    display_name: str
```

use semantically named base schemas:

```python
from base_pydantic_schemas import ImmutableDTO
from base_typed_string import BaseTypedString


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class UserProfileReadModel(ImmutableDTO):
    """Stable read model returned from application layer."""

    user_id: UserId
    display_name: DisplayName
```

Now the model says more:

* this is a DTO
* it is immutable
* it rejects undeclared fields
* it uses strict Pydantic validation
* it preserves typed semantic fields
* it can be safely returned as a stable application snapshot

## Public API

```python
from base_pydantic_schemas import (
    ArbitraryImmutableDTO,
    ArbitraryMutableDTO,
    BaseDocument,
    BaseSchema,
    ImmutableDTO,
    MutableDTO,
    PersistentDocument,
    SchemaVersion,
    UnixMicrosecondTimestampedMixin,
    UnixMillisecondTimestampedMixin,
    UnixNanosecondTimestampedMixin,
    VersionedMixin,
)
```

## Deferred schema construction

Ordinary imports keep their existing eager construction behavior:

```python
from base_pydantic_schemas import MutableDTO, BaseDocument
```

Opt in when defining models whose validators and serializers may never be used:

```python
from base_pydantic_schemas.deferred import MutableDTO, BaseDocument


class UpdateQuantity(MutableDTO):
    quantity: int


class InventoryDocument(BaseDocument):
    quantity: int
```

The deferred namespace exports the same twelve public names. All model bases and
timestamp/version mixins inherit `ConfigDict(defer_build=True)`. Validation
policies, timestamp factories, serialization behavior, and the `SchemaVersion`
type are shared with the ordinary API.

Deferring construction reduces import/startup allocation for unused model
validators and serializers. That work moves to first use or an explicit build;
it is not eliminated. Some schema errors also move from class definition to
first use or build.

Child configuration keeps inherited settings unless explicitly overridden:

```python
from typing import ClassVar

from pydantic import ConfigDict


class NamedCommand(UpdateQuantity):
    model_config: ClassVar[ConfigDict] = ConfigDict(title="Named command")


class EagerCommand(UpdateQuantity):
    model_config: ClassVar[ConfigDict] = ConfigDict(defer_build=False)
```

Use an explicit list of application-owned models in application CI to catch
delayed schema errors. Import or define all referenced models before rebuilding:

```python
from pydantic import BaseModel


application_models: tuple[type[BaseModel], ...] = (
    UpdateQuantity,
    InventoryDocument,
)
for model in application_models:
    model.model_rebuild(force=True)
```

The library's tests cover its bases; application CI must check the application's
own models and references. See executable examples:

```bash
python examples/deferred_usage.py
python examples/deferred_ci_build.py
```

## Model types

| Base class              | Mutable | Frozen | Extra fields | Arbitrary types | Main use                                                       |
| ----------------------- | ------: | -----: | -----------: | --------------: | -------------------------------------------------------------- |
| `MutableDTO`            |     yes |     no |    forbidden |              no | commands, request state, normalized input                      |
| `ImmutableDTO`          |      no |    yes |    forbidden |              no | read models, responses, query results, snapshots               |
| `ArbitraryMutableDTO`   |     yes |     no |    forbidden |             yes | runtime boundary objects with clients, callbacks, iterators    |
| `ArbitraryImmutableDTO` |      no |    yes |    forbidden |             yes | frozen runtime boundary values                                 |
| `PersistentDocument`    |     yes |     no |    forbidden |              no | custom persistence documents                                   |
| `BaseDocument`          |     yes |     no |    forbidden |              no | default persisted documents with timestamps and schema version |

All concrete base classes are configured with:

```python
from pydantic import ConfigDict

model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True,
    extra="forbid",
    validate_default=True,
    strict=True,
)
```

Mutable models additionally use:

```python
validate_assignment=True
```

Immutable models additionally use:

```python
frozen=True
```

Arbitrary DTOs additionally use:

```python
arbitrary_types_allowed=True
```

## MutableDTO

Use `MutableDTO` for command/request objects that may be enriched, normalized, or
updated before a use case is executed.

```python
from base_pydantic_schemas import MutableDTO
from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class Biography(BaseTypedString):
    """Optional user biography."""


class ProfileVersion(BaseTypedInt):
    """Optimistic concurrency version."""


class UpdateUserProfileCommand(MutableDTO):
    """Command accepted by application layer."""

    user_id: UserId
    display_name: DisplayName
    biography: Biography | None = None
    expected_profile_version: ProfileVersion


command: UpdateUserProfileCommand = UpdateUserProfileCommand(
    user_id=UserId("user_marty_mcfly"),
    display_name=DisplayName("Marty McFly"),
    expected_profile_version=ProfileVersion(7),
)

command.biography = Biography("Backend developer living in NewAmsterdam.")

payload: dict[str, object] = command.model_dump(mode="json")
```

## ImmutableDTO

Use `ImmutableDTO` for data that should not change after construction.

Good fits:

* API response DTOs
* read models
* query results
* application snapshots
* domain-facing immutable values

```python
from base_pydantic_schemas import ImmutableDTO
from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class CityName(BaseTypedString):
    """City name shown in user profile."""


class ProfileVersion(BaseTypedInt):
    """Read model profile version."""


class UserProfileReadModel(ImmutableDTO):
    """Stable read model returned from a use case."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion


read_model: UserProfileReadModel = UserProfileReadModel(
    user_id=UserId("user_marty_mcfly"),
    display_name=DisplayName("Marty McFly"),
    city_name=CityName("NewAmsterdam"),
    profile_version=ProfileVersion(7),
)

response_payload: dict[str, object] = read_model.model_dump(mode="json")
```

## ArbitraryMutableDTO

Use `ArbitraryMutableDTO` only at runtime boundaries where the DTO must carry
objects that Pydantic cannot fully model as data.

Examples:

* iterators
* callbacks
* clients
* transactions
* framework objects
* adapters
* file handles
* runtime-only services

```python
from collections.abc import Callable

from base_pydantic_schemas import ArbitraryMutableDTO, ImmutableDTO
from base_typed_string import BaseTypedString


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class ImportSourceName(BaseTypedString):
    """External import source name."""


class ImportedUserRow(ImmutableDTO):
    """Parsed external row."""

    external_user_id: UserId
    display_name: DisplayName


class UserImportedEvent(ImmutableDTO):
    """Application event produced after import."""

    imported_user_id: UserId
    display_name: DisplayName


class UserImportIterator:
    """Runtime iterator object."""

    def __init__(
        self,
        rows: tuple[ImportedUserRow, ...],
    ) -> None:
        self._rows: tuple[ImportedUserRow, ...] = rows
        self._next_row_index: int = 0

    def __iter__(self) -> "UserImportIterator":
        return self

    def __next__(self) -> ImportedUserRow:
        if self._next_row_index >= len(self._rows):
            raise StopIteration

        imported_user_row: ImportedUserRow = self._rows[self._next_row_index]
        self._next_row_index = self._next_row_index + 1

        return imported_user_row


class UserImportBoundaryJob(ArbitraryMutableDTO):
    """Runtime boundary DTO carrying non-Pydantic objects."""

    source_name: ImportSourceName
    record_iterator: UserImportIterator
    publish_user_imported_event: Callable[[UserImportedEvent], None]
```

Prefer `MutableDTO` when arbitrary runtime objects are not required.

## ArbitraryImmutableDTO

Use `ArbitraryImmutableDTO` when the model must carry arbitrary runtime objects
but should be frozen after construction.

```python
from collections.abc import Callable

from base_pydantic_schemas import ArbitraryImmutableDTO


class RuntimeCallbackBundle(ArbitraryImmutableDTO):
    """Frozen runtime callback bundle."""

    on_success: Callable[[], None]
    on_failure: Callable[[Exception], None]
```

## BaseDocument

Use `BaseDocument` for normal persisted documents.

It includes:

* `created_at`
* `updated_at`
* `schema_version`

Default timestamp precision is UNIX microseconds.

```python
from base_pydantic_schemas import BaseDocument
from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class CityName(BaseTypedString):
    """City name stored in user profile."""


class ProfileVersion(BaseTypedInt):
    """Persistence document version."""


class UserProfileDocument(BaseDocument):
    """Default persisted document."""

    user_id: UserId
    display_name: DisplayName
    city_name: CityName
    profile_version: ProfileVersion = ProfileVersion(1)


document: UserProfileDocument = UserProfileDocument(
    user_id=UserId("user_marty_mcfly"),
    display_name=DisplayName("Marty McFly"),
    city_name=CityName("NewAmsterdam"),
)

persistence_payload: dict[str, object] = document.model_dump(mode="json")

restored_document: UserProfileDocument = UserProfileDocument.model_validate(
    persistence_payload,
)
```

Example JSON-like payload:

```python
{
    "created_at": 1760000000000000,
    "updated_at": 1760000000000000,
    "schema_version": "1",
    "user_id": "user_marty_mcfly",
    "display_name": "Marty McFly",
    "city_name": "NewAmsterdam",
    "profile_version": 1,
}
```

`created_at` and `updated_at` are captured independently through Pydantic
`default_factory`. They are not guaranteed to be identical.

`updated_at` is not automatically changed when the model is mutated. Update it
explicitly in your repository or use case boundary.

## PersistentDocument with custom mixins

Use `PersistentDocument` directly when you need custom metadata layout or a
different timestamp precision.

```python
from base_pydantic_schemas import (
    PersistentDocument,
    UnixMillisecondTimestampedMixin,
    VersionedMixin,
)
from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString
from typed_time_provider import Milliseconds


class OutboxMessageId(BaseTypedString):
    """Outbox message identifier."""


class AggregateId(BaseTypedString):
    """Domain aggregate identifier."""


class EventType(BaseTypedString):
    """Domain event type name."""


class EventPayloadJson(BaseTypedString):
    """Serialized event payload."""


class RetryCount(BaseTypedInt):
    """Number of delivery attempts."""


class OutboxMessageDocument(
    UnixMillisecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """Outbox document stored with millisecond timestamps."""

    message_id: OutboxMessageId
    aggregate_id: AggregateId
    event_type: EventType
    payload_json: EventPayloadJson
    retry_count: RetryCount = RetryCount(0)
    published_at: Milliseconds | None = None
```

Available timestamp mixins:

```python
UnixNanosecondTimestampedMixin
UnixMicrosecondTimestampedMixin
UnixMillisecondTimestampedMixin
```

Available versioning mixin:

```python
VersionedMixin
```

The default schema version is:

```python
SchemaVersion("1")
```

## Dependency injection example

Schemas should stay simple. Business logic should depend on protocols and receive
repositories, clocks, clients, and services through constructor injection.

```python
from typing import Protocol

from base_pydantic_schemas import BaseDocument, ImmutableDTO, MutableDTO
from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString


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
```

## Serialization

The package does not add storage-specific methods.

Use native Pydantic APIs:

```python
persistence_payload: dict[str, object] = document.model_dump(mode="json")
json_payload: str = document.model_dump_json()
restored_document: UserProfileDocument = UserProfileDocument.model_validate(
    persistence_payload,
)
```

This keeps persistence adapters explicit.

For example, MongoDB, PostgreSQL, Redis, S3, Kafka, or an event store should each
own its own boundary mapping rules.

## Recommended usage

Use `MutableDTO` for:

* command objects
* request state
* normalized input
* application-layer mutable data

Use `ImmutableDTO` for:

* read models
* API responses
* query results
* stable snapshots
* domain-facing values

Use `ArbitraryMutableDTO` for:

* runtime boundary jobs
* injected callbacks
* streaming iterators
* transaction handles
* framework objects
* external clients

Use `ArbitraryImmutableDTO` for:

* frozen runtime boundary values
* immutable callback bundles
* runtime configuration objects with arbitrary dependencies

Use `BaseDocument` for:

* default persistence documents
* models that need `created_at`
* models that need `updated_at`
* models that need `schema_version`

Use `PersistentDocument` plus mixins for:

* custom metadata layouts
* millisecond timestamps
* nanosecond timestamps
* documents where versioning is optional
* documents where timestamp fields need custom names or behavior

## Design principles

### Semantic base classes

A schema base class should describe the model's role.

`UserProfileReadModel(ImmutableDTO)` is clearer than `UserProfileReadModel(BaseModel)`.

`UserProfileDocument(BaseDocument)` is clearer than `UserProfileDocument(BaseModel)`.

### Strict by default

Models should not silently coerce unexpected input.

For example, a strict DTO should not quietly turn `"123"` into `123` for normal
integer fields.

### Extra fields are forbidden

Unexpected payload fields usually mean one of these things:

* API contract mismatch
* outdated client
* wrong integration mapping
* persistence migration bug
* typo

So undeclared fields are rejected.

### Typed fields compose well

The package is designed to work with semantic primitive wrappers such as:

```python
from base_typed_float import BaseConstrainedTypedFloat, BaseTypedFloat
from base_typed_int import BaseConstrainedTypedInt, BaseTypedInt
from base_typed_string import BaseConstrainedTypedString, BaseTypedString
from typed_time_provider import Microseconds


class DisplayName(BaseTypedString):
    """Unconstrained semantic display name."""


class UserHandle(BaseConstrainedTypedString):
    """Lowercase public handle with intrinsic format constraints."""

    min_length = 3
    max_length = 32
    pattern = r"^[a-z][a-z0-9_]*$"


class RetryCount(BaseTypedInt):
    """Unconstrained retry count received from an external source."""


class ImportBatchSize(BaseConstrainedTypedInt):
    """Import batch size accepted by the application."""

    ge = 1
    le = 1_000


class TemperatureCelsius(BaseTypedFloat):
    """Unconstrained finite temperature in degrees Celsius."""


class CompletionRatio(BaseConstrainedTypedFloat):
    """Completion ratio in the inclusive range from zero to one."""

    ge = 0.0
    le = 1.0


class CreatedAt(Microseconds):
    """Creation UNIX timestamp in microseconds."""
```

This makes schemas readable without adding heavy domain framework abstractions.

### Persistence-neutral documents

`BaseDocument` and `PersistentDocument` are not tied to MongoDB, SQL, Redis,
Kafka, or any specific storage engine.

They are Pydantic models with persistence-oriented defaults.

Storage adapters decide how to persist them.

## Local development

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run lint:

```bash
ruff check src tests examples
ruff format src tests examples
```

Run type checks:

```bash
mypy src tests examples
pyright
```

Build package:

```bash
python -m build
```

## Package status

Current version:

```text
0.3.0
```

The public API is intentionally small and stable:

```text
BaseSchema
MutableDTO
ImmutableDTO
ArbitraryMutableDTO
ArbitraryImmutableDTO
PersistentDocument
BaseDocument
UnixNanosecondTimestampedMixin
UnixMicrosecondTimestampedMixin
UnixMillisecondTimestampedMixin
VersionedMixin
SchemaVersion
```

## License

MIT
