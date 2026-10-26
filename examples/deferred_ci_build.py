"""Check an explicit application model list in CI after defining references."""

from __future__ import annotations

from pydantic import BaseModel

from base_pydantic_schemas.deferred import BaseDocument, ImmutableDTO, MutableDTO


class CreateInventoryCommand(MutableDTO):
    """Command with a reference to a model defined later."""

    item: InventoryItem


class InventoryItem(ImmutableDTO):
    """Application-owned item definition."""

    name: str
    quantity: int


class InventoryDocument(BaseDocument):
    """Application-owned persistence model."""

    item: InventoryItem


APPLICATION_MODELS: tuple[type[BaseModel], ...] = (
    CreateInventoryCommand,
    InventoryItem,
    InventoryDocument,
)


def main() -> None:
    for model in APPLICATION_MODELS:
        model.model_rebuild(force=True)
    print("Application model schemas built successfully.")


if __name__ == "__main__":
    main()
