# Harness derivation — browser-extension — round 203

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep an eye on the authenticated sites I choose, and only interrupt me when something changed enough that I should act.”"
- **useful because:** This turns the browser's unique access into an always-on personal signal: Safari reads logged-in pages, relay compares and ranks changes, and the pendant delivers a short alert even when the Mac is not in front of the owner. A spoken follow-up can ask the Mac to prepare the next reversible step.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background scheduler/page watcher uses a cheaper model for extraction and diffing; relay-realtime handles only the short spoken alert and follow-up.
- **latency:** Polling can be hourly or site-configured; alert generation under 10 seconds after a detected change; voice response under 1 second after the owner asks.
- **cost:** Roughly $0.01–$0.08 per changed page depending on extraction length; unchanged pages should use hashes/DOM selectors and avoid model calls. Main cost is authenticated page extraction and change classification.
- **security:** Read only origins explicitly entered by the owner; do not invent a site list. Persist only short host-keyed claims under the existing 24-hour/200-character browser-fact limits, never HTML or screenshots. Alerts must omit categories configured as never-speak. No action should be executed from a change alone.
- **missing:** An owner-editable empty per-origin watch policy (selectors, cadence, extract/redact/never-store, may-speak/must-not-speak); A durable scheduler that invokes browser jobs while Safari is online; Change baselines and semantic diffing tied to existing browser provenance; A relay-to-offline-alert-inbox delivery path for queued notifications

### "“Read the page I’m looking at, give me the important parts through the pendant, and let me ask follow-up questions without copying the page into memory.”"
- **useful because:** No other node can reach Safari's existing sessions, and no other node is as convenient as the worn device for a hands-free follow-up. This makes arbitrary authenticated pages conversational instead of requiring the owner to bring the Mac into view.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** A background/local extractor first identifies headings, tables, and relevant claims; relay-realtime performs only the low-latency spoken summary and follow-up grounding.
- **latency:** Initial extraction under 5 seconds for a normal page; first spoken summary within 2 seconds of request; follow-ups under 1 second when the extracted capsule is cached in RAM.
- **cost:** About $0.01–$0.05 per page read; follow-ups are cheap while the ephemeral capsule is alive. Cost is dominated by sending page structure to the extractor, not audio.
- **security:** The active tab URL and page claims leave the Mac only for the requested interaction. Keep the page capsule ephemeral with an explicit expiry; save no page text, HTML, or screenshot. Apply the existing browser provenance and redaction machinery before speech. Navigation and clicks are separate commands and never implicit in a read.
- **missing:** A reliable active-tab/read-page command path (current browser action bridge can navigate, but active-tab discovery is incomplete); An ephemeral page-capsule store with automatic expiry and section-level citations; Pendant request/response correlation for “that page/that section” follow-ups

### "“Prepare this authenticated web form, tell me exactly what would be sent through the pendant, and submit it only when I explicitly say to.”"
- **useful because:** Forms are where browser access becomes practical action: the extension can use the owner's logged-in session, while the pendant provides a hands-free review of recipients, amounts, dates, and changed fields before an irreversible submit. The Mac can recover a draft if the browser disconnects.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Mac-planner/browser extraction handles field mapping and validation; relay-realtime is used only to read the compact diff and capture the owner's explicit submit instruction.
- **latency:** Fill and diff in under 10 seconds; spoken review under 3 seconds; after approval, submit and receipt in under 10 seconds.
- **cost:** Approximately $0.02–$0.10 per form depending on field count and visual ambiguity; most work is deterministic DOM extraction. Confirmation calls are short.
- **security:** Never infer values for high-impact fields; mark unknowns and show the exact destination, amount, attachments, and changed fields. Keep an undoable fill receipt and preserve provenance, but never persist passwords or page bodies. Explicit approval is required immediately before submit, and the system must show a post-submit receipt or recoverable failure.
- **missing:** A browser form planner that maps labels to fields and emits a compact before/after diff; A pendant-friendly review protocol supporting corrections by field name; A submit/receipt transaction wrapper with idempotency and undo for fills; Owner-configured per-origin field redaction rules, shipped empty

### "“When I’m comparing options on a logged-in website, tell me which choice fits my real schedule and constraints, then prepare that choice for me.”"
- **useful because:** Today the browser can see an authenticated page, but it cannot combine that view with the owner's local reality. This would let the owner make decisions hands-free: Safari supplies the actual available options, the Mac supplies calendar/files or other explicitly selected constraints, and the pendant gives a concise recommendation with the evidence before preparing anything.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → dashboard
- **model tier:** A background planner extracts structured options and checks deterministic constraints locally; use the realtime tier only to ask the owner a concise clarification and speak the recommendation.
- **latency:** Extract and compare in 10–20 seconds for a normal page; clarification and spoken answer under 2 seconds; preparation under 10 seconds after selection.
- **cost:** Approximately $0.03–$0.15 per comparison, dominated by structured extraction and visual interpretation of irregular option tables. Calendar/file constraint checks should be local and nearly free.
- **security:** The owner must explicitly choose which local sources are relevant for each task; never search all files by default. Send only the minimum page claims and constraint values to the planner, retain an evidence capsule rather than page text, and show source URLs and assumptions in the dashboard. Recommendations must not silently purchase, book, or submit anything.
- **missing:** A structured option-extraction contract that handles tables, cards, calendars, prices, eligibility rules, and visually rendered controls; A local constraint query that lets the owner name sources such as a date range or calendar, rather than granting unrestricted file search; A cross-surface evidence bundle linking each recommendation to page fields and local constraints; A pendant interaction for correcting one assumption (“not Friday”, “cheapest”, “include refundable only”)

### "“Check the account pages I name and tell me whether they disagree about my current details, then prepare a correction plan without changing anything.”"
- **useful because:** Different services often hold conflicting addresses, renewal dates, names, or status fields. Browser access can inspect the actual logged-in records, while the Mac can normalize the fields and the pendant can explain the conflict without forcing the owner to visit every site.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background extraction and deterministic field normalization use a cheaper model; realtime is reserved for the short spoken conflict report and owner corrections.
- **latency:** Compare 2–5 named origins in 30 seconds; spoken result under 3 seconds once the comparison is ready.
- **cost:** About $0.05–$0.25 per comparison set, mostly page extraction. Deterministic normalization and diffing should be local.
- **security:** Only inspect origins and fields explicitly named for that run. Never persist raw account values or page bodies; store only redacted conflict claims with short TTL and provenance. Preparing a correction plan must not mutate any account.
- **missing:** A cross-origin field normalization and conflict model; A per-run source/field selection UI and compact dashboard report; A redaction-aware evidence bundle that distinguishes exact values from merely missing fields; A safe handoff from comparison to an editable correction plan

### "“Create a dated proof of what this authenticated account page said when I checked it, so I can use it later if the site changes.”"
- **useful because:** For refunds, billing disputes, eligibility, and service failures, the owner needs more than a spoken summary: they need a compact, timestamped, verifiable record tied to the source page. The browser can reach the session; the Mac can seal a local evidence receipt; the pendant can later retrieve the claim without retaining an entire page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** A background extractor creates a structured claim set and cryptographic digest; realtime is only used if the owner asks for an audio explanation later.
- **latency:** Evidence receipt in under 10 seconds for a normal page; later retrieval under 1 second from local storage.
- **cost:** About $0.01–$0.06 per receipt. Hashing and local sealing are negligible; extraction is the main cost.
- **security:** The receipt must clearly distinguish a cryptographic capture of observed content from an official third-party attestation. Keep raw screenshots/page text encrypted locally only when the owner explicitly requests them; default storage is redacted claims, URL, timestamp, and digest with an expiry policy. Never expose session cookies or credentials.
- **missing:** An owner-visible evidence-receipt format with timestamp, origin, claim list, digest, and extraction limitations; Encrypted local retention and export of an explicitly requested receipt; A verification view that rechecks whether a later page still matches the captured digest; A pendant lookup command for receipt ID and claim


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-session lease and recovery protocol: when an authenticated Safari tab is the subject of an in-progress read or form draft, the extension periodically publishes a short-lived tab identity (device, tabId, origin, title hash, expiry) to the Mac agent; if the tab closes or Safari restarts, the Mac marks the job paused, reopens only the same origin/URL when the extension returns, and reconciles the DOM before allowing a draft to continue. Never copy cookies or page text into the lease.
- **owner gets:** A laptop sleep, Safari crash, or accidental tab close would no longer silently lose a carefully prepared authenticated task. The owner gets a clear pendant alert that work paused or resumed, rather than discovering later that a form was stale or an account page was missed.
- effort: Medium: extension heartbeat metadata, local-agent lease store, DOM/version reconciliation, and relay status/alert integration.  ·  risk: A reopened URL may have changed or may land on a login page; reconciliation must invalidate the draft rather than continue on a different page. Recover by discarding the draft and showing its last field diff. The lease contains origin metadata, so it needs short TTL and local-only default.
- cost: Negligible API cost; small local storage and heartbeat traffic. No new hardware.  ·  latency: Sub-second heartbeat handling; recovery adds 2–5 seconds for navigation and DOM reconciliation.
- security: Improves safety by preventing stale authenticated actions, but origin/title metadata is still sensitive. Encrypt or keep on Mac, expire in minutes, and never include cookies, tokens, HTML, or screenshots.
- depends on: A functioning browser command enqueue path through POST /execute; A durable undoable browser job/draft receipt (build on POST /prepare and GET /browser/provenance if present); Owner-configured empty per-origin policy rather than hardcoded origins; A pendant alert delivery path using offline_alert_inbox


## What it asked for

_Nothing._
