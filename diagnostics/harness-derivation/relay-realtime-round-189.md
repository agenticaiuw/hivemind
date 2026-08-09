# Harness derivation — relay-realtime — round 189

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with the thing I asked earlier?"
- **useful because:** The owner can get a quick status without waking the Mac or re-running anything, reducing confusion and repeated work.
- **path:** relay-realtime
- **model tier:** realtime
- **latency:** Under one second for typical cases; it’s a local relay read.
- **cost:** Very low; a single relay job-status read.
- **security:** Status text must be spoken verbatim when it indicates failure/unknown to avoid misreporting outcomes.
- **missing:** None if relay_job_status is fully implemented and accessible via tool routing

### "If I lose connection, keep my memo and send it later."
- **useful because:** The owner doesn’t have to repeat themselves when connectivity drops; it preserves intent and reduces frustration.
- **path:** pendant → relay-realtime → faculty-action
- **model tier:** realtime only for confirming receipt when connectivity returns
- **latency:** Immediate local capture; forwarding later can be opportunistic.
- **cost:** Low; storage and retry are bounded by short memos.
- **security:** Voice memos are sensitive; encryption at rest on-device and authenticated upload are important.
- **missing:** A consistent manifest-backed queue across all payload types so memos, bookmarks, and alerts reuse one mechanism rather than duplicating

### "“Put this browser task on a bookmark: save the exact page and form state I’m looking at, and later restore it or tell me precisely what changed.”"
- **useful because:** Today a spoken request can trigger an action, but the owner cannot preserve a private, authenticated browser moment as a durable, recoverable object. This would turn a fleeting Safari state into a named handoff: useful for half-filled forms, research trails, and purchases paused from the pendant while away from the Mac.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use the realtime model only to capture the owner’s label and disambiguate; use a cheaper background model to summarize DOM/state and compute semantic differences. The browser extension records the state; mac-planner restores it.
- **latency:** Acknowledge the bookmark in under 2 seconds; capture in under 10 seconds. Restoration may take 30–90 seconds and can be asynchronous.
- **cost:** Roughly $0.01–$0.08 per capture/restore, dominated by DOM/state summarization and any screenshot OCR; no model call is needed for simple state serialization.
- **security:** State may contain authenticated pages, tokens, typed PII, and screenshots. Keep raw state on the Mac/browser profile, encrypt the relay metadata, never send cookies or passwords to the model, and make the pendant announcement generic (for example, “browser bookmark saved”). Restoration must report fields that no longer match rather than silently submitting.
- **missing:** A durable browser-state bookmark record with encrypted, owner-scoped storage; Browser-extension capture of form values, scroll/selection state, and stable semantic locators without exporting cookies; A restore-and-diff operation that can pause on changed or destructive steps; Relay-to-pendant completion delivery for captures made after the voice session

### "“Read the private page I’m on, but keep its raw contents on my Mac; send only the minimum redacted facts needed to answer me.”"
- **useful because:** The owner currently has to choose between cloud conversational convenience and exposing authenticated work/personal pages to the relay. A local browser extractor can answer questions about sensitive pages while the pendant remains the natural interface, without uploading the page, cookies, or screenshots.
- **path:** pendant → browser-extension → mac-planner → relay → dashboard
- **model tier:** Run extraction and redaction locally on the Mac with a small model or deterministic DOM selectors; use the realtime relay model only on the redacted, bounded result to speak the answer. Escalate to a local Mac planner when the question requires navigation.
- **latency:** Under 3 seconds for a text-heavy page and under 8 seconds for a complex dashboard. The pendant should say when local extraction is still running rather than timing out silently.
- **cost:** About $0.00–$0.02 per request if extraction is local; the dominant cost is the short redacted text sent to the realtime model, not the page itself.
- **security:** Redaction must be fail-closed for passwords, tokens, account numbers, and hidden DOM. Raw HTML, screenshots, and browser cookies never leave the Mac. Show an audit record of extracted fields and allow the owner to disable cloud answering per site. A wrong redaction is a privacy failure, so uncertain fields should be omitted and the answer should say so.
- **missing:** A Mac-local page-questioning/extraction endpoint callable by the relay; Site-aware sensitive-field detection and a hard byte/token budget for relay payloads; A request-scoped privacy receipt showing exactly what crossed the Mac boundary; A browser action mode that returns structured fields rather than a full browser_read_page transcript

### "“Watch me do this browser task once, turn it into a named voice command, and next time repeat it with the new values I dictate.”"
- **useful because:** The system today can execute a planned browser action, but the owner must explain the workflow again every time. Demonstration-to-routine would let a worn pendant turn one real authenticated Safari workflow into a reusable personal skill—especially valuable for repetitive portals that no public API exposes.
- **path:** pendant → browser-extension → mac-planner → relay → dashboard
- **model tier:** Use the browser extension to record a structured trace locally; use the background planner model to infer parameters, invariants, and stop conditions. The realtime model only captures the name, supplied values, and final spoken result.
- **latency:** Recording has no added latency. Compile a trace into a routine in under 30 seconds. A later run should acknowledge immediately, execute asynchronously, and return a concise spoken result with a link to the trace.
- **cost:** $0.03–$0.20 to compile a demonstration depending on screenshots and trace length; routine runs should cost under $0.03 unless a changed page requires replanning.
- **security:** Traces can contain credentials and personal data. Keep raw keystrokes and screenshots on-device, replace values with typed parameters, redact secrets, and require explicit opt-in at recording start. A generated routine must never infer that a submit/payment/send step is safe merely because it appeared in the demonstration; preserve the owner’s existing maximum-access policy while clearly reporting such steps.
- **missing:** A browser-extension trace recorder with semantic DOM targets, waits, and parameter markers; A routine compiler/validator and versioned routine store; A replay engine that detects page drift and hands recovery to mac-planner; A pendant command namespace and durable completion/error delivery for named routines

### "“While my Mac is carrying out that long task, let me steer it from the pendant: pause at the next safe boundary, change one parameter, skip a step, or continue.”"
- **useful because:** Long Mac/browser jobs are currently fire-and-forget once handed off. The owner cannot safely correct a mistaken assumption from the wearable without cancelling or starting over. A live control channel makes the pendant a true remote cockpit for work that outlasts a voice turn.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** The realtime relay classifies only the short steering command and speaks status. The Mac planner owns the task state and uses a small policy model to find safe checkpoints; mac-vision/browser-extension report observations. No expensive re-planning is needed for a simple parameter edit.
- **latency:** Acknowledge a steer request in under 500 ms. Pause or apply a parameter change at the next checkpoint within 5 seconds; if the Mac is offline, queue the request and tell the owner plainly.
- **cost:** Under $0.01 per steering event; cost is dominated by a compact state snapshot, not a new full plan. A recovery re-plan may cost $0.05–$0.30.
- **security:** The relay must bind controls to the owner’s active job and reject stale or ambiguous job references. Do not pretend a pause happened until the Mac acknowledges it. Keep a tamper-evident event log of requested, accepted, and applied edits; preserve the owner’s maximum-access policy, but never silently substitute a different target or value.
- **missing:** A bidirectional job-control protocol with pause/resume/skip/edit operations and acknowledged sequence numbers; Planner checkpoints that describe the next reversible boundary and current parameters; A pendant-facing job selector for multiple concurrent jobs; Mac planner and browser/vision adapters that can apply edits without discarding completed work


## Changes it proposed to its own stack

### `integration` — Implement a real, enum-based intent router that maps a small set of spoken intents to typed actions, returning a jobId and a human-safe spoken summary.
- **owner gets:** It makes voice control predictable and safer, and reduces accidental side effects from free-form routing.
- effort: High; requires schema design, resolver logic, and integration with plan/execute.  ·  risk: Medium; a bad mapping could mis-execute. Mitigate with conservative defaults and explicit confirmation for high-risk intents.
- cost: Moderate; adds an extra planning step.  ·  latency: Small added overhead; acceptable for most tasks.
- security: Positive; reduces ambiguity and makes auditing easier.
- depends on: Using the existing POST /plan and POST /execute action vocabulary

### `model-routing` — Introduce a background monitoring service (scheduler or durable-object alarms) for job completion, with a notification pipeline to the pendant via the existing inbox concept.
- **owner gets:** They can start something and forget it, then get a concise alert when it’s done.
- effort: High; needs new infrastructure and clear delivery semantics.  ·  risk: Medium; duplicate or missing alerts are annoying. Mitigate with idempotent receipts and TTLs.
- cost: Moderate ongoing cost; depends on polling frequency and number of jobs.  ·  latency: Notification latency depends on polling interval; user experience improves most when it’s under a minute.
- security: Must avoid leaking job details; keep alerts minimal and respect consent.
- depends on: A durable queue for alerts; A real implementation for relay_event_push or a replacement route


## What it asked for

_Nothing._
## Its own summary

Discovered the current toolset and grants. Verified that relay_job_status has a real description, while relay_route_intent, server_browser_actions, and relay_event_push are granted schemas but unresolved (calling them won’t perform work). Proposed multiple capabilities/changes; some were rejected as duplicates, but an enum-based intent router and a background completion-monitoring pipeline were recorded as new, useful directions.

**Biggest unknown:** What concrete, non-duplicate capability would most help the owner right now that requires a new cross-surface mechanism beyond job completion notifications and manifest introspection, and which missing routes/tools should be built first to support it.

