# Harness derivation — mac-planner — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — The Mac agent now has Accessibility and Screen Recording granted, synthesized input verified, Safari foreground, browser bridge online, relay reachable, and the pendant bench remains USB-testable even though LTE registration is not established.
  - evidence: mac_readonly_inspect(operation=running_apps) returned trusted:true, screenRecording:true, eventsPost:true; GET /ops/status returned ready:true, browser online, relay reachable, macBridgeOnline:true.

## Capabilities it proposed

### "When I say “mark this for later” during a meeting, use the pendant button and my Mac to save a useful breadcrumb: identify the calendar event, record the exact time, capture the active document or browser page, and put a short follow-up note in my workspace that I can ask for later."
- **useful because:** A button press is reliable when speech would interrupt a meeting. The result is more than a timestamp: it ties the moment to the meeting and the thing actually on screen, so “what was that thing I marked?” becomes answerable days later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to acknowledge the bookmark and answer retrieval questions; use a cheaper background model to correlate the calendar event, caption the captured UI metadata, and draft the follow-up note.
- **latency:** LED acknowledgement immediately; desktop capture under 2 seconds; note visible within 10 seconds. Retrieval should be one short spoken sentence.
- **cost:** About $0.01–$0.04 per bookmark depending on whether a small model summarizes the page; the dominant cost is optional screenshot/text summarization, not the calendar lookup.
- **security:** The active URL, window title, and possibly a redacted UI snapshot leave the Mac. Never capture password fields or arbitrary page bodies by default. Creating a note is low impact under the owner's stated policy, but sending mail or creating external tasks must remain a separate explicit action.
- **missing:** A relay endpoint that accepts offline_moment_bookmark events and joins them to a calendar event and Mac observation; A bounded Mac semantic capture returning document identity, selected text, and a redacted active-window snapshot; A durable meeting-breadcrumb record and retrieval index shared by relay and dashboard

### "Help me buy something online, but do all the research and fill the cart yourself; stop at the final purchase button and tell me the exact item, seller, total, shipping date, and return policy through the pendant. Only complete the purchase after I explicitly say “buy it.”"
- **useful because:** This turns a tedious logged-in browser task into a near one-sentence interaction without silently spending money. The Mac/browser can handle sessions and checkout details while the pendant is the low-friction confirmation surface.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheaper background model for comparison and policy extraction; use realtime only for the short spoken status and final confirmation exchange.
- **latency:** Research and cart staging in 30–90 seconds; confirmation summary in under 3 seconds once the checkout page is stable. Never auto-submit on a timeout or reconnect.
- **cost:** Roughly $0.02–$0.10 per purchase task, dominated by page reading across several product pages; browser navigation itself has no model token cost.
- **security:** The browser session may expose addresses and payment metadata to the planner. Redact card numbers and passwords from page extraction. The final purchase is an irreversible high-impact action and must require a fresh spoken confirmation tied to the displayed total; price, seller, or cart changes invalidate it. A browser disconnect must fail closed at the cart, not retry checkout.
- **missing:** A browser transaction state that fingerprints the cart contents and expires a confirmation; A final-submit guard in the browser harness that cannot be bypassed by a stale plan or reconnect; Structured extraction of total, seller, shipping, and return policy with redaction

### "When I say “save that claim,” take the sentence or selection I am looking at in Safari, preserve the exact quote, page title, URL, author and capture time, and append it as a cited evidence card to my workspace without switching me away from the page."
- **useful because:** It prevents the common failure where a saved link no longer tells me what mattered. The browser has the authenticated page and selection; the Mac can write a durable Markdown card; the pendant gives a fast voice trigger while I keep working.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use realtime only to resolve the short command and acknowledge it. Use a small background model only when the page has no selection and a sentence must be identified; deterministic DOM extraction handles the normal case.
- **latency:** Capture selection and URL in under 2 seconds; append the card in under 5 seconds. If no safe selection is available, say so rather than guessing silently.
- **cost:** Near-zero for selected-text capture; at most $0.005 for fallback sentence extraction. Storage and browser calls dominate latency, not inference.
- **security:** Authenticated page text can contain secrets or personal data. Default to the explicit selection only, redact password/credit-card fields, and store the source URL plus quote locally in ~/AI-Pendant-Workspace. Never send the whole page to the relay unless the owner explicitly asks.
- **missing:** A browser command for read-only selected-text, citation metadata, and DOM range capture; A Mac append-only evidence-card writer with hash and source metadata; A relay intent that binds the spoken phrase to the active browser session without using stale tab state

### "Take this multi-step desktop task overnight, keep a durable checkpoint after every file or browser milestone, and tell me on the pendant only when it finished, is blocked, or needs a decision; if the Mac restarts, resume without repeating completed work."
- **useful because:** Long research, exports, and file organization currently depend on one uninterrupted Mac-agent run. Durable checkpoints and atomic file staging would let the owner delegate genuinely long work without waking to duplicate files, half-written exports, or an unexplained timeout.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Use a cheap background model for planning and checkpoint reconciliation; use realtime only for an exception alert or the owner's resume/cancel command.
- **latency:** No interactive latency requirement; checkpoint each milestone within 2 seconds. Resume after a restart within 30 seconds. Pendant alerts should be one sentence and only on terminal state or a blocking decision.
- **cost:** Usually $0.02–$0.20 depending on research/browser pages; durable staging and receipt work is local. The main model cost is re-planning only after a failed or changed step.
- **security:** The job may touch logged-in browser data and local files. Persist only redacted plans, hashes, and receipts—not page secrets. A restart must not replay purchases, mail sends, deletes, or other irreversible steps; those remain blocked at a decision checkpoint. The owner can cancel from the pendant.
- **missing:** A relay scheduler/worker that keeps a job alive while the Mac is asleep or reconnecting; A resumable planner contract with idempotency keys and per-step completion receipts; A pendant-facing exception channel for blocked/decision states; A policy-aware replay classifier for irreversible actions

### "After you do something across my Mac and browser, let me ask the pendant “why did you do that?” and receive a concise causal explanation: what I asked, what you observed, which sources supported the choice, every action taken, and what can still be undone. Let me request a dry-run replay before repeating it."
- **useful because:** Today a receipt says that a job ran, but it does not give the owner a trustworthy, human-readable chain from request to observation to action across nodes. This would make automation inspectable after the fact without forcing the owner to read logs, and would expose stale or surprising browser decisions before they recur.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a small background model to assemble a redacted causal summary from structured events; use realtime only to answer the short spoken question. Deterministic replay checks should not consume a model call.
- **latency:** Answer an explanation query in under 3 seconds from stored events; generate a dry-run replay in under 10 seconds. If an event is missing, say exactly which link is missing rather than inventing rationale.
- **cost:** Under $0.02 per explanation in normal cases; storage/indexing dominates. Dry-run replay is mostly local planning and browser inspection.
- **security:** Receipts can contain private URLs, document names, and mail metadata. Store an owner-visible redacted causal graph, keep secrets out of model prompts, and require explicit confirmation before any replay that mutates the Mac or browser. An explanation must distinguish observed facts from model inference.
- **missing:** A cross-node event schema with immutable observation/action IDs and causal parent links; A relay endpoint that joins Mac job receipts, browser command results, and pendant intents into one redacted causal graph; A dry-run replay engine that verifies current state against the original observations before offering actions

### "When I bring the pendant close to my Mac, hand off the conversation and its working set automatically: show the relevant files and browser tabs on the Mac, switch the voice session to text, and keep the pendant as the remote control; when I walk away, lock the handoff and stop exposing the working set."
- **useful because:** The owner should not have to repeat context or hunt for the right tabs when moving between a wearable conversation and a desktop task. Proximity makes the handoff feel physical and can also close an exposed work context when the owner leaves.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only for the active conversation. A small background model can select the relevant working-set items from the session graph; proximity transitions and locking are deterministic.
- **latency:** Detect arrival/departure within 2 seconds; render the handoff in under 5 seconds. On link loss or uncertain proximity, fail closed for private content and leave the Mac unchanged.
- **cost:** Low ongoing model cost, roughly $0.01 per handoff for context selection; hardware and secure radio integration dominate.
- **security:** Proximity is not identity by itself. Require an authenticated pendant key plus proximity, encrypt the handoff, and avoid opening secrets or password managers automatically. Departure should revoke the desktop session token, but must not delete files or interrupt an in-progress safe job.
- **missing:** An authenticated proximity channel such as UWB/BLE ranging on the pendant and Mac-side agent; A relay session-transfer protocol with short-lived, revocable handoff tokens; A working-set manifest that maps a voice thread to specific Mac files and browser tabs; A local privacy policy for what may be revealed on arrival and what must remain confirmation-gated

### "Let me say “keep this on my Mac” or “you may use the cloud for this,” and have that choice travel with the task: prevent private text, screenshots, and browser data from crossing the pendant, relay, or model boundary unless the task's declared policy allows it, then show me a compact data-flow receipt."
- **useful because:** The owner currently has to trust that each surface will redact correctly. A task-level data boundary would let him use cloud reasoning when useful while keeping a document, meeting, or logged-in page local when it matters, with evidence of what actually crossed the boundary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic policy evaluation and redaction by default; use a cheap model only to explain a denied transfer. Realtime should never decide whether a payload is allowed to leave the device.
- **latency:** Policy decision under 100 ms before every cross-node transfer; redaction under 1 second for ordinary text and metadata. If classification is uncertain, keep data local and tell the owner.
- **cost:** Near-zero model cost for enforcement; local scanning and receipt storage dominate. Optional explanation is under $0.01 per denial.
- **security:** This is security-critical: policy enforcement must occur before serialization, not after a model call. Browser secrets, passwords, payment details, and raw microphone audio need hard-deny classes. The owner must be able to inspect and revoke a task policy, and a receipt must distinguish blocked, redacted, hashed, and transmitted fields.
- **missing:** A shared task data-label format and policy interpreter implemented in relay, Mac planner, and browser bridge; Preflight hooks that inspect/redact payloads before POST /pipeline, browser commands, or model requests; A local-only execution mode that can complete tasks without sending raw content to the relay; A tamper-evident, owner-readable data-flow receipt


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac is substantially more capable than the old inventory: AI Pendant Agent has Accessibility and Screen Recording, input posting is verified, Safari/browser bridge are online, relay and Mac bridge are reachable, and 20 apps are running. Recorded three new owner-facing capabilities: pendant-to-meeting breadcrumb capture (calendar + active document/page), citation-preserving browser claim capture, and durable overnight Mac work with checkpoint/resume and pendant exception alerts. A purchase assistant and bench health-check were deliberately not counted as new: they collided with existing backlog ideas.

**Biggest unknown:** The remaining high-value gaps are implementation seams rather than basic reach: typed browser selected-text/metadata capture, a bounded USB/UART diagnostic runner and parser for the already-accepted fixture, and a true resumable planner with idempotency and irreversible-step handling. The pending semantic-context request should not be re-asked this round.

