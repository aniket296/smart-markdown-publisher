"""Shared pytest fixtures for Smart Markdown-to-Print Desktop Publisher unit tests."""

from pathlib import Path
import pytest


@pytest.fixture
def sample_rich_markdown() -> str:
    """Return a rich Markdown manuscript with YAML frontmatter, callouts, code blocks, and tables."""
    return """---
title: Distributed Storage Engine Architecture
subtitle: Consensus, Write-Ahead Logging & B-Tree Compaction
author: Dr. Evelyn Vance
date: 2026-11-12
version: 2.4.0
institution: Systems Research Lab
cover: true
toc: true
header: CONFIDENTIAL TECHNICAL SPEC
footer: Systems Research Lab - Internal Distribution
---

# 1. Architectural Overview

Modern distributed storage engines rely on deterministic replication and crash-safe write-ahead logging (WAL) to guarantee durability under arbitrary node failures.

> [!NOTE]
> All storage nodes must synchronize hybrid logical clocks within a 15ms drift budget before joining the Raft quorum.

## 1.1 Write-Ahead Log Pipeline

Incoming mutations are serialized into framed log segments prior to memtable insertion.

```python
def append_wal_frame(buffer: bytearray, payload: bytes, term: int) -> int:
    frame_header = f"{term:08x}:{len(payload):08x}\\n".encode("ascii")
    buffer.extend(frame_header + payload)
    return len(buffer)
```

> [!WARNING] Disk Flush Semantics
> Skipping `fsync` on commit frames can cause silent split-brain state after an unclean power cycle.
>
> Always verify hardware write-cache policies on NVMe arrays.

# 2. Storage Engine Benchmarks

Below is the throughput and tail-latency comparison across compaction profiles:

| Profile | Write Throughput (ops/s) | P99 Latency (ms) | Space Amplification |
| :--- | :---: | :---: | :--- |
| Leveled Compaction | 142,000 | 3.8 | 1.12x |
| Size-Tiered | 310,000 | 9.4 | 1.65x |
| FIFO Ephemeral | 485,000 | 1.1 | 1.02x |

```sql
SELECT node_id, MAX(commit_index) AS head_index, AVG(flush_latency_ms)
FROM cluster_wal_telemetry
WHERE recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY node_id
ORDER BY head_index DESC;
```
"""


@pytest.fixture
def sample_chapter_folder(tmp_path: Path) -> Path:
    """Create a temporary multi-chapter book directory with natural sorting filenames."""
    book_dir = tmp_path / "manuscript_book"
    book_dir.mkdir(parents=True, exist_ok=True)

    (book_dir / "01_intro.md").write_text(
        """---
title: Enterprise Systems Handbook
author: Principal Engineering Group
cover: true
toc: true
---

# Chapter 1: Introduction

Foundational principles of reliable systems design.
""",
        encoding="utf-8",
    )

    (book_dir / "02_architecture.md").write_text(
        """---
title: Ignored Chapter Override
---

# Chapter 2: Service Mesh Architecture

Zero-trust mTLS routing and circuit breaking across regional clusters.
""",
        encoding="utf-8",
    )

    (book_dir / "10_appendix.md").write_text(
        """# Chapter 10: Operational Checklist

Final production readiness verification criteria.
""",
        encoding="utf-8",
    )

    return book_dir
