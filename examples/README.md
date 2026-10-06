# Complete Examples

These examples show the complete `marketplace.auction/v1` message flow without requiring the
Marketplace reference implementation, a database, or an API key.

```bash
uv run python examples/complete_vickrey/run.py
uv run python examples/custom_multi_attribute/run.py
uv run python examples/reverse_procurement/run.py
```

## Examples

### `complete_vickrey`

An Initiator creates a product auction, a Participant accepts the frozen mechanism, two Participants
submit sealed offers, and the Authority returns a second-price order. The forward-auction example
uses seller/buyer labels only as domain context, not as required protocol fields.

### `custom_multi_attribute`

An Authority publishes a custom mechanism with a machine-readable offer schema, a natural-language
`human_spec`, a formal scoring description, and an implementation identity. The example evaluates
price, delivery time, and quality, then emits the settlement projection.

### `reverse_procurement`

An Initiator publishes a procurement requirement and service providers submit offers. The example
shows how the same protocol envelope supports reverse auctions and multi-attribute selection without
changing the command names.

### `raw_a2a`

The JSON files contain transport-neutral DataPart payloads for clients written in languages other
than Python. Wrap each object in the A2A JSON-RPC binding and send it to the Agent's advertised
`supportedInterfaces` URL.
