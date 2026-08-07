# Harness derivation — mac-planner — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When my pendant is plugged into my Mac, make it a local voice console automatically: carry my live conversation over USB despite no LTE registration, use the Mac's network for the relay, and resume on LTE later without losing context."
- **useful because:** The pendant is physically wearable and testable now but currently becomes useless when its modem is unregistered or LTE is weak. This makes voice control reliable at a desk and turns the Mac-attached prototype into a real daily fallback, with no microphone opened on the Mac.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** Realtime only for the live turn; a cheap background worker maintains session/checkpoint reconciliation.
- **latency:** Under 250 ms added one-way over USB; reconnect and session reconciliation under 2 seconds.
- **cost:** Negligible model cost beyond the existing live turn; engineering is a USB serial audio/WebSocket tunnel and reconnect state machine.
- **security:** USB audio and control frames must be authenticated and bound to the local pendant identity; never expose the serial bridge beyond localhost. Persist only opaque session checkpoints, not raw audio.
- **missing:** Pendant USB serial audio/control framing and host-side serial daemon; Relay transport mode that accepts a Mac-local pendant tunnel and migrates the same session between USB and LTE; A small Mac launch agent to discover /dev/cu.usbmodem00096003658* and bridge frames

### "I’m starting a meeting—press the pendant button once to put my Mac in a quiet mode, remember what I was doing, and press it again afterward to restore everything and tell me what I missed."
- **useful because:** A physical, glance-free gesture is faster and safer than hunting through macOS controls while joining a meeting. The Mac can suppress distractions, the browser can preserve the active work context, and the pendant can announce the restoration and a short missed-item digest afterward.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Realtime handles the two short spoken confirmations; background model summarizes accumulated notifications and calendar/mail changes after the meeting.
- **latency:** Quiet mode within 1 second of the button event; restoration within 2 seconds; digest within 30 seconds.
- **cost:** One cheap background summarization call per meeting; no model call for the deterministic mode toggle.
- **security:** Do not read notification contents aloud in public by default; store a bounded, encrypted meeting capsule locally and expire it after 24 hours. The second press must restore only state this routine changed.
- **missing:** Pendant firmware button event exposed over the active USB/LTE control channel; Mac state snapshot/restore for focus mode, volume, foreground app, and browser tab set; A notification/calendar delta collector and meeting-capsule store; Relay routine that correlates start/end presses and sends a compact spoken result

### "If I tap the pendant twice within 10 seconds after you change something on my Mac, undo the last reversible change and tell me exactly what was restored."
- **useful because:** The owner can recover from an accidental open, move, volume change, or reversible edit without finding the Mac window or remembering a command. It gives the wearable a concrete safety affordance for the system’s otherwise maximum-control automation.
- **path:** pendant → mac-planner → relay-realtime → faculty-action
- **model tier:** No expensive reasoning for the gesture; deterministic receipt lookup and undo, with realtime only for the brief spoken confirmation.
- **latency:** Recognize the double tap in 300 ms and complete a supported undo within 2 seconds.
- **cost:** No per-use model cost; one small persistent action receipt per mutation and a bounded undo record.
- **security:** Only undo actions explicitly marked reversible by the executor; never undo sends, deletes, purchases, or browser submissions. Require a fresh receipt ID and expire the gesture window to prevent replay.
- **missing:** Pendant double-tap event and debounce firmware; Action receipts need a reversible flag plus inverse payload, not just human-readable logs; A relay endpoint that maps the pendant gesture to the most recent session-scoped Mac job and calls /jobs/:jobId/undo; Spoken receipt that names the affected app/path without leaking private content

### "I lost the thread—capture what I was doing on the Mac and in my browser right now, recover the last few relevant spoken turns, and leave one resumable workspace packet with the next three actions."
- **useful because:** Today a context switch destroys the connection between the owner’s voice, open tabs, editor state, and unfinished desktop work. A single spoken recovery command would turn an interruption into a concrete restart point rather than another explanation to the assistant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime only acknowledges capture; a cheaper background model assembles and ranks the recovery packet.
- **latency:** Capture acknowledgement under 1 second; packet available within 20 seconds.
- **cost:** One small background summarization call per requested packet; storage is a few kilobytes of text and metadata, with optional local screenshots.
- **security:** Redact secrets, passwords, and private page bodies by default; include URLs and app names with provenance. The packet expires after 7 days and is stored in ~/AI-Pendant-Workspace unless the owner chooses another destination.
- **missing:** A single cross-surface snapshot schema joining recent voice turns, foreground app, editor files, browser tabs, and active Mac jobs; A resumable packet writer that records source timestamps and next-action dependencies; A relay command that can request the snapshot without opening the Mac microphone

### "File a private incident report for this pendant session: collect the relevant UART and relay diagnostics, attach the exact reproduction timeline, redact credentials, and open it in my editor for review—never submit it automatically."
- **useful because:** The owner already wants the pendant to file its own bug reports, but today diagnosing a failure requires manually finding logs and reconstructing what happened. This would convert a confusing drop or audio glitch into a reviewable, reproducible report in one spoken request.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** Cheap background extraction and redaction; realtime only confirms that the report is ready.
- **latency:** Start capture immediately; draft report within 30 seconds of the request.
- **cost:** One low-cost log summarization call; local report and selected log excerpts are typically under 100 KB.
- **security:** Credential/token regexes plus structured field allowlists must run before persistence. Include hashes and timing metadata rather than raw audio. Opening is allowed, submission is always a separate owner action.
- **missing:** A signed, queryable diagnostic event stream spanning pendant UART, ESP32 bridge, relay, and Mac job IDs; Automatic credential and personal-data redaction with a visible omissions list; A report assembler that writes Markdown to ~/AI-Pendant-Workspace and opens it in VS Code

### "Prepare a redacted handoff for a human teammate: gather the relevant editor files, authenticated-page links, pendant/relay evidence, and a short explanation of the unresolved decision; create a draft message and a review folder, but do not send anything."
- **useful because:** The system can act across surfaces but cannot currently package its partial understanding for a human who must take over. This would let the owner move a problem from AI context into a reviewable, privacy-bounded handoff without copying tabs, logs, and notes by hand.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Background model assembles and redacts the handoff; realtime is unnecessary unless the owner asks for a spoken status.
- **latency:** A review folder and draft within 45 seconds; never block on sending.
- **cost:** One background synthesis call plus local file creation; dominant cost is extracting and redacting selected browser/editor evidence.
- **security:** Require an explicit recipient and source scope; exclude credentials, secrets, unrelated tabs, and raw audio. Draft must visibly list every included source and every redaction. Sending remains a separate owner action.
- **missing:** A source-scoped evidence collector that can join VS Code files, browser tabs, relay diagnostics, and pendant events; A redaction engine with an inclusion manifest and deterministic secret scanning; A handoff bundle format and draft-message writer that preserves links and provenance


## Changes it proposed to its own stack

### `integration` — Ship a localhost pendant bridge daemon that claims /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, frames button/audio/diagnostic packets with sequence numbers, forwards them to the existing Mac pipeline endpoints, and reconnects without duplicating events. Expose a one-line status in the Mac agent and persist only the last acknowledged sequence per device.
- **owner gets:** With the two boards already plugged into this Mac, the owner can use the pendant as a dependable local control and audio accessory today instead of waiting for LTE registration or manually restarting firmware tools.
- effort: Medium: serial framing, launchd lifecycle, reconnect tests, and a narrow pipeline adapter; no model work.  ·  risk: A stale daemon could consume the serial ports or duplicate button presses. Use exclusive-open, heartbeat expiry, sequence acknowledgements, and a kill/unplug recovery path.
- cost: No recurring API cost; approximately 1–3 MB resident Mac memory and negligible CPU while idle.  ·  latency: Adds roughly 10–30 ms over USB serial; reconnect target under 2 seconds.
- security: Bind to exact USB VID/PID/serial identities, keep the listener localhost-only, and reject unknown serial devices. Do not log audio payloads.
- depends on: Pendant and ESP32 firmware must publish a documented framed control protocol; Relay must accept a Mac-local transport identifier for session continuity; A launchd-installed serial bridge binary/script


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities. (1) Most important: when the pendant is USB-attached, preserve the same live voice session through the Mac’s network despite no LTE registration, then migrate back to LTE without losing context; missing pieces are the serial audio/control tunnel, transport migration, and a localhost daemon. (2) A single pendant press starts a meeting quiet mode that snapshots Mac/browser state; a second press restores only changed state and delivers a private missed-item digest; missing pieces are button events, state snapshot/restore, and a bounded meeting capsule. (3) A double-tap within 10 seconds undoes the most recent reversible Mac action and speaks a receipt; missing pieces are firmware debounce, reversible inverse payloads in receipts, and a session-scoped undo adapter. I also proposed the local serial daemon, but the recorder flagged it as close to the first capability, so I will not restate it.

**Biggest unknown:** Whether the pendant firmware currently emits any framed button/control packets over the live USB serial connection, and whether the Mac can claim both serial devices concurrently without an existing process. The next useful step is a read-only serial/protocol inventory, not another proposal.

