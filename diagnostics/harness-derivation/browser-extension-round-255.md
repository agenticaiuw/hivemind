# Harness derivation — browser-extension — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with one active tab, YouTube video “Max Hodak: Average Is Not Good Enough”; POST /execute successfully ran browser_list_tabs and browser_read_page, returning read-only receipts and an evidence capsule.
  - evidence: POST /execute 2026-08-09T03:29:45Z and 03:30:17Z; browser_read_page result included capsuleId evd_691badd4db5e.

## Capabilities it proposed

### "“I’m on a webpage with a form filled in. Before anything is sent, read me the fields and values that will be submitted, point out anything unusual, and let me approve or revise it from the pendant.”"
- **useful because:** This is the safest way to automate authenticated web work: Safari has the owner’s session and sees the real form, the relay can explain it, and the pendant gives a human-readable final review without exposing credentials to another surface. It catches wrong recipients, amounts, dates, and attachments at the last moment.
- **path:** browser → relay → pendant → mac-planner
- **model tier:** Realtime only for the short field-diff explanation; deterministic browser extraction and local policy do the rest.
- **latency:** 2–5 seconds to inspect and summarize; approval should remain pending until the owner responds. No submit occurs automatically.
- **cost:** ~$0.01–$0.05 per review, dominated by one short realtime summary; extraction and diff are local.
- **security:** The form values are sensitive and must stay in the live execution path, never browser memory. Show exact destination and high-impact fields on the pendant; submitting, sending, or purchasing still requires explicit owner approval. Redact secrets such as passwords and tokens. The owner’s per-origin policy remains an empty, inspectable configuration until supplied.
- **missing:** A browser action that returns structured form controls plus current values and submit target; A pending-approval object that can be resolved by a pendant button/voice response; A browser executor that can apply only approved field edits and then submit exactly the reviewed form

### "“Turn the video or article I’m looking at into a short, cited decision capsule: what it claims, what evidence supports it, what I should do next, and save it to my workspace so I can play it from the pendant later.”"
- **useful because:** The browser can reach authenticated transcripts, paywalled articles, and private dashboards that web search cannot. This turns a page the owner is already viewing into an actionable, provenance-backed note and an offline spoken capsule, rather than a disposable chat summary.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Use a cheaper background model for extraction and claim/evidence mapping; reserve realtime for a brief spoken handoff when the owner asks.
- **latency:** 15–60 seconds depending on page length; immediately acknowledge capture, then deliver the capsule asynchronously.
- **cost:** ~$0.03–$0.20 per capsule, dominated by transcript/article extraction and synthesis; browser reads and local note creation are cheap.
- **security:** Only capture the current tab and the requested scope. Persist claims and citations, not HTML, screenshots, or full page text; browser facts should retain the existing short TTL and host provenance. Never upload cookies or credentials. Require confirmation before sharing the capsule outside the Mac workspace.
- **missing:** Page-aware extraction for transcript/article sections and citations; A workspace writer that creates a durable note plus audio asset; A relay job that pushes the completed audio to offline_alert_inbox without blocking the conversation

### "“When my Mac is about to sleep or lose connectivity, preserve my authenticated Safari work so I can continue on the pendant or another Mac later: tell me which tabs are active, capture only the task state and safe return links, and restore the session when I’m back.”"
- **useful because:** A browser session is uniquely valuable because it contains logins no other node can reach, yet it currently disappears with sleep, reboot, or a disconnected bridge. This makes the wearable and relay a continuity layer: the owner gets a compact task handoff, not a stale screenshot or leaked page dump.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Deterministic tab/session state capture; a cheap background model may compress task labels. Realtime is only for the short spoken alert.
- **latency:** Capture in under 3 seconds on sleep/network-loss signal; restore in under 10 seconds when Safari returns.
- **cost:** Near-zero for state capture and links; <$0.01 if a model labels the task. Storage is small and TTL-bound.
- **security:** Persist origin, title, safe URL, and explicit task metadata only—not cookies, DOM, page text, or screenshots. Per-origin rules must be owner-configured and empty by default. Restoration must never submit forms or replay clicks; it only reopens tabs and reports what changed.
- **missing:** A Mac sleep/network-loss hook that invokes a browser checkpoint; A session checkpoint schema with redaction and expiry; A restore operation that safely reopens tabs on the registered Safari device and reports unavailable sessions

### "“Compare the two authenticated pages I have open, find contradictions in their dates, amounts, names, or status, and tell me exactly which page supports each side.”"
- **useful because:** People routinely cross-check a private dashboard against an invoice, booking, portal, or confirmation. Today the browser can read pages one at a time, but cannot produce a provenance-backed contradiction report across sessions. The pendant gets the discrepancy while the evidence remains on the Mac.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Cheap background extraction and deterministic field normalization; realtime only for the final short spoken discrepancy report.
- **latency:** Under 10 seconds for two ordinary pages; longer pages become an asynchronous job.
- **cost:** About $0.02–$0.10 per comparison, dominated by structured extraction and normalization.
- **security:** Read only the explicitly selected tabs. Keep raw page content transient; retain only short claims, source URLs, and element-level provenance under existing browser TTL rules. Never infer that a discrepancy is fraud without labeling it as an inconsistency.
- **missing:** A multi-tab browser read action with stable tab identity; Schema-aware field extraction and value/date/currency normalization; A provenance join that cites both page evidence capsules in the spoken result

### "“Use only the numbers visibly present on this authenticated page to calculate the answer I ask for, show me the formula and source fields on the pendant, and leave the page untouched.”"
- **useful because:** A private billing, analytics, or shopping page often contains the exact inputs needed for a decision, but copying them manually is error-prone. This would combine browser-only access with a transparent calculator and a wearable readback, without clicking or changing the site.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Deterministic extraction, unit normalization, and arithmetic; use a small model only to map the owner’s natural-language question to candidate fields, with a strict no-invention check.
- **latency:** 2–6 seconds for a normal page and calculation.
- **cost:** Under $0.02 per invocation; most work is local extraction and arithmetic.
- **security:** The result must include the exact source fields and URL, reject missing/ambiguous units, and say “insufficient data” rather than estimate. Do not persist raw values unless the owner explicitly asks for a finding. No browser mutation is permitted.
- **missing:** A visible-number extraction contract with units and selectors; A verifiable calculation engine that returns formula plus inputs; A pendant response format for formula/value readback


## Changes it proposed to its own stack

### `browser-harness` — Add a read-only “evidence lens” to the Safari extension: for every extracted claim, return the exact DOM accessibility node/visible label, a clipped surrounding phrase, tab identity, and content hash in the receipt, while keeping page text transient and applying existing redaction before it leaves the extension.
- **owner gets:** When the pendant tells the owner “the amount is $X” or “the deadline is Tuesday,” they can ask where it came from and receive a precise, trustworthy answer instead of a black-box summary. This makes private browser automation dependable for consequential decisions.
- effort: Medium: extension content-script extraction, receipt schema, redaction integration, and relay rendering.  ·  risk: Dynamic pages may move nodes or expose misleading labels; fall back to URL/title/hash and mark evidence stale. Never block ordinary reads if a selector cannot be stabilized.
- cost: Negligible runtime/API cost; modest implementation and testing cost.  ·  latency: Adds roughly 50–200 ms to page reads.
- security: Improves provenance but increases exposure of snippets; enforce existing secret/sensitive redaction and never persist full DOM or screenshots.
- depends on: A stable browser_read_page/inspect action contract; Existing browser provenance and evidence-capsule storage; Pendant playback of short cited source labels


## What it asked for

_Nothing._
## Its own summary

Confirmed live browser access: Safari has one active YouTube tab and POST /execute successfully performs browser_list_tabs and browser_read_page with evidence receipts. Recorded three new cross-surface capabilities: wearable form preflight before submission, cited page/video decision capsules saved for later playback, and sleep/network-loss authenticated-session continuity. The form preflight is the strongest near-term product because it safely combines browser session reach, Mac execution, relay explanation, and pendant approval.

**Biggest unknown:** The granted browser_read_or_navigate wrapper remains unresolved because browser_list_tabs is ambiguous with browser_list_sessions; direct POST /execute works. The missing product pieces are structured form extraction, pendant-resolvable approval, checkpoint/restore hooks, and durable audio-note generation. Owner still needs to supply any per-origin rules before private-site automation.

