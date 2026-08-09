# Harness derivation — browser-extension — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-execution** — Safari extension is online with one real tab (tabId 52) on a YouTube video, and POST /execute with actions:[{type:'browser_read_page',tabId:'52'}] successfully returned page text plus an evidence capsule and receipt.
  - evidence: GET /browser/status at 2026-08-09T03:14:24Z; POST /execute at 2026-08-09T03:15:17Z returned ok:true, capsule evd_691badd4db5e, receipt rcpt_0cee9196.

## Capabilities it proposed

### "When I say “watch this page for a decision,” keep checking the currently logged-in Safari page, detect a material change, and give me a two-sentence explanation plus the exact evidence and time it changed on my pendant."
- **useful because:** Authenticated pages often contain decisions and deadlines that public search cannot reach. The browser sees the session, the relay can compare readings cheaply, and the pendant can surface the result even when the owner is away from the Mac.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background browser polling and a cheap diff/extraction model; realtime only for the owner's spoken request and final clarification.
- **latency:** Initial setup under 5 seconds; subsequent checks every owner-selected interval, with alert delivery under 30 seconds after a detected change.
- **cost:** Roughly $0.01–$0.05 per check depending on page size and extraction; most cost is authenticated page extraction, not speech.
- **security:** Only the current authenticated origin is read; page bodies are never persisted. Persist short claims with URL, timestamp, and evidence capsule, using the existing 24-hour/200-character browser retention. Starting a watch must state origin, cadence, and expiration aloud; no form submission or message send.
- **missing:** A first-class watch creation route that accepts current tab, extraction question, cadence, and expiry; A durable page-diff cursor that stores hashes/claims rather than page text; Relay-to-pendant delivery wiring for a detected change, using offline_alert_inbox

### "Say “show me the proof,” and the system should put the exact source passage and timestamp from my authenticated Safari page next to the spoken summary, then let me ask a follow-up about only that passage."
- **useful because:** A spoken browser summary is hard to trust when the page is private or high-stakes. This creates an inspectable chain from pendant speech to a bounded page excerpt without dumping or retaining the whole page.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime model handles the follow-up; a cheaper extraction model creates a small evidence capsule and locator first.
- **latency:** Evidence capsule in under 8 seconds; follow-up answer under 2 seconds if the capsule is still live.
- **cost:** About $0.01–$0.04 per evidence request; page extraction and a small realtime follow-up dominate.
- **security:** Never speak or persist unrelated page content. Return a bounded excerpt only on explicit request, redact secrets and account identifiers, and expire it with the existing browser TTL. The owner must be able to revoke the capsule.
- **missing:** A browser evidence viewer/locator that maps extracted claims to stable DOM ranges or screenshots without retaining full HTML; A pendant action for ‘show proof’ and a relay protocol carrying a temporary capsule ID; A revocation endpoint exposed to the spoken agent

### "While I am on a private web page, let me say “make me a briefing from this,” and have the browser collect only the decisions, deadlines, and unanswered questions across the page and my open related tabs, then read a prioritized briefing on the pendant."
- **useful because:** The owner should not have to copy private material into chat. This combines the browser's authenticated reach with cross-tab synthesis and wearable delivery, while limiting extraction to an explicit purpose rather than archiving pages.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap background extraction per tab, followed by a single synthesis pass; realtime only if the owner asks a spoken follow-up.
- **latency:** Up to 20 seconds for 3–8 tabs; incremental progress can arrive immediately and the final briefing should be ready within 45 seconds.
- **cost:** Approximately $0.05–$0.20 per briefing, dominated by multi-tab extraction and synthesis; spoken audio is minor.
- **security:** Read only the selected tab and explicitly related tabs, never the whole browser by default. Keep only short claims and provenance under the browser retention policy; do not persist page text or screenshots. Surface which tabs contributed and omit claims that disagree rather than silently choosing.
- **missing:** A user-facing related-tab selection and bounded scope protocol; A multi-tab extraction job that feeds the existing disagreement/cross-check machinery; A briefing artifact that can be queued into offline_alert_inbox and deleted after playback

### "When I say “check whether this deadline fits,” compare the deadline on the private webpage I’m viewing against my Calendar, reminders, and existing commitments, then tell me the conflict and propose the smallest schedule change without changing anything yet."
- **useful because:** A deadline is only useful when checked against the owner’s actual commitments. The browser can see the authoritative private page while the Mac can see local planning data; neither surface alone can reliably answer whether the date fits.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background extraction and deterministic calendar overlap first; realtime model only for the spoken explanation and tradeoff question.
- **latency:** Under 15 seconds for one page and the next 30 days of commitments.
- **cost:** Approximately $0.03–$0.10 per check; browser extraction and calendar normalization dominate.
- **security:** Read only the current page and necessary calendar window. Persist no page text; retain only a short deadline claim and provenance under existing browser TTL. Scheduling changes remain drafts until explicitly requested.
- **missing:** A cross-surface deadline object with confidence, timezone, and source citation; A conflict resolver that can rank schedule changes by disruption and produce a draft rather than mutate Calendar; A spoken result format that names the authoritative source and competing commitments

### "Say “make this private page accessible,” and have the system turn the currently logged-in page into a spoken, structured version—headings, controls, tables, and the next actionable link—while preserving the page’s privacy and letting me jump back to any section."
- **useful because:** Private web apps are often visually dense and inaccessible to a person wearing a voice-first device. This would make the browser session usable hands-free rather than merely summarizing it, without requiring the owner to expose the page publicly.
- **path:** browser → relay → pendant → mac-bridge
- **model tier:** A cheap DOM/accessibility-tree parser creates structure; realtime handles navigation questions and section jumps.
- **latency:** Initial structure in under 8 seconds; section navigation under 2 seconds when the page is already captured.
- **cost:** About $0.01–$0.05 per page structure; model cost is limited by sending only the selected section.
- **security:** Keep content transient and scoped to the bound tab. Never persist the full accessibility tree or screenshots; retain only the selected claim/evidence capsule. Do not activate controls unless the owner separately asks.
- **missing:** A browser accessibility-tree extraction action with stable section locators; A pendant navigation protocol for next section, previous section, and jump-to-control; A bounded section cache that can be discarded independently of browser provenance

### "When I say “find me an appointment,” search the logged-in booking site, compare available slots with my Calendar and travel constraints, and return three ranked options on the pendant without booking any of them."
- **useful because:** Finding a viable appointment requires credentials in the browser, personal availability on the Mac, and a spoken decision interface. Today each node can handle only part of this and the owner must manually shuttle times between them.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background browser extraction plus deterministic calendar/travel filtering; realtime only to clarify preferences and read the shortlist.
- **latency:** One to two minutes for a site with several result pages; incremental candidates should appear as they are found.
- **cost:** Approximately $0.05–$0.25 per search, dominated by authenticated pagination and extraction.
- **security:** Search only the named provider and date range. Do not submit, reserve, or expose personal calendar details to the website. Store candidate slots only as short-lived job data, and stop before any booking or payment action.
- **missing:** A browser pagination/search runner that can operate read-only across result pages; A constraint handoff from Calendar, travel time, and owner preferences into the browser job; A ranked candidate artifact with expiry and a clear ‘not booked’ state


## Changes it proposed to its own stack

### `browser-harness` — Add an explicit tab lease: Safari extension reports a stable tab handle, URL/origin, title, and last-seen timestamp; the owner can bind one spoken task to that tab for a short TTL. Every browser read or click carries the lease and returns a receipt, while navigation to a different origin automatically pauses the lease.
- **owner gets:** The owner can say “keep working on this” without repeating which private tab he means, and the system will not accidentally continue on a different tab after Safari changes focus.
- effort: Medium: extension heartbeat state, lease storage, execute validation, and spoken status.  ·  risk: A stale lease could target the wrong page; expire aggressively, announce tab title/origin before the first action, and require re-binding after origin changes. Recovery is simply rebind.
- cost: Negligible API cost; no hardware cost.  ·  latency: Adds one local validation round, under 100 ms.
- security: Reduces accidental cross-tab disclosure by making scope explicit; lease metadata should not include page content.
- depends on: Safari extension heartbeat; POST /execute; GET /browser/status

### `relay` — Create a browser-to-pendant ‘question token’ protocol: a read result carries a short-lived token, claim list, source URL/title, and evidence capsule ID; the pendant can send that token with a follow-up like “is that deadline firm?” without resending page text or the entire conversation.
- **owner gets:** The owner can have a natural, low-latency conversation about a private page while keeping sensitive content out of repeated prompts and making every answer traceable to the exact read.
- effort: Medium-high: token registry, relay routing, expiry/revocation, and pendant event encoding.  ·  risk: A token may be replayed or outlive the page. Bind it to the device/session, expire within minutes, and return ‘page may have changed’ rather than pretending freshness.
- cost: Small storage and relay traffic; lower model cost because full page context is not resent.  ·  latency: Follow-ups become faster by avoiding re-extraction; first read unchanged.
- security: Sensitive claims still cross relay transiently; encrypt in transit, avoid logs, and retain only the bounded capsule ID/claim.
- depends on: POST /pipeline/events; GET /browser/provenance; POST /browser/provenance/trace; offline_alert_inbox

### `integration` — Connect authenticated browser jobs to the existing offline_alert_inbox with semantic severity and deduplication: a job may emit at most one alert per claim fingerprint, include source and expiry, and retract an unread alert if a later read disproves it.
- **owner gets:** The owner gets only genuinely new, actionable private-page changes on the wearable, including when the Mac link drops, instead of repeated or stale notifications.
- effort: High: browser job runner change detection, alert schema, dedup/retraction state, and relay-to-firmware delivery.  ·  risk: A parser error could create a false alarm or retract a real one. Keep the source claim and confidence in the alert, preserve an audit record, and provide a long-press replay of the last source/time.
- cost: Low ongoing API cost with hash-based dedup; modest firmware storage for a handful of alerts.  ·  latency: Alert within one poll interval; no impact on ordinary voice turns.
- security: Alerts must contain only the minimum claim, not page text; origin and expiry are visible so stale private facts cannot masquerade as current.
- depends on: Browser job runner; POST /memory/browser-findings; offline_alert_inbox; GET /jobs/:jobId/receipts

### `browser-harness` — Add a read-only browser accessibility projection that emits a compact tree of headings, tables, form controls, labels, and stable section locators, with a server-side cursor for requesting one section at a time.
- **owner gets:** The pendant could make dense private sites understandable and navigable instead of giving the owner an undifferentiated page dump.
- effort: High: Safari content-script extraction, locator repair after DOM updates, table/chart summarization, and section paging.  ·  risk: A stale locator could highlight or activate the wrong control; all returned controls must default to observation and report when the page changed. Recovery is a fresh projection.
- cost: Low storage if only one section is cached; moderate extraction cost for complex pages.  ·  latency: Initial projection 2–8 seconds; section requests under 1 second when cached.
- security: The projection is sensitive page content, so keep it in an expiring session cache and never write the complete tree to logs or memory.
- depends on: POST /execute; Safari extension content-script support; Browser evidence capsules

### `integration` — Add a typed cross-surface ‘constraint packet’ exchanged between browser jobs and Mac planning: source facts, timezone, validity window, hard constraints, soft preferences, and an explicit mutation prohibition. The packet must be inspectable and expire automatically.
- **owner gets:** The system could safely combine a private website with Calendar, travel, and reminders without losing which facts came from where or accidentally turning a search into a booking.
- effort: Medium-high: schema, validation, planner adapters, expiry handling, and spoken rendering.  ·  risk: Bad normalization could discard a viable option or invent compatibility. Preserve raw source citations, mark unknowns, and return candidates rather than silently deciding.
- cost: Tiny serialization cost; lower model cost through structured context.  ·  latency: Slight planning overhead, typically under 200 ms.
- security: Keeps credentials in the browser and sends only derived constraints to the Mac; packet must carry origin and retention labels.
- depends on: POST /plan; POST /execute; GET /browser/provenance; Calendar/reminder adapters

### `interaction` — Add a pendant ‘section cursor’ state for browser sessions: the owner can say next, previous, repeat value, or jump to the cited section, and the relay resumes from the current cursor without replaying the page or entire conversation.
- **owner gets:** A voice-first owner can inspect a private page at their own pace and ask precise follow-ups instead of restarting a long browser read each time.
- effort: Medium: cursor IDs, compact section cache, relay routing, and playback/navigation events.  ·  risk: Cursor state can become stale after navigation. Announce title and section revision, invalidate on page hash change, and fall back to a fresh read.
- cost: Minimal relay/storage cost; lower inference cost from bounded context.  ·  latency: Navigation under 1–2 seconds for cached sections.
- security: Cursor IDs must be session-bound and should reveal no page content if logged or intercepted; discard them when the session ends.
- depends on: POST /pipeline/events; POST /execute; Browser evidence capsules; Pendant playback-control primitive


## What it asked for

_Nothing._
