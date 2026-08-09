# Harness derivation — faculty-judgement — round 265

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What did I miss while the pendant or Mac was offline? Tell me what was generated, what actually reached the device, and what still needs my attention.”"
- **useful because:** The system can generate briefings and jobs while delivery is uncertain, but today catch-up has no real pendant-item input and receipts stop before authenticated download/playback. This would reconcile relay jobs, audio artifacts, pendant delivery ACKs, browser spool, and local receipts into one honest offline-gap report—separating never generated, generated but undelivered, downloaded but unheard, and completed.
- **path:** relay → pendant → mac → browser
- **model tier:** background deterministic reconciliation; realtime only to answer the spoken question and optionally play one selected item
- **latency:** 2–4 seconds when receipts are present; stale or missing surfaces should return an explicit partial report
- **cost:** Under $0.02 per report; mostly reads and deterministic joins, with optional TTS cost for playback
- **security:** Use opaque artifact IDs and source references in the report; do not read private briefing text aloud until the owner selects an item. Deduplicate offline ACK replay and never mark an item heard from download alone.
- **missing:** a durable join from relay job to Mac/local job and artifact; catchup ingestion of authenticated pendant ACKs; a state machine distinguishing generated/downloaded/started/finished/interrupted; a user-facing report route and review cursor

### "“Before you speak, can you prove the pendant is ready—and if not, tell me whether the problem is radio, audio, playback, or stale delivery?”"
- **useful because:** A green connection is not proof that the owner can hear anything. This readiness check would combine the latest authenticated delivery ACKs, UART audio metrics, relay/browser connectivity, queue depth, and recent artifact checksum/playback evidence into a fail-closed verdict. It would prevent the system from confidently delivering a briefing into a dead or stale path and give the owner one actionable explanation.
- **path:** pendant → relay → mac → browser
- **model tier:** deterministic health evaluator first; background model only to summarize multiple failures in owner language
- **latency:** Under 1 second from cached metrics; at most 3 seconds if a live Mac/relay probe is needed
- **cost:** Near-zero model cost for the evaluator; at most $0.01 for an optional concise explanation
- **security:** Expose only metrics, opaque artifact IDs, and failure reasons—never UART payloads or speech content. Fail closed when timestamps, session authentication, or ACK continuity are missing. A health verdict must not itself retry or mutate delivery.
- **missing:** a unified freshness window and health verdict over existing metrics; live route adapters for UART diagnostics and pendant availability; correlation between artifact IDs, pipeline events, and playback ACKs; a concise owner-facing status endpoint and dashboard card

### "“What did you decide for me today without asking, what did you deliberately not do, and what would have happened if I had been available?”"
- **useful because:** The system can already make policy and attention decisions, but the owner cannot inspect the negative space: suppressed interruptions, deferred jobs, blocked actions, or the reason an autonomous choice was made. A daily agency ledger would make the hive accountable without forcing the owner to monitor it live. Each entry would show the triggering evidence, policy rule, chosen action, alternatives rejected, expiry, and whether the outcome was later confirmed or contradicted.
- **path:** relay → mac → browser → pendant
- **model tier:** background deterministic aggregation of policy/attention/receipt events; realtime only for a short spoken answer or when the owner drills into one entry
- **latency:** Generate incrementally; under 2 seconds to retrieve the day's ledger, with deeper explanation under 5 seconds
- **cost:** Under $0.02 per daily ledger; mostly local/relay reads, with a small model call only for grouping and plain-language synthesis
- **security:** This is sensitive behavioral telemetry. Keep raw evidence local by default, expose only redacted summaries to the pendant, encrypt relay copies, and let the owner delete individual entries. Never infer motives or claim an action was considered unless a durable policy/evaluation event exists.
- **missing:** durable append-only records for autonomy_policy_evaluate and attention_arbitrate decisions, including suppressed/deferred outcomes; a shared correlation key linking evidence, policy evaluation, job, and receipt across surfaces; retention and redaction rules for behavioral decision history; a dashboard/voice query route that distinguishes observed facts from reconstructed explanations


## Changes it proposed to its own stack

### `relay` — Add a lease_until/lease_owner recovery protocol to relay_jobs, modeled on the working routine lease: claim atomically, renew during execution, sweep expired processing jobs back to queued with an attempt counter, and emit a receipt explaining whether recovery was safe or suppressed because the job was non-idempotent.
- **owner gets:** When the Mac or network dies halfway through a request, the owner currently gets a job stuck in processing for up to 24 hours with no honest answer. This lets work resume or clearly fail instead of disappearing, while preventing duplicate external actions.
- effort: Medium: schema migration, D1 and memory-store parity, bridge renewal, and tests for crash/retry/idempotency.  ·  risk: A lease that expires during a slow but healthy action could duplicate side effects. Fail closed for non-idempotent or destructive jobs, require action idempotency keys, and surface every requeue in the receipt.
- cost: Negligible storage and one periodic sweep; no model cost. A small heartbeat request while a job runs.  ·  latency: Adds no startup latency; recovery occurs on the next sweep, typically within one scheduler interval.
- security: Improves availability but expands replay risk; bind leases to authenticated worker identity and never replay destructive work without a durable idempotency proof.
- depends on: a durable relay store migration; cross-surface relay/local job ID mapping; using existing actionIdFor()/executionJournal idempotency evidence

### `integration` — Make the Mac bridge write normalized memory events to the existing fleet-memory POST endpoint after confirmed user-visible outcomes, including retraction events when the owner edits or forgets a fact; project relay memory into the next voice context instead of sending only inheritedText.
- **owner gets:** Preferences, tasks, and corrections made on one body would finally follow the owner to the others. Saying “I changed my editor” or correcting a task once would stop the relay, Mac, browser, and pendant from disagreeing.
- effort: Medium-low: one bridge writer, migration check for relay_memory_events, retry/idempotency handling, and projection integration; the schema, TTLs, retractions, and byte budgets already exist.  ·  risk: A bridge crash could lose an event or duplicate it. Use event IDs and retry-safe writes; only emit after a confirmed outcome, classify sensitivity conservatively, and keep the existing inheritedText fallback until projection is verified.
- cost: Tiny D1 writes and bounded storage (existing 128 KiB log budget); no additional model call.  ·  latency: Do not block the owner response on relay persistence; enqueue asynchronously and expose sync health in receipts.
- security: Cross-body memory increases disclosure surface. Preserve sensitivity and surfaces fields, redact before relay projection, and make retraction propagation auditable.
- depends on: apply fleet-memory migration to the live schema; a writer call from local-agent/bridge.js; a durable relay↔Mac correlation field; projection fallback and error telemetry


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing directions: an offline-gap report that distinguishes generated/downloaded/heard work; relay job lease recovery so interrupted work cannot remain silently stuck; and a real fleet-memory writer so corrections and preferences cross bodies. A readiness verdict for the pendant was also recorded, but it is connective work over existing health, pipeline, browser, and ACK surfaces. The privacy-erasure capability was correctly rejected as an existing backlog item rather than restated.

**Biggest unknown:** I still need the implementation truth for the joins: whether live pipeline artifacts already carry a stable artifact ID through relay, Mac, and pendant ACKs, and whether fleet-memory migration is applied to the live relay schema. Without those, I can specify the owner experience but cannot honestly promise end-to-end reconciliation.

