from uuid import UUID

import pytest

from a2a_auction_protocol import (
    AuctionCapability,
    CommandResult,
    CreateAuctionPayload,
    MechanismId,
    PROTOCOL,
    SubmitActionPayload,
    command,
    command_fingerprint,
    compatibility_actions,
    load_schema,
    notification_catalog,
    operation_catalog,
    validate_wire_message,
)


def test_versioned_command_result_and_schema():
    envelope = command(
        "submit_offer",
        "buyer-1",
        {"auction_id": "auction-1", "offer": {"amount": 15000}},
    )
    validate_wire_message(envelope.model_dump(mode="json"))
    result = CommandResult(
        command_id=envelope.command_id,
        status="accepted",
        data={"accepted": True},
    )

    assert PROTOCOL == "marketplace.auction/v1"
    assert isinstance(envelope.command_id, UUID)
    assert result.command_id == envelope.command_id
    assert load_schema()["$id"] == "urn:a2a:marketplace.auction:v1"
    assert command_fingerprint(envelope) == command_fingerprint(envelope.model_copy(deep=True))


def test_capability_is_role_neutral_and_advertises_mechanisms_and_actions():
    capability = AuctionCapability(
        mechanisms=[MechanismId.VICKREY],
        actions=["join_auction", "submit_offer"],
    )

    assert capability.supports(
        mechanism=MechanismId.VICKREY,
        action="submit_offer",
    )
    assert "protocol:marketplace.auction/v1" in capability.tags()
    assert not any(tag.startswith("role:") for tag in capability.tags())


def test_custom_mechanisms_do_not_require_a_new_package_version():
    capability = AuctionCapability(
        roles=[],
        mechanisms=["custom.score_auction"],
        actions=["submit_offer"],
    )

    assert capability.supports(mechanism="custom.score_auction", action="submit_offer")
    assert "mechanism:custom.score_auction" in capability.tags()


def test_role_neutral_card_uses_initiator_and_participants():
    from a2a_auction_protocol import AuctionCard

    card = AuctionCard(
        auction_id="auction-1",
        initiator_id="agent-requester",
        title="Delivery contract",
        description="Three-day delivery service.",
        image_url=None,
        product_url="https://example.com/items/1",
        category="service",
        currency="USD",
        start_price=1000,
        reserve_price=None,
        min_increment=1,
        status="OPEN",
        starts_at="2026-10-07T00:00:00Z",
        ends_at="2026-10-07T00:05:00Z",
        anti_sniping_seconds=0,
        max_extensions=0,
        extension_count=0,
        current_price=1000,
        current_winner_agent_id=None,
        version=1,
        authority_agent_card_url="https://example.com/.well-known/agent-card.json",
        participants={"requester": "agent-requester"},
    )

    assert card.initiator_id == "agent-requester"
    assert card.participants == {"requester": "agent-requester"}
    assert card.seller_id is None
    assert card.buyer_id is None


def test_product_url_is_an_absolute_http_url():
    payload = CreateAuctionPayload(
        title="linked item",
        start_price=1000,
        product_url="https://shop.example/items/123",
    )
    assert payload.product_url == "https://shop.example/items/123"

    with pytest.raises(ValueError, match="absolute http or https URL"):
        CreateAuctionPayload(title="invalid", start_price=1000, product_url="items/123")


def test_canonical_operations_separate_notifications_and_compatibility_aliases():
    assert [item["action"] for item in operation_catalog()] == [
        "list_mechanisms",
        "get_mechanism",
        "create_auction",
        "join_auction",
        "submit_action",
        "cancel_auction",
        "get_auction",
    ]
    assert [item["action"] for item in notification_catalog()] == ["market_update"]
    assert compatibility_actions() == ["submit_offer", "observe_auction", "place_bid"]

    payload = SubmitActionPayload(
        auction_id="auction-1",
        action_type="submit_offer",
        action_data={"amount": 15000},
    )
    assert payload.action_data == {"amount": 15000}
