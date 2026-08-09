# Harness derivation — mac-planner — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac accessibility and screen capture state** — Live observe reports Accessibility trusted, synthesized events posting, Screen Recording true, secure input false, and UI actions will reach the screen for AI Pendant Agent. Foreground is loginwindow; 20 apps running and four durable browser sessions exist.
  - evidence: mac_readonly_inspect operation=running_apps invoked GET /observe at 2026-08-09T00:24:30Z, HTTP 200.

## Capabilities it proposed

### "When my calendar meeting ends, capture where I actually left off and give me a one-sentence handoff when I pick up the pendant again."
- **useful because:** The useful state is not the meeting transcript: it is the exact work context abandoned when the meeting began. The relay can join the pendant's moment bookmark with Calendar, the Mac's foreground/document state, and browser tabs, then produce a durable, privacy-redacted re-entry card. A later button press speaks the next action and the Mac can reopen only the explicitly recorded resources.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for card construction; realtime only for the later one-sentence spoken pickup
- **latency:** Capture under 3 seconds at meeting end; pickup speech starts under 2 seconds; card generation can finish within 30 seconds.
- **cost:** About $0.01–$0.04 per meeting card depending on context length; most cost is one background summarization call, not the short pickup response.
- **security:** Calendar title and active URLs/document names may be sensitive. Keep raw context on the Mac, send only redacted identifiers and snippets to relay, encrypt the card at rest, expire it after 7 days, and never reopen a resource without an explicit pickup command. The owner has allowed browser reads but destructive actions still require confirmation.
- **missing:** A semantic Mac read for active document/window identity and selected text (the current observe route gives host state and tabs but not reliable document identity).; A calendar event-boundary trigger that correlates an offline_moment_bookmark to the just-ended event.; A durable handoff-card record and pendant command to retrieve one card.

### "Run a pendant health check now, and tell me whether the microphone, 24 kHz playback, modem path, and USB bench connection all pass; if anything fails, leave a timestamped report beside the project."
- **useful because:** Today the board is physically attached over USB but not LTE-registered, so a user can test the entire audio path without pretending the cellular link is healthy. This turns the accepted diagnostic fixture into an owner-facing release gate: one spoken verdict, machine-readable counters, and a report an engineer can act on.
- **path:** pendant → mac-terminal → mac-planner → relay → dashboard
- **model tier:** background deterministic parser for UART counters and report generation; realtime only to speak the final verdict
- **latency:** Start immediately and return a first status within 2 seconds; fixture and parse complete within 60 seconds.
- **cost:** Under $0.01 per run; shell execution and deterministic parsing dominate, with no model call required unless the owner asks for explanation.
- **security:** The report may contain filesystem paths and serial diagnostics, but never microphone samples. Restrict writes to ~/AI-Pendant-Workspace/diagnostics, include hashes and firmware version, and do not infer LTE failure as an audio failure. USB serial commands must be bounded and logged.
- **missing:** A real bounded bidirectional USB-serial harness for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; the current inventory has no serial route and arbitrary run_shell receipts lack reliable exit status.; A stable diagnostic command protocol that arms s16-dbfs over USB and emits a machine-readable completion marker.; A report adapter that distinguishes 'LTE unavailable' from local audio/codec failures.

### "Watch my signed-in browser sessions for security-relevant changes, and alert me on the pendant only when a session logs out, lands on a new domain, or hits a permission/verification prompt."
- **useful because:** A browser session can silently expire or be redirected while the owner is away from the Mac. The browser extension can observe the session boundary, the relay can classify only high-signal changes, and the pendant can surface a short alert without exposing page contents. This is a cross-node safety net rather than a task-specific website automation.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** cheap background classifier over URL/title/status metadata; realtime only when the owner asks 'what changed?'
- **latency:** Detect within 10 seconds of a heartbeat; speak an alert within 3 seconds after classification; no polling faster than once per 10 seconds.
- **cost:** A few cents per day at most; polling/heartbeat is the dominant cost, and classification can be rules-first with no model call for obvious logout or domain changes.
- **security:** Never send page bodies, cookies, form values, or screenshots to relay by default. Store only origin, title hash, session id, and reason code. Domain allow/deny policy must be owner-configurable. A prompt alert must not auto-click or approve anything; the owner must explicitly ask for browser action.
- **missing:** A browser-session event stream with old/new origin, authentication-state, and prompt indicators rather than one-shot inspect.; A relay-side debounce and per-session baseline store with retention limits.; An existing pendant alert-inbox payload field for reason codes and expiry (reuse the inbox, not another device queue).

### "After you do something on my Mac or in my browser, tell me whether the intended result is actually true—not merely whether the click or command ran—and let me ask the pendant for the proof later."
- **useful because:** A successful UI event is not a successful outcome: a click can hit the wrong tab, a file write can land in the wrong folder, and a browser form can be rejected after submission. The owner should receive a short spoken receipt grounded in an independent read-back, with the exact evidence retained for later inspection. This turns automation from 'I tried' into 'the world now matches the request.'
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic postcondition checks first; cheap background model only to map a natural-language goal to a bounded verifier; realtime for the owner's follow-up question
- **latency:** Return action plus verification within 5 seconds for local files/UI state and within 15 seconds for browser/network results; later pendant proof lookup under 2 seconds.
- **cost:** Usually under $0.01 per action because read-back is local; model cost appears only for ambiguous goal-to-postcondition mapping.
- **security:** Evidence must be redacted before relay storage and must never include passwords, cookies, or full private page bodies. Sending mail, deleting files, buying, and other destructive outcomes remain confirmation-gated by owner policy. A failed verification must be reported as unknown or failed, never upgraded to success from the action receipt alone.
- **missing:** A typed postcondition schema attached to every Mac/browser action, with observable checks such as file hash/path, window state, URL/title, or returned page confirmation.; An independent verifier that runs after execution and records evidence separately from the executor receipt.; A durable pendant query keyed by job id that can speak the last verified outcome and its uncertainty.


## Changes it proposed to its own stack

### `mac-harness` — Add a first-class bounded USB bench harness for the two physically attached chips: allowlist the nRF9160 modem port and ESP32 bridge port, expose open/write/read/close as one job with timeout, regex-framed completion, byte limits, SHA-256 log receipt, and atomic report staging. Reject every other device path and never present it as the normal LTE product transport.
- **owner gets:** The owner can run the accepted audio diagnostic today and receive a trustworthy pass/fail report instead of manually watching an unjoinable UART log. It also makes the pendant's current USB-attached state genuinely testable while LTE registration remains absent.
- effort: Medium: local agent action plus a small serial worker and parser tests; hardware fixture protocol changes are required.  ·  risk: A bad framing rule could hang or misclassify a partial diagnostic. Use hard timeouts, bounded buffers, explicit completion markers, and preserve raw logs for replay. Recovery is to kill the worker and leave the board untouched; never auto-flash firmware.
- cost: No API cost; roughly 1–2 engineering weeks and no hardware cost because both ports are live. Disk use is capped per report.  ·  latency: Adds under 100 ms setup and streaming latency; diagnostic duration remains fixture-defined.
- security: Reduces risk versus arbitrary run_shell by constraining ports and commands, but it exposes hardware logs and must redact tokens. Keep the existing FULL_CONTROL path unchanged for owner policy; this is an observable, typed bench path.
- depends on: audio_path_diagnostic_fixture; mac-terminal bounded serial read capability t22-ib1b; a machine-readable fixture completion protocol; mac_workbench_transaction for atomic report receipt


## What it asked for

_Nothing._
## Its own summary

Discovered live Mac state: Accessibility and Screen Recording are now granted and synthesized input is verified; 20 apps and four browser sessions are present, with loginwindow foreground. Recorded four deliverables: meeting-end context handoff, owner-facing pendant health check, browser-session security alerts, and the bounded USB bench harness that makes the attached nRF9160/ESP32 testable. The owner-facing value is now concrete while LTE registration is still absent.

**Biggest unknown:** The key missing product primitive is still trustworthy semantic context and transport: active document/window identity for handoff cards, event-level browser auth changes, and a bounded bidirectional USB serial worker with machine-readable diagnostic completion and exit receipts. Existing observe/browser routes are ambiguous or too coarse for these.

