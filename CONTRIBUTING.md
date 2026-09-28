# Contributing

## Development

This package targets Python 3.13 and uses `uv`:

```bash
uv sync --extra dev
uv run pytest
```

Keep the shared wire contract transport-neutral. Changes to command fields,
result fields, mechanism negotiation, or schema semantics should include a
test and a short entry in the changelog.

The package does not implement an auction database, HTTP server, payment flow,
or winner-selection engine. Those belong to an Authority or reference
implementation built on this contract.
