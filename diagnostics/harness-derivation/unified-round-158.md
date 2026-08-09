# Harness derivation — unified — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Can you show me exactly what you used to answer that, and what is still uncertain?”"
- **useful because:** Turns the hive from a black box into a trustworthy personal instrument: one spoken request yields a compact, provenance-preserving chain across the pendant turn, relay job, Mac files/apps, and browser tabs, instead of forcing the owner to inspect four logs. It is distinct from commitment_evidence_query (only bound commitments) and incident_diagnostics (only incidents).
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic aggregation first; background model only to summarize conflicting evidence; realtime is used only to phrase the spoken answer.
- **latency:** Under 1 s for a recent answer; up to 5 s for a historical multi-surface trace.
- **cost:** Near-zero for hashes/joins; <$0.01 when a background model must summarize ambiguity.
- **security:** Return pointers, hashes, timestamps, and redacted excerpts by default; never export secrets, page credentials, or raw audio. Require confirmation before opening sensitive source content. Data leaves the device only as already-authorized evidence.
- **missing:** A provenance event schema linking conversation turn ID to /pipeline/audio, /jobs/:jobId/receipts, Mac action receipts, and browser inspection IDs; A read-only unified provenance route and dashboard view; Explicit uncertainty/conflict scoring

### "“Run a pendant hearing check now and tell me whether the mic, link, bridge, and speaker are healthy.”"
- **useful because:** The owner can test the real USB-connected nRF9160 and ESP32 path before trusting a conversation, with a single spoken verdict instead of interpreting packet counters. It exercises both directions and catches modem loss, decode overruns, bridge buffer failure, clipping, and continuity regressions while the hardware is actually available today.
- **path:** pendant → relay → mac-bridge → dashboard-ux
- **model tier:** Deterministic fixture generation, fault checks, and threshold verdicts; background model only turns raw failures into one short repair explanation.
- **latency:** 30–60 s for a normal check; never block ordinary conversation startup.
- **cost:** No model cost for healthy runs; <$0.01 only for a failure explanation; USB test uses negligible bandwidth and a bounded fixture.
- **security:** Use synthetic speech/noise only, never record the room. Mark the run with a nonce and expire artifacts quickly. Require confirmation before any repair or firmware flash.
- **missing:** A callable USB test orchestrator joining the existing fixture hooks to the live bridge; A typed health verdict with thresholds and receipts; A user-facing route to launch and retrieve the check

### "“Every morning, tell me only what is broken across my pendant, Mac, browser, and scheduled work—and what I should do first.”"
- **useful because:** The owner currently has independent routines and raw health endpoints; this produces one anomaly-only daily briefing that catches a dead Safari bridge, stranded Mac job, stale browser command, pendant audio degradation, or failed scheduled routine before the owner discovers it during use.
- **path:** relay → pendant → mac-bridge → browser → dashboard-ux
- **model tier:** Background deterministic aggregation and cheap classifier; realtime model is not used unless the owner asks follow-up questions.
- **latency:** Runs in the background in under 2 minutes; one short spoken sentence at the existing morning-brief time, with no interruption if healthy.
- **cost:** <$0.01/day; dominated by one optional background summary, not by health reads.
- **security:** Speak only status classes and remediation, not page titles, file names, or message contents. Keep raw diagnostics local and retain a bounded 24-hour anomaly window. Repairs always require explicit confirmation.
- **missing:** A cross-surface anomaly schema and deduplication window; A scheduled aggregator that can read typed health/receipt results; A quiet, anomaly-only delivery policy integrated with the existing briefing queue

### "“Forget that completely—every copy, transcript, queued job, browser capture, and derived memory—and prove when it is gone.”"
- **useful because:** The owner can revoke a thought or conversation instead of merely muting future capture. One request would find and delete the source and derived artifacts across pendant storage, relay records, Mac workspace, browser evidence, pipeline artifacts, and context graph, then return a signed deletion receipt listing any copy that could not be reached.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic identity search, deletion, and verification; no realtime model required. A background model may explain irreducible uncertainty only after the deterministic report.
- **latency:** Immediate local latch and queueing; normal deletion receipt within 30 seconds, with retries continuing in the background.
- **cost:** Low storage/query cost; <$0.01 only if a model summarizes exceptions.
- **security:** Deletion must be bound to an explicit owner-selected item or time range, never inferred from vague speech. Require physical confirmation for broad ranges. Preserve only minimal compliance metadata: request ID, hashes, timestamps, and deletion status. Do not claim deletion where a third-party browser service cannot verify it.
- **missing:** A cross-surface artifact index linking raw and derived records; Idempotent deletion tombstones and retry workers on relay, Mac, and browser; A cryptographic deletion receipt with an explicit unreachable/ unverifiable state; An owner-facing selector for the exact conversation, time range, or memory

### "“Before you do this, tell me the exact promise you are making; afterward, prove whether reality matches it.”"
- **useful because:** The owner gets a machine-checkable contract for consequential work: intended targets, expected state changes, prohibited side effects, and evidence required for success. After execution it detects partial success and lies such as a relay acceptance being mistaken for a browser submission or audio playback.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic contract compilation and postcondition checks; planner model only drafts ambiguous natural-language expectations, which must be shown to the owner before execution.
- **latency:** Under 2 seconds for a prepared contract; verification within 5 seconds after a normal job.
- **cost:** Near-zero for typed predicates and receipts; <$0.02 for complex contract drafting.
- **security:** Never silently broaden targets or convert a missing postcondition into success. Sensitive values are represented by hashes and predicates, not copied into the contract. Irreversible effects still require the existing physical approval latch.
- **missing:** A typed precondition/postcondition DSL spanning files, browser state, relay status, and audio delivery; Adapters that evaluate postconditions against existing receipts and browser evidence; A spoken contract readback and physical approval binding; A durable mismatch record that blocks downstream actions

### "“If I lose this Mac or relay, let me recover my identity, preferences, unfinished work, and device state onto a replacement without exposing my secrets.”"
- **useful because:** The hive becomes survivable rather than tied to one laptop or one database. A new Mac or relay could verify the pendant, restore only encrypted owner-approved state, identify unfinished actions without replaying unsafe steps, and resume the conversation with an honest gap report.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic encrypted backup, device attestation, and replay classification; background model may summarize recovered context but never decides what to replay.
- **latency:** Restore manifest in under 10 seconds; full recovery in minutes depending on encrypted artifact volume.
- **cost:** Small encrypted storage and transfer cost; no per-restore model cost unless summarizing recovered context.
- **security:** Use a pendant-held key or owner-approved recovery ceremony; never export browser cookies, passwords, or raw audio by default. Separate identity keys from recoverable context. Unsafe/unrepeatable ledger steps must be quarantined, not replayed.
- **missing:** A device identity and recovery-key ceremony; Encrypted, versioned cross-surface backup manifests; Adapters for context graph, routines, receipts, browser session metadata, and pending ledgers; A restore dry-run that clearly separates recoverable, missing, and unsafe state


## Changes it proposed to its own stack

### `integration` — Introduce a signed, append-only provenance envelope at the relay/ Mac boundary. Every pipeline event, audio artifact, browser command/result, and Mac job receipt gets a common correlation ID, source surface, monotonic sequence, redaction class, content hash, and parent ID; add a read-only join endpoint that returns the evidence graph without payload secrets. Do not build another job ledger: link existing /pipeline/events, /pipeline/audio, /jobs/:jobId/receipts, /browser/result, and /context-graph records.
- **owner gets:** When the pendant says an answer or action succeeded, the owner can ask why and receive a trustworthy, short chain showing what was observed, what was executed, and what remains uncertain—rather than believing a status label that may only mean 'accepted by relay.'
- effort: Medium-high: schema, correlation propagation in relay and Mac agent, redaction tests, and dashboard rendering.  ·  risk: A correlation bug could falsely join unrelated private data. Fail closed on missing IDs, hash only normalized redacted content, and expose 'unproven' rather than guessing. Recovery is append-only migration; old records remain unjoined.
- cost: Negligible storage per event (roughly 200–400 bytes); no recurring model cost for joins, optional background summarization <$0.01/query.  ·  latency: Adds sub-10 ms local bookkeeping; historical joins may take up to 1 s.
- security: Improves auditability but creates a metadata map across surfaces. Encrypt at rest, retain only bounded hashes/pointers, and enforce existing bearer/session bindings.
- depends on: A stable turn/job correlation ID emitted by /pipeline/events and propagated into Mac job and browser command receipts; A documented redaction classification for browser and Mac evidence; Owner retention/deletion policy (still unanswered)

### `memory` — Add a cross-surface revocation ledger, not a second memory store. Every captured item and derived artifact receives an opaque lineage ID; a deletion request writes an idempotent tombstone, propagates it to relay, Mac, browser, pipeline, and context-graph stores, and blocks re-materialization. Verification returns per-surface deleted, pending, unreachable, or unverifiable states.
- **owner gets:** The owner can actually take something back and know which copies remain, instead of trusting a vague 'forgotten' response while transcripts or derived facts continue to exist elsewhere.
- effort: High: lineage propagation, deletion adapters, retry/reconciliation, and adversarial tests for stale caches and offline pendant queues.  ·  risk: A bad lineage join could delete the wrong artifact. Require explicit selection, preview all matched items, use tombstones before physical deletion, and make broad deletion physical-confirmation-only. Recovery is a tombstone audit and restore only from an owner-approved backup.
- cost: Bounded metadata growth; roughly one small record per artifact plus tombstones. No routine model cost.  ·  latency: Local revocation is immediate; complete convergence may take minutes when the pendant, browser, or relay is offline.
- security: Reduces retained sensitive data but creates a sensitive lineage map. Encrypt it, minimize fields, restrict access, and retain deletion receipts only as long as the owner's policy allows.
- depends on: An owner retention/deletion policy; Opaque lineage IDs propagated through pipeline, job, browser, capture, and context-graph records; Idempotent deletion endpoints on each surface; A physical confirmation path for broad or irreversible deletion


## What it asked for

### `c22-mu8k` (context) — owner's intended timezone for personal routines and 'morning/evening' language
- why: Live memory says America/Chicago while the Mac's authoritative resolved timezone is America/New_York; daily routines currently fire on the Mac zone. A cross-surface anomaly briefing and provenance timestamps must not silently choose the wrong personal zone.
- would change: I will keep Mac-resolved events in America/New_York, but I will either schedule owner-facing routines in the owner's stated zone or explicitly label the conversion; until answered I will not infer Chicago or New York as the owner's location.

