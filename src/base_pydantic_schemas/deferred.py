"""Opt-in schema bases that build validators and serializers on first use."""

from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas._arbitrary_immutable_dto import (
    ArbitraryImmutableDTO as _ArbitraryImmutableDTO,
)
from base_pydantic_schemas._arbitrary_mutable_dto import (
    ArbitraryMutableDTO as _ArbitraryMutableDTO,
)
from base_pydantic_schemas._base_document import BaseDocument as _BaseDocument
from base_pydantic_schemas._base_schema import BaseSchema as _BaseSchema
from base_pydantic_schemas._immutable_dto import ImmutableDTO as _ImmutableDTO
from base_pydantic_schemas._mutable_dto import MutableDTO as _MutableDTO
from base_pydantic_schemas._persistent_document import (
    PersistentDocument as _PersistentDocument,
)
from base_pydantic_schemas.mixins.timestamped import (
    UnixMicrosecondTimestampedMixin as _UnixMicrosecondTimestampedMixin,
)
from base_pydantic_schemas.mixins.timestamped import (
    UnixMillisecondTimestampedMixin as _UnixMillisecondTimestampedMixin,
)
from base_pydantic_schemas.mixins.timestamped import (
    UnixNanosecondTimestampedMixin as _UnixNanosecondTimestampedMixin,
)
from base_pydantic_schemas.mixins.versioned import SchemaVersion as SchemaVersion
from base_pydantic_schemas.mixins.versioned import VersionedMixin as _VersionedMixin

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


class BaseSchema(_BaseSchema):
    """Shared root that defers Pydantic validator and serializer construction."""

    model_config: ClassVar[ConfigDict] = ConfigDict(defer_build=True)


class MutableDTO(_MutableDTO, BaseSchema):
    """Strict mutable DTO with deferred construction."""


class ImmutableDTO(_ImmutableDTO, BaseSchema):
    """Strict immutable DTO with deferred construction."""


class ArbitraryMutableDTO(_ArbitraryMutableDTO, BaseSchema):
    """Mutable runtime boundary DTO with deferred construction."""


class ArbitraryImmutableDTO(_ArbitraryImmutableDTO, BaseSchema):
    """Immutable runtime boundary DTO with deferred construction."""


class PersistentDocument(_PersistentDocument, BaseSchema):
    """Persistence-neutral document with deferred construction."""


class UnixNanosecondTimestampedMixin(_UnixNanosecondTimestampedMixin, BaseSchema):
    """Typed UNIX nanosecond timestamps with deferred construction."""


class UnixMicrosecondTimestampedMixin(_UnixMicrosecondTimestampedMixin, BaseSchema):
    """Typed UNIX microsecond timestamps with deferred construction."""


class UnixMillisecondTimestampedMixin(_UnixMillisecondTimestampedMixin, BaseSchema):
    """Typed UNIX millisecond timestamps with deferred construction."""


class VersionedMixin(_VersionedMixin, BaseSchema):
    """Typed schema versioning with deferred construction."""


class BaseDocument(
    _BaseDocument,
    UnixMicrosecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """Default timestamped and versioned document with deferred construction."""
