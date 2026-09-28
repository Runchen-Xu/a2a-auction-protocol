"""Build and validate a marketplace.auction/v1 offer command."""

from a2a_auction_protocol import SubmitOfferPayload, command, validate_wire_message


payload = SubmitOfferPayload(
    auction_id="auction-123",
    offer={"amount": 15000},
    expected_version=5,
    source="manual",
)
envelope = command("submit_offer", "buyer-1", payload.model_dump(mode="json"))
validate_wire_message(envelope.model_dump(mode="json"))
print(envelope.model_dump_json(indent=2))
