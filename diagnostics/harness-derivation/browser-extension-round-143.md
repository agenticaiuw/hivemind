# Harness derivation — browser-extension — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari extension is online with 9 tabs; active tab is platform.openai.com Billing overview, tabId 1148327, and no commands are pending.
  - evidence: GET /browser/status returned online=true, tabCount=9, tabUrl=https://platform.openai.com, pendingCommands=0 at 2026-08-08T01:05:39Z.

## Capabilities it proposed

### "When I'm viewing a logged-in web page, turn any explicit deadlines, appointments, or required actions on it into draft reminders with the exact source link and quoted evidence; let me review the drafts from the pendant before saving them."
- **useful because:** Important dates buried in portals become actionable without copy/paste, while preserving provenance and avoiding accidental calendar changes.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** background for page extraction and date normalization; realtime only for the pendant's short review conversation
- **latency:** Under 10 seconds to inspect the active page; review is conversational
- **cost:** About $0.01–$0.04 per page batch; browser extraction and Mac reminder creation dominate latency, not tokens
- **security:** Reads authenticated page text and may expose dates or names to the relay; transmit only relevant excerpts, retain URL/evidence hash, and never save until owner explicitly accepts the draft set. Form submission is out of scope.
- **missing:** active-page deadline/action extractor with evidence spans; draft reminder queue with accept/reject per item; browser-to-Mac reminder handoff; pendant review of a multi-item draft set

### "Watch the price, availability, or appointment slots on this authenticated page and alert me only when the meaningful value changes, with the old and new values and a link; keep checking even when the page is no longer open."
- **useful because:** The browser can reach private pricing and scheduling portals that public search cannot, and the pendant can deliver a short alert without making the owner repeatedly revisit the site.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** scheduled/background extraction with a cheap model; realtime only to speak an alert or answer follow-up
- **latency:** Initial setup under 15 seconds; checks can run on a configurable schedule, alert delivery within one check interval
- **cost:** Roughly $0.01–$0.08 per check depending on page size; polling and authenticated browser execution dominate
- **security:** Origin credentials remain in Safari; send only the selected field and evidence, redact account/order data, encrypt watch state, and provide a visible pause/delete control. Never purchase or book automatically.
- **missing:** owner-created watch definition from a page selection; durable scheduled browser session re-open/check runner; semantic value extraction and old/new diff; offline alert delivery integration

### "Save the useful part of the page I'm viewing as a personal handoff: capture the URL, title, selected passage, and why I saved it from my spoken note, then put it in my Mac notes or project context so I can continue later."
- **useful because:** A fleeting authenticated page becomes a searchable, attributable piece of work context without screenshots, manual copying, or losing the reason it mattered.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** realtime for turning the spoken note into a short label; background for deduplication and indexing
- **latency:** Under 5 seconds from button/voice request to confirmation
- **cost:** Under $0.02 per handoff; extraction and local persistence dominate
- **security:** The selected passage may contain private information; keep raw text local where possible, apply origin redaction rules, store a short excerpt plus hash and source URL, and make deletion available. Do not share the handoff externally.
- **missing:** browser selection/active-page capture with stable passage anchors; spoken-note attachment to a capture; Mac Notes/project-context writer with provenance; deduplication and deletion UI

### "Handle a private web task end to end across my logged-in tabs and Mac: find the right record, reconcile it against my local calendar or notes, fill every reversible field, and return a spoken checklist of exactly what is ready to submit—then resume from that checkpoint when I say continue."
- **useful because:** This is the first capability that turns browser access into real personal assistance rather than page reading: it can bridge private portals and local context, survive interruptions, and eliminate repetitive clerical work while leaving the final irreversible click explicit.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → dashboard
- **model tier:** background planner for decomposition and reconciliation; realtime only for clarifying ambiguous records and the final spoken checkpoint
- **latency:** 30–90 seconds for a multi-tab task; checkpoint must be available even if Safari or the relay drops
- **cost:** $0.05–$0.30 per task; browser round trips and computer-use retries dominate, with model cost rising for ambiguity
- **security:** Private page contents, calendar, and notes cross the browser/Mac boundary; keep raw page text ephemeral, log every field change and URL, bind the plan to tab/session identity, and never submit, send, purchase, or delete without an explicit continuation command. Recovery must reopen the exact checkpoint, not restart blindly.
- **missing:** durable cross-surface task plan and checkpoint store; record identity reconciliation between browser content and local apps; field-level browser action receipts and replay from checkpoint; continuation command routed from pendant to the same browser session

### "When my Mac or Safari restarts, restore the private web work I was in the middle of—including the exact tabs, scroll positions, search filters, and unsent form fields—so I can continue from the pendant without losing the task."
- **useful because:** A laptop restart, crash, or accidental tab close should not destroy hours of authenticated work or force the owner to reconstruct a delicate workflow from memory. This would preserve continuity in the one place where the browser has private session access.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** background state capture and restoration; realtime only for a short spoken confirmation or ambiguity about which workstream to restore
- **latency:** Capture incrementally with negligible interaction cost; restore within 15 seconds after Safari reconnects
- **cost:** Under $0.02 per restore; storage and browser round trips dominate, with no need for expensive model calls unless state is ambiguous
- **security:** Saved state can contain private URLs, form contents, tokens, and sensitive text. Keep field values encrypted on the Mac, never send raw form state to the relay, expire snapshots, bind them to origin and browser profile, and visibly list/delete saved workstreams. Restoration must never submit a form or trigger a purchase.
- **missing:** incremental browser workflow snapshots including scroll/filter/form state; encrypted local snapshot storage with expiry; tab/session restoration after extension reconnect; conflict detection when the underlying page changed; pendant command to list and resume named workstreams


## What it asked for

_Nothing._
