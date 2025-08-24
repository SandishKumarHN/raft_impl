import pytest

from dabeaz.raft import Log, LogEntry


def test_log_append_and_retrieve():
    log = Log()
    log.append(LogEntry(1, "a"), LogEntry(1, "b"))
    assert log.last_index() == 2
    assert log.last_term() == 1
    assert log.entry(1).command == "a"


def test_log_slice_and_delete():
    log = Log()
    log.append(LogEntry(1, "a"), LogEntry(1, "b"), LogEntry(2, "c"))
    assert [e.command for e in log.slice(2)] == ["b", "c"]
    log.delete_from(3)
    assert log.last_index() == 2
    assert log.last_term() == 1
