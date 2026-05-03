from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas._base_schema import BaseSchema


class MutableDTO(BaseSchema):
    """
    Strict mutable Data Transfer Object.

    Intended for application boundaries where values may be updated after model
    creation, but the schema should remain explicit and strongly validated.

    Configuration:
    - supports validation from object attributes
    - supports population by field name and alias
    - forbids undeclared fields
    - validates field assignment after creation
    - validates default values
    - uses strict Pydantic validation to avoid implicit coercion

    Use for command models, mutable request-state objects, and internal DTOs that
    require controlled mutation.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        strict=True,
    )
