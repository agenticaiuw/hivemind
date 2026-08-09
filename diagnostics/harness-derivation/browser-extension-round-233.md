# Harness derivation — browser-extension — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 4 tabs; POST /execute browser_list_tabs and browser_read_page work. Tabs include X (active), DoorDash checkout, YouTube, and dashboard URL (tab content may change between list and read).
  - evidence: POST /execute browser_list_tabs at 2026-08-09T00:48:36Z returned 4 tabs; browser_read_page at 00:48:41Z returned authenticated X page text.

## Capabilities it proposed

### "“When I say ‘what’s on this page?’, read the active Safari tab, answer the specific question I ask, and speak the answer through my pendant without leaving the page text behind.”"
- **useful because:** The browser is the only node with the owner’s authenticated sessions, while the pendant is the only node available while his hands and eyes are busy. This turns the current tab into a private, voice-queryable surface: a single button/utterance can ask about a shipping status, a dashboard value, or a long document. It is more useful than dumping a page because the relay answers only the asked question and the browser evidence can be cited.
- **path:** pendant → relay-realtime → browser → mac-planner
- **model tier:** Realtime for the short question/answer; do not send the page to the expensive model twice. Browser extracts the addressed page once, a cheap structured extractor selects relevant passages, and realtime verbalizes only the answer. Persist only a short browser finding if explicitly requested.
- **latency:** 2–5 seconds after the page read; up to 10 seconds for a long authenticated application.
- **cost:** Usually one browser_read_page plus a small extraction/realtime turn; roughly $0.01–$0.05 depending on page length. Dominant cost is model context, not browser I/O.
- **security:** Page text and screenshots can contain secrets. Keep content in the in-flight job, apply existing redaction, do not store HTML/screenshots, and return provenance URL/evidence without exposing it in unrelated turns. An empty per-origin configuration remains the owner’s choice. No mutation is involved.
- **missing:** A reliable active-tab/read-page action resolver (the current wrappers ambiguously resolve, although POST /execute already works); A pendant utterance/button event that carries a page-question correlation ID; A bounded in-flight page context handoff from browser to realtime relay

### "“Scan the authenticated page I name for deadlines, renewal dates, or required actions; show me the exact dates and source snippets, then—only after I say ‘schedule them’—create the reminders on my Mac and put a concise alert on my pendant.”"
- **useful because:** Important dates are often trapped behind portals and billing pages that the relay and Mac cannot log into. This bridges browser-only evidence to Mac-native reminders and the always-available pendant, while separating extraction from mutation: the owner gets a verifiable list first, then chooses whether to schedule. It prevents silent calendar pollution and makes an authenticated website useful after the tab is closed.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background extraction/classification for dates and action phrases; realtime only for the owner’s confirmation and a concise spoken summary. Mac action execution should be deterministic once the structured reminder payload is approved.
- **latency:** Read/extract in 5–15 seconds; reminder creation under 3 seconds after approval; pendant alert should arrive within 5 seconds.
- **cost:** One page read and small structured extraction, roughly $0.01–$0.04; Mac reminder and relay delivery dominate no API cost. Re-running should use the page’s content hash to avoid duplicate work.
- **security:** Never retain the page body. Store only date, task, host, URL, short quoted evidence (within existing browser-fact limits), and a content hash with 24-hour TTL. Treat a date as untrusted until displayed with its source. Scheduling is a mutation and must be a separate explicit owner command; the browser must never submit forms.
- **missing:** A browser-page date/action extractor that emits normalized candidates and content hashes; A confirmation payload/receipt that carries the exact reminders from browser to Mac; A relay-to-pendant alert adapter for newly created reminders and a deduplication key

### "“Before I submit anything in Safari, read the form or cart, turn it into a plain-language transaction summary with totals, recipients, dates, and risky fields, and let me compare that summary aloud on my pendant; fill corrections if I ask, but never submit.”"
- **useful because:** The browser can see logged-in checkout and submission forms; the pendant gives the owner an independent channel to catch a wrong address, quantity, subscription, or recipient before an irreversible click. This is not a permission gate—the owner keeps maximum control—it is a human-readable, cross-device checksum and a safe stopping point before submission.
- **path:** browser → relay-realtime → pendant → mac-planner
- **model tier:** Use deterministic DOM extraction and local normalization for fields/totals. Use realtime only to explain anomalies or answer “what changed?”; a cheap model can classify field risk and produce the short summary.
- **latency:** 3–8 seconds for an ordinary form/cart; under 15 seconds for a dynamic checkout.
- **cost:** Mostly browser extraction and deterministic diffing; about $0.005–$0.03 when a model is needed. Screenshots should not be sent unless DOM extraction fails.
- **security:** Treat form values as secrets: keep the complete payload in volatile job scope, redact payment credentials, and persist only a field-name/status receipt and short provenance. Speak sensitive values only when the owner explicitly asks. Do not click submit or send; show the exact proposed mutation and leave the tab unchanged.
- **missing:** A generic browser DOM/form serializer that excludes passwords, card numbers, and hidden tokens; A deterministic canonicalization and diff engine for pre/post form state; A pendant playback payload for a short transaction checksum and an owner-directed correction loop

### "“From the authenticated page I name, fetch the original invoice or statement, save it into my local receipts folder with a useful filename, extract the amount and date, and tell me on the pendant where it was saved.”"
- **useful because:** Important documents often exist only behind a logged-in portal and are easy to lose in browser downloads. This uses Safari’s session to obtain the original artifact, the Mac to store and organize it, and the pendant to confirm completion while the owner is away from the screen. It preserves the document itself locally without sending it to the relay or model for long-term storage.
- **path:** browser → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use browser and local file operations deterministically. A cheaper model may classify the document and suggest a filename; realtime is only for the short completion announcement.
- **latency:** 10–30 seconds for a normal PDF; up to 60 seconds for a portal with a generated download.
- **cost:** Usually under $0.02; dominated by browser download and local file I/O, not inference. No cloud upload should be necessary.
- **security:** The downloaded artifact may contain financial or identity data. Keep it on the owner’s Mac, never upload it to the relay, redact extracted summaries, and write an audit receipt containing only path, host, date, and hash. Do not silently overwrite an existing file; use a collision-safe name and report it.
- **missing:** A browser download action that returns a local artifact handle rather than page text; A Mac-side quarantine, hashing, and receipt step for browser-originated files; A configurable local destination and overwrite policy supplied by the owner

### "“Find a time on this authenticated booking page that fits my Mac calendar, prefer my stated working hours, fill the matching slot, and tell me the exact appointment details on my pendant—stop before the final confirmation.”"
- **useful because:** Booking pages can see availability only through the owner’s logged-in session, while only the Mac knows the owner’s actual calendar conflicts. Combining both avoids the common failure of choosing an available slot that overlaps an existing commitment. The owner retains the final click, but the tedious search and form filling are done for him.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic interval intersection for calendar and page availability; cheap extraction for booking fields; realtime only for preference clarification and the final spoken candidate.
- **latency:** 5–20 seconds for a week of slots; under 5 seconds to fill the selected slot after the owner chooses.
- **cost:** Approximately $0.01–$0.04, mostly structured extraction. Calendar and browser operations are local.
- **security:** Calendar titles and appointment details are sensitive; use only the minimum busy/free data needed and do not persist page text. Never press the final confirmation or send an invite. Show timezone, duration, attendees, location, and price before stopping.
- **missing:** A browser availability-table/form extractor that understands time zones and recurring slots; A calendar busy/free query exposed to the planner without exporting full event details; A robust fill checkpoint that survives a dynamic booking page changing between read and type

### "“Audit my open Safari tabs for active authenticated sessions, tell me which sites are signed in and what each session appears able to access, then log out only the sites I name and verify that the sessions are gone.”"
- **useful because:** The owner can accumulate powerful logged-in tabs without remembering them, especially after using a shared or borrowed Mac. The browser can see session state that the pendant and relay cannot; the pendant provides an immediate voice inventory, and the Mac/browser can perform targeted logout and verify it rather than merely closing a tab.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic tab/session inspection and logout verification; use a cheap classifier for login indicators. Realtime is only for the spoken inventory and selecting sites.
- **latency:** 5–15 seconds for the inventory; under 10 seconds per logout/verification.
- **cost:** Under $0.03 per audit, dominated by browser round trips; no page body needs to reach a model.
- **security:** Do not expose account identifiers beyond the owner’s request, and do not persist session cookies or page text. Logout can destroy unsaved work, so warn about unsaved forms and close only named origins. Record only a minimal success/failure receipt. This is an explicitly requested mutation, not an automatic security policy.
- **missing:** A browser session/login-state inspector that distinguishes signed-in, signed-out, and ambiguous states; Origin-scoped logout workflows with post-logout verification; A concise session inventory delivered to the pendant without speaking secrets


## What it asked for

_Nothing._
