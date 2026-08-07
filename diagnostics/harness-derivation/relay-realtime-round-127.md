# Harness derivation — relay-realtime — round 127

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I get cut off mid-request, keep going and pick up exactly where we left off when I reconnect."
- **useful because:** On a wearable, interruptions are normal. The owner shouldn’t lose progress because LTE drops, audio glitches, or they had to stop talking.
- **path:** pendant → relay → mac-bridge → browser → relay
- **model tier:** Realtime only for initial recognition and clarification; a cheaper planner model continues the task off the critical audio path.
- **latency:** Under 300ms to acknowledge and save progress; continuation can take seconds to minutes depending on the task.
- **cost:** Low per interruption for saving a compact state; most cost is downstream planning and browser/Mac actions, not the relay.
- **security:** Store only task-relevant text and references, not raw audio. Encrypt state at rest. Make it clear to the owner what was saved and let them discard it.
- **missing:** A persistent, typed task-state envelope shared across surfaces; An implementation for relay_route_intent schema or equivalent routing; A durable job runner with resumable steps; A relay capability inventory endpoint for observability

### "“When you do something on my behalf, give me a trustworthy, voice-readable proof of exactly what each surface saw, changed, or sent— and let me ask ‘why?’ or ‘show me the source’ without rerunning it.”"
- **useful because:** Today the owner can receive completion receipts, but cannot reliably distinguish an agent’s observation from an action, inspect the exact evidence used, or audit data leaving the Mac/browser. A compact provenance record would make delegation safe to trust while the owner is away from the Mac, and would let the pendant answer follow-up questions from durable evidence rather than guessing or repeating side effects.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only to answer the owner’s short audit question and summarize precomputed records. Have a cheaper background model normalize long page diffs and Mac observations into structured provenance; do not spend realtime tokens replaying work.
- **latency:** Initial voice answer under 1 second from cached provenance; deeper ‘why/show source’ lookup under 3 seconds. Recording metadata adds negligible action latency; screenshot/page evidence capture may add up to 1–2 seconds per step.
- **cost:** Roughly $0.001–$0.02 per delegated task for compact structured logging and optional background summarization; storage and evidence retention dominate, not inference. Realtime audit replies cost only a short turn.
- **security:** Evidence can contain private page text, screenshots, files, and secrets. Store encrypted, redact credentials/tokens before persistence, retain hashes plus minimal excerpts by default, and require an explicit owner request to reveal sensitive evidence. Every record needs surface, timestamp, operation, input/output hashes, and whether data crossed the device boundary. Never claim a source was inspected when only a model summary exists.
- **missing:** A shared provenance/event schema with one delegation id and per-step causal links across relay, Mac, and browser; Mac and browser adapters that emit read/action/data-egress events and content hashes, not only final receipts; Encrypted evidence storage with redaction, retention limits, and a voice-query endpoint; A dashboard and pendant response format for cited excerpts, source URLs/file paths, and uncertainty; Correlation of existing /plan, /execute, /jobs/:jobId/receipts, /browser/inspections, and browser-session records into one immutable timeline

### "“While I’m away from my Mac, quietly tap my pendant when a delegated task needs my attention or finishes; let me press once to hear the short result and use distinct patterns for success, question, failure, and connection loss.”"
- **useful because:** A voice-only system is easy to miss when the owner is walking, working, or has no earbuds in. The current pendant has one button and one LED but no dependable tactile attention channel, so Mac/browser work can finish without the owner noticing. A discreet, glance-free signal would make delegation practical in daily life rather than requiring repeated spoken status checks.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No realtime inference for the signal itself. Emit typed events from Mac/browser to the relay; use a cheap background classifier only to choose a short urgency class. Relay-realtime speaks the result only after the owner presses the button or asks.
- **latency:** Completion-to-tap under 2 seconds while the relay and pendant are connected; button-to-spoken-summary under 1 second. Queue the event if LTE is briefly unavailable and deliver it on reconnect.
- **cost:** About $4–$12 incremental hardware (coin vibration motor, driver, mounting, and optional haptic isolation), plus under $0.001 per event in relay traffic. Battery impact should be under 1–2% per day with short pulses; firmware and enclosure testing dominate effort.
- **security:** Patterns must reveal no private task content to nearby people. Do not vibrate for sensitive data unless configured; use generic urgency labels. Authenticate and deduplicate event delivery so an old completion cannot trigger a misleading tap. A button press should disclose details only over the authenticated voice session.
- **missing:** A haptic actuator and driver in the pendant (the current one-button/one-LED device cannot provide tactile states); A durable authenticated relay-to-pendant event channel with sequence numbers, acknowledgement, deduplication, and reconnect delivery; A compact firmware event queue and button interaction state machine that fits the existing RAM/flash budget; Mac and browser adapters that publish typed lifecycle events (needs-attention, completed, failed, disconnected) instead of only final logs; Owner-configurable urgency/pattern preferences and a dashboard test button


## Changes it proposed to its own stack

### `integration` — Build a resumable, cross-surface job envelope: a durable record of the goal, last completed step, next step, and evidence/receipts, so Mac/browser work can continue after relay disconnects and be summarized later.
- **owner gets:** They can start something by voice, lose connection, and still get a trustworthy, step-by-step result when they reconnect—without repeating themselves.
- effort: Medium to large. Needs a durable store (D1/DO), step idempotency, and receipt linking across Mac and browser harnesses.  ·  risk: Medium. Resuming incorrectly could duplicate actions; mitigate with idempotency keys, typed receipts, and explicit irreversible checkpoints.
- cost: Moderate. Storage and receipt linking add some cost; the big cost remains downstream action execution.  ·  latency: Slight overhead to write checkpoints; improved reliability overall.
- security: Requires careful scoping and encryption of stored state; store minimal sensitive data.
- depends on: Durable job runner or equivalent persistence; Implementations for relay_route_intent and server_browser_actions or alternative routing/execution paths


## What it asked for

_Nothing._
## Its own summary

Recorded two new capabilities: (1) proof-carrying, source-linked provenance across relay/Mac/browser actions, with redaction and voice audit; (2) discreet haptic pendant notifications for delegated-task completion/attention, requiring a tactile actuator, authenticated event delivery, and firmware queueing. Both extend beyond existing receipts/status and do not assume today’s wiring is sufficient.

**Biggest unknown:** The pendant’s exact mechanical, power, and spare-memory budget for adding a haptic actuator, plus the still-unimplemented relay-to-pendant event channel and cross-surface provenance emitter schema.

