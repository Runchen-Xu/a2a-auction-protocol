"""Build a creation payload with a canonical product page."""

from a2a_auction_protocol import CreateAuctionPayload, MechanismSpec, command


payload = CreateAuctionPayload(
    title="GPU",
    description="Used RTX 4090",
    product_url="https://shop.example/items/123",
    image_url="https://shop.example/images/123.jpg",
    start_price=10000,
    reserve_price=12000,
    mechanism=MechanismSpec(id="vickrey"),
)
envelope = command("create_auction", "seller-1", payload.model_dump(mode="json"))
print(envelope.model_dump_json(indent=2))
