# Harness derivation — relay-realtime — round 28

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that longer task after I stop talking, and tell me what happened later."
- **useful because:** The owner is wearing the pendant and often walks away. They should be able to hand off a multi-step job, then get a clear status update without keeping a live conversation open.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only to confirm handoff; mac-planner for planning/execution; relay_job_status for later status, using a cheaper tier if available for summary.
- **latency:** Under 1 second to confirm handoff; background work can take minutes. Status checks should be near-instant and not require the Mac to be awake.
- **cost:** Low per invocation for handoff/status; dominant cost is mac-planner execution and any browser automation, plus storage for job logs.
- **security:** Status text may contain sensitive content from apps or pages. Only return minimal, user-sized summaries and store provenance. Never claim completion unless the job is marked done.
- **missing:** A durable job lifecycle service that spans relay and mac, with consistent IDs and typed states; A notification path to the pendant/dashboard when a job finishes; Optional server-side browser execution for jobs that do not require the Mac

### "“What was I looking at on my Mac or in the browser earlier, and what did I need to do next?” (Also: “Continue from the thing I was working on.”)"
- **useful because:** The owner is usually away from the Mac when speaking to the pendant, yet their unfinished context is split between open Mac apps, browser tabs with authenticated sessions, and voice history. Today the pendant cannot reconstruct that context; this would let a brief spoken request recover the relevant thread and continue it without manually remembering filenames, tabs, or error messages.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime handles intent disambiguation and a concise spoken answer only. A cheaper background extraction/indexing model continuously turns permitted Mac/browser activity snapshots into short searchable evidence; mac-planner and browser harness fetch live details only for the selected thread.
- **latency:** Under 2 seconds for a spoken answer from the recent local index; up to 10 seconds when live Mac/browser evidence must be collected. Never block the voice turn on a full app crawl—say what is known and offer to continue asynchronously.
- **cost:** Roughly $0.01–$0.05 per recall, dominated by live evidence extraction and planner calls; routine indexing should use a small/cheap model and batch snapshots rather than the realtime tier.
- **security:** Activity may include private documents, messages, and authenticated pages. Keep raw contents on the Mac/browser session where possible, send only narrowly selected snippets and hashes to the relay, encrypt the activity ledger, provide per-app/site exclusions and retention limits in the dashboard, and clearly identify uncertainty. Continuing an action must be a separate explicit request; merely recalling context must not mutate anything.
- **missing:** A cross-surface activity ledger that records bounded, timestamped active-window/tab/document context plus embeddings or compact summaries; Mac and browser harness APIs to export the currently relevant context on demand, with app/site exclusion and redaction support; A relay retrieval endpoint that ranks evidence across voice, Mac, and browser records and returns citations/timestamps; A dashboard view for retention, exclusions, and deleting individual context records; A continuation handoff protocol from the selected recalled thread to mac-planner/browser without conflating recall with execution

### "“Use the file I just edited to fill out that form in the browser, attach it, and tell me exactly what was submitted.”"
- **useful because:** Today Mac and browser actions are separate command paths, so the owner cannot use a local artifact while away from the Mac to complete an authenticated web workflow. This bridges the Mac’s local files and the browser’s logged-in session into one voice-directed operation, with a precise spoken receipt instead of forcing the owner to remember paths, tabs, and fields.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime parses the request and resolves only obvious references. mac-planner locates and reads the permitted local artifact; browser harness operates the authenticated session; a cheaper verifier extracts the final field values and attachment identity. Realtime speaks the concise result and any ambiguity.
- **latency:** Resolve references in 2 seconds; complete ordinary workflows in 10–30 seconds. If either surface is offline, preserve a resumable job and report the exact missing leg rather than pretending completion.
- **cost:** About $0.03–$0.15 per completed workflow, dominated by planner/browser interaction and post-submit verification; simple reference resolution should be cheap cached retrieval.
- **security:** This can move private local files into authenticated websites and submit consequential data. Maintain a provenance manifest (source path/hash, destination origin, fields, timestamp), redact secrets from relay logs, restrict file selection to the explicitly resolved artifact, detect origin changes, and return a spoken receipt. The owner allows access without confirmation, but submission must still be observable and recoverable with a cancel/undo or draft mode where the destination supports it.
- **missing:** A cross-surface job protocol carrying artifact references, not raw files, between Mac bridge and browser harness; Mac-side artifact resolver that can identify the recently edited file and expose a bounded read/attachment stream; Browser-side form schema extraction, upload support, and post-submit receipt capture; A durable job/receipt store with resumable state, idempotency keys, and failure recovery across relay, Mac, and browser outages; Dashboard provenance and deletion controls for transferred artifacts and receipts

### "“Mark this moment.” (Press the pendant button, optionally say a short label, then later: “Take me back to the moment I marked as ‘pricing bug.’”)"
- **useful because:** The pendant is the only surface physically with the owner, while the meaningful context may be on a Mac window or authenticated browser tab. A one-button anchor would capture the owner’s intent at the instant it matters—even when they cannot stop to copy a URL or filename—and later reopen or summarize the exact cross-device context.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** The pendant firmware records a local timestamp/button event and the relay pairs it with a short voice label. A cheap background worker requests compact active-context snapshots from Mac and browser, stores a ranked anchor, and realtime later answers or routes a reopen request.
- **latency:** Button acknowledgement must be immediate and offline-capable; pairing and context capture should finish within 5 seconds when devices are reachable. Retrieval should answer in under 2 seconds from the anchor index.
- **cost:** A few cents per labeled anchor at most; the dominant cost is occasional Mac/browser context capture, not the button event or realtime response. Firmware storage and LTE payloads are small.
- **security:** Anchors can expose whatever was onscreen, including private pages. Default to a short encrypted summary plus origin/path and allow app/site exclusions, retention expiry, and deletion. Do not upload screenshots by default. If reopening a page could cause a mutation, open read-only and report the target before any action.
- **missing:** Firmware support for a durable button event queue with timestamp, sequence number, and optional short audio-label association; A relay pairing window that correlates the event with nearby-in-time voice and device context despite clock drift or intermittent LTE; Mac/browser APIs for a point-in-time active-window/tab snapshot and a stable reopen token; An anchor index with retention, exclusion, and deletion controls in the dashboard; A read-only reopen/summarize operation that can recover gracefully when the original app, tab, or file no longer exists


## Changes it proposed to its own stack

### `routines` — Introduce a scheduler layer (cron-like) with durable job definitions, per-job cadence, retry policy, quiet hours, and a wake/dispatch mechanism that can target mac-planner, server browser, or relay summaries. Use Cloudflare Cron/Durable Object alarms as the first backend, with a queue abstraction so the Mac and future services can share it.
- **owner gets:** Unlocks everyday conveniences like morning briefs, page watches, and follow-up tasks without keeping a session open. The owner can trust the system to act later, then report back.
- effort: High. Requires new storage tables, dispatch code, and job state transitions; plus UI to manage jobs.  ·  risk: Misfires (duplicate runs, wrong time zone, runaway retries). Mitigate with idempotency keys, per-job rate limits, and clear audit logs. Provide a kill switch and manual rerun.
- cost: Moderate ongoing compute/storage; biggest cost is scheduled runs and external automation. Cloudflare cron/alarm costs are small compared to model execution.  ·  latency: Adds no latency to live conversations; improves perceived latency by doing work ahead of time.
- security: Scheduled jobs may access private data. Needs strict scoping, stored consent, and auditability.
- depends on: Typed job schema with provenance and idempotency; Notification/receipt mechanism to deliver results back to the owner


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: cross-surface recall of unfinished Mac/browser context, voice-directed use of a local Mac artifact in an authenticated browser form with provenance receipts, and a physical pendant “mark this moment” anchor that captures and later reopens cross-device context. Each includes the missing relay, Mac, browser, firmware, storage, and dashboard changes rather than assuming current wiring.

**Biggest unknown:** Whether the existing Mac bridge and browser harness can expose point-in-time active-context snapshots and stable read-only reopen tokens; that determines how much new instrumentation the first two capabilities require.

