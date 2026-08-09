# Harness derivation — unified — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I start an important conversation, prove the whole audio path is healthy; if it is not, tell me exactly what will fail and switch to the safest working profile.”"
- **useful because:** The shipped 24 kHz path is excellent but runs near the single-core budget and has a history of framing, optimization, and startup-audio failures. A deliberate, bounded rehearsal gives the owner a meaningful go/no-go answer instead of discovering loss while speaking, and can use the already-shipped congestion guard without inventing a new always-on test.
- **path:** pendant → relay-realtime → mac-planner → mac-bridge
- **model tier:** deterministic diagnostics and profile selection; background model only to explain the result in plain language
- **latency:** 15–30 seconds on explicit request, never on the hot path; immediate local mute/fallback if a live call is already degraded.
- **cost:** <$0.01 per rehearsal; bandwidth and device CPU dominate, with no routine SD writes.
- **security:** Synthetic fixtures must contain no owner speech and must not be persisted as audio. Require explicit invocation, cap duration, and return counters rather than raw recordings.
- **missing:** A callable orchestration route that invokes the existing audio diagnostic fixture and congestion guard together; A bridge acknowledgement correlated to the fixture run; A safe profile-apply operation with an owner-visible receipt

### "“My pendant is silent or stuck—diagnose the entire path, tell me the one cause you found, and repair only that cause if it is safe.”"
- **useful because:** Today failures span pendant state, relay jobs, the Mac bridge, and browser polling, so the owner gets repeated retries or a vague timeout. This turns a cross-surface incident into one bounded diagnosis with a dry-run explanation, an idempotent repair when allowed, and a receipt proving what changed.
- **path:** pendant → relay-realtime → mac-bridge → mac-planner → browser-extension → dashboard
- **model tier:** deterministic health correlation and repair selection; background model only for concise owner-facing explanation
- **latency:** Diagnosis under 3 seconds; safe repair under 10 seconds; never interrupt an active conversation or mutate without confirmation for non-idempotent repairs.
- **cost:** <$0.01 per incident; dominated by health probes, not model inference.
- **security:** Least privilege per repair kind, no page contents in diagnostics, redact tokens and audio metadata, require an explicit confirmation token for mutation, and return before/after receipts. If confidence is low, stop at diagnosis.
- **missing:** A single incident coordinator that correlates pendant events, relay receipts, Mac jobs, browser commands, and system health; A dry-run-to-repair state machine with idempotency and a lease; A pendant-visible result path that does not pretend an unprompted binary push is available

### "“Continue the task I started earlier, but first tell me exactly which steps already happened and which steps are safe to run again.”"
- **useful because:** A restart currently leaves the owner to find a job or ledger ID and manually interpret partial work. A spoken continuation should use durable workbench and ledger evidence to avoid duplicate messages, writes, or browser submissions, while clearly stopping when replay safety is unknown.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic ledger/workbench reconciliation; background model only to summarize the handoff
- **latency:** Read-only handoff under 3 seconds; execution begins only after explicit confirmation and runs asynchronously with progress receipts.
- **cost:** <$0.01 for reconciliation; normal action execution costs apply only after confirmation.
- **security:** Gate on replaySafety, not reversibility; require fresh confirmation for unrepeatable or unknown steps; bind continuation to jobId, plan digest, and world fingerprint; never infer completion from a missing receipt.
- **missing:** Production caller for GET /workbench/jobs/:jobId/handoff and GET /workbench/contexts/:contextId; Correct ledger closure for ordinary completed orchestrator runs; Relay job lease expiry/requeue so a dead Mac cannot strand work; A spoken/dashboard confirmation path for blocked steps

### "“When a meeting on my Mac starts, put the pendant into privacy mode automatically; keep it private until I physically release it, and show me which meeting caused the lock.”"
- **useful because:** The pendant's privacy latch is only useful if the owner remembers to activate it. Calendar-aware entry would prevent accidental capture during scheduled meetings, while requiring a physical release prevents software, calendar edits, or a stale Mac from silently re-enabling capture. This is a genuinely cross-surface safeguard: Calendar on the Mac supplies intent, the relay delivers the staged state, and the pendant enforces it locally even after links fail.
- **path:** mac-planner → relay-realtime → pendant → dashboard
- **model tier:** deterministic calendar matching, state transition, and physical-latch enforcement; no expensive model needed except optional meeting-title summarization
- **latency:** Enter privacy within 1 second of a confirmed meeting start; remain effective offline; release only after a deliberate pendant gesture and reflect convergence within 5 seconds.
- **cost:** Negligible model cost; one calendar read and a small signed state event per transition. No audio or meeting content needs to leave the Mac.
- **security:** Default to privacy on ambiguous overlaps, never infer a meeting from email text, minimize the title to a local label, never auto-release, and treat calendar deletion as insufficient to unlock. The pendant must persist the lock and emit a receipt when it enforces it.
- **missing:** A calendar-to-relay privacy policy and schedule evaluator; A signed staged privacy command bound to a meeting instance and expiry; A relay delivery/convergence path for the already-accepted local_privacy_latch; A dashboard view explaining the active lock and its release requirement


## Changes it proposed to its own stack

### `integration` — Make every extracted context fact a first-class provenance object with an immutable factId, source capsule IDs, derived-copy links, retention class, and a cascade-erase transaction. Add a read-only projection endpoint and a confirmation-gated erase endpoint that tombstones the fact and all replicas, while leaving Mac action journals untouched.
- **owner gets:** The owner can finally answer “what do you remember about me?” and remove one mistaken or unwanted inference without deleting the audit trail of actions the system performed.
- effort: Medium: adapt the context-graph storage and memory projection, add a relay tombstone protocol, and build a small dashboard list/detail/erase flow.  ·  risk: A partial off-machine erase could create misleading certainty. Use states requested, acknowledged, and converged; retry idempotently by factId and surface lag. Never hard-delete action history in this transaction.
- cost: Low storage and API cost; one small tombstone and provenance record per fact. No model call required for deletion.  ·  latency: Local listing remains fast; convergence may take seconds or longer while the relay is offline.
- security: Reduces privacy exposure by making hidden memory discoverable and erasable. Provenance must be redacted to the minimum evidence needed for recognition.
- depends on: A fact/evidence projection joining GET /memory/projection and GET /context-graph; Relay support for idempotent tombstones and convergence receipts; Dashboard confirmation UI

### `hardware` — Add a small secure element with non-exportable device keys and a monotonic counter to the production pendant or bridge, and make privacy-state transitions, physical approvals, and audio-delivery receipts sign over the counter, nonce, and state hash. Keep the current nRF9160 firmware behavior as the fallback when the element is absent, but refuse to claim tamper-evident provenance in that mode.
- **owner gets:** The owner could distinguish a real physical approval or privacy transition from a replayed, duplicated, or forged relay message. That matters when the pendant approves an action, claims it stayed private, or reports that audio was actually delivered—not merely accepted by the server.
- effort: Medium hardware revision plus firmware/relay protocol work; bench validation on the live USB-connected chips, then a production-board spin.  ·  risk: A lost or corrupted key could strand the device. Use factory provisioning with a recovery certificate and explicit unenrolled mode; never silently fall back from a claimed-attested state to unsigned behavior.
- cost: Roughly $0.50–$2 per unit and a few milliamps only during signing, depending on the chosen secure element; negligible steady-state draw.  ·  latency: Typically tens of milliseconds per signed event, off the audio sample path; batch only metadata, never PCM.
- security: Strongly improves anti-replay and provenance, but introduces key provisioning and replacement trust decisions. The relay must reject counter rollback and expose enrollment state.
- depends on: physical_transaction_approval_latch; local_privacy_latch; audio_delivery_ack_queue; A production device identity and key-rotation policy


## What it asked for

_Nothing._
## Its own summary

Round 216 produced three new recorded directions: (1) an explicit audio-path rehearsal/go-no-go command built around the shipped 24 kHz fixture and congestion guard, (2) a cross-surface silent/stuck-pendant diagnosis and least-privilege repair flow with dry-run and receipts, and (3) owner-invoked continuation of interrupted work using replaySafety, workbench handoffs, plan/world binding, and explicit confirmation. The extracted-fact inspection/erase idea was correctly rejected as an existing capability, so I did not rephrase it.

**Biggest unknown:** The remaining blocker is implementation wiring rather than discovery: the audio rehearsal needs a fixture-to-profile coordinator and bridge acknowledgement; recovery needs a safe repair state machine and pendant-visible result path; continuation needs ledger closure, relay job leases, and a real spoken/dashboard approval path. I still need the owner's policy decisions on phone-as-transport, interruption urgency, and product battery/size/thermal targets before those can be made product commitments.

