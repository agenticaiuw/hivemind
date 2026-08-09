# Harness derivation — browser-extension — round 193

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser execution** — Authenticated Safari browser control is live through POST /execute: browser_list_tabs and browser_snapshot succeeded against DoorDash active tab 3032326 and YouTube subscriptions tab 3186198, returning evidence capsules and receipts.
  - evidence: POST /execute HTTP 200 at 2026-08-08T22:15:44Z with two successful read-only browser actions.

## Capabilities it proposed

### "“Check this form against my calendar and files, point out anything inconsistent, and leave it unsubmitted.”"
- **useful because:** Before an irreversible submission, the owner gets a private cross-check of dates, names, amounts, and attachments. Safari contributes the authenticated form and its session; the Mac contributes local Calendar/files; the pendant gives a hands-free answer. It catches mistakes no single surface can see.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Cheaper background/local planner for field extraction and deterministic comparisons; realtime tier only for the owner's spoken request and final concise report.
- **latency:** 5–15 seconds for a normal form; never click Submit or Send. If a field is ambiguous, report it rather than guessing.
- **cost:** One browser snapshot/read, one bounded Calendar/files query, and a small structured comparison prompt; typically 2–5k tokens, dominated by document extraction.
- **security:** Forms may contain secrets and regulated data. Keep raw values on-device, pass only normalized field labels/values needed for comparison, and retain no page body. This is an audit-only action; owner policy allows maximum access, but the workflow intentionally stops before irreversible submission and records an evidence receipt.
- **missing:** Structured browser form-field extraction including labels, current values, and submit controls; A Mac planner adapter that returns only relevant local facts with provenance; A cross-surface diff response and explicit stop-before-submit behavior

### "“Watch the authenticated pages I have explicitly configured and tell me only when a new urgent item appears.”"
- **useful because:** The browser can see logged-in dashboards that Calendar/Mail integrations cannot. A change detector turns that unique reach into an actionable alert: browser reads the configured page, planner compares a redacted set of claims, relay ranks urgency, and the pendant's existing offline alert inbox delivers it even when the Mac link drops.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Scheduled/background cheap model for polling, deduplication, and urgency classification; realtime model only if the owner asks follow-up questions.
- **latency:** Polling cadence chosen per origin (for example 5–30 minutes); alert generation under 10 seconds after a detected change.
- **cost:** One lightweight read and small diff per poll; cost scales with number of explicitly configured origins, with most work in browser polling rather than generation.
- **security:** Ship with an empty per-origin configuration and require the owner to add sites/categories. Persist only short claims, host, URL, provenance, and 24-hour TTL via existing browser findings; never persist page text or screenshots. Alerts should expose only the minimum claim and expire.
- **missing:** Persistent per-origin watch configuration and schedule UI (empty by default); Browser page-watch/diff worker using read-only action allowlists; Urgency taxonomy and deduplication wired to offline_alert_inbox; Owner-facing alert history and disable controls

### "“Save the useful thing on this authenticated page as a reminder for me, with the source link and the exact detail you found.”"
- **useful because:** It bridges the browser's private session to the Mac's durable action without making the owner copy a URL or dictate details. For example, an order status, renewal date, or appointment portal deadline becomes a correctly sourced reminder. The browser reads; the planner extracts one bounded claim; the Mac creates the reminder; the pendant confirms it.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime handles intent and a short confirmation; a cheaper local/background pass extracts a single date/title/source from the page and validates it before calling the reminder action.
- **latency:** Under 8 seconds for a normal page. Read-only browser inspection first; reminder creation is reversible and should return a receipt and undo handle.
- **cost:** One browser read/snapshot plus a small extraction prompt and one Mac reminder action; roughly 1–3k tokens, with browser latency dominating.
- **security:** Only extract the requested bounded detail, not the whole page. Do not persist page text; retain URL and a short host-keyed claim under existing browser TTL/provenance rules. The reminder body should omit secrets and redact sensitive values. Speak back exactly what was saved and provide the existing undo path.
- **missing:** A browser-to-reminder structured handoff carrying source URL, claim, and confidence; Date/renewal extraction that refuses ambiguous dates instead of guessing; Pendant confirmation and undo-status speech integration

### "“Search the authenticated tabs I already have open and tell me which source is authoritative when they disagree.”"
- **useful because:** Today the browser can inspect one page, but it cannot reconcile conflicting private sources. This would answer questions such as “Which delivery date is correct?” or “Which renewal amount is current?” by reading several already-open logged-in tabs, comparing timestamps and provenance, and explaining the conflict rather than silently choosing one. The pendant supplies the question; Safari supplies access; the Mac planner performs the multi-source reasoning; the relay speaks the result.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use a cheaper planner for parallel extraction, timestamp normalization, and contradiction detection; reserve realtime for the short spoken question and final answer.
- **latency:** 5–12 seconds for up to five open tabs. The system should return partial results if one tab times out and explicitly name missing sources.
- **cost:** One bounded read per selected tab plus a compact comparison prompt, approximately 3–8k tokens depending on the number of sources; browser reads dominate latency.
- **security:** Read only tabs selected by the owner’s question; never click, type, or submit. Keep raw page content transient, persist only short claims with host, URL, timestamp, and provenance under the existing browser TTL rules. Do not infer authority from domain alone; expose the evidence and confidence.
- **missing:** Multi-tab query planning that chooses relevant open tabs without reading every page indiscriminately; A normalized claim schema for values, timestamps, source identity, and freshness; Conflict explanation that refuses to collapse materially different claims into one answer; Pendant intent routing for a scoped authenticated-source question

### "“Tell me when one of my configured authenticated sites has silently logged me out, and open its re-login page ready for me.”"
- **useful because:** Silent session expiry currently looks like missing data or a failed automation. The owner should get a precise pendant alert naming the site and the blocked task, while Safari is navigated to the re-login page without entering credentials. This prevents missed bills, stale dashboards, and misleading answers while preserving the owner’s existing login flow.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background classifier detects login walls and distinguishes them from ordinary empty/error pages; realtime is only used for the alert or a follow-up question.
- **latency:** Detected on the next page read or watch poll, with an alert in under 10 seconds; navigation to the re-login page should be immediate and reversible.
- **cost:** Small browser read and classifier invocation per configured origin; negligible compared with repeated failed planner attempts.
- **security:** Never capture or speak password fields, MFA codes, recovery tokens, or page contents. Navigation may open the login page but must not type or submit credentials. Store only origin, blocked task, and timestamp; allow the owner to disable alerts per origin.
- **missing:** Reliable login-wall/session-expiry classifiers across sites; A browser result privacy filter that strips credential and MFA fields before any model sees them; Origin-specific alert configuration and a re-login navigation action; Pendant alert text that identifies the blocked task without exposing sensitive page data

### "“Find all deadlines visible in the authenticated tabs I’ve configured, compare them with my Mac calendar, and tell me only where they conflict.”"
- **useful because:** The owner currently has private deadlines split across web portals and local Calendar. This would surface only actionable collisions—such as two appointments, a renewal and travel, or a portal deadline that falls during an existing commitment—rather than producing another bulk briefing. Safari contributes authenticated dates that no other node can access; the Mac contributes the calendar; the planner normalizes time zones and the pendant gives a concise exception-only answer.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/local planner for date extraction, timezone normalization, and deterministic overlap detection; realtime only for the owner’s question and spoken exception list.
- **latency:** 10–30 seconds for a configured set of pages; return source URLs and confidence for every conflict, and say when a page could not be read.
- **cost:** One bounded read per configured page, one Calendar query, and a small structured comparison; approximately 3–7k tokens, mostly extraction context.
- **security:** The origin set and categories must be explicitly configured and empty by default. Keep only normalized deadline claims, source URL, timestamp, and provenance under the existing short browser TTL; never retain page bodies. Do not create, move, or cancel events automatically.
- **missing:** A cross-origin deadline extractor with timezone and recurrence handling; A Calendar query constrained to the relevant date range; A deterministic interval/conflict engine with provenance-preserving output; A compact pendant response format for multiple conflicts


## What it asked for

### `t16-8e9f` (tool) — browser_read_current_page
- why: The browser extension is now online with authenticated Safari tabs, and direct POST /execute works, but every granted browser wrapper is unresolved for read/snapshot calls. A resolved read-only tool is needed for the owner-facing product, not just probing.

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "browser_read_page",
        "browser_snapshot",
        "browser_list_tabs"
      ]
    },
    "tabId": {
      "type": "string"
    },
    "selector": {
      "type": "string"
    }
  },
  "required": [
    "action"
  ]
}
```

## Its own summary

Recorded three new browser capabilities: authenticated multi-tab contradiction resolution, session-expiry alerts with safe re-login navigation, and cross-origin authenticated deadline conflict detection against Mac Calendar. Each requires new cross-surface orchestration while preserving read-only browser access and short-lived provenance claims.

**Biggest unknown:** Whether any of these highly specific multi-source workflows already exists in the backlog under a different name; the recorder accepted all three, with no duplicate refusal.

