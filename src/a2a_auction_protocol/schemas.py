"""Access to the versioned JSON Schemas shipped with the protocol package."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any


@lru_cache(maxsize=None)
def load_schema(name: str = "marketplace.auction.v1.json") -> dict[str, Any]:
    resource = files("a2a_auction_protocol").joinpath("schemas", name)
    return json.loads(resource.read_text(encoding="utf-8"))


def validate_wire_message(value: dict[str, Any]) -> None:
    """Validate a command or result with the normative schema.

    Importing jsonschema lazily keeps model-only consumers lightweight while the
    marketplace runtime still gets a second, language-neutral validation boundary.
    """

    from jsonschema import Draft202012Validator

    Draft202012Validator(load_schema()).validate(value)
