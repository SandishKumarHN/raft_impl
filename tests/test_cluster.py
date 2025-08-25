import asyncio
import types

from dabeaz.raft import RaftNode, State
from dabeaz.network import NetworkManager
from dabeaz.cluster import ClusterManager


async def run_cluster():
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
    leaders = [n for n in nodes.values() if n.state is State.LEADER]
    assert len(leaders) == 1
    leader = leaders[0]

    await leader.apply_command(("set", "x", "y"))
    await asyncio.sleep(0.2)
    for node in nodes.values():
        assert node.state_machine.get("x") == "y"

    for node in nodes.values():
        node.stop()
    await asyncio.gather(*tasks)


def test_cluster_replication():
    asyncio.run(run_cluster())
