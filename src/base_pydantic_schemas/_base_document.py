from base_pydantic_schemas._persistent_document import PersistentDocument
from base_pydantic_schemas.mixins.timestamped import UnixMicrosecondTimestampedMixin
from base_pydantic_schemas.mixins.versioned import VersionedMixin


class BaseDocument(
    UnixMicrosecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """
    Default persistence document base.

    Combines:
    - PersistentDocument validation configuration
    - created_at and updated_at UNIX timestamps in typed microseconds
    - schema_version for persistence schema evolution

    This is the main convenience base for persisted application documents.

    The timestamp fields are captured independently through default factories.
    They are not guaranteed to be identical at microsecond precision.

    Use PersistentDocument plus explicit mixins when another timestamp precision
    or custom metadata layout is required.
    """
