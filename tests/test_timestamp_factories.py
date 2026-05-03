from __future__ import annotations

import pytest
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds, WallClock

import base_pydantic_schemas._factories as timestamp_factories  # pyright: ignore[reportPrivateUsage]


class FixedUnixNanosecondFactory:
    """Deterministic factory returning one fixed UNIX nanosecond value."""

    def __init__(
        self,
        unix_nanoseconds: int,
    ) -> None:
        self._unix_nanoseconds: int = unix_nanoseconds

    def __call__(self) -> int:
        return self._unix_nanoseconds


def install_fixed_wall_clock(
    monkeypatch: pytest.MonkeyPatch,
    unix_nanoseconds: int,
) -> None:
    unix_nanosecond_factory: FixedUnixNanosecondFactory = FixedUnixNanosecondFactory(
        unix_nanoseconds=unix_nanoseconds,
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


def test_create_current_unix_nanoseconds_returns_typed_nanoseconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fixed_wall_clock(
        monkeypatch=monkeypatch,
        unix_nanoseconds=1_700_000_000_123_456_789,
    )

    unix_nanoseconds: Nanoseconds = (
        timestamp_factories.create_current_unix_nanoseconds()
    )

    assert unix_nanoseconds == Nanoseconds(1_700_000_000_123_456_789)
    assert isinstance(unix_nanoseconds, Nanoseconds)


def test_create_current_unix_microseconds_returns_typed_microseconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fixed_wall_clock(
        monkeypatch=monkeypatch,
        unix_nanoseconds=1_700_000_000_123_456_789,
    )

    unix_microseconds: Microseconds = (
        timestamp_factories.create_current_unix_microseconds()
    )

    assert unix_microseconds == Microseconds(1_700_000_000_123_456)
    assert isinstance(unix_microseconds, Microseconds)


def test_create_current_unix_milliseconds_returns_typed_milliseconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fixed_wall_clock(
        monkeypatch=monkeypatch,
        unix_nanoseconds=1_700_000_000_123_456_789,
    )

    unix_milliseconds: Milliseconds = (
        timestamp_factories.create_current_unix_milliseconds()
    )

    assert unix_milliseconds == Milliseconds(1_700_000_000_123)
    assert isinstance(unix_milliseconds, Milliseconds)
