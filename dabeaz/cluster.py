"""Cluster manager that propagates membership using a gossip step."""

from __future__ import annotations

import random
from typing import Dict

from .network import NetworkManager
from .raft import RaftNode, State


class ClusterManager:
    """Maintain a set of nodes and exchange membership via gossip."""

    def __init__(self, network: NetworkManager) -> None:
        self.network = network
        self.nodes: Dict[str, RaftNode] = {}

    def add_node(self, node: RaftNode) -> None:
        self.nodes[node.id] = node
        # Update peer information for all members
        for n in self.nodes.values():
            n.set_peers(self.nodes.keys())

    def gossip_round(self) -> None:
        """Perform a single round of membership gossip."""

        ids = list(self.nodes.keys())
        for node in self.nodes.values():
            if len(ids) < 2:
                continue
            partner_id = random.choice([i for i in ids if i != node.id])
            partner = self.nodes[partner_id]
            combined = set(node.peers) | set(partner.peers) | {node.id, partner_id}
            node.set_peers(combined)
            partner.set_peers(combined)

    def leader(self) -> RaftNode | None:
        for node in self.nodes.values():
            if node.state is State.LEADER:
                return node
        return None
