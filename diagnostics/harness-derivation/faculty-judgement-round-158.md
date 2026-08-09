# Harness derivation — faculty-judgement — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Make my morning brief trustworthy: reconcile conflicts first, then give me one brief at the right time and tell me what you could not verify.""
- **useful because:** The owner currently has duplicate 07:00/07:30 routines, conflicting timezone evidence, and calendar reads that can silently look empty when unauthorized. This turns a brief from plausible prose into a visibly qualified decision, and prevents duplicate audio.
- **path:** relay → mac → pendant
- **model tier:** background for reconciliation and ranking; realtime only for the owner's follow-up question
- **latency:** Under 5 seconds for the reconciliation; audio can be generated asynchronously and surfaced when the pendant is available.
- **cost:** ~$0.01–$0.04 per scheduled run; dominated by one background synthesis, not the deterministic checks.
- **security:** Do not speak calendar/mail contents until permissions and source freshness pass. Show source IDs and failed checks on the dashboard; spoken output should say only that a source was unavailable. Requires explicit owner policy for quiet hours and sensitive speech.
- **missing:** A scheduler hook that invokes reconcile_personal_state before routine audio generation; A duplicate-brief suppression key shared by routines and audio artifacts; A real EventKit permission/readability probe, not the existing Automation TCC probe; A relay-to-Mac durable record of the reconciliation verdict

### ""If my brief was downloaded but I never heard it, recover it once over USB, resume at the right item, and never play the same item twice.""
- **useful because:** The pendant is physically testable over USB now while LTE is unregistered. Today server acceptance is not proof of download or playback, and multiple scheduled briefings can create duplicate audio. This gives the owner reliable delivery rather than optimistic job completion.
- **path:** relay → mac → pendant
- **model tier:** Deterministic state machine for ACK reconciliation and dedupe; cheap background model only to produce a one-sentence recovery status.
- **latency:** Detect within one reconnect/USB heartbeat; recovery decision under 1 second, with audio transfer latency unchanged.
- **cost:** Negligible model cost in the common path; <$0.001 per recovery decision, with storage/USB traffic dominating.
- **security:** Artifact IDs and monotonic device sequences only; never send transcript or raw audio in recovery metadata. Require a bounded retry count and expiry so an old brief cannot replay unexpectedly. Owner must be able to cancel via the universal stop latch.
- **missing:** USB serial bridge transport from Mac to the currently attached nRF9160 and ESP32; A durable artifact/item idempotency index spanning routine runs and pipeline audio; A reconnect worker that consumes audio delivery ACKs and requeues only unplayed items; Playback-position checkpoints in the brief manifest

### ""Forget everything this source taught you about me, everywhere it was copied, and show me a receipt proving what was removed and what could not be removed.""
- **useful because:** Deletion is currently fragmented: evidence revocation does not reach derived facts, deleting a capture leaves a full-text context-graph copy, and there is no global forget operation. A source-linked erasure receipt is the only honest way for the owner to trust a privacy request.
- **path:** mac → relay → browser → pendant
- **model tier:** Deterministic provenance traversal and tombstone propagation; no expensive model unless the owner asks for a natural-language explanation.
- **latency:** Preview under 3 seconds; apply asynchronously, with a durable receipt and spoken completion only after every reachable store reports.
- **cost:** ~$0.001–$0.01 per request; dominated by local disk and relay writes, not inference.
- **security:** Default to preview and require explicit owner confirmation before destructive propagation. Never include secret source text in the receipt. Preserve only opaque IDs, hashes, timestamps, and failure reasons; expiration and retry must be explicit.
- **missing:** A common capsuleId/source link on every derived fact and context-graph entity; A cross-store tombstone/forget protocol for Mac, relay fleet memory, browser provenance, and pendant caches; A durable erasure ledger with per-store completion, retry, and irrecoverability states; Relay schema migration for memory events and revocations

### ""Before you send anything that commits me socially or professionally, show me the commitment you think I am making, what evidence supports it, and let me approve only that commitment—not the whole hidden action.""
- **useful because:** Today confirmation is action-shaped: approve a browser or Mac operation, often without a compact statement of the promise it creates. The owner needs protection from accidental commitments such as accepting a deadline, promising a deliverable, agreeing to spend, or speaking for someone else. This is a semantic boundary no single node can provide: the browser sees the draft and recipient, the Mac sees local context, the relay judges the commitment, and the pendant provides deliberate physical consent.
- **path:** browser → mac → relay → pendant
- **model tier:** A background model extracts a structured commitment from the proposed action and supporting context; deterministic policy evaluates risk; realtime is used only if the owner asks a follow-up question.
- **latency:** Prepare the commitment card in 3–8 seconds; approval response under 500 ms once the owner presses the pendant button; never block ordinary read-only work.
- **cost:** Approximately $0.02–$0.10 per high-stakes draft, dominated by semantic extraction and context comparison. No model call for already-classified low-risk actions.
- **security:** The commitment card must minimize recipient and message content, redact secrets, and retain evidence references rather than raw private text. Sending remains impossible until physical approval binds to the exact commitment hash, recipient set, and expiration. If extraction confidence is low, fail closed and ask the owner to review the original draft.
- **missing:** A commitment schema covering promise, deadline, recipient, spend, representation, confidence, and reversibility; Semantic extraction from browser drafts, mail drafts, calendar edits, and Mac actions; A policy rule that classifies social/professional commitments separately from ordinary reversible mutations; Binding of the commitment hash to the existing physical_transaction_approval_latch; A post-send receipt that records what commitment was actually made and whether it differed from the approved one

### ""Plan my day around the attention and battery I will actually have—not just the deadlines on my calendar—and tell me which tasks you deliberately left for later.""
- **useful because:** Calendar-based planning assumes the owner can always attend, listen, and act. A wearable system can observe pendant delivery capacity and interruption history, while the Mac sees active work and the relay sees deadlines. The owner gets a plan that respects finite cognitive and audio bandwidth, with explicit deferrals rather than an impossible checklist.
- **path:** pendant → mac → relay → browser
- **model tier:** Background model for task-duration and cognitive-load estimation; deterministic scheduling and policy checks for deadlines, quiet windows, battery, and delivery capacity.
- **latency:** Initial plan in under 10 seconds; incremental rescheduling under 2 seconds after a missed delivery, new deadline, or battery change.
- **cost:** $0.02–$0.08 per substantial replanning pass; most updates are deterministic and should cost effectively nothing.
- **security:** Do not infer health or emotional state from microphone data. Use only explicit owner settings, device telemetry, task metadata, and observable interruption outcomes. Keep sensitive task titles out of spoken replanning notices unless the owner permits them.
- **missing:** A shared resource model for owner attention, pendant availability, audio queue capacity, Mac activity, and browser availability; Task estimates and completion evidence linked to the existing day-plan and job receipts; A scheduler that can defer or split reversible work without changing external commitments; Owner-visible explanations for every deferral and a manual override path; Battery and delivery telemetry exposed to the relay planner

### ""After you act for me, verify the world changed the way you intended, not merely that your command completed, and tell me if the result is still uncertain.""
- **useful because:** A successful Mac or browser command is not proof that an email was accepted, a reservation changed, a form persisted, or a calendar edit survived. The browser can inspect the resulting page, the Mac can reread local state, and the relay can compare the observation with the intended effect. The owner gets outcome truth instead of execution optimism.
- **path:** mac → browser → relay → pendant
- **model tier:** Deterministic postcondition checks first; background model only when the result requires semantic comparison between the intended change and observed UI/state. Realtime speaks a short qualified result.
- **latency:** For reversible local actions, verify within 5 seconds; for external sites, poll up to a policy-defined deadline and then report unresolved rather than claiming success.
- **cost:** $0.005–$0.05 per action depending on whether a browser reread or semantic comparison is needed.
- **security:** Verification must use read-only follow-up operations and redact private page contents from receipts and speech. Never retry a mutation merely because verification is inconclusive; require explicit confirmation for a second attempt. Preserve before/after evidence hashes and the exact observation time.
- **missing:** Typed postcondition declarations for Mac and browser actions; A read-only verifier that can bind an observation to the original action and session; A distinction between command accepted, external effect observed, and effect contradicted; A durable outcome receipt linked to the action idempotency key; Policy for external sites whose state is eventually consistent or hides confirmation


## Changes it proposed to its own stack

### `relay` — Add lease_until, lease_owner heartbeat, and a bounded requeue sweep to relay_jobs, following the working routine lease pattern. On expiry, mark the attempt abandoned, preserve its receipt, and requeue only if the job's idempotency key has not produced a terminal effect.
- **owner gets:** A Mac sleep, USB disconnect, or process crash should not make a requested job vanish in 'processing' for 24 hours. The owner gets eventual completion or an explicit recoverable failure instead of having to ask again.
- effort: Medium: schema migration, D1 and memory-store parity, bridge heartbeat, and tests for crash/requeue/idempotency.  ·  risk: A late worker could race a requeued job; fence tokens and action idempotency must make stale completion harmless. Recovery is to inspect the receipt and cancel the requeued attempt.
- cost: Negligible API cost; one small periodic D1 query and heartbeat writes per active job.  ·  latency: No change on healthy jobs; recovery begins after a configurable lease, e.g. 2 minutes.
- security: Lease tokens must be opaque and scoped to the job; do not expose worker credentials in owner-facing receipts.
- depends on: Persist relay-job-id to Mac-job-id mapping; Use the existing actionIdFor idempotency key at the relay boundary

### `memory` — Wire the Mac bridge's post-job fact/event emission to the existing shared fleetMemory writer, add the missing relay_memory_events migration to the deployed schema, and emit retraction events when a source is revoked or a capture is forgotten.
- **owner gets:** Preferences and decisions learned on the Mac would finally be available to the pendant and relay, while forgetting a source would stop stale copies from silently shaping future answers. This is felt as continuity and privacy, not a refactor.
- effort: Medium: bridge event mapping, schema migration, sensitivity-safe projection tests, and source-retraction fan-out.  ·  risk: Over-sharing or accidental raw-quote persistence; enforce the existing byte limits, sensitivity classifier, source IDs, and never send secret values in fleet projections. Roll back by disabling the writer while retaining local events.
- cost: Low: bounded D1 writes (up to 1 KiB/event) and projection reads; no model cost.  ·  latency: Adds tens of milliseconds to post-job synchronization, off the owner's conversational critical path.
- security: Cross-node propagation increases disclosure surface; default to opaque normalized claims, allowlist surfaces, and emit explicit retractions rather than destructive disappearance.
- depends on: Add capsuleId/source link to derived facts; Implement the owner's disclosure policy as a value, not a hardcoded trust list


## What it asked for

_Nothing._
