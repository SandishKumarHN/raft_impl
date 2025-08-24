# Raft Implementation Overview

## Class Diagram
```mermaid
classDiagram
    class RaftNode {
        id: str
        state: State
        current_term: int
        log: Log
        commit_index: int
        last_applied: int
        +start()
        +apply_command(command)
        +send(peer_id, message)
    }
    class Log {
        +append(entries)
        +entry(index)
        +slice(start)
        +delete_from(index)
    }
    class LogEntry {
        term: int
        command: Any
    }
    class RequestVote {
        term
        candidate_id
        last_log_index
        last_log_term
    }
    class RequestVoteResult {
        term
        vote_granted
    }
    class AppendEntries {
        term
        leader_id
        prev_log_index
        prev_log_term
        entries: List<LogEntry>
        leader_commit
    }
    class AppendEntriesResult {
        term
        success
        match_index
    }
    RaftNode --> Log
    Log --> LogEntry
    RaftNode --> RequestVote
    RaftNode --> AppendEntries
```

## Architecture Diagram
```mermaid
flowchart LR
    Client -->|command| Leader
    Leader -->|AppendEntries| Follower1
    Leader -->|AppendEntries| Follower2
    Follower1 -->|AppendEntriesResult| Leader
    Follower2 -->|AppendEntriesResult| Leader
```

## Flow Diagram
```mermaid
sequenceDiagram
    participant F as Follower
    participant C as Candidate
    participant L as Leader
    F->>F: election timeout
    F->>C: becomes Candidate
    C->>Peers: RequestVote
    Peers-->>C: RequestVoteResult
    C->>C: majority?
    C->>L: become Leader
    L->>Peers: AppendEntries
    Peers-->>L: AppendEntriesResult
```

## Operations

### Leader Election
1. A follower times out and becomes a candidate.
2. Candidate increments term and requests votes.
3. Peers grant vote if log is up-to-date and they haven't voted.
4. Candidate becomes leader upon majority.

### Log Replication
1. Client sends a command to the leader.
2. Leader appends command as a new log entry.
3. Leader sends AppendEntries RPCs to followers.
4. Followers append entry and respond.
5. Once entry is replicated on majority, leader commits and applies it.
