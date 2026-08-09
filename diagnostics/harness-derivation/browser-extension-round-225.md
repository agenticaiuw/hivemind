# Harness derivation — browser-extension — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with two tabs: active YouTube video “Max Hodak: Average Is Not Good Enough” (tabId 3186198) and inactive Google News search (tabId 5688537). browser_list_tabs and browser_read_page both work through POST /execute.
  - evidence: POST /execute actions browser_list_tabs and browser_read_page returned status success at 2026-08-09T00:24:31–36Z.

## Capabilities it proposed

### "“Compare what this logged-in page says with the latest public information and tell me if anything conflicts.”"
- **useful because:** Only the browser can read the owner’s authenticated account while the relay can obtain current public facts. It would catch stale balances, policy mismatches, shipment/status discrepancies, or account notices without exposing page text to other surfaces; the pendant gets a concise discrepancy report with links and evidence.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background/cheap model for extraction and comparison; realtime only to turn the final discrepancy into a short spoken answer.
- **latency:** 5–15 seconds for a two-source comparison; the browser read and public fetch dominate.
- **cost:** Roughly $0.01–$0.05 per comparison, dominated by page extraction and one background reasoning call; no expensive realtime turn unless spoken interactively.
- **security:** The browser page may contain private account data. Send only bounded extracted claims and provenance, never HTML, screenshots, or full page text. Default to the existing 24-hour browser-fact TTL and 200-character cap; an explicit empty per-origin policy remains the owner’s choice. Never act on a discrepancy automatically.
- **missing:** A comparison orchestrator that can request one authenticated browser read and one public fetch, normalize claims, and return an evidence-linked diff; A compact spoken discrepancy card in the pendant protocol; Owner-configurable per-origin extraction/redaction rules (ship empty)

### "“Check this logged-in appointment page against my calendar, find conflicts, and prepare the best reschedule options without changing anything.”"
- **useful because:** The browser is the only node that can see appointment portals behind the owner’s login; the Mac can see the local calendar and calculate conflicts; the relay can rank alternatives and the pendant can announce the result while the owner is away from the screen. It turns an opaque portal visit into an actionable schedule decision, without submitting a cancellation or booking.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background extraction and deterministic calendar overlap calculation; realtime only for the owner’s follow-up conversation.
- **latency:** Under 20 seconds for one appointment and a local calendar window; browser read and calendar query run in parallel.
- **cost:** About $0.01–$0.04 per request; mostly one extraction/summarization call. Calendar comparison itself is local and cheap.
- **security:** Keep appointment details as short-lived, host-keyed claims; do not persist page HTML or screenshots. Return only the minimum title/time/location needed for conflict computation. Present alternatives as a preview; do not click cancel, reschedule, or book.
- **missing:** A bridge that maps browser-extracted date/time/location claims into the Mac calendar query and back into a ranked alternative list; A browser locator strategy for appointment details across unknown origins; A spoken result format that can distinguish confirmed appointment facts from inferred free slots

### "“Privacy now: hide every authenticated Safari page, and tell me when it is safe to restore them.”"
- **useful because:** A worn button is the fastest trustworthy signal that someone is looking over the owner’s shoulder. The pendant can trigger it even when the Mac is across the room; the relay can fan the command to Safari, which navigates each private tab to a safe interstitial while retaining only encrypted restoration handles. The owner gets a spoken acknowledgement and can restore later without hunting through windows.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No LLM needed for the panic action; deterministic relay and extension logic. Use a cheap model only if the owner asks which tabs were affected.
- **latency:** Under 2 seconds from button press to all tabs receiving the hide command; extension polling is the limiting factor.
- **cost:** Negligible API cost; one small relay event and one browser command batch. Storage is a bounded encrypted list of tab IDs and original origins/URLs, not page contents.
- **security:** This is deliberately destructive-looking but reversible: never persist page text, cookies, or screenshots; restoration handles must be encrypted and expire. A hidden tab may still have unsaved form input, so the default must warn that unsaved edits cannot be recovered. Restoration should require a deliberate pendant action, but not an LLM confirmation.
- **missing:** A firmware trigger mapped to a privacy panic event (button gesture or dedicated physical event); A browser action to replace all matching authenticated tabs with a local neutral page and later restore their URLs; Encrypted, expiring tab-handle storage shared between relay and extension; An extension acknowledgement that distinguishes every-tab success from partial failure

### "“Use the text I’m currently highlighting in Safari: explain it in plain language, then draft a reply in the same page’s reply box—but do not submit it.”"
- **useful because:** Today the owner must copy sensitive authenticated text into chat, explain which passage matters, and manually paste the draft back. A browser extension can capture only the current selection and its DOM context, while the relay reasons over that bounded snippet and returns a draft to the exact originating field. The Mac/browser combination can leave the draft visibly in place, and the pendant can read a short explanation while the owner keeps working. This is a private, precise bridge between a page the browser can see and a physical conversational interface; no page-wide scrape is needed.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime for the owner’s spoken explanation and draft; use a small fast model because the input is a bounded selection, with no need to resend the whole page.
- **latency:** 2–5 seconds from selection request to spoken explanation; under 8 seconds to place the draft in the originating field.
- **cost:** About $0.003–$0.02 per invocation, dominated by one short model call and the browser round trip.
- **security:** Transmit only the selected text, nearby labels, origin, and field identifier; never send the rest of the page, cookies, or screenshots. Do not persist the selection or draft by default. If the page is a message composer, stop before submission and show the exact proposed text on-screen and over audio.
- **missing:** A browser extension action that returns the user’s current selection plus a stable field/DOM locator; A relay operation that binds a response to the originating tab and selection, rather than a generic page read; A browser type operation that can target the originating reply field and report whether the inserted draft remains undoable; A pendant interaction for “explain and draft this” while the owner is hands-free


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely usable now: I listed two live tabs and read the active YouTube page through POST /execute (the wrapper tools remain ambiguous, but the underlying route works). I recorded three new cross-surface capabilities: authenticated appointment-vs-calendar conflict checking, a pendant-triggered Safari privacy panic/hide-and-restore flow, and authenticated/public discrepancy comparison. The recorder flagged each as adjacent to existing backlog, so I did not rephrase them further; the privacy flow is the most distinct and immediately owner-visible.

**Biggest unknown:** The remaining blocker is not page access: it is the missing connective behavior. I still need a real pendant privacy event, an extension action that hides/restores all authenticated tabs with encrypted expiring handles, and a browser-to-Mac calendar/claim bridge. The granted browser_read_current_page/focus tools still do not resolve; POST /execute is the working path today.

