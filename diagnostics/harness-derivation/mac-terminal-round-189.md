# Harness derivation — mac-terminal — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take care of whatever is on my screen.”"
- **useful because:** This would be the single most useful everyday action: a button press or spoken phrase on the pendant hands the currently focused Mac window and authenticated Safari tab to one planner, which figures out the smallest useful next step, acts through the Mac or browser session, and tells the owner exactly what changed. Today the owner must explain which app/tab is relevant and manually bridge the wearable to the machine.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the short intent and spoken result; a cheaper background planner handles screen/tab interpretation and execution, escalating to realtime only when ambiguity blocks action.
- **latency:** First acknowledgement under 700 ms; capture active-window/tab context within 2 s; simple actions complete within 10 s, with truthful_action_status_beacon and a spoken progress update for longer work.
- **cost:** About $0.01–$0.05 for a simple turn depending on screenshots and browser DOM; the expensive part is vision tokens, so send structured window/tab metadata first and a screenshot only when needed.
- **security:** The Mac snapshot may contain private document names and the browser may expose authenticated data. Keep capture on the Mac where possible, redact secrets before relay, never infer authorization from screen content, and speak a preview when the inferred action is destructive. The owner’s maximum-access policy means no artificial gate for ordinary reversible work, but every result must say what actually ran.
- **missing:** A single context-capture contract joining focused app, selected text, active Safari tab metadata, screenshot/DOM inspection, and the pendant turn ID; Planner routing that can choose Mac shell, typed Mac action, browser command, or mac-vision from that contract; A durable result receipt that links the spoken request, captured context, action job, browser command, and final evidence

### "“Read me the important thing in the Safari page I’m on, and if it needs action, do it.”"
- **useful because:** The owner can get a spoken, source-grounded answer without touching the keyboard: the browser extension supplies the authenticated page’s visible content and session identity, the Mac supplies which tab is actually foreground, and the pendant is the zero-friction output. If the page contains a task (approval, reply, deadline, form), the agent can execute it and read back the exact result rather than merely summarizing.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** A cheap extraction/classification model handles page text and identifies candidate actions; realtime is reserved for the two-sentence spoken answer and a follow-up question when multiple actions are plausible.
- **latency:** Foreground-tab confirmation under 1 s, extraction under 4 s, spoken answer under 6 s; actions continue asynchronously with a pendant status pulse and completion receipt.
- **cost:** Roughly $0.005–$0.03 per page when DOM text is available; screenshots and vision are fallback costs. Browser content, not whole browser history, should be sent.
- **security:** Authenticated content must remain scoped to the active tab and current browser session; do not include cookies or raw page source in relay logs. The agent must quote the page title/host and the evidence excerpt it used, and distinguish 'I read' from 'I acted'.
- **missing:** A foreground-tab lock so the active Safari tab cannot silently change between capture and action; A browser-side 'read/actionable' result containing bounded text spans and stable element IDs rather than a screenshot-only observation; A spoken evidence formatter that cites host, page title, and the exact action receipt

### "“Do it, but don't tell me it's done until you have verified the result.”"
- **useful because:** This turns the system from an action launcher into a dependable assistant. After a Mac shell, UI, or authenticated-browser action, it independently checks the expected postcondition—file exists with the right contents, window state changed, message appears in Sent, form shows success—and reports success, failure, or uncertain state on the pendant. For high-value work, that is more useful than faster execution because it prevents confident false completion.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A low-cost deterministic verifier evaluates typed postconditions and receipts; use mac-vision or a small model only when the state is visual/semantic. Realtime speaks the final three-state result, not the whole trace.
- **latency:** Verification begins immediately after each action; ordinary checks under 2 s, visual/browser checks under 8 s. If verification exceeds that, the pendant says 'still checking' and never upgrades to completed by timeout.
- **cost:** Near-zero for filesystem/process/HTTP status checks; $0.01–$0.04 when a screenshot or DOM interpretation is required. This saves more expensive retries and owner time.
- **security:** Verification must not perform a second mutation while checking. Evidence should be minimized and redacted, with host/app/page identity and hashes or bounded excerpts rather than full private content. Persist the precondition, intended postcondition, observed state, and confidence so an owner can audit what 'done' meant.
- **missing:** An action schema carrying explicit preconditions and postconditions through POST /execute rather than only a free-form label; A verifier registry for shell, file, Mac UI, and browser assertions, including a third state of unknown; A cross-surface receipt join keyed to the same turn/job/action ID and firmware status-beacon update only after verification

### "“Only interrupt me for something that truly needs me now; otherwise handle it and give me a quiet digest later.”"
- **useful because:** The owner gets an assistant that protects attention across the wearable, Mac, and authenticated browser instead of turning every notification into a spoken interruption. It can recognize that a calendar change, work message, browser alert, or failed Mac job is urgent, ask one concise question through the pendant when necessary, and defer everything else into a time-bounded digest with no repeated alerts.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background classifier handles incoming events and urgency scoring; realtime is used only for an actually urgent interruption or the owner's reply. A daily digest can use a slower background model.
- **latency:** Ingest events within 3 seconds; urgent decisions within 5 seconds; non-urgent items are silent and summarized at the owner's next configured quiet-window boundary.
- **cost:** Usually under $0.01 per event with structured notification metadata; model cost is dominated by long message bodies, which should only be fetched for candidates near the urgency threshold.
- **security:** Notification content can be highly private. Keep raw bodies on the Mac/browser where possible, send only extracted features to the relay, and make the pendant announce source and reason before reading sensitive text aloud. The system must never silently send, accept, cancel, or modify an external commitment merely because it classified it urgent.
- **missing:** A unified event intake for Mac notifications, browser page watches, job failures, and relay events with deduplication and provenance; An owner-editable urgency policy that learns from explicit dismiss/defer/interrupt feedback without silently changing high-impact preferences; A durable quiet queue with expiry, escalation rules, and a spoken digest renderer shared by relay and dashboard


## Changes it proposed to its own stack

### `browser-harness` — Implement a two-phase foreground-tab lease: on a pendant request, atomically capture Safari window/tab identity, URL origin, title, DOM revision/hash, and selected text; reject any browser action if the tab/window or revision changes before execution, then reacquire and verify the same lease after the action. Return a bounded evidence span and an explicit stale-context result to the relay.
- **owner gets:** The owner can ask about or act on the page they are actually looking at without the assistant accidentally reading one tab and clicking another after Safari changed, a race that is currently invisible and particularly dangerous for authenticated work.
- effort: Medium: extension heartbeat and inspection schema changes plus a lease store in the Mac agent; no new model is required.  ·  risk: Dynamic pages may legitimately change their DOM and cause a false stale result. Retry one fresh inspection, then speak that the page changed rather than guessing. Never retain cookies or full page bodies in the lease.
- cost: Tiny local metadata store; usually no additional API tokens because the lease uses existing inspection data.  ·  latency: Adds one inspection/hash round trip, typically 200–800 ms; avoids expensive vision retries and mistaken actions.
- security: Improves session safety by binding actions to origin/tab identity; logs only origin, title, revision hash, and bounded excerpts.
- depends on: A browser inspection response with stable tab/window identity and DOM revision; A turn-scoped correlation ID shared by pendant, relay, Mac job, and browser command


## What it asked for

_Nothing._
## Its own summary

Produced three distinct owner-facing capabilities: “take care of whatever is on my screen” as a cross-surface handoff, source-grounded spoken Safari action, and postcondition-verified execution. Added a concrete browser-harness change: a two-phase foreground-tab lease that detects tab/DOM races before acting. The system already has the component routes; the missing value is their shared turn identity, evidence contract, and verification semantics.

**Biggest unknown:** Whether the browser extension currently exposes a stable tab/window identifier and DOM revision/hash in its inspection payload. Without that, a safe foreground lease cannot distinguish a page that changed from the page that was originally inspected.

