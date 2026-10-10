# A2A Auction Protocol

An extensible auction business protocol for AI Agents communicating over A2A.

It defines interoperable auction commands, AuctionCards, mechanism descriptions, offers, outcomes,
and settlement results for the `marketplace.auction/v1` protocol. This repository provides reusable
Pydantic models, validation helpers, JSON Schema, and runnable examples as a Python reference
implementation.

![A2A auction protocol overview](assets/a2a-auction-protocol-overview.png)

The diagram shows the core flow: an Initiator publishes an item or requirement, a Broker exposes
the auction, Participants read the AuctionCard and submit offers, and the Authority applies the
frozen mechanism to produce the authoritative order.

## Background

Agent-to-Agent (A2A) communication makes it possible for independent agents to discover one
another and exchange messages, but communication alone does not define how an economic interaction
should work. An agent may need to buy a product, procure a service, allocate a scarce resource, or
select a supplier from several autonomous offers. Without a shared business contract, every pair
of agents must invent its own fields, bidding rules, result format, and interpretation of failure.

An auction is a useful coordination primitive for this setting because it makes competition,
eligibility, visibility, winner selection, and settlement explicit. The challenge is that an A2A
auction must support more than a single price field: different authorities may use sealed bids,
second-price settlement, reverse procurement, multi-attribute scoring, or a new mechanism that was
not known when the client was written.

`marketplace.auction/v1` provides that shared business layer. It lets independent Initiators,
Participants, Brokers, and Authorities communicate using a common contract while leaving the
actual mechanism innovation with the Authority.

## Why It Matters

The protocol is useful for four related reasons:

1. **Interoperability.** A Participant can recognize an auction capability from an AgentCard and
   use the same command and result shapes with independent implementations.
2. **Mechanism transparency.** Participants can inspect the offer schema, winner rule, settlement rule,
   visibility policy, and natural-language explanation before joining.
3. **Authority and safety boundaries.** An LLM Agent may propose an offer, but the Authority owns
   state transitions, concurrency, winner selection, and settlement. A model cannot rewrite the
   auction rules by producing a different answer.
4. **Auditability and extensibility.** A frozen mechanism definition, `spec_hash`, command ID,
   auction version, events, and structured order make an outcome explainable. Custom mechanisms can
   be added without changing the core command envelope.

This makes the protocol useful both as an engineering interoperability layer and as a research
boundary for studying how autonomous or LLM-based agents behave under explicit market mechanisms.

## Contributions

This project makes five focused contributions on top of A2A:

1. **A reusable auction business protocol.** It defines a stable `marketplace.auction/v1`
   envelope for commands, results, AuctionCards, offers, mechanism descriptions, and orders. A2A
   supplies the agent-to-agent transport; this project supplies the auction semantics that A2A
   intentionally leaves to applications.
2. **Mechanism-neutral extensibility.** The protocol is not tied to one auction format. It can
   describe English, first-price, Vickrey, Dutch, reverse, multi-attribute, and Authority-defined
   mechanisms through an open mechanism identifier, offer schema, visibility policy, winner rule,
   settlement rule, and tie-breaker.
3. **Explicit rule understanding and freezing.** Participants can inspect a machine-readable
   `formal_spec`, a human-readable `human_spec`, and an executable implementation identity before
   joining. The selected definition is frozen by `spec_hash`, so a mechanism cannot silently change
   after an auction begins.
4. **A clear authority and audit boundary.** The Authority is the source of valid state versions,
   offer validation, winner selection, and settlement results. Command IDs, optimistic versions,
   structured outcomes, and A2A correlation identifiers make duplicate requests and auction results
   easier to audit. LLM Agents may reason or propose offers, but they do not override these rules.
5. **A common basis for AI-agent auction research.** Because different agents can use the same
   wire contract and the same frozen mechanism, researchers can compare prompts, models, valuation
   information, budgets, bidding strategies, efficiency, welfare, revenue, and regret without
   changing the communication layer for every experiment. The protocol is therefore a research
   enabler, not a claim that this repository itself proves that LLM Agents are economically rational.

The project deliberately does **not** claim to be a new version of the A2A standard. It is an
application-level protocol that uses A2A as its transport and message envelope. It also does not
provide a universal payment, identity, reputation, delivery, or dispute-resolution standard;
those concerns remain concrete implementation or domain choices.

## Application Scenarios

- **Agent commerce:** autonomous buyers compete for products, digital goods, or scarce inventory.
- **Reverse procurement:** an Initiator publishes a requirement and provider agents compete on price,
  delivery, quality, or other attributes.
- **Service marketplaces:** agents bid to perform tasks such as delivery, data collection,
  translation, or software work.
- **Resource allocation:** agents compete for compute capacity, API quotas, laboratory equipment,
  network bandwidth, or time slots.
- **Multi-attribute contracting:** an Authority scores price, quality, delivery time, reliability,
  and other attributes instead of ranking offers by price alone.
- **Mechanism research:** researchers compare truthful bidding, strategic shading, risk-taking,
  LLM prompting, welfare, revenue, efficiency, and regret under a common protocol.

The protocol is intentionally not a payment network or a complete marketplace. Payment, delivery,
identity, authentication, reputation, and dispute resolution can be layered on later by a concrete
implementation.

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

The canonical operation surface is intentionally small:

```text
list_mechanisms  get_mechanism  create_auction  join_auction
submit_action    cancel_auction  get_auction
```

`market_update` is an asynchronous notification, not a participant request. `submit_offer` is
the compatibility spelling for a sealed offer, and `observe_auction` is an alias for
`get_auction`; reference services may continue to accept both aliases without advertising them
as canonical operations. `place_bid` is retained only for older clients.

For one-shot mechanisms, clients can use `submit_offer`. For dynamic mechanisms, clients should
read `mechanism_definition.action_schema` from the AuctionCard and use the generic `submit_action`
operation. The reference marketplace currently exposes these action mappings:

| Mechanism | Actions | Meaning |
| --- | --- | --- |
| `first_price_sealed` / `vickrey` | `submit_offer`, `exit` | Submit one sealed offer or abstain by exiting |
| `english` | `raise_bid`, `exit` | Raise the public price or leave the auction |
| `dutch` | `accept_current_price`, `exit` | Accept the Authority's current clock price or leave |

Example action carried as an A2A JSON `DataPart`:

```json
{
  "protocol": "marketplace.auction/v1",
  "command_id": "uuid",
  "action": "submit_action",
  "actor_id": "participant-1",
  "payload": {
    "auction_id": "auction-001",
    "action_type": "accept_current_price",
    "action_data": {"observed_price": 1500},
    "expected_version": 8,
    "source": "manual"
  }
}
```

The Authority recomputes the current clock price and applies the action atomically. Action
schemas, visibility, settlement rules, and implementation identity are included in the frozen
mechanism definition and covered by its `spec_hash`. `submit_offer` remains supported for
backward compatibility.

The core protocol is role-neutral. Commands identify the sender with `actor_id`; an AuctionCard
identifies the creator with `initiator_id`; and a mechanism may describe its own participant
labels in `participant_model`. Terms such as `buyer`, `seller`, `requester`, and `provider` are
optional domain labels, not mandatory fields in every auction. An auction names its authoritative
Agent through `authority_agent_card_url`. An Authority may implement built-in or custom mechanism
IDs; the selected mechanism definition and `spec_hash` are negotiated before joining and frozen
for the auction.

This repository is intentionally not a marketplace server. It does not include a database, HTTP
service, payment system, or winner-selection engine.

## Runnable Examples

The repository includes complete, transport-neutral transcripts rather than only isolated model
snippets:

```bash
uv run python examples/complete_vickrey/run.py
uv run python examples/custom_multi_attribute/run.py
uv run python examples/reverse_procurement/run.py
```

The `complete_vickrey` example covers Initiator creation, AuctionCard publication, mechanism
acceptance, sealed offers, second-price settlement, and order creation. The custom and reverse
examples show how the same envelope supports Authority-owned scoring and initiator-led procurement.
Raw JSON DataPart examples for non-Python clients are in [`examples/raw_a2a`](examples/raw_a2a),
with a directory guide in [`examples/README.md`](examples/README.md).

## End-to-End Example

The following example shows a forward Vickrey auction for a product page. The snippets below are
the business messages carried as an A2A `DataPart`; the surrounding JSON-RPC request and response
add the normal A2A message, context, and task identifiers.

### 1. Discover an Authority

A protocol-capable Authority advertises the protocol in its AgentCard. This is a protocol-relevant
excerpt, not a replacement for the complete A2A AgentCard:

```json
{
  "name": "Example Auction Authority",
  "supportedInterfaces": [
    {
      "url": "https://authority.example/a2a",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "skills": [
    {
      "id": "marketplace.auction.v1",
      "name": "Auction Authority",
      "tags": [
        "protocol:marketplace.auction/v1",
        "action:create_auction",
        "action:join_auction",
        "action:submit_offer",
        "action:get_auction",
        "mechanism:vickrey"
      ]
    }
  ]
}
```

The client checks the AgentCard before sending a command. Discovery itself can be handled by a
Broker catalog; it is not a required business command in this protocol.

### 2. Create an Auction

The Python package constructs the business command. In this forward-auction example, the initiator
happens to be a Seller, but the command itself only carries `actor_id`.

```python
from a2a_auction_protocol import (
    CreateAuctionPayload,
    JoinAuctionPayload,
    MechanismSpec,
    SubmitOfferPayload,
    command,
    validate_wire_message,
)

MECHANISM_HASH = "sha256:" + ("0" * 64)


def build_vickrey_flow():
    create_payload = CreateAuctionPayload(
        title="RTX 4090 GPU",
        description="Used GPU in working condition.",
        product_url="https://shop.example/items/gpu-4090",
        image_url="https://shop.example/images/gpu-4090.jpg",
        category="computer-hardware",
        currency="USD",
        start_price=10_000,
        reserve_price=12_000,
        min_increment=100,
        duration_seconds=30,
        anti_sniping_seconds=5,
        max_extensions=3,
        direction="forward",
        mechanism=MechanismSpec(id="vickrey", version="1"),
    )
    create = command(
        "create_auction",
        "agent-initiator",
        create_payload.model_dump(mode="json"),
    )

    join = command(
        "join_auction",
        "agent-participant-1",
        JoinAuctionPayload(
            auction_id="auction-123",
            accepted_mechanism_hash=MECHANISM_HASH,
        ).model_dump(mode="json"),
    )

    offer = command(
        "submit_offer",
        "agent-participant-1",
        SubmitOfferPayload(
            auction_id="auction-123",
            offer={"amount": 19_000},
            expected_version=4,
            source="manual",
        ).model_dump(mode="json"),
    )

    for envelope in (create, join, offer):
        validate_wire_message(envelope.model_dump(mode="json"))

    return create, join, offer
```

The package is transport-neutral: each returned envelope can be serialized with
`model_dump(mode="json")` and placed in an A2A `DataPart` sent through `message/send`.

The amount is an integer minor unit. In this example, `10000` means `$100.00` if the currency is
USD. The `product_url` is copied into the AuctionCard and creation event; it is informational and
does not replace the Authority's frozen auction state.

### 3. AuctionCard Returned by the Authority

The Authority returns an `AuctionCard`. A Python client can validate and inspect the returned
object without reconstructing the JSON manually:

```python
from a2a_auction_protocol import AuctionCard


def read_auction_card(command_result: dict) -> AuctionCard:
    card = AuctionCard.model_validate(command_result["data"]["auction"])
    print(card.title, card.status, card.version)
    print(card.mechanism.id, card.mechanism.spec_hash)
    return card
```

The card is a public snapshot: it identifies the initiator, item or requirement, mechanism,
timing, current state, and Authority endpoint. The selected `participant_model` describes any
domain-specific labels without making `buyer` or `seller` mandatory.

The `spec_hash` is important: it binds the auction to the exact mechanism definition that Participants
accepted. The `version` is the auction state version used for optimistic concurrency control.

### 4. Participant Accepts the Mechanism and Joins

Before joining, the Participant retrieves the mechanism definition and verifies that it understands the
offer schema, visibility policy, winner rule, and settlement rule:

```python
from a2a_auction_protocol import JoinAuctionPayload, command


join = command(
    "join_auction",
    "agent-participant-1",
    JoinAuctionPayload(
        auction_id=card.auction_id,
        accepted_mechanism_hash=card.mechanism.spec_hash,
    ).model_dump(mode="json"),
)
```

An Authority rejects a missing or mismatched mechanism hash. A Participant that cannot evaluate the
mechanism can decline to join.

### 5. Participant Submits a Sealed Offer

```python
from a2a_auction_protocol import SubmitOfferPayload, command, validate_wire_message


offer = command(
    "submit_offer",
    "agent-participant-1",
    SubmitOfferPayload(
        auction_id=card.auction_id,
        offer={"amount": 19_000},
        expected_version=card.version,
        source="manual",
    ).model_dump(mode="json"),
)
validate_wire_message(offer.model_dump(mode="json"))
```

The client serializes the command and sends it in an A2A `DataPart`. Assume `authority_client` is
the application's A2A JSON-RPC adapter; the package itself intentionally does not choose an HTTP
client or server framework. The Authority validates the command atomically and returns a
structured `CommandResult`:

```python
result = authority_client.send_data_part(offer.model_dump(mode="json"))
if result.status == "accepted":
    print(result.data["auction_version"])
else:
    print(result.error.code, result.error.message)
```

The bid amount remains redacted while the Vickrey auction is open. Public events can expose that
a bid was accepted without exposing the sealed amount.

### 6. Final Settlement

When the Authority closes the auction, the client reads the authoritative result rather than
computing the winner locally:

```python
from a2a_auction_protocol import AuctionCard, OrderView


# final_result is the CommandResult returned by the Authority after closing.
final_card = AuctionCard.model_validate(final_result.data["auction"])
order = OrderView.model_validate(final_result.data["order"])

print(final_card.status)                 # SOLD
print(final_card.current_winner_agent_id)
print(order.winner_id)
print(order.final_price)                  # second-highest offer
print(order.parties)                     # mechanism-defined party labels
```

For the example offers `19_000` and `17_000`, a Vickrey Authority returns the participant with
the `19_000` offer as the winner and a clearing price of `17_000`. The order remains
`PENDING_SETTLEMENT` because this protocol does not implement payment, delivery, or refunds.

The complete transport-neutral transcript is available at
[`examples/complete_vickrey/run.py`](examples/complete_vickrey/run.py) and can be run with:

```bash
uv run python examples/complete_vickrey/run.py
```

## Custom and Natural-Language Mechanisms

The protocol is not limited to the built-in English, first-price, or Vickrey examples. Mechanism
IDs are open strings, so an Authority can publish a more complex mechanism without changing the
`marketplace.auction/v1` command envelope or requiring a new version of this package.

For example, an Authority can define a multi-attribute procurement mechanism:

```json
{
  "id": "acme.score_auction",
  "version": "1",
  "title": "Price, delivery, and quality score auction",
  "description": "The lowest verified score wins.",
  "human_spec": "Each supplier submits a price, delivery time, and quality score. The Authority computes score = price + delivery_days * 500 - quality_score * 100. The lowest score wins. Ties go to the earliest valid offer.",
  "offer_schema": {
    "type": "object",
    "properties": {
      "price": {"type": "integer", "minimum": 1},
      "delivery_days": {"type": "integer", "minimum": 1},
      "quality_score": {"type": "integer", "minimum": 0, "maximum": 100}
    },
    "required": ["price", "delivery_days", "quality_score"],
    "additionalProperties": false
  },
  "rules": {
    "winner": "lowest_score",
    "score_formula": "price + delivery_days * 500 - quality_score * 100",
    "tie_breaker": "earliest_valid_offer"
  },
  "settlement": {
    "winner_rule": "lowest_score",
    "price_rule": "winner_offer.price",
    "offer_visibility": "sealed_until_close",
    "tie_breaker": "earliest_valid_offer"
  },
  "formal_spec": {
    "score_field": "score",
    "score_direction": "minimize",
    "score_inputs": ["price", "delivery_days", "quality_score"]
  },
  "implementation": {
    "type": "authority_plugin",
    "id": "acme.score_auction",
    "version": "1"
  },
  "field_visibility": {
    "price": "sealed_until_close",
    "delivery_days": "sealed_until_close",
    "quality_score": "seller",
    "score": "public"
  },
  "directions": ["reverse"],
  "spec_hash": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

This mechanism is more expressive than a single `amount` field: it can represent multi-attribute,
reverse, score-based, or Authority-specific auctions. A Participant can discover it through
`list_mechanisms` and `get_mechanism`, inspect the offer schema and rules, then echo its
`spec_hash` in `join_auction`.

Natural-language mechanisms are supported through `human_spec`. This is useful when rules are
complex and need to be explained to a human or an LLM Agent. However, the protocol makes an
important distinction:

```text
human_spec       -> readable explanation
formal_spec      -> machine-readable semantics
implementation   -> Authority-owned executable rule
```

Natural language alone is not the final arbiter of a winner or price. If an Authority publishes
only `human_spec`, a Participant may understand the proposal but cannot independently execute or verify
the result. For interoperable and auditable execution, the Authority should provide an
`offer_schema`, `formal_spec`, deterministic `implementation` identity, and a frozen `spec_hash`.
The Authority remains responsible for validating offers, computing outcomes, and returning a
result that corresponds to the frozen definition.

This also allows LLM Agents to reason about a custom mechanism without allowing the LLM to change
the hard constraints. The LLM may propose an offer or explain a decision; the Authority plugin
still enforces the mechanism and produces the authoritative settlement.

### Python Message Construction

The same commands can be built and validated without importing any Marketplace implementation:

```python
from a2a_auction_protocol import SubmitOfferPayload, command, validate_wire_message

payload = SubmitOfferPayload(
    auction_id="auction-123",
    offer={"amount": 19000},
    expected_version=4,
    source="automatic",
)
envelope = command("submit_offer", "buyer-1", payload.model_dump(mode="json"))
validate_wire_message(envelope.model_dump(mode="json"))

# Send envelope.model_dump(mode="json") as an A2A DataPart to the
# Authority's supportedInterfaces URL.
```

This package deliberately does not contain a database, HTTP server, market catalog, payment
implementation, or auction state machine. It provides the shared wire contract that independent
auction authorities, Initiators, Participants, and clients can use.

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

For a full reference implementation with Broker, Authority, Initiator, Participant, SQLite persistence,
and runnable mechanism samples, see the companion `a2a-auction-marketplace` project.

`AuctionCapability` helps an Agent describe supported mechanisms and actions in its AgentCard. The
protocol version is `marketplace.auction/v1`; individual mechanism versions are
negotiated through `get_mechanism`; the selected definition and `spec_hash` are frozen into the
AuctionCard, and Participants echo that hash when joining. Mechanism IDs are open strings, so an authority can advertise
`custom.immediate` or another local mechanism without changing the shared protocol package.

Each definition can carry a `human_spec` for a detailed natural-language explanation, a
`formal_spec` for machine-readable semantics, and an `implementation` descriptor for the
Authority-owned deterministic plugin. Natural language is explanatory; it is not by itself the
arbiter of winners or prices. `field_visibility` controls which offer and outcome fields can be
published while an auction is open, including `public`, `sealed_until_close`, `seller`, and
`authority` policies.

The core protocol does not require `seller` or `buyer` roles. If a domain needs them, the selected
mechanism may describe those labels in `participant_model`, and the final order may record them in
its `parties` map. An auction authority is identified by the `authority_agent_card_url` in each
`AuctionCard`, then discovered by its supported actions and mechanisms rather than a mandatory role
name. The authority is the sole source of valid state versions and settlement results for that
auction. A Broker remains marketplace infrastructure:
it may expose registration and a public catalog through REST without extending this protocol.
