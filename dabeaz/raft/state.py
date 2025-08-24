from __future__ import annotations

"""State definitions for the Raft consensus algorithm.

This module defines the three high level server states used by
Raft: followers, candidates and leaders.  States are deliberately
kept in a separate module to provide a clear separation between
core protocol logic and implementation details.
"""

from enum import Enum, auto


class State(Enum):
    """Enumeration of the roles assumed by a Raft server."""

    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()
