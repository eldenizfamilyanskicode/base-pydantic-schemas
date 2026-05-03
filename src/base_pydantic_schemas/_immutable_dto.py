from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas._base_schema import BaseSchema


class ImmutableDTO(BaseSchema):
    """
    Strict immutable Data Transfer Object.

    Intended for value-like application data that should not change after
    construction.

    Configuration:
    - supports validation from object attributes
    - supports population by field name and alias
    - forbids undeclared fields
    - validates default values
    - uses strict Pydantic validation to avoid implicit coercion
    - freezes model instances after creation

    Use for query results, read models, domain-facing DTOs, and stable input
    snapshots.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        frozen=True,
        validate_default=True,
        strict=True,
    )
