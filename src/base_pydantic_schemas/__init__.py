"""
Public API for base_pydantic_schemas.

The package provides small, opinionated Pydantic v2 base classes for projects
that want consistent DTO and persistence model configuration across services.

The public API is intentionally narrow:
- strict mutable DTOs
- strict immutable DTOs
- arbitrary-type DTOs
- persistence-neutral document bases
- typed UNIX timestamp mixins
- typed schema versioning

The package does not implement storage-specific serialization. Use Pydantic's
native model_dump(), model_dump_json(), and model_validate() APIs at persistence
boundaries.
"""

from base_pydantic_schemas._arbitrary_immutable_dto import ArbitraryImmutableDTO
from base_pydantic_schemas._arbitrary_mutable_dto import ArbitraryMutableDTO
from base_pydantic_schemas._base_document import BaseDocument
from base_pydantic_schemas._base_schema import BaseSchema
from base_pydantic_schemas._immutable_dto import ImmutableDTO
from base_pydantic_schemas._mutable_dto import MutableDTO
from base_pydantic_schemas._persistent_document import PersistentDocument
from base_pydantic_schemas.mixins import (
    SchemaVersion,
    UnixMicrosecondTimestampedMixin,
    UnixMillisecondTimestampedMixin,
    UnixNanosecondTimestampedMixin,
    VersionedMixin,
)

__all__: list[str] = [
    "ArbitraryImmutableDTO",
    "ArbitraryMutableDTO",
    "BaseDocument",
    "BaseSchema",
    "ImmutableDTO",
    "MutableDTO",
    "PersistentDocument",
    "SchemaVersion",
    "UnixMicrosecondTimestampedMixin",
    "UnixMillisecondTimestampedMixin",
    "UnixNanosecondTimestampedMixin",
    "VersionedMixin",
]

__version__: str = "0.1.0"
