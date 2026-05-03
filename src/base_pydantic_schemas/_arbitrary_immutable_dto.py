from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas._base_schema import BaseSchema


class ArbitraryImmutableDTO(BaseSchema):
    """
    Immutable DTO that allows arbitrary runtime types.

    Intended for value-like models that must carry non-Pydantic runtime objects
    while still preserving a frozen, explicit schema.

    Configuration:
    - supports validation from object attributes
    - supports population by field name and alias
    - forbids undeclared fields
    - allows arbitrary runtime types
    - validates default values
    - freezes model instances after creation
    - should stay strict for all fields that Pydantic can validate

    Prefer ImmutableDTO when arbitrary runtime types are not required.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        frozen=True,
        validate_default=True,
        strict=True,
    )
