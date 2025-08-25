import asyncio

from dabeaz.raft import (
    AppendEntries,
    LogEntry,
    RaftNode,
    RequestVote,
)
from dabeaz.network import NetworkManager


async def call(coro):
    return await coro


def test_request_vote_granted_for_up_to_date_candidate():
    async def run():
        net = NetworkManager()
        follower = RaftNode("f1", net)
        follower.current_term = 1
        follower.log.append(LogEntry(1, "x"))
        msg = RequestVote(1, "cand", 1, 1)
        res = await follower._on_request_vote("cand", msg)
        return res.vote_granted

    assert asyncio.run(run()) is True


def test_request_vote_rejected_if_term_old():
    async def run():
        net = NetworkManager()
        follower = RaftNode("f1", net)
        follower.current_term = 2
        msg = RequestVote(1, "cand", 0, 0)
        res = await follower._on_request_vote("cand", msg)
        return res.vote_granted

    assert asyncio.run(run()) is False


def test_append_entries_appends_and_commits():
    async def run():
        net = NetworkManager()
        follower = RaftNode("f1", net)
        follower.current_term = 1
        follower.log.append(LogEntry(1, "x"))
        msg = AppendEntries(
            term=2,
            leader_id="l1",
            prev_log_index=1,
            prev_log_term=1,
            entries=[LogEntry(2, "y")],
            leader_commit=2,
        )
        res = await follower._on_append_entries("l1", msg)
        return res.success, follower.commit_index, follower.log.last_index()

    success, commit_index, last_index = asyncio.run(run())
    assert success is True
    assert commit_index == 2
    assert last_index == 2
