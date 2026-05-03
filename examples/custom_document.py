from base_typed_int import BaseTypedInt
from base_typed_string import BaseTypedString
from typed_time_provider import Milliseconds

from base_pydantic_schemas import (
    PersistentDocument,
    UnixMillisecondTimestampedMixin,
    VersionedMixin,
)


class OutboxMessageId(BaseTypedString):
    """Outbox message identifier."""


class AggregateId(BaseTypedString):
    """Domain aggregate identifier."""


class EventType(BaseTypedString):
    """Domain event type name."""


class EventPayloadJson(BaseTypedString):
    """Serialized event payload."""


class RetryCount(BaseTypedInt):
    """Number of delivery attempts."""


class OutboxMessageDocument(
    UnixMillisecondTimestampedMixin,
    VersionedMixin,
    PersistentDocument,
):
    """
    Custom persisted document.

    Uses millisecond timestamps because many queues, databases, and logs store
    event time in milliseconds.
    """

    message_id: OutboxMessageId
    aggregate_id: AggregateId
    event_type: EventType
    payload_json: EventPayloadJson
    retry_count: RetryCount = RetryCount(0)
    published_at: Milliseconds | None = None


def main() -> None:
    document: OutboxMessageDocument = OutboxMessageDocument(
        message_id=OutboxMessageId("outbox_message_001"),
        aggregate_id=AggregateId("user_marty_mcfly"),
        event_type=EventType("user.profile.updated"),
        payload_json=EventPayloadJson(
            '{"user_id":"user_marty_mcfly","city_name":"NewAmsterdam"}',
        ),
    )

    persistence_payload: dict[str, object] = document.model_dump(mode="json")

    print(persistence_payload)


if __name__ == "__main__":
    main()
