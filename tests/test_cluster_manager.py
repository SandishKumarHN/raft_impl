from dabeaz.network import NetworkManager
from dabeaz.cluster import ClusterManager
from dabeaz.raft import RaftNode


def test_gossip_membership():
    net = NetworkManager()
    cluster = ClusterManager(net)
    n1 = RaftNode("n1", net)
    n2 = RaftNode("n2", net)
    n3 = RaftNode("n3", net)
    cluster.add_node(n1)
    cluster.add_node(n2)
    cluster.add_node(n3)
    for _ in range(5):
        cluster.gossip_round()
    assert set(n1.peers) == {"n2", "n3"}
    assert set(n2.peers) == {"n1", "n3"}
    assert set(n3.peers) == {"n1", "n2"}
