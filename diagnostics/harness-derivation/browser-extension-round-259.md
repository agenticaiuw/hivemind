# Harness derivation — browser-extension — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with one authenticated-capable tab currently at YouTube (tabId 85, windowId 84); bridge heartbeat is fresh and pendingCommands=0. The nRF pendant remains offline.
  - evidence: GET /browser/status at 2026-08-09T03:41:50Z returned online=true, tabCount=1, tabUrl=https://www.youtube.com, tabId=85, pendingCommands=0.

## Capabilities it proposed

### "“Compare the total and delivery date on the order page I’m viewing with my calendar and reminders, and tell me if anything conflicts.”"
- **useful because:** This catches expensive or time-critical mistakes that no single surface can see: the browser has the authenticated order, while the Mac has the owner’s schedule. The pendant can give a short spoken verdict without requiring the owner to switch apps.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** background for extraction and normalization; realtime only for the final spoken answer
- **latency:** 10–20 seconds for a one-page read plus local calendar/reminder lookup; speak a provisional result if either source is slow
- **cost:** Low: one background extraction and a small structured comparison; dominated by authenticated page extraction, not voice-model tokens
- **security:** Do not persist order-page text or payment details. Retain only short-lived, host-keyed claims with URL provenance; redact account and card identifiers. Reading is automatic, but any calendar mutation would require a separate explicit request.
- **missing:** A cross-surface comparison job that accepts browser claims and a named local source (calendar/reminders); A normalized date/amount conflict schema and concise pendant speech renderer; An evidence-linked result that can show which page and event caused the conflict

### "“Make this page an accountable task: extract what I owe or need to do, remind me before the deadline, and keep checking the logged-in page until it’s resolved.”"
- **useful because:** The owner routinely encounters obligations in places that do not belong to Calendar or Mail. This turns a private web page into a durable, spoken commitment: Safari supplies the truth, the Mac schedules and rechecks it, the relay survives sleep, and the pendant surfaces the deadline when the owner is away from the screen.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** background model for extraction, deadline normalization, and page-diff classification; realtime model only when the owner asks for status or the deadline is urgent
- **latency:** Initial extraction under 15 seconds; scheduled checks can be minutes to hours apart; urgent alert delivery under 10 seconds after a detected change
- **cost:** Moderate background cost per check, dominated by authenticated browser sessions; low voice cost because the pendant receives a few structured claims rather than page text
- **security:** Persist only task fields (issuer, obligation, deadline, status, source host/URL), never page HTML or screenshots. Keep browser claims on a short TTL, encrypt the task record, and let the owner revoke the watch. Never click completion or submit a form without a fresh explicit command.
- **missing:** A durable obligation object linking a browser finding to a reminder and a page-watch; Semantic resolution criteria (what counts as paid, submitted, canceled, or complete) with a human-readable diff; A relay-to-pendant alert path that includes deadline urgency and a one-button 'read next action' response

### "“Finish the verification flow I’m looking at: read the one-time code or QR target from Safari, put it into the real iPhone app, and tell me whether it succeeded.”"
- **useful because:** Many services split work between an authenticated desktop page and a phone app. Today the owner must manually transcribe codes and navigate two screens; this combines the browser’s private session, Mac iPhone Mirroring, and the pendant’s result into one short interaction.
- **path:** browser → mac-planner → ios → relay → pendant
- **model tier:** realtime for interpreting the owner’s spoken intent and final status; background/local deterministic extraction for the code and verification-state checks
- **latency:** 15–30 seconds for a normal code handoff; stop and report if the page asks for a new credential, payment, or an approval not explicitly requested
- **cost:** Low to moderate: browser extraction plus a handful of iPhone UI actions; model cost is small if the code is parsed locally and the status is read from accessibility/UI text
- **security:** Treat codes as secrets: never persist them, never speak the full code aloud unless requested, and redact from receipts/logs. Require the owner’s explicit utterance for each session; stop before any purchase, account recovery, or permission grant. Capture only success/failure and a redacted destination.
- **missing:** A short-lived secret handoff channel from Safari extraction to the iPhone action runner; Cross-device transaction IDs and redacted receipts that correlate browser and iPhone state; A verification-state detector that can distinguish success, expired code, wrong code, and an unexpected high-impact prompt

### "“Audit the account data export I’m looking at: compare it with my last export, tell me what changed, and point out anything I should revoke or correct.”"
- **useful because:** An authenticated service can expose changes that are invisible in the Mac’s ordinary Mail, Calendar, or files. The browser can reach the private export page, the Mac can parse and diff the downloaded archive locally, and the pendant can give a short, actionable summary without uploading the export.
- **path:** browser → mac-planner → mac-vision → relay → pendant
- **model tier:** Background/local processing for archive parsing, schema-aware diffing, and sensitive-field classification; realtime only for the owner’s follow-up questions and the final spoken summary.
- **latency:** 30–90 seconds for a normal export; stream progress to the pendant and return a first change summary as soon as metadata is parsed.
- **cost:** Moderate local CPU and disk I/O; low API cost because raw exports stay on the Mac and only structured deltas reach the model.
- **security:** Exports may contain passwords, identifiers, health data, or private messages. Keep the archive local, use an encrypted temporary directory, never send raw rows or persist them after the diff, and speak only redacted categories and counts by default. Any revocation or correction must be a separate explicitly requested action.
- **missing:** A browser-to-local-download handoff that verifies origin and associates the file with the requested account; A local schema-aware diff engine with field-level redaction and deletion-on-completion; A revocation/correction candidate report that links each finding to its local file evidence without exposing the export contents

### "“Check the security activity for this account, explain any sign-in I don’t recognize, and prepare the exact session revocations for me to approve.”"
- **useful because:** The private security dashboard is often the only place showing account compromise. The browser reaches it behind the owner’s login, the Mac correlates device and time clues, and the pendant can deliver an urgent plain-language warning while stopping short of destructive revocation.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Background model for event normalization and anomaly grouping; realtime for the owner’s question and the concise urgent alert.
- **latency:** Under 20 seconds for the first security activity page; urgent unknown-login alerts should reach the pendant within 10 seconds of a scheduled check.
- **cost:** Low to moderate background cost per check; dominated by authenticated page reads, with tiny structured alert payloads.
- **security:** Security logs themselves reveal sensitive locations and devices. Retain only a short-lived redacted event fingerprint and source provenance; never speak a full IP, token, or recovery code by default. Stage revocations with target, reason, and expected consequence; do not click the final revoke control until explicitly approved.
- **missing:** A security-event extraction and deduplication recipe that handles common account dashboards without hardcoded origins; A redacted anomaly model using the owner’s known-device context without inventing a location allowlist; A staged multi-session revocation form that can be reviewed and then executed as one explicit transaction

### "“Show me every permission this site currently has, compare it with last time, and stage the least-disruptive way to remove anything unnecessary.”"
- **useful because:** Permission changes are buried in authenticated account settings and browser prompts, and the owner rarely knows what changed. Safari can inspect the private settings, the Mac can model consequences, and the pendant can summarize the tradeoff before any access is removed.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Background/local model for permission inventory, change detection, and dependency analysis; realtime only for explaining a proposed removal and answering follow-ups.
- **latency:** 15–30 seconds for one origin; a batch audit can run in the background and alert only on newly granted or elevated permissions.
- **cost:** Low for one origin, moderate for a batch; mostly browser reads and local comparison, with no need to transmit page bodies.
- **security:** Permission pages can contain account identifiers and security settings. Store only normalized permission names, levels, origin, timestamp, and provenance; never retain screenshots or raw settings text. Treat removal as a staged mutation and stop before applying it.
- **missing:** A normalized cross-browser permission vocabulary and dependency graph; A durable, privacy-bounded baseline for permission state with meaningful diffs; A reviewable mutation plan that can apply only selected removals and produce an undo receipt


## Changes it proposed to its own stack

### `integration` — Add a short-lived cross-device handoff transaction: Safari can publish one extracted, typed secret or non-secret token under a nonce; the iPhone action runner consumes it exactly once; the Mac agent records only a redacted outcome and the relay can announce success/failure to the pendant. Bind both sides to the active browser session and expire in 90 seconds.
- **owner gets:** The owner can complete split browser/phone verification flows without copying codes, while retaining a clear stop point when the flow becomes a login recovery, purchase, or permission grant.
- effort: Medium: browser extension result schema, local-agent transaction store, iPhone action adapter, and receipt/redaction plumbing.  ·  risk: A stale or misrouted code could be entered into the wrong app. Mitigate with origin/app fingerprints, one-time consumption, short expiry, and a visible spoken confirmation of destination before entry. Recovery is simply expiry and manual entry.
- cost: Negligible storage and API cost; one extra local transaction record per handoff.  ·  latency: Adds under 1 second for local handoff; verification remains bounded by the app/page.
- security: Improves security by preventing code persistence and transcript leakage, but creates a high-value transient secret path; keep it memory-only where possible and redact every receipt/log.
- depends on: A resolved browser_read_page or browser_inspect action path; An iOS action runner exposed through the Mac agent; Cross-surface transaction IDs and redacted execution receipts


## What it asked for

_Nothing._
## Its own summary

Discovered a live Safari bridge (one tab, tabId 85, YouTube, fresh heartbeat) and the expanded local-agent manifest, including browser jobs, cross-check, handle-this, evidence, forms, catch-up, and iOS-capable surfaces. Recorded three new cross-surface capabilities: compare authenticated orders against Calendar/reminders; convert a web obligation into a watched, deadline-backed task; and hand a one-time Safari verification code into the real iPhone. Also proposed the integration change that makes the third safe: a nonce-bound, one-use, redacted secret handoff. The strongest capability is accountable web obligations: it closes the gap between private portals and the owner’s actual commitments, with the pendant surfacing deadlines while away.

**Biggest unknown:** The browser is online and now has a tab, but every granted browser wrapper still resolves ambiguously (browser_list_tabs vs browser_list_sessions), so I cannot reliably invoke browser_read_page/inspect from this agent. What is still needed is one unambiguous, implemented read action using the system spelling browser_read_page (or a direct POST /execute schema I can call). Engineering also still needs the cross-surface obligation schema/page-watch linkage and the one-time browser-to-iPhone handoff; no further owner preference is required for these proposals.

