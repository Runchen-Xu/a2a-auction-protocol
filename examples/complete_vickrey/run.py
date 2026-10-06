"""Run a complete, transport-neutral Vickrey protocol transcript."""

from __future__ import annotations

import json

from a2a_auction_protocol import (
    CreateAuctionPayload,
    MechanismSpec,
    SubmitOfferPayload,
    command,
    validate_wire_message,
)


HASH = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def show(label: str, value: object) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def main() -> None:
    create_payload = CreateAuctionPayload(
        title="RTX 4090 GPU",
        description="Used GPU in working condition.",
        product_url="https://shop.example/items/gpu-4090",
        image_url="https://shop.example/images/gpu-4090.jpg",
        currency="USD",
        start_price=10_000,
        reserve_price=12_000,
        mechanism=MechanismSpec(id="vickrey", version="1"),
    )
    create = command("create_auction", "seller-1", create_payload.model_dump(mode="json"))
    validate_wire_message(create.model_dump(mode="json"))
    show("1. Initiator -> Authority: create_auction", create.model_dump(mode="json"))

    auction = {
        "auction_id": "auction-123",
        "initiator_id": "seller-1",
        "title": create_payload.title,
        "description": create_payload.description,
        "product_url": create_payload.product_url,
        "image_url": create_payload.image_url,
        "currency": create_payload.currency,
        "mechanism": {
            "id": "vickrey",
            "version": "1",
            "rules": {},
            "spec_hash": HASH,
        },
        "start_price": create_payload.start_price,
        "reserve_price": create_payload.reserve_price,
        "min_increment": create_payload.min_increment,
        "status": "OPEN",
        "current_price": create_payload.start_price,
        "current_winner_agent_id": None,
        "version": 1,
        "authority_agent_card_url": "https://authority.example/.well-known/agent-card.json",
        "direction": "forward",
        "participants": {},
    }
    show("2. Authority -> Broker/Participants: AuctionCard", auction)

    join = command(
        "join_auction",
        "buyer-1",
        {"auction_id": "auction-123", "accepted_mechanism_hash": HASH},
    )
    show("3. Participant -> Authority: join_auction", join.model_dump(mode="json"))

    offers = []
    for buyer_id, amount in (("buyer-1", 19_000), ("buyer-2", 17_000)):
        payload = SubmitOfferPayload(
            auction_id="auction-123",
            offer={"amount": amount},
            expected_version=4,
            source="automatic",
        )
        offer = command("submit_offer", buyer_id, payload.model_dump(mode="json"))
        validate_wire_message(offer.model_dump(mode="json"))
        offers.append((buyer_id, amount))
        show(f"4. {buyer_id} -> Authority: sealed submit_offer", offer.model_dump(mode="json"))

    winner, winning_offer = max(offers, key=lambda item: item[1])
    second_price = sorted((amount for _, amount in offers), reverse=True)[1]
    final = {
        **auction,
        "status": "SOLD",
        "current_price": second_price,
        "current_winner_agent_id": winner,
        "current_outcome": {
            "values": {
                "winning_offer": {"amount": winning_offer},
                "second_highest_offer": {"amount": second_price},
            },
            "winner_id": winner,
            "clearing_price": second_price,
            "currency": "USD",
        },
        "version": 7,
    }
    order = {
        "order_id": "order-123",
        "auction_id": "auction-123",
        "winner_id": winner,
        "parties": {
            "initiator": "seller-1",
            "winner": winner,
        },
        "currency": "USD",
        "final_price": second_price,
        "status": "PENDING_SETTLEMENT",
    }
    show("5. Authority: final AuctionCard", final)
    show("6. Authority: Order", order)


if __name__ == "__main__":
    main()
