# Harness derivation — mac-terminal — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “diagnose the audio,” tell me whether the pendant, USB link, ESP32 bridge, Mac audio output, or Bluetooth headphones are the failing part, and prove it with a short spoken result."
- **useful because:** Today a silent wearable/audio chain leaves the owner guessing which of five links failed. A coordinated test can isolate the fault instead of restarting everything or losing a conversation.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Background/cheap model for interpreting bounded telemetry; realtime only to speak the concise result.
- **latency:** Under 10 seconds for the first verdict; deeper capture may run up to 60 seconds with spoken progress.
- **cost:** Usually <$0.01 per invocation; most work is deterministic serial/audio telemetry, not model tokens.
- **security:** USB diagnostic frames and local audio-device names stay on the Mac/relay; never upload microphone content. Require explicit confirmation before playing test tones.
- **missing:** A real Mac serial reader for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the granted schema is unresolved); A bounded telemetry/framing protocol emitted by both firmware images; Mac routes for audio-device state and loopback/underrun counters; A correlation ID joining pendant frames, ESP32 counters, pipeline events, and the spoken verdict

### "When I say “finish this on my computer,” carry the task through the pendant, my authenticated browser session, and the Mac, then tell me exactly what changed and where the evidence came from."
- **useful because:** The owner should not have to restate a task or inspect whether a browser click actually worked. This makes the wearable the front door while the browser supplies private sessions and the Mac performs local work, with a factual completion report rather than a confident guess.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime model handles the short intent and clarification; background model executes and summarizes the durable receipts.
- **latency:** Acknowledge in under 2 seconds; ordinary tasks complete in 15–90 seconds, with progress spoken if longer.
- **cost:** <$0.03 typical; browser/Mac actions dominate latency, and summary generation is the only material model cost.
- **security:** Authenticated page contents remain inside the browser harness; send only selected claims and URLs to the relay. Confirm before irreversible sends, purchases, deletes, or submissions; preserve an evidence trail for every changed field.
- **missing:** A single cross-surface task ID propagated from pendant audio through relay, browser command/result, and POST /execute job; A browser-side commit-verification step that rereads the resulting page/state after a mutation; A compact spoken receipt format with changed fields, source URL, and verification status; Recovery for a disconnected browser or Mac without claiming completion

### "If the audio link drops while I am talking, move the live turn to my Mac without making me start over, keep the browser or Mac task running, and tell me when the wearable is back."
- **useful because:** A dropped wearable link currently risks losing the owner's words or leaving an action in an unknown state. The Mac is physically present now, so it can preserve the turn and continue work while the pendant reconnects.
- **path:** pendant → mac-planner → relay → browser-extension → dashboard
- **model tier:** Realtime model only for turn continuity and short status; cheap background model reconciles transcripts and action state after reconnection.
- **latency:** Detect and announce handoff within 1 second; resume speech/control within 3 seconds; reconcile after reconnect without blocking the owner.
- **cost:** <$0.02 per handoff; transcript cursor and event routing dominate, not generation.
- **security:** Keep the active transcript encrypted and local to the Mac/relay; never replay stale audio as fresh input. Do not duplicate a side effect: browser/Mac jobs must be idempotently associated with the turn before retry.
- **missing:** A shared turn cursor and exactly-once action key understood by pendant, relay, Mac, and browser; A Mac-side audio fallback that can capture/output without opening the microphone until the owner explicitly starts the handoff; A reconnect reconciliation endpoint that compares the pendant replay cursor with pipeline/job receipts; A user-visible distinction between queued, running, completed, and stale work

### "Start this task from my pendant, and let it keep running on my Mac and authenticated browser only while my pendant is physically nearby; if I walk away, pause at the next safe boundary and tell me what is waiting."
- **useful because:** The owner gets continuity without leaving an authenticated browser or a long-running local action unattended in an empty room. It is a physical-presence lease, not another confirmation prompt: work can proceed hands-free while the owner is present and naturally pauses when they leave.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** Cheap deterministic lease/watchdog for proximity and job state; realtime model only for the owner's spoken start and concise pause/resume notices.
- **latency:** Presence loss detected within 3 seconds; pause at the next declared safe boundary; resume within 5 seconds of return.
- **cost:** <$0.01 per task after implementation; ongoing cost is heartbeat traffic and local state, not generation.
- **security:** Never transmit raw location. Use an ephemeral proximity token and coarse present/absent state. Define unsafe boundaries explicitly so a lost heartbeat cannot interrupt a committed file write or duplicate a browser submission.
- **missing:** A product pendant radio path that can provide authenticated local proximity to the Mac (current nRF9160/LTE and USB bench link are not a wearable Mac-presence protocol); A lease token shared by pendant, relay, browser session, and Mac job; Per-action safe-boundary metadata and a pause/resume contract for POST /execute and browser commands; A durable owner-visible lease history so a pause is distinguishable from task failure

### "When I ask “what did I leave unfinished?”, give me one prioritized list spanning my open Mac jobs, browser commands, drafts, and the last spoken task, with a one-sentence resume action for each."
- **useful because:** Today unfinished work is split across job records, browser sessions, local files, and conversation state. The owner should recover their day from one spoken question instead of remembering which surface held each half-completed task.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model builds the ranked digest from structured state; realtime model only answers the short spoken query and reads the top item.
- **latency:** Under 5 seconds for a useful first list; deeper evidence can fill in asynchronously.
- **cost:** <$0.02 per request; ranking structured records is cheap, while provenance excerpts dominate context size.
- **security:** Keep authenticated page text out of the relay summary unless the owner asks. Return source labels and sensitivity flags, and never infer that a failed or interrupted action is complete.
- **missing:** A unified unfinished-work record keyed to a common task ID across Mac jobs, browser commands, pipeline turns, and drafts; A durable distinction among paused, interrupted, failed, awaiting-owner-input, and completed-but-unverified; A resume planner that can safely reconstruct the next action without replaying prior side effects; A compact privacy-filtered projection suitable for spoken output


## Changes it proposed to its own stack

### `hardware` — Build the wearable revision with a secure local-presence channel (BLE 5.3 or UWB, hardware-backed device identity, and a tiny always-on proximity beacon) alongside LTE, plus a physical privacy indicator tied directly to microphone power. The relay and Mac use signed rotating presence leases; the privacy indicator is not software-overridable.
- **owner gets:** The owner can know that a task is running only while the pendant is actually with them, and can trust that the microphone is electrically off when the privacy indicator says so. This enables safe walk-away pausing without turning the system into a maze of prompts.
- effort: High: new radio/antenna and enclosure review, secure-element provisioning, Mac companion pairing, firmware power-state design, and relay lease protocol.  ·  risk: Radio coexistence, battery drain, pairing loss, and false absence could pause work unexpectedly. Recover with a local grace period, explicit stale state, and resume from idempotent task checkpoints rather than replaying actions.
- cost: Roughly $8–25 added BOM plus certification/antenna work; 1–10 mW average beacon budget depending on BLE/UWB duty cycle.  ·  latency: Presence decisions in 1–3 seconds; negligible impact on LTE/audio when scheduled around active streaming.
- security: Improves physical-presence and microphone trust, but introduces pairing keys and proximity metadata that must be rotated and never exposed as location history.
- depends on: A cross-surface task/lease identity carried by pendant, relay, browser, and Mac; Safe-boundary and idempotent resume semantics for local and browser actions; A hardware-backed enrollment and revocation flow


## What it asked for

_Nothing._
## Its own summary

Produced three new cross-surface capabilities: (1) a spoken, evidence-backed whole-chain audio diagnosis; (2) a pendant-initiated browser+Mac task that verifies state changes and reports provenance; and (3) live-turn handoff to the Mac during a wearable link drop, with exactly-once reconciliation on reconnect. The boards are visible as physical devices, but the granted serial diagnostic tool still cannot resolve: the live inventory has no serial capability. I also notified relay-realtime not to assume LTE registration.

**Biggest unknown:** Whether the current firmware emits a stable, parseable health/audio counter frame over either USB UART. We need a real bounded serial reader (or a narrowly scoped run_shell implementation) plus a shared turn/task correlation protocol before claiming end-to-end audio diagnosis or seamless handoff.

