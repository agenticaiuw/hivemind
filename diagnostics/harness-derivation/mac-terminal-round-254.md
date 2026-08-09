# Harness derivation — mac-terminal — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB serial access** — The granted mac_usb_serial_diagnostics schema still does not resolve in the live inventory, so no serial frame was read. The only currently reachable mechanism for these ports remains POST /execute with run_shell, using the existing dual-chip capture scripts.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; nearest action:get_mac_status score 0.225. Established inventory notes diagnostics/dual_chip_autocapture.sh and diagnostics/start_dual_capture.sh.

## Capabilities it proposed

### "When I plug the pendant and audio bridge into my Mac, tell me whether both chips are healthy, what failed, and give me one command to fix or reproduce it."
- **useful because:** The hardware is physically on the desk today, but a failed UART capture currently leaves the owner staring at raw logs. This turns bring-up into a truthful owner-facing diagnosis: pendant button/LED state, bridge audio counters, port presence, framing/firmware errors, and a reproducible next action. It uses the wearable as the trigger and the relay as the voice/result surface rather than being another Mac-only diagnostic.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** Use mac-planner for bounded parsing and deterministic health rules; use the expensive realtime tier only to explain an already-computed diagnosis conversationally. No model call is needed for port discovery, counters, CRCs, or known firmware faults.
- **latency:** Start capture within 2 seconds; first health verdict within 8 seconds; allow up to 30 seconds for a controlled dual-UART reproduction. The pendant should show testing/failed/completed through truthful_action_status_beacon.
- **cost:** Usually <$0.01 in model/API cost because parsing and known-fault matching are local; the dominant cost is one short relay explanation when the owner asks follow-up questions.
- **security:** UART output can contain identifiers, paths, or captured audio metadata. Keep raw logs on the Mac, send only bounded counters/error codes and a redacted excerpt to relay, and require an explicit owner phrase before uploading a full log. Never claim LTE health from a USB-only test.
- **missing:** A real read-only serial reader/parser for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the granted schema is still unresolved); A stable JSON health frame in both firmwares with build ID, boot reason, sequence, CRC/error counters, and audio underrun counters; A relay intent that can start the Mac bench capture and stream progress, rather than merely returning a finished shell job

### "If the internet is down, let me keep talking through the pendant and Bluetooth headphones using my Mac, then sync the conversation and any actions when the relay comes back."
- **useful because:** Today the wearable, ESP32 audio bridge, and headphones are real, but the cloud relay is a single point of failure. A local voice path would make the pendant useful on an airplane, in a dead Wi‑Fi room, or during a relay outage: the owner still hears replies and can issue Mac actions, while deferred cloud work is clearly marked as pending rather than lost.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime
- **model tier:** Use a local small speech recognizer and local low-latency TTS on the Mac for offline turns; use mac-planner for deterministic local actions and gpt-realtime-2.1 only after reconnect for cloud-quality follow-up and synchronization. Do not spend realtime tokens while disconnected.
- **latency:** Button-to-local-recording under 100 ms; partial transcript under 1 s; first spoken local response under 2 s. Reconcile the queued transcript/action receipts within 10 s of relay recovery.
- **cost:** Offline turns have no API cost; local CPU and roughly 15–25% battery/power overhead on the Mac dominate. Reconnection sync costs only the compact transcript/action summary, not raw audio.
- **security:** Offline audio and transcripts must remain on the Mac until the owner explicitly enables sync. Queue action intents with a unique turn ID and never replay an already acknowledged side effect. Say 'local mode' in the reply and expose the mode through the pendant's existing truthful status beacon.
- **missing:** A USB audio transport or framed PCM endpoint between nRF9160 and Mac; current USB is bench-only and the production path is LTE-M; A local ASR/TTS service with interruption handling and a small durable turn journal; A reconnect reconciliation route that accepts turn IDs, local receipts, and pending action intents with exactly-once semantics; Firmware support to select Mac-local audio versus LTE/cloud audio without feeding stale frames

### "That Mac task went wrong—undo the last thing you did, or, if it cannot be safely undone, show me exactly what changed and restore the affected project to its last known-good checkpoint."
- **useful because:** The current shell is deliberately unrestricted, but most failures are recoverability failures: a command can alter files, the job record lacks an exit code, and cancel does not stop a running process. A spoken recovery command from the pendant would turn maximum capability from 'hope the model was right' into a usable working relationship. It should use git/APFS/file snapshots where available, and be honest when an external or irreversible effect cannot be reversed.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Use deterministic Mac tooling to capture a before/after manifest, git diff, process status, and available undo receipt. Use gpt-5.6-luna only to map the owner's natural-language target to one of those recorded changes; use realtime solely to converse and read the result aloud.
- **latency:** A recovery answer within 3 seconds for an existing receipt; filesystem restore within 15 seconds for a bounded project; long-running rollback is handed back as a tracked job with pendant progress.
- **cost:** <$0.01 for receipt lookup and diff calculation; snapshot storage is the main cost (bounded by project size). Model cost is a short intent-resolution call only when 'that' is ambiguous.
- **security:** Restoring the wrong directory is worse than leaving it changed. Never infer scope from a vague shell string alone: bind 'that' to the latest completed action and its touched paths, preserve a pre-restore snapshot, and refuse to claim rollback of email, network, or external side effects. Raw command strings and diffs stay on the Mac unless the owner asks for them.
- **missing:** Per-action before-state snapshots and a durable change manifest for run_shell, including exit code and child PID/process group; A real restore/undo route that can execute the existing reversible receipts and create a compensating receipt (current undo.js covers only a few action types); A spoken reference resolver that joins pendant turn IDs to the latest Mac job/action, since planMeta.jobId currently does not join ledgers to jobs; Boot-time reconciliation so a recovery request cannot treat a stale processing job as live

### "Run this long task on my Mac and keep me updated through the pendant; if I say 'stop after the current step' or 'that output means abort', actually interrupt it and tell me exactly what completed before stopping."
- **useful because:** Today a shell job is a black box: output is retained only after execution, cancellation cannot interrupt a running exec, and the pendant can report a stale state while a process continues. The owner should be able to supervise a real Mac task conversationally without sitting at the screen, including making a mid-run decision from live output. This is not merely a status query or a retry; it is an interactive, step-aware execution session spanning the wearable, relay, and terminal.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner
- **model tier:** Use a deterministic PTY/process supervisor for byte streaming, step boundaries, process-group termination, and receipts. Use gpt-realtime-2.1 only to summarize bounded output and interpret the owner's interruption; use gpt-5.6-luna for planning the next step after an explicit stop. Never send the full unbounded terminal stream to a model.
- **latency:** First progress event within 500 ms of a line or step boundary; spoken updates at most every 3 seconds unless the owner asks for silence. A stop command must reach the Mac within 1 second and report whether the process group exited, was killed, or ignored termination.
- **cost:** Low API cost: deterministic streaming dominates, with one short realtime summary per meaningful milestone. Retain raw output locally with a bounded ring rather than paying to retransmit it.
- **security:** Terminal output may contain secrets and arbitrary command content. Keep raw bytes on the Mac, redact likely credentials before relay, and send only selected lines plus exit/signal metadata. The remote stop must be bound to the active job and turn ID so an old spoken 'stop' cannot kill a later task. This adds control, not an approval gate; the owner's existing maximum-access policy remains intact.
- **missing:** A PTY or spawn/execFile supervisor that captures PID, process group, exit code, signal, and incremental stdout/stderr instead of using one opaque exec promise; A websocket or SSE-like authenticated job event stream from the Mac agent to relay, with backpressure and reconnect cursors; Real cancellation wired to the child process signal and a step-aware protocol for multi-action jobs; A pendant conversation command that targets the currently announced job ID and preserves the stream cursor across brief link loss


## Changes it proposed to its own stack

### `hardware` — Replace the prototype HUZZAH32 A2DP-source bridge with a production audio bridge that has native USB Audio Class plus a modern Bluetooth audio transmitter (or an ESP32-S3-class design with enough PSRAM and a supported LE Audio/SBC pipeline). Keep the nRF's Opus framing, but move resampling and buffering into a bounded bridge with hardware flow control and a watchdog-visible frame counter.
- **owner gets:** Headphone audio would stop depending on a precompiled 44.1 kHz SBC path that can starve when a 44 kB buffer is used. The pendant could work directly with the Mac for bench/offline use and with headphones in normal wear, with fewer silences, less latency, and a truthful underrun indication instead of a reply that appears to have vanished.
- effort: High: prototype a new bridge board/firmware, implement USB Audio Class and Bluetooth pairing/reconnect, characterize clock drift and Opus-to-PCM buffering, then validate against the existing nRF I2S wire clock and headphones.  ·  risk: Bluetooth interoperability and RF coexistence may regress; preserve the current ESP32 as a fallback and expose bridge firmware/codec version in the health frame. A watchdog should fail audio closed and request a transport restart rather than replay stale PCM.
- cost: Roughly $20–60 per prototype bridge plus enclosure/cables; several hundred mW additional peak draw depending on radio and USB mode. No per-turn API cost.  ·  latency: Potentially removes one resample/SBC buffering stage and can cut perceived playback latency by 50–150 ms, though LE Audio compatibility must be measured.
- security: Pairing keys and USB audio are local; store no cloud credentials on the bridge. Provide an explicit pairing reset and do not make the bridge a general USB network device.
- depends on: A stable framed audio/health protocol shared by nRF9160, bridge, and Mac; A bounded serial/USB bench harness for the currently connected prototype; Audio-link state reporting from the already accepted audio_link_truth_and_recovery firmware skill


## What it asked for

_Nothing._
## Its own summary

Round 254 produced four owner-facing directions. The most ambitious is a genuine offline voice mode: pendant + Mac + bridge continue local conversation during relay/LTE loss, then reconcile compact turn IDs and action receipts on reconnect. I also proposed spoken, checkpoint-backed recovery for unrestricted Mac shell work, a dual-chip bench diagnosis flow, and a production audio-bridge hardware replacement. The live USB probe is still unavailable: mac_usb_serial_diagnostics remains unresolved, so no UART truth was obtained. The current prototype facts are now confirmed: nRF Opus playback is 24 kHz/60 ms into a 31.25 kHz I2S wire clock, and the HUZZAH32 is an SBC-only 44.1 kHz A2DP source with tight RAM and a known starvation risk.

**Biggest unknown:** Whether the connected nRF9160 and ESP32 actually enumerate and emit usable health/audio frames. The only path that can test this today is a bounded run_shell invocation of the existing dual-chip capture scripts; the granted serial-specific tool has no live implementation. The next useful system work is a real host serial reader plus stable JSON health frames, not another wrapper or resolver rename.

