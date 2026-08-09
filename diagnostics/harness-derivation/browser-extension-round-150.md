# Harness derivation — browser-extension — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Every morning, tell me only the things in my authenticated inbox and open web accounts that can cost me money, expire, or require a response today—and put the supporting evidence on my pendant if I ask.”"
- **useful because:** The live Gmail inbox visibly contains payment notices, account-verification deadlines, receipts, and automated failures mixed with thousands of bulk messages. This turns the browser’s unique access into a daily action list rather than another unread count, while keeping evidence available on demand.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background model for extraction/deduplication; realtime only for the owner’s follow-up question.
- **latency:** 5–10 minutes after scheduled scan; under 2 seconds for a pendant follow-up.
- **cost:** Low: one background extraction pass over changed snippets plus cheap embeddings/dedup; realtime cost only when questioned. Dominant cost is authenticated page extraction, not speech.
- **security:** Read only origins explicitly configured by the owner; default to empty per-origin rules and never persist raw page text. Store only redacted deadlines, sender, amount bucket, and source URL; pendant speaks category-safe summaries. Never send or submit mail/forms.
- **missing:** A durable authenticated page-watch scheduler that can invoke browser_read_page against selected tabs/origins; Owner-supplied per-origin read/extract/redact/never-store configuration; Delta storage and deadline/entity normalization across Gmail, browser tabs, and Mac calendar; A relay-to-offline_alert_inbox delivery adapter with source citations

### "“While I’m viewing a logged-in page, explain the exact next step I need to take, prepare the reversible parts across the browser and Mac, and give me a spoken checklist with a stop point before anything is sent.”"
- **useful because:** The extension can see sessions no other node can, while the Mac can prepare files/reminders and the pendant can make the result usable away from the screen. This is especially valuable for bills, account verification, returns, and event registrations where the owner wants progress without losing control of the final submission.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Realtime model for the short interactive explanation; cheaper background planner for extracting fields and generating reversible preparation steps.
- **latency:** Initial page interpretation under 8 seconds; each follow-up under 2 seconds.
- **cost:** Moderate: one vision/text interpretation per page plus a few local actions; speech dominates only for long checklists.
- **security:** Page contents remain local to the browser bridge except the minimum redacted fields needed for planning. Show a complete preview of any email/form text before submit; do not click final submit, purchase, send, or confirm. Maintain origin and tab affinity.
- **missing:** A browser action that returns structured field/section provenance rather than flattened text; Cross-surface draft handoff from browser to Mac reminders/files; A first-class irreversible-step detector that is observability-only and does not impose a policy gate; Pendant command to request the prepared checklist and evidence

### "“Watch the authenticated pages I choose for meaningful changes, compare each change to what was there before, and interrupt me only when the change affects money, access, travel, or a deadline—with a one-sentence reason and a link I can open.”"
- **useful because:** A logged-in browser tab can expose changes invisible to email or public search: billing dashboards, ticket portals, account security pages, and order status. Change-aware alerts avoid repeatedly reading whole pages and make the pendant a useful exception channel instead of a notification firehose.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap scheduled diff/parser first; realtime model only when the owner asks “what changed?” or the diff is ambiguous.
- **latency:** Poll on a configurable schedule (15 minutes to daily); alert generation under 30 seconds after a change; spoken answer under 2 seconds.
- **cost:** Low-to-moderate: DOM hashes and local extraction are cheap; model calls only for changed regions. Storage and polling dominate operational cost.
- **security:** No raw page snapshots by default; persist redacted structural fingerprints and extracted facts only. Per-origin allowlist and per-category speak/store controls are explicit owner configuration. URLs in alerts may reveal sensitive origin, so alerts should use opaque local references until opened.
- **missing:** Durable page-watch jobs bound to Safari tab/session identity and recoverable after tab reload; Region-level DOM diff with redaction before persistence; Offline alert inbox routing with deduplication and expiry; Dashboard controls for origin/category policy and watch pause

### "“For the logged-in services I choose, tell me when their fees, renewal terms, privacy settings, or account permissions materially change, explain the old-versus-new clause in plain English, and keep a private history I can query later.”"
- **useful because:** A page can change in ways that do not create an email or visible task: subscription price increases, auto-renewal language, data-sharing defaults, and newly granted permissions. The browser session is the only node that can inspect those authenticated account and consent pages; a semantic change history protects the owner from silently accepting altered terms.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap scheduled extraction and structural hashing first; background model compares only candidate policy/fee/permission clauses; realtime model answers the owner’s spoken “what changed?” query.
- **latency:** Daily or weekly scan, with a change explanation available within 30 seconds; spoken follow-up under 2 seconds from stored summaries.
- **cost:** Low-to-moderate: most scans use hashes and targeted extraction, while model cost is concentrated on changed clauses. Storage is small because only redacted clause versions and provenance are retained.
- **security:** This handles highly sensitive account and privacy settings. Ship with an empty origin allowlist and explicit per-origin rules for read, extract, redact, speak, and retain. Never retain whole pages or credentials; redact names, identifiers, and tokens before comparison. Do not accept terms or change settings automatically; expose a preview and link for the owner to act.
- **missing:** A semantic policy/fee/permission clause extractor with stable provenance selectors; Versioned, redacted clause storage with retention and deletion controls; A scheduler that can revisit authenticated browser origins despite tab reloads or login expiry; A pendant query path for “what changed at [service]?” and a dashboard timeline

### "“Audit the account and security settings on the authenticated services I select, find stale recovery methods, missing two-factor protection, or inconsistent personal details, and give me a prioritized fix list without changing anything.”"
- **useful because:** The browser can reach security pages and settings that email/search cannot. A periodic cross-service audit would catch an old phone number, weak recovery email, disabled MFA, or mismatched legal/billing details before an account lockout or failed transaction.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background model for field normalization and risk ranking; realtime only for the owner’s follow-up and guided step-by-step repair.
- **latency:** Weekly/monthly scan; results within 2 minutes of starting; spoken item explanation under 2 seconds.
- **cost:** Moderate: several authenticated page reads per origin and a normalization pass; no realtime cost unless the owner asks for guidance.
- **security:** Security settings and recovery identifiers are exceptionally sensitive. Use an explicit origin allowlist, redact actual phone/email values into masked fingerprints, never speak secrets aloud, never persist raw settings, and stop before every mutation. An owner-visible audit log must show exactly which origins were inspected.
- **missing:** Origin-specific security-page recipes and structured field extraction; Masked cross-origin identity/security comparison with no raw-value persistence; A scheduled audit runner and a pendant-safe priority summary; Guided browser navigation that can prepare but not submit setting changes

### "“When I am signed in to several services, build me a private, expiring ‘proof packet’ for a task—such as a return, reimbursement, travel claim, or support case—with the exact order number, dates, receipts, and links, then let me review it on my pendant before I share it.”"
- **useful because:** The browser can access receipts, order portals, tickets, and support pages behind separate logins. Today the owner must manually hunt across tabs and risk sending the wrong document. A time-limited, cited packet would reduce that work while preserving a deliberate human review before any upload or message.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background model for entity matching and packet assembly; realtime model only summarizes the packet or answers a review question.
- **latency:** Under 60 seconds for up to six already-open authenticated tabs; pendant review response under 2 seconds.
- **cost:** Moderate: multiple page extracts and attachment metadata; model cost is dominated by cross-page entity matching. Expiring storage limits ongoing cost.
- **security:** Packets may contain addresses, receipts, travel details, and identifiers. Keep them encrypted and short-lived, show every included source and field, redact by default, require explicit owner review before export, upload, email, or share, and auto-delete after expiry.
- **missing:** Cross-tab entity matching with citations and attachment collection; Encrypted expiring packet storage and a pendant review protocol; A human-readable review screen plus spoken inclusion/exclusion controls; Export handoff to browser/Mac that stops before irreversible submission


## Changes it proposed to its own stack

### `browser-harness` — Build an authenticated page-watch runner: persist an owner-configured origin/tab watch, periodically enqueue browser_read_page or browser_snapshot through POST /execute, compute redacted region-level diffs against the previous observation, classify only changed facts (deadline, charge, access/security, travel), and emit a deduplicated event with source tab and expiry to the relay/offline alert inbox. Pause safely when tab/session identity changes and resume only after re-binding.
- **owner gets:** The owner gets alerted about a changed logged-in billing, ticket, or account page without repeatedly reading the whole page or keeping Safari in front of him; the pendant can announce the one change that actually needs attention.
- effort: Medium-high: scheduler/job persistence, browser session affinity, DOM-region diffing, redaction, event routing, and a small dashboard policy editor.  ·  risk: Stale tabs, login expiry, and noisy DOM changes could create false alerts; recover by marking observations expired, showing the source URL/tab, deduplicating by semantic fingerprint, and providing a one-tap pause. Never perform a final submit or mutation.
- cost: Low polling and storage cost with cheap hashes; occasional model classification of changed regions is the dominant API cost.  ·  latency: 15-minute-to-daily configurable polling; typically under 30 seconds from detected change to alert.
- security: High-value authenticated data is touched. Keep raw snapshots ephemeral, redact before persistence, require explicit per-origin and per-category read/speak/store settings, and use opaque alert references rather than exposing sensitive URLs in spoken text.
- depends on: Owner supplies first origins and no-speak/no-store categories; A durable scheduler that can call POST /execute; A relay adapter to offline_alert_inbox

### `memory` — Add a redacted authenticated-policy ledger distinct from ordinary journal/capture: normalize fee, renewal, privacy, and permission clauses into versioned records with origin, account-scope label, effective date, source selector, semantic diff, confidence, and owner-configured retention. A scheduled browser job writes only changed clauses; relay and pendant queries retrieve the latest diff without exposing raw page text.
- **owner gets:** The owner can prove what a logged-in service said before it changed, understand a surprise charge or permission change, and ask the pendant for a concise explanation months later instead of searching old pages or emails.
- effort: High: clause extraction and selector stability, redaction, versioning, retention/deletion UI, and integration with authenticated browser scheduling.  ·  risk: Incorrect extraction could imply a change where none exists, or miss a subtle clause. Store source evidence capsules and confidence, label uncertain comparisons, allow re-check from the live page, and never take an acceptance action.
- cost: Small persistent metadata footprint; model cost only for candidate clause diffs, with occasional rechecks of ambiguous changes.  ·  latency: Scheduled scans can be slow; querying an already-recorded diff is near-instant. Live re-check may take several seconds.
- security: Sensitive authenticated policy data is retained. Encrypt ledger storage, default retention short, support per-origin never-store, redact identifiers before indexing, and keep raw page text ephemeral.
- depends on: An owner-provided authenticated-origin allowlist and retention policy; Durable browser scheduler with login-expiry handling; A structured clause extractor and provenance format; Relay/pendant query routing for ledger records


## What it asked for

_Nothing._
## Its own summary

Round 150 produced three new owner-facing capabilities and one concrete browser-harness change. I verified the real Safari extension is online with 9 tabs and successfully read the authenticated Gmail inbox through POST /execute; actionable examples include an API funding charge, an upcoming autopay, an expiring Wells Fargo verification, and a CI failure. The most valuable proposed capability is a cross-origin authenticated attention triage that filters logged-in pages and inbox changes down to money/access/travel/deadline items and delivers concise evidence to the pendant. I also proposed interactive reversible preparation with a spoken pre-submit checklist, and semantic authenticated page watches with redacted diffs and exception alerts. The browser watch runner was recorded as a browser-harness change.

**Biggest unknown:** I still need the owner’s explicit first 3–5 authenticated origins, categories never to speak, and categories never to persist. Technically, the system still needs durable tab/session-bound watch scheduling, region-level redacted diff persistence, structured page provenance, and a relay adapter into the accepted offline_alert_inbox. The granted browser wrapper remains ambiguous/unimplemented for list-tabs, but direct POST /execute is live and usable today.

