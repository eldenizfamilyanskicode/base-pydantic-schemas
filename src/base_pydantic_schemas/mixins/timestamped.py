from pydantic import Field
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds

from base_pydantic_schemas._base_schema import BaseSchema
from base_pydantic_schemas._factories import (
    create_current_unix_microseconds,
    create_current_unix_milliseconds,
    create_current_unix_nanoseconds,
)


class UnixNanosecondTimestampedMixin(BaseSchema):
    """
    Adds creation and update timestamps in typed UNIX nanoseconds.

    Fields:
    - created_at: wall-clock UNIX timestamp captured at model creation
    - updated_at: wall-clock UNIX timestamp captured at model creation

    The two fields use independent default factories and are not guaranteed to
    have the same value.
    """

    created_at: Nanoseconds = Field(
        default_factory=create_current_unix_nanoseconds,
        description="Creation wall-clock UNIX timestamp in nanoseconds.",
    )

    updated_at: Nanoseconds = Field(
        default_factory=create_current_unix_nanoseconds,
        description="Last update wall-clock UNIX timestamp in nanoseconds.",
    )


class UnixMicrosecondTimestampedMixin(BaseSchema):
    """
    Adds creation and update timestamps in typed UNIX microseconds.

    This is the default timestamp precision used by BaseDocument. It is usually
    precise enough for application persistence while staying compact and easy to
    inspect.

    Fields:
    - created_at: wall-clock UNIX timestamp captured at model creation
    - updated_at: wall-clock UNIX timestamp captured at model creation

    The two fields use independent default factories and are not guaranteed to
    have the same value.
    """

    created_at: Microseconds = Field(
        default_factory=create_current_unix_microseconds,
        description="Creation wall-clock UNIX timestamp in microseconds.",
    )

    updated_at: Microseconds = Field(
        default_factory=create_current_unix_microseconds,
        description="Last update wall-clock UNIX timestamp in microseconds.",
    )


class UnixMillisecondTimestampedMixin(BaseSchema):
    """
    Adds creation and update timestamps in typed UNIX milliseconds.

    Useful when persisted timestamps should match systems that store time in
    millisecond precision.

    Fields:
    - created_at: wall-clock UNIX timestamp captured at model creation
    - updated_at: wall-clock UNIX timestamp captured at model creation

    The two fields use independent default factories and are not guaranteed to
    have the same value.
    """

    created_at: Milliseconds = Field(
        default_factory=create_current_unix_milliseconds,
        description="Creation wall-clock UNIX timestamp in milliseconds.",
    )

    updated_at: Milliseconds = Field(
        default_factory=create_current_unix_milliseconds,
        description="Last update wall-clock UNIX timestamp in milliseconds.",
    )
