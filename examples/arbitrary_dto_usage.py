from collections.abc import Callable

from base_typed_string import BaseTypedString

from base_pydantic_schemas import ArbitraryMutableDTO, ImmutableDTO


class UserId(BaseTypedString):
    """Application user identifier."""


class DisplayName(BaseTypedString):
    """Public display name."""


class ImportSourceName(BaseTypedString):
    """Name of external import source."""


class ImportedUserRow(ImmutableDTO):
    """
    Immutable row parsed at integration boundary.

    In real projects this can be produced from CSV, Kafka, S3 object, HTTP stream,
    database cursor, or another external source.
    """

    external_user_id: UserId
    display_name: DisplayName


class UserImportedEvent(ImmutableDTO):
    """Application event produced after importing one user."""

    imported_user_id: UserId
    display_name: DisplayName


class NewAmsterdamUserImportIterator:
    """
    Runtime iterator object.

    This class intentionally has state. It should not be converted into a plain
    list just to satisfy schema validation.
    """

    def __init__(
        self,
        rows: tuple[ImportedUserRow, ...],
    ) -> None:
        self._rows: tuple[ImportedUserRow, ...] = rows
        self._next_row_index: int = 0

    def __iter__(self) -> "NewAmsterdamUserImportIterator":
        return self

    def __next__(self) -> ImportedUserRow:
        if self._next_row_index >= len(self._rows):
            raise StopIteration

        current_row: ImportedUserRow = self._rows[self._next_row_index]
        self._next_row_index = self._next_row_index + 1

        return current_row


class UserImportBoundaryJob(ArbitraryMutableDTO):
    """
    Boundary DTO carrying runtime-only dependencies.

    ArbitraryMutableDTO is useful here because record_iterator is a runtime object,
    and publish_user_imported_event is a function dependency.
    """

    source_name: ImportSourceName
    record_iterator: NewAmsterdamUserImportIterator
    publish_user_imported_event: Callable[[UserImportedEvent], None]


def publish_user_imported_event(user_imported_event: UserImportedEvent) -> None:
    printed_payload: dict[str, object] = user_imported_event.model_dump(mode="json")
    print(printed_payload)


def run_import_job(import_job: UserImportBoundaryJob) -> None:
    for imported_user_row in import_job.record_iterator:
        user_imported_event: UserImportedEvent = UserImportedEvent(
            imported_user_id=imported_user_row.external_user_id,
            display_name=imported_user_row.display_name,
        )

        import_job.publish_user_imported_event(user_imported_event)


def main() -> None:
    imported_rows: tuple[ImportedUserRow, ...] = (
        ImportedUserRow(
            external_user_id=UserId("external_user_marty_mcfly"),
            display_name=DisplayName("Marty McFly"),
        ),
    )

    record_iterator: NewAmsterdamUserImportIterator = NewAmsterdamUserImportIterator(
        rows=imported_rows,
    )

    import_job: UserImportBoundaryJob = UserImportBoundaryJob(
        source_name=ImportSourceName("NewAmsterdam"),
        record_iterator=record_iterator,
        publish_user_imported_event=publish_user_imported_event,
    )

    run_import_job(import_job)


if __name__ == "__main__":
    main()
