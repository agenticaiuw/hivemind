# Harness derivation — browser-extension — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live Safari state** — Safari extension is online with two tabs: active authenticated DoorDash order tab 3032326 and inactive YouTube subscriptions tab 3186198. Direct POST /execute browser_list_tabs and browser_read_page succeeded; the granted wrapper tools remain unresolved.
  - evidence: POST /execute 200 at 2026-08-08T22:18:31Z returned 2 tabs; POST /execute browser_read_page tabId 3032326 returned live order status and evidence capsule evd_b02c47cc2647.

## Capabilities it proposed

### "“While I’m out, keep an eye on the authenticated order or booking page I left open. If its promised time slips, tell me on the pendant; otherwise say nothing. When I ask ‘what changed?’, read the live page and give me the delta.”"
- **useful because:** This turns a logged-in browser tab into an actionable exception channel: the browser can see private status, the always-awake relay can notice change, and the worn pendant can alert without the owner reopening Safari. It avoids noisy routine updates and uses the live DoorDash tab that is actually present now.
- **path:** browser → relay → pendant → mac-planner
- **model tier:** Cheap background polling/diff model for page normalization; realtime only for the owner’s spoken follow-up. Use the expensive model only when a material delta needs interpretation.
- **latency:** Poll every 5–15 minutes while a watch is active; alert within one poll interval. Spoken follow-up under 2 seconds after the owner asks.
- **cost:** Low: browser fetch and structural diff dominate; one short background summarization call only on a change, roughly cents per day per watched page.
- **security:** The browser reads authenticated content and must retain only a redacted status claim, URL, timestamp, and evidence capsule—not page text or screenshots. Watching must be explicitly started for a tab and stop when the tab closes or session expires. Never click, tip, cancel, or submit.
- **missing:** A first-class page-watch schedule bound to a browser session/tab with field-level diffing and relay event delivery; Pendant alert payload support beyond the existing offline alert inbox, including a concise change claim and severity; Owner-configurable empty per-origin and per-category speech/retention rules

### "“Find the due date and amount on the bill in the private tab I already have open, show me the extracted fields, and—only after I say yes—put a reminder on my Mac for three days before it’s due.”"
- **useful because:** No other node can see the logged-in bill, and no browser automation should silently turn a read into a commitment. This makes the private page useful while preserving a clear preview boundary: extract first, speak a compact receipt, then let the Mac create the reminder only on an explicit yes.
- **path:** browser → relay-realtime → pendant → mac-planner
- **model tier:** Background/local extraction for labels, dates, and currency; realtime model only to resolve the owner’s confirmation and explain ambiguity.
- **latency:** Extraction in 3 seconds; spoken preview in 5 seconds; reminder creation immediately after confirmation.
- **cost:** A few cents or less per invocation; browser read and local date parsing dominate, with a small model call for ambiguous fields.
- **security:** Never store the bill body or screenshot. Persist only a short claim with host, URL, evidence capsule, and 24-hour browser TTL. Mask account numbers and payment details in speech. The Mac action must be a separate confirmation turn and produce an undoable receipt.
- **missing:** A browser field-extraction action that returns typed date/amount/merchant claims with redaction; A confirmation-linked handoff that binds the exact preview to one create_reminder action and rejects stale previews; A browser-to-Mac provenance link so the reminder records which page claim caused it

### "“Before I leave for the appointment I booked online, check the private confirmation tab against my calendar and tell me on the pendant only what could make me late—changed time, address, check-in instructions, or missing preparation.”"
- **useful because:** This is a genuinely cross-surface task: the browser holds the confirmation behind a login, the Mac knows the owner’s calendar and travel context, the relay joins them while the laptop may be closed, and the pendant delivers only an exception-sized answer. Today these facts are stranded in separate places.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Cheap scheduled/background join and rule-based contradiction detection; use the realtime model only to answer a follow-up such as ‘what do I need to bring?’
- **latency:** Run on demand or 90 minutes before the calendar event; target a 10-second end-to-end result and a sub-20-second alert if a page read retries.
- **cost:** Low per run: one browser read, one local calendar query, and a short synthesis; roughly a few cents, with no continuous polling.
- **security:** The confirmation page is read-only and never submitted or modified. Store only normalized appointment facts and their two provenance links, with browser claims expiring after 24 hours; redact confirmation numbers and full addresses from logs and spoken output unless needed. If the page and calendar disagree, say so rather than choosing silently.
- **missing:** A calendar-event-to-browser-session join that can identify the owner’s confirmation tab without an invented site allowlist; A structured contradiction/late-risk evaluator for time, location, and preparation fields; A relay job that can wake the browser, join results with local calendar data, and push a prioritized offline pendant alert

### "“When you tell me something you found in a private web page, give me a tiny source token too. If I press the pendant’s bookmark button later, reopen the exact page and section on my Mac and read back what you relied on—without saving the page itself.”"
- **useful because:** Authenticated browser answers are unusually hard to audit: the owner may hear a claim while walking and later need to know whether it came from a live order, account page, or stale memory. A physical, replayable source token would make spoken browser assistance trustworthy without turning the system into a page archive.
- **path:** browser → pendant → relay → mac-planner
- **model tier:** No expensive reasoning for replay; deterministic evidence lookup and local page reopening. Use realtime only if the owner asks for a plain-language explanation of conflicting evidence.
- **latency:** Speak the token inline in under 100 ms; replay should reopen the source in under 5 seconds and read a compact excerpt or claim.
- **cost:** Negligible per use; storage is short claim metadata and hashes, not page bodies. The engineering cost is browser anchor capture and cross-device token routing.
- **security:** Tokens must be opaque, short-lived, and bound to the owner’s browser session. Reopening requires the existing Safari login and must never transmit credentials to the relay. Persist only claim text within the existing browser 24-hour/200-character limits, URL, anchor/hash, and evidence capsule; if the page changed, say ‘source changed’ rather than presenting new text as old evidence.
- **missing:** A browser evidence-token format that records a stable DOM/text anchor plus content hash without retaining HTML or screenshots; A pendant input/output path for announcing and later resolving the token, integrated with the existing offline_moment_bookmark behavior; A Mac/browser replay action that navigates to the source and verifies the hash before extracting the cited section; A cross-surface evidence resolver that can safely expire tokens when the browser session or 24-hour finding TTL ends


## What it asked for

_Nothing._
## Its own summary

Safari is no longer empty: I verified two live tabs and successfully read the authenticated DoorDash order through direct POST /execute. I recorded three new cross-surface capabilities: exception-only authenticated page alerts to the pendant; private bill extraction followed by explicit Mac reminder confirmation; and appointment-readiness reconciliation between a logged-in confirmation page, calendar, relay, and offline pendant. I also informed mac-planner that direct /execute works.

**Biggest unknown:** The browser wrapper tools still do not resolve reliably, so production needs one canonical browser action path (or direct POST /execute routing) rather than relying on the ambiguous wrappers. Product gaps remain page-watch scheduling/diffing, typed field extraction and stale-preview handoff, and calendar-to-browser session joining.

