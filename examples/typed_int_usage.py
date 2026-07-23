from base_typed_int import BaseConstrainedTypedInt, BaseTypedInt

from base_pydantic_schemas import MutableDTO


class ImportedRecordCount(BaseTypedInt):
    """Unconstrained semantic count reported by an external source."""


class ImportBatchSize(BaseConstrainedTypedInt):
    """Import batch size accepted by the application."""

    ge = 1
    le = 1_000


class ImportBatchDTO(MutableDTO):
    """Command combining ordinary and constrained typed integers."""

    imported_record_count: ImportedRecordCount
    batch_size: ImportBatchSize


def main() -> None:
    import_batch: ImportBatchDTO = ImportBatchDTO.model_validate(
        {
            "imported_record_count": 12_500,
            "batch_size": 500,
        },
    )

    import_batch.batch_size = ImportBatchSize(750)

    assert type(import_batch.imported_record_count) is ImportedRecordCount
    assert type(import_batch.batch_size) is ImportBatchSize

    print(import_batch.model_dump(mode="json"))


if __name__ == "__main__":
    main()
