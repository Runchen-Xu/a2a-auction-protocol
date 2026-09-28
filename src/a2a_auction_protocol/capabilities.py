from __future__ import annotations

from pydantic import BaseModel, Field

from a2a_auction_protocol.models import AgentRole, MechanismId
from a2a_auction_protocol.protocol import PROTOCOL_NAMESPACE, PROTOCOL_VERSION


class AuctionCapability(BaseModel):
    """Business-protocol capability advertised by an A2A AgentCard."""

    protocol: str = PROTOCOL_NAMESPACE
    versions: list[str] = Field(default_factory=lambda: [PROTOCOL_VERSION])
    roles: list[AgentRole] = Field(default_factory=list)
    mechanisms: list[str] = Field(default_factory=lambda: [item.value for item in MechanismId])
    actions: list[str] = Field(default_factory=list)

    def supports(
        self,
        *,
        version: str = PROTOCOL_VERSION,
        role: AgentRole | None = None,
        mechanism: str | MechanismId | None = None,
        action: str | None = None,
    ) -> bool:
        return (
            version in self.versions
            and (role is None or role in self.roles)
            and (mechanism is None or str(mechanism) in self.mechanisms)
            and (action is None or action in self.actions)
        )

    @property
    def protocol_version(self) -> str:
        return f"{self.protocol}/v{PROTOCOL_VERSION}"

    @property
    def skill_id(self) -> str:
        return f"{self.protocol}.v{PROTOCOL_VERSION}"

    def tags(self) -> list[str]:
        return [
            f"protocol:{self.protocol_version}",
            *(f"role:{role.value}" for role in self.roles),
            *(f"mechanism:{mechanism}" for mechanism in self.mechanisms),
            *(f"action:{action}" for action in self.actions),
        ]

    def description(self) -> str:
        mechanisms = ", ".join(self.mechanisms)
        role_clause = f" for roles {', '.join(role.value for role in self.roles)}" if self.roles else ""
        return f"Supports {self.protocol_version}{role_clause}; mechanisms: {mechanisms}."
