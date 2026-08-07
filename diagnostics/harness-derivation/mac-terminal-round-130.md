# Harness derivation — mac-terminal — round 130

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Something in my project just failed—find the cause, fix the safe parts, and tell me exactly what changed.”"
- **useful because:** This would turn a wearable alert into an end-to-end recovery loop: the pendant hears the request, the relay keeps it alive, Safari contributes authenticated CI/email evidence, and the Mac inspects and patches the local checkout. Today those surfaces can each report facts, but none can carry an incident from evidence to verified repair.
- **path:** pendant → relay-realtime → browser-extension → mac-terminal → mac-planner → unified
- **model tier:** Use realtime only for the short spoken interaction; use a cheaper background planner for log correlation and a local Mac executor for tests. Escalate to the expensive model only when evidence conflicts or the repair is ambiguous.
- **latency:** Acknowledge on the pendant in under 2 seconds; first diagnosis in 20 seconds; safe patch/test loop may take 2–5 minutes, with spoken progress after each phase.
- **cost:** Roughly $0.01–$0.08 per incident depending on transcript and CI-page context; test execution is local, while browser evidence and the final synthesis dominate model tokens.
- **security:** Authenticated browser text and local source diffs leave the device only to the relay/model needed for diagnosis. Never transmit secrets or whole repositories; redact tokens and send bounded error windows/diffs. Automatic edits must be limited to a declared checkout and produce a diff plus test receipt; ask before pushing, emailing, or deleting.
- **missing:** incident state machine joining a pendant request, browser evidence, local job, and final receipt; bounded repository/log redaction before model upload; background retry/verification worker; Accessibility permission for AI Pendant Agent if the workflow needs visible UI fallback

### "“Even when the relay is down, let me press the pendant button and hear a local status or saved instruction through my headphones; sync what happened when the Mac reconnects.”"
- **useful because:** The pendant and ESP32 are physically USB-attached today, so this is runnable before LTE registration. It gives the owner a dependable offline escape hatch instead of a silent dead wearable, while preserving a durable event trail for the cloud conversation later.
- **path:** pendant → ESP32 audio bridge → mac-terminal → relay-realtime
- **model tier:** No network model for fixed commands: firmware handles button/debounce and the Mac handles a tiny deterministic command table. Use a cheap background model only to summarize queued events after reconnection; reserve realtime for a live relay session.
- **latency:** LED/audio acknowledgement within 150 ms of the button press; a cached spoken status within 1 second; queued-event sync within 10 seconds of relay availability.
- **cost:** Near-zero API cost offline; under $0.01 for optional post-reconnect summarization. Engineering cost is serial framing, queue persistence, and SBC playback, not inference.
- **security:** USB serial must authenticate the paired Mac and reject arbitrary host commands. Persist event IDs and coarse status, not microphone audio or secrets. The Mac should expose only signed, allowlisted local responses; replay protection is required when draining the queue.
- **missing:** nRF9160 USB-serial button/event protocol and a small offline command table; Mac daemon that owns /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA without competing with flashing tools; durable encrypted queue and idempotent relay sync; ESP32 reconnect/watchdog behavior and a spoken-packet framing format

### "“Make the pendant agent able to control the screen again, and prove it worked.”"
- **useful because:** Today the Mac reports Accessibility as untrusted for the actual AI Pendant Agent binary, while UI actions can return success without reaching the screen. The owner cannot ask the system to diagnose the binary/permission mismatch, guide the exact repair, and then verify a real input event end-to-end. This would turn a silent broken surface into a self-repairing one.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → mac-vision → dashboard-ux
- **model tier:** Use a cheap local deterministic diagnostic and verification routine; use realtime only to explain the result through the pendant. Vision is needed only for the final visual proof, not for every step.
- **latency:** Detect the mismatch in under 2 seconds, guide the owner through the one required System Settings change in under a minute, and verify a harmless test interaction within 5 seconds after permission changes.
- **cost:** Under $0.01 per repair attempt; nearly all work is local macOS permission inspection and a bounded verification action. Vision upload, if explicitly enabled, is the dominant cost.
- **security:** Changing Accessibility is a powerful owner-controlled macOS permission and must never be silently granted. The agent may open the correct System Settings pane and provide exact instructions, but the owner must make the OS decision. Verification should use a harmless target (for example focus a known app) and must not transmit screenshots unless consented.
- **missing:** a permission-repair workflow that identifies the running executable rather than trusting the app label; a signed harmless input probe with an observable target-state assertion; a dashboard/pendant status that distinguishes permission missing, event rejected, and target not found; Screen Recording consent and an optional visual proof path for mac-vision

### "“Read the authenticated page I’m looking at into my headphones, skip the boilerplate, and let the pendant pause, resume, or jump to the next section.”"
- **useful because:** No single node can do this privately and continuously today: the browser has the authenticated page and section structure, the Mac can synthesize audio, the ESP32 bridge can deliver SBC audio to headphones, and the worn button is the only practical pause control. It would let the owner consume long work pages without moving focus or exposing them on a speaker.
- **path:** pendant → ESP32 audio bridge → browser-extension → mac-terminal → relay-realtime
- **model tier:** Use a local/cheap text extraction and sectioning model for page cleanup; use macOS say or the relay TTS fallback for speech. Realtime is unnecessary except for conversational commands that change playback.
- **latency:** Start playback within 3 seconds, pause/resume under 150 ms at the button, and advance sections within 1 second. Buffer only the next 10–20 seconds so navigation remains responsive.
- **cost:** Usually near-zero API cost with local extraction and macOS say; optional model cleanup costs less than $0.01 per page. Bluetooth SBC playback and USB serial are local.
- **security:** Authenticated page text must remain in the local browser/Mac path by default; do not send it to the relay unless the owner explicitly asks for cloud summarization. Bind controls to the active tab/session, show the origin in the first spoken cue, and discard cached text when playback ends.
- **missing:** a browser command that returns semantic sections and a stable tab/session lease rather than one full page blob; a streaming TTS player with section boundaries and pause/seek commands; nRF9160 button event forwarding over USB serial to the Mac playback controller; ESP32 bridge buffering that does not starve its Bluetooth stack


## Changes it proposed to its own stack

### `mac-harness` — Make execution planning reachability-aware without restricting FULL_CONTROL_MODE: expose a live capability matrix (Accessibility/input posting, Screen Recording, per-app Automation, browser extension health, serial devices) to the planner; label each action with its required substrate; if a substrate is unavailable, automatically choose an equivalent shell, AppleScript, browser-DOM, or direct app route, and mark UI-only actions as unverified rather than successful. For the current host this would avoid ui_click/type_text because /observe reports Accessibility trusted=false and eventsPost=false.
- **owner gets:** The owner stops hearing “done” when nothing reached the screen. Requests keep working despite missing permissions, and when no equivalent exists they get an honest explanation and a useful next step instead of a silently lost action.
- effort: Medium: add capability probes to planning context, an action-to-substrate registry, fallback selection, and receipt semantics; test against Safari, Finder, Reminders, and terminal workflows.  ·  risk: A fallback can affect a different target than intended (for example the wrong browser tab). Recover with explicit target IDs, pre/post state snapshots, and automatic failure marking; do not claim success from process exit alone.
- cost: Negligible API cost; saves tokens and retries by preventing doomed UI loops. A small local probe runs periodically and is cached.  ·  latency: Adds under 100 ms from cached capability state; avoids multi-step vision retries that currently cost seconds.
- security: No new authority or gate. Capability details stay local and are reduced to booleans/target IDs before model context; shell remains owner-approved maximum access.
- depends on: A single canonical /observe or /ops/status capability snapshot consumed by mac-planner; Action receipts that distinguish process success, target-state success, and unverified UI delivery; Accessibility grant to the actual AI Pendant Agent binary if true UI control is desired

### `mac-harness` — Add an opt-in “workspace time machine” around arbitrary run_shell jobs: capture cwd, argv, relevant environment names (never values for secrets), git HEAD/index/worktree state, and a manifest of files created/removed/modified before and after execution; for non-git paths use APFS snapshots or a quarantine/backup area. Expose one-click restore and a human-readable change set alongside the existing job receipt, while leaving FULL_CONTROL_MODE and unattended execution unchanged.
- **owner gets:** After asking the agent to run an unfamiliar command, the owner can see exactly what it touched and restore the project if the result is bad—even for shell commands that current undo.js cannot reverse.
- effort: High: filesystem event/manifest capture, bounded snapshot storage, restore conflict handling, and integration with jobs and receipts.  ·  risk: Snapshots can be incomplete for external services, huge builds, or files outside the workspace; restoring over newer owner edits could destroy work. Require a dry-run restore preview, compare current hashes, and refuse only the restore operation when conflicts exist (never block the original command).
- cost: Local disk usage proportional to changed files; compress manifests and cap snapshots (for example 2 GB or 7 days). No meaningful API cost.  ·  latency: Manifest capture adds tens to hundreds of milliseconds; APFS snapshot creation is fast, while large backup copies happen asynchronously.
- security: Snapshots may retain secrets that a command generated. Encrypt the local store, apply retention, redact known secret files from model summaries, and never upload snapshot contents by default.
- depends on: Stable job IDs and lifecycle records from GET /jobs and GET /journal/:jobId; Receipt attachment support at GET /jobs/:jobId/receipts; A restore endpoint that can validate hashes and apply a conflict-aware rollback


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery found the Mac agent and relay healthy, browser extension online with Gmail plus two failed example.com tabs, but /observe confirms the critical truthfulness defect: Accessibility is untrusted for the actual AI Pendant Agent binary, synthesized events are rejected, and UI actions can report success while doing nothing. I recorded four distinct proposals this round: cross-surface incident diagnosis/repair, USB-tethered offline pendant operation, reachability-aware truthful fallback planning, and a workspace time-machine for arbitrary shell jobs. The most valuable near-term fix is reachability-aware planning plus honest receipts; the most ambitious owner-visible capability is the pendant/Mac/relay incident recovery loop.

**Biggest unknown:** Whether any existing firmware or relay code already defines USB serial framing and queued event/audio synchronization. I asked relay-realtime. I still need that answer, implementation of the granted diagnostic/typed-action schemas (the grants are schemas but currently return no implementation), and Accessibility granted specifically to /Users/evanliu/Applications/AI Pendant Agent.app if real UI control is expected.

