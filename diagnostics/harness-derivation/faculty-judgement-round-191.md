# Harness derivation — faculty-judgement — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you speak this briefing, tell me whether it contains private material and route each item to the safest output. I can change that rule later.”"
- **useful because:** The current briefing redaction is only one path; pendantSpeech and audioBrief can speak arbitrary text, and there is no bystander or recipient policy. This capability would make the pendant safe to wear in public without silently inventing the owner's preferences.
- **path:** relay → mac → pendant
- **model tier:** Realtime for the spoken one-sentence status; deterministic policy evaluation for every item, with a cheaper background classifier only when sensitivity is unknown.
- **latency:** Less than 250 ms added at an utterance boundary; never delay emergency stop or playback cancellation.
- **cost:** Near-zero for deterministic rules; <$0.005 for occasional ambiguous classification.
- **security:** Ship conservative defaults as editable policy fields, not hardcoded consent: secret never spoken, sensitive queued unless explicitly allowed, normal allowed only to the selected surface. Include the matched rule and provenance in the receipt. Fail closed on missing sensitivity or policy; do not expose raw content in logs.
- **missing:** a unified output gate around pendantSpeech and audioBrief; owner-editable destination/data-class policy persistence; bystander/public-presence signal (currently only idle/presence exists); policy enforcement on pipeline audio creation

### "“What did I actually hear, what did I miss, and play only the items I never finished.”"
- **useful because:** Generated jobs and server receipts do not prove pendant download or playback. With delivery ACKs now available, the owner can get a truthful catch-up instead of repeated or silently lost briefings, including after an offline period.
- **path:** relay → pendant → mac
- **model tier:** Deterministic reconciliation and ranking; realtime only to summarize the final short list or handle a replay request.
- **latency:** Under 2 seconds for status and under 5 seconds to enqueue a replay; tolerate offline pendant by presenting a queued state.
- **cost:** <$0.002 per query; no model needed unless the owner asks for a natural-language summary.
- **security:** Join only opaque artifact IDs and authenticated device sessions; do not infer that downloaded means heard. Deduplicate by eventId and device sequence, distinguish interrupted from finished, expire stale audio, and require confirmation before replaying sensitive content aloud.
- **missing:** a durable owner-facing delivery projection over POST /pipeline/events; integration with catch-up ranking so played items are suppressed and interrupted items retained; replay enqueue semantics tied to artifact provenance; offline ACK upload status in the relay UI

### "“Trace my last request end to end: what I said, which plan ran, what the Mac/browser changed, what the relay accepted, and whether the pendant actually played it.”"
- **useful because:** The system currently has five unrelated ID namespaces and only a telemetry blob joins relay and Mac. Receipts prove isolated steps, while playback ACKs prove isolated device events. An owner-facing causal timeline would make failures and duplicate work understandable instead of forcing guesswork.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic event join and phase classification; use the realtime model only to compress the verified timeline into the owner's requested one sentence.
- **latency:** Under 2 seconds for a recent request; up to 10 seconds when assembling a long-running job across surfaces.
- **cost:** <$0.003 per query; most work is indexed receipt/event retrieval, not inference.
- **security:** Show only owner-authenticated jobs and redact secrets from spoken output. Preserve raw evidence locally with short retention; expose hashes, timestamps, statuses, and provenance links by default. Never infer success from a server acceptance or download; each phase must be explicitly observed or marked unknown.
- **missing:** a durable correlation key linking relay job IDs, Mac jobs, browser commands, action IDs, and artifact IDs; an append-only cross-surface event index with phase schemas; join of record_pendant_delivery_event to pipeline/job receipts; owner-facing route that renders the causal chain and unknown gaps

### "“What are you assuming about me right now? Show me the assumptions that could change what you do, let me correct one, and use the correction everywhere from now on.”"
- **useful because:** The owner currently has facts, graph entities, inherited memory text, browser findings, and relay state that can disagree, while no surface can show the active assumptions as a single editable set. A correction that reaches only one store is worse than no correction: the system will appear to comply and later repeat the same mistake.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic projection and conflict detection for the assumption list; realtime model only translates the selected correction into a short confirmation and asks for clarification when the owner's wording is genuinely ambiguous.
- **latency:** Under 2 seconds to show the active assumptions and under 5 seconds to apply a correction across reachable surfaces; if a surface is offline, mark it pending rather than claiming global application.
- **cost:** <$0.005 per invocation; storage and propagation dominate, with model usage limited to ambiguous natural-language corrections.
- **security:** Display provenance, confidence, sensitivity, age, and affected decisions for every assumption. Treat corrections as owner-authored but do not silently erase source evidence; create a superseding/retraction event. Secret values must never be spoken in the confirmation. Fail closed when propagation is incomplete and expose exactly which surfaces still hold the old value.
- **missing:** a read projection of active assumptions spanning facts, context graph, inherited fleet text, and relay memory; a single owner-authored correction/retraction event with idempotent fan-out; production writers for shared fleet memory; conflict-aware prompt projection that records which assumption version was used; a durable cross-surface propagation receipt


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: a source-wide erasure receipt (the recorder identified it as already present, so it must not be re-proposed); a conservative, policy-driven spoken-output gate; truthful heard/missed briefing catch-up from pendant playback ACKs; and an end-to-end causal request timeline. The two new proposals were recorded, while the erasure idea collided with an existing backlog item and should be treated as already claimed rather than rephrased.

**Biggest unknown:** The next implementation decision is not model quality: it is which missing connective primitive gets built first. The strongest candidates are (1) a real output gate around every pendantSpeech/audioBrief path, or (2) a durable cross-surface correlation/event index. Both need owner-visible policy/retention choices, and the owner has not yet set those values.

