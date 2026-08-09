# Harness derivation — faculty-judgement — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the pendant audio link starts degrading, detect it and quietly switch to the best profile before I hear dropouts; tell me only if it could not recover."
- **useful because:** The owner gets reliable speech instead of silently missing words. It uses measured device telemetry and actual playback acknowledgements, so it reacts to the experience rather than trusting that an artifact was generated.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Background rules/cheap model for anomaly classification; realtime model only for a one-sentence owner explanation after repeated recovery failure.
- **latency:** Telemetry evaluation under 2 seconds; profile change at the next safe audio-item boundary, with no conversational interruption.
- **cost:** Near-zero model cost for normal operation; occasional cheap classification call, dominated by no model call when deterministic thresholds match.
- **security:** Only opaque artifact IDs and audio metrics leave the device; no transcript or raw PCM. Profile changes are reversible and should be logged with evidence and require no owner confirmation.
- **missing:** A typed cross-surface audio health controller that can request a profile change and verify it against pendant_delivery ACKs; A device/bridge command for applying a profile at an item boundary; A dashboard history of metric-triggered changes

### "After each scheduled briefing, tell me whether it was actually downloaded and played on the pendant, not merely generated; if it failed, give me one concise recovery choice."
- **useful because:** Today a routine can be marked completed while the owner never hears it. This closes the loop from schedule to artifact to physical delivery and makes the system honest about whether it reached the person.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Deterministic receipt join and attention policy; cheap model only to phrase an exception, never to infer delivery without ACK evidence.
- **latency:** Join delivery events within 30 seconds of reconnect; speak only on the next appropriate attention window, or immediately for an owner-marked urgent briefing.
- **cost:** No model cost for success; a few hundred tokens only for rare failure wording. Storage is tiny event metadata, not audio.
- **security:** Expose artifact IDs, timestamps, byte counts, and playback state—not briefing text—to the dashboard by default. Recovery actions (requeue, shorten, or mark heard) are reversible and should use autonomy_policy_evaluate.
- **missing:** A durable join from routine/pipeline IDs to artifact IDs and briefing item IDs; A reconnect reconciliation job that deduplicates offline pendant ACKs and marks routine delivery truth; A recovery action that can requeue only the missing artifact without duplicating a successfully played item

### "When I press the pendant because I didn't understand the last thing you said, replay only that item's key claim in plainer language and show me the source on my Mac; don't restart the whole brief."
- **useful because:** A wearable conversation fails at the moment a sentence is missed, and today recovery either repeats too much or loses the source. This binds a physical request to the exact spoken item, produces a smaller repair, and leaves an inspectable citation on the Mac.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Realtime model for the short comprehension repair; deterministic item binding, provenance lookup, and delivery receipt handling around it.
- **latency:** Stop current playback immediately; begin the repair within 1.5 seconds and keep it under one spoken sentence unless the owner asks for detail.
- **cost:** One small realtime generation per repair, typically under 200 output tokens; no Mac/browser model call unless source rendering needs extraction.
- **security:** The repair must inherit the item's sensitivity and provenance policy; never speak withheld source text. Opening a source tab is read-only and should be bounded to the cited URL. A physical press is the trigger, not inferred speech approval.
- **missing:** A distinct local event for 'explain simpler' versus next/previous on the existing playback-interrupt path; A relay operation that generates a repair from the current item's evidence without losing the cursor; A Mac route that opens the cited source in a read-only, sensitivity-aware view and records the repair receipt

### "What did you decide not to interrupt me about today? Show me the suppressed items, why each was held, when it expires, and let me release one item without changing my global quiet policy."
- **useful because:** A quiet assistant can fail invisibly: the owner cannot tell whether nothing happened or the system deliberately deferred something. This gives an auditable, content-minimized suppression inbox and lets the owner correct one decision without accidentally changing every future interruption.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Deterministic suppression receipts and policy explanations; cheap model only to summarize a selected item after the owner explicitly asks.
- **latency:** List in under 2 seconds; releasing one item should enqueue it for the next safe attention window, or speak immediately only when the owner explicitly requests that.
- **cost:** No model cost for listing or policy reasons; one short generation for an owner-selected summary. Small durable metadata log.
- **security:** Default list contains source class, urgency, policy rule, deadline, and sensitivity—not private subject/body text. Releasing inherits the item's sensitivity and attention policy. The action must be reversible and scoped to one receipt.
- **missing:** A durable suppression receipt store fed by attention_arbitrate decisions; A read-only route that exposes matched policy rules and expiry without leaking content; A scoped release operation with idempotency and provenance, distinct from changing the global policy


## Changes it proposed to its own stack

### `integration` — Implement a durable briefing delivery ledger keyed by routine ID, pipeline ID, artifact ID, and item ID. Ingest authenticated pendant ACKs idempotently, reconcile on reconnect, and expose a single owner-facing state machine: generated, queued, downloaded, playback_started, playback_finished, interrupted, or failed. Do not mark a routine's delivery complete at generation time.
- **owner gets:** The owner can trust “you heard it” and receive one recovery choice instead of duplicate or missing briefings.
- effort: Medium: schema/migration, relay join logic, Mac/pendant reconnect reconciliation, and a small status route.  ·  risk: Duplicate or out-of-order ACKs could create false state; require event-id dedupe, monotonic sequence checks, and retain raw evidence for explanation. Recover by recomputing state from the event log.
- cost: Negligible metadata storage and no routine model cost.  ·  latency: ACK reconciliation within one reconnect cycle; no added audio startup latency.
- security: Store opaque IDs and delivery metadata by default; keep briefing text behind existing provenance access.
- depends on: record_pendant_delivery_event; POST /pipeline/events; a durable relay store/migration; a routine-to-pipeline/artifact join

### `interaction` — Add a signed playback-item control envelope carrying item_id, cursor_token, evidence_refs, sensitivity, and available controls. A pendant interrupt can request only one of explain_simpler, repeat_key_claim, next, or defer; relay validates the token, generates at most one bounded repair, and Mac opens only the cited read-only source. Record the owner's physical control and the resulting repair as one receipt.
- **owner gets:** When speech is unclear, one press repairs the exact sentence instead of restarting a long briefing or forcing the owner to remember what to ask for.
- effort: Medium-high: firmware event vocabulary, relay token validation, item-aware generation, and a read-only Mac citation view.  ·  risk: A stale token could expose the wrong item; expire tokens at item boundary and fail closed to a generic “I can’t identify that sentence.” Never treat a voice transcript as approval.
- cost: One short realtime generation only when requested; otherwise no model cost.  ·  latency: Target under 1.5 seconds after the physical interrupt; source opening can happen asynchronously.
- security: Inherited sensitivity and provenance must gate both audio and Mac display; no raw source text in the pendant envelope.
- depends on: audio_brief_item_action; record_pendant_delivery_event; explain_action_provenance; a distinct physical interrupt/control event; read-only cited-source Mac route

### `model-routing` — Create a closed-loop audio health controller that combines UART diagnostics, pipeline metrics, and authenticated pendant delivery ACKs. It should classify degradation deterministically, choose among already-verified profiles at an item boundary, verify the next packet/playback outcome, and roll back after a failed transition. Escalate to the realtime model only to explain a persistent failure.
- **owner gets:** The pendant should recover from dropouts itself instead of making the owner repeat a question or wonder whether the system heard them.
- effort: Medium: metric normalizer, profile transition command, verification window, and receipt-linked audit record.  ·  risk: Oscillation or a bad profile could worsen audio; add hysteresis, cooldown, bounded retries, and a known-good fallback. Never alter microphone capture policy silently.
- cost: No routine model cost; occasional short explanation generation only after recovery fails.  ·  latency: Profile changes wait for an utterance boundary; detection under two seconds.
- security: Only opaque IDs and numeric metrics cross surfaces. Diagnostics drafts remain local and reviewable, never auto-filed.
- depends on: pendant_diagnostics_and_bug_draft; record_pendant_delivery_event; POST /pipeline/audio; a typed profile-apply/verify operation; durable pipeline event storage


## What it asked for

_Nothing._
## Its own summary

Round 152 produced three new owner-facing directions: self-healing audio before dropouts, truthful scheduled-brief delivery based on physical playback rather than generation, and one-press comprehension repair bound to the exact spoken item and its cited source. I also translated each into concrete integration changes; the recorder flagged the delivery concept as adjacent to an existing idea, so the genuinely new boundary is the authenticated physical playback truth and item-level recovery, not another generic briefing queue.

**Biggest unknown:** I still need the authoritative durable join and storage shape for routine run → pipeline → artifact → briefing item, plus the exact firmware event vocabulary and transport available over today's USB serial link. Without those, delivery truth and comprehension repair can be designed but not safely implemented. I also need confirmation whether /v1/routines is live before treating it as an established route.

