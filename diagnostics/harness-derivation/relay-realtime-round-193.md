# Harness derivation — relay-realtime — round 193

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is offline, check a public webpage for me anyway and read the key info aloud."
- **useful because:** This makes the pendant useful when the Mac is asleep: you can still get answers from the web without waiting to reconnect.
- **path:** relay-realtime → relay
- **model tier:** Realtime for conversation; cheaper model for extraction/summarization.
- **latency:** A few seconds is fine; reading aloud should start once key facts are extracted.
- **cost:** Moderate per request: one remote page fetch plus summarization. Dominated by network and parsing.
- **security:** Avoid authenticated pages and personal data. Only allow public URLs and safe extraction; block scripts and downloads.
- **missing:** A real server-side browser capability (server_browser_actions) or equivalent headless browsing in the relay surface; A safe allowlist and content sanitization policy

### "“When I say ‘sort this out,’ reconcile the relevant evidence across my Mac, authenticated browser tabs, and the pendant conversation, then tell me the answer and fix the discrepancy if it is safe.” For example, resolve a conflicting reservation, missing confirmation, or stale document without making me explain which surface contains each clue."
- **useful because:** Today each surface can be queried or acted on, but none can establish that three contradictory artifacts refer to the same real-world item. The owner gets one spoken investigation with cited evidence, rather than manually searching Mail/files/browser and guessing which copy is current.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay extracts the entity and urgency only; a cheaper background investigation model performs cross-surface entity resolution; faculty-perception gathers evidence, faculty-judgement chooses the canonical interpretation, and faculty-action applies only reversible repairs. The relay returns a short spoken conclusion with an evidence count and uncertainty.
- **latency:** Acknowledge in under 500 ms; first useful spoken hypothesis within 8 s; allow 1–3 minutes for authenticated browser/Mac evidence collection, with a final alert rather than holding the voice channel open.
- **cost:** Roughly $0.03–$0.15 per investigation depending on screenshots and document extraction; browser/Mac latency and multimodal evidence, not relay speech, dominate.
- **security:** Evidence may include private mail, files, and authenticated pages. Keep raw artifacts on their originating surface, send hashes/snippets and provenance by default, redact secrets before model calls, and require explicit confirmation before destructive or externally visible repair.
- **missing:** Cross-surface entity/provenance bundle with stable artifact IDs and timestamps; A background investigation job that can query Mac and browser in one case; Conflict-resolution output schema with citations and uncertainty; A repair transaction that can be previewed and undone

### "“Watch the thing I just asked you to change and interrupt me only if the result is materially different from what I intended.” The system should compare the eventual Mac/browser outcome with my original spoken constraints, detect silent partial success or collateral changes, and explain exactly what needs attention."
- **useful because:** A job receipt can say that actions ran while still missing the owner’s actual goal. This gives the owner an outcome-level guarantee: failed logins, wrong tabs, partial edits, and unintended side effects are caught without requiring them to poll or inspect the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay preserves the utterance and constraints; a background verifier compares pre/post snapshots, action receipts, and browser/Mac observations; faculty-judgement classifies success, partial success, or contradiction; faculty-action can roll back reversible changes. Use the relay only for the spoken exception summary.
- **latency:** Immediate acknowledgement under 500 ms; verification starts as soon as the job ends and completes within 10–30 s for ordinary tasks. Notify the pendant only on exception or a concise requested completion.
- **cost:** About $0.01–$0.08 per completed job; screenshots, OCR, and long documents dominate, while most receipt-only checks are cheap.
- **security:** Verification must not silently broaden access or repeat mutations. Persist a constraint digest and before/after metadata, not full private content unless needed; make notifications explicit about confidence and never claim success from an unobserved state.
- **missing:** Constraint extraction and durable binding of the original utterance to a job; Before/after observation snapshots for Mac and browser; Goal-level verifier and partial-success taxonomy; Automatic safe rollback plus exception delivery to the pendant

### "“Give me a spoken, source-backed answer about what is happening on my computer right now, but do not expose private screen content unless it is necessary.” The pendant should be able to ask the Mac and browser for a minimal redacted state, correlate it with relay health and the last action, and answer whether the problem is the app, the browser session, the network, or the pendant."
- **useful because:** The owner is often away from the Mac and currently receives isolated status signals. A diagnosis that distinguishes stale browser authentication from a dead Mac, relay failure, or pendant audio failure prevents wasted retries and makes remote recovery possible from one button press.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Faculty-perception gathers typed health probes and minimal redacted UI signals; faculty-judgement performs fault isolation; faculty-action runs a reversible recovery such as relaunching an app or refreshing a session. Realtime speaks the diagnosis; no expensive model is used for normal telemetry.
- **latency:** Health diagnosis in 2–5 s; recovery attempt in under 20 s. If the Mac is offline, answer that fact immediately from relay/device telemetry rather than waiting.
- **cost:** Under $0.01 for typed probes; $0.03–$0.10 when a screenshot or vision pass is required. Network reachability and optional vision sampling dominate.
- **security:** Default to structured process/window/session/error metadata and redact titles, URLs, and text. Any screenshot or authenticated-page content requires a narrow reason and short retention. Recovery actions must be logged with before/after receipts.
- **missing:** A unified health/fault vocabulary spanning pendant, relay, Mac, and browser; Redaction-aware Mac/browser probe endpoints; Fault graph correlating telemetry with job and audio timelines; A pendant-facing diagnostic response and recovery policy


## Changes it proposed to its own stack

### `relay` — Add a durable CrossSurfaceCase object created from one spoken turn. It stores the normalized entity, original constraints, source artifact references (Mac/browser/pendant), observation timestamps, confidence, and a final claim; planners and action agents must append evidence and receipts to that case rather than returning unrelated job records.
- **owner gets:** The owner can ask one follow-up such as “which copy is current?” and get an answer grounded in the same investigation, instead of restarting and re-explaining the problem.
- effort: Medium: schema, case lifecycle, adapters around plan/execute/browser inspection, and compact spoken rendering.  ·  risk: Stale or incorrectly linked artifacts could create a confident but wrong conclusion. Expire cases, show provenance and confidence, and permit case abandonment without mutating source data.
- cost: Small storage cost; roughly $0.002–$0.01 extra per case for metadata and one cheap summarization pass.  ·  latency: Adds under 300 ms to case creation; evidence collection remains asynchronous.
- security: Centralizes references to private artifacts, so store opaque IDs and redacted snippets by default with per-case retention.
- depends on: A background cross-surface investigation worker; Stable artifact IDs and provenance adapters for Mac and browser; A follow-up endpoint that retrieves case context

### `model-routing` — Persist a ConstraintDigest beside every planned job: explicit success conditions, prohibited side effects, target entities, and ambiguity markers extracted from the owner’s utterance. At completion, run a separate verifier against receipts and fresh observations; classify success, partial success, contradiction, or unverifiable before emitting any spoken completion.
- **owner gets:** “Done” would mean the requested outcome was observed, not merely that a list of clicks and shell commands returned without errors.
- effort: Medium-high: constrained extraction, verifier prompts/evaluators, observation adapters, and integration with undo/event delivery.  ·  risk: A verifier may falsely reject a genuinely successful task or miss a subtle side effect. Keep raw receipts, expose “unverifiable,” and never auto-retry a mutation from verifier output alone.
- cost: $0.005–$0.05 per job depending on whether screenshots or document comparisons are necessary.  ·  latency: Adds 2–20 s after execution; no delay to initial acknowledgement.
- security: Constraint digests should avoid copying private content; observations must be purpose-limited and redacted.
- depends on: Cross-surface case or job context persistence; Mac/browser before-and-after observation snapshots; A real asynchronous completion watcher

### `context` — Create a redaction-first FaultGraph that joins pendant audio/connection telemetry, relay pipeline events, Mac reachability, browser-session heartbeats, and recent job receipts into typed hypotheses (Mac offline, browser auth expired, relay stalled, audio degraded, action partially applied). Expose only the minimal fields needed for spoken diagnosis.
- **owner gets:** From anywhere in the house, the owner could learn whether retrying will help and receive the right recovery, instead of repeatedly saying the same command into a broken path.
- effort: High: common event schema, correlation windows, probe adapters, diagnosis rules, and pendant-sized response summaries.  ·  risk: Bad correlation could blame the wrong component or trigger an inappropriate recovery. Start read-only, attach evidence and confidence to every hypothesis, and make recovery separately auditable.
- cost: Low telemetry storage and under $0.01 per diagnosis unless vision is invoked.  ·  latency: Typed probes can answer in 2–5 s; vision fallback may add 5–15 s.
- security: Redact screen text, URLs, and document names by default; retain raw diagnostics only under short TTL.
- depends on: Unified health vocabulary; Mac and browser redaction-aware probes; Correlation with /pipeline and job timelines; Pendant-facing status delivery


## What it asked for

_Nothing._
