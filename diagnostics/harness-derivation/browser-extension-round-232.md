# Harness derivation — browser-extension — round 232

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari on MacIntel is online with 4 tabs; browser content is now potentially available, unlike the prior zero-tab state, but the granted browser wrappers still do not invoke actions from this agent.
  - evidence: discover devices returned Safari on MacIntel · browser · Safari · 4 tab(s) · online; browser_read_or_navigate(browser_read_page) returned invoked:false and wouldHaveCalled action:browser_read_page.

## Capabilities it proposed

### ""Fill this form with what I just dictated, read it back, and leave it unsent.""
- **useful because:** Dictating into a logged-in web form is high-value and reversible: Safari handles the authenticated site while the pendant handles hands-free input, and the owner gets an exact spoken preview before any irreversible submit.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard-ux
- **model tier:** Realtime for transcription, field mapping, and concise readback; no background model is needed unless the owner asks for a long document.
- **latency:** Field filling within 8 seconds, then immediate readback; never wait on a remote job before showing the draft.
- **cost:** One realtime turn and 2–4 browser actions, approximately $0.02–$0.08; browser round trips and form extraction dominate latency.
- **security:** Never submit, send, purchase, or delete. Limit actions to browser_read_page/browser_type and navigation; preserve an undoable provenance record of changed fields, but never store credentials or full page text. The owner already allows browser clicks but requires confirmation before sending mail, deleting files, or buying.
- **missing:** Reliable browser action invocation through POST /execute; Field-level extraction and a durable undo receipt for browser fills; A clear pendant event to accept/reject the readback

### ""Watch this authenticated page and tell me on the pendant if something important changes.""
- **useful because:** It turns a logged-in Safari session into a personal alert source: the relay can periodically compare a small set of owner-selected claims, while the pendant delivers a short alert even when the Mac link later drops. This is more useful than polling public pages because no other node can reach these sessions.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Cheap background/scheduled extraction and diffing; realtime only when the owner asks follow-up questions or an alert needs spoken phrasing.
- **latency:** Background checks can take 1–5 minutes and tolerate a missed poll; alert enqueue under 10 seconds after a detected change.
- **cost:** A few cents per monitored origin per day depending on cadence and extraction size; browser navigation and authenticated page loads dominate, not model inference.
- **security:** Owner must explicitly configure origins and claims; ship empty config rather than inventing sites. Persist only short claims with URL/evidence capsule under existing browser TTL, never HTML/screenshots. Alerts must identify stale/session-expired state and avoid reading sensitive claim categories aloud unless configured.
- **missing:** A durable browser watch scheduler with session-expiry detection; An explicit empty per-origin read/extract/redact/never-store configuration UI; Relay-to-pendant delivery of browser findings and stale-session errors

### ""Check the two accounts I have open and tell me whether their details agree.""
- **useful because:** Cross-tab reconciliation is not page summarization or monitoring: Safari can hold separate authenticated systems that no other node can access, and the relay can compare only the specific claims the owner asks about. Examples include matching a reservation against a confirmation or an invoice against a portal balance.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for a short comparison after two targeted browser reads; use a cheaper model for long tables only when requested.
- **latency:** Under 10 seconds for two tabs; state clearly if either tab is stale, logged out, or unavailable.
- **cost:** Approximately $0.03–$0.12 per comparison; authenticated page extraction and context size dominate.
- **security:** Read only the two explicitly selected tabs, do not persist source text, and speak only the requested fields. Never infer that a mismatch authorizes a purchase, cancellation, or reply.
- **missing:** A user-facing way to identify two tabs by title/ref from the pendant; Reliable browser POST /execute invocation and multi-tab extraction; A claim-level comparison/redaction step

### ""My login expired—get me back to the page and tell me exactly what I need to do.""
- **useful because:** Authenticated browser automation currently fails opaquely when a session expires. The pendant should receive a concise stale-session alert, Safari should navigate to the site's login/recovery page, and the owner can complete credentials manually while the system never sees or stores the secret.
- **path:** browser-extension → mac-planner → pendant → relay-realtime
- **model tier:** Cheap deterministic session-state detection and navigation; realtime only to explain the recovery screen or answer a follow-up.
- **latency:** Detect on the next requested read, alert within 5 seconds, and leave Safari positioned for manual recovery.
- **cost:** Negligible model cost; one or two browser reads/navigation actions.
- **security:** Never type passwords, OTPs, or recovery codes. Do not scrape login fields. Keep the session-expired event as a short non-sensitive status, and require the owner to handle any challenge or MFA.
- **missing:** Reliable browser action invocation; Session-expiry classification from browser results; A pendant alert route distinct from normal page findings

### ""I’m in a live web meeting—whisper the last few minutes and tell me if I was asked to do anything.""
- **useful because:** The pendant can privately summarize an authenticated meeting or webinar while the owner keeps the meeting open in Safari. This is different from static page explanation: it continuously consumes changing on-screen captions, identifies direct requests, and delivers a short private prompt without interrupting the meeting audio.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap streaming/background extraction for captions and request detection; realtime only for an immediate spoken whisper or follow-up.
- **latency:** Incremental updates every 15–30 seconds, with a spoken alert within 5 seconds when the owner is directly addressed or assigned an action.
- **cost:** Roughly $0.02–$0.10 per meeting hour depending on caption volume; transcription/context processing dominates.
- **security:** Meeting content is highly sensitive. Default to no persistence, no screenshots, host/session indicator in the alert, and an explicit per-session start/stop. Never send extracted content to public search or other participants. Do not activate on a page merely because it resembles a meeting.
- **missing:** A streaming browser-read or caption-delta action rather than one-shot page extraction; A per-session privacy toggle and local discard path; Low-latency relay delivery to the pendant while Safari remains active

### ""Mark the exact place in this private web document where I stopped, and let me resume it from the pendant tomorrow.""
- **useful because:** The owner can consume long authenticated documents hands-free without losing their place. Safari supplies the current document and selection/scroll context; the relay stores only a compact locator and the pendant later reopens the same authenticated page, rather than storing page text.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap deterministic locator extraction and scheduled reopening; realtime only to answer a spoken question about the resumed section.
- **latency:** Bookmark creation under 2 seconds; resume navigation under 8 seconds, with a clear stale-or-moved-target report.
- **cost:** Near-zero model cost; one browser extraction and one navigation per bookmark.
- **security:** Persist only URL origin, document identifier if available, and a structural locator/anchor—not page text, screenshots, or credentials. If the page changed, report uncertainty instead of silently opening a nearby sensitive section. Owner must explicitly start the session.
- **missing:** A browser selection/scroll/anchor extraction action; A durable, page-text-free authenticated resume token; Pendant-triggered reopen and stale-anchor handling

### ""Guide me through this logged-in website hands-free: what can I activate here, and take me to the next control I name.""
- **useful because:** This provides an authenticated web accessibility layer rather than a one-off summary. Safari exposes landmarks, headings, form labels, and focus state; the pendant lets the owner navigate a complex private site by speech while preserving the browser session and avoiding visual screen sharing.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic DOM landmark extraction and focus navigation first; realtime only for ambiguous spoken control names or concise guidance.
- **latency:** Speak the current landmark list within 4 seconds; focus the named control within 3 seconds. Stop before activation unless the owner explicitly asks to activate a reversible control.
- **cost:** Low: mostly browser DOM queries and short realtime turns, approximately $0.01–$0.04 per interaction.
- **security:** Read only the currently visible/accessibility-relevant controls; redact values in password, payment, and secret fields. Never announce hidden fields or credentials. Keep activation scoped to the named control and preserve the owner’s existing destructive-action policy.
- **missing:** Browser accessibility-tree/landmark extraction and focus-control actions; A speech-to-control disambiguation response that names competing matches; A pendant command mode that distinguishes navigation from activation


## Changes it proposed to its own stack

### `browser-harness` — Make one concrete, read-only browser executor callable from this agent: accept an enum of browser_list_tabs, browser_read_page, browser_snapshot, browser_navigate, browser_wait_for, browser_click, browser_type; dispatch to POST /execute and return the extension result (including tabId, title, URL, text, and stale-session errors). Keep browser_type/click available but let each task pass an explicit allow set. This is not a new policy gate; it is the missing invocation path.
- **owner gets:** The owner currently has four live Safari tabs and has granted browser reading, but the pendant cannot answer a question about them because every available wrapper either ambiguously resolves or reports wouldHaveCalled without calling. A working executor turns the browser tier from a promise into something usable today.
- effort: Small-to-medium: publish one unambiguous action contract, wire it to existing /execute enqueue/wait logic, and add result normalization plus timeout/error propagation.  ·  risk: A malformed browser action could navigate or fill the wrong tab. Default read-only action allow set and return tab identity; recover by leaving irreversible submit outside the action enum for this path and preserving existing owner policy.
- cost: No meaningful API cost; one local bridge implementation and browser round-trip per action.  ·  latency: Adds one local round trip, typically under 1–3 seconds; avoids the current 45-second dead-end timeout.
- security: No new access beyond the owner's existing Safari session. Do not log page text, credentials, or screenshots; return redacted/error metadata where possible.
- depends on: POST /execute permission already granted; Safari extension polling/result bridge; A stable action enum matching the live manifest rather than ambiguous aliases


## What it asked for

_Nothing._
