from __future__ import annotations

import pytest
from pydantic import PydanticSchemaGenerationError, ValidationError

from base_pydantic_schemas import MutableDTO
from tests.runtime_boundary import assign_runtime_value
from tests.testing_types import (
    ArbitraryImmutableImportJobDTO,
    ArbitraryMutableImportJobDTO,
    DisplayName,
    ImportedUserEvent,
    RuntimeDatabaseSession,
    SourceName,
    UserId,
    create_arbitrary_immutable_import_job,
    create_arbitrary_mutable_import_job,
    publish_imported_user_event,
)


def test_arbitrary_mutable_dto_accepts_runtime_objects_and_callables() -> None:
    import_job: ArbitraryMutableImportJobDTO = create_arbitrary_mutable_import_job()

    assert import_job.source_name == SourceName("NewAmsterdam")
    assert isinstance(import_job.database_session, RuntimeDatabaseSession)
    assert import_job.database_session.session_name == SourceName(
        "new_amsterdam_import",
    )
    assert import_job.publish_imported_user_event is publish_imported_user_event


def test_arbitrary_mutable_dto_validates_assignment_for_runtime_objects() -> None:
    import_job: ArbitraryMutableImportJobDTO = create_arbitrary_mutable_import_job()
    replacement_session: RuntimeDatabaseSession = RuntimeDatabaseSession(
        session_name=SourceName("replacement_import"),
    )

    import_job.database_session = replacement_session

    assert import_job.database_session is replacement_session

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=import_job,
            field_name="database_session",
            field_value=object(),
        )

    with pytest.raises(ValidationError):
        assign_runtime_value(
            target_object=import_job,
            field_name="publish_imported_user_event",
            field_value="not_callable",
        )


def test_arbitrary_immutable_dto_accepts_runtime_objects() -> None:
    import_job: ArbitraryImmutableImportJobDTO = create_arbitrary_immutable_import_job()

    assert import_job.source_name == SourceName("NewAmsterdam")
    assert isinstance(import_job.database_session, RuntimeDatabaseSession)
    assert import_job.publish_imported_user_event is publish_imported_user_event


def test_arbitrary_immutable_dto_rejects_assignment() -> None:
    import_job: ArbitraryImmutableImportJobDTO = create_arbitrary_immutable_import_job()
    replacement_session: RuntimeDatabaseSession = RuntimeDatabaseSession(
        session_name=SourceName("replacement_import"),
    )

    with pytest.raises(ValidationError):
        import_job.database_session = replacement_session


def test_arbitrary_dto_callable_dependency_can_be_invoked() -> None:
    captured_events: list[ImportedUserEvent] = []

    def capture_imported_user_event(
        imported_user_event: ImportedUserEvent,
    ) -> None:
        captured_events.append(imported_user_event)

    import_job: ArbitraryMutableImportJobDTO = ArbitraryMutableImportJobDTO(
        source_name=SourceName("NewAmsterdam"),
        database_session=RuntimeDatabaseSession(
            session_name=SourceName("runtime_session"),
        ),
        publish_imported_user_event=capture_imported_user_event,
    )

    imported_user_event: ImportedUserEvent = ImportedUserEvent(
        user_id=UserId("user_marty_mcfly"),
        display_name=DisplayName("Marty McFly"),
    )

    import_job.publish_imported_user_event(imported_user_event)

    assert captured_events == [imported_user_event]


def test_regular_dto_rejects_unknown_runtime_type_at_model_definition() -> None:
    with pytest.raises(PydanticSchemaGenerationError):

        class InvalidRuntimeBoundaryDTO(MutableDTO):
            database_session: RuntimeDatabaseSession

        _ = InvalidRuntimeBoundaryDTO
