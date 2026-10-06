# Changelog

## 0.2.0 - 2026-10-07

- Made the core protocol role-neutral: commands use `actor_id`, AuctionCards use `initiator_id`,
  and settlement projections use `winner_id` plus mechanism-defined `parties`.
- Added `participant_model` so a mechanism can describe buyer/seller, requester/provider, or
  domain-specific participation semantics without hard-coding them into the core envelope.
- Changed capability discovery guidance to use actions and mechanisms; legacy role declarations are
  retained only for compatibility with early clients.

## 0.1.0 - 2026-09-29

- Initial reusable `marketplace.auction/v1` protocol package.
- Added Pydantic wire models, command helpers, capability declarations, and
  normative JSON Schema.
- Added mechanism negotiation, frozen `spec_hash`, field visibility, reverse
  auctions, and canonical `product_url` support.
