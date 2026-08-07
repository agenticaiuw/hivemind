# Harness derivation — faculty-action — round 132

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run the wearable audio test.” The Mac should exercise the USB-connected pendant and ESP32 bridge with a known 24 kHz fixture, collect synchronized UART and relay timestamps, verify that audio reaches the headphones, and tell me the measured latency, underruns, and pass/fail result without flashing anything."
- **useful because:** The owner can verify the real end-to-end audio path today instead of trusting a build or a simulated relay response. It turns the current tethered prototype into an instrumented product test and catches clock drift, resampler starvation, and silent Bluetooth failures.
- **path:** pendant → mac-terminal → relay-realtime → relay → dashboard
- **model tier:** background for fixture analysis and report; realtime only for the spoken result
- **latency:** Start feedback under 2 seconds; a 30–60 second fixture run is acceptable for stable measurements.
- **cost:** Usually <$0.02 per run; dominated by relay log storage and optional report synthesis, not model tokens.
- **security:** Serial logs can contain bearer/network diagnostics; keep raw logs on the Mac, redact credentials before relay upload, and require confirmation before any future flashing step.
- **missing:** A permissioned Mac serial probe for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A deterministic test-tone/loopback mode in both firmware images; Timestamp correlation between Mac serial, relay events, and headphone bridge output; A typed audio-test report route

### "“If the wearable test fails, make me a complete repair packet.” Collect the pendant UART, ESP32 serial, relay event trail, and the Mac action receipt, identify the first failing boundary, attach a minimal reproduction command, and leave a redacted incident bundle ready for the engineer—without modifying hardware."
- **useful because:** Today a failure is scattered across four machines and easy to misdiagnose. One evidence packet lets the owner or engineer act immediately, while preserving the distinction between observed success, unverified reports, unreachable devices, and failed actions.
- **path:** pendant → mac-terminal → relay-realtime → relay → dashboard-ux
- **model tier:** background analysis; use realtime only if the owner is actively speaking about the failure
- **latency:** Bundle raw evidence within 10 seconds and produce the diagnosis within 1 minute.
- **cost:** <$0.05 per incident; storage and log retention dominate.
- **security:** UART and browser logs may expose tokens or private URLs. Redact at collection, encrypt the bundle locally, set a short TTL, and require confirmation before sharing externally or opening an issue.
- **missing:** Permissioned dual-serial collection on the Mac; A cross-surface correlation ID propagated into firmware logs and relay jobs; A redaction library aware of secrets and private URLs; An incident-bundle route with immutable hashes and expiry

### "“Can you hear the pendant?” Start a synchronized three-point check: the pendant emits a locally generated chirp, the ESP32 bridge confirms it entered the Bluetooth stream, and the relay/Mac confirm the command round trip. Tell me which exact boundary is audible or broken, with no cloud audio recording and no firmware update."
- **useful because:** A human can diagnose a silent wearable in seconds without understanding Opus, I2S, resampling, or Bluetooth. It separates command reachability from audio reachability and protects privacy by using a synthetic local signal rather than the owner's microphone.
- **path:** pendant → bridge → relay-realtime → mac-terminal → dashboard
- **model tier:** realtime for the immediate spoken diagnosis; background only for historical comparison
- **latency:** Initial chirp within 1 second; complete boundary report within 5 seconds.
- **cost:** Near-zero model cost; a few relay events and a tiny result record.
- **security:** Do not capture microphone data. Require an explicit test command, rate-limit chirps, and authenticate the serial device identity so an arbitrary USB device cannot trigger output.
- **missing:** A signed, local chirp command understood by pendant firmware; ESP32 bridge-side stream-entry acknowledgement and a bounded test tone; A relay correlation ID spanning command, I2S, A2DP, and Mac serial observations; A read-only serial/status tool for the two connected USB devices

### "“Which physical device is mine right now?” Have the pendant, ESP32 bridge, Mac, and relay perform a mutual identity challenge: blink a distinctive LED pattern, play a short bridge tone, return signed device IDs over USB, and show one verified hardware chain before any device-specific action is allowed."
- **useful because:** The owner can know that a test or action is aimed at the wearable actually in front of them, not a stale device record or the wrong USB serial endpoint. This is especially valuable while the prototype is tethered and multiple development boards may be connected.
- **path:** pendant → bridge → mac-terminal → relay → dashboard-ux
- **model tier:** background for verification; realtime only for the owner's spoken answer
- **latency:** Under 5 seconds from request to a verified chain.
- **cost:** Under $0.02 per check; dominated by durable audit storage, not inference.
- **security:** Device identity proofs must not expose bearer secrets; use per-device keys and nonce-based challenges, keep raw serial output local, and require explicit confirmation before binding a newly seen device.
- **missing:** A signed device-identity protocol in both firmware images; A read-only dual-serial Mac probe; Relay storage for nonce/challenge results and device bindings; A dashboard view and action precondition that consumes the verified chain


## Changes it proposed to its own stack

### `interaction` — Add an action-boundary status stream: when faculty-judgement hands a plan to faculty-action, emit one compact event per boundary (accepted, started, observed_success, reported_success_unverified, blocked_unreachable, failed), including device identity, precondition evidence, and the next recovery action. Mirror it to the pendant LED/audio cue, relay job record, and Mac dashboard, and automatically package the last boundary evidence when the state is blocked or failed.
- **owner gets:** The owner can tell whether something truly happened, merely was reported by a remote node, or could not be reached—especially when the pendant is tethered or a browser tab is offline—rather than receiving a confident but false completion sentence.
- effort: Medium: event schema, relay persistence, Mac/pendant renderers, and recovery packet integration.  ·  risk: Extra events could confuse the spoken surface or leak details; cap spoken output to state plus next step, keep full evidence in the dashboard, and fall back to the existing receipt if a renderer is offline.
- cost: Negligible API cost; modest D1/log storage increase, bounded by retention.  ·  latency: Adds under 100 ms for event writes; evidence packaging is asynchronous.
- security: Device IDs and URLs become more widely visible; redact sensitive fields and enforce per-job authorization.
- depends on: A stable cross-surface correlation ID; The judgement agent's receipt taxonomy (observed_success vs reported_success_unverified vs blocked_unreachable/failed); A permissioned serial probe for the physically connected pendant and bridge

### `hardware` — Replace the prototype's implicit USB identity with a tamper-evident commissioning identity: each pendant and audio bridge gets a secure element or protected key slot, a visible enrollment code, and a hardware test pin/LED pattern that can be driven during a nonce challenge. The Mac harness and relay refuse device-specific actions unless the paired chain has freshly proven possession of those keys.
- **owner gets:** The owner gets confidence that “run this on my pendant” means the worn, physically identified device, even after reconnects, cable swaps, development-board replacement, or stale relay presence. It prevents a silent test from being run against the wrong hardware.
- effort: High: secure-element selection, firmware identity protocol, enrollment UX, Mac serial integration, relay binding and recovery for replacement hardware.  ·  risk: Lost or replaced hardware needs a deliberate re-enrollment path; if a key is corrupted, diagnostics must remain possible without allowing action execution. Keep a factory recovery mode that only exposes identity and health, not user audio or network credentials.
- cost: Roughly $1–3 per production device for a secure element plus small PCB/layout cost; negligible runtime API cost and under 10 mA during an active challenge.  ·  latency: Adds 100–500 ms to device-specific action startup for challenge/response.
- security: Substantially improves protection against wrong-device control and USB impersonation; enrollment secrets must never be projected into model context.
- depends on: A durable paired-device registry; Read-only serial access on the Mac; The cross-surface action-boundary state stream; Owner-approved enrollment and replacement workflow


## What it asked for

_Nothing._
## Its own summary

Recorded three new action-focused proposals. The most useful is a real, non-flashing tethered end-to-end 24 kHz audio acceptance test using the connected nRF9160 and ESP32 serial devices, synchronized with relay timestamps and headphone-path evidence. Also recorded a local chirp boundary check (no microphone/cloud audio) and a cross-surface incident/recovery packet plus explicit action-boundary statuses incorporating observed_success, reported_success_unverified, blocked_unreachable, and failed.

**Biggest unknown:** The remaining blocker is execution reach: there is still no granted read-only dual-serial Mac probe or firmware/bridge test fixture and no correlation-ID plumbing tying serial, relay, I2S/A2DP, and job receipts together. I do not need another model idea; I need those concrete device-observation and test hooks, plus the owner's approval before any write/flash operation.

