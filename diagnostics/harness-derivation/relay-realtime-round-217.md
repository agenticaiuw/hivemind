# Harness derivation — relay-realtime — round 217

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me what’s going on right now with my devices and connection, and whether you can actually act on my Mac from here."
- **useful because:** The owner needs confidence in the system state: is the Mac reachable, is the pendant online, are we paired, and what actions are possible. This avoids false expectations and speeds troubleshooting in the field.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Realtime relay for the spoken status; no need for a heavyweight model.
- **latency:** Under 1–2 seconds for a spoken summary; detailed diagnostics can be offered as a follow-up.
- **cost:** Low. A couple of status reads; keep payload small and cache the last known state to avoid repeated calls.
- **security:** Status should avoid leaking sensitive identifiers (e.g., full device IDs). If multiple devices exist, avoid exposing unrelated device details.
- **missing:** A unified status endpoint on the relay that merges Mac agent status, pendant status, bridge status, and job queue health.; A stable pairing record the relay can read without probing private routes piecemeal.; A small cache in the relay for last-known device state and last error.

### "Watch this task or workflow and interrupt me only if something needs my attention, like a confirmation, an error, or a missing login."
- **useful because:** This turns the system into a smart assistant instead of a chatbox. The owner can start a multi-step workflow, then focus on other things while the system handles the boring parts and only calls out when human input is required.
- **path:** relay → mac-bridge → browser
- **model tier:** Mac planner or delegated agent for workflow execution; relay only for attention-worthy interrupts.
- **latency:** Workflow can run for minutes; interrupts should be near-real-time when a blocking condition occurs.
- **cost:** Moderate. Cost is dominated by delegated workflow steps and browser actions; interrupts are small and infrequent.
- **security:** Never auto-confirm high-impact actions. If a login or destructive action is needed, ask explicitly. Avoid speaking sensitive data aloud; summarize instead.
- **missing:** A standing watch for workflow state changes, not just completion (needs_attention).; A delivery path for attention events to the pendant or phone that works when the session has ended.; A way to represent ‘needs attention’ across mac actions, browser actions, and job receipts.

### "Summarize what you remember that’s relevant to this task, including preferences and recent context, without me repeating myself."
- **useful because:** This reduces friction and prevents the assistant from asking redundant questions. The owner gets a tight recap that respects memory scope and avoids irrelevant web artifacts.
- **path:** relay → mac-bridge → memory
- **model tier:** Cheaper background model for memory projection; relay for the spoken summary.
- **latency:** 1–3 seconds for a short summary; longer details only on request.
- **cost:** Low to moderate. Most cost is memory projection and filtering; keep summaries short and cache task-scoped context.
- **security:** Never expose sensitive memory unless explicitly requested. Respect memory scoping to avoid leaking browser-derived facts into unrelated conversations.
- **missing:** Wiring the existing memory projection into the live conversation context path so the relay can use it cheaply.; A small ‘context summary’ tool that returns a short spoken block sized for the pendant.; A budget mechanism to cap tokens per turn and report what was dropped.

### "When I say “find the thing I was looking at,” have the pendant search my open Mac apps and authenticated browser tabs together, identify the same item across them, and read me the answer plus where it came from."
- **useful because:** Today the owner must remember whether information was in Safari, Outlook, VS Code, or a local file. This would make the worn device a unified index over the contexts the other nodes can individually reach, while preserving provenance instead of hallucinating a merged answer.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use relay-realtime only for intent extraction and a one-sentence spoken answer; use mac-planner for local app/file search and browser-extension for authenticated tabs; use faculty-perception/judgement to reconcile evidence and a cheaper background model for ranking.
- **latency:** Acknowledge in under 500 ms; return an initial result in 5–10 s, with a follow-up prompt if the two surfaces disagree.
- **cost:** Roughly $0.02–$0.10 per lookup depending on whether browser and Mac evidence both need model interpretation; most cost is evidence extraction, not speech.
- **security:** Search results can contain private mail, documents, and authenticated pages. Keep raw evidence on the Mac/extension where possible, send only selected snippets and URLs to the relay, redact secrets, and make destructive follow-up actions separately explicit.
- **missing:** A real cross-surface search orchestration endpoint that can fan out to Mac and browser in one job; A provenance/evidence schema that survives planning and returns ranked snippets; A relay response path that can speak a result while retaining the selected artifact for follow-up

### "If I say “stop” or “pause that” while my Mac or browser is carrying out a multi-step task, stop at the next safe boundary, tell me exactly what already happened, and let me resume from that checkpoint later."
- **useful because:** A spoken front door currently hands work away, but the owner cannot reliably interrupt an unattended workflow from the pendant. This prevents a mistaken long-running action from continuing and turns a fragile handoff into a controllable transaction.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Relay-realtime handles the short stop/pause intent; a deterministic job controller owns cancellation and checkpoints; use the slower planner only to describe the checkpoint or construct a resume plan.
- **latency:** Play an immediate local acknowledgement within 300 ms; issue cancellation within 1 s; report the checkpoint within 3 s.
- **cost:** <$0.01 for most interrupts; the dominant cost is engineering a cancellation/checkpoint protocol, not inference.
- **security:** Cancellation must be idempotent and must not claim rollback. Each completed action needs a receipt, and any partially applied external mutation must be clearly reported. Resume tokens must be scoped to the owner and expire.
- **missing:** Cooperative cancellation and safe-boundary checkpoints in Mac/browser jobs; A durable per-action receipt plus explicit partial-state model; A real pendant-to-active-job interrupt route, rather than only polling completed jobs

### "Fill out this authenticated web form using what you already know about me, ask me only for missing or ambiguous fields through the pendant, and stop before the final submit unless I explicitly say submit."
- **useful because:** Forms are where the wearable’s memory, the browser’s authenticated session, and the relay’s conversation are uniquely complementary. The owner can complete tedious applications while away from the Mac without having the system silently invent or disclose values.
- **path:** pendant → relay → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheaper planner for DOM field mapping and memory matching; relay-realtime asks concise clarification questions and speaks the pending-field summary; deterministic action code performs filling and leaves submit as a separate action.
- **latency:** Start in 2 s, map and fill ordinary forms in 10–30 s, and ask one bundled clarification question rather than interrupting once per field.
- **cost:** About $0.03–$0.15 per form; DOM inspection and field matching dominate, with little realtime-model usage.
- **security:** Treat every field as sensitive until classified. Never transmit raw memory wholesale: resolve values locally, show the owner the field names and masked values, log every fill, and require an explicit spoken submit command for irreversible external effects.
- **missing:** A browser form-inspection and fill primitive with stable field identifiers; A field-level memory projection that can distinguish permitted autofill from ambiguous values; A pending clarification state that survives a dropped voice session and returns through the existing alert inbox


## What it asked for

_Nothing._
