# Harness derivation — relay-realtime — round 30

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Did you hear that, and is it playing or still working?"
- **useful because:** This is the everyday friction point: the owner needs a confident, honest answer about audio capture and playback, plus whether a requested task is queued, running, or done—without guessing or polling multiple systems.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for immediate spoken receipts; mac-planner/browser for long-running work summaries.
- **latency:** Under 200ms for 'heard/playing/queued' receipts; longer status details can arrive later.
- **cost:** Very low for receipts (tiny events); status lookups cost dominated by downstream job status retrieval when needed.
- **security:** Receipts can leak sensitive intent. Only store and speak minimal state; avoid raw transcripts; never claim completion unless it’s confirmed by the authoritative source.
- **missing:** Unified interaction-receipts stream with correlation ids; Durable short-lived event storage and a read/push interface; Policy for what is spoken immediately vs queued to avoid interrupting the owner

### "While you are carrying out a long task on my Mac or in my signed-in browser, let me say “pause”, “stop”, or “what’s happening?” into the pendant and get an immediate, truthful spoken status; if I stop talking, automatically pause or expire the task safely."
- **useful because:** The owner is usually away from the Mac and cannot reach its screen. Today a queued action can continue without a wearable control surface, leaving the owner unable to halt a mistaken navigation or understand whether anything happened. A pendant-controlled execution lease makes remote automation interruptible and understandable rather than fire-and-forget.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short voice command and intent classification; mac-planner/browser-extension perform pause, cancel, checkpoint, and status operations; a cheaper background model can summarize the checkpoint for speech; dashboard stores the event timeline for later inspection.
- **latency:** Acknowledge pause/stop within 500 ms at relay, deliver the control to the active executor within 2 s, and speak a compact status within 3 s. Lease expiry should be enforced server-side even if the Mac becomes unreachable.
- **cost:** About $0.005–$0.03 per control interaction depending on whether a background summary model is needed; most cost is optional status summarization, not routing. Durable execution leases/checkpoints add modest Worker/Durable Object storage and Mac implementation work.
- **security:** Control commands and status metadata leave the pendant for the relay and may include app names or browser URLs. Stop must be honored without confirmation; pause/cancel should be authenticated to the paired pendant. The executor must checkpoint before destructive transitions, redact secrets from spoken status, and make lease expiry fail closed.
- **missing:** A durable per-task execution lease with owner/pendant authentication and expiry; A common pause/cancel/status control protocol implemented by relay, mac-planner, mac-vision, and browser-extension; Checkpoint and resumable-state support in Mac and browser executors; A low-latency relay route for controls plus truthful spoken receipts; Dashboard timeline showing control, checkpoint, and final disposition

### "When I ask the pendant “where did I see that?” or “what did we decide about this?”, search my own recent Mac actions, browser pages, voice conversations, and task receipts, then answer with the source and a direct way to reopen it."
- **useful because:** Today the wearable can start work but cannot recall the owner’s fragmented recent activity across the signed-in browser, Mac, and voice history. This would turn the hive into an episodic memory that works while the owner is away from the computer, without relying on generic web search or requiring them to remember which surface held the information.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheaper background indexing model extracts entities, timestamps, decisions, and source links as events arrive; realtime only resolves the spoken query and reads a concise result. Exact source retrieval should be deterministic rather than generated.
- **latency:** Capture/index asynchronously in under 2 seconds per event; answer a voice recall query in under 4 seconds, with a first spoken result as soon as one high-confidence match is found.
- **cost:** Roughly $0.01–$0.05 per indexed conversation/task batch and under $0.01 per lookup; storage/indexing dominates recurring cost, while realtime speech remains the expensive portion of interaction.
- **security:** This contains highly sensitive personal and authenticated-browser activity. Keep raw page content and transcripts encrypted, store only local/source-scoped embeddings and minimal excerpts by default, never send secrets to a model unnecessarily, and require explicit spoken confirmation before opening or exposing a sensitive source on another surface.
- **missing:** A consented event-capture stream from relay voice runs, Mac planner receipts, and browser-extension page/activity events; An encrypted owner-scoped episodic index with retention and deletion controls; Cross-source retrieval that returns provenance, timestamps, confidence, and reopenable deep links; A relay query route and response format for concise spoken answers; Dashboard controls to inspect, correct, export, or erase remembered events

### "Let me say “undo the last thing you did” to the pendant and have the hive identify the specific recent Mac/browser action, explain the planned reversal briefly, and apply a compensating action wherever it is safely reversible."
- **useful because:** Remote automation is valuable only if mistakes are recoverable while the owner is away from the Mac. Current receipts can describe completion, but they do not provide a cross-surface, voice-addressable undo that understands whether the last action was a browser edit, file move, calendar change, or message draft.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime resolves “last thing” and speaks the concise plan; deterministic action receipts and per-surface compensators select the reversal; a cheaper background model can map unfamiliar action descriptions to candidate compensators, never inventing a reversal without a recorded inverse.
- **latency:** Identify the target and speak it within 1.5 seconds; execute a known inverse within 5 seconds; if no inverse exists, say so immediately and offer the exact source/action receipt instead.
- **cost:** About $0.01–$0.04 per undo, dominated by optional inverse-plan generation. Receipt indexing and inverse metadata add small persistent storage costs; browser/Mac compensator implementation is the main engineering cost.
- **security:** An incorrect undo can itself cause data loss or duplicate side effects. Every action needs an immutable receipt, explicit reversibility classification, idempotent inverse, and a short spoken target announcement; irreversible actions must be reported as non-undoable rather than approximated. Receipts may contain private URLs, filenames, and message metadata and require encryption and retention controls.
- **missing:** A cross-surface action receipt schema with stable operation IDs and recorded inverse/compensation metadata; Idempotent undo handlers for Mac files/apps and authenticated browser operations; Relay resolution of temporal references such as “last thing” across concurrent jobs; Checkpointing and conflict detection so an undo cannot overwrite newer owner edits; A pendant spoken receipt and dashboard audit trail for every undo attempt and outcome


## Changes it proposed to its own stack

### `integration` — Add a relay-side 'interaction receipts' stream that spans audio and actions: (1) emit and persist events for capture start/stop, ASR segment accepted, TTS playback start/complete, and action delivery accepted/started/completed; (2) expose them as a lightweight read endpoint and as a push to a Durable Object or message bus; (3) include correlation ids linking a spoken utterance to downstream jobs and back. Use it to drive a short spoken receipt to the owner ("playing now", "queued", "failed") and to let other agents reason about continuity without re-polling multiple systems.
- **owner gets:** They get truthful, consistent feedback about what’s happening right now. No more "did it hear me?" or "did that run?" ambiguity—especially when the Mac is asleep, the browser is offline, or audio is congested.
- effort: Medium. Requires defining event schema, wiring emit points in relay audio and action routing, and a small persistence layer (Durable Object or D1).  ·  risk: If event ordering is wrong, receipts could lie. Mitigate with monotonic sequence numbers per session, correlation ids, and explicit 'unknown' states. If persistence fails, fall back to best-effort delivery acceptance only.
- cost: Low per event. Storage/egress dominated by retention policy; keep short TTL and compact payloads.  ·  latency: Minimal. Events are small; do not block audio on persistence—fire and buffer with backpressure.
- security: Events may include sensitive utterance metadata. Store minimal content (ids, timestamps, status), hash or omit raw text, and enforce tenant isolation.
- depends on: Durable Object or equivalent persistence for short-lived session events; A defined correlation-id convention across relay, mac jobs, and browser commands


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: pendant-controlled execution leases with pause/stop/status and safe expiry; cross-surface episodic recall over voice, Mac, browser, and receipts; and voice-addressable compensating undo for reversible Mac/browser actions. Each requires new relay protocols plus downstream executor/index support, rather than assuming current wiring exists.

**Biggest unknown:** Whether existing action-receipt or job-status work already includes a stable inverse-operation schema; the proposals deliberately specify that missing foundation instead of assuming it.

