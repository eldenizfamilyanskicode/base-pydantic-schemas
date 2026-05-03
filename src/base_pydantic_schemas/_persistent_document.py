from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas._base_schema import BaseSchema


class PersistentDocument(BaseSchema):
    """
    Strict persistence-neutral base model.

    Intended for models that are stored outside the running process, for example
    in a database, object store, search index, event log, or external persistence
    layer.

    This class intentionally does not define storage-specific serialization
    methods. Use Pydantic's native model_dump(), model_dump_json(), and
    model_validate() APIs at persistence boundaries.

    Configuration:
    - supports validation from object attributes
    - supports population by field name and alias
    - forbids undeclared fields
    - validates field assignment after creation
    - validates default values
    - uses strict Pydantic validation to avoid implicit coercion

    Use directly when a persisted model needs custom metadata. Use BaseDocument
    when the default created_at, updated_at, and schema_version fields are enough.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        strict=True,
    )
