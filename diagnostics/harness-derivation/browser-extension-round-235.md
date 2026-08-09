# Harness derivation — browser-extension — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 5 tabs; active tab is authenticated-capable USPS Tracking at https://tools.usps.com, and there are currently no browser jobs or pending commands.
  - evidence: GET /browser/status and GET /browser-jobs returned 200 at 2026-08-09T00:55Z.

## Capabilities it proposed

### "“What am I looking at?” (or “read the price/date/name here”) while I’m on a Safari page."
- **useful because:** This is the clearest browser-only superpower: the owner can point the pendant at an authenticated page without dictating a URL or touching the keyboard, and receive one short spoken answer. It joins live Safari session context, page extraction, relay reasoning, and the worn speaker; no other node can see the logged-in page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Realtime only for the one-sentence answer; browser extraction and redaction are deterministic, with a cheaper background model only if the page needs semantic selection.
- **latency:** 2–5 seconds from button/voice trigger to spoken answer; hard timeout at 10 seconds with a terse failure.
- **cost:** Usually one realtime turn plus a small extracted text payload; roughly $0.01–$0.05, dominated by model completion, not page access.
- **security:** The extension must identify the active tab and extract only the requested field or visible region, never upload HTML/screenshots by default. Apply existing browser finding limits (claim-only, host-keyed, 24-hour TTL, 200-character values); do not persist page text. Speaking sensitive values needs the owner's existing category policy. No irreversible browser action is allowed.
- **missing:** A reliable browser_read_current_page/current-tab-context action or event (the previously requested tool is still unavailable); A pendant button/voice event that asks the browser tier for the active-tab context; A small relay contract carrying tabId, visible selection/field label, and redacted extraction

### "“Prepare me for this meeting” while its invite or meeting page is open in Safari."
- **useful because:** The browser session may contain the authoritative agenda, private attendee list, dial-in details, or a shared doc that Calendar alone cannot see. This turns an authenticated tab into a useful, briefable meeting packet on the pendant instead of forcing the owner to hunt across tabs and apps.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for extraction and packet assembly; realtime only to answer a follow-up or speak the final 3-bullet brief.
- **latency:** 30 seconds for a first packet, with a 5-second spoken acknowledgment and asynchronous completion in the alert inbox.
- **cost:** One small background extraction/summarization job, about $0.01–$0.08; page text volume is the dominant variable, capped and chunked.
- **security:** Read-only and no sending/joining/clicking. Extract only agenda, time, attendees, decisions, and explicit prep links; retain short claims with URL/evidence and existing 24-hour browser TTL, never the page body. The packet must label browser-derived claims as unverified if the page changed.
- **missing:** A browser job that can bind the active authenticated tab to a meeting-prep request and follow only same-origin prep links; A cross-surface join between browser findings and existing meeting-prep/calendar data; A pendant spoken-status/alert payload for a packet that finishes after the owner walks away

### "“Tell me when this login stops working, and give me the exact page I need to fix it.”"
- **useful because:** Authenticated browser automation silently fails when a session expires, which is worse than doing nothing: the owner believes a watch or prep job ran. A session-health sentinel would detect login walls, MFA challenges, consent screens, and permission loss, then use the pendant's durable alert inbox to make the failure actionable even if the Mac is unattended.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic browser classifiers first; a cheap background model may classify an unfamiliar login/interstitial. Realtime is unnecessary except for a spoken urgent alert.
- **latency:** Check at job start and at most every 15 minutes while a watch is active; alert within 30 seconds of a detected failure.
- **cost:** Near-zero for DOM/status checks; occasional small classifier call, under $0.01 per check. Cost is dominated by polling frequency, so only active jobs are checked.
- **security:** Never capture or transmit passwords, OTPs, cookies, or page screenshots on a failure path. Report origin, failure class, timestamp, and a safe re-auth URL. Do not click MFA, accept consent, or submit credentials. Store only a short-lived health event, not page content.
- **missing:** A first-class browser session-health result with explicit states (authenticated, expired, MFA/consent required, blocked, unknown); A watch/job scheduler hook that marks a browser job stale rather than reporting success; A safe re-auth handoff that opens the origin and stops for the owner, plus a durable offline alert

### "“Does this shipment actually arrive today?” while USPS tracking, my order page, and my email are available."
- **useful because:** The owner should get a trustworthy answer from the intersection of private sources, not a guess from one tracking page: reconcile the carrier scan, the merchant promise, and the latest receipt or delay notice, then speak only the conclusion and the conflicting evidence. No single node can do this: Safari has the logged-in pages, the Mac has local mail/calendar context, the relay reasons, and the pendant makes the result available while away from the screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background extraction and deterministic date/status reconciliation; realtime only for a short spoken answer or follow-up.
- **latency:** Under 20 seconds for an initial answer, with a durable alert if one source is unavailable or contradictory.
- **cost:** About $0.02–$0.10 per check, dominated by extraction and synthesis; most comparisons should be rule-based.
- **security:** Read only. Do not persist order numbers, addresses, or page bodies; retain only a short expiring conclusion with per-source provenance. Never click delivery changes or contact the merchant/carrier without a separate request.
- **missing:** A cross-source evidence join that can correlate the same shipment without storing raw identifiers; A contradiction/date-normalization engine for carrier, merchant, and mail claims; A spoken result format that names uncertainty and source freshness

### "“Save me a way back to exactly this private workflow if the site changes or I get logged out.”"
- **useful because:** Today a browser session is effectively a fragile tab and a failed automation leaves the owner to reconstruct the task. The system should capture a credential-free, human-readable workflow checkpoint: origin, page purpose, non-secret selectors/landmarks, last successful step, and a short explanation of what remains. After a crash, redesign, or expired session, Safari can reopen the route and the pendant can say where to resume.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model to turn a successful run into a compact workflow checkpoint; deterministic browser replay and landmark matching; realtime only for spoken recovery instructions.
- **latency:** Checkpoint in under 5 seconds after a task; recovery attempt under 15 seconds, then alert with a precise resume link.
- **cost:** Roughly $0.01–$0.05 per checkpoint; replay is mostly local and deterministic.
- **security:** Never save cookies, passwords, OTPs, page text, or screenshots. Store only origin, route, redacted landmarks, and a short-lived provenance record. Replay must stop at login, MFA, consent, or any irreversible action.
- **missing:** A durable credential-free workflow-checkpoint schema and versioning; Browser landmark matching that survives DOM redesigns without clicking blindly; A recovery result that distinguishes resumed, logged out, changed page, and unsafe-to-continue

### "“Before I rely on this, check the private page against current public information and tell me what does not match.”"
- **useful because:** The owner often needs to know whether a logged-in notice, policy, price, deadline, or account status is still consistent with the outside world. Safari can read the private source nobody else can reach, web search can gather public sources, the relay can identify contradictions, and the pendant can speak a compact confidence-ranked answer. This is materially different from merely summarizing or watching one page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background research and deterministic claim extraction; use realtime only when the owner asks a follow-up.
- **latency:** 45 seconds for a first cross-check, with source-by-source progress available through the pendant; never block the owner’s conversation longer than 10 seconds before acknowledging.
- **cost:** About $0.05–$0.25 depending on public-source search breadth; the authenticated page extraction is cheap, while source comparison dominates.
- **security:** Send only the minimum claims needed to public research; redact names, account IDs, addresses, and tokens. Keep private-source claims short-lived and provenance-linked. Mark public sources by date and reputation; never turn a conflict into an automatic action or advice without uncertainty.
- **missing:** A privacy-preserving claim broker that separates private claims from public search queries; A contradiction and freshness evaluator with explicit confidence and dated citations; A spoken answer format that says which source disagrees and what the owner should verify manually


## What it asked for

_Nothing._
