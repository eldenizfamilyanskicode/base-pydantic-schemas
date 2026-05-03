from typing import Any


def assign_runtime_value(
    target_object: object,
    field_name: str,
    field_value: Any,
) -> None:
    """
    Assign a value through a dynamic runtime boundary.

    Use this only in tests that intentionally verify Pydantic runtime assignment
    validation with values that static type checkers should reject.
    """

    setattr(target_object, field_name, field_value)
