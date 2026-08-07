# Harness derivation — browser-extension — round 87

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live state** — No browser extension is online: home-chrome is offline with 0 tabs, while the browser session store still contains three stale Safari sessions and the command queue reports 7 pending commands.
  - evidence: GET /browser/status returned online:false, home-chrome tabCount:null and pendingCommands:7; GET /browser/sessions returned default/probe-form/probe-form2 with old tabIds and lastUsedAt timestamps.

## Capabilities it proposed

### "“If a logged-in website signs me out while you’re working, tell me immediately, pause safely, and let me resume the unfinished task after I sign back in.”"
- **useful because:** Authenticated browser work currently has stale sessions and the extension can disappear; without auth-state awareness, a workflow may fail ambiguously or leave a filled draft in an unknown state. This gives the owner a precise, spoken recovery path without exposing credentials or replaying actions into the wrong account.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard-ux → unified
- **model tier:** Use a cheap background classifier for page/auth-state detection and receipt generation; reserve realtime only for the pendant alert and the owner's follow-up conversation.
- **latency:** Detect on each browser result (under 200 ms locally) and deliver the pendant notification on the next relay poll/stream (typically under 2 s). Resume validation can take one browser round trip.
- **cost:** Near-zero incremental model cost for URL/status heuristics; occasional small classifier call only for ambiguous login pages. Dominant cost is one browser snapshot when a result indicates redirect or auth error.
- **security:** Never inspect, store, or transmit passwords, OTPs, cookies, or page form values from credential fields. Store only origin, account label if already known, auth-state reason, tab/session fingerprint, and a redacted draft receipt. Require the owner to perform reauthentication directly in Safari; resume must revalidate origin and tab before any action.
- **missing:** A browser auth-state detector recognizing login redirects, 401/403 pages, consent screens, and expired-session interstitials without reading secrets; A durable paused-job record that stores the next safe step and redacted draft state; A reconnect/resume handshake between the Safari extension and relay, including a user-visible 'reauthenticated' signal; A pendant notification/event type for browser authentication loss

### "“Compare the information on these two private sites and tell me exactly where they disagree—then prepare the safest next step, but do not change either site.”"
- **useful because:** People routinely reconcile a booking against a calendar, an invoice against an order portal, or a task board against an email. Today the browser can inspect one workflow at a time, but it cannot produce a structured, evidence-linked discrepancy report across authenticated origins while keeping both sites untouched.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Use a cheaper background model for extraction normalization and field-by-field comparison; use realtime only to answer the owner's spoken follow-up. Escalate to the expensive tier only when the two pages disagree on entity identity or semantics.
- **latency:** Collect two to four already-open/private pages within 10 seconds; provide a spoken discrepancy summary within 15 seconds. No mutation or submission occurs.
- **cost:** Usually a few small extraction/comparison calls; the dominant cost is authenticated page snapshots and context transfer, not realtime audio. Cache normalized field evidence for the duration of the task only.
- **security:** Keep raw private page text on the Mac where possible; send the relay only redacted fields, source URLs, timestamps, and short evidence snippets. Enforce origin/session binding so data from unrelated accounts cannot be silently joined. Never infer or display credentials, tokens, or sensitive form fields unless explicitly requested.
- **missing:** A cross-origin comparison job primitive with an explicit set of source tabs and a user-supplied comparison key (for example reservation number or invoice ID); A schema for normalized private-page facts with source locator, timestamp, confidence, and sensitivity labels; A reconciliation report that cites both source tabs and preserves the untouched before-state; A planner handoff that turns discrepancies into review-only next steps without invoking browser mutations


## Changes it proposed to its own stack

### `browser-harness` — Implement an authenticated-session sentinel between browser results and job receipts. For every browser result, classify only navigation metadata/status/title and non-sensitive DOM markers for signed-out states (login redirect, 401/403, expired-session interstitial, consent wall). On detection, atomically pause the job at the next action, emit a redacted auth_lost event to the relay, and persist a resumable checkpoint. After the extension reports the same origin and a fresh tab fingerprint, require a new browser_snapshot and mark the checkpoint revalidated before continuing; never replay the pre-auth action automatically.
- **owner gets:** A private-site task stops clearly at the moment Safari logs out instead of failing mysteriously or continuing against a login page. The pendant says which site needs attention, and after the owner signs in they can continue without losing the prepared, unsent work.
- effort: Medium: detector rules plus a small site-agnostic marker schema, atomic job pause/checkpoint state, relay event plumbing, and resume tests across redirects and tab replacement.  ·  risk: Some sites use unusual login pages and may cause false pauses; recovery is an explicit 'resume after snapshot' action and a per-origin rule override. False negatives are limited by refusing to continue when the expected page role does not match the checkpoint.
- cost: Minimal storage and relay traffic; mostly local metadata. One extra snapshot on reauthentication; no continuous model call required.  ·  latency: Sub-200 ms metadata check per browser result; one extra browser round trip only when resuming.
- security: Reduces credential/session confusion. Credentials, cookies, OTPs, and input values remain inside Safari; logs contain only origin, redacted reason, and fingerprints.
- depends on: GET /browser/sessions and POST /browser/sessions for session identity; GET /browser/poll and POST /browser/result/:commandId for extension exchange; GET /jobs/:jobId and GET /jobs/:jobId/receipts for durable checkpoint/receipt integration; POST /pipeline/events for pendant-visible auth_lost notifications

### `context` — Add a privacy-scoped cross-origin fact joiner for browser research. It accepts only an explicit comparison key and a bounded list of tab/session IDs, extracts typed facts locally from each page, normalizes dates, amounts, statuses, and identifiers, and emits a discrepancy graph whose every edge cites origin, tab, timestamp, locator, confidence, and sensitivity. The joiner must reject implicit joins across origins, expire its scratch facts after the job, and hand only the redacted discrepancy graph to relay speech and the review-only planner.
- **owner gets:** The owner can ask whether two private systems agree and get an answer they can verify, without dumping whole logged-in pages into cloud context or risking an accidental edit. This turns fragmented private browser access into a trustworthy reconciliation tool.
- effort: Medium-high: typed extraction contracts, local normalization and entity matching, provenance graph, sensitivity-aware projection, and integration tests for mismatched reservations/invoices/calendar entries.  ·  risk: Ambiguous matches could produce a false discrepancy or miss one. Show candidate matches and confidence, retain source citations locally for review, and never create an action plan when identity confidence is below threshold.
- cost: Small local storage footprint; model cost is limited to normalization and ambiguous matching. Cloud payloads are smaller because only typed facts and evidence hashes leave the Mac.  ·  latency: Adds roughly 2–8 seconds for parallel extraction and comparison; no mutation latency because this is review-only.
- security: Strongly reduces cross-account leakage by requiring explicit tabs and comparison keys, origin-scoped extraction, sensitivity labels, short TTL scratch storage, and redacted relay projection.
- depends on: Browser session records from GET /browser/sessions and POST /browser/sessions; Browser execution/result exchange through POST /execute, GET /browser/poll, and POST /browser/result/:commandId; Research briefing persistence via POST /research and GET /research/briefings/:id; Pendant delivery through POST /pipeline/events


## What it asked for

_Nothing._
## Its own summary

Fresh discovery shows the browser tier is offline (home-chrome is the only registered device, with zero tabs), while three stale Safari sessions remain in storage and 7 browser commands are pending. I recorded this finding and sent it to mac-planner. I proposed and recorded a new capability/change: detect authenticated-session loss, pause browser jobs safely, notify the pendant with a redacted reason, and resume only after the owner reauthenticates and a fresh snapshot validates the origin/tab. This is distinct from generic page watching or queue durability.

**Biggest unknown:** The actual Safari extension is not currently heartbeating, so I cannot verify auth-loss detection or resume behavior against a live authenticated page.

