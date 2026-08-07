# Harness derivation — mac-terminal — round 69

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent observability** — At 2026-08-07T12:02Z the Mac agent is in FULL_CONTROL_MODE with planner enabled, but ops readiness is false because Accessibility and Screen Recording are not granted; browser extension is offline with 5 pending commands; computer-use loop is disabled. Journal reports 120 retained jobs, 147 actions, 14 failures, 0 undoable, and 112 without tier attribution.
  - evidence: GET /ops/status and GET /journal via probe_http in round 69

## Capabilities it proposed

### "“Keep an eye on my Mac and browser bridge. If a job is stuck or the bridge goes offline, tell me on the pendant, retry safe work when it comes back, and give me one concise recovery report.”"
- **useful because:** Today the Mac reports browser offline with five pending commands, computer-use disabled, and missing Accessibility/Screen Recording while jobs continue to accumulate failures; the owner otherwise discovers this only after asking. An always-awake relay can detect the outage, preserve intent, retry only idempotent/read jobs, and deliver a short spoken explanation instead of silently losing work.
- **path:** relay-realtime → mac-planner → browser-extension → unified → mac-terminal
- **model tier:** background for periodic health classification and retry decisions; deterministic rules for heartbeat, idempotency, backoff, and receipt aggregation; realtime only to announce an urgent outage or answer a status question
- **latency:** Health checks every 1–5 minutes; outage detection under one interval, pendant alert under 2 seconds once detected; recovery report within 10 seconds of bridge heartbeat. No planner call for ordinary healthy checks.
- **cost:** Near-zero when healthy (HTTP checks and D1 state). Occasional gpt-4.1-mini call, roughly 2–4k input tokens, only to compress several failures into a spoken report; dominant cost is the rare recovery summary, not monitoring.
- **security:** Health metadata, job labels, and failure text leave the Mac for relay state; command payloads and page contents must not. Retry allowlist must be idempotent/read-only (status, list tabs, snapshot, read page); never retry typing, sending, deleting, purchasing, or shell mutations. Preserve the owner's existing maximum-access/no-gate policy, but make the retry classification auditable and expose exact receipts.
- **missing:** A durable bridge-health monitor and lease/heartbeat state in the relay; A retry queue that understands idempotency keys, exponential backoff, tab/session affinity, and safe-vs-never-auto-retry action types; A pendant notification/audio event for bridge outage and recovery (not just a response to a spoken request); A compact cross-surface recovery receipt correlating relay alert, Mac job, browser command, and final result; A way to distinguish temporary missing permissions/offline extension from a permanently unsupported action and suppress repeated alerts

### "“When I’m away from my Mac, let me tap the pendant to queue a task with a short voice note; when I get back, have the relay and Mac resume it from the right project and tell me exactly what completed, without making me repeat myself.”"
- **useful because:** Today a dropped Mac/browser connection turns an in-progress request into a conversational dead end: the owner must remember what they asked, repeat it, and reconstruct context. A wearable tap plus relay persistence can capture intent at the moment it matters, while the Mac later supplies files, apps, and authenticated sessions. This is a true handoff between the body, always-on service, and private machine rather than a Mac-only task runner.
- **path:** relay-realtime → mac-planner → mac-terminal → unified
- **model tier:** Realtime only for the brief voice note and immediate acknowledgement; deterministic relay storage, deduplication, and delivery; background gpt-4.1-mini to normalize the note and select the active project when the Mac reconnects; planner tier only if the resumed task is genuinely ambiguous.
- **latency:** Pendant acknowledgement under 500 ms using a local canned response; relay persistence under 1 second; resume within 15 seconds of Mac reconnection; completion spoken or queued for playback within 5 seconds after the Mac returns a receipt.
- **cost:** Tiny for short notes: roughly 300–800 input tokens to normalize only when needed, plus a few hundred tokens for a completion summary. Most handoffs use deterministic storage and existing Mac execution, so the dominant cost is ambiguity escalation.
- **security:** Voice notes and task metadata are stored in relay D1 and may contain private intent; encrypt or minimize them and expire unclaimed handoffs. Never transmit authenticated page contents, arbitrary shell output, or secrets to the relay. Bind delivery to the paired pendant and Mac identity, preserve project/session provenance, and require the existing owner policy before any destructive or external side effect.
- **missing:** A pendant-side offline capture and acknowledgement mode that survives a dropped relay link; A durable relay handoff record containing audio/text note, capture time, pairing identity, intended surface, project hint, and lifecycle state; A reconnect protocol that lets the Mac claim handoffs exactly once and report progress/receipt updates; A context reattachment operation that resolves the handoff to the Mac's active project, session, and relevant recent thread without resending the entire conversation; A pendant playback queue for completion receipts when the owner is no longer in a live voice session


## Changes it proposed to its own stack

### `mac-harness` — Make every executed action, including actions nested inside a planner result and browser-bridge commands, emit a durable execution envelope: jobId, action index, surface, routing tier/model, start/end timestamps, timeout, exit code, stdout/stderr byte counts plus redacted digest, idempotency key, undoability, and a normalized failure class. Backfill the envelope at job finalization when a child executor cannot report synchronously, and expose aggregate counters and per-job drill-down through /journal and /jobs/:id/receipts.
- **owner gets:** The Mac currently has 147 actions but 112 are unattributed to a model tier, 14 failed, and none are marked undoable. When the pendant says “it failed,” the owner cannot tell whether the planner, shell, browser extension, timeout, or missing Mac permission caused it, nor whether retry is safe. This turns every spoken completion into a trustworthy, concise receipt without adding approval gates or reducing capability.
- effort: Medium: shared envelope middleware in executor/jobTracker, adapters in browserBridge and shell execution, failure taxonomy, schema migration for the JSON job store, and dashboard/journal rendering; add tests for timeout, child-process failure, extension offline, and planner escalation.  ·  risk: Existing receipts and old jobs may have partial fields; version envelopes and mark unknown rather than guessing. Redact secrets and cap captured output to hashes/previews. If instrumentation itself fails, action execution must continue and a local fallback receipt should be written.
- cost: No meaningful model cost; a few hundred bytes per action and modest JSON storage growth. Periodic compaction can retain full detail for the newest 120 jobs and aggregates for older records.  ·  latency: Under 5 ms per action for envelope writes in memory; one bounded disk flush at job completion. No extra planner round trip.
- security: Improves auditability without changing authorization. Store only metadata and redacted output digests by default; keep command text under existing local-agent protections and never send stdout/stderr wholesale to relay.
- depends on: Keep existing actionReceipts.js, jobTracker.js, routingStats.js, and /journal contracts compatible; Define a shared action-envelope schema used by shell, Mac typed actions, and browser bridge; Add correlation propagation from pendant request through relay job and local Mac child actions

### `hardware` — Add a small encrypted nonvolatile event spool dedicated to handoff intents—an I2C/QSPI FRAM or protected flash ring buffer with monotonic sequence numbers, plus a firmware button gesture that commits a short voice-note reference and acknowledgement state before attempting the relay upload. The spool should retain at least 64 compact events and support atomic append/acknowledge, replay after reboot, and secure erase after receipt confirmation.
- **owner gets:** A tap made while the owner is walking, underground, or between Wi‑Fi and cellular coverage would not vanish. The pendant could honestly say “saved; I’ll finish this when your Mac is back,” then deliver the request later without requiring the owner to remember it.
- effort: Medium hardware revision and firmware work: select FRAM/protected flash, add the bus and secure-storage key handling, implement a power-loss-safe ring format, and integrate replay with relay pairing. Prototype first using existing flash to validate the protocol before spinning the board.  ·  risk: A damaged or worn storage cell could lose queued intents; use sequence/CRC, wear leveling, and duplicate relay acknowledgement. Voice data is sensitive, so store encrypted compressed audio or preferably a short transcript plus bounded audio fallback, and erase after receipt. A full spool must produce a local overflow indication rather than silently dropping the oldest request.
- cost: Approximately $1–$4 per device for a small FRAM/protected-flash part and minor PCB assembly impact; negligible idle power, brief write current during a tap. No recurring model cost for the storage itself.  ·  latency: Local commit acknowledgement under tens of milliseconds; replay is asynchronous and does not delay normal conversation.
- security: Adds a durable local copy of private intent, so keys must be device-bound and inaccessible over unauthenticated UART. Secure erase and pairing-scoped replay are required; never treat the spool as a general filesystem.
- depends on: Define the relay handoff record and exactly-once acknowledgement protocol; Implement pendant firmware event capture and reconnect replay; Add paired-device key provisioning and receipt-driven deletion; Provide a relay-to-pendant completion playback queue


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface capability: durable pendant handoff notes that survive Mac/relay disconnection and resume exactly once when the Mac returns, plus a hardware change for an encrypted nonvolatile pendant event spool. Both include missing implementation and security details.

**Biggest unknown:** Whether the current pendant firmware has enough spare flash/bus capacity for an atomic encrypted event spool; a hardware/firmware inspection would be needed in a future round.

