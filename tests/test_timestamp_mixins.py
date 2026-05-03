from __future__ import annotations

import pytest
from pydantic import BaseModel
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds, WallClock

import base_pydantic_schemas._factories as timestamp_factories  # pyright: ignore[reportPrivateUsage]
from base_pydantic_schemas._base_schema import BaseSchema
from base_pydantic_schemas.mixins.timestamped import (
    UnixMicrosecondTimestampedMixin,
    UnixMillisecondTimestampedMixin,
    UnixNanosecondTimestampedMixin,
)
from base_pydantic_schemas.mixins.versioned import SchemaVersion
from tests.testing_types import (
    CityName,
    DisplayName,
    MicrosecondAuditDocument,
    MillisecondAuditDocument,
    NanosecondAuditDocument,
    RetryCount,
    UserId,
    UserProfileDocument,
)


class SequentialUnixNanosecondFactory:
    """Deterministic UNIX nanosecond factory for timestamp tests."""

    def __init__(
        self,
        unix_nanosecond_values: tuple[int, ...],
    ) -> None:
        self._unix_nanosecond_values: tuple[int, ...] = unix_nanosecond_values
        self._next_value_index: int = 0

    def __call__(self) -> int:
        if self._next_value_index >= len(self._unix_nanosecond_values):
            return self._unix_nanosecond_values[-1]

        unix_nanosecond_value: int = self._unix_nanosecond_values[
            self._next_value_index
        ]
        self._next_value_index = self._next_value_index + 1

        return unix_nanosecond_value

    @property
    def call_count(self) -> int:
        return self._next_value_index


def install_deterministic_wall_clock(
    monkeypatch: pytest.MonkeyPatch,
    unix_nanosecond_values: tuple[int, ...],
) -> SequentialUnixNanosecondFactory:
    unix_nanosecond_factory: SequentialUnixNanosecondFactory = (
        SequentialUnixNanosecondFactory(
            unix_nanosecond_values=unix_nanosecond_values,
        )
    )

    deterministic_wall_clock: WallClock[Microseconds] = WallClock(
        preferred_time_unit_type=Microseconds,
        unix_nanosecond_factory=unix_nanosecond_factory,
    )

    monkeypatch.setattr(
        timestamp_factories,
        "_default_wall_clock",
        deterministic_wall_clock,
    )

    return unix_nanosecond_factory


def test_base_document_timestamp_factories_are_independent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unix_nanosecond_factory: SequentialUnixNanosecondFactory = (
        install_deterministic_wall_clock(
            monkeypatch=monkeypatch,
            unix_nanosecond_values=(
                1_000,
                2_000,
            ),
        )
    )

    document: UserProfileDocument = UserProfileDocument(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
        city_name=CityName("NewAmsterdam"),
    )

    assert document.created_at == Microseconds(1)
    assert document.updated_at == Microseconds(2)
    assert unix_nanosecond_factory.call_count == 2


def test_nanosecond_timestamped_mixin_uses_nanosecond_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_deterministic_wall_clock(
        monkeypatch=monkeypatch,
        unix_nanosecond_values=(
            123,
            456,
        ),
    )

    document: NanosecondAuditDocument = NanosecondAuditDocument(
        user_id=UserId("user_marty_mcfly"),
    )

    assert document.created_at == Nanoseconds(123)
    assert document.updated_at == Nanoseconds(456)
    assert isinstance(document.created_at, Nanoseconds)
    assert isinstance(document.updated_at, Nanoseconds)


def test_microsecond_timestamped_mixin_uses_microsecond_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_deterministic_wall_clock(
        monkeypatch=monkeypatch,
        unix_nanosecond_values=(
            123_456_000,
            123_457_000,
        ),
    )

    document: MicrosecondAuditDocument = MicrosecondAuditDocument(
        user_id=UserId("user_marty_mcfly"),
    )

    assert document.created_at == Microseconds(123_456)
    assert document.updated_at == Microseconds(123_457)
    assert isinstance(document.created_at, Microseconds)
    assert isinstance(document.updated_at, Microseconds)


def test_millisecond_timestamped_mixin_uses_millisecond_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_deterministic_wall_clock(
        monkeypatch=monkeypatch,
        unix_nanosecond_values=(
            123_000_000,
            124_000_000,
        ),
    )

    document: MillisecondAuditDocument = MillisecondAuditDocument(
        user_id=UserId("user_marty_mcfly"),
    )

    assert document.created_at == Milliseconds(123)
    assert document.updated_at == Milliseconds(124)
    assert isinstance(document.created_at, Milliseconds)
    assert isinstance(document.updated_at, Milliseconds)


def test_timestamp_field_descriptions_are_exposed_in_model_fields() -> None:
    created_at_field = UserProfileDocument.model_fields["created_at"]
    updated_at_field = UserProfileDocument.model_fields["updated_at"]

    assert (
        created_at_field.description
        == "Creation wall-clock UNIX timestamp in microseconds."
    )
    assert (
        updated_at_field.description
        == "Last update wall-clock UNIX timestamp in microseconds."
    )


def assert_timestamp_field_descriptions(
    model_type: type[BaseModel],
    timestamp_unit_name: str,
) -> None:
    created_at_field = model_type.model_fields["created_at"]
    updated_at_field = model_type.model_fields["updated_at"]

    assert (
        created_at_field.description
        == f"Creation wall-clock UNIX timestamp in {timestamp_unit_name}."
    )
    assert (
        updated_at_field.description
        == f"Last update wall-clock UNIX timestamp in {timestamp_unit_name}."
    )


def test_timestamp_mixins_are_base_schema_subclasses() -> None:
    assert issubclass(UnixNanosecondTimestampedMixin, BaseSchema)
    assert issubclass(UnixMicrosecondTimestampedMixin, BaseSchema)
    assert issubclass(UnixMillisecondTimestampedMixin, BaseSchema)


def test_nanosecond_timestamped_mixin_accepts_explicit_typed_values() -> None:
    document: NanosecondAuditDocument = NanosecondAuditDocument(
        created_at=Nanoseconds(1_700_000_000_123_456_789),
        updated_at=Nanoseconds(1_700_000_000_123_456_999),
        schema_version=SchemaVersion("2"),
        user_id=UserId("user_marty_mcfly"),
        retry_count=RetryCount(1),
    )

    assert document.created_at == Nanoseconds(1_700_000_000_123_456_789)
    assert document.updated_at == Nanoseconds(1_700_000_000_123_456_999)
    assert document.schema_version == SchemaVersion("2")
    assert document.retry_count == RetryCount(1)


def test_microsecond_timestamped_mixin_accepts_explicit_typed_values() -> None:
    document: MicrosecondAuditDocument = MicrosecondAuditDocument(
        created_at=Microseconds(1_700_000_000_123_456),
        updated_at=Microseconds(1_700_000_000_123_999),
        schema_version=SchemaVersion("2"),
        user_id=UserId("user_marty_mcfly"),
        retry_count=RetryCount(1),
    )

    assert document.created_at == Microseconds(1_700_000_000_123_456)
    assert document.updated_at == Microseconds(1_700_000_000_123_999)
    assert document.schema_version == SchemaVersion("2")
    assert document.retry_count == RetryCount(1)


def test_millisecond_timestamped_mixin_accepts_explicit_typed_values() -> None:
    document: MillisecondAuditDocument = MillisecondAuditDocument(
        created_at=Milliseconds(1_700_000_000_123),
        updated_at=Milliseconds(1_700_000_000_999),
        schema_version=SchemaVersion("2"),
        user_id=UserId("user_marty_mcfly"),
        retry_count=RetryCount(1),
    )

    assert document.created_at == Milliseconds(1_700_000_000_123)
    assert document.updated_at == Milliseconds(1_700_000_000_999)
    assert document.schema_version == SchemaVersion("2")
    assert document.retry_count == RetryCount(1)


def test_all_timestamp_field_descriptions_are_exposed_in_model_fields() -> None:
    assert_timestamp_field_descriptions(
        model_type=NanosecondAuditDocument,
        timestamp_unit_name="nanoseconds",
    )
    assert_timestamp_field_descriptions(
        model_type=MicrosecondAuditDocument,
        timestamp_unit_name="microseconds",
    )
    assert_timestamp_field_descriptions(
        model_type=MillisecondAuditDocument,
        timestamp_unit_name="milliseconds",
    )
