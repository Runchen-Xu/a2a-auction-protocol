"""The normative operation catalog for marketplace.auction/v1.

The catalog is intentionally small and transport-neutral. A2A JSON-RPC carries the
messages, while these definitions describe the business operation contract. Compatibility
aliases remain accepted by reference services but are not part of the canonical catalog.
"""

from __future__ import annotations

from typing import Any

OPERATION_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "action": "list_mechanisms",
        "request_schema": "#/definitions/emptyPayload",
        "result_schema": "#/definitions/mechanismListResult",
        "idempotent": True,
        "mutates_state": False,
        "async": False,
    },
    {
        "action": "get_mechanism",
        "request_schema": "#/definitions/getMechanismPayload",
        "result_schema": "#/definitions/mechanismResult",
        "idempotent": True,
        "mutates_state": False,
        "async": False,
    },
    {
        "action": "create_auction",
        "request_schema": "#/definitions/createAuctionPayload",
        "result_schema": "#/definitions/auctionResult",
        "idempotent": True,
        "mutates_state": True,
        "async": False,
    },
    {
        "action": "join_auction",
        "request_schema": "#/definitions/joinAuctionPayload",
        "result_schema": "#/definitions/auctionResult",
        "idempotent": True,
        "mutates_state": True,
        "async": False,
    },
    {
        "action": "submit_action",
        "request_schema": "#/definitions/submitActionPayload",
        "result_schema": "#/definitions/actionResult",
        "idempotent": True,
        "mutates_state": True,
        "async": False,
    },
    {
        "action": "cancel_auction",
        "request_schema": "#/definitions/cancelAuctionPayload",
        "result_schema": "#/definitions/auctionResult",
        "idempotent": True,
        "mutates_state": True,
        "async": False,
    },
    {
        "action": "get_auction",
        "request_schema": "#/definitions/getAuctionPayload",
        "result_schema": "#/definitions/auctionResult",
        "idempotent": True,
        "mutates_state": False,
        "async": False,
    },
)

NOTIFICATION_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "action": "market_update",
        "request_schema": "#/definitions/marketUpdatePayload",
        "result_schema": "#/definitions/emptyResult",
        "idempotent": True,
        "mutates_state": False,
        "async": True,
    },
)

COMPATIBILITY_ACTIONS: tuple[str, ...] = (
    "submit_offer",
    "observe_auction",
    "place_bid",
)


def operation_catalog() -> list[dict[str, Any]]:
    return [dict(item) for item in OPERATION_CATALOG]


def notification_catalog() -> list[dict[str, Any]]:
    return [dict(item) for item in NOTIFICATION_CATALOG]


def compatibility_actions() -> list[str]:
    return list(COMPATIBILITY_ACTIONS)
