# Harness derivation — faculty-judgement — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me my morning brief, but only speak items that are genuinely deliverable now; if playback is interrupted or never starts, leave exactly one retry for me and tell me what was missed.”"
- **useful because:** The current scheduled jobs can complete on the relay while audio is never downloaded or heard, and duplicate daily routines can produce repeated briefs. This makes the brief a closed-loop promise rather than a generation receipt: one deduplicated decision, one delivery attempt, and an honest missed-item state.
- **path:** relay → mac → pendant
- **model tier:** Use the cheap/background model for triage and deduplication; reserve realtime only for the short spoken retry or owner follow-up.
- **latency:** Brief assembly under 10s in the background; delivery ACK handling is asynchronous; retry notification should be under 1s after a confirmed interruption when the link is available.
- **cost:** Roughly one background model call per brief (typically <$0.03); delivery ACKs and arbitration are local/HTTP bookkeeping, not model calls.
- **security:** Only opaque artifact IDs and delivery states cross surfaces. Apply briefingTriage redaction before TTS; never retry sensitive content aloud automatically. Require the owner’s existing physical playback/stop semantics for replay, and expire stale items.
- **missing:** A durable dedupe key joining the two existing morning routines to one brief; A semantic brief-item/artifact mapping from generation through pendant playback; A relay-side retry scheduler that consumes record_pendant_delivery_event without creating duplicates

### "“After a Mac or link outage, continue the thing I asked for instead of making me remember and repeat it—show me the exact step that is safe to resume, and ask before any irreversible step.”"
- **useful because:** Today an in-flight relay job can remain processing forever after a Mac crash, while relay and Mac IDs are not joined. A restart-safe continuation would preserve the owner’s intent, avoid duplicate external actions, and make recovery visible rather than silently losing work.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap deterministic lease/recovery logic for detection and safe step selection; realtime model only if the owner asks to resolve an ambiguous continuation.
- **latency:** Detect an orphan within 1–2 minutes; present a one-sentence recovery status on reconnect; no model wait for routine lease handling.
- **cost:** Negligible API cost for lease sweeps and receipts; occasional <$0.01 model call only for ambiguity.
- **security:** Never replay a non-idempotent or destructive step automatically. Revalidate current browser/Mac state and run autonomy_policy_evaluate; require physical consent for external side effects. Keep snippets redacted and provenance-linked.
- **missing:** relay_jobs lease_until plus requeue/expiry sweep; Durable relay-job-id ↔ Mac-job-id foreign-key mapping, not telemetry-only; A typed resume checkpoint containing the last completed idempotent step and its evidence

### "“When you tell me something is clear, waiting, or done, let me ask ‘why?’ and get the short evidence chain—including what you could not read—without exposing private source text aloud.”"
- **useful because:** The system can currently produce confident all-clear calendar/day-plan answers when EventKit is unauthorized, and completion receipts do not explain the evidence-to-judgement chain. This gives the owner a trustworthy answer and distinguishes observed, inferred, and unreadable instead of pretending absence is emptiness.
- **path:** relay → mac → pendant
- **model tier:** Deterministic provenance and permission reconciliation first; cheap model only to compress a verified chain into one sentence.
- **latency:** Under 2s for an explanation from stored receipts/evidence; no fresh broad scan unless the owner explicitly asks.
- **cost:** Usually no model call; <$0.005 when compression is needed.
- **security:** Spoken explanations default to source titles, timestamps, confidence, and redacted snippets only; sensitive details stay dashboard/local. Revocation must invalidate derived claims and future briefings, not just hide the capsule.
- **missing:** A unified explanation record connecting source read, permission/readability verdict, judgement, and delivered effect; A real capsuleId/source link on derived memory facts so revocation can propagate; A safe spoken-vs-dashboard field policy for provenance detail

### "“When the pendant behaves strangely, make me a reviewable bug report from its UART log: what happened, how often, whether audio was affected, and the smallest reproduction—not a vague ‘something failed’ and never send it without me.”"
- **useful because:** The owner explicitly wants the pendant to file its own bug reports, but the useful first version is an evidence-backed draft that correlates firmware diagnostics with audio delivery and preserves a human review boundary. It can turn an intermittent wearable failure into an actionable report without silently transmitting private audio or submitting externally.
- **path:** pendant → mac → relay
- **model tier:** Deterministic UART parsing and metric extraction first; a cheap background model summarizes the timeline and proposes a reproduction. Realtime is unnecessary unless the owner asks verbally for the current diagnosis.
- **latency:** Under 5s for a 30-minute log window and draft creation; longer logs run in the background and return a job receipt.
- **cost:** Usually <$0.01 for a compact summary; parsing and draft storage are local. No audio bytes need leave the device.
- **security:** Strip PCM, transcript, auth material, and opaque credentials from the draft; retain only counters, timestamps, firmware/build IDs, and redacted excerpts. Draft locally or in a private workspace, never submit automatically. Correlate only authenticated delivery events and preserve provenance so the owner can revoke the draft.
- **missing:** A production UART cursor/export from the connected nRF9160 and ESP32, with authenticated record boundaries; A structured parser for firmware-specific counters and build metadata rather than regex over arbitrary text; A correlation key joining UART records to audio artifact/session IDs; A local review UI that lets the owner edit and approve a draft

### "“When your bodies disagree about what happened, show me the disagreement in one sentence, let me choose the governing fact, and make that choice apply consistently next time.”"
- **useful because:** A Mac observation, browser page, relay receipt, and pendant event can each be locally plausible yet conflict. Today the system can collect evidence and explain actions, but it cannot turn the owner’s adjudication into a durable, scoped precedent shared by every body. This prevents the same disagreement from recurring and makes uncertainty visible instead of silently averaging it away.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic conflict extraction and precedent matching; use the background model only to compress competing evidence into a short owner-facing comparison.
- **latency:** Present a conflict within 3s of receiving the second contradictory observation; persist the owner’s choice immediately after one physical confirmation or explicit spoken confirmation for non-destructive facts.
- **cost:** Usually no model call; under $0.01 when summarization is needed. Storage is small typed records, not raw transcripts.
- **security:** Precedents must be scoped by subject, source, and expiry—not global truths. Never let a spoken correction authorize an external side effect. Preserve both rejected and selected evidence references, redact private snippets in spoken output, and permit revocation.
- **missing:** A typed conflict object with competing claims, freshness, provenance, and scope; A durable cross-surface precedent writer and reader; current fleet memory has a schema but no production writer; An owner-choice endpoint that records which claim governs without mutating source systems; Policy evaluation that can consume precedents as evidence rather than treating them as facts

### "“When I correct the assistant, turn that correction into a visible rule, test the rule against my existing routines and pending plans, and tell me what behavior will change.”"
- **useful because:** Corrections currently disappear into conversation or loosely typed memory. The owner should not have to repeat “never send that,” “ask before this,” or “use this source instead” across the pendant, Mac, browser, and relay. A correction compiler would expose the proposed scope, find affected automation, and make the change auditable rather than silently changing behavior.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime model extracts the owner’s correction only when spoken; deterministic policy compilation, impact analysis, and enforcement should use the cheaper policy engine.
- **latency:** Acknowledge immediately; compile and show affected routines/plans within 5s; policy takes effect only after explicit owner confirmation.
- **cost:** One short realtime extraction call when needed, generally <$0.01; policy checks are deterministic.
- **security:** A correction must never broaden authority accidentally. Default to narrower scope, finite expiry, and fail-closed behavior. Do not persist raw speech; store the normalized rule plus provenance. Destructive or external-action rules require physical confirmation.
- **missing:** A durable policy registry with scope, expiry, precedence, and human-readable wording; A compiler from owner corrections into the typed autonomy policy schema; Impact analysis over routines, queued jobs, browser watches, and pending approvals; A cross-surface policy distribution and version acknowledgement protocol

### "“If the relay, Mac, browser, or pendant is unavailable, keep a truthful degraded version of my assistant alive, then reconcile what it did and did not know when the connection returns.”"
- **useful because:** Today each body can appear healthy while another is absent, and many operations simply stop or leave stale state. The owner needs continuity with explicit capability boundaries: the pendant can still surface queued alerts, the Mac can still do local work, and the relay can queue intent—but no body should pretend it completed a job it could not verify.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic capability-state machine and reconciliation; background model only for merging ambiguous offline notes after reconnect.
- **latency:** Degraded-mode decision under 500ms locally; reconnect reconciliation within 10s for ordinary state and under 2s for safety/cancellation events.
- **cost:** Near-zero model cost for health/state transitions; occasional <$0.02 background merge for ambiguous offline records.
- **security:** Offline bodies must not perform irreversible external actions without fresh authority and owner consent. Cache only opaque intents and minimal metadata, encrypt local queues, expire authority while disconnected, and surface every unverified completion explicitly.
- **missing:** A signed, versioned capability lease for each surface; An offline intent envelope that is distinct from storing raw audio and can be reconciled idempotently; Cross-surface event ordering and conflict resolution; A reconnect report that distinguishes completed, attempted, expired, and unknown actions


## What it asked for

_Nothing._
