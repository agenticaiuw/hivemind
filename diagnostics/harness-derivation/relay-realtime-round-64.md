# Harness derivation — relay-realtime — round 64

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If it can’t reach my Mac right now, keep going anyway — check if the task is queued, and if you can, do the web part from the cloud and tell me what’s done and what’s waiting."
- **useful because:** When the owner is away from the Mac, they still want progress. This combines relay-side status checks with cloud browser work, so the system can continue without waking the Mac or leaving the user guessing.
- **path:** relay → browser → mac-bridge
- **model tier:** Realtime only for the spoken status; planning and web automation should run on a cheaper non-realtime tier when possible.
- **latency:** Quick spoken update (under a second) when checking status; web automation may take several seconds but should stream progress if available.
- **cost:** Low for status checks; moderate for cloud browser sessions dominated by page loads and extraction.
- **security:** Cloud browsing touches third-party sites; only open the minimum URLs, avoid authenticated sessions unless explicitly required, and clearly report what data was accessed. Never claim completion unless status says done.
- **missing:** A stable cloud browser harness wired to the relay (server_browser_actions) with session and auth constraints defined; Clear policy for when to prefer cloud browsing vs delegating to the Mac; Typed receipts that link cloud steps to Mac jobs for a single user-visible outcome

### "While you are carrying out a task on my Mac or in my signed-in browser, let me steer it from the pendant: “skip that,” “use the other account,” “stop after drafting,” or “what are you doing now?” Then resume and give me a concise spoken result when it finishes."
- **useful because:** Today a delegated job becomes opaque once it leaves the voice turn; the owner must walk back to the Mac or restart the request. This makes the wearable a true remote control for work already in flight, combining the pendant’s presence, the relay’s low-latency conversation, the Mac planner’s state, and the browser’s authenticated session.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Use relay-realtime only to classify the short steering utterance and speak status. Use the cheaper planner tier to re-plan the remaining work; use mac-vision/browser execution only for the concrete next step.
- **latency:** Acknowledge a steering command in under 1 second; reflect the new plan/status in 2–5 seconds. Completion can take as long as the underlying Mac/browser task.
- **cost:** About $0.01–$0.08 per steering event, dominated by planner re-planning and any fresh page/screenshot context; status-only questions should be relay-local and near-zero incremental model cost.
- **security:** The relay must bind speech to the owner’s active job and never steer another session. Browser contents, Mac screenshots, and spoken commands may leave the device to the relay; persist only redacted task state and action receipts. Destructive or externally visible actions should remain explicitly represented in the spoken plan, even though the owner’s maximum-access policy does not require a confirmation gate.
- **missing:** A durable job control channel with pause, cancel, amend, and resume semantics across relay, Mac planner, and browser bridge; Typed job events and checkpoints that can be summarized over voice, including which surface currently owns execution; An interruption-safe planner that can re-plan from the last committed checkpoint and avoid replaying completed actions; Pendant-to-job correlation and a compact spoken status protocol, plus dashboard visibility for active/paused jobs

### "Check whether the information I’m looking at in the browser agrees with the source on my Mac, and tell me exactly what conflicts—for example, “does this invoice total match the PDF and the accounting email?”"
- **useful because:** The owner currently has to manually move facts between an authenticated browser session and local files or mail. A wearable answer that identifies the conflicting fields and cites each source would prevent costly mistakes while they are away from the desk; it depends on combining surfaces that no single node can reach.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheaper background comparison model for extraction and field-level diffing; use relay-realtime only for the spoken request, clarification, and concise result. Escalate to Mac-vision only when a source is visual or not accessible as structured text.
- **latency:** Acknowledge immediately; return a small comparison in 5–15 seconds, with longer documents continuing asynchronously and a spoken completion alert.
- **cost:** Roughly $0.03–$0.20 per comparison, dominated by document extraction and the amount of browser/Mac context; cache content hashes and extracted fields to avoid resending unchanged documents.
- **security:** This can expose private mail, local files, and authenticated pages to the relay/model. The system must show source names, retain only hashes plus the requested extracted fields, and never silently include unrelated tabs or files. External sharing is out of scope unless separately requested.
- **missing:** A cross-surface source selector that resolves the active browser tab and a narrowly scoped Mac file/mail query; A common citation and field-extraction format for browser pages, PDFs, messages, and screenshots; A relay job that compares immutable snapshots and reports provenance plus uncertainty; A redaction and retention layer so raw private documents are not retained after the comparison

### "Learn this workflow from me once: when I say “prepare the launch report,” gather the open browser dashboard, the latest project files, and the numbers from my Mac, update the report draft, and leave me a spoken summary. Let me review and edit the learned steps by voice later."
- **useful because:** The owner should not have to re-explain a cross-device routine every week. Demonstration-based workflows turn the hive into a personal tool without requiring the owner to write automation, while keeping the wearable as the invocation and correction surface.
- **path:** pendant → relay → mac-planner → mac-terminal → mac-vision → browser-extension → browser → dashboard
- **model tier:** Use the expensive realtime model only to capture the demonstration and handle invocation/clarification. Compile the trace into a parameterized workflow with a cheaper model, then execute ordinary steps through the planner and browser/Mac harnesses.
- **latency:** Voice confirmation of what was learned in under 3 seconds; ordinary invocations should acknowledge in under 1 second and report completion asynchronously. Editing a workflow can take one conversational turn per change.
- **cost:** Approximately $0.05–$0.30 to compile a new demonstration, then $0.005–$0.05 per invocation depending on screenshots and document extraction. Most savings come from reusing the compiled workflow and context hashes.
- **security:** Demonstrations may contain private documents, account names, and typed data. Store a redacted workflow graph rather than a raw transcript or screenshot recording, encrypt credentials by reference, and expose a spoken/dash­board “what will this do?” preview. Never generalize secrets or literal recipients into reusable slots without labeling them.
- **missing:** A cross-surface trace recorder that captures intent, observations, actions, and outcomes without storing unnecessary content; A workflow compiler that converts traces into editable parameterized steps with explicit read/write effects; A versioned workflow registry with dry-run, rollback, and owner-visible diffs; Adapters that can invoke the same workflow through pendant speech and route each step to the Mac or authenticated browser


## What it asked for

_Nothing._
## Its own summary

Recorded three new capabilities: live spoken steering of in-flight Mac/browser jobs; field-level contradiction checking between authenticated browser sources and local Mac sources; and demonstration-based reusable cross-surface workflows. Their required changes are enumerated in each proposal, including durable job control, provenance/retention, trace capture, workflow compilation, and versioned rollback.

**Biggest unknown:** Whether existing backend jobs and browser/Mac bridges already emit enough checkpointed, typed events to support interruption-safe steering; I did not re-discover this round per instruction.

