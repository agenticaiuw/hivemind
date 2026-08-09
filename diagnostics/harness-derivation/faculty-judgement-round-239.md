# Harness derivation — faculty-judgement — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m listening to a briefing, let me say ‘challenge that’ (or press the pendant) and tell me whether the claim survives a fresh check, with the source and any contradiction saved in my notes.”"
- **useful because:** Research briefs currently ask the owner to trust a narrated conclusion. A low-friction challenge path turns passive audio into accountable judgement: pause the exact item, re-check the cited page and independent sources, speak a short verdict, and preserve the evidence so the owner can revisit it.
- **path:** pendant → relay → browser → mac
- **model tier:** Use the realtime model only to bind the interruption to the current spoken item and produce the short spoken reply; use the cheaper background model for source comparison and note drafting. Browser reads the authenticated source when needed, relay coordinates, and Mac writes the reviewable note.
- **latency:** Acknowledge/pause under 300 ms; spoken “checking” under 1 s; first verdict within 15 s, with a durable note when research completes. If browser is offline, say so and do not imply verification.
- **cost:** About $0.01–$0.05 per challenge depending on number of source pages; browser reads and background comparison dominate, not the short realtime turn.
- **security:** Never send the owner’s spoken challenge or private note text to an untrusted research origin. Reuse existing redaction and provenance; authenticated pages stay in the browser surface. Saving a note is reversible but should carry citations, timestamp, and a clear ‘not verified’ state when sources disagree.
- **missing:** Bind the audio item’s citation/source IDs to a research job and persist the comparison result.; A compact contradiction/verdict schema and a note writer that includes provenance rather than only prose.; A spoken interruption route that invokes background research instead of treating every barge-in as a new conversation.

### "“Tell me what I actually heard today—not what was generated—and let me replay only the brief items that never finished playing.”"
- **useful because:** Scheduled audio can be generated, queued, downloaded, started, interrupted, or finished, and those are different facts. The owner needs a truthful missed-brief answer that deduplicates overlapping routines and offers targeted replay instead of another full briefing.
- **path:** relay → pendant → mac → browser
- **model tier:** Use deterministic receipt reconciliation and attention arbitration for the normal path; use the cheaper background model only to summarize the missed item set. Realtime is reserved for the owner’s short spoken query and replay confirmation.
- **latency:** Answer from persisted delivery events in under 2 s; enqueue a selected replay within 1 s. If ACKs are stale or absent, explicitly say ‘delivery unknown’ rather than ‘you missed it’.
- **cost:** Usually under $0.01 per query; the expensive part is occasional summary generation, while reconciliation and deduplication are deterministic.
- **security:** Delivery records contain opaque artifact IDs and timing, not transcript content. Keep source-sensitive text behind the existing provenance policy; replay must honor the current attention decision and never bypass a stop latch or an unexpired owner policy.
- **missing:** A durable join from routine/job/briefing item to artifact ID and delivery events.; A query that computes generated/downloaded/started/finished/interrupted/unknown states and coalesces duplicate routine outputs.; A replay planner that creates a new artifact only for genuinely unfinished items and carries the prior item’s evidence links.

### "“If the pendant audio cuts out, recover the conversation for me automatically: tell me exactly what was lost, offer a short replay, and give me the UART evidence if it keeps happening.”"
- **useful because:** A dropped link or decoder underrun currently turns a live answer into an ambiguous silence. The owner should get a bounded recovery—not a repeated full response—and a useful diagnosis when the fault is real.
- **path:** pendant → relay → mac
- **model tier:** Use deterministic playback/download ACKs and audio metrics to detect the gap and select the missing segment. Use the realtime model only for the immediate one-sentence recovery offer; use a cheaper background model to compress a long lost segment and correlate repeated faults.
- **latency:** Detect interruption from the pendant event immediately; offer recovery within 500 ms of link restoration; replay a 5–12 second digest within 3 s. Never block a new owner utterance while recovery is pending.
- **cost:** A few cents only when regeneration or summarization is needed; most interruptions use cached audio and no model call.
- **security:** The recovery artifact must inherit the original item’s sensitivity and source policy. Do not persist raw microphone audio beyond the existing failure-path rule. Diagnostics drafts remain local/reviewable and are never filed automatically.
- **missing:** A semantic gap map from playback position to transcript/audio segment, not just an artifact-level interrupted flag.; Idempotent recovery-artifact generation and a replay queue that respects the universal stop latch.; A policy for when repeated interruptions create a local diagnostics draft instead of repeatedly bothering the owner.

### "“When I undo or reject something you did, learn the rule I was protecting and stop making that class of mistake again—show me the rule before it affects a future action.”"
- **useful because:** Today an undo is an isolated repair. The owner must repeatedly catch the same category of error across the Mac, browser, and pendant. Turning a confirmed correction into a reviewable, expiring guardrail makes the system improve from the owner’s judgement without silently training on an ambiguous refusal.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic receipt/undo evidence to identify the candidate action and enforce an existing policy rule. Use the realtime model only to ask one concise clarification when the correction is ambiguous; use a cheaper background model to draft the generalized rule and test it against recent action history.
- **latency:** After an undo, offer a candidate rule in under 2 s; future preflight checks add under 100 ms. Never block the owner’s next unrelated action while rule drafting is pending.
- **cost:** Usually below $0.01 per correction; background generalization and historical testing dominate occasional calls.
- **security:** A correction must not become a broad surveillance-derived preference. Store the exact evidence, scope, expiry, confidence, and owner confirmation; default to draft-only and fail closed for destructive/external actions. Never infer a rule from a failed tool call alone.
- **missing:** A durable owner-confirmed guardrail record with scope, expiry, evidence references, and versioning.; A way to distinguish explicit rejection/undo from technical failure and to present the candidate rule before activation.; A cross-surface hook that feeds the confirmed rule into autonomy_policy_evaluate and explains which guardrail matched.


## What it asked for

_Nothing._
## Its own summary

Produced three owner-facing capabilities: challenge a narrated research claim with fresh evidence and a cited note; a truthful “what did I actually hear?” view using pendant delivery ACKs (the recorder flagged this as close to an existing idea, so it should be treated as one consolidated capability, not two); and bounded recovery after interrupted audio with a short replay plus local diagnostics evidence. Two were accepted cleanly; the delivery-ledger idea was recorded but marked close to prior backlog and should not be restated.

**Biggest unknown:** The remaining work is implementation, not another owner permission: bind briefing items to artifact IDs and evidence, persist routine/job-to-device delivery joins, map playback positions to recoverable transcript/audio segments, and verify which existing provenance route can carry the challenge result. I do not need to ask again for interruption or disclosure preferences; ship conservative, traceable defaults and expose those policy fields for later owner choice.

