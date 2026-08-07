# Harness derivation — relay-realtime — round 78

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this to my Mac planner: open my project and prepare the next steps, then tell me what you’re doing as it progresses."
- **useful because:** The owner can speak once and get a coordinated, observable workflow from a wearable: intent routing, planning on the Mac, execution, and status updates without guessing whether something is queued, stranded, or completed.
- **path:** pendant → relay → mac-bridge → mac-planner → browser
- **model tier:** Realtime model at relay only for intent capture and brief updates; cheaper planner/executor model on Mac for multi-step work; browser only if needed for web context.
- **latency:** Under a second to acknowledge and route; planning/execution can take longer but must stream status updates to the relay.
- **cost:** Low per invocation at relay; dominant cost is downstream planning/execution and any browser session work.
- **security:** Intent and minimal context leave the pendant. No blocking gates, but status must be truthful and receipts recorded. Sensitive data should be minimized in the relay payload.
- **missing:** relay_route_intent implementation (currently schema only); Durable job runner for routed intents and status streaming; Unified job/status mapping so the relay can report progress without inventing a protocol

### "“While I was away, tell me exactly what you did for me, what actually changed, and what still needs attention.”"
- **useful because:** Today the owner can inspect individual jobs, receipts, browser results, or history, but cannot get one trustworthy, spoken, cross-surface account tying the original voice request to Mac actions, browser commands, partial failures, and final state. This matters specifically because the pendant is worn away from the Mac and the browser extension can strand work while offline.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to classify the question and speak a concise answer; have a cheaper background summarizer build the evidence-backed timeline from receipts and results, then cache it for instant follow-up questions.
- **latency:** Initial answer under 2 seconds from cached event records; if aggregation is needed, speak “I’m checking the evidence” immediately and return within 5 seconds. Follow-up questions should be sub-second from the cached timeline.
- **cost:** Roughly $0.001–$0.01 per completed request depending on event count; the dominant cost is background summarization, not the short realtime response. Most queries should be zero additional model cost when the timeline is precomputed on each job completion.
- **security:** The answer may include sensitive browser page titles, URLs, or Mac file/app details, so retain the existing session scoping and redact secrets from spoken summaries. Do not claim success from a plan or queued command: each statement needs an observed receipt/result, with explicit labels for planned, queued, stranded, failed, and completed. Undo links should point to existing receipts rather than inventing reversal behavior.
- **missing:** A durable correlation id propagated from the initial voice run through /plan, /execute, Mac receipts, browser command ids, and final results; A relay-side event ledger that merges Mac and browser events in timestamp order and persists compact evidence references; A background summarizer and cached per-request timeline API; A spoken-result formatter that enforces observed-vs-inferred language and distinguishes the browser extension’s offline queue from completed work


## Changes it proposed to its own stack

### `relay` — Implement relay_route_intent as the explicit, schema-backed routing entry point for voice intents. It should accept intent label, utterance, and optional context, forward to mac-planner or mac-vision, and emit a job id that the relay can track without inventing a protocol.
- **owner gets:** Voice commands become predictable and observable. The owner gets immediate acknowledgment and reliable progress updates, even if the Mac sleeps or the browser extension is offline.
- effort: Medium: schema exists; needs implementation and wiring to planner/vision endpoints plus job bookkeeping.  ·  risk: Misrouting or duplicate routing could trigger unintended actions. Mitigate with idempotency keys and receipts; rely on existing undo receipts for reversals.
- cost: Small relay compute cost per intent; downstream compute dominates.  ·  latency: Improves by avoiding ad-hoc inference and multi-hop ambiguity.
- security: Centralizes intent logging; must minimize sensitive utterance content and protect logs. No new permissions beyond routing endpoints.

### `integration` — Add a durable job runner with status streaming across surfaces. The relay assigns a job id; Mac planner/executor and browser harness report state transitions and receipts. Relay can answer 'what’s happening' truthfully without polling the Mac live.
- **owner gets:** The owner hears accurate, timely updates and can safely walk away. Queued vs stranded vs completed becomes clear, especially when the browser extension is offline.
- effort: High: requires durable storage, eventing, and consistent job lifecycle across relay, Mac, and browser harness.  ·  risk: Partial failures could leave jobs orphaned; mitigate with timeouts, retries, and reconcilers that can safely mark jobs unknown/failed.
- cost: Moderate: durable storage and event traffic; still cheaper than repeatedly invoking the realtime tier.  ·  latency: Better perceived latency due to streaming updates; avoids round trips for status checks.
- security: Job metadata becomes sensitive; must enforce access control and retention limits.
- depends on: relay_route_intent implementation; job/receipt schema alignment across surfaces

### `integration` — Add an end-to-end voice-quality contract for every live session: the pendant advertises its actual capture codec/rate, the relay records input and TTS output telemetry separately, computes a simple quality verdict (capture, uplink, transcription, or playback), and exposes a compact diagnostic object that the realtime agent can explain aloud. Add adaptive fallback rules that lower output bitrate or switch to a shorter acknowledgement when LTE-M uplink quality degrades, without pretending that 15.625 kHz input is 24 kHz end-to-end.
- **owner gets:** When a command is misunderstood or a reply cuts out, the owner can ask “was that my connection or did you misunderstand me?” and receive a truthful answer plus a shorter, more reliable response. This reduces repeated commands and makes the worn device dependable away from the Mac.
- effort: Medium: define telemetry schema, persist one compact record per voice run, add relay-side quality classification and TTS fallback, and add a small pendant firmware capability advertisement. No new model is required for the classification.  ·  risk: Incorrect diagnosis could blame LTE for a recognition error or vice versa. Recover by reporting the raw measured dimensions and an unknown verdict when evidence is insufficient; retain the current fixed audio path as the fallback. Avoid changing codec mid-utterance.
- cost: Negligible storage and Worker CPU; occasional telemetry fields add a few hundred bytes per run. Adaptive TTS may reduce audio egress rather than increase API cost.  ·  latency: No added conversational latency for the normal path; verdict calculation is local and asynchronous. A degraded-link acknowledgement can be generated immediately before the full response.
- security: Telemetry must exclude transcript content and network identifiers beyond coarse quality metrics; only the owner’s session may read it. Do not persist raw audio merely to diagnose quality.
- depends on: A versioned pendant audio-capability handshake; A relay voice-run telemetry schema distinguishing input sample rate from output sample rate; A small read-only voice-quality endpoint or state projection for the realtime agent


## What it asked for

_Nothing._
## Its own summary

Recorded two new items. (1) Evidence-backed cross-surface “what happened while I was away?”: a causal timeline joining the voice request, Mac receipts, browser command/results, queue state, and observed final outcomes, with planned/queued/stranded/failed/completed labels and spoken follow-ups. (2) An end-to-end voice-quality contract that reports actual input/output telemetry separately, diagnoses capture vs uplink vs transcription vs playback, and adapts acknowledgements/TTS under LTE-M degradation. Both require new correlation/telemetry infrastructure rather than assuming today’s routes are sufficient.

**Biggest unknown:** Whether the existing backlog already contains a narrowly equivalent cross-surface causal timeline or audio-quality contract under a different title; I was instructed not to discover further this round, so the proposal records the missing behavior and concrete dependencies rather than re-checking.

