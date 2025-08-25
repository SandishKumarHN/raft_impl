import asyncio
from dabeaz.raft import LogEntry, WriteAheadLog, RaftNode, State


def test_wal_persists_and_recovers(tmp_path):
    path = tmp_path / "wal.log"
    log1 = WriteAheadLog(path)
    log1.append(LogEntry(1, "a"), LogEntry(1, "b"))
    log1.close()

    log2 = WriteAheadLog(path)
    assert log2.last_index() == 2
    assert log2.entry(1).command == "a"
    log2.close()


def test_node_uses_wal(tmp_path):
    path = tmp_path / "node.log"

    async def run():
        node = RaftNode("n1", wal_path=str(path))
        node.state = State.LEADER
        await node.apply_command("x")
        node.log.close()

        node2 = RaftNode("n1", wal_path=str(path))
        result = node2.log.last_index(), node2.log.entry(1).command
        node2.log.close()
        return result

    last_index, cmd = asyncio.run(run())
    assert last_index == 1
    assert cmd == "x"
