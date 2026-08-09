# Harness derivation — browser-extension — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 9 tabs, active X home tab, and authenticated Gmail tab; POST /execute browser_list_tabs succeeds end-to-end and returns tab provenance plus receipts. The previously granted browser enqueue wrapper tools remain unresolved, so direct POST /execute is the working path.
  - evidence: GET /browser/status returned online=true, tabCount=9, active tab 1163292 at https://x.com/home; POST /execute browser_list_tabs returned 9 tabs including Gmail tab 901464 and receipt rcpt_b8f19d96-7734-4159-9ebf-1054232b1b45.

## Capabilities it proposed

### "When I say “explain this page,” use the page currently open in Safari, summarize it for me through the pendant, and let me ask follow-ups like “what do I need to do?” or “show me the relevant section.”"
- **useful because:** This is the single most useful browser capability: the owner can use the wearable as a voice layer over any authenticated page already open, without copying text, screenshots, or exposing the page to a public search service. It combines the pendant's immediacy, relay conversation, Safari's logged-in session, and Mac execution.
- **path:** pendant → relay-realtime → browser-harness → mac-planner
- **model tier:** Realtime for the spoken summary and follow-up intent; a cheaper background model for long-page extraction and section indexing.
- **latency:** First spoken gist in 3–6 seconds; follow-up section lookup in under 5 seconds. Browser extraction is the dominant delay.
- **cost:** About $0.01–$0.05 per short explanation, dominated by model tokens after page extraction; long pages should use background summarization.
- **security:** Page text leaves Safari and reaches the local agent/relay model. Never persist raw page text by default; retain only a short-lived encrypted page fingerprint, selected excerpts, URL, and tab ID. Ship with per-origin rules empty and ask the owner to choose origins and categories that may be spoken or stored. Never click submit/send/purchase from a follow-up without explicit instruction.
- **missing:** A reliable active-tab browser_read_page/snapshot command exposed to the planner (POST /execute currently works, but the granted enqueue wrappers are unresolved); A streaming page-excerpt handoff from browser harness to realtime conversation; Owner-supplied per-origin read/extract/redact/never-store configuration

### "Check my open authenticated travel, work, and calendar pages together and tell me whether the dates, times, locations, and names disagree; give me a spoken conflict list and offer to create reminders, but do not edit any source page."
- **useful because:** Cross-page consistency is something a single browser tab cannot do reliably. The browser holds the owner's sessions, the Mac can inspect local Calendar/Mail, and the pendant makes the result available while away from the screen. It catches double-bookings, stale itinerary times, and mismatched names before they become expensive mistakes.
- **path:** browser-harness → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for structured extraction and entity/date normalization; Realtime only to answer the owner's spoken question and read the final conflicts.
- **latency:** 20–45 seconds for an on-demand audit of up to six tabs; under 5 seconds to speak the already-computed result.
- **cost:** Roughly $0.03–$0.15 per audit, dominated by extracting and normalizing multiple pages; reminders are local and cheap.
- **security:** This joins highly sensitive travel, calendar, and identity data. Do not store raw page text or send it to third-party search. Persist only normalized fields needed for the conflict report, with an expiry. Require the owner to supply explicit origins/categories; default configuration must be empty. Creating a reminder is reversible, but source-page edits are out of scope.
- **missing:** A browser multi-tab capture action that returns bounded, structured excerpts with tab provenance; A normalizer that emits typed date/time/location/person records and confidence; An owner-configured origin/category policy and expiry-backed conflict cache

### "Watch a page I choose in Safari for a meaningful change—such as a new appointment status, an updated order, or a newly available application slot—and tell me on the pendant exactly what changed, with the old and new value and a link, without repeatedly reading the whole page aloud."
- **useful because:** A logged-in browser is the only node that can see many private dashboards. Change detection turns that reach into a practical alert instead of requiring the owner to remember to check. The pendant can deliver a terse alert offline through the already accepted alert inbox, while the Mac/relay maintain the watch.
- **path:** browser-harness → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background polling plus deterministic DOM/structured-data diffing; use a small model only when the changed region needs semantic classification. Realtime is only for the owner's follow-up.
- **latency:** Poll interval configurable from 1 minute to daily; a detected change should reach the relay within 10 seconds and the pendant on the next link. Most cost is polling and authenticated browser wakeups, not model inference.
- **cost:** Near-zero model cost for selectors/JSON diffs; roughly $0.01–$0.08 per semantic diff. Browser wakeups and Mac power are the main operational costs.
- **security:** Watching can expose private values and may be mistaken for authorization to act. Store only redacted old/new snippets and a hash by default, never full page snapshots. Let the owner define per-origin selectors and categories; ship with no origins configured. Alerts must identify the source and timestamp, and no automatic click/submit should follow a change.
- **missing:** Durable watch definitions with selector/region extraction and backoff; Semantic DOM/structured-data diffing with redaction before persistence; Relay scheduling while Safari/Mac is asleep, plus delivery to offline_alert_inbox

### "When I ask “is this email safe?”, inspect the currently open authenticated Gmail message and its links, follow them only in an isolated read-only browser context, and tell me through the pendant whether the sender, destination, login request, and urgency look suspicious—without opening the link in my normal session or sending anything."
- **useful because:** This gives the owner a practical phishing check that public search or the Mac alone cannot provide: Safari can see the private message and its real authenticated context, while the relay can compare domains and language and the pendant can warn before the owner taps. It is especially useful when the owner is away from the screen.
- **path:** browser-harness → relay-realtime → mac-planner → pendant
- **model tier:** Cheap deterministic checks first (sender/domain mismatch, redirects, certificate/origin, login form, urgency phrases); a background model classifies ambiguous language. Realtime only speaks the concise verdict and confidence.
- **latency:** 5–12 seconds for a message with up to ten links; domain/redirect inspection dominates. The warning should be speakable immediately if a high-confidence mismatch is found.
- **cost:** About $0.01–$0.04 per check, mostly model classification for ambiguous content; isolated browser tabs and network fetches are the larger operational concern.
- **security:** Reading the email and visiting links exposes message content and potentially tracking URLs. Never submit forms, enter credentials, download files, or use the owner's normal cookie jar. Use a disposable isolated session, strip query tracking parameters where safe, retain only verdict/evidence hashes, and show the exact sender and destination domains. This is advice, not a guarantee.
- **missing:** A disposable browser-session profile isolated from the owner's logged-in Safari cookies; A safe link inspection action that stops at login, download, form submission, or credential prompts; Deterministic phishing evidence extraction (header identity where available, redirect chain, origin, certificate, form actions); A concise pendant warning protocol with confidence and an option to open the harmless destination


## Changes it proposed to its own stack

### `browser-harness` — Make the already-working POST /execute browser path the canonical planner-facing browser_run_actions API, with explicit tab affinity: every browser_read_page/snapshot result must include tabId, origin, title, capture timestamp, and a short-lived page fingerprint; a voice session can pin that tab, and navigation or tab closure automatically invalidates the pin instead of silently switching to another tab.
- **owner gets:** When the owner says “that page,” the pendant answers from the page he actually means, not an unrelated Gmail/X tab. It makes authenticated browser help dependable across nine open Safari tabs and makes spoken citations possible.
- effort: Medium: normalize action schema and result envelope in local-agent/browserBridge.js/browserSessions.js, then add session-pin handling and tests for tab closure/navigation.  ·  risk: A stale pin could make a request fail rather than answer from the wrong page; recover by speaking the tab title and asking the owner to switch or pin another tab. Existing browser actions remain available.
- cost: Negligible API cost; small local CPU/storage cost for fingerprints and metadata.  ·  latency: Adds under 100 ms locally; avoids expensive retries and wrong-page model calls.
- security: Improves isolation by preventing cross-origin tab confusion. Do not persist page text; fingerprints and metadata should expire quickly.
- depends on: Owner-supplied per-origin browser privacy rules; A canonical action wrapper that maps browser_read_page/browser_snapshot to POST /execute


## What it asked for

_Nothing._
## Its own summary

This round produced three browser-only, cross-surface capabilities and one concrete harness change. Safari is genuinely live now: 9 tabs are open, including authenticated Gmail, and POST /execute successfully listed them with receipts. The most important proposal is voice “explain this page” from the pendant, grounded in the pinned active Safari tab. I also recorded authenticated cross-page date/conflict auditing, configurable meaningful-change watches delivered through the offline alert inbox, and tab-affinity/provenance so “that page” cannot silently resolve to the wrong login.

**Biggest unknown:** I still need the owner to choose the first 3–5 authenticated origins and provide per-origin rules: what may be read, spoken, extracted, and persisted (plus categories never spoken aloud). The system should ship with this configuration empty rather than guessing. Technically, POST /execute is working today; the granted browser enqueue wrappers still do not resolve, so canonicalizing /execute is the remaining harness gap.

