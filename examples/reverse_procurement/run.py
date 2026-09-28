"""Show a Buyer-led reverse procurement auction transcript."""

from __future__ import annotations

import json

from a2a_auction_protocol import CreateAuctionPayload, MechanismSpec, SubmitOfferPayload, command


HASH = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def show(label: str, value: object) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def main() -> None:
    requirement = CreateAuctionPayload(
        title="Deliver 100 packages",
        description="Buyer needs a logistics supplier for a three-day delivery window.",
        product_url="https://buyer.example/requirements/logistics-100",
        currency="USD",
        start_price=20_000,
        direction="reverse",
        mechanism=MechanismSpec(id="reverse_first_price", version="1"),
    )
    publish = command("create_auction", "buyer-requester", requirement.model_dump(mode="json"))
    show("1. Buyer -> Authority: reverse create_auction", publish.model_dump(mode="json"))

    card = {
        "auction_id": "reverse-auction-123",
        "buyer_id": "buyer-requester",
        "seller_id": None,
        "title": requirement.title,
        "description": requirement.description,
        "product_url": requirement.product_url,
        "direction": "reverse",
        "bidder_role": "seller",
        "status": "OPEN",
        "start_price": 20_000,
        "currency": "USD",
        "mechanism": {
            "id": "reverse_first_price",
            "version": "1",
            "rules": {},
            "spec_hash": HASH,
        },
        "authority_agent_card_url": "https://authority.example/.well-known/agent-card.json",
        "version": 1,
    }
    show("2. Authority -> Seller Agents: reverse AuctionCard", card)

    for seller_id, amount in (("seller-a", 15_000), ("seller-b", 13_000)):
        offer = SubmitOfferPayload(
            auction_id="reverse-auction-123",
            offer={"amount": amount},
            source="automatic",
        )
        message = command("submit_offer", seller_id, offer.model_dump(mode="json"))
        show(f"3. {seller_id} -> Authority: supplier offer", message.model_dump(mode="json"))

    show(
        "4. Authority: reverse settlement",
        {
            "winner_id": "seller-b",
            "seller_id": "seller-b",
            "buyer_id": "buyer-requester",
            "final_price": 13_000,
            "status": "PENDING_SETTLEMENT",
        },
    )


if __name__ == "__main__":
    main()
