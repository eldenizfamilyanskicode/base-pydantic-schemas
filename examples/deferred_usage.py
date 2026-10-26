"""Opt into deferred construction without changing validation policies."""

from typing import ClassVar

from pydantic import ConfigDict

from base_pydantic_schemas.deferred import BaseDocument, MutableDTO


class UpdateQuantity(MutableDTO):
    """Command whose validator and serializer build on first use."""

    quantity: int


class InventoryDocument(BaseDocument):
    """Persisted quantity with typed timestamps and schema version."""

    quantity: int


class NamedCommand(UpdateQuantity):
    """Additional configuration preserves inherited defer_build."""

    model_config: ClassVar[ConfigDict] = ConfigDict(title="Named command")


class EagerCommand(UpdateQuantity):
    """A specific descendant can request eager construction."""

    model_config: ClassVar[ConfigDict] = ConfigDict(defer_build=False)


def main() -> None:
    assert not UpdateQuantity.__pydantic_complete__
    assert NamedCommand.model_config.get("defer_build") is True
    assert EagerCommand.__pydantic_complete__

    command = UpdateQuantity(quantity=3)
    assert UpdateQuantity.__pydantic_complete__
    document = InventoryDocument(quantity=command.quantity)
    payload: dict[str, object] = document.model_dump(mode="json")
    restored = InventoryDocument.model_validate(payload)
    assert restored == document
    print(restored.model_dump_json())


if __name__ == "__main__":
    main()
