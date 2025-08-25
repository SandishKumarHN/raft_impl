"""Interactive command line interface for the Raft demo cluster."""

from __future__ import annotations

import argparse
import asyncio
import sys

from .cluster import ClusterManager
from .network import NetworkManager
from .raft import RaftNode
from .client import KeyValueClient


async def _run(nodes: int) -> None:
    """Start a cluster with *nodes* members and process stdin commands."""

    net = NetworkManager()
    cluster = ClusterManager(net)
    node_objs = {}
    for i in range(1, nodes + 1):
        node = RaftNode(f"n{i}", net)
        cluster.add_node(node)
        node_objs[node.id] = node
    tasks = [asyncio.create_task(n.start()) for n in node_objs.values()]
    await asyncio.sleep(0.2)  # allow election
    client = KeyValueClient(cluster)
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        parts = line.strip().split()
        if not parts:
            continue
        cmd = parts[0].lower()
        if cmd == "set" and len(parts) == 3:
            await client.set(parts[1], parts[2])
        elif cmd == "get" and len(parts) == 2:
            val = await client.get(parts[1])
            if val is not None:
                print(val)
        elif cmd == "delete" and len(parts) == 2:
            await client.delete(parts[1])
        elif cmd == "checkpoint":
            for n in node_objs.values():
                n.log.checkpoint()
            print("checkpointed")
        elif cmd in {"stop", "quit", "exit"}:
            break
        elif cmd == "remove" and len(parts) == 2:
            node_id = parts[1]
            node = node_objs.pop(node_id, None)
            if node is not None:
                node.stop()
                cluster.nodes.pop(node_id, None)
                print(f"removed {node_id}")
        else:
            print("unknown command")
    for n in node_objs.values():
        n.stop()
    await asyncio.gather(*tasks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Raft demo CLI")
    parser.add_argument("--nodes", type=int, default=3, help="number of nodes in cluster")
    args = parser.parse_args()
    asyncio.run(_run(args.nodes))


if __name__ == "__main__":  # pragma: no cover
    main()
