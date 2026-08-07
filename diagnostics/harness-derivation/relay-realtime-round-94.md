# Harness derivation — relay-realtime — round 94

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this to the right place and keep going after I stop talking. Tell me what happened when it’s done."
- **useful because:** This is the everyday experience: the owner speaks once, the system picks the right surface, and the pendant later delivers a crisp status update without needing the Mac to stay awake.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for intent capture only; planning and execution on cheaper downstream models.
- **latency:** Under a second to acknowledge and queue; minutes or longer for completion depending on the task.
- **cost:** Low per intent for the relay ledger; downstream planning/execution and any browser automation dominate cost.
- **security:** Utterances and extracted data may be sensitive. Store only what is needed, encrypt in transit, and keep a minimal, redacted job record. Provide clear status messages; do not fabricate completion.
- **missing:** relay_route_intent implementation; durable relay intent ledger and status endpoint; downstream completion callback to relay; optional pendant notification path for async completion

### "“Carry this task from my pendant to my Mac: keep the conversation, open the exact browser pages and draft state, and let me continue without explaining everything again.”"
- **useful because:** Today a spoken task and a later desktop session are disconnected. This would let the owner start while away, then resume at the Mac with the relevant browser tabs, cited findings, pending decisions, and draft text reconstructed instead of repeating the request.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime handles the short spoken capture and explicit handoff phrase; a cheaper background model compacts the transcript and evidence into a task capsule; mac-planner restores the capsule into browser tabs and a resumable plan when the Mac is available.
- **latency:** Acknowledge the handoff on the pendant within 1 second; capsule creation may take 2–5 seconds; desktop restoration should begin within 10 seconds of the Mac coming online.
- **cost:** About $0.01–$0.05 per handoff, dominated by background transcript/evidence compaction; restoring tabs and passing structured state adds negligible model cost.
- **security:** Capsules may contain private speech, authenticated URLs, and draft data. Store encrypted, expire by default, bind the capsule to the owner's device/session, and visibly report which tabs and text will be restored. Opening pages is reversible, but sending or submitting anything must remain an explicit action.
- **missing:** A durable cross-surface task-capsule store with versioned transcript, evidence citations, browser session/tab identifiers, pending actions, and expiry; A pendant button/voice handoff event that seals a capsule and later signals that it is ready to resume; Browser support for exporting/restoring authenticated tab state without copying page secrets into the model prompt; Mac-planner support for capsule discovery, conflict detection against changed tabs, and resumable execution; A user-facing handoff/resume status and receipts view

### "“If the Mac or browser agent gets stuck, ask me the one small question you need on my pendant, then continue automatically when I answer.”"
- **useful because:** Long-running desktop work currently either guesses through ambiguity or leaves a job incomplete. The owner should be able to resolve a missing choice while away from the Mac, without restarting the task or repeating its context.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Mac-planner/browser agents detect a typed ambiguity and produce a short question plus 2–4 choices; relay-realtime delivers and collects the spoken answer; a background state machine validates the answer and resumes the existing job. Use realtime only for the brief question/answer exchange.
- **latency:** Question delivery under 2 seconds after an agent reports ambiguity; answer acknowledgement under 1 second; resume within 5 seconds after the answer reaches the worker.
- **cost:** Roughly $0.005–$0.03 per interruption, mostly one short realtime turn and optional answer normalization; no full-task reprompt should be needed.
- **security:** The question must not leak more page content than necessary. Include job and choice identifiers, redact secrets, expire unanswered questions, reject answers for stale job versions, and record the answer and resulting receipt. Do not silently interpret a free-form answer when it could select a destructive operation.
- **missing:** A first-class blocked-on-owner job state with a correlation id, safe checkpoint, question payload, expiry, and resume transition; A relay push path from Mac/browser jobs to the pendant and an answer endpoint that preserves the original voice session; Planner/browser adapters that can pause at an ambiguity and resume from a deterministic checkpoint rather than replanning from scratch; Compact spoken-choice rendering and robust transcription of choice numbers/short phrases; Dashboard visibility for waiting questions, stale questions, and the eventual receipt


## Changes it proposed to its own stack

### `relay` — Add a relay-side intent routing endpoint and durable intent ledger that the realtime agent can call instead of ad-hoc tool calls. It would accept a small intent label, utterance, and optional normalized context, then forward to the chosen downstream surface (mac-planner by default) and return a job id. The relay also exposes a status endpoint for that job and a completion callback that can deliver a spoken summary to the pendant even after the conversation ends.
- **owner gets:** They can say something once, walk away, and later hear exactly what happened, without the relay inventing a protocol or depending on the Mac being awake at that moment.
- effort: Medium to high. Requires defining a stable intent schema, implementing the relay router, and wiring a callback path from downstream agents back to the relay.  ·  risk: Misrouting or duplicate execution if idempotency is not handled. Mitigate with idempotency keys, strict intent validation, and a durable job ledger. Provide an undo path where possible.
- cost: Adds relay storage reads/writes (D1) per intent plus small compute. Downstream work dominates cost. Voice delivery is a small additional cost.  ·  latency: Fast initial response (queue + job id). Completion happens async and does not block the pendant.
- security: Intent payloads contain potentially sensitive utterances. Must authenticate, encrypt in transit, and minimize stored context; redact where possible.
- depends on: A working relay_route_intent implementation (currently schema-only); A durable job runner or at least a durable ledger for intent state; A completion callback route on the relay that downstream agents can call


## What it asked for

_Nothing._
## Its own summary

I discovered the current categories, tools, surfaces, hardware, and backlog, and verified that relay_route_intent is still schema-only. I proposed a relay-side intent router + durable ledger and a cross-surface capability for async completion updates, so the owner can speak once, walk away, and later hear exactly what happened.

**Biggest unknown:** Whether the relay already has any hidden routing/status endpoints for intent jobs (outside the Mac agent routes), and whether a durable job runner exists for relay-originated work.

