"""Simple in-process network manager.

This abstraction wires together nodes by identifier and offers minimal
RPC-style communication used by the educational Raft implementation.
"""

from __future__ import annotations

from typing import Dict, Any, Callable


class NetworkManager:
    """Registry for nodes that allows RPC-style calls."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Any] = {}

    def register(self, node: Any) -> None:
        """Register a node instance with an ``id`` attribute."""

        self._nodes[node.id] = node

    async def rpc(self, sender: str, receiver: str, method: str, *args: Any) -> Any:
        """Invoke ``method`` on ``receiver`` passing ``sender`` and ``args``."""

        target = self._nodes[receiver]
        func: Callable[..., Any] = getattr(target, method)
        return await func(sender, *args)
