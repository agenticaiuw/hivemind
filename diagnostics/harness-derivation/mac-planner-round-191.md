# Harness derivation — mac-planner — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-perception** — The live Mac bridge now has Accessibility and Screen Recording trusted for AI Pendant Agent; synthesized input is verified, secure input is off, Safari browser bridge is online with 9 tabs and no pending commands.
  - evidence: mac_readonly_inspect operation running_apps/foreground_app at 2026-08-08T02:25:44Z and GET /browser/status

## Capabilities it proposed

### "“Keep my pendant usable while it is plugged into my Mac, even before LTE registration: start a real conversation, stream both audio directions, and tell me when the link is only USB.”"
- **useful because:** The hardware is physically here now but LTE is not registered. This would make the pendant a useful wearable today instead of a silent future device, with the Mac acting as a transparent transport while preserving the same relay conversation semantics.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Realtime only for speech; no model on the USB transport path. Relay routing decides tethered versus cellular from bridge health.
- **latency:** Audio packet forwarding under 30 ms added one-way; link-state announcement within 1 s; no LLM turn added.
- **cost:** Negligible inference cost; roughly 1–2 engineering weeks for a serial/WebSocket daemon, framing tests, and reconnect handling.
- **security:** USB audio and control remain on the owner's Mac; do not expose the serial port to LAN. Pair by device serial and require an explicit tether mode; never silently fall back from cellular to a host that is not trusted.
- **missing:** mac_serial_exchange (the requested tool is still unavailable); A small signed Mac USB transport daemon for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Relay device state that accepts a tether transport as equivalent to an LTE session

### "“I marked something on my pendant earlier—bring that moment to this Mac, show me the related page or note in my current browser, and make a short dated note without making me repeat it.”"
- **useful because:** The pendant is the only surface present at the moment of capture, while the Mac and authenticated Safari session are the only surfaces able to retrieve and organize context. This closes the gap between an offline bookmark and actually finding the work again.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Cheap background classifier for matching the bookmark to recent browser tabs/calendar/mail; realtime model only if the owner asks a follow-up question.
- **latency:** A spoken retrieval answer in 2–5 s; open the chosen tab and create the note atomically within 8 s.
- **cost:** One small background classification call, typically <$0.01; Mac/browser work dominates latency, not tokens.
- **security:** Only use the owner's existing Safari session and redact page body by default. Never create or send external content without a separate explicit request; show the matched URL/title and confidence in the spoken receipt.
- **missing:** A relay endpoint that exposes offline_moment_bookmark records to the Mac planner with stable event IDs; A browser command to open a matched existing tab or URL and return title/URL; A deduplicating note writer keyed by bookmark event ID

### "“Before you buy, delete, or send anything from my Mac or authenticated browser, read me exactly what will happen; commit only when I confirm on the pendant.”"
- **useful because:** The owner explicitly wants confirmation for buying, deleting files, and sending mail, but the current FULL_CONTROL_MODE has no approval gate. A spoken two-phase commit makes the wearable the confirmation surface while the Mac/browser retain the reach to perform the action.
- **path:** relay → pendant → mac-planner → browser-extension
- **model tier:** Realtime model extracts the requested operation and produces a concise preview; deterministic action classification and commit token handling should not use an LLM.
- **latency:** Preview within 2 s, pendant confirmation window 30 s, execution and receipt within 5 s after confirmation.
- **cost:** At most one short realtime turn per risky action, usually <$0.01–$0.05; no call for deterministic receipt or timeout.
- **security:** The preview must include target, account, amount/path, and irreversible effects, with secrets redacted. Confirmation token must be one-shot, bound to exact action hash, device/session, and expiry; timeout cancels. This is a narrow user-facing commit flow, not a blanket policy rewrite.
- **missing:** An action preflight result wired into relay plans, including browser operations (current mac_action_preflight covers Mac action lists only); A relay-held one-shot confirmation token endpoint and pendant confirm/cancel event; A commit adapter that passes the exact approved plan to POST /execute or browser enqueue

### "“When I press the diagnostic button, turn the pendant’s UART failure log into a concise bug report, attach the measured audio counters and firmware build, and leave a draft issue in my workspace for me to review.”"
- **useful because:** The owner explicitly wants a pendant that files its own bug reports. It would convert hard-to-interpret serial evidence into an actionable artifact without requiring the owner to copy logs or remember which build produced them; importantly, it stops at a local draft rather than silently publishing.
- **path:** pendant → mac-planner → relay → browser-extension
- **model tier:** Cheap background model extracts symptoms and writes the draft; deterministic parser supplies counters, timestamps, device ID, and build hash. Realtime is unnecessary.
- **latency:** Collect the bounded UART window in under 3 s; draft within 15 s; no interruption to an active call.
- **cost:** Usually <$0.02 per diagnostic draft; storage and serial transfer dominate, with no browser model call unless the owner asks to publish.
- **security:** Keep raw logs local by default and redact tokens/paths before sending a summary upstream. Draft is never submitted automatically. Attach only the diagnostic fixture output, not microphone PCM or ambient recordings.
- **missing:** A firmware diagnostic-button/serial arm command that emits a bounded, tagged log bundle (the accepted fixture currently has a serial trigger but no report contract); mac_serial_exchange or an equivalent allowlisted reader for the two live USB serial devices; A local draft/issue template writer with build and counter fields

### "“If I give you an instruction while I’m offline—‘when I’m back at my Mac, save this page to the project and remind me tomorrow’—remember the exact intent, then resume it later against the current browser and files without making me repeat myself.”"
- **useful because:** Today the pendant can preserve a moment or voice memo, but it cannot preserve an actionable, target-bound instruction and safely finish it after the owner moves between dead zones, Mac, and authenticated browser sessions. This is the difference between recording what was said and carrying work across an interruption.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime model only parses the spoken instruction at capture time; a cheaper background model resolves references and checks whether the original target still exists when connectivity returns. Deterministic execution handles the final Mac/browser plan.
- **latency:** Offline capture acknowledgement under 300 ms; reconciliation within 10 s of link restoration; stale-target preview within 2 s before any mutation.
- **cost:** About $0.01–$0.04 per deferred instruction, dominated by one short parse and later reference resolution; no cost while merely queued.
- **security:** Persist the minimum structured intent, not ambient audio by default. Bind each instruction to an owner/device/session and an expiry. If the page, account, path, or requested effect changed, do not guess: speak the mismatch and require a new confirmation for sending, deleting, purchasing, or other irreversible action. Encrypt the pending intent locally and erase it after receipt or expiry.
- **missing:** A new durable deferred-intent record distinct from the existing voice-memo/bookmark payloads, with target fingerprints, expiry, and idempotency key; Relay reconciliation that turns a queued intent into a current Mac/browser plan and reports stale-target conflicts; A resume executor that can atomically apply safe steps and return a spoken completion or conflict receipt

### "“When I’m wearing the pendant and ask ‘what am I looking at?’, inspect the current Mac window and browser page, explain the important controls or error in one short spoken sentence, and include the exact place I can return to.”"
- **useful because:** The pendant has no display, while the Mac has the visual and authenticated browser context. Today those surfaces can be inspected separately, but they do not produce a concise, location-preserving spoken explanation for a wearer who cannot stop to read the screen.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay
- **model tier:** A local/cheap vision model handles screenshot plus accessibility tree; realtime is reserved for the owner’s follow-up conversation. Browser DOM and URL extraction should be deterministic, with no model call when the page is simple.
- **latency:** Capture and answer in 3–6 s; URL/window identity returned with the sentence; stop immediately if the foreground app changes during capture.
- **cost:** <$0.02 for a bounded screenshot/tree interpretation; local capture and speech delivery dominate latency.
- **security:** Redact password fields, secure-input windows, and unrelated background apps before inference. Do not transmit the full screen by default: crop to the foreground window and send only the extracted explanation and return location after the turn. Authenticated page content must remain scoped to the owner’s active browser session.
- **missing:** A stable semantic UI snapshot contract with roles, labels, selected state, and window identity (not just pixels); A browser inspection result that returns the active tab’s title, URL, and bounded relevant DOM text without resolver ambiguity; A relay request/response envelope joining the Mac snapshot to one pendant spoken turn

### "“Read the useful parts of the authenticated page I’m on through the pendant while I’m away from the Mac; let me say ‘skip’, ‘go back’, or ‘bookmark this paragraph’, and stop when the page changes.”"
- **useful because:** A browser session can reach pages the pendant cannot, and the pendant can deliver audio where the Mac cannot follow the owner. Today there is no durable, page-bound narration channel with spoken navigation and a bookmark tied to the exact paragraph, so the owner must remain at the screen.
- **path:** browser-extension → relay → pendant → mac-planner
- **model tier:** Cheap background extraction/chunking for the page; realtime handles only low-latency skip/back/bookmark commands. Use deterministic text extraction and sentence boundaries rather than repeatedly sending the whole page to the model.
- **latency:** Start playback within 3 s; skip/back response under 500 ms; page-change cancellation under 1 s; bookmark acknowledgement under 1 s.
- **cost:** Roughly $0.01–$0.05 per page depending on length, with caching by page revision so navigation costs almost nothing; audio bandwidth is the main ongoing cost.
- **security:** Read only the active tab and bounded visible/article content, never hidden fields or other tabs. Detect URL/DOM revision and cancel on navigation. Store only a short redacted excerpt plus URL and paragraph locator for a bookmark; do not retain the full authenticated page.
- **missing:** A page-to-speech stream with chunk IDs, sentence boundaries, and cancel-on-revision semantics; Low-latency pendant playback controls mapped to skip/back/bookmark events without confusing them with existing recording/bookmark button behavior; A browser content extractor that can identify a stable paragraph locator and return revision changes


## What it asked for

_Nothing._
## Its own summary

Discovered live state: the Mac bridge is online, AI Pendant Agent now has Accessibility and Screen Recording, synthesized input is verified, Safari’s bridge is online with 9 tabs and zero pending commands. I recorded that finding. I submitted four new owner-facing capabilities: USB-tethered pendant voice transport while LTE is unregistered; bookmark-to-current-workspace recovery; pendant-confirmed two-phase commit for destructive Mac/browser actions; and diagnostic UART log to local bug-report draft. The recorder accepted all four, while warning that the tether and bug-report ideas are adjacent to earlier backlog entries, so future work must focus on the missing transport/report contracts rather than re-describing them.

**Biggest unknown:** The requested mac_serial_exchange capability is still unavailable, so I cannot read or drive /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA from this agent. That blocks validating the USB tether and UART bug-report flows. Browser tab inspection is also currently resolver-ambiguous between browser_inspect and POST /browser/inspect; the live /browser/status route confirms Safari is online, but not page contents.

