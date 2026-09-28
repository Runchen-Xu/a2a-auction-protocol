from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID, uuid4

from a2a_auction_protocol.models import CommandEnvelope, CommandResult, ErrorBody

PROTOCOL_NAMESPACE = "marketplace.auction"
PROTOCOL_VERSION = "1"
PROTOCOL = f"{PROTOCOL_NAMESPACE}/v{PROTOCOL_VERSION}"
JSON_MEDIA_TYPE = "application/json"
EXTENSION_URI = "urn:a2a:marketplace.auction:v1"


def command(
    action: str,
    actor_id: str,
    payload: dict[str, Any],
    command_id: UUID | None = None,
) -> CommandEnvelope:
    return CommandEnvelope(
        command_id=command_id or uuid4(),
        action=action,
        actor_id=actor_id,
        payload=payload,
    )


def accepted(envelope: CommandEnvelope, data: dict[str, Any] | None = None) -> CommandResult:
    return CommandResult(command_id=envelope.command_id, status="accepted", data=data or {})


def rejected(
    envelope: CommandEnvelope,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    *,
    category: str = "validation",
    retryable: bool = False,
    fields: list[dict[str, str]] | None = None,
) -> CommandResult:
    return CommandResult(
        command_id=envelope.command_id,
        status="rejected",
        error=ErrorBody(
            code=code,
            message=message,
            category=category,
            retryable=retryable,
            fields=fields or [],
            details=details or {},
        ),
    )


def command_fingerprint(envelope: CommandEnvelope) -> str:
    """Return a stable hash for idempotency-key conflict detection."""

    canonical = json.dumps(
        {
            "protocol": envelope.protocol,
            "action": envelope.action,
            "actor_id": envelope.actor_id,
            "payload": envelope.payload,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


class CommandRejected(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        *,
        category: str = "validation",
        retryable: bool = False,
        fields: list[dict[str, str]] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.category = category
        self.retryable = retryable
        self.fields = fields or []
