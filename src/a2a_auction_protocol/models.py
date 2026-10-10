from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from urllib.parse import urlparse
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class AgentRole(StrEnum):
    """Legacy economic labels kept for compatibility with early clients.

    New protocol messages should use ``actor_id`` and mechanism-defined
    participation semantics instead of requiring buyer/seller roles.
    """

    SELLER = "seller"
    BUYER = "buyer"


class AuctionDirection(StrEnum):
    FORWARD = "forward"
    REVERSE = "reverse"


class AuctionStatus(StrEnum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    SOLD = "SOLD"
    CLOSED_NO_SALE = "CLOSED_NO_SALE"
    CANCELLED = "CANCELLED"


class OrderStatus(StrEnum):
    PENDING_SETTLEMENT = "PENDING_SETTLEMENT"


class StrategyName(StrEnum):
    CONSERVATIVE = "conservative"
    INCREMENTAL = "incremental"
    DEADLINE = "deadline"


VisibilityMode = Literal[
    "public",
    "participants",
    "seller",
    "authority",
    "sealed_until_close",
]


class MechanismId(StrEnum):
    ENGLISH = "english"
    FIRST_PRICE_SEALED = "first_price_sealed"
    VICKREY = "vickrey"
    DUTCH = "dutch"
    REVERSE_FIRST_PRICE = "reverse_first_price"
    REVERSE_VICKREY = "reverse_vickrey"
    REVERSE_MULTI_ATTRIBUTE = "reverse_multi_attribute"


class MechanismSpec(BaseModel):
    id: str = Field(default=MechanismId.ENGLISH.value, min_length=1, max_length=100)
    version: str = Field(default="1", min_length=1, max_length=20)
    rules: dict[str, Any] = Field(default_factory=dict)
    spec_hash: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")


class MechanismDefinition(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    human_spec: str = Field(
        default="",
        max_length=20000,
        description="Full natural-language explanation for human and LLM consumers.",
    )
    offer_schema: dict[str, Any]
    action_schema: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Machine-readable schema for mechanism actions such as submitting an offer, "
            "accepting a clock price, or exiting."
        ),
    )
    rules: dict[str, Any] = Field(default_factory=dict)
    settlement: dict[str, Any]
    formal_spec: dict[str, Any] = Field(
        default_factory=dict,
        description="Machine-readable semantics beyond the basic offer and settlement fields.",
    )
    implementation: dict[str, Any] = Field(
        default_factory=dict,
        description="Authority-owned implementation identity and execution boundary.",
    )
    participant_model: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Mechanism-defined participation semantics. The core protocol does not require "
            "buyer/seller roles; a mechanism may describe initiators, offerors, providers, "
            "requesters, or other domain-specific labels here."
        ),
    )
    field_visibility: dict[str, VisibilityMode] = Field(
        default_factory=dict,
        description="Visibility policy for offer and outcome fields.",
    )
    directions: list[AuctionDirection] = Field(
        default_factory=lambda: [AuctionDirection.FORWARD],
        description="Market directions in which this mechanism may be created.",
    )
    spec_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class A2ATransportContext(BaseModel):
    """The A2A identifiers which carry one marketplace command.

    These identifiers are transport metadata, not business identifiers. Keeping the
    mapping explicit lets a client correlate a command with an A2A task while the
    command_id remains stable across retries and bindings.
    """

    message_id: str | None = None
    context_id: str | None = None
    task_id: str | None = None


class FieldError(BaseModel):
    path: str
    message: str


class OutcomeView(BaseModel):
    """Mechanism-neutral public state and settlement projection."""

    values: dict[str, Any] = Field(default_factory=dict)
    winner_id: str | None = None
    clearing_price: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class GetMechanismPayload(BaseModel):
    mechanism_id: str = Field(min_length=1, max_length=100)
    version: str = Field(default="1", min_length=1, max_length=20)
    rules: dict[str, Any] = Field(default_factory=dict)
    auction_id: str | None = None


class CreateAuctionPayload(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=4000)
    image_url: str | None = None
    product_url: str | None = None
    category: str = Field(default="general", min_length=1, max_length=80)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    start_price: int = Field(gt=0)
    reserve_price: int | None = Field(default=None, gt=0)
    min_increment: int = Field(default=100, gt=0)
    duration_seconds: int = Field(default=30, ge=3, le=86400)
    anti_sniping_seconds: int = Field(default=5, ge=0, le=3600)
    max_extensions: int = Field(default=3, ge=0, le=100)
    direction: AuctionDirection = AuctionDirection.FORWARD
    mechanism: MechanismSpec = Field(default_factory=MechanismSpec)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("currency must be a three-letter ISO code")
        return value.upper()

    @field_validator("product_url")
    @classmethod
    def validate_product_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("product_url must be an absolute http or https URL")
        return value


class JoinAuctionPayload(BaseModel):
    auction_id: str
    accepted_mechanism_hash: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )


class SubmitOfferPayload(BaseModel):
    auction_id: str
    offer: dict[str, Any] = Field(min_length=1)
    expected_version: int | None = Field(default=None, ge=0)
    source: Literal["automatic", "manual"] = "manual"


class SubmitActionPayload(BaseModel):
    """Mechanism-neutral action envelope for dynamic and sealed auctions."""

    auction_id: str
    action_type: str = Field(min_length=1, max_length=80)
    action_data: dict[str, Any] = Field(default_factory=dict)
    expected_version: int | None = Field(default=None, ge=0)
    source: Literal["automatic", "manual"] = "manual"


class PlaceBidPayload(BaseModel):
    """Deprecated amount-only payload accepted for older clients."""

    auction_id: str
    amount: int = Field(gt=0)
    expected_version: int | None = Field(default=None, ge=0)
    source: Literal["automatic", "manual"] = "manual"


class CancelAuctionPayload(BaseModel):
    auction_id: str


class GetAuctionPayload(BaseModel):
    auction_id: str


class MarketUpdatePayload(BaseModel):
    auction: dict[str, Any]


class CommandEnvelope(BaseModel):
    protocol: Literal["marketplace.auction/v1"] = "marketplace.auction/v1"
    command_id: UUID
    action: str = Field(min_length=1, max_length=80)
    actor_id: str = Field(min_length=1, max_length=80)
    payload: dict[str, Any] = Field(default_factory=dict)


class ErrorBody(BaseModel):
    code: str
    message: str
    category: Literal[
        "validation",
        "authorization",
        "conflict",
        "lifecycle",
        "mechanism",
        "dependency",
        "internal",
    ] = "validation"
    retryable: bool = False
    fields: list[FieldError] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class CommandResult(BaseModel):
    protocol: Literal["marketplace.auction/v1"] = "marketplace.auction/v1"
    command_id: UUID
    status: Literal["accepted", "rejected"]
    data: dict[str, Any] = Field(default_factory=dict)
    error: ErrorBody | None = None
    a2a: A2ATransportContext | None = None

    @model_validator(mode="after")
    def result_is_consistent(self) -> CommandResult:
        if self.status == "rejected" and self.error is None:
            raise ValueError("rejected result requires an error")
        if self.status == "accepted" and self.error is not None:
            raise ValueError("accepted result cannot contain an error")
        return self


class AuctionCard(BaseModel):
    auction_id: str
    initiator_id: str | None = Field(
        default=None,
        description="Agent that created the auction or procurement request.",
    )
    title: str
    description: str
    image_url: str | None
    product_url: str | None = None
    category: str
    currency: str
    mechanism: MechanismSpec = Field(default_factory=MechanismSpec)
    mechanism_definition: MechanismDefinition | None = None
    start_price: int
    reserve_price: int | None
    min_increment: int
    status: AuctionStatus
    starts_at: datetime
    ends_at: datetime
    anti_sniping_seconds: int
    max_extensions: int
    extension_count: int
    current_price: int
    current_winner_agent_id: str | None
    current_outcome: OutcomeView = Field(default_factory=OutcomeView)
    version: int
    authority_agent_card_url: str
    direction: AuctionDirection = AuctionDirection.FORWARD
    participants: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Optional mechanism-defined participant labels mapped to agent IDs, for example "
            "{\"requester\": \"agent-1\"}."
        ),
    )
    # Compatibility fields from the pre-role-neutral draft. New producers should omit them.
    creator_id: str | None = Field(default=None, description="Legacy compatibility field.")
    seller_id: str | None = Field(default=None, description="Legacy compatibility field.")
    buyer_id: str | None = Field(default=None, description="Legacy compatibility field.")
    bidder_role: AgentRole | None = Field(default=None, description="Legacy compatibility field.")


class OrderView(BaseModel):
    order_id: str
    auction_id: str
    winner_id: str | None = None
    parties: dict[str, str] = Field(
        default_factory=dict,
        description="Mechanism-defined settlement parties mapped to agent IDs.",
    )
    currency: str
    final_price: int | None = Field(default=None, ge=0)
    status: OrderStatus
    created_at: datetime
    settlement: OutcomeView = Field(default_factory=OutcomeView)
    # Compatibility fields from the pre-role-neutral draft. New producers should omit them.
    seller_id: str | None = Field(default=None, description="Legacy compatibility field.")
    buyer_id: str | None = Field(default=None, description="Legacy compatibility field.")


class ParticipantConfig(BaseModel):
    participant_id: str
    budget: int = Field(gt=0)
    strategy: StrategyName
    authority_url: str


class BuyerConfig(BaseModel):
    """Legacy buyer-specific strategy configuration.

    New generic clients should use :class:`ParticipantConfig`.
    """

    buyer_id: str
    budget: int = Field(gt=0)
    strategy: StrategyName
    authority_url: str
