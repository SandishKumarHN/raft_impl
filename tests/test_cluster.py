import asyncio
import types
from dabeaz.raft import RaftNode, State, LogEntry


async def run_cluster():
    nodes = {name: RaftNode(name) for name in ("n1", "n2", "n3")}
    for node in nodes.values():
        node.set_peers(nodes)

    # Deterministic and fast timeouts
    timeouts = [0.01, 0.02, 0.03]
    for (node, timeout) in zip(nodes.values(), timeouts):
        node._election_timeout = types.MethodType(lambda self, t=timeout: t, node)
        node.heartbeat_interval = 0.01

    tasks = [asyncio.create_task(n.start()) for n in nodes.values()]
    # allow election
    await asyncio.sleep(0.1)
    leaders = [n for n in nodes.values() if n.state is State.LEADER]
    assert len(leaders) == 1
    leader = leaders[0]

    await leader.apply_command("first")
    await asyncio.sleep(0.1)
    for node in nodes.values():
        assert node.log.last_index() == 1
        assert node.log.entry(1).command == "first"

    for node in nodes.values():
        node.stop()
        await node._inbox.put((node.id, None))
    await asyncio.gather(*tasks)


def test_cluster_replication():
    asyncio.run(run_cluster())
