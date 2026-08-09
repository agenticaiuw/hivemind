# Harness derivation — browser-extension — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online and currently reports 2 tabs; active tabId 3186198 is YouTube (“Max Hodak: Average Is Not Good Enough - YouTube”), with no pending commands. This supersedes the earlier tabCount=0 observation.
  - evidence: GET /browser/status returned online:true, tabCount:2, tabId:3186198, tabUrl:https://www.youtube.com, pendingCommands:0 at 2026-08-09T00:33:30Z.

## Capabilities it proposed

### "“What on my logged-in sites actually needs my attention?”"
- **useful because:** This would turn the pendant into an always-available authenticated triage surface: the relay asks Safari to inspect only owner-configured origins, the browser extracts short claims, Mac-planner ranks urgency, and the pendant speaks one sentence or queues it in offline_alert_inbox. Unlike public search, it reaches sessions only Safari has and produces an actionable answer without reading whole pages aloud.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use the realtime tier only for the owner’s short voice request and final one-sentence rendering; use a cheaper background model for per-page extraction and urgency ranking, with deterministic rules first.
- **latency:** 15–30 seconds for an on-demand triage; background watches can run on a schedule and alert only on a material change.
- **cost:** Roughly $0.01–$0.08 per run depending on number of pages and extraction calls; browser navigation and deterministic ranking dominate latency, not tokens.
- **security:** Ship with an empty per-origin configuration. The owner later supplies origins and read/extract/redact/never-store rules. Persist only short host-keyed claims under the existing 24-hour/200-character browser-fact limits; never persist HTML, screenshots, or page text. No submit/click mutation in triage.
- **missing:** A browser watcher/orchestrator that can iterate the owner’s explicit origin config and normalize page claims; A material-change/deduplication event that can push a finding to the pendant; A small dashboard editor for origin and spoken-category rules; End-to-end test fixtures for authenticated pages without storing their contents

### "“Fill this form with the details we discussed, but don’t send it yet.” Then: “Show me exactly what will be sent.”"
- **useful because:** The browser can use the owner’s authenticated session and fill a tedious form, while the pendant is the second pair of eyes that surfaces the exact recipient, amount, attachments, and changed fields. It makes high-value browser automation practical without silently sending mail, buying, or submitting anything.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use the background/local planner for DOM discovery and reversible field filling; use realtime only to summarize the proposed payload and answer the owner’s approval question. A deterministic field diff should be shown before any model prose.
- **latency:** Under 20 seconds to fill a short form; under 5 seconds to produce the payload diff after the owner asks.
- **cost:** About $0.01–$0.05 per form, mostly local planner/model extraction; browser commands and the final short spoken summary are inexpensive.
- **security:** Never submit on the fill operation. Show origin, target action, all non-empty fields, and any attachment/file names. Approval must be explicit and scoped to the exact page state and payload hash; stale or changed DOM invalidates it. Do not store form contents or screenshots beyond the existing provenance/undo record.
- **missing:** A page-state hash and structured field-diff result from browser actions; A scoped approval token that binds /approve to one browser command and payload hash; A browser submit action that is disabled until that token is consumed; A pendant-friendly confirmation phrase and timeout/review UI

### "“Read me the important parts of the page I’m looking at, and bookmark the exact point I ask about.”"
- **useful because:** The owner can be away from the Mac while Safari holds a page or video. The browser extracts headings/transcript/visible context, the model produces a short spoken answer, and the pendant’s existing moment bookmark records a page URL plus a compact claim rather than page text. This is a distinct, immediate conversational bridge rather than a scheduled watch.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime model handles the owner’s spoken question and a short answer; use a cheaper extraction model or deterministic reader mode for page structure/transcripts. Do not send screenshots unless extraction fails and the owner asks for visual interpretation.
- **latency:** 3–8 seconds for visible-page extraction and a one-sentence answer; bookmark acknowledgement under 2 seconds.
- **cost:** Approximately $0.005–$0.03 per page question, with token cost proportional to extracted headings/transcript snippets rather than the page body.
- **security:** Only target the explicitly active Safari tab and report its origin/title before reading. Respect the existing browser retention rule: store at most a short claim with URL and evidence capsule, 24-hour TTL, 200-character cap; never store page HTML or screenshots. Bookmarking must be opt-in per utterance.
- **missing:** A reliable active-tab/read-page command that returns structured visible text and URL in one result; A transcript/reader extraction fallback for pages that expose no useful DOM text; A bookmark payload joining URL, content section or media timestamp, and the owner’s question; A compact pendant prompt/result protocol for “about this” follow-up questions

### "“While this web meeting is open, keep a private rolling index of decisions, questions, and commitments. If I ask the pendant ‘what did we decide about X?’, answer from the meeting and show me the exact source moment.”"
- **useful because:** This gives the owner a wearable memory for authenticated browser meetings without requiring him to take notes or interrupt the call. Safari can read captions or meeting notes that only the logged-in browser can access; the relay answers short spoken follow-ups; the Mac stores only structured decisions and timestamps, not a transcript.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background extraction model continuously on caption deltas, with deterministic deduplication and speaker/time indexing. Use the realtime tier only for the owner’s follow-up question and concise answer.
- **latency:** Index new caption material within 5–10 seconds; answer a follow-up in under 4 seconds.
- **cost:** Approximately $0.02–$0.15 per meeting hour depending on caption volume and extraction frequency; the dominant cost is rolling caption summarization.
- **security:** The feature must be explicitly started and visibly show recording/indexing state. Default to ephemeral meeting memory with automatic deletion after the session; persist only owner-marked decisions. Never capture microphone audio or unrelated tabs. Source moments should be returned as timestamps/short claims, not transcript dumps.
- **missing:** A browser caption-delta reader that can follow a live authenticated meeting tab without repeatedly scraping the entire page; An ephemeral, session-scoped meeting index with explicit start/stop and automatic expiry; A source-moment protocol that links each extracted decision to a timestamp and tab state; A pendant command for starting, stopping, and asking about the active meeting

### "“Compare these two logged-in pages and tell me what doesn’t match.”"
- **useful because:** The owner can have Safari compare information that no public search can reach—for example, a provider’s invoice against a portal status, or a reservation against a confirmation page—and receive only the discrepancies, with the source tab for each claim. This turns private browser access into verification rather than simple reading.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a background/local model to extract normalized fields from each explicitly selected tab, then deterministic comparison for dates, amounts, names, and statuses. Realtime is used only to explain the resulting differences aloud.
- **latency:** 20–45 seconds for two pages, including navigation/read extraction; under 5 seconds for a follow-up about one discrepancy.
- **cost:** About $0.02–$0.10 per comparison, dominated by extracting two page representations; deterministic diffing keeps reasoning cost low.
- **security:** Require the owner to identify both tabs or confirm the proposed pair before reading. Keep source URLs and short field claims only; never persist page bodies, credentials, or screenshots. Redact account numbers and unrelated personal fields before the pendant speaks. Do not click or submit.
- **missing:** A two-tab selection protocol reachable from a pendant request; A schema for normalized private-page fields with provenance per field; A deterministic discrepancy engine handling currency, dates, status synonyms, and stale pages; A spoken result format that names the two origins and reads only material differences

### "“Describe the chart or dashboard in my logged-in browser, and tell me what changed since the last time I checked it.”"
- **useful because:** Many important private pages communicate through charts, color, and layout rather than readable text. The browser can access the authenticated dashboard, a vision pass can interpret the current visual state, and the pendant can deliver a compact trend plus a spoken explanation without requiring the owner to sit at the Mac.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Use mac-vision or a cheaper vision model for chart/table interpretation and change detection; use realtime only to answer the owner’s follow-up in one short spoken sentence.
- **latency:** 10–25 seconds for the first chart read; 5–10 seconds for comparison against a retained structural snapshot.
- **cost:** Approximately $0.03–$0.20 per request, dominated by image/vision inference. Avoid repeated full screenshots by hashing regions and sending only changed panels.
- **security:** Require the owner to name or confirm the active tab. Redact account identifiers and unrelated dashboard panels before vision processing. Retain only normalized metrics and a short provenance claim, never screenshots by default. Treat visual OCR as uncertain and say when a value cannot be read confidently.
- **missing:** A browser snapshot result that preserves viewport and chart-region identity; A chart/table extraction schema with confidence and units; A privacy-preserving structural snapshot diff that can compare dashboard states without retaining images; A spoken uncertainty and citation format for visual claims


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface “active page capsule” protocol: Safari returns {tabId, origin, title, selected/visible text blocks, media timestamp, and a short-lived state hash}; relay binds the capsule to the owner’s next pendant question, and the browser refuses to answer against a different tab or changed state. The capsule is ephemeral unless the owner explicitly bookmarks a claim.
- **owner gets:** The owner can say “what does this page mean?” or “is this the thing I was looking at?” while wearing the pendant and get an answer grounded in the exact Safari tab, rather than an answer accidentally based on another tab or stale page.
- effort: Medium: extension result schema, relay correlation, extraction fallback, and a small state-change test matrix.  ·  risk: A tab can navigate between read and answer, producing a stale interpretation. Surface the title/origin and invalidate on state-hash change; recover by asking the browser for a fresh capsule. Never silently fall back to another tab.
- cost: Low API cost; extraction payload is capped and avoids screenshots. No hardware cost.  ·  latency: Adds roughly 0.5–2 seconds for capsule extraction and state validation.
- security: Improves isolation by binding authenticated content to an explicit tab and short-lived request; does not create an origin allowlist, so retain the owner-configured empty-by-default policy.
- depends on: A working browser_read_page/browser_snapshot action result with URL and tab identity; A relay request correlation ID carried through /execute and /pipeline/events; Existing browser-finding TTL/provenance rules


## What it asked for

_Nothing._
