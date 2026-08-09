# Harness derivation — relay-realtime — round 249

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Check the USB-connected pendant and audio bridge and tell me what’s broken."
- **useful because:** Today, the pendant is physically connected to the Mac even if LTE isn’t registered. A quick health check saves a lot of guesswork.
- **path:** mac-bridge → relay-realtime → pendant → audio bridge
- **model tier:** Realtime to coordinate and narrate; Mac-local logic to run diagnostics and parse results.
- **latency:** A few seconds for a basic probe; longer if audio loopback tests run.
- **cost:** Low. Mostly local diagnostic commands and small status payloads.
- **security:** Diagnostics may expose serial identifiers and device metadata; keep them local and avoid logging sensitive identifiers to shared stores.
- **missing:** A defined ingestion route for USB diagnostic results (mac-planner asked for this); A standard diagnostic schema for pendant/bridge health including audio loopback and firmware versions

### "When I say “save my place,” have the pendant and my Mac create a resumable checkpoint of exactly where I was working, then let me say “resume my place” later."
- **useful because:** Away from the Mac, the owner can preserve a real work context rather than a vague note: active app and window, browser tabs and authenticated page location, relevant document paths, and the next safe action. On return, one spoken command reconstructs the workspace and reports anything that could not be restored.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime only interprets the short command; mac-planner performs the checkpoint/restore plan, with mac-vision verifying visible state and the browser extension contributing authenticated tab state. Use a cheaper background worker for checkpoint indexing and a final dashboard rendering.
- **latency:** A spoken acknowledgement in under 2 seconds; checkpoint capture may take 5–15 seconds and restore 10–30 seconds, with an asynchronous pendant alert when complete.
- **cost:** About $0.01–$0.05 per checkpoint/restore depending on planner and verification calls; browser and Mac inspection dominate, not the acknowledgement.
- **security:** Checkpoint metadata can expose private URLs, file names, and window contents. Keep artifacts on the owner’s relay/Mac, encrypt at rest, redact page text by default, and require an explicit spoken confirmation before restore actions that type, send, delete, or modify files.
- **missing:** A durable checkpoint schema storing synchronized Mac, browser, and terminal observations with timestamps and redaction policy; Mac and browser snapshot adapters that can be captured as one consistent checkpoint; A restore executor that detects drift and presents conflicts instead of blindly replaying stale actions; A user-visible checkpoint list and expiry/deletion controls

### "Do this as one transaction across my Mac and browser: update the source document, update the matching web form, and stop before submitting if the two no longer match."
- **useful because:** Today a multi-surface task can partially succeed while the owner is away, leaving a local file and an authenticated web form disagreeing. A cross-surface transaction would make the system useful for consequential work: inspect both sides, apply reversible changes, prove they agree, and either commit or leave a precise recovery point.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime classifies the request and states the boundary; a cheaper planning tier computes the action graph. mac-planner and browser-extension execute their portions, while mac-vision verifies the rendered result. Realtime is only re-entered for a concise exception or completion statement.
- **latency:** Immediate acknowledgement under 2 seconds; 15–60 seconds for inspection and execution. If a precondition changes, stop and notify rather than guessing.
- **cost:** Roughly $0.03–$0.15 per transaction; verification snapshots and replanning dominate. Failed transactions should cost less by reusing receipts and captured state.
- **security:** The browser may hold authenticated sessions and the Mac may contain private files. Do not export page contents to the model unless needed; retain hashes and field-level diffs where possible. The default commit boundary is the final external submit, which must be explicitly confirmed even though reversible local edits need not be.
- **missing:** A transaction coordinator with durable step dependencies spanning Mac and browser jobs; Idempotency keys and compensating actions for each supported Mac/browser action; Cross-surface compare/commit primitives that can compare semantic fields rather than screenshots alone; A receipt format that proves preconditions, changes, and postconditions as one outcome

### "I’m leaving my desk. Watch this work session across my Mac and authenticated browser, and when I come back tell me only what materially changed since I left."
- **useful because:** The owner should be able to walk away without either staring at the screen or receiving noisy notifications. The system would snapshot a declared work context, detect semantic changes in the local project and logged-in page while the owner is gone, suppress duplicates, and deliver one evidence-backed spoken delta when requested or when a genuinely urgent change occurs.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime handles start/stop and the final short explanation. A low-cost scheduled/watch evaluator performs periodic checks; mac-planner reads local project state, browser-extension reads the authenticated page, and mac-vision is invoked only when text/state extraction is ambiguous.
- **latency:** Start acknowledgement under 2 seconds. Checks can run every 5–15 minutes. A requested delta should be ready in under 10 seconds; urgent alert delivery should target under 1 minute after detection.
- **cost:** Approximately $0.01–$0.08 per check depending on whether visual verification is needed; unchanged checks should be hash-only and nearly free. A full return briefing costs one planner call plus selected evidence reads.
- **security:** The watch must be explicitly scoped and visibly active, with an owner-controlled expiry. Authenticated page content and local files stay in their owning surface; relay stores hashes, timestamps, and minimal extracted change snippets. Never speak sensitive changes aloud until the owner asks for the briefing, and support immediate stop/delete.
- **missing:** A temporary cross-surface watch session with one baseline ID and an explicit expiry; Semantic diff adapters for Mac files/apps and authenticated browser pages, rather than independent URL polling; A deduplicating urgency classifier and evidence bundle joining Mac and browser observations; A pendant-facing request/response path that can retrieve the delta after the original voice session ends

### "If I say “privacy now,” immediately freeze my Mac and authenticated browser work, stop queued actions, and tell me exactly what was locked and what could not be stopped."
- **useful because:** A worn device is the one control surface the owner has when someone walks up to an unattended Mac. One spoken command should close the gap between relay jobs, the local planner, and browser sessions: pause new work, lock the display, hide sensitive windows, and produce a truthful inventory instead of assuming every process stopped.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime recognizes the high-priority command and emits the first acknowledgement. A dedicated low-latency control path fans out to Mac and browser; mac-planner handles local locking/cancellation, browser-extension closes or masks authenticated tabs, and the dashboard shows the resulting receipt. No large model is needed unless a failure needs explanation.
- **latency:** Acknowledge in under 1 second; issue freeze commands within 2 seconds; report per-surface outcome within 5 seconds. Cancellation must be best-effort but bounded, never falsely reported as complete.
- **cost:** Under $0.01 per invocation; the dominant cost is none beyond command routing and receipt storage. A model call is only needed to explain an unusual failure.
- **security:** This is intentionally disruptive and must be an explicit phrase, not inferred from silence. Store no page contents in the relay. Use a locally authenticated device/session token, make the command idempotent, and expose an emergency local override so the owner cannot be locked out by a stale relay state.
- **missing:** A relay-level emergency control fan-out that can reach all active Mac/browser jobs concurrently; Mac actions for lock-screen, hide/close sensitive windows, and cancel/park planner jobs with receipts; Browser-extension actions for masking or closing authenticated tabs and acknowledging completion; A pendant gesture or firmware command path that remains available when ordinary voice uplink is unavailable


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: resumable cross-surface work checkpoints, transactional Mac/browser execution with semantic pre/post verification, temporary cross-surface departure watches with a material-change briefing, and a spoken emergency privacy freeze spanning Mac, browser, and queued relay work. The proposals deliberately identify the missing connective coordinators and durable evidence/receipt semantics rather than pretending existing routes already compose these behaviours.

**Biggest unknown:** Whether the existing watch, approval, and verification routes can be safely composed atomically; the live inventory exposed route fragments but not their cross-surface concurrency, cancellation, or idempotency guarantees.

