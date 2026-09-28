from uuid import UUID

import pytest

from a2a_auction_protocol import (
    AgentRole,
    AuctionCapability,
    CommandResult,
    CreateAuctionPayload,
    MechanismId,
    PROTOCOL,
    command,
    command_fingerprint,
    load_schema,
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


def test_capability_advertises_roles_mechanisms_and_actions():
    capability = AuctionCapability(
        roles=[AgentRole.BUYER],
        mechanisms=[MechanismId.VICKREY],
        actions=["join_auction", "submit_offer"],
    )

    assert capability.supports(
        role=AgentRole.BUYER,
        mechanism=MechanismId.VICKREY,
        action="submit_offer",
    )
    assert not capability.supports(
        role=AgentRole.SELLER,
        mechanism=MechanismId.VICKREY,
        action="submit_offer",
    )
    assert "protocol:marketplace.auction/v1" in capability.tags()


def test_custom_mechanisms_do_not_require_a_new_package_version():
    capability = AuctionCapability(
        roles=[],
        mechanisms=["custom.score_auction"],
        actions=["submit_offer"],
    )

    assert capability.supports(mechanism="custom.score_auction", action="submit_offer")
    assert "mechanism:custom.score_auction" in capability.tags()


def test_product_url_is_an_absolute_http_url():
    payload = CreateAuctionPayload(
        title="linked item",
        start_price=1000,
        product_url="https://shop.example/items/123",
    )
    assert payload.product_url == "https://shop.example/items/123"

    with pytest.raises(ValueError, match="absolute http or https URL"):
        CreateAuctionPayload(title="invalid", start_price=1000, product_url="items/123")
