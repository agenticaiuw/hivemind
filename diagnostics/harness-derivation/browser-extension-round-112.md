# Harness derivation — browser-extension — round 112

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-bridge-health** — Live browser state is inconsistent: /browser/status reports only offline home-chrome, no tab, and 11 pending commands; /ops/status reports the same browser offline. Stored sessions still point to old Safari tab IDs (UTC clock and Selenium form), while /browser/inspections is empty. Treat queued processing work and stored tabs as orphaned until a fresh heartbeat, not as retryable live work.
  - evidence: GET /browser/status 200; GET /ops/status 200; GET /browser/sessions 200; GET /browser/inspections 200 in round 112

## Capabilities it proposed

### "If Safari disconnects while you are working, preserve the research and resume safely when it reconnects—without repeating clicks or silently losing what was already read."
- **useful because:** Today a stale bridge leaves 11 pending commands and sessions pointing at dead tab IDs, so the owner cannot tell whether work is lost, duplicated, or safe to resume. A resumable browser handoff would turn disconnects into a clear paused task: retain authenticated reads, invalidate unsafe mutations, and continue only from verified page state.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** background for checkpoint reconciliation and page-diff extraction; realtime only to announce a pause/resume result over the pendant
- **latency:** Checkpoint every completed browser step (<1 s local); on reconnect, revalidate the tab and resume within 5–15 s; never wait on realtime inference for queue safety
- **cost:** Low API cost: mostly local JSON/D1 state and browser extraction; one background model call only when a checkpoint must be semantically reconciled, typically <$0.02 per interrupted job
- **security:** Authenticated page text remains on the Mac/relay job store according to existing retention policy; checkpoints must redact passwords, tokens, and form secrets. Reads may be replayed only after URL/origin and tab identity are revalidated. Any send/submit/purchase step is invalidated on disconnect and requires a fresh owner review, with the exact pending payload shown.
- **missing:** A browser job state machine with per-step durable checkpoints and atomic completion markers; A stale-lease sweeper that expires processing commands and marks tab-bound sessions orphaned instead of retrying them; A reconnect handshake that reports extensionId, tabId, windowId, URL, and document fingerprint before resumption; A dashboard and pendant notification for paused, resumed, and abandoned browser work

### "Use the right logged-in tab for this task, and show me exactly which account and page you used before you take any action."
- **useful because:** The bridge can retain multiple authenticated sessions, but current state exposes stale tab IDs and no reliable live tab inventory. Selecting by verified origin, title, account label, and fresh document fingerprint prevents reading the wrong account and makes private-page answers auditable without asking the owner to manually switch tabs.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for tab/account disambiguation and extraction; realtime only for the owner's short spoken confirmation of the selected source
- **latency:** Inventory and fingerprint in 1–3 s; source brief in under 10 s; no model call for straightforward exact-origin matches
- **cost:** Usually <$0.01 per request; dominated by one small extraction/classification call when several tabs match
- **security:** Account identifiers and URLs are sensitive and must stay in the authenticated job record with short retention. Do not expose page contents until the selected tab is verified. Never infer an account from URL alone; show origin, title, last-seen time, and a short redacted excerpt. Destructive browser actions remain stopped before submission.
- **missing:** A real extension list-tabs/claim-tab heartbeat returning tab identity, origin, title, and account-safe metadata; A session selector that binds a job to an origin plus document fingerprint, not only a numeric tab ID; A redacted source receipt surfaced to the pendant and dashboard

### "Remember this private webpage for me: after I close Safari, let me ask the pendant about the exact facts I saw, with a freshness warning and a link to reopen the source."
- **useful because:** Authenticated browser access disappears when Safari disconnects or a tab closes, so private information cannot follow the owner into a later voice conversation. A selective, expiring page capsule would let the pendant answer from what was actually observed—without granting the relay ongoing access to the account—and make clear when the answer is stale or needs a live re-read.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Background model creates a compact fact capsule and redacts irrelevant page content; realtime model answers short follow-up questions by retrieving only matching capsule fields
- **latency:** Capture in 2–5 seconds after a page read; pendant answer under 2 seconds from local/relay storage; live refresh is a separate, explicit operation
- **cost:** Typically <$0.01 per saved page, dominated by one background extraction; storage is small encrypted JSON, with configurable expiry and automatic deletion
- **security:** Capsules contain private authenticated content and must be encrypted at rest with per-owner keys, field-level sensitivity labels, origin and capture timestamp, and a short TTL. Never retain passwords, payment data, hidden form fields, or full page HTML by default. Relay retrieval must return only requested fields, log access, and say when the source has not been revalidated. Reopening a source requires the browser session; no capsule may be used to perform an action.
- **missing:** An encrypted, field-selective private-page capsule store shared between the browser bridge and relay; A browser read result schema carrying canonical URL, capture time, selected facts, redaction metadata, and expiry; Pendant/relay retrieval by source and fact, with explicit stale-data language and delete/export controls; A reopen-source command that asks the browser extension to navigate only, never submit


## Changes it proposed to its own stack

### `browser-harness` — Add a local-first extraction mode to the Safari bridge: the extension computes selectors, text spans, and structured fields inside the browser, applies sensitivity redaction before transport, and sends the model only the requested fields plus short source hashes. Each result carries an origin, tab/document fingerprint, DOM locator, capture time, and a user-visible preview of exactly what left Safari. Fall back to full-page extraction only for an explicitly chosen task and record that exception.
- **owner gets:** The owner could ask about logged-in Gmail, GitHub, banking, or work pages without shipping an entire private page—including unrelated messages, tokens, or hidden fields—to the relay. Answers would remain useful while private browsing becomes materially safer and easier to audit.
- effort: Medium: extension content-script extraction and redaction, typed result schema, relay validation, and dashboard inspection UI; substantial test coverage across dynamic pages and iframes.  ·  risk: Poor selectors or dynamic DOMs could omit context and produce an incomplete answer. Recover by showing the extracted preview and offering a one-time full-page retry; never silently widen scope. Redaction bugs are mitigated by default-deny field classes and local tests against password/payment/hidden inputs.
- cost: Slightly lower model and bandwidth cost because only requested fields travel; modest extension CPU use during extraction and small encrypted audit records.  ·  latency: Adds roughly 100–500 ms locally; usually reduces network and model latency.
- security: Strongly improves data minimization, but the extension becomes security-critical. Use origin-bound code, signed extension updates, encrypted transport, short-lived result payloads, and never persist raw DOM by default.
- depends on: A functioning Safari extension command/result round trip; A typed browser result schema accepted by /execute and the relay; A dashboard view for redaction preview and extraction audit


## What it asked for

_Nothing._
## Its own summary

Round 112 produced two new browser proposals: resumable, checkpointed handoff after Safari disconnects (with stale-lease quarantine and mutation invalidation), and verified tab/account selection with redacted source receipts. Fresh evidence shows the bridge is genuinely unusable right now: /browser/status and /ops/status report offline, 11 pending commands remain, stored sessions reference dead tab IDs, and inspections are empty. I recorded this and alerted mac-planner.

**Biggest unknown:** The missing implementation is still the live Safari bridge path: a fresh extension heartbeat/tab inventory and a working command enqueue/result round trip. Until that exists, no authenticated page read or safe reconnect test can be performed; I do not need more owner context this round.

