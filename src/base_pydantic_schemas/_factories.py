"""
Default timestamp factories used by timestamped mixins.

These factories exist for Pydantic Field(default_factory=...) integration.
Business logic should prefer dependency-injected WallClockInterface instances
from typed_time_provider instead of importing these functions directly.
"""

from typed_time_provider import Microseconds, Milliseconds, Nanoseconds, WallClock

_default_wall_clock: WallClock[Microseconds] = WallClock(
    preferred_time_unit_type=Microseconds,
)


def create_current_unix_nanoseconds() -> Nanoseconds:
    """
    Return the current wall-clock UNIX timestamp in typed nanoseconds.

    Intended for Pydantic default_factory usage in timestamped schema mixins.
    """
    return _default_wall_clock.now_unix(return_type=Nanoseconds)


def create_current_unix_microseconds() -> Microseconds:
    """
    Return the current wall-clock UNIX timestamp in typed microseconds.

    Intended for Pydantic default_factory usage in timestamped schema mixins.
    """
    return _default_wall_clock.now_unix()


def create_current_unix_milliseconds() -> Milliseconds:
    """
    Return the current wall-clock UNIX timestamp in typed milliseconds.

    Intended for Pydantic default_factory usage in timestamped schema mixins.
    """
    return _default_wall_clock.now_unix(return_type=Milliseconds)
