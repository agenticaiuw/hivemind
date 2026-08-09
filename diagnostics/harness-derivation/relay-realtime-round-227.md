# Harness derivation — relay-realtime — round 227

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch my authenticated work portal and tell me only when a genuinely high-priority item needs my attention."
- **useful because:** The owner can be away from the Mac and still receive a small, actionable alert instead of repeatedly opening a portal or receiving noisy page-change notifications. This is the single most useful missing end-to-end capability because it combines the worn front door, an already-authenticated browser session, always-awake relay logic, and the Mac/browser execution surface.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Use the realtime tier only to create or modify the watch and explain it; use a slower background model on each check to extract portal items, classify urgency against the owner's task/preference context, and produce a one-sentence alert. Use the browser harness for authenticated reads, never relay-side credentials.
- **latency:** Watch creation should answer in under 2 seconds. A scheduled check may take 10-30 seconds, and delivery should occur within one check interval; unchanged pages must produce no alert.
- **cost:** Approximately $0.01-$0.08 per check depending on page size and extraction model; browser execution and repeated authenticated page reads dominate, not the realtime turn.
- **security:** Portal content leaves the Mac browser only as extracted text and selected metadata. Persist only the minimal item title, deadline, source URL, and urgency rationale with a short TTL. Require explicit confirmation only when the owner asks the system to act on an item; reading and alerting are reversible and should not be gated.
- **missing:** A browser-harness watch adapter that can bind a watch to an authenticated tab/session and expose a stable extraction contract; A scheduler/worker that runs browser watches while the relay is awake and records failures distinctly from no-change; A priority extractor that uses scoped memory without leaking unrelated portal content; A durable delivery bridge from watch reports to the existing pendant alert inbox

### "Change that task while it is running: skip the email step, use the other folder, and keep going."
- **useful because:** Today a long Mac/browser delegation is effectively a black box: the owner must wait, cancel externally, or start a duplicate task. From the worn pendant they should be able to correct a live job and have the planner continue from its verified checkpoint, which is uniquely useful when they are away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime parses the correction and acknowledges it briefly. A slower planner validates the running job's checkpoint, rewrites only the remaining action graph, and hands execution back to the Mac agent; vision is used only for the current UI state when the checkpoint is not semantic.
- **latency:** Acknowledge the correction within 1 second. Produce a revised plan within 5 seconds, then continue without replaying completed actions. If no safe checkpoint exists, report that immediately rather than guessing.
- **cost:** $0.02-$0.10 per steering event; the dominant cost is re-planning with current Mac/browser state, while the realtime turn remains short.
- **security:** The correction must be bound to one authenticated job and one checkpoint to prevent cross-task edits. Persist the original and revised plans, skipped actions, and execution receipts. Do not silently broaden the task when the utterance is ambiguous; ask one concise clarification.
- **missing:** A job-control protocol with pause, inspect-checkpoint, patch-remaining-plan, resume, and abort operations; Planner checkpoints that record completed actions and side effects in an idempotent form; Mac/browser executors that can pause between actions and report a stable current state; Pendant routing that associates a spoken 'that task' with the active job and delivers the revised outcome

### "Compare the document in my authenticated browser portal with the matching file on my Mac and tell me exactly what differs."
- **useful because:** This solves a class of real tasks no single surface can do: the browser has the private source, the Mac has the local copy, and the pendant is the only practical way to ask while away. It returns a concise, evidence-backed discrepancy list instead of merely opening two locations for the owner.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime identifies the two sources and speaks only the result. Browser and Mac agents extract structured text locally; a cheaper comparison model aligns sections, dates, totals, and names, escalating to vision only for scanned or layout-dependent documents.
- **latency:** Under 3 seconds to acknowledge and locate both candidates; 15-45 seconds for extraction and comparison. If either source is unavailable, report which side failed rather than comparing stale content.
- **cost:** $0.03-$0.20 per comparison depending on OCR and document length; extraction/OCR dominates, with the relay using only a short spoken response.
- **security:** Keep raw portal and local documents on their originating surfaces where possible; send only normalized fields and hashes to the comparison step. Redact secrets and expire the comparison artifact. Never upload a private document to an untrusted external service without an explicit policy allowing it.
- **missing:** A cross-surface document locator that can pair a browser download/page with a Mac file using owner terms and recency; Structured extraction/OCR contracts from both browser and Mac agents; A comparison worker that emits field-level evidence and source links/paths; A relay response format that can speak a short discrepancy summary and provide details on request


## What it asked for

_Nothing._
## Its own summary

Discovery shows the core production tools exist (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate, read_web_page, relay_job_status). The devices list shows the Mac bridge and Safari browser are online; a mobile test device is offline. Among newly granted items, relay_event_push and relay_route_intent are schema-only and unresolved (they won’t execute). job_completion_watch resolves to GET /jobs/:jobId, so it can read job state, but it does not create a real watch/emitter yet. The Mac route table is rich and includes /plan, /execute, /jobs, /journal, /routines, and browser orchestration endpoints.

**Biggest unknown:** Whether the relay has any real, callable endpoint for delivering asynchronous notifications to the pendant/phone/dashboard after a voice session ends (a concrete push channel). If none exists, the system still needs an implemented event delivery path, not just a schema.

