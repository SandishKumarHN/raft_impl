from __future__ import annotations

"""Log structure used by the Raft consensus algorithm.

The log is modelled as an append only list of ``LogEntry`` objects.
Each entry stores the term in which it was created together with the
command that should be applied to the replicated state machine once
the entry has been committed.
"""

from dataclasses import dataclass
from typing import Any, List


@dataclass
class LogEntry:
    """A single entry in the replicated log."""

    term: int
    command: Any


class Log:
    """Simple in-memory log implementation."""

    def __init__(self) -> None:
        self._entries: List[LogEntry] = []

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._entries)

    def append(self, *entries: LogEntry) -> None:
        self._entries.extend(entries)

    def entry(self, index: int) -> LogEntry:
        return self._entries[index - 1]

    def last_index(self) -> int:
        return len(self._entries)

    def last_term(self) -> int:
        if not self._entries:
            return 0
        return self._entries[-1].term

    def slice(self, start: int) -> List[LogEntry]:
        return self._entries[start - 1 :]

    def delete_from(self, index: int) -> None:
        del self._entries[index - 1 :]
