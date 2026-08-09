# Harness derivation — browser-extension — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension-live** — Safari extension successfully bootstrapped a real tab and completed browser_navigate through POST /execute; tabId 1148327, URL https://www.google.com/. The previously observed logged-in OpenAI billing page was also readable in a browser_read_page receipt.
  - evidence: POST /execute response at 2026-08-08T01:44:18Z: browser_navigate success, extension commandId browser_684f9673-e284-44a3-a0b1-f4dd7b9d33d6, tabId 1148327; response logs include browser_read_page with authenticated billing content.

## Capabilities it proposed

### "“When I ask ‘what was that thing I saw yesterday?’, find the authenticated page I was looking at, reopen it, and remind me of the relevant detail.”"
- **useful because:** Browser sessions are the only place that can see the owner's logged-in history, while the relay and pendant can answer without making him search again. A time/origin query over browser evidence capsules turns a fleeting page visit into recoverable memory without persisting raw page text.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for indexing page metadata and evidence hashes; realtime only for the owner's spoken retrieval question
- **latency:** Under 3 seconds for a recent-page lookup; up to 10 seconds for semantic matching across older visits.
- **cost:** About $0.01–$0.05 per semantic retrieval, dominated by embedding/search and only occasionally a model summary; raw authenticated text should remain ephemeral on the Mac.
- **security:** Never persist page text by default. Store origin, title, timestamp, content hash, a short owner-configured excerpt class, and tab/session locator; require explicit per-origin rules for what may be retained. Reopen only the matched tab and do not expose secrets in the spoken response.
- **missing:** time-indexed browser evidence index with retention controls; browser session history event emitted to the relay; reopen-by-evidence locator action; owner-configurable per-origin retention policy

### "“Check this booking page against my calendar, tell me which available option actually works, and fill in that choice—but stop before the final confirmation.”"
- **useful because:** This is a genuinely multi-surface action: the browser has the authenticated booking session, the Mac has the private calendar, the planner resolves travel/time-zone conflicts, and the pendant gives a short decision-ready answer. It prevents the common failure of choosing an available slot that collides with something the browser cannot see.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for calendar normalization and candidate ranking; realtime only for ambiguity or a spoken follow-up
- **latency:** Read and compare in 5–15 seconds; filling the reversible fields should take under 5 seconds after the owner chooses.
- **cost:** Roughly $0.02–$0.10 per booking comparison, dominated by authenticated page extraction and calendar normalization; no cost for sites with unchanged cached structure.
- **security:** Per-origin rules must explicitly allow reading appointment options; calendar event titles should be reduced to busy/free windows before leaving the Mac. Never submit, send, or pay. Show the exact selected date/time and fields to the owner before the stopping point.
- **missing:** structured availability extraction across common booking widgets; calendar free-busy projection exposed to the planner; cross-origin timezone and travel-time resolver; reliable fill-only browser transaction mode with a submit boundary

### "“Find the charge I’m disputing, gather the matching receipt from my Mac, draft the dispute in the logged-in site, and read me the evidence before I submit.”"
- **useful because:** It combines the browser's authenticated financial session with local files the browser cannot reach and the pendant's immediate spoken review. The owner gets a prepared, evidence-backed form instead of manually hunting a transaction and receipt, while retaining the final irreversible action.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** background model for receipt/transaction matching and draft composition; realtime for the final spoken evidence review and questions
- **latency:** 30–60 seconds for a typical charge and local receipt search; draft should be ready in under 90 seconds.
- **cost:** Approximately $0.05–$0.25 per case, dominated by OCR/document matching and model synthesis; browser extraction and local search are otherwise free.
- **security:** Financial pages and receipts are highly sensitive. Keep documents on the Mac, send the relay only a minimized evidence summary, and make retention zero by default. Per-origin and per-category policy must be explicit. Fill and save a draft only; never click submit, upload, send, or authorize a refund without the owner.
- **missing:** local receipt-to-transaction matcher with document provenance; browser form schema/extraction for dispute workflows; cross-surface sensitive-data minimizer; durable draft checkpoint that survives a dropped browser link

### "“Before I accept this updated policy, compare it with the version I previously saw, tell me exactly what changed, and save a private record of my decision.”"
- **useful because:** The browser can reach authenticated policy, insurance, subscription, and workplace pages that public search cannot; the Mac can retain a local prior snapshot; the relay can compute a clause-level diff; and the pendant can deliver a concise spoken warning before the owner clicks accept. This protects the owner from silently changed terms rather than merely summarizing the current page.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background model for document normalization and clause diffing; realtime only for the owner's follow-up questions or spoken review.
- **latency:** 10–30 seconds for a normal policy page; under 5 seconds when a normalized prior version is already indexed.
- **cost:** Approximately $0.03–$0.20 per comparison, dominated by document extraction and clause-level model comparison; local hashing and storage are negligible.
- **security:** Policy pages may contain account identifiers or employment/financial details. Store the prior and new normalized documents locally with encryption and a configurable retention period; send the relay only the clauses needed for the spoken explanation. Never accept, sign, or check consent automatically. The decision record should contain timestamp, origin, version hashes, and the owner's explicit choice—not unnecessary page text.
- **missing:** versioned local policy vault with encrypted storage and retention controls; DOM/PDF normalization that preserves clause boundaries and headings; semantic clause-diff and materiality ranking; explicit decision-record event connected to the browser tab and owner action

### "“Show me what personal data this logged-in service holds about me, download the export to my Mac, and give me a spoken inventory without reading secrets aloud.”"
- **useful because:** Today the owner must navigate each service's privacy dashboard, understand opaque export formats, and inspect sensitive archives manually. The browser can operate inside the existing login, the Mac can download and locally classify the archive, and the pendant can provide a safe high-level inventory while leaving the raw export on-device.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background model for local archive parsing and category inventory; realtime only to answer the owner's spoken questions about the inventory.
- **latency:** Initiating the export in under 10 seconds; inventory after download in 1–3 minutes depending on archive size. Never block the browser while a provider prepares a delayed export.
- **cost:** About $0.05–$0.50 per archive, dominated by local OCR/structured parsing and one summary pass; storage and download bandwidth dominate large exports, not API calls.
- **security:** Raw exports must never leave the Mac or be persisted in relay memory. Use an encrypted, owner-visible directory, automatic expiry, category-level redaction, and a spoken response that excludes credentials, tokens, message bodies, and precise location unless explicitly requested. Requesting an export can notify the provider, so show the request details before initiating it.
- **missing:** provider-agnostic privacy-dashboard navigation recipes; local encrypted archive quarantine and expiry; archive parsers and category classifier; spoken redaction policy for personal-data inventories; long-running browser job that resumes when an export email or download becomes available

### "“Audit the security settings and active sessions in this logged-in account, tell me what is risky, and prepare the safest fixes without signing me out or changing anything yet.”"
- **useful because:** A browser session can see security controls and session lists that public tools cannot; the Mac planner can compare them with the owner's configured devices and known network context; the pendant can deliver an urgent, short risk report. The system would turn a buried security page into an actionable audit while avoiding accidental lockout.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for normalizing sessions, security settings, and recommended remediation; realtime for urgent alerts or owner questions.
- **latency:** Initial audit in 10–20 seconds; remediation plan in under 30 seconds. Changes remain staged until the owner explicitly requests them.
- **cost:** Approximately $0.03–$0.15 per account audit, dominated by structured extraction and risk ranking; recurring checks can use hashes and avoid model calls when unchanged.
- **security:** Security pages expose device names, IPs, recovery addresses, and sometimes secrets. Keep raw values local, speak only risk categories and masked identifiers, and make storage opt-in. Never revoke sessions, rotate credentials, alter recovery methods, or enable MFA automatically; show every proposed change and its lockout consequences first.
- **missing:** security-page adapters for session and MFA controls; local known-device/network inventory; risk rules for impossible travel, stale sessions, and weak recovery settings; staged remediation planner with dependency and lockout analysis; origin-specific emergency alert policy for truly suspicious changes


## Changes it proposed to its own stack

### `browser-harness` — Add a Safari page-context “Send to Pendant” action that captures the current tab's URL, title, selected text (or a bounded DOM excerpt), and a short-lived tab/session locator, then emits a typed browser_context event. The relay can route it to the pendant or Mac planner; the extension must return an event id and allow explicit discard before persistence.
- **owner gets:** The owner can point at a confusing paragraph, invoice line, or booking option and ask the pendant about exactly that material without copying it or dictating a URL. It makes the browser a second set of eyes rather than a separate app he has to operate.
- effort: Medium: Safari extension context-menu/UI, bounded extraction, POST /pipeline/events schema, and relay routing. One engineer can prototype a text-only version in days; robust selection and SPA handling take longer.  ·  risk: Selection may contain secrets or personal data, and stale tab locators may reopen the wrong state. Bound payload size, apply the owner's per-origin policy, expire events quickly, and show the captured title/selection in the extension before sending. Recovery is discard and re-read the live tab.
- cost: Negligible API cost for text-only forwarding; roughly $0.01–$0.05 if a model summarizes it. No hardware cost.  ·  latency: Context event should reach the relay in under 1 second; spoken answer in 2–5 seconds.
- security: High-value privacy boundary: default to ephemeral, minimized selection text; do not store full pages or screenshots unless the owner explicitly enables an origin.
- depends on: POST /pipeline/events; POST /pipeline/audio; POST /execute; GET /browser/status; per-origin retention/redaction configuration


## What it asked for

_Nothing._
