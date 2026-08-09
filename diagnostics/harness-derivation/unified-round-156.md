# Harness derivation — unified — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface health** — Mac agent v0.5.0, relay, Safari extension, Accessibility, Screen Recording, and AppleScript automation are all currently ready; Safari has 9 tabs and zero pending commands. Pendant pipeline history still contains processing jobs and one prior blocked approval that was spoken as waiting for dashboard approval.
  - evidence: GET /ops/snapshot 200 at round 156; GET /browser/status 200; GET /pipeline 200

## Capabilities it proposed

### ""Keep this conversation with me when I unplug the Mac and walk away; when I reconnect or LTE returns, continue exactly where we stopped without repeating a turn or losing my approval state.""
- **useful because:** This is the core wearable promise: the Mac can provide the USB session today, while the pendant must remain the same conversation when its transport changes. Exactly-once turn handoff prevents duplicate speech, lost commands, and accidental re-submission of actions.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime for live turn arbitration; background model only for compact reconciliation summaries.
- **latency:** Transport handoff decision under 250 ms at a turn boundary; never interrupt or duplicate an active utterance. Reconnect reconciliation under 2 s.
- **cost:** Low incremental model cost; mostly sequence/state logic. One short realtime reconciliation call only when manifests disagree, typically <$0.01.
- **security:** Persist only turn IDs, transport ownership, action/approval nonces, and hashes—not raw audio. Reject stale transport generations and require the physical approval latch again if an uncommitted action crosses a handoff.
- **missing:** A durable cross-transport turn ledger shared by USB bridge, relay, and LTE session; Firmware emission of transport-generation and turn-boundary receipts; Relay job lease/requeue for a Mac that disappears mid-turn; A deterministic conflict policy for simultaneous USB and LTE ownership

### ""At the end of the day, tell me which things I asked you to do are still unresolved, with the exact evidence and the next safe step.""
- **useful because:** Commitments currently span speech, Mac jobs, browser tabs, and relay receipts. The owner should get one trustworthy closure report instead of remembering to ask each surface separately; it can distinguish done, evidenced-but-not-confirmed, blocked, and never-dispatched.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/planner tier for nightly aggregation; realtime only when the owner asks a follow-up.
- **latency:** Nightly report ready before the configured morning routine; interactive lookup under 3 s.
- **cost:** Usually <$0.02 per nightly report with deterministic filtering and a small planner pass; evidence retrieval dominates, not audio.
- **security:** Search only explicitly bound apps/tabs and jobs. Do not infer completion from intent or spoken acknowledgement. Redact page contents and expose only evidence excerpts, timestamps, and provenance. Mutating a blocked item always requires the existing physical latch.
- **missing:** A durable commitment record emitted at utterance time with scope, deadline, and evidence bindings; A scheduler that invokes commitment_evidence_query and joins returned candidates to relay/Mac receipts; A user-facing disposition state and expiry policy (the owner retention policy is still unknown)

### ""Before you read anything private aloud, give me a one-line exposure receipt: what source, which app or tab, what left the Mac, and whether it was stored; let me cancel before speech starts.""
- **useful because:** The owner currently has no compact, human-auditable answer to what crossed the browser/Mac/relay boundary. A spoken receipt makes privacy concrete at the moment it matters, while the pendant's local latch remains an immediate emergency stop.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy and redaction; realtime model only to phrase the already-typed receipt.
- **latency:** Receipt generated within 150 ms before playback; cancellation must mute within one audio frame. No network round trip may be required for the local stop.
- **cost:** Negligible model cost for templated receipts; bounded metadata storage under a few KB/day.
- **security:** Receipt itself must avoid repeating secrets. Use source/tab identifiers, sensitivity class, byte counts, hashes, destination, retention class, and delivery status. Never log raw DOM or audio. If classification is uncertain, default to withhold and require physical approval.
- **missing:** A single provenance envelope emitted by browser extraction, Mac action, relay persistence, and TTS playback; A pre-playback gate that can hold synthesized audio until the receipt is acknowledged or cancelled; A bounded owner-visible exposure history with the still-unknown retention/deletion policy

### ""Compare what these two open sources say about the same claim, tell me exactly where they disagree, and let me inspect the quoted evidence without you choosing a winner.""
- **useful because:** The owner can reach private browser tabs and public research, but cannot currently get a provenance-preserving disagreement map. This would prevent confident answers that silently blend incompatible dates, definitions, or numbers.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/planner tier for extraction and alignment; realtime only for the short spoken summary.
- **latency:** Under 10 seconds for two already-open sources; playback waits until both evidence capsules are complete.
- **cost:** Typically <$0.03 per comparison; extraction and alignment dominate, with no audio-model call beyond speech.
- **security:** Read-only and bound to explicitly selected tabs or files. Quote only capped spans, redact secrets and form values, label inference versus verbatim evidence, and never let page instructions become commands.
- **missing:** A typed cross-source extraction contract with quote offsets and source fingerprints; A semantic claim-alignment/difference engine that preserves unresolved disagreement; A dashboard and pendant interaction for selecting two sources and drilling into evidence

### ""Give me a private, local-only answer about what is on my Mac right now, and prove that no browser, relay, or cloud model was involved.""
- **useful because:** Some questions—open windows, a local file, a draft, or an on-device status—should not leave the machine. Today the owner has no enforceable, human-readable distinction between local observation and cloud-assisted reasoning.
- **path:** pendant → mac-bridge → dashboard
- **model tier:** Deterministic local collectors plus a local planner/model; never route this mode to realtime cloud inference.
- **latency:** Under 2 seconds for local status and under 8 seconds for local document synthesis; refusal is immediate if the local-only boundary cannot be proven.
- **cost:** Near-zero API cost when local model/AppleScript extraction suffices; local compute and bounded document parsing dominate.
- **security:** A signed execution receipt must identify every process, file, and model used, with hashes and timestamps. No raw content or telemetry leaves the Mac. If any required component is not attestable, refuse rather than silently downgrade.
- **missing:** A hard model-routing/data-egress policy with local-only refusal semantics; Process/model attestation and a signed no-network receipt; Local model availability and a typed safe read surface for files, windows, and AppleScript results

### ""When I ask you to investigate something, show me a bounded research plan first, then stop automatically when the evidence threshold is met or the time/budget limit is reached.""
- **useful because:** The owner currently cannot tell whether a research request is still searching, has enough independent evidence, or is spending unbounded time and money. A stop condition makes delegated work predictable and reviewable rather than opaque.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for research and evidence synthesis; realtime only to announce plan, stop, or request a decision.
- **latency:** Plan spoken within 2 seconds; execution runs within an owner-selected wall-time and source-count budget, with a hard stop and partial result.
- **cost:** Bounded by explicit source/model caps; normally <$0.10 for a small investigation, with cost shown before execution.
- **security:** Read-only by default, explicit domain/tab allowlist, no page-derived instruction execution, and no hidden continuation after the stop condition. Any action beyond research requires a separate staged transaction and physical approval.
- **missing:** A durable research budget/stop-condition state machine; Evidence-quality metrics (independence, freshness, contradiction, source coverage); A pause/resume UI that preserves partial evidence without treating it as a conclusion


## Changes it proposed to its own stack

### `integration` — Close the currently dead approval loop end to end: when a plan is blocked, persist the existing approvalHandoff record in the relay, mark the spoken readback as delivered, surface it on the next pendant conversation (never an unsolicited interruption), accept the physical_transaction_approval_latch nonce, and execute only if plan/world digest, TTL, and replay state still match. Replace the false 'waiting for your approval on the dashboard' promise with a truthful pending status and a resumable next-conversation prompt.
- **owner gets:** Today the system can tell the owner that approval is waiting, but no dashboard or relay path can ever complete it. This turns a spoken dead end into a safe action the owner can actually finish with the button on the pendant.
- effort: Medium-high: relay D1 approval persistence and delivery receipts, bridge/orchestrator wiring, next-conversation prompt, and integration tests across reconnect and expiry.  ·  risk: A stale or duplicated approval could execute an old action. Mitigate with existing planDigest/world fingerprint/TTL, physical nonce and replay guard; default to refuse on any mismatch. Recover by leaving the plan pending for a new prepare cycle.
- cost: Negligible storage and request cost; one bounded approval record per pending plan. No routine audio or SD writes.  ·  latency: Adds one short pending-state read on conversation start; approval execution remains within normal Mac action latency.
- security: Improves security by making approval a real, action-bound physical confirmation rather than an unusable spoken claim. Keep approval and execution credentials separate as a follow-on hardening step.
- depends on: Relay implementation of shared/approvalHandoff.js APPROVAL_STORE_CONTRACT; orchestrator closeLedger call so completed plans are not falsely interrupted; relay_jobs lease_until and requeue sweep; Pendant delivery path that supports the existing physical_transaction_approval_latch; Next-conversation pending approval selection and truthful speech


## What it asked for

_Nothing._
## Its own summary

Round 156 produced three recorded cross-surface capabilities: exactly-once USB/LTE conversation handoff, evidence-backed unresolved-commitment closure, and pre-playback privacy exposure receipts. I also recorded live health: Mac, relay, Safari, Accessibility, Screen Recording, and automation are ready; pipeline history still exposes processing jobs and a dead approval promise. A change proposal was recorded to close the approval loop through the relay and physical latch.

**Biggest unknown:** The owner’s retention/deletion policy is still unknown and should govern exposure receipts, commitment evidence, and pending approval records. Technically, the remaining blockers are LTE registration, a durable cross-transport turn ledger, relay approval persistence/delivery, and relay job leases.

