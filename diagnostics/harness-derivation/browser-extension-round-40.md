# Harness derivation — browser-extension — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Live GET /browser/status currently reports online=false, only home-chrome with no tab, and pendingCommands=3; Safari is not presently registered in the live status despite earlier Safari heartbeat context.
  - evidence: probe_http GET /browser/status at 2026-08-07T10:14Z returned {online:false, devices:[home-chrome tabCount:null tabUrl:"" online:false], pendingCommands:3}.

## Capabilities it proposed

### "Every morning, check my logged-in Gmail, GitHub, and calendar web accounts, tell me only what is urgent, and prepare replies or actions without sending them."
- **useful because:** The owner has explicitly asked for Gmail and GitHub reads, but those requests have failed because no account registry, web urgency ranking, or draft store connects authenticated Safari pages to the existing brief. This would use browser-only sessions for private web data, Mac/relay for durable briefing and scheduling, and the pendant for a concise alert—something no single node can provide.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** background: deterministic page extraction and deduplication first, then a cheap background model (gpt-4.1-mini class) to rank urgency and compose drafts; escalate to realtime only if the owner asks a spoken follow-up.
- **latency:** Scheduled brief can take 30–90 seconds across three origins; pendant alert should arrive within 5 seconds after the aggregate is stored. Interactive drill-down should target under 10 seconds per origin.
- **cost:** Roughly 6–12k input tokens and 500–1.5k output tokens per morning depending on page size, dominated by authenticated page text; deterministic extraction, hashes, and unchanged-page skipping should make repeat days much cheaper.
- **security:** Private page text leaves Safari only to the local agent/relay model; store origin-scoped encrypted extracts and redact secrets, tokens, and message bodies from logs. Never auto-submit, send, delete, or purchase. Drafts must be explicitly marked unsent and actions shown to the owner before any irreversible step. Account registry must be opt-in per origin and support revoke.
- **missing:** An opt-in authenticated-origin/account registry with session health and last-success timestamps; Web-content urgency scoring with provenance, deduplication, and cross-origin ranking (existing notification triage only scores Mail.app envelopes); A durable encrypted drafts-and-proposed-actions store keyed to source URL/thread/issue; A scheduled browser fan-out runner that wakes Safari, retries offline devices, and reports partial results instead of leaving pending commands; A compact pendant notification payload plus a Mac/relay drill-down view with citations

### "When I ask, 'What am I on the hook for?', search my logged-in web pages and Mac documents, connect the same issue or person across them, and give me a dated list of commitments with the source for each one."
- **useful because:** Today the owner can read individual pages or receive separate briefs, but cannot obtain a trustworthy cross-surface commitment ledger. A private email thread, GitHub issue, and calendar event can describe one obligation; connecting them prevents missed promises without requiring the owner to remember where each detail lives.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Use deterministic extraction for dates, names, URLs, issue IDs, and message/thread identifiers; use a background model only to resolve entity matches and distinguish a promise from discussion. Realtime is needed only for the final spoken answer.
- **latency:** Under 90 seconds for an on-demand scan of configured origins; under 3 seconds to answer from the cached local ledger, with an explicit freshness timestamp and a background refresh option.
- **cost:** Initial scan roughly 8–20k input tokens and 1–3k output tokens, dominated by private page/document text; incremental scans should send only changed excerpts and cost roughly 1–4k tokens.
- **security:** Keep the canonical ledger encrypted on the Mac; send only the minimum commitment titles, dates, and citations to the relay/pendant. Preserve source permissions and allow per-origin exclusion. Do not infer sensitive obligations as facts without labeling uncertainty. Reading is allowed, but creating reminders or sending follow-ups remains a separate owner-directed action.
- **missing:** A cross-surface commitment schema with evidence spans, confidence, due date, owner, and last-seen timestamp; Entity and thread resolution across browser URLs, Mac files, calendar records, and mail metadata; An incremental private index with deletion/revocation and source-level access controls; A query route that returns compact cited commitments to the realtime pendant agent; Conflict handling when two sources disagree about a due date or responsibility


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-session watchdog and recovery loop: persist each command with origin, tab affinity, enqueue time, and expiry; when Safari is offline, stop accumulating blind pending commands, ask the Mac bridge to bring Safari to the requested origin (or report that no browser session is available), then resume only after a fresh extension heartbeat. Return per-origin partial receipts and automatically cancel expired commands.
- **owner gets:** The live browser status is currently offline with three pending commands, so requests can appear stuck and later execute against stale pages. The owner would instead get a clear 'Gmail unavailable' result, or have Safari recovered and the work continue safely.
- effort: Medium: browserBridge/browserSessions persistence, extension-heartbeat watchdog, Mac bridge callback, and tests for offline/reconnect/race cases.  ·  risk: A reconnect could open an unintended tab or replay a stale read. Mitigate with origin allowlists, command TTLs, idempotency keys, and never replaying mutations; recover by cancelling the job and showing its receipt.
- cost: Negligible storage and one background health request per minute; no extra model call unless a retry needs summarization.  ·  latency: Offline detection under 60 seconds; recovery adds roughly 2–10 seconds when the Mac bridge is online.
- security: Do not transmit cookies or credentials; only origin metadata crosses the bridge. Require explicit opt-in for origins and redact URLs containing query secrets.
- depends on: A durable browser job runner/receipt schema; A Mac bridge action to open or focus Safari; The extension heartbeat being authoritative for tab/session availability


## What it asked for

_Nothing._
