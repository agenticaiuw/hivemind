# Harness derivation — browser-extension — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the full article or document open in my logged-in browser, tell me the thesis and the three points worth remembering, and save only the citation and my spoken takeaway.”"
- **useful because:** The browser is the only node that can reach the owner's paywalled or private document sessions. It can hand the relay grounded text, while the pendant makes the result consumable during a walk; storing a citation and owner-authored takeaway instead of page text prevents a private reading session becoming a permanent transcript.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for extraction and citation checking; realtime only for the short spoken answer and follow-up questions
- **latency:** Initial extraction 10–30 seconds depending on document length; spoken summary begins within 2 seconds after the result arrives; follow-up section lookup under 5 seconds.
- **cost:** Roughly $0.01–$0.08 per document, dominated by model tokens for long pages; browser extraction and local citation storage are negligible.
- **security:** Authenticated document text leaves Safari only to the local Mac agent and relay model for this request. Never persist raw page text by default; persist URL/title/author/date plus the exact spoken takeaway, with an empty per-origin retention policy the owner can inspect. Any export, share, or download requires an explicit separate request.
- **missing:** long-document pagination/reader-mode extraction with section anchors; a retention-aware citation/takeaway record type; a relay prompt that answers follow-up questions from an ephemeral evidence capsule

### "“Look at the private booking or appointment page I have open, cross-check its date, timezone, location, and cancellation deadline against my Mac calendar, and tell me whether I need to act today; if I say yes, create a reminder with the source link.”"
- **useful because:** This joins authenticated browser truth with local calendar state, a boundary no single node can cross. It prevents missed deadlines caused by stale confirmation emails or timezone errors and turns a read-only private page into a useful, reversible local reminder without submitting anything on the site.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for field extraction and calendar comparison; realtime for the owner's yes/no conversation
- **latency:** Read and compare in 5–15 seconds; reminder creation under 3 seconds after confirmation.
- **cost:** About $0.005–$0.03 per check, mostly structured extraction and a small comparison prompt; Mac calendar API and browser operations are local.
- **security:** Appointment details and calendar events are sensitive and should be ephemeral except for the reminder the owner explicitly requests. Per-origin rules must be supplied by the owner rather than hardcoded. Never click booking, cancellation, or payment controls; creating a local reminder is reversible and separate.
- **missing:** a browser-to-Mac structured field handoff with provenance and timezone normalization; calendar read/compare action exposed to the planner; a confirmation response that carries the exact reminder payload and source URL

### "“What am I looking at right now? Give me the useful context from the page in my active Safari tab, and let me ask follow-up questions without reading the whole page aloud.”"
- **useful because:** A worn pendant has no screen and cannot know which private page the owner is viewing; Safari has the session and active-tab context, while the relay can turn it into a short spoken answer. This makes the pendant a hands-free companion to authenticated work instead of a separate text-only assistant. Follow-ups stay grounded to the live page and expire when the tab changes.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** realtime model for the first short answer and follow-ups, with a cheaper background model optionally pre-indexing very long pages
- **latency:** Active-tab capture under 1 second; first spoken sentence within 2–3 seconds; follow-ups under 3 seconds while the evidence capsule is live.
- **cost:** About $0.005–$0.04 per interaction, dominated by realtime model tokens; page extraction and tab metadata are local.
- **security:** The active URL and page text may contain private data. Send only the requested tab's extracted content, redact secrets before model use, do not persist raw text, and expire the evidence capsule on tab navigation or a short timeout. The owner must be able to disable spoken output for configured origins/categories; do not invent that taxonomy.
- **missing:** a reliable active-tab browser action/result path (current route has list/read but no stable active-tab selector); a pendant-triggered request carrying the current browser device/session affinity; ephemeral page evidence capsules with invalidation on navigation and follow-up grounding

### "“Compare the two private pages I have open—such as an invoice and its order confirmation—and tell me exactly where their totals, dates, names, or status disagree, with a short evidence quote for each mismatch.”"
- **useful because:** The browser alone can read each session but cannot reliably reason across them in the owner's voice workflow; the relay can normalize fields and the pendant can speak only the discrepancies. This catches duplicate charges, wrong renewal dates, and stale status pages before the owner acts, without sending or changing anything.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for structured extraction and cross-page comparison; realtime only to explain a flagged mismatch or answer a follow-up
- **latency:** Capture two selected tabs and produce a spoken discrepancy list in 8–20 seconds; follow-up evidence lookup under 4 seconds.
- **cost:** Approximately $0.01–$0.06 per comparison, dominated by extraction/comparison tokens; browser and local normalization are negligible.
- **security:** Two authenticated pages may contain unrelated private data, so transmit only the selected fields and tightly bounded evidence spans. Do not persist raw page text or combine origins into long-term memory. Require the owner to name or select the two tabs; no automatic cross-origin crawling. Default to speaking discrepancies, not full financial or identity values, unless requested.
- **missing:** a user-facing two-tab selection/affinity contract in the browser bridge; schema-constrained extraction for dates, currency, identity, and status with source spans; ephemeral cross-page comparison capsules that can be discarded after the answer

### "“Take the one practical detail from the private page I’m viewing—like the pickup address, confirmation number, or entry instructions—and make it available on my pendant for the next few hours, even if my Mac disconnects.”"
- **useful because:** Today a private browser page is trapped behind Safari and the pendant loses access when the Mac link drops. This creates a deliberately small, expiring handoff: the browser supplies one owner-requested fact, the relay sends it to the pendant's offline alert inbox, and the owner can replay it without exposing the rest of the page or needing a phone.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for selecting and validating the requested field; no realtime model needed unless the owner asks a spoken clarification
- **latency:** Extract and queue the short fact in 5–12 seconds; replay is local and immediate while offline.
- **cost:** About $0.002–$0.02 per handoff, mostly small extraction; local queueing and replay have no API cost.
- **security:** The owner must explicitly name the field and duration. Payloads are short-lived, encrypted in transit, deleted on expiry or button acknowledgement, and never include the page body. Confirmation codes and access instructions should be treated as sensitive; the pendant should indicate expiry and avoid broadcasting them except on a deliberate replay.
- **missing:** a relay command that turns a browser evidence span into a typed expiring pendant payload; field validation and expiry metadata for offline_alert_inbox; a browser tab/session selector that binds the handoff to the page the owner intended

### "“Use the private reservation page I have open to build me a compact departure plan: destination, check-in deadline, and when I must leave from my current Mac location; put the plan on my pendant so I can follow it without reopening Safari.”"
- **useful because:** A reservation's real check-in deadline and address are often behind a login, while the Mac is the node that can calculate a route and the pendant is the only surface that remains available while walking. Combining them turns a buried confirmation into a time-bounded plan rather than a generic reminder.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for extracting reservation facts and composing the plan; local Mac routing for travel time; realtime only if the owner asks for a spoken adjustment
- **latency:** Produce the plan in 10–30 seconds; pendant replay is immediate and should refresh only when the owner asks.
- **cost:** Roughly $0.01–$0.05 per plan, mainly extraction and optional map/routing lookup; pendant delivery is negligible.
- **security:** Use only the selected reservation tab and current coarse location needed for routing. Do not persist itinerary page text or exact location beyond the expiring plan. Never book, modify, or check in; clearly label travel-time uncertainty and timezone.
- **missing:** a local routing/current-location action exposed to the Mac planner; a typed reservation schema with timezone and check-in deadline validation; an expiring pendant plan payload with update/cancel semantics


## Changes it proposed to its own stack

### `browser-harness` — Add an active-tab evidence lease: every browser_read_page result gets a tabId, URL, navigation token, and expiry; the extension heartbeat or next read invalidates the lease when that tab navigates, closes, or changes origin. Relay follow-up questions must fail closed to a fresh read rather than answer from stale authenticated text.
- **owner gets:** When the owner asks a follow-up about a private page, the pendant will not confidently answer about yesterday's tab after Safari moved on. It makes hands-free page help trustworthy without requiring the owner to remember to say “refresh.”
- effort: Moderate: extend browserBridge/browserSessions result metadata, compare heartbeat tab URL/title and a navigation counter, and add one relay evidence lookup path.  ·  risk: Safari heartbeats may lag, causing a brief stale-window or unnecessary refresh. Recover by treating unknown heartbeat state as expired and asking for a fresh read; never delete the owner's browser session.
- cost: Negligible API cost; one small metadata write per browser result and heartbeat. No meaningful hardware cost.  ·  latency: Follow-up may add 0.5–2 seconds when a fresh read is required; unchanged for a stable tab.
- security: Positive: reduces accidental cross-page disclosure and prevents stale private evidence from surviving navigation. Raw page text remains ephemeral.
- depends on: A working browser_read_page action through POST /execute; Navigation/tab identity reported by the Safari extension heartbeat; Ephemeral evidence capsule lookup in the relay


## What it asked for

_Nothing._
## Its own summary

Established live browser usefulness this round: Safari is online with 9 tabs and POST /execute can directly perform browser_read_page, returning page text, provenance evidence capsules, and receipts. Recorded three cross-node capabilities: authenticated document-to-citation reading, booking/calendar deadline comparison with reversible reminders, and hands-free active-tab context through the pendant. Also recorded an active-tab evidence lease that invalidates stale private page context on navigation. Told mac-planner that direct /execute works despite the enqueue wrapper resolver failures.

**Biggest unknown:** The remaining blocker is not browser reach: it is the missing end-to-end trigger and evidence lifecycle. I still need a reliable pendant-to-active-tab request path, navigation-aware invalidation in the browser bridge, and an owner-supplied per-origin/category retention and speakability configuration. The generic enqueue wrappers remain ambiguous; direct POST /execute is usable now.

