"""Show an Authority-owned multi-attribute mechanism and its result."""

from __future__ import annotations

import json

from a2a_auction_protocol import command, validate_wire_message


HASH = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


MECHANISM = {
    "id": "acme.score_auction",
    "version": "1",
    "title": "Price, delivery, and quality score auction",
    "human_spec": (
        "The lowest score wins: price + delivery_days * 500 - quality_score * 100. "
        "Ties go to the earliest valid offer."
    ),
    "offer_schema": {
        "type": "object",
        "properties": {
            "price": {"type": "integer", "minimum": 1},
            "delivery_days": {"type": "integer", "minimum": 1},
            "quality_score": {"type": "integer", "minimum": 0, "maximum": 100},
        },
        "required": ["price", "delivery_days", "quality_score"],
        "additionalProperties": False,
    },
    "formal_spec": {
        "score_direction": "minimize",
        "score_formula": "price + delivery_days * 500 - quality_score * 100",
    },
    "settlement": {
        "winner_rule": "lowest_score",
        "price_rule": "winner_offer.price",
        "offer_visibility": "sealed_until_close",
    },
    "implementation": {
        "type": "authority_plugin",
        "id": "acme.score_auction",
        "version": "1",
    },
    "field_visibility": {"*": "sealed_until_close"},
    "directions": ["reverse"],
    "spec_hash": HASH,
}


def score(offer: dict[str, int]) -> int:
    return offer["price"] + offer["delivery_days"] * 500 - offer["quality_score"] * 100


def main() -> None:
    show = lambda label, value: print(
        f"\n=== {label} ===\n{json.dumps(value, indent=2, ensure_ascii=False)}"
    )
    show("1. Authority -> Agents: custom mechanism", MECHANISM)

    offers = {
        "seller-a": {"price": 15_000, "delivery_days": 3, "quality_score": 90},
        "seller-b": {"price": 14_500, "delivery_days": 6, "quality_score": 90},
        "seller-c": {"price": 16_000, "delivery_days": 2, "quality_score": 90},
    }
    for seller_id, offer in offers.items():
        message = command(
            "submit_offer",
            seller_id,
            {"auction_id": "reverse-auction-123", "offer": offer, "source": "automatic"},
        )
        validate_wire_message(message.model_dump(mode="json"))
        show(f"2. {seller_id} -> Authority: submit_offer", message.model_dump(mode="json"))

    winner, winning_offer = min(offers.items(), key=lambda item: score(item[1]))
    show(
        "3. Authority: custom settlement",
        {
            "winner_id": winner,
            "winning_offer": winning_offer,
            "score": score(winning_offer),
            "clearing_price": winning_offer["price"],
            "mechanism_spec_hash": HASH,
        },
    )


if __name__ == "__main__":
    main()
