from __future__ import annotations

import pytest
from pydantic import ValidationError
from typed_time_provider import Microseconds, Milliseconds, Nanoseconds

from tests.testing_types import (
    ManualMicrosecondDocument,
    ManualMillisecondDocument,
    ManualNanosecondDocument,
    UserId,
)


def test_manual_nanosecond_document_roundtrip_restores_typed_fields() -> None:
    payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456_789,
        "updated_at": 1_700_000_000_123_456_999,
        "user_id": "user_marty_mcfly",
    }

    document: ManualNanosecondDocument = ManualNanosecondDocument.model_validate(
        payload,
    )

    assert document.created_at == Nanoseconds(1_700_000_000_123_456_789)
    assert document.updated_at == Nanoseconds(1_700_000_000_123_456_999)
    assert document.user_id == UserId("user_marty_mcfly")
    assert document.model_dump(mode="json") == payload


def test_manual_microsecond_document_roundtrip_restores_typed_fields() -> None:
    payload: dict[str, object] = {
        "created_at": 1_700_000_000_123_456,
        "updated_at": 1_700_000_000_123_999,
        "user_id": "user_marty_mcfly",
    }

    document: ManualMicrosecondDocument = ManualMicrosecondDocument.model_validate(
        payload,
    )

    assert document.created_at == Microseconds(1_700_000_000_123_456)
    assert document.updated_at == Microseconds(1_700_000_000_123_999)
    assert document.user_id == UserId("user_marty_mcfly")
    assert document.model_dump(mode="json") == payload


def test_manual_millisecond_document_roundtrip_restores_typed_fields() -> None:
    payload: dict[str, object] = {
        "created_at": 1_700_000_000_123,
        "updated_at": 1_700_000_000_999,
        "user_id": "user_marty_mcfly",
    }

    document: ManualMillisecondDocument = ManualMillisecondDocument.model_validate(
        payload,
    )

    assert document.created_at == Milliseconds(1_700_000_000_123)
    assert document.updated_at == Milliseconds(1_700_000_000_999)
    assert document.user_id == UserId("user_marty_mcfly")
    assert document.model_dump(mode="json") == payload


def test_manual_timestamp_documents_reject_string_timestamp_coercion() -> None:
    payload: dict[str, object] = {
        "created_at": "1_700_000_000_123_456",
        "updated_at": 1_700_000_000_123_999,
        "user_id": "user_marty_mcfly",
    }

    with pytest.raises(ValidationError):
        ManualMicrosecondDocument.model_validate(payload)
