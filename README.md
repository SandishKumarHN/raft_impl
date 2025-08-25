### Raft Impl

Minimal educational implementation of the Raft consensus algorithm.

See [docs/raft_diagrams.md](docs/raft_diagrams.md) for class, architecture,
and flow diagrams along with operation descriptions.

The log supports an optional write-ahead log that persists entries to disk and
fsyncs after every append.  Existing WAL files are automatically loaded when a
node starts, allowing recovery after restarts.
