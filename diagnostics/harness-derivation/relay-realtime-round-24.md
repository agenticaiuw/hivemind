# Harness derivation — relay-realtime — round 24

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I asked you to handle that on my Mac—what’s the status?”"
- **useful because:** The owner shouldn’t wonder whether a delegated task is still running, failed, or finished. A quick spoken status lets them keep moving while away from the Mac.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime for the spoken query; a cheaper Mac-side planner/executor reports status and results.
- **latency:** Sub-second reply when a status is already known; otherwise a short acknowledgment and a follow-up when the Mac reports back.
- **cost:** Low per query. The dominant cost is Mac-side status retrieval and any stored receipts, not relay compute.
- **security:** Status text can leak sensitive task names or file paths. Only return what’s needed for the owner to understand progress; redact secrets; require confirmation before reading full outputs aloud.
- **missing:** A durable receipt/status store keyed by job id and owner identity; A relay-readable status endpoint or tool to fetch status and results; A queue for completion summaries for the relay to speak later (or a dashboard inbox)


## Changes it proposed to its own stack

### `context` — Introduce a typed, minimal context service for the relay: given an utterance and a desired outcome (status query, dictation, mac task), return only relevant facts (device online state, last job ids, last spoken receipts), each with TTL and provenance, capped to a small token budget. Cache between turns and invalidate on updates.
- **owner gets:** Faster, more accurate voice responses without re-sending bulky state every turn, lowering latency and cost while keeping answers grounded.
- effort: Medium. Needs a small service/schema and adapters in relay and mac-bridge, plus caching and invalidation rules.  ·  risk: Wrong or stale context could misroute a task or reference the wrong job. Mitigate with TTLs, provenance, and explicit job ids in receipts.
- cost: Moderate initial build; ongoing savings by reducing prompt/context size per turn.  ·  latency: Improves response time by avoiding large context assembly; small overhead for cache lookup.
- security: Centralizes sensitive state; must enforce strict per-owner isolation and audit logging. Encrypt at rest.
- depends on: A durable store for receipts/state and cache invalidation hooks from mac-bridge


## What it asked for

_Nothing._
