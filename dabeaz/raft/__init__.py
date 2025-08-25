"""A minimal educational implementation of the Raft consensus algorithm.

The package is split into a small collection of modules that each
focus on one aspect of the protocol.  The goal is not to be feature
complete but to provide a clean reference implementation that mirrors
the structure presented in ``preparation/raft.md``.
"""

from .state import State
from .log import Log, LogEntry, WriteAheadLog
from .messages import (
    RequestVote,
    RequestVoteResult,
    AppendEntries,
    AppendEntriesResult,
)
from .node import RaftNode

__all__ = [
    "State",
    "Log",
    "LogEntry",
    "WriteAheadLog",
    "RequestVote",
    "RequestVoteResult",
    "AppendEntries",
    "AppendEntriesResult",
    "RaftNode",
]
