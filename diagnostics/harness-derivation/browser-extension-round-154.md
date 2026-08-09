# Harness derivation — browser-extension — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Read the page I’m on and tell me the three things that matter, then save the source and a one-sentence takeaway to my capture.""
- **useful because:** This is the shortest path from a private, already-authenticated Safari page to a durable spoken answer. It combines browser-only session access with relay summarization and Mac capture; public pages could be handled by search, but private dashboards, documents, and logged-in feeds cannot.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a cheap background summarizer for extraction and capture; reserve realtime only for the spoken answer or follow-up.
- **latency:** 3–8 seconds for read/extract/summarize; under 2 seconds to start speech after the result arrives.
- **cost:** About $0.01–$0.05 per invocation, dominated by page text sent to the summarizer; truncate to the visible article and never send passwords/forms.
- **security:** Page text leaves Safari for processing and may contain private data. Ship with an explicit per-origin read/extract/redact/never-store configuration, empty until the owner sets it; redact inputs and payment fields, and persist only the owner-approved takeaway plus URL. No submit or mutation is involved.
- **missing:** A reliable active-tab/read-page action in the browser tool manifest (the underlying POST /execute action already exists); An owner-editable per-origin extraction and retention policy UI; A capture writer that accepts browser provenance and redacted text

### ""When I’m checking out online, compare the final total and delivery date with the alternatives I already have open, fill the best option, and stop with a review of exactly what would be submitted.""
- **useful because:** It turns the browser’s unique access to logged-in carts and checkout pages into an actually useful buying assistant: it can see the real total, shipping, account-specific discounts, and delivery estimate, while the Mac/relay compare alternatives and the pendant gives a concise review before the irreversible step.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap structured extraction for totals and dates; background model for comparison; realtime only for the final spoken review.
- **latency:** 10–30 seconds across tabs, with immediate progress events; stop before submit and return the exact field/value diff.
- **cost:** Roughly $0.03–$0.15, dominated by multi-page extraction and comparison; use deterministic DOM extraction first.
- **security:** Checkout pages contain addresses, contact and payment metadata. Keep raw page snapshots local, redact payment numbers and secrets before model calls, and apply per-origin rules. Filling fields is reversible, but submitting orders, messages, or payment must never happen in this workflow.
- **missing:** A browser multi-tab extraction/field-fill orchestration layer; A structured checkout schema and diff renderer; A durable, owner-visible pending-submission review state

### ""Watch this private page for changes and tell me only when something materially changed; if the Mac is disconnected, queue the alert on my pendant.""
- **useful because:** This is the single most valuable browser feature: it makes authenticated pages useful while the owner is away, not only during a voice turn. The browser holds sessions nobody else can reach, the relay evaluates diffs, and the pendant remains the last-mile alert surface through a dropped Mac link.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use deterministic DOM/text hashing and a cheap background classifier for materiality; use realtime only if the owner asks for explanation.
- **latency:** Poll on a configurable cadence (for example 5–30 minutes); alert within one poll interval, with no model call when the page is unchanged.
- **cost:** Near-zero on unchanged polls; about $0.005–$0.03 per material change, dominated by changed-text classification and optional speech generation.
- **security:** Snapshots can expose private authenticated content. Store hashes and minimal redacted change excerpts by default, not full pages; per-origin policy must specify read/extract/redact/never-store. Alert text should be short and category-aware, and the owner must explicitly create each watch.
- **missing:** A durable authenticated page-watch scheduler and per-watch cadence; DOM-region selectors plus robust diffing across SPA navigation; Relay-to-pendant alert delivery integration for offline_alert_inbox

### ""Look at this private offer, invoice, or account notice, check its important claims against trustworthy public sources, and tell me what looks inconsistent or suspicious.""
- **useful because:** The browser can see the owner’s authenticated document while web search can independently check domains, dates, prices, policy language, and contact details. Neither surface alone can perform this private-context verification. The pendant delivers a concise warning without requiring the owner to read a long report.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use deterministic extraction and domain/date checks first, web_search for corroboration, and a background reasoning model for contradiction analysis. Realtime is only for the spoken conclusion.
- **latency:** 15–45 seconds for a full check; speak an immediate ‘checking’ status and return a short verdict plus evidence links.
- **cost:** Approximately $0.03–$0.20, dominated by public-source retrieval and reasoning over the private excerpt.
- **security:** Private page content is sensitive and may include account numbers. Extract only the relevant claim region, redact identifiers locally, and send public queries without private identifiers. Never label something fraud solely from model uncertainty; distinguish missing evidence from contradiction.
- **missing:** A private-excerpt plus public-evidence fan-out workflow; Claim extraction with confidence and contradiction citations; A spoken risk/verdict schema that preserves uncertainty

### ""Open this service’s privacy settings, show me what personal data it holds and the export or deletion choices, prepare the request, and give me a record of exactly what I would submit.""
- **useful because:** Account privacy controls are often buried behind existing logins and vary by service. The browser can reach them, the Mac can organize the inventory and save a local record, and the pendant can summarize the consequences. This gives the owner practical control over personal data without requiring the agent to submit an irreversible request.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap extraction model to classify settings and data categories, with realtime only for the owner’s questions about consequences.
- **latency:** 30–90 seconds per service, with incremental progress and a review artifact before any submission.
- **cost:** About $0.05–$0.30 per service, depending on the number of settings pages and documents; most work is browser navigation.
- **security:** This handles extremely sensitive account data and may expose deletion consequences. Store only the owner-approved inventory, redact identifiers, isolate each origin’s evidence, and stop before export download, deletion, or submission unless explicitly directed in a separate action.
- **missing:** A privacy-settings navigation and category extraction workflow; A structured consequence-aware review document; Encrypted local storage and lifecycle deletion for privacy evidence

### ""Use my logged-in sites to assemble a private account health report: unusual sign-ins, changed security settings, expiring payment methods, and pending verification steps, grouped by what I need to do today.""
- **useful because:** Security and account-maintenance signals are scattered across authenticated sites and unavailable to public search. The browser gathers the evidence, the Mac normalizes dates and urgency, the relay ranks actionability, and the pendant speaks only the few items that need attention.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Scheduled background extraction and deterministic ranking; no realtime model unless the owner asks for details.
- **latency:** A scheduled scan can take 1–3 minutes across configured origins; urgent alerts should arrive within the next polling interval.
- **cost:** Roughly $0.05–$0.40 per scan depending on the number of origins; unchanged pages should be skipped using local hashes.
- **security:** This creates a high-value security profile. Keep raw pages local, retain only structured findings and minimal redacted evidence, encrypt the report, and require explicit owner configuration of origins and scan cadence. Do not change settings or revoke sessions automatically.
- **missing:** A per-origin account-health adapter framework; A security-event normalization and deduplication layer; A scheduled browser scan runner with offline pendant alert delivery


## Changes it proposed to its own stack

### `browser-harness` — Add a browser_selection_clip action that reads only the current Safari selection, URL, title, and optional nearby heading, then emits a signed provenance capsule to the relay. A pendant button press can request “explain this” or “save this,” and the Mac writes the redacted clip to capture without sending the entire page.
- **owner gets:** The owner can highlight one confusing paragraph or number and ask about exactly that, instead of exposing or narrating an entire private page. It makes the pendant useful while browsing and keeps the data boundary narrow.
- effort: Medium: Safari extension selection API, one POST /execute action, relay capsule routing, and a small capture adapter.  ·  risk: Selection can include secrets accidentally; show the origin and character count in the result, enforce the configured per-origin policy, and provide a local undo/delete for the created capture. If the extension drops, fall back to URL-only context.
- cost: Low API cost; usually under $0.01 because clips are short. No hardware cost.  ·  latency: Sub-second capture; 1–3 seconds for an explanation.
- security: Improves privacy versus full-page reads, but selected text can still be sensitive. Default to never storing raw selection; retain only the owner-requested summary.
- depends on: Owner-configured per-origin policy; POST /execute browser action routing; POST /capture

### `browser-harness` — Add screenshot-region extraction for authenticated pages whose meaningful content is rendered in canvas, charts, PDFs, or inaccessible shadow DOM. The extension captures a bounded viewport/region and returns OCR plus a low-resolution evidence hash; the relay can answer questions or compare a later region without persisting the image.
- **owner gets:** Important private dashboards and receipts often have no useful DOM text. The owner gets answers from charts and scanned documents that the current page reader silently misses.
- effort: High: extension region capture, local OCR or vision handoff, region coordinate persistence, and redaction/evidence handling.  ·  risk: Screenshots can capture unrelated private content; require an explicit region or a page rule, cap dimensions, and discard pixels after OCR. If OCR confidence is low, say so instead of inventing values.
- cost: $0.02–$0.12 per vision/OCR invocation depending on resolution; local OCR can reduce cost. No hardware cost.  ·  latency: 2–8 seconds for OCR/vision.
- security: More sensitive than text extraction. Raw pixels should remain on the Mac, with only redacted OCR and an evidence hash sent upstream unless the owner explicitly asks for visual analysis.
- depends on: POST /execute; GET /browser/inspections; Per-origin redaction policy; A local OCR/vision action in the Mac agent

### `interaction` — Create a spoken browser evidence protocol: every answer derived from Safari carries origin, tab title, observed timestamp, and a compact evidence pointer; the pendant can say “source,” “show me,” or “forget that” to retrieve, open, or delete the exact evidence capsule. Keep the answer usable even when Safari is later closed.
- **owner gets:** Private-page answers become trustworthy and controllable: the owner can verify where a number came from, return to the same logged-in page, or erase the supporting content without hunting through logs.
- effort: Medium-high: provenance schema across browser results, relay speech intents, Mac evidence index, and pendant deletion/open commands.  ·  risk: A stale tab or changed page could make a pointer misleading. Include observed time and a freshness state; opening a private URL should target the existing Safari session, never copy credentials.
- cost: Low per-use cost; mostly metadata and a tiny index. No hardware cost.  ·  latency: Normal answers unchanged; source/forget commands under 2 seconds.
- security: Adds discoverable metadata about private browsing, so encrypt the local index, avoid storing raw content by default, and honor per-origin never-store settings.
- depends on: POST /execute browser result receipts; GET /browser/sessions; POST /capture and DELETE /capture/:key; Pendant spoken_status_interrupt


## What it asked for

_Nothing._
