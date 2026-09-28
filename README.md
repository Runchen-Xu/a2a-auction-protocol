# a2a-auction-protocol

Reusable Pydantic models and helpers for the `marketplace.auction/v1` business protocol carried
inside A2A JSON-RPC messages.

## Install

```bash
uv add a2a-auction-protocol
```

The package targets Python 3.13. It can also be installed from a checkout while developing:

```bash
uv add git+https://github.com/Runchen-Xu/a2a-auction-protocol
```

## What This Package Defines

The protocol is a business contract layered on A2A:

```text
A2A JSON-RPC and DataPart  ->  transport binding
marketplace.auction/v1     ->  auction commands and result shapes
Authority implementation    ->  state, mechanism execution, and settlement
```

It defines commands, AuctionCard, offers, mechanism descriptions, capability declarations,
idempotency identifiers, visibility policies, and the normative JSON Schema. Discovery may be
provided by a Broker or another catalog; Broker is not a required protocol role.

The protocol has two participant roles, `seller` and `buyer`. An auction names its authoritative
Agent through `authority_agent_card_url`. An Authority may implement built-in or custom mechanism
IDs; the selected mechanism definition and `spec_hash` are negotiated before joining and frozen
for the auction.

This repository is intentionally not a marketplace server. It does not include a database, HTTP
service, payment system, or winner-selection engine.

This package deliberately does not contain a database, HTTP server, market catalog, payment
implementation, or auction state machine. It provides the shared wire contract that independent
auction authorities, Seller Agents, Buyer Agents, and clients can use.

It also ships the normative JSON Schema and operation catalog. Use `validate_wire_message()` at
an integration boundary when a client or service is not implemented in Python:

```python
from a2a_auction_protocol import command, validate_wire_message

message = command("get_auction", "buyer-1", {"auction_id": "auction-123"})
validate_wire_message(message.model_dump(mode="json"))
```

The schema describes the marketplace DataPart, while A2A JSON-RPC remains the transport binding.
`CommandResult.a2a` carries A2A message, context, and task correlation identifiers without making
them part of the business `command_id` or auction state machine.

```python
from a2a_auction_protocol import SubmitOfferPayload, command

payload = SubmitOfferPayload(auction_id="auction-123", offer={"amount": 15000})
envelope = command("submit_offer", "buyer-1", payload.model_dump(mode="json"))
```

`CreateAuctionPayload.product_url` optionally carries the canonical HTTP(S) product page, while
`image_url` carries a product image. The link is copied into `AuctionCard` and is informational;
the Authority remains authoritative for the frozen auction state and settlement.

For a full reference implementation with Broker, Authority, Seller, Buyer, SQLite persistence,
and runnable mechanism samples, see the companion `a2a-auction-marketplace` project.

`AuctionCapability` helps an Agent describe supported roles, mechanisms, and actions in its
AgentCard. The protocol version is `marketplace.auction/v1`; individual mechanism versions are
negotiated through `get_mechanism`; the selected definition and `spec_hash` are frozen into the
AuctionCard, and Buyers echo that hash when joining. Mechanism IDs are open strings, so an authority can advertise
`custom.immediate` or another local mechanism without changing the shared protocol package.

Each definition can carry a `human_spec` for a detailed natural-language explanation, a
`formal_spec` for machine-readable semantics, and an `implementation` descriptor for the
Authority-owned deterministic plugin. Natural language is explanatory; it is not by itself the
arbiter of winners or prices. `field_visibility` controls which offer and outcome fields can be
published while an auction is open, including `public`, `sealed_until_close`, `seller`, and
`authority` policies.

The participant roles are `seller` and `buyer`. An auction authority is identified by the
`authority_agent_card_url` in each `AuctionCard`, then discovered by its supported actions and
mechanisms rather than a mandatory role name. The authority is the sole source of valid state
versions and settlement results for that auction. A Broker remains marketplace infrastructure:
it may expose registration and a public catalog through REST without extending this protocol.
