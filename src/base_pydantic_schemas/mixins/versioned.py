from base_typed_string import BaseTypedString
from pydantic import Field

from base_pydantic_schemas._base_schema import BaseSchema


class SchemaVersion(BaseTypedString):
    """
    Typed persistence schema version.

    Represents the version of a persisted model shape, not the package version
    and not the application release version.

    Use this field for migration logic, backward compatibility checks, and
    explicit persisted document evolution.
    """


DEFAULT_SCHEMA_VERSION = SchemaVersion("1")


class VersionedMixin(BaseSchema):
    """
    Adds a typed schema_version field to a Pydantic model.

    The default version is "1". Applications can override schema_version in
    subclasses or during model construction when introducing explicit persistence
    migrations.
    """

    schema_version: SchemaVersion = Field(
        default=DEFAULT_SCHEMA_VERSION,
        description=(
            "Persistence schema version. This is not the package version or "
            "application release version."
        ),
    )
