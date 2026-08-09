# Harness derivation — browser-extension — round 220

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at a logged-in webpage in Safari—answer my spoken question about this page, using the exact visible evidence, but forget the page as soon as you answer.”"
- **useful because:** This is the single most useful browser capability: the owner can ask about bills, dashboards, tickets, or forms that the other agents cannot access, without copying private text into chat or teaching the system a site-specific routine. The active Safari session is the private reach; the pendant is the natural query and answer surface.
- **path:** pendant → browser → relay-realtime → mac-planner
- **model tier:** Browser extracts the current page or selected region; a small model answers grounded only in that extraction; realtime handles the short spoken exchange.
- **latency:** Under 5 seconds from button/voice request to answer for a normal page; no background polling.
- **cost:** One extraction plus one small grounded answer per question; page text is held only in an in-memory request capsule and not sent to long-term memory.
- **security:** Must require an explicit owner gesture or spoken wake phrase to read the active authenticated tab. Redact secrets and form fields by default; never persist HTML, screenshots, or page text. Return citations as page title/heading/URL, while applying existing browser-fact TTL rules only if the owner explicitly asks to save a claim.
- **missing:** A resolved browser_read_current_page/current-tab action (the currently granted resolver is ambiguous); A transient page-context channel from browser result to relay voice turn; A strict no-persist execution mode that bypasses browser-finding memory writes

### "“When I say ‘turn this into a reminder,’ take the appointment, deadline, or renewal date from the authenticated Safari page I’m viewing, show me the exact reminder text and date on the pendant, and create it on my Mac with an undo trail.”"
- **useful because:** It closes the gap between private web information and the owner’s actual life: no copying dates from portals, receipts, or booking pages. Browser has the login, Mac has Reminders, and the pendant makes the extracted fact reviewable while walking away from the screen.
- **path:** browser → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Cheap structured extraction for date/title/location; deterministic reminder creation; realtime only for the spoken request and concise read-back.
- **latency:** Extract and preview in 3 seconds; create within 5 seconds after the owner’s explicit command; undo available immediately.
- **cost:** One browser extraction and occasional small parse call; Mac reminder action and receipt are local. No repeated polling.
- **security:** Only operate on the active tab after an explicit request. Show the exact title/date/time/time-zone and source URL before writing. Store claim provenance and an undoable job receipt, not page text. Treat ambiguous dates and recurring events as unresolved rather than guessing.
- **missing:** A browser-to-structured-field extraction contract that returns evidence spans without persisting page content; A pendant display/audio preview protocol for structured web findings; An atomic bridge from browser provenance to POST /reminders with an undoable job receipt

### "“If I long-press the pendant and say ‘privacy,’ immediately hide my authenticated Safari tabs, cancel queued browser commands, and erase transient page material from the relay; when I unlock, restore only the tab URLs, not their contents.”"
- **useful because:** The pendant is the one control the owner has in hand when leaving the Mac or noticing someone nearby. Today a logged-in browser session and queued page results can remain exposed. This makes physical presence a privacy control spanning gadget, extension, relay, and Mac rather than a browser preference the owner has to reach.
- **path:** pendant → relay-realtime → browser → mac-planner → dashboard
- **model tier:** Firmware and relay state machine, no model call. A cheap deterministic command cancels browser jobs and broadcasts a privacy mode; realtime is not on the critical path.
- **latency:** Under 1 second to stop new browser work and mark the relay private; tab hiding/closing within 2 seconds; restoration only on an explicit unlock.
- **cost:** Negligible API cost; extension command and relay state update dominate.
- **security:** The panic action must be local/button-triggered and work even if speech or LTE is unavailable, with a clearly visible LED state. Keep only encrypted tab URLs/session identifiers needed for restoration, never page contents or screenshots. Do not silently submit forms or mutate sites. Provide an audit event and a local recovery path if a command is interrupted.
- **missing:** A pendant privacy-mode device skill with a dedicated long-press path and local queued state; Browser extension actions for hide/close tabs and cancellation acknowledgement, plus a privacy-mode heartbeat; Relay-wide transient context purge and a deterministic restore-URLs-only flow

### "“Compare the statement or invoice I’m viewing in my logged-in browser with the last one I approved, tell me exactly what changed, and—if it looks normal—archive only a compact comparison; if it looks unusual, alert me on the pendant.”"
- **useful because:** The owner gets a private, cross-surface anomaly check that neither a generic browser reader nor the Mac’s ordinary finance integrations can provide: Safari supplies the authenticated current document, the Mac performs a local structured comparison, and the pendant surfaces an actionable exception without reading the whole document aloud.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Browser extraction plus deterministic field comparison first; a small model handles layout variation and explains only the deltas; realtime is used only for an on-demand spoken explanation.
- **latency:** One-shot comparison in 5–10 seconds; anomaly alert within 2 seconds after extraction; no continuous polling required.
- **cost:** One browser extraction and one small normalization call per comparison; local diffing dominates neither latency nor cost. Persist at most a compact, redacted comparison record.
- **security:** The owner explicitly chooses the active page and comparison target; do not infer financial sites or categories. Require field-level extraction confidence and show source URL, period, totals, and changed fields before archiving. Never retain statement HTML, screenshots, account numbers, or full line items; encrypt and TTL the comparison. Anomalies must be phrased as differences, not fraud claims.
- **missing:** A structured authenticated-document extractor that emits typed fields plus evidence spans without retaining page content; A local comparison store with owner-approved baseline selection, redaction, encryption, and short retention; A pendant alert payload for a bounded anomaly summary and a follow-up drill-down request; An explicit browser-to-Mac handoff tying the extraction to the chosen baseline and an undo/delete receipt

### "“Read the choices on this logged-in webpage, number them, and let me choose one from the pendant; move Safari to that choice and read the next step, but never submit anything.”"
- **useful because:** It makes dense authenticated web interfaces usable while the owner is away from the screen or has limited vision. The browser contributes session access and exact controls, the relay turns them into a small spoken menu, and the pendant provides a physical selection channel. This is more than page summarization: it is reversible, stateful navigation without sending a form.
- **path:** browser → relay-realtime → pendant → mac-planner
- **model tier:** Deterministic DOM/accessibility-tree extraction and selector mapping; small model only normalizes labels; realtime handles the low-latency spoken menu.
- **latency:** Menu in 2–4 seconds; selection acknowledgement under 1 second; stop immediately on navigation or ambiguity.
- **cost:** One browser read and a cheap label-normalization call per step; no background model work.
- **security:** Default to an action allow-set containing read, focus, scroll, and highlight only. Never click submit, send, purchase, delete, or equivalent. Speak labels but redact detected secrets. Preserve a short navigation receipt and URL, not page content; abort if the page changes or a selector is ambiguous.
- **missing:** A browser accessibility-tree/choice extraction action with stable element IDs; A pendant menu/selection firmware skill that supports numbered options and timeout/cancel; A browser action that focuses/highlights an element without activating it; A relay state machine joining spoken menus to one authenticated browser session

### "“Tell me before an authenticated Safari session is about to expire, identify which unsent drafts or partially completed pages would be lost, and save only a local recovery note—not the private page contents.”"
- **useful because:** Session expiry is a uniquely browser failure that can silently destroy work behind login. Safari can see the real session and form state, the Mac can checkpoint safe metadata, and the pendant can warn the owner while there is still time to act. It prevents lost work without automating a sensitive submission.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic cookie/session and form-state signals; no expensive model unless the owner asks for a plain-language explanation of what is at risk.
- **latency:** Detect within 30 seconds of a session warning; pendant alert under 2 seconds; recovery note written locally within 1 second.
- **cost:** Negligible model cost; extension polling and local encrypted metadata storage dominate.
- **security:** Never read or persist field values by default, especially passwords, payment data, or message bodies. Store only origin, page title, field names/counts, URL, and a local timestamp, encrypted and short-lived. The owner explicitly chooses origins; no assumptions about work portals. Do not refresh or re-authenticate automatically; surface the exact action needed.
- **missing:** Extension telemetry for session-expiry/reauthentication warnings and unsaved-form presence; An encrypted local recovery-note store with field-name-only redaction guarantees; A relay-to-offline-alert-inbox adapter with deduplication and severity; A dashboard to inspect and delete recovery notes


## What it asked for

_Nothing._
## Its own summary

Discovered Safari is now online with 2 tabs and the Mac bridge is online. The newly granted browser wrapper still cannot resolve list-tabs because the live resolver confuses browser_list_tabs with browser_list_sessions; I did not guess or cause a browser side effect. I recorded three non-duplicate capabilities: ephemeral grounded Q&A about the active authenticated page, page-to-reminder extraction with provenance/undo, and a pendant-triggered privacy panic mode that hides tabs and purges transient page context. The first is the highest-value browser capability and requires no persistence of page text.

**Biggest unknown:** Whether the live extension can return the active tab/page content and acknowledge hide/cancel commands. The missing product pieces are a resolved current-page read, transient no-persist context path, structured evidence-to-reminder bridge, and a firmware/browser privacy-mode handshake. I still need the owner to supply explicit per-origin rules when ready; I will not invent sites or sensitivity categories.

