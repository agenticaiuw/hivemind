# Harness derivation — unified — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run a live pendant check now, then tell me whether I can safely have a conversation.”"
- **useful because:** Today the owner can run pieces of an audio fixture or inspect jobs, but cannot get one owner-facing verdict that starts with the physically connected USB pendant, exercises capture and playback, and distinguishes a bad cable/bridge, codec timing, or relay loss. This turns the hardware that is already on the desk into a trustworthy pre-call check rather than discovering failure mid-conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for the deterministic test and report; realtime only to speak the short verdict if requested
- **latency:** 15–30 seconds for a local USB fixture; up to 60 seconds if a relay round trip is included
- **cost:** ~$0.01–$0.05 per invocation; dominated by optional model-generated explanation, not the deterministic probes
- **security:** Synthetic audio only by default; never upload microphone content. Require explicit confirmation before any test that transmits captured speech. Return raw counters and a signed run ID so the spoken verdict is auditable.
- **missing:** A USB-aware test orchestrator that claims the pendant and ESP32 bridge, runs the existing audio diagnostic fixture, then invokes validation and correlates serial counters; A typed HEALTHY/DEGRADED/FAILED report with failure-domain classification; A local-only mode that refuses relay/network traffic

### "“Approve the staged action I just held the pendant for, execute it once, and show me exactly what happened.”"
- **useful because:** The physical approval latch can already emit a nonce, and the Mac already has action receipts, but the owner still lacks a closed loop: staged challenge → deliberate wearable approval → relay/Mac execution → one receipt proving the approved plan, world state, and result are the same. This is the single most important cross-surface safety feature because it makes the pendant a real consent boundary instead of decorative feedback.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background/planner for staging and receipt explanation; deterministic execution and nonce verification must not depend on a model
- **latency:** Approval event visible within 2 seconds over USB or next reconnect over LTE; execution starts within 5 seconds after verification; receipt available within 10 seconds
- **cost:** ~$0.01–$0.08 per action; model cost only for natural-language staging/summary, while hashes, expiry, replay checks, and execution are deterministic
- **security:** Bind nonce to plan digest, world fingerprint, expiry, and monotonic device counter. Never send secrets/page contents to the pendant. Reject duplicate, expired, changed-world, or already-consumed approvals. Keep approval and execution credentials separate; browser actions require target/session binding and explicit owner confirmation for off-machine or irreversible effects.
- **missing:** Implement the approvalHandoff relay store and delivery/readback path; the current contract is schema-only and deliveredAt can never be set; Consume the physical_transaction_approval_latch event at the relay and route it to the exact pending approval; Wire orchestrator/bridge to prepare staged actions and close ledgers; add a durable relay job lease/requeue path; Dashboard control showing pending, approved, refused, executed, and receipt states

### "“When the Mac or link drops, recover only the safe parts of what you were doing and ask me about anything ambiguous.”"
- **useful because:** The code already computes replaySafety and a durable ledger, but no production caller turns that into recovery. An owner-facing recovery mode would prevent duplicated messages or browser submissions while automatically continuing idempotent/additive work and presenting a compact list of blocked steps on the next conversation.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** background deterministic resume planner; realtime only for the next-conversation explanation and owner decision
- **latency:** Scan on bridge startup/reconnect in under 2 seconds; resume safe steps within 5 seconds; no automatic replay of unrepeatable/unknown actions
- **cost:** ~$0.005–$0.03 per recovery scan; mostly local deterministic work, with model cost only when summarizing ambiguous steps
- **security:** Gate auto-resume on replaySafety idempotent/additive, not reversibility. Require fresh physical approval for irreversible/off-machine/uncontained work. Bind resumes to unexpired leases and original plan/world digest; stop all later steps after the first ask. Do not infer completion from a missing receipt.
- **missing:** Fix ordinary orchestrator runs to close their ledgers, otherwise every historical plan appears interrupted; Add relay_jobs lease_until and a requeue sweep for Mac outages; Call planResume from startup/reconnect and persist a human-visible recovery decision; Run the browser bridge supervisor sweep so orphaned command leases actually expire

### "“Move this live conversation from USB to LTE (or back) without making me repeat myself or hearing duplicate audio.”"
- **useful because:** The pendant is physically testable over USB today but is not LTE-registered. Once both paths exist, a transport switch is exactly when conversational systems lose or duplicate a turn. A cross-surface handoff would preserve the last committed turn boundary, drain old audio, and resume on the new path with one continuity receipt.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic transport/session controller; realtime model only continues the conversation after the handoff
- **latency:** Under 1 second at a turn boundary; never switch mid-frame or mid-speech
- **cost:** <$0.01 per handoff; protocol/state work dominates, not inference
- **security:** Authenticate both transport sessions to the same device/session nonce; reject stale frames and duplicate sequence numbers. Do not silently fall back to a phone or another device. Expose the selected transport and any dropped frame range to the owner.
- **missing:** Relay-side dual-path session coordinator with atomic ownership transfer; A signed handoff receipt carrying device ID, conversation ID, last uplink/downlink sequence, and transport; Mac bridge support for draining and acknowledging the USB session before LTE takes ownership; Owner-configurable transport policy (lte_only, phone_preferred, phone_fallback)

### "“Before you speak, tell me whether this answer came from my live audio, a browser session, a Mac file, or an inference—and let me ask for the evidence without replaying private content.”"
- **useful because:** The owner cannot currently distinguish what the system directly observed from what a model inferred. A provenance answer would make spoken claims inspectable across the pendant, relay, Mac, and browser while exposing only hashes, timestamps, source labels, and confidence unless the owner explicitly requests the underlying content.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background provenance assembler; realtime tier only for a short spoken source label when latency matters
- **latency:** Under 300 ms when evidence receipts already exist; asynchronous for a full evidence bundle
- **cost:** ~$0.01–$0.06 per answer, mostly optional summarization; hashes and joins are deterministic
- **security:** Evidence must be least-privilege and bound to specific tabs/apps/files. Never send raw browser page contents or private audio to the pendant by default. Preserve provenance through summarization and label unsupported inference as unsupported, not low-confidence fact.
- **missing:** A provenance envelope attached to every model claim and TTS response; Cross-surface evidence join for pipeline events, browser results, Mac receipts, and audio delivery; Spoken source labels and a dashboard drill-down that can redact content; A policy for confidence versus direct observation

### "“If the Mac, browser, and pendant disagree about what happened, tell me the disagreement plainly and ask one focused question instead of choosing a story.”"
- **useful because:** Today each surface can report its own status, but there is no owner-facing conflict object that compares their timestamps, sequence numbers, and receipts. This would prevent a relay-accepted response from being reported as heard, or a browser command as completed merely because a Mac job succeeded.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic reconciliation first; background model only summarizes the ranked hypotheses and asks the focused clarification
- **latency:** Under 2 seconds for existing receipts; remain unresolved rather than waiting indefinitely for an offline surface
- **cost:** ~$0.01–$0.04 per conflict; joins and ordering are deterministic, with a small optional summarization call
- **security:** Expose only metadata and redacted evidence by default. Bind comparisons to one job/conversation/device and distinguish clock uncertainty from actual contradiction. Never resolve a conflict by taking the most recent untrusted report.
- **missing:** A typed cross-surface event envelope with source clock, monotonic sequence, receipt ID, and confidence; A reconciliation engine that emits consistent, contradictory, missing, and indeterminate states; A dashboard and spoken interaction that asks exactly one clarification and records the answer as a policy decision; Clock-skew and offline-window metadata from pendant, relay, Mac, and browser


## Changes it proposed to its own stack

### `relay` — Add a transport-neutral turn commit protocol: every uplink and downlink frame is associated with a turn ID and monotonic sequence; the relay persists only the last committed boundary and a bounded receipt, and handoff requires old-path drain ACK plus new-path resume ACK. Reject frames below the boundary and mark gaps explicitly instead of replaying them.
- **owner gets:** Switching between the desk USB connection and a future standalone link would not make the owner repeat a sentence, hear an answer twice, or wonder which transport is active.
- effort: Medium: relay state/schema plus Mac bridge and pendant event plumbing; test with forced disconnects and the existing fault injector.  ·  risk: A bad boundary could suppress one frame or duplicate a response. Recover by requiring both ACKs, timing out to the old path, and exposing a visible failed-handoff state rather than guessing.
- cost: Negligible storage and compute; bounded per-session metadata only.  ·  latency: Adds one turn-boundary RTT, typically <1 s; no cost within a turn.
- security: Improves replay resistance, but the handoff receipt must be authenticated and scoped to device/session.
- depends on: usb_fallback_audio_session firmware behavior; A relay job/session lease and sequence-aware audio event schema

### `dashboard-ux` — Create a read-only “owner safety timeline” that joins staged approval, physical nonce event, execution receipt, browser target/session, and audio delivery/playback receipts into one chronological card. It must show missing links as gaps, never infer success from a job status, and offer no execute control until the approval loop is actually wired.
- **owner gets:** After asking the pendant to do something, the owner can answer the human question “did it happen, and did I hear the result?” without opening five logs or trusting a misleading green job badge.
- effort: Medium: typed join over existing receipt IDs plus dashboard rendering and redaction rules.  ·  risk: A join bug could falsely imply completion. Mitigate with explicit evidence provenance, per-surface timestamps, and an UNKNOWN state whenever any receipt is absent or clock ordering is ambiguous.
- cost: Low; indexed metadata reads, no model call required.  ·  latency: Near-instant for existing receipts; eventual updates as device acknowledgements arrive.
- security: High-value audit view, but redact page contents, audio, secrets, and raw browser text by default; bind visibility to the owner session.
- depends on: audio_delivery_ack_queue; physical_transaction_approval_latch; approval relay persistence/delivery; typed GET /jobs/:jobId/receipts and browser result records

### `context` — Add an evidence-bound claim ledger: before a response is rendered, assign each factual claim an immutable claim ID and attach source receipts, observation time, transformation steps, and an expiration time. When a source is deleted, stale, or contradictory, the claim becomes explicitly withdrawn or unknown rather than remaining in conversational memory. The ledger stores metadata and hashes by default, not raw audio or page content.
- **owner gets:** The assistant would stop confidently repeating an old or inferred fact after its source changed or was erased, and the owner could ask “why do you believe that?” and receive a concise, inspectable answer.
- effort: High: shared schema across realtime responses, Mac planning, browser observations, memory/context graph, and dashboard rendering.  ·  risk: Incomplete instrumentation could make many claims appear unknown. Recover by migrating high-value sources first, showing an explicit coverage indicator, and never silently treating missing provenance as proof.
- cost: Low-to-moderate metadata storage; modest per-response token overhead if provenance is summarized, with no raw-content requirement.  ·  latency: Small deterministic join cost; under 100 ms for local receipts, with no extra model call on the hot path.
- security: Improves auditability and deletion correctness, but claim metadata can itself reveal activity patterns; encrypt it, scope access, and honor erasure tombstones.
- depends on: Owner retention/deletion policy; A shared receipt ID format across relay, Mac, browser, pendant, and audio delivery; Cross-surface erasure receipts; Model response instrumentation that emits claim boundaries


## What it asked for

_Nothing._
