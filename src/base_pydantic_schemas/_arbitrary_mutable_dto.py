from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas._base_schema import BaseSchema


class ArbitraryMutableDTO(BaseSchema):
    """
    Mutable DTO that allows arbitrary runtime types.

    Intended for boundaries where a model must carry objects that Pydantic cannot
    fully validate through standard schemas, such as injected clients, handles,
    adapters, framework objects, or third-party runtime instances.

    Configuration:
    - supports validation from object attributes
    - supports population by field name and alias
    - forbids undeclared fields
    - allows arbitrary runtime types
    - validates field assignment after creation
    - validates default values
    - should stay strict for all fields that Pydantic can validate

    Prefer MutableDTO when arbitrary runtime types are not required.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
        strict=True,
    )
