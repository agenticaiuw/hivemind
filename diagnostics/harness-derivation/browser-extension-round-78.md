# Harness derivation — browser-extension — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — At 2026-08-07T12:26Z /browser/status reports Safari absent/offline and home-chrome offline, with 6 pending browser commands; direct enqueue wrappers are still unimplemented, and a POST /execute browser_navigate probe did not return within 20s.
  - evidence: GET /browser/status 200: online=false, devices home-chrome only, pendingCommands=6; POST /execute browser_navigate probe timed out.

## Capabilities it proposed

### "If my browser disappears while you are working, pause safely, keep the exact place you were at, and continue automatically when it comes back—tell me only if you need me to reopen or choose a tab."
- **useful because:** Authenticated browser work is uniquely dependent on a live Safari extension. Today a dropped heartbeat can leave commands pending with no owner-visible explanation and risks losing task position. This makes long private-page tasks dependable without resending forms or repeating completed reads.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheaper background model for queue recovery, state reconciliation, and retry classification; use realtime only to explain a pause/resume to the owner over the pendant. Escalate to the stronger model only when the restored tab differs or page state conflicts.
- **latency:** Detect offline within one heartbeat interval; acknowledge the pause to the pendant in under 2 seconds. Resume within 10 seconds of a matching Safari session returning. Never retry a mutation automatically unless its receipt proves it was not delivered.
- **cost:** Usually <$0.01 per interruption (state-machine bookkeeping and a small background reconciliation call); realtime cost only when speaking an update. Dominant cost is re-reading a restored page, not the queue metadata.
- **security:** Persist only opaque session/tab identifiers, action hashes, and redacted page checkpoints; do not copy cookies or page secrets to the relay. A restored tab must match origin, session binding, and checkpoint fingerprint before resuming. Any uncertain click/type/submit is abandoned and surfaced as a draft with exact next action; no message, purchase, or form submission is auto-retried.
- **missing:** Durable browser task state machine with per-step completion receipts and a resumable checkpoint distinct from the current in-memory command queue; Heartbeat-loss event and reconnection hook from browserBridge to the job runner; Tab reattachment using origin/session identity plus semantic page fingerprint, with owner-facing recovery status; Idempotency classification for browser mutations and a replay-safe read-only retry policy; Pendant/relay notification for paused, resumed, and needs-owner states

### "Save the important part of the private page I’m looking at into my Mac project, with the source link and date, but keep the page text off the cloud and don’t send or submit anything."
- **useful because:** The browser is the only node with the owner’s authenticated view, while the Mac is the right place for durable local project files. This turns a fleeting logged-in tab into a searchable, cited local artifact without leaking private page contents to the relay or requiring the owner to copy and paste.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → unified
- **model tier:** Use a low-cost background model on the Mac to select and lightly structure the extracted section; use realtime only for the pendant confirmation. Keep raw page text on the Mac and avoid sending it to the relay model unless the owner explicitly asks for a spoken summary.
- **latency:** Capture visible/selected content in 2–5 seconds and write the local artifact within 5 seconds; spoken confirmation under 2 seconds after completion.
- **cost:** Near-zero model cost for deterministic extraction and Markdown writing; <$0.01 only when local structuring or deduplication needs a model. Network cost is metadata-only.
- **security:** The extension sends page text only over the authenticated local bridge to the Mac; relay receives project name, filename, and success/failure, not content. Redact password fields, payment data, hidden DOM, and cross-origin frames by default. Show the exact local path, source URL, extracted character count, and a short local preview before writing if the page contains sensitive fields. Never submit forms or alter the source page.
- **missing:** A browser action that extracts the owner-selected DOM range or visible semantic region with a stable source locator; A local-only handoff mode in browserBridge that routes extracted content directly to Mac storage without relay/model serialization; A project artifact writer with URL/title/timestamp/selection metadata and content hashing for deduplication; A pendant command/context signal identifying the active project and a concise completion receipt

### "Compare the charges on my logged-in banking, utility, and subscription pages, find duplicate or conflicting charges, and prepare a locally saved evidence packet and dispute drafts—but do not contact anyone or submit anything."
- **useful because:** No single node can do this today: Safari alone can see the private account pages, the Mac can correlate records and preserve an evidence packet, and the pendant can give the owner a concise explanation while they are away from the screen. It targets a concrete, high-value private-web task rather than another generic page summary.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a background model for table extraction, normalization, duplicate detection, and draft generation. Use the realtime tier only for the owner's spoken question or final short briefing; use the stronger model only to adjudicate ambiguous merchant/date/amount matches.
- **latency:** Collect and normalize each already-open authenticated page within 10 seconds per page, produce an initial discrepancy list within 60 seconds, and leave drafts/evidence on the Mac within 2 minutes. Do not hold the live voice turn open while the background job runs.
- **cost:** Roughly $0.03–$0.15 per run depending on page count and OCR/HTML volume; browser reads and model context dominate. Local hashing, PDF/HTML capture, and artifact writing are negligible.
- **security:** Raw account content stays on the Mac after extraction; relay receives only progress and a redacted discrepancy summary unless the owner explicitly asks for details. Never collect passwords, full account numbers, or hidden form fields. Store evidence encrypted locally with source URL, timestamp, and content hash. Drafts are review-only; no dispute submission, message sending, or account mutation occurs automatically.
- **missing:** A browser workflow that can read and label transaction rows across multiple authenticated origins while preserving each row's source tab and locator; A local normalization and matching worker for merchant, amount, currency, date, pending/posted state, and recurring-charge identity; An encrypted Mac evidence-packet artifact format linking each finding to a source snippet or screenshot hash and generation timestamp; A draft generator that can produce one dispute per selected finding without transmitting account secrets to the relay; A cross-origin task coordinator that keeps each site's session isolated and reports partial completion when one account is offline


## What it asked for

_Nothing._
## Its own summary

I established a live failure: Safari is currently offline, home-chrome has never connected, and six browser commands are pending. The granted browser enqueue tools are still unimplemented; a direct /execute browser_navigate attempt waited without a response. I recorded this and notified mac-planner. I proposed two new cross-surface capabilities: resumable authenticated browser work with safe pause/reconnect checkpoints, and local-only capture of private page content into the active Mac project with citations and no relay content leakage. What I still need is not owner context: I need a functioning enqueue/dispatch implementation or a returning Safari heartbeat, plus durable browser checkpoints and completion receipts so private tasks can resume without repeating clicks.

**Biggest unknown:** Whether the six pending commands are safe read-only navigations or include mutations; until the bridge returns and exposes typed command state, they should be treated as paused and not replayed.

