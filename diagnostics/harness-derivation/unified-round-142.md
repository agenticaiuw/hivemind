# Harness derivation — unified — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run a pendant-and-headphones bench certification: capture a short spoken turn over USB, send it through the real relay/TTS path, verify the ESP32 bridge's 44.1 kHz Bluetooth handoff, inject controlled loss, and give me one pass/fail report with artifacts and the exact failing boundary."
- **useful because:** The owner can discover in one minute whether the thing he is wearing can actually hear and speak today, rather than separately guessing whether nRF capture, relay transport, Opus, or the SBC/A2DP bridge failed. This is actionable on the physically connected hardware even before LTE registration.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background
- **latency:** Under 90 seconds for the normal 20-second fixture; report partial boundaries within 10 seconds if a device is absent.
- **cost:** Low API cost: deterministic orchestration and signal checks dominate; one short background model call only to summarize anomalies, under $0.03 typical.
- **security:** Synthetic speech and captured test audio must be labeled and deleted by default; no owner-room audio should be retained. Require explicit confirmation before using a real conversational recording, and redact serial identifiers from shared artifacts.
- **missing:** A least-privilege serial harness that can address both /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with typed frame receipts; An orchestrator joining USB capture, relay pipeline ID, bridge acknowledgement, and audio_pipeline_validate into one run; A bridge-side observable for SBC/A2DP enqueue, underrun, and playback-start/finish rather than treating I2S receipt as hearing

### "Keep my conversation alive while I unplug the pendant from the Mac: announce the USB-to-LTE handoff, finish the current turn exactly once, and tell me if the session is degraded instead of silently dropping or duplicating audio."
- **useful because:** Today the device is physically testable over USB but is not LTE-registered. A real owner will move between desk and outside; continuity across that boundary is the difference between a dependable wearable and two unrelated demos.
- **path:** pendant → mac-bridge → relay-realtime → dashboard
- **model tier:** realtime
- **latency:** Handoff decision within 250 ms at a turn boundary; never interrupt an active spoken frame. A reconnect may take up to 3 seconds, with a concise spoken status.
- **cost:** Negligible model cost: sequence/transport state machine does the work; reserve a small realtime call only for a human-readable degraded-status sentence.
- **security:** Bind both transports to the same authenticated session and monotonic turn counter; reject late USB/LTE frames and never buffer microphone audio across an untrusted transport. Expose only counters and state, not raw audio, in the dashboard.
- **missing:** A production transport-arbiter consuming the accepted usb_fallback_audio_session firmware behavior and LTE link state; Relay session records that atomically fence the old transport and accept the new one at a turn boundary; A real LTE registration and field test; the current USB-connected pendant is the only live path

### "When I next talk to you, read me the one action that is waiting for my approval, let me approve or cancel it with the pendant's physical hold, and then show me a receipt that the exact staged action—not a changed version—ran."
- **useful because:** The code currently has an approval protocol and a physical approval latch, but a blocked plan can be spoken about and discarded because nothing persists and re-presents it. This closes the only safe path for browser/Mac actions that need the owner's deliberate consent without pretending the pendant can interrupt him out of the blue.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** realtime
- **latency:** At the first natural conversation turn, present one compact summary in under 2 seconds; physical decision acknowledgment under 1 second; execution and receipt are asynchronous and resumable.
- **cost:** Low: deterministic digest/world/expiry checks and relay persistence dominate. One short realtime summary is typically under $0.02; no model call is needed for verification.
- **security:** Persist only action summaries, digests, risk tier, expiry, and withheld-sensitive markers—not passwords or page contents. Bind approval to plan digest, world fingerprint, session, and nonce; require physical approval for irreversible/off-machine/uncontained tiers; expire and cancel stale records. Keep approval and execution credentials separated before shipping.
- **missing:** A real relay implementation of shared/approvalHandoff.js APPROVAL_STORE_CONTRACT and a delivery/readback receipt; A caller from bridge/orchestrator into prepareAction, plus a pending-approval selector at the next conversation; A separate authorization boundary so an approval token cannot itself execute arbitrary /execute work; Orchestrator closeLedger integration and explicit handling of stale/inflight ledgers before offering anything for approval

### "Never claim you told me something unless the pendant/bridge can prove it was played; if playback is interrupted, resume or say plainly that I missed it and offer the exact response again."
- **useful because:** Today relay acceptance and even a download receipt do not guarantee the owner heard the words. This turns delivery evidence into an honest conversation contract: no silent loss of reminders, approvals, or safety-critical instructions.
- **path:** relay-realtime → pendant → mac-bridge → dashboard
- **model tier:** realtime
- **latency:** Playback-state decisions under 200 ms; a retry or concise 'I couldn't confirm that' status within one turn, without blocking ordinary speech on a slow receipt.
- **cost:** Very low: deterministic state machine and receipt joins; model cost only for a short retry/status utterance, typically under $0.01.
- **security:** Retain only opaque artifact IDs, hashes, byte ranges, and playback state. Do not infer that the microphone heard the output or record the room to prove it. Require confirmation before replaying sensitive content after an interruption, and expire unacknowledged artifacts.
- **missing:** A policy engine that makes relay speech delivery conditional on playback evidence rather than merely enqueue success; A bridge receipt that distinguishes decoded, started, completed, and interrupted playback with monotonic sequence binding; A user-visible retry/acknowledgement state that cannot be confused with ordinary conversational text


## Changes it proposed to its own stack

### `firmware` — Add a long-call clock-drift servo in the ESP32 bridge: timestamp each nRF I2S block and each A2DP SBC enqueue, estimate producer/consumer ppm drift over a bounded ring, and make only sub-sample/polyphase phase corrections when the fill level crosses thresholds. Emit drift_ppm, buffer_fill, correction_count, and underrun_count in the existing delivery receipt; never grow the buffer beyond the measured safe limit.
- **owner gets:** Bluetooth crystal drift accumulates over minutes even when every individual packet is valid. This prevents the owner hearing a periodic click, stretched syllable, or eventual silence during a long conversation, without spending more RAM on the already tight bridge.
- effort: Medium: bridge firmware changes, a deterministic two-clock simulator, and a 30-minute hardware run with the Bose headphones. No pendant firmware change is required.  ·  risk: An overly aggressive servo could modulate pitch or conceal a real link failure. Use hysteresis, cap correction rate below audibility, and fall back to an explicit degraded/paused state when the ring cannot safely absorb drift. Recovery is reset-to-neutral at a turn boundary.
- cost: No API model cost. Firmware work only; likely under 1 KB code and a few hundred bytes of state. No additional hardware cost or meaningful power change.  ·  latency: No intentional conversational latency increase; a small existing bridge buffer is used as the drift reservoir.
- security: Receipts contain timing/counter metadata only, never PCM or Bluetooth contents. Preserve the existing authenticated session binding for reports.
- depends on: audio_delivery_ack_queue (s9-vtxc) for the receipt fields; audio_path_diagnostic_fixture (s16-dbfs) for long-run synthetic validation; A bridge-side monotonic timestamp and observable A2DP enqueue/playback counters

### `hardware` — Replace the prototype ESP32 A2DP bridge with a purpose-built Bluetooth audio bridge that has an audio PLL, native 24 kHz LC3/LE Audio (with SBC fallback), a hardware I2S DMA path, and an exposed playback-clock/timestamp counter. Keep the nRF USB/LTE framing contract unchanged and make the bridge advertise its negotiated codec and clock quality in the delivery receipt.
- **owner gets:** The owner gets a genuinely wearable audio path: lower buffering latency, less resampling distortion, fewer long-call drift failures, and a path that can preserve the pendant's 24 kHz speech quality instead of forcing the prototype through 44.1 kHz stereo SBC. It also makes 'delivered' observable beyond merely handing bytes to a Bluetooth stack.
- effort: High: select and prototype a production BLE Audio-capable module, redesign the bridge PCB/power/audio interfaces, implement LC3/SBC negotiation and clock telemetry, then run RF, battery, thermal, and headphone interoperability tests. This is intentionally a product-level change, not a refactor of the current DK demo.  ·  risk: LE Audio headphone compatibility is uneven and the new module could introduce pairing or RF regressions. Retain SBC fallback and the existing ESP32 bridge as a test fixture; require codec negotiation receipts and an automatic fallback before exposing the new path as default.
- cost: Roughly $15–$40 incremental module/PCB cost in low volume, plus certification/NRE; likely lower steady-state power than the 240 MHz ESP32 but this must be measured on the selected module. No per-call API cost.  ·  latency: Potentially removes tens of milliseconds of SBC/resampling buffering; actual end-to-end latency must be measured against the current 60 ms Opus framing and Bluetooth headphone buffering.
- security: Introduces Bluetooth pairing keys and a new radio firmware supply chain. Store keys in the module's protected storage, never send them to the relay, and expose only negotiated codec/counters.
- depends on: A production bridge product specification (battery, enclosure, RF and headphone compatibility); A bridge delivery receipt schema with playback-clock evidence; The shipped 24 kHz pendant/relay framing contract; Hardware audio and RF validation with representative headphones


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing additions: (1) a USB-connected pendant/ESP32/relay bench certification with controlled loss and one boundary-level verdict, (2) a transport handoff concept (noted as close to an existing continuity idea, so it should be merged rather than developed twice), and (3) a bridge firmware clock-drift servo to prevent long-call Bluetooth clicks/silence. I also proposed the missing next-conversation approval loop that persists a staged plan, binds the pendant hold to its digest, and returns an execution receipt. The most valuable immediate work is the bench certification because both chips are physically connected and testable today.

**Biggest unknown:** The live bridge observability boundary: whether firmware currently exposes A2DP enqueue/playback start/finish, SBC underruns, and a monotonic clock independent of I2S. Without those counters, we can certify bytes reaching the bridge but not that the owner actually hears them. I still need a least-privilege USB serial harness and an inventory of the bridge's current telemetry before claiming an end-to-end pass.

