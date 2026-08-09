# Harness derivation — unified — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Forget the fact you inferred about my trip to Chicago, and show me everywhere it was copied.""
- **useful because:** Turns the owner's explicit retention rule into a trustworthy cross-surface operation: list the extracted fact, its evidence capsule and derived projections, delete the fact and copies, and honestly report replicated relay deletion as pending rather than claiming instant erasure.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background
- **latency:** Local inventory and deletion receipt in under 2 s; off-machine acknowledgement may take minutes and must remain visibly pending.
- **cost:** ~$0.01 per request; dominated by one background extraction/provenance pass and relay replication checks.
- **security:** Only extracted facts explicitly selected by stable fact ID may be deleted; preserve action/job audit history; redact evidence in the spoken confirmation; require physical approval latch for deleting multiple facts or sensitive evidence capsules.
- **missing:** Owner-visible extracted-fact index with stable IDs; Provenance edges from fact to evidence capsule and derived copies; Idempotent DELETE route spanning local facts, context graph, relay D1/R2, and pending-deletion receipts; Next-conversation delivery of the deletion receipt

### ""I approved that staged browser action with the pendant—continue it once, and tell me exactly what happened if the Mac was offline.""
- **useful because:** Closes the currently broken approval story without pretending the pendant can be interrupted: the relay holds a nonce-bound staged plan, the next conversation reads it, the physical approval latch authorizes it, and replay-safe work resumes exactly once after an outage.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background
- **latency:** Approval status available in the next turn under 1 s; execution begins when the Mac reconnects, with receipt within the job's normal completion time.
- **cost:** ~$0.005–$0.02 per staged action; mostly relay storage and a cheap planner only when the prior plan is no longer valid.
- **security:** Gate automatic continuation on replaySafety idempotent/additive, not reversibility; require fresh physical nonce approval for irreversible/off-machine/uncontained steps; bind plan digest, world fingerprint, expiry and approval counter; never replay unrepeatable browser submissions; keep audit history.
- **missing:** Relay implementation of shared approvalHandoff APPROVAL_STORE_CONTRACT; Conversation-triggered pending-approval readback and deliveredAt marking; Orchestrator closeLedger call to stop false interrupted plans; Relay job lease_until and requeue sweep; Executor that consumes planResume decisions instead of returning a GET-only preview

### ""Why did I hear a gap or distortion in your last answer? Diagnose the whole audio delivery path and give me one concrete fix.""
- **useful because:** Makes audio reliability owner-facing instead of a log dump: correlate the 24 kHz capture/Opus/modem/relay/bridge/playback evidence, identify whether loss, timing, CPU, or bridge buffering caused the defect, and recommend a measured fallback or repair.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background
- **latency:** A compact preliminary diagnosis in 3 s; full correlated report and recommended action under 30 s.
- **cost:** ~$0.02–$0.08 per incident; dominated by artifact analysis, not realtime inference.
- **security:** Use sequence numbers, counters and hashes rather than retaining speech; default to redacted metadata; require confirmation before changing codec profile or restarting a bridge; preserve the raw receipt but do not upload audio unless already authorized for that run.
- **missing:** Correlation key joining audio_delivery_ack_queue, pipeline events, relay receipts and bridge acknowledgements; Owner-facing verdict schema with evidence and confidence; Safe repair planner that can apply duplex_audio_congestion_guard changes only after confirmation; Real fault-injection implementation (the granted audio_link_fault_inject currently resolves to no live route)

### ""These two tabs and that file disagree. Which one should I trust, and what is the smallest piece of evidence that settles it?""
- **useful because:** Today the system can read browser pages, Mac state, jobs, and context separately, but cannot adjudicate a contradiction across them. This gives the owner a provenance-ranked answer with the disagreement preserved, rather than a confident blend or a destructive sync.
- **path:** pendant → browser → mac-bridge → relay → dashboard
- **model tier:** background
- **latency:** Spoken preliminary answer in 5 seconds; linked evidence bundle under 20 seconds.
- **cost:** $0.02–$0.10 per investigation, dominated by bounded page/file reads and one synthesis pass.
- **security:** Read only by default; bind investigation to named tabs and paths; never upload page secrets or file bodies beyond the selected evidence; require confirmation before changing either source.
- **missing:** Cross-source evidence model that retains source URL/path, observed time, hash and scope; Contradiction detector with explicit unknown/insufficient-evidence outcome; Owner-readable evidence bundle and stable citation IDs; Least-privilege bindings for browser tabs and Mac paths

### ""Give this browser session to the pendant for the next hour, but only let it read my travel booking and nothing else.""
- **useful because:** The owner cannot currently grant a temporary, narrow delegation boundary. This would let the wearable request information from an already-authenticated browser without handing the agent an all-or-nothing bearer credential, and would expire automatically.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** realtime
- **latency:** Grant/deny feedback within 1 second; each permitted read under 3 seconds.
- **cost:** Under $0.01 per read; mostly relay token validation and browser bridge messaging.
- **security:** Capability token must bind to exact tab/session, URL pattern, operation=read, fields, expiry and nonce; physical pendant confirmation required; deny navigation, downloads, form submission and cross-origin escalation; log every read and revoke immediately on privacy latch.
- **missing:** Scoped browser capability tokens rather than one agent-wide bearer token; Extension enforcement of tab, origin, operation and field scope; Pendant-readable grant/revoke state and physical confirmation binding; Revocation propagation and an owner-visible access log

### ""I changed my mind halfway through that multi-step task. Stop wherever it is, tell me what crossed the line, and leave me a safe continuation plan.""
- **useful because:** Current undo is whole-job and many actions are explicitly not undoable; cancellation does not produce a trustworthy boundary between completed, in-flight and not-started work. This gives the owner a deliberate stop with a durable, non-executing handoff that another turn or machine can safely inspect.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background
- **latency:** Stop request acknowledged immediately; boundary receipt and continuation plan within 5 seconds after in-flight actions settle.
- **cost:** $0.01–$0.05 per interruption, mostly receipt construction and state verification.
- **security:** Cancellation must win before dispatch of pending steps; never claim rollback where undo is unsupported; freeze the plan digest and world fingerprint; require fresh approval to continue; redact browser contents from the spoken summary.
- **missing:** Cooperative cancellation checkpoints in every executor and browser command lease; A durable partial-stop receipt linking ledger steps to job receipts; Planner that emits a safe continuation without executing it; Physical interrupt acknowledgement path that works during active playback


## Changes it proposed to its own stack

### `relay` — Make the granted diagnostic and fault-injection contracts live: add authenticated, read-only incident correlation over /ops/snapshot, /health, /jobs and pipeline receipts, plus a controlled SWB/legacy loss-and-jitter test endpoint that stores only redacted counters and an artifact ID. Add relay job lease_until/claimedAt expiry and a requeue sweep so a dead Mac cannot strand owner work for 24 hours.
- **owner gets:** When a response fails or the Mac dies, the owner gets a real diagnosis and recoverable work instead of a silent timeout; the system can prove whether the 24 kHz path degraded and retry safely.
- effort: Medium: route adapters, D1 schema migration, lease sweeper, and integration tests across relay/Mac/bridge; high test effort for fault profiles.  ·  risk: A lease race could execute a job twice; require idempotency keys and compare-and-set claims, and quarantine ambiguous jobs for owner review. Fault tests must never run against production audio without an explicit test profile.
- cost: Low storage and worker cost; fault artifacts capped and TTL'd. No routine speech audio retention.  ·  latency: Adds one lightweight health/lease sweep; diagnosis is seconds, not on the realtime audio path.
- security: Bearer-authenticated diagnostics, redacted artifacts, separate test namespace, no page contents or raw audio by default.
- depends on: audio_delivery_ack_queue; audio_path_diagnostic_fixture; GET /ops/snapshot; GET /health; GET /jobs/:jobId/receipts

### `context` — Add a signed, append-only claim/evidence graph for cross-surface contradictions: every imported browser fact, Mac file observation, relay receipt, and pendant event gets a source binding, observation timestamp, content hash, freshness window, and confidence independent of the model's prose. Add a resolver that returns competing claims and the minimum discriminating read instead of collapsing them.
- **owner gets:** The owner can ask which source is trustworthy and receive an answer that shows what was actually observed, what is stale, and what would settle the disagreement—without silently merging incompatible versions.
- effort: High: schema and retention rules, adapters for browser/Mac/relay/pendant receipts, deterministic conflict tests, and dashboard citations.  ·  risk: Bad freshness assumptions could hide a valid source; default to showing both claims and 'insufficient evidence'. Never let this layer mutate source systems.
- cost: Small persistent metadata overhead; background synthesis only when the owner asks.  ·  latency: Observation writes add milliseconds; adjudication takes seconds and is off the realtime audio path.
- security: Hash and source metadata by default; encrypt sensitive evidence references; enforce tab/path bindings and owner deletion semantics for extracted claims.
- depends on: GET /context-graph; GET /machine-context; GET /browser/sessions; GET /jobs/:jobId/receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one relay change: provenance-preserving fact erasure, next-conversation physical approval/resume, owner-readable audio incident diagnosis, plus live fault-injection/incident routes and relay leases. Discovery confirms the existing stack has many useful primitives, but the new granted diagnostic tools did not resolve to live implementations when called.

**Biggest unknown:** Whether the orchestrator will wire the granted schemas to real routes or expects implementation in the workspace; specifically audio_link_fault_inject and incident_diagnostics currently return unresolved, so I cannot truthfully run SWB fault tests or correlated incident snapshots yet.

