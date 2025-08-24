from __future__ import annotations

"""Core logic for a Raft server.

The implementation provided here is intentionally minimal and is meant
for educational purposes.  A ``RaftNode`` communicates with its peers by
calling their RPC handler methods directly.  The module contains the
state machine that drives leader election, log replication and the
basic safety properties described in ``preparation/raft.md``.
"""

import asyncio
import random
from typing import Dict, Optional

from .log import Log, LogEntry
from .messages import (
    AppendEntries,
    AppendEntriesResult,
    RequestVote,
    RequestVoteResult,
)
from .state import State


class RaftNode:
    """A single participant in a Raft cluster."""

    heartbeat_interval = 0.05

    def __init__(self, node_id: str) -> None:
        self.id = node_id
        self.state: State = State.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log = Log()
        self.commit_index = 0
        self.last_applied = 0
        self.peers: Dict[str, "RaftNode"] = {}
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        self._inbox: "asyncio.Queue[tuple[str, object]]" = asyncio.Queue()
        self._stop = asyncio.Event()

    # ------------------------------------------------------------------
    # Cluster configuration
    # ------------------------------------------------------------------
    def set_peers(self, peers: Dict[str, "RaftNode"]) -> None:
        """Configure peer nodes for this server."""

        # Do not include ourselves in the peer mapping
        self.peers = {pid: p for pid, p in peers.items() if pid != self.id}

    # ------------------------------------------------------------------
    # High level API
    # ------------------------------------------------------------------
    async def start(self) -> None:
        """Start the node's main loop."""

        while not self._stop.is_set():
            if self.state == State.FOLLOWER:
                await self._run_follower()
            elif self.state == State.CANDIDATE:
                await self._run_candidate()
            else:
                await self._run_leader()

    def stop(self) -> None:
        self._stop.set()

    async def apply_command(self, command: object) -> None:
        """Append a command to the log.  Only valid for leaders."""

        if self.state != State.LEADER:
            raise RuntimeError("only the leader may accept commands")
        self.log.append(LogEntry(self.current_term, command))

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------
    async def send(self, peer_id: str, message: object) -> None:
        await self.peers[peer_id]._inbox.put((self.id, message))

    async def _recv(self, timeout: Optional[float]) -> Optional[tuple[str, object]]:
        try:
            return await asyncio.wait_for(self._inbox.get(), timeout)
        except asyncio.TimeoutError:
            return None

    async def _handle_rpc(self, sender: str, message: object) -> None:
        if isinstance(message, RequestVote):
            await self._on_request_vote(sender, message)
        elif isinstance(message, AppendEntries):
            await self._on_append_entries(sender, message)

    # ------------------------------------------------------------------
    # Follower behaviour
    # ------------------------------------------------------------------
    async def _run_follower(self) -> None:
        timeout = self._election_timeout()
        msg = await self._recv(timeout)
        if msg is None:
            self.state = State.CANDIDATE
            return
        sender, rpc = msg
        await self._handle_rpc(sender, rpc)

    # ------------------------------------------------------------------
    # Candidate behaviour
    # ------------------------------------------------------------------
    async def _run_candidate(self) -> None:
        self.current_term += 1
        self.voted_for = self.id
        votes = 1
        last_idx = self.log.last_index()
        last_term = self.log.last_term()
        for pid, peer in self.peers.items():
            req = RequestVote(self.current_term, self.id, last_idx, last_term)
            res = await peer._on_request_vote(self.id, req)
            if res.vote_granted:
                votes += 1
        if votes > len(self.peers) // 2:
            self.state = State.LEADER
            for pid in self.peers:
                self.next_index[pid] = self.log.last_index() + 1
                self.match_index[pid] = 0
            return
        # Election failed; wait before trying again
        await asyncio.sleep(self._election_timeout())

    # ------------------------------------------------------------------
    # Leader behaviour
    # ------------------------------------------------------------------
    async def _run_leader(self) -> None:
        for pid in self.peers:
            await self._send_append_entries(pid)
        await asyncio.sleep(self.heartbeat_interval)

    # ------------------------------------------------------------------
    # RPC handlers
    # ------------------------------------------------------------------
    async def _on_request_vote(self, sender: str, msg: RequestVote) -> RequestVoteResult:
        if msg.term < self.current_term:
            return RequestVoteResult(self.current_term, False)
        if msg.term > self.current_term:
            self.current_term = msg.term
            self.state = State.FOLLOWER
            self.voted_for = None
        if (
            (self.voted_for in (None, msg.candidate_id))
            and self._log_is_up_to_date(msg.last_log_index, msg.last_log_term)
        ):
            self.voted_for = msg.candidate_id
            return RequestVoteResult(self.current_term, True)
        return RequestVoteResult(self.current_term, False)

    async def _on_append_entries(self, sender: str, msg: AppendEntries) -> AppendEntriesResult:
        if msg.term < self.current_term:
            return AppendEntriesResult(self.current_term, False, self.log.last_index())
        self.state = State.FOLLOWER
        self.current_term = msg.term
        self.voted_for = sender
        if msg.prev_log_index > 0:
            if msg.prev_log_index > self.log.last_index():
                return AppendEntriesResult(self.current_term, False, self.log.last_index())
            prev = self.log.entry(msg.prev_log_index)
            if prev.term != msg.prev_log_term:
                self.log.delete_from(msg.prev_log_index)
                return AppendEntriesResult(self.current_term, False, self.log.last_index())
        if msg.entries:
            self.log.delete_from(msg.prev_log_index + 1)
            self.log.append(*msg.entries)
        if msg.leader_commit > self.commit_index:
            self.commit_index = min(msg.leader_commit, self.log.last_index())
        return AppendEntriesResult(self.current_term, True, self.log.last_index())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _election_timeout(self) -> float:
        return random.uniform(0.15, 0.3)

    def _log_is_up_to_date(self, index: int, term: int) -> bool:
        my_term = self.log.last_term()
        if term != my_term:
            return term > my_term
        return index >= self.log.last_index()

    async def _send_append_entries(self, peer_id: str) -> None:
        next_idx = self.next_index[peer_id]
        prev_idx = next_idx - 1
        prev_term = self.log.entry(prev_idx).term if prev_idx > 0 and self.log.last_index() >= prev_idx else 0
        entries = self.log.slice(next_idx) if next_idx <= self.log.last_index() else []
        msg = AppendEntries(
            term=self.current_term,
            leader_id=self.id,
            prev_log_index=prev_idx,
            prev_log_term=prev_term,
            entries=entries,
            leader_commit=self.commit_index,
        )
        res = await self.peers[peer_id]._on_append_entries(self.id, msg)
        if res.success:
            self.match_index[peer_id] = res.match_index
            self.next_index[peer_id] = res.match_index + 1
        else:
            self.next_index[peer_id] = max(1, self.next_index[peer_id] - 1)
