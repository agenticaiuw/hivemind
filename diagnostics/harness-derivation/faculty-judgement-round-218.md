# Harness derivation — faculty-judgement — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make my scheduled briefs count as done only when I actually hear them, and catch me up on anything I missed.”"
- **useful because:** Today a routine can report completed after generation even if audio was never downloaded or played. This closes the gap between the system doing work and the owner receiving it, especially across LTE loss, a sleeping Mac, or an interrupted pendant.
- **path:** relay → pendant → mac-planner
- **model tier:** Use the normal/background model to reconcile routine output and delivery receipts; reserve realtime only for the owner’s catch-up request.
- **latency:** No added latency to routine generation. Delivery reconciliation runs within 30 seconds of an ACK or reconnect; catch-up response under 2 seconds from stored receipts.
- **cost:** Low: one small background decision per routine run; dominant cost is existing briefing/audio generation, not reconciliation.
- **security:** Persist only opaque artifact IDs, routine IDs, and short summaries; never infer that an item was heard from download alone. A missed item may be replayed only through the existing owner-triggered alert path. Require confirmation before changing or disabling a routine.
- **missing:** A durable routine-outcome record joining routine ID, relay job ID, artifact ID, and pendant playback state; A scheduler reconciliation step that distinguishes generated, downloaded, started, finished, and interrupted; A compact catch-up projection that deduplicates items already finished and expires stale items

### "“When I ask for the news again, give me only what changed since the last news answer, in three short sentences, and tell me when sources disagree.”"
- **useful because:** The owner repeatedly asks for the same world/US headlines. A change-only, source-disagreement-aware answer prevents recycled headlines, makes freshness explicit, and fits the owner’s one-short-sentence spoken preference while preserving a detailed cited version for later review.
- **path:** browser-extension → relay → pendant → mac-planner
- **model tier:** Background research model gathers and clusters sources; a cheap deterministic diff removes previously delivered claims; realtime only compresses the final three sentences when the owner is actively listening.
- **latency:** Under 20 seconds for a fresh request when browser access is online; if sources are unavailable, say so immediately rather than fabricate continuity.
- **cost:** Moderate: web retrieval and clustering dominate; incremental requests can reuse source fingerprints and avoid resending full prior articles.
- **security:** Use public sources by default and keep URLs, timestamps, and claim fingerprints rather than article bodies in the long-lived state. Never present a single source as consensus; disclose paywalls or inaccessible sources. No posting or account actions.
- **missing:** A durable per-topic spoken-claim ledger with source URLs, publication times, claim fingerprints, and last-delivered timestamp; A source freshness and disagreement evaluator that returns evidence, not just a prose summary; A change-only news route that can distinguish genuinely new claims from rewritten copies

### "“What actually happened today?”"
- **useful because:** The system currently stores actions, notes, browser findings, reminders, and spoken interactions in separate places, so the owner cannot get a trustworthy chronological account of their day. A source-linked timeline would distinguish observed events from inferred summaries and expose gaps instead of inventing continuity.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** A cheap background projector builds the timeline from receipts and typed events; realtime only answers the owner’s focused question or reads a short digest.
- **latency:** Update incrementally after each completed job or capture; answer a day query in under 3 seconds from the projection, with an explicit slower-refresh option.
- **cost:** Low-to-moderate: projection is local/deterministic; model cost is only for compressing a selected time window. Storage is bounded metadata, not raw audio.
- **security:** Every line must carry a source and confidence marker. Keep private/secret content out of spoken summaries by default and offer screen-only detail. Do not treat action telemetry as a human event without labeling it; allow deletion to propagate to all derived timeline entries.
- **missing:** A single normalized event projection joining job receipts, browser provenance, voice-note metadata, captures, reminders, and pendant delivery events; A real retention and deletion cascade for derived timeline rows; A query route that returns chronological events with source IDs, confidence, sensitivity, and explicit unknown gaps

### "“Don’t interrupt me while I’m talking or thinking aloud; wait for a natural pause, then tell me only what still matters.”"
- **useful because:** A quiet-hour rule cannot distinguish a silent focused owner from someone actively speaking, and calendar urgency cannot tell whether an interruption would break a thought. A signed, low-latency turn-taking contract would make the pendant feel socially usable: defer ordinary events during speech, preserve hard deadlines, and deliver a compact digest at the next safe pause.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime firmware/relay logic detects speech and turn boundaries; a cheaper background model ranks and compresses deferred events. The expensive model is not called for every audio frame.
- **latency:** Local speech-state transitions under 100 ms; urgent events may preempt only under the owner’s explicit policy. Deferred digest becomes available within 1 second of a stable pause.
- **cost:** Low model cost; the dominant work is a small on-device VAD/turn-state machine and relay event arbitration. No continuous transcript needs to leave the pendant.
- **security:** Transmit only signed states and timing (speaking, pause, confidence, sequence), never raw audio or inferred words. Fail closed on uncertain state by deferring nonurgent notifications. Emergency override and what qualifies as emergency must remain owner-configurable and auditable.
- **missing:** A pendant-local voice-activity and pause detector with hysteresis that survives link loss; A signed turn-state event protocol with monotonic sequence numbers and expiry; An attention policy extension that treats natural pauses as delivery windows and records why an event was deferred or released; A bounded deferred-event digest that coalesces duplicates without silently dropping deadlines


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: delivery truth for scheduled audio (done means actually heard, with catch-up), change-only source-disagreement-aware news, and a source-linked “what happened today?” timeline. I discovered the owner repeatedly asks for short world/US news, has multiple overlapping 07:00/07:30 briefs, and prefers one short spoken sentence. I do not need another permission or tool grant to specify these; implementation needs durable joins/projections and deletion/retention semantics listed in each proposal.

**Biggest unknown:** The owner’s explicit policy for what may be spoken aloud and what counts as an urgent interruption remains intentionally unset. Until they choose it, all three should default to conservative, non-sensitive spoken summaries and owner-triggered detail.

