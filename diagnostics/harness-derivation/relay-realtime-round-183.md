# Harness derivation — relay-realtime — round 183

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Summarize what you’re doing right now and why, and let me interrupt for a shorter version.”"
- **useful because:** This makes the system feel trustworthy and controllable in the moment. The owner gets a quick, spoken plan with a clear escape hatch to avoid long monologues.
- **path:** relay-realtime → mac-planner → faculty-judgement → faculty-action
- **model tier:** Realtime for narration; downstream tiers execute and report.
- **latency:** Under a second to start the summary; follow-up details only if requested.
- **cost:** Low; short status pull plus a brief spoken response. Dominant cost is any status fetch from Mac.
- **security:** Status may include filenames or sensitive context; summarize at a high level unless asked to drill down.
- **missing:** A consistent, low-cost status snapshot format across Mac and relay that’s designed for speech.; A small policy for what to include by default vs only on request.

### "“Notice when my browser session is about to go stale and keep my place for later.”"
- **useful because:** When the Mac/browser link drops or the owner walks away, work-in-progress context is often lost. Preserving the working set reduces rework and frustration.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception
- **model tier:** Cheaper background model to detect staleness and serialize state; realtime only to confirm.
- **latency:** A quick confirmation; background work can take a few seconds.
- **cost:** Moderate; depends on tab inspection and session serialization. Dominant cost is browser state capture.
- **security:** Captured tabs and content are sensitive; store only what’s needed (URLs, titles, minimal form state) and encrypt at rest.
- **missing:** A robust browser session snapshot schema and restore path.; A staleness signal (heartbeats, last-activity timestamps) and a place to store snapshots.

### "“Why are you telling me this, and show me the source and the last time it changed.”"
- **useful because:** The owner currently receives a conclusion but cannot interrogate its provenance from the pendant. This capability would make spoken automation trustworthy: relay gathers a source chain from the Mac app, authenticated browser page, and its own transformations, then answers which source caused the claim, when it was observed, and what uncertainty or disagreement exists. It is especially valuable when the owner is away from the screen.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short spoken explanation; a cheaper structured provenance service records hashes, timestamps, selectors, and transformations, while a small judge model summarizes conflicts only when asked.
- **latency:** First sentence under 1 second from cached receipt; a live source refresh may take 3–8 seconds.
- **cost:** Usually under $0.01 using stored structured metadata; $0.03–$0.10 when refreshing multiple sources or summarizing a conflict.
- **security:** Source content can include private mail or authenticated pages. Store minimal excerpts and cryptographic fingerprints by default, redact secrets, and let the owner request full content explicitly. A source must never be represented as checked if it was stale or unavailable.
- **missing:** A provenance envelope attached to every observation and action receipt; Common source identifiers for Mac apps, browser DOM/session observations, and relay-generated transformations; A pendant voice intent for provenance questions and a compact spoken formatter

### "“Change the plan I already gave you: keep what is done, replace the remaining steps with this new constraint.”"
- **useful because:** Long computer tasks are brittle today: once delegated, the owner must wait, start over, or issue a competing command. A live plan-edit capability lets the worn front door revise an in-flight Mac/browser workflow while preserving completed work, showing the exact remaining steps and avoiding duplicate mutations. This is useful when the owner remembers a constraint after walking away from the screen.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime extracts the constraint delta and acknowledges it; a background planner performs a dependency-aware splice against the current action graph; the Mac/browser tiers execute the revised suffix and emit receipts.
- **latency:** Acknowledge the edit under 700 ms; produce a revised plan in 2 seconds; execution proceeds asynchronously with a spoken update when the next checkpoint is reached.
- **cost:** $0.02–$0.08 per edit, dominated by replanning and optional visual verification; no cost for idle jobs beyond storage.
- **security:** A stale edit could race with an action already executing. Require versioned plans, atomic cancellation at action boundaries, idempotency keys, and a spoken summary of what cannot be changed because it already ran. Keep private page contents local to the Mac/browser executor where possible.
- **missing:** Versioned mutable action graphs rather than immutable queued plans; Cancel/pause/resume and patch endpoints with action-boundary semantics; A planner diff format and relay session binding so “the plan” is unambiguous

### "“Before you change anything, rehearse the whole operation and tell me what I would see, what data it would touch, and how long it should take.”"
- **useful because:** The current system plans and executes, but the owner cannot get a faithful, cross-surface preview of a multi-step operation. A rehearsal would run read-only discovery against the actual Mac state and authenticated browser session, resolve selectors and dependencies, estimate duration, and return a spoken consequence map without performing mutations. It is not a permission gate; it is a way to avoid surprises and to debug workflows while away from the screen.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime summarizes the preview; a cheaper planner compiles a read-only shadow plan, while Mac vision/browser adapters inspect the live UI and mark uncertain steps.
- **latency:** Speak an immediate acknowledgement under 500 ms; return a short preview in 3–10 seconds, with longer inspections continuing as a job.
- **cost:** $0.02–$0.12 per preview, dominated by browser/Mac inspection and screenshots; substantially cheaper than executing then repairing.
- **security:** Even read-only inspection can expose authenticated content. Redact values and transmit only labels, domains, app names, selectors, and hashes unless the owner asks for detail. The executor must enforce a no-mutation rehearsal mode, including no clipboard writes, downloads, navigation submissions, or filesystem changes.
- **missing:** A true dry-run contract understood by every action type; Shadow-state inspection and side-effect detection for Mac and browser actions; A consequence-map schema and spoken renderer for affected apps, files, accounts, and estimated duration

### "“Make these changes across my Mac and browser as one operation: either all of them succeed, or leave everything exactly as it was.”"
- **useful because:** A single spoken request can currently partially succeed across heterogeneous surfaces, leaving a calendar, file, or web form inconsistent with the others. A cross-node transaction coordinator would prepare each mutation, verify preconditions, commit in a defined order, and compensate or restore snapshots when a later participant fails. That is a genuinely hive-level capability: neither the pendant, relay, Mac, nor browser can provide it alone.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime captures scope and speaks transaction state; a background coordinator handles prepare/commit/compensation; Mac and browser agents provide deterministic adapters and receipts.
- **latency:** Immediate acceptance under 500 ms; prepare phase 2–8 seconds; spoken result after commit or compensation, with durable status if a participant is unreachable.
- **cost:** $0.03–$0.15 per transaction, dominated by planning, state snapshots, and visual verification; storage is proportional to changed files/forms.
- **security:** True atomicity is impossible for some external services. Label guarantees honestly per participant, refuse to claim rollback where no compensating operation exists, encrypt snapshots, expire them quickly, and never submit irreversible external actions under an all-or-nothing claim.
- **missing:** A transaction coordinator with prepare/commit/abort phases and participant leases; Action adapters that declare preconditions, idempotency, inverse or compensation, and atomicity level; Cross-surface snapshot/receipt storage and a spoken failure explanation


## Changes it proposed to its own stack

### `integration` — Create a cross-surface “handoff ledger” for in-progress tasks: when the relay accepts a command, it emits a durable, minimal record (task id, origin, target, last known state, next expected callback). Mac/browser agents update it as they act; the relay reads it to answer “what’s happening?” without rehydrating full context.
- **owner gets:** The owner gets consistent status from any surface: on-pendant voice, Mac, or future phone. It reduces confusing mismatches like “it’s running” in one place and “unknown” in another.
- effort: Medium to high. Needs a small storage layer and agreements on state transitions.  ·  risk: Medium. State divergence is possible; mitigate with versioned updates and receipts.
- cost: Low per update; dominant cost is downstream work. Ledger writes are tiny.  ·  latency: Improves perceived responsiveness by avoiding expensive recomputation.
- security: Store minimal metadata; avoid payloads like document text. Use per-owner isolation.
- depends on: Durable storage (Durable Object, KV, or similar) for the ledger; Agreed task state model across relay, Mac, and browser agents


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: provenance interrogation for every spoken claim, live editing of an in-flight Mac/browser plan, and cross-surface prepare/commit/compensation transactions. The first undo proposal collided with an existing backlog item and was intentionally not restated. These capabilities require new connective semantics—provenance envelopes, versioned mutable plans, and transaction participants—even though they build on existing routes.

**Biggest unknown:** The exact existing receipt and action schemas are not fully inventoried from this relay surface, so implementation would first need to identify which actions can honestly declare snapshots, inverses, compensation, or provenance without overstating guarantees.

