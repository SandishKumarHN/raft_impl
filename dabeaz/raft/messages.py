from __future__ import annotations

"""RPC message definitions used by Raft nodes to communicate.

The protocol is expressed through a small set of remote procedure
calls.  To keep concerns separated the message dataclasses are
contained in their own module.  Real network transport is left to a
higher level component.
"""

from dataclasses import dataclass
from typing import List
from .log import LogEntry


@dataclass
class RequestVote:
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int


@dataclass
class RequestVoteResult:
    term: int
    vote_granted: bool


@dataclass
class AppendEntries:
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int


@dataclass
class AppendEntriesResult:
    term: int
    success: bool
    match_index: int
