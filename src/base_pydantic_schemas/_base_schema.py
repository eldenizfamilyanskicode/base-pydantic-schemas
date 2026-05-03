from pydantic import BaseModel


class BaseSchema(BaseModel):
    """
    Root Pydantic model for this package.

    BaseSchema intentionally does not define model_config. Concrete base classes
    choose their own validation policy, mutability, strictness, and arbitrary-type
    behavior.

    Use this class when you want a shared root type but do not want to inherit
    DTO or persistence-specific configuration.
    """
