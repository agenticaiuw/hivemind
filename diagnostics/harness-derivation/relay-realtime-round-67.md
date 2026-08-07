# Harness derivation — relay-realtime — round 67

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m back at my Mac—what changed since I left, and put me back where I was?”"
- **useful because:** The pendant is usually worn away from the Mac, so the owner loses the thread between physical contexts. A return-to-work delta would compare a departure checkpoint with the current Mac and authenticated browser state, explain only meaningful changes, and restore the exact working context instead of making the owner reconstruct it.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to capture the spoken request and deliver a short answer; use a cheaper background model or deterministic diffing for checkpoint comparison. mac-planner restores reversible app/window/document state, while browser-extension reads and restores the authenticated tab/session context.
- **latency:** A spoken acknowledgment within 1 second, then a concise delta within 5 seconds when Mac and browser are online. Restoration can report progress asynchronously through the pendant.
- **cost:** Roughly $0.01–$0.05 per return, dominated by one background model call over compact checkpoint diffs; deterministic state collection and storage are negligible.
- **security:** Checkpoints may contain document titles, URLs, and snippets from authenticated pages. Keep raw snapshots encrypted and retain only a bounded redacted summary; never send page contents to the relay-realtime model unless needed. Restoring tabs/apps is reversible and should be automatic under the owner's stated policy, with an undo receipt.
- **missing:** A departure/return checkpoint store with redaction and retention rules; Mac instrumentation that emits a stable working-context fingerprint and can restore it; Browser-extension API for authenticated-tab fingerprints and reversible restoration; Cross-surface diffing and an asynchronous pendant status/receipt path

### "“I’m leaving now—watch this job until it finishes, recover safely if it stalls, and tell me only if I need to intervene.”"
- **useful because:** The owner is physically away from the Mac much of the time. Today a voice request can start work, but nothing reliably watches a long-running Mac/browser task after the conversation ends, detects a stall, performs bounded recovery, and escalates only a genuine human decision. This turns the pendant into a useful remote presence rather than a one-shot command button.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a durable Worker/Durable Object monitor and deterministic heartbeats/state checks for normal operation. Use a cheaper background model only to classify ambiguous failure evidence; use relay-realtime for the initial request and urgent spoken escalation.
- **latency:** Start acknowledgement under 1 second. Heartbeats every 15–30 seconds without model calls; detect a stall within one heartbeat window. Speak only on completion, bounded recovery, or a real intervention request.
- **cost:** Approximately $0.01–$0.05 per watched job, dominated by occasional failure classification; normal heartbeats are Worker/storage operations. Cost scales with watch duration and should have an explicit expiry.
- **security:** The monitor must be scoped to the exact job and allowed recovery actions, never broaden a goal after a failure. Browser sessions and Mac files remain private to their surfaces; send the relay only status summaries and evidence links. Record every recovery and provide an undo/stop command from the pendant.
- **missing:** A durable watch/heartbeat and expiry facility on the relay (Cron/Durable Object alarm or equivalent); Typed progress and failure signals from Mac planner, Mac vision, and browser extension; A bounded recovery policy with retry budgets and stop/undo semantics; Pendant push delivery for completion and escalation after the original voice turn


## Changes it proposed to its own stack

### `model-routing` — Add a first-class relay intent router that all surfaces use: a typed envelope (intent label, utterance, target, constraints, trace id) that routes to mac-planner or browser harness, and stores a relay job record immediately. Provide a status hook for relay_job_status to read, and receipts for downstream actions.
- **owner gets:** The owner gets reliable, consistent behavior: saying “open my simulator project” or “check that page” always routes the same way, can be resumed later, and can be explained back as a coherent job.
- effort: Medium. Requires schema definition, storage of job records in the relay, and updates to mac-planner/browser harness to accept the envelope. It also needs UI/logging for traceability.  ·  risk: Routing bugs could send a task to the wrong surface. Mitigate with strict schema validation, intent audit logs, and safe fallbacks (ask a clarifying question or delegate to mac-planner).
- cost: Small per request for envelope creation and job record storage. Most cost remains downstream.  ·  latency: Minimal added latency (tens of milliseconds) for envelope validation and record creation.
- security: Improves security by making data flow explicit; risk is centralized metadata. Protect with access controls and redaction.
- depends on: A stable tool interface for relay_route_intent or equivalent; A relay job record store with receipts


## What it asked for

### `c13-2kde` (context) — granted tools that cannot be described
- why: The granted list includes relay_route_intent and server_browser_actions, but describe(name) reports they do not exist. I need to know whether they are available under a different name, provided implicitly, or still pending wiring.
- would change: If they are available, I will use them to route intents and run server-side browser actions without inventing a protocol. If they are not, I will request them explicitly and avoid assuming they work.

