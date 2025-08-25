"""Simple key-value client that talks to a Raft cluster."""

from __future__ import annotations

import asyncio
from .cluster import ClusterManager


class KeyValueClient:
    def __init__(self, cluster: ClusterManager) -> None:
        self.cluster = cluster

    async def set(self, key: str, value: str) -> None:
        leader = self.cluster.leader()
        retries = 5
        while leader is None and retries:
            await asyncio.sleep(0.05)
            leader = self.cluster.leader()
            retries -= 1
        if leader is None:
            raise RuntimeError("no leader available")
        await leader.apply_command(("set", key, value))
        # give the cluster time to replicate and apply
        await asyncio.sleep(0.05)

    async def get(self, key: str) -> str | None:
        leader = self.cluster.leader()
        if leader is None:
            raise RuntimeError("no leader available")
        return leader.state_machine.get(key)
