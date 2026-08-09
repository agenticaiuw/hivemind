# Harness derivation — browser-extension — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at this page—what matters, and if there’s a deadline, remind me.” The system should read the current authenticated Safari tab, summarize only actionable content, and create a Mac reminder with a link and provenance; the pendant speaks the result and queues it if offline."
- **useful because:** This is the highest-value browser feature: it turns an existing logged-in page into a spoken decision and a durable next action without copying text or losing the source. It works across surfaces no single node can reach: Safari has the session, Mac can create the reminder, relay interprets, and the pendant delivers it.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** Use the cheaper background/local planner for page extraction and deadline normalization; reserve realtime only for the owner’s spoken question and final concise answer.
- **latency:** 3–8 seconds for read/extract and reminder draft; under 1 second to acknowledge on the pendant. Never submit or alter the source page.
- **cost:** Usually one cheap extraction/planner call plus one short realtime turn; browser and reminder operations dominate neither tokens nor API cost.
- **security:** Ship with an empty per-origin configuration. Persist only a short claim, URL, and evidence capsule under existing 24-hour/200-character browser-fact rules; never persist page HTML. Read-only browser allow-set, and speak a preview of title/date/link before creating the reminder. The owner’s existing maximum-access policy means no artificial gate, but source-page submission remains out of scope.
- **missing:** A browser-current-page context action exposed to the voice planner (the existing browser_read_current_page request is still unavailable); A structured extractor for dates/deadlines and reminder payloads with evidence-capsule links; An explicit per-origin configuration UI, initially empty

### "“Prepare the next step from whatever I’m viewing, but don’t send it.” The system should inspect the authenticated Safari page, extract the relevant form or reply context, draft a response or fill plan on the Mac, show the exact fields and text back through the pendant, and leave the browser stopped before the final submit/send."
- **useful because:** It removes the tedious, error-prone copying between a logged-in web page and the Mac while preserving the owner’s control at the one consequential boundary. The browser is the only node that can see the session; the Mac can construct the draft; the pendant can review it hands-free.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** Use local deterministic DOM extraction and a cheaper planner for field mapping; use realtime only to resolve an ambiguous instruction or read back a compact diff.
- **latency:** 5–15 seconds for extraction and draft; stop reliably before submit/send. Review should fit in one short spoken turn with a link to the draft state.
- **cost:** One bounded planner call per draft, with browser and local action execution as the main latency; no model call for straightforward field copying.
- **security:** Default browser action allow-set excludes submit/send/purchase, while honoring the owner’s maximum-access policy by making the exclusion a task scope rather than a permission gate. Persist no page text; retain only field labels, redacted values, URL, and evidence capsule. Show all outgoing text verbatim and provide existing job undo for local mutations.
- **missing:** A browser action scope that can fill multiple fields yet explicitly terminates before submit; Field-level redaction and provenance in the draft preview; A spoken/visual diff channel shared by Safari, Mac planner, and pendant

### "“Compare these two logged-in tabs and tell me what conflicts.” The system should read two explicitly selected Safari sessions, align their dates, amounts, names, or statuses, speak only the material discrepancy through the pendant, and offer a source-linked Mac note without storing either page."
- **useful because:** Many high-stakes browser tasks are cross-site reconciliation: an invoice against a bank transaction, a shipment against an order, or a portal deadline against a calendar. Safari can hold both authenticated sessions while the relay and pendant make the comparison hands-free; neither page alone can answer it.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Use deterministic extraction and normalization first, then a cheap background model for conflict ranking; realtime only for the owner’s question and a short spoken finding.
- **latency:** 5–12 seconds for two reads and comparison; no writes to either site. A note is created only after the owner asks for it.
- **cost:** Two browser reads plus one bounded comparison call; token cost is limited by field extraction rather than full page text.
- **security:** Require explicit session IDs/tab handoff for both pages; never infer a second origin from the first. Apply existing host-keyed, 24-hour, 200-character browser-fact retention and redact values not needed for the comparison. Speak only the minimum discrepancy and include URLs/provenance, not raw page text.
- **missing:** A multi-session browser read action that accepts pinned session IDs and returns bounded field claims; A comparison schema for dates, money, status, and identity with uncertainty reporting; A source-linked note payload that can be created on the Mac without persisting page bodies

### "“If this logged-in page reaches the condition I named, do the safe follow-up automatically.” For example: when an authenticated order changes to delivered, add a pickup reminder; when a portal item becomes overdue, create a task. The browser should evaluate the condition, the Mac should perform only the declared reversible follow-up, and the pendant should report the source and result."
- **useful because:** Today the browser can be read and the Mac can act, but the owner must manually bridge the two every time. This gives them dependable, event-driven assistance across an authenticated session and local life without asking the browser to send messages, purchase, or mutate the source site.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Use scheduled browser extraction plus deterministic condition matching; use a cheap background model only to normalize dates/statuses. Realtime is needed only for setup and concise result delivery.
- **latency:** Condition checks on the owner-selected cadence; once true, local follow-up within 10 seconds. The source page remains read-only.
- **cost:** Low recurring cost: browser reads and deterministic comparisons dominate; invoke a model only when a field cannot be normalized confidently.
- **security:** The owner must explicitly specify the origin/session, condition, and allowed follow-up at setup; ship with no origins preconfigured. Keep the source page read-only, persist only a short host-keyed claim under existing browser TTL/size bounds, and attach URL/evidence provenance to the reminder. Make the rule one-shot by default, visibly log each firing, and provide undo for the Mac-side action.
- **missing:** A durable conditional browser-rule engine that can schedule reads against a pinned browser session; Typed condition evaluation over bounded browser claims (status, date, amount, presence) with uncertainty handling; A cross-surface trigger that submits a declared reversible Mac action and delivers its receipt to the pendant


## Changes it proposed to its own stack

### `browser-harness` — Add a live-tab lease and explicit handoff marker: when a voice task starts, capture tabId/windowId/url/title plus a content hash; every subsequent browser action must verify the same tab (or return a compact “Safari moved to X” event). Expose “this is the tab I mean” as a one-click/voice handoff and let the owner pin a session until the task ends.
- **owner gets:** The owner will stop getting answers about the wrong Safari tab when another app or tab changes focus. Long browser tasks become dependable instead of silently reading a different authenticated page.
- effort: Medium: extend browser session state, add hash/identity checks to the existing execute bridge, and surface a handoff event to relay and pendant.  ·  risk: A legitimate navigation changes URL/content and could look like drift; recover by treating same tabId/windowId as authoritative, asking only when the tab identity changes, and allowing an explicit rebind. No page content needs to be persisted.
- cost: Negligible storage and compute; one hash per read/action, no additional model call.  ·  latency: Under 50 ms local verification per action; avoids expensive retries and wrong-page model calls.
- security: Improves containment of authenticated data by preventing accidental cross-tab reads. Store only tab identity and content hash, not page text.
- depends on: A functioning browser-current-page context action for voice tasks; Existing GET /browser/sessions and POST /execute session plumbing; An owner-visible session pin/handoff control


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely online now (4 tabs; active authenticated X tab) and POST /execute browser_read_page succeeded, so browser work is no longer blocked by tab availability. This round recorded three new capabilities: page-to-action extraction (read current page, identify deadline, create a provenance-linked reminder), pre-submit authenticated form drafting with spoken exact-field review, and two-tab authenticated reconciliation (compare claims across pinned sessions). It also recorded a browser-harness change: tab identity lease/content-hash handoff so a task cannot silently switch to the wrong logged-in tab. I notified mac-planner of the live state and blockers. A page-watch proposal was correctly rejected as already existing; I will not restate it.

**Biggest unknown:** The missing connective primitive is still a voice-addressable current-page context action with explicit session/tab pinning. Existing /execute and browser sessions can read pages, but the planner lacks a stable way to say “the page I’m looking at” and verify it stayed the same. Also still needed: structured bounded deadline/field extraction and a source-linked reminder/note payload. Owner input is only needed later to populate the deliberately empty per-origin configuration; no site assumptions were made.

