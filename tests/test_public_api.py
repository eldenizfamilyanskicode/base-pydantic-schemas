from __future__ import annotations

import base_pydantic_schemas as package
import base_pydantic_schemas.mixins as mixins
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


def test_package_public_api_exports_expected_names() -> None:
    expected_public_names: set[str] = {
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
    }

    actual_public_names: set[str] = set(package.__all__)

    assert actual_public_names == expected_public_names

    for public_name in package.__all__:
        assert hasattr(package, public_name)


def test_package_public_api_objects_are_reexported_by_identity() -> None:
    assert package.ArbitraryImmutableDTO is ArbitraryImmutableDTO
    assert package.ArbitraryMutableDTO is ArbitraryMutableDTO
    assert package.BaseDocument is BaseDocument
    assert package.BaseSchema is BaseSchema
    assert package.ImmutableDTO is ImmutableDTO
    assert package.MutableDTO is MutableDTO
    assert package.PersistentDocument is PersistentDocument
    assert package.SchemaVersion is SchemaVersion
    assert package.UnixMicrosecondTimestampedMixin is UnixMicrosecondTimestampedMixin
    assert package.UnixMillisecondTimestampedMixin is UnixMillisecondTimestampedMixin
    assert package.UnixNanosecondTimestampedMixin is UnixNanosecondTimestampedMixin
    assert package.VersionedMixin is VersionedMixin


def test_package_version_is_current_public_version() -> None:
    assert package.__version__ == "0.1.0"


def test_mixins_public_api_exports_expected_names() -> None:
    expected_public_names: set[str] = {
        "SchemaVersion",
        "UnixMicrosecondTimestampedMixin",
        "UnixMillisecondTimestampedMixin",
        "UnixNanosecondTimestampedMixin",
        "VersionedMixin",
    }

    actual_public_names: set[str] = set(mixins.__all__)

    assert actual_public_names == expected_public_names

    for public_name in mixins.__all__:
        assert hasattr(mixins, public_name)


def test_mixins_public_api_objects_are_reexported_by_identity() -> None:
    assert mixins.SchemaVersion is SchemaVersion
    assert mixins.UnixMicrosecondTimestampedMixin is UnixMicrosecondTimestampedMixin
    assert mixins.UnixMillisecondTimestampedMixin is UnixMillisecondTimestampedMixin
    assert mixins.UnixNanosecondTimestampedMixin is UnixNanosecondTimestampedMixin
    assert mixins.VersionedMixin is VersionedMixin
