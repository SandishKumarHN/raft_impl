import asyncio
import types

from dabeaz.client import KeyValueClient
from dabeaz.cluster import ClusterManager
from dabeaz.network import NetworkManager
from dabeaz.raft import RaftNode


def test_client_kv():
    async def run():
        net = NetworkManager()
        cluster = ClusterManager(net)
        nodes = {name: RaftNode(name, net) for name in ("n1", "n2", "n3")}
        for node in nodes.values():
            cluster.add_node(node)
        timeouts = [0.01, 0.02, 0.03]
        for (node, timeout) in zip(nodes.values(), timeouts):
            node._election_timeout = types.MethodType(lambda self, t=timeout: t, node)
            node.heartbeat_interval = 0.01
            node._reset_election_timer()
        tasks = [asyncio.create_task(n.start()) for n in nodes.values()]
        await asyncio.sleep(0.2)
        client = KeyValueClient(cluster)
        await client.set("a", "1")
        val1 = await client.get("a")
        await client.delete("a")
        val2 = await client.get("a")
        for node in nodes.values():
            node.stop()
        await asyncio.gather(*tasks)
        return val1, val2

    assert asyncio.run(run()) == ("1", None)
