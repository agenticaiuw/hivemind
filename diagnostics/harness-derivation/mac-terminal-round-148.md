# Harness derivation — mac-terminal — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **USB bench integration surface** — Live inventory has no dedicated serial-device route or tool. The owner’s Mac bridge and Safari are online, but coordination with the physically connected nRF9160 and ESP32 must currently be implemented as a Mac harness; existing HTTP pipeline routes do not expose serial health or timing counters.
  - evidence: discover:routes lists /execute and pipeline endpoints but no serial route; get_hardware_spec(bridge), get_hardware_spec(pendant) identify the two boards and their audio constraints; request_tool t22-ib1b was queued for bounded read-only serial diagnostics.

## Capabilities it proposed

### "When I press the pendant while it is USB-connected, let me say or choose a command for my Mac, execute it locally even with no LTE, and hear a truthful result; if I unplug it, queue the same request and finish it when the relay returns."
- **useful because:** This makes the wearable useful today on the bench instead of pretending LTE registration exists, while preserving the same intent across USB-local and cloud-remote operation. The owner gets one physical command surface with continuity rather than a separate Mac workflow and an unreliable offline gadget.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → relay → dashboard
- **model tier:** Realtime only for the short spoken intent and final spoken acknowledgement; use a cheaper background model to normalize queued requests, classify completion, and summarize receipts.
- **latency:** Button-to-local acknowledgement under 300 ms; local execution starts under 1 s; USB serial reconnect detection under 2 s; queued cloud handoff is asynchronous.
- **cost:** About $0.01–$0.05 per spoken cloud turn depending on transcription/context; USB-local commands can avoid model/API cost when mapped deterministically. Dominant cost is realtime speech/context, not serial transport.
- **security:** The existing owner policy allows unrestricted trusted execution. Still expose whether execution was USB-local or relay-remote, never claim completion without a receipt, and carry only the request plus bounded result across relay. Confirmation is not required by owner policy, but destructive actions remain visibly labeled in the receipt.
- **missing:** A Mac serial daemon for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with framed, CRC'd pendant/bridge messages; A local USB intent endpoint and reconnectable queue that can select local execution before relay dispatch; Firmware/bridge message types for request, receipt, and spoken-result playback; current accepted status beacon can display state but does not transport arbitrary intents; A unified request ID spanning pendant button edge, Mac /execute jobId, relay pipelineId, and final audio receipt

### "Calibrate my wearable audio link: play a deterministic sweep through the nRF9160 and ESP32 bridge, measure USB/I2S/Bluetooth timing and dropouts, then save the correction profile and tell me whether the link is healthy."
- **useful because:** The two boards are physically attached now, so this gives the owner a concrete answer about whether the thing they wear will sound reliable instead of discovering drift, starvation, or latency during a real conversation. It also turns the bridge's known 31,250→44,100 resampling and tight buffer limit into measured facts.
- **path:** pendant → Mac-terminal → mac-vision → relay-realtime → dashboard
- **model tier:** No realtime model for the test itself. Use deterministic DSP and a cheap background model only to explain the measurements in plain language; reserve realtime for an optional spoken verdict.
- **latency:** A 30–60 second automated test, with first pass/fail in under 5 seconds and a detailed report afterward.
- **cost:** Near-zero API cost for deterministic tones, serial timestamps, and packet counters; under $0.01 for an optional concise explanation. Hardware cost $0 using the connected boards.
- **security:** No microphone recording leaves the Mac; use generated tones and aggregate counters only. Do not silently overwrite the active audio profile: version profiles and select the new one explicitly in the local agent.
- **missing:** A typed serial test harness that can address both live USB ports and correlate nRF frame IDs with ESP32 I2S/Bluetooth counters; A loopback or timestamp marker in firmware/bridge (including underrun, overrun, reconnect, and SBC queue depth counters); A profile store and route to apply a selected latency/resampling correction to the playback pipeline; A dashboard/report endpoint exposing test run, raw counters, verdict, and profile version

### "That Mac command failed — diagnose the actual exit condition, show me the smallest repair, and retry only the failed step without repeating anything that already succeeded."
- **useful because:** Today a failed shell action loses its exit code, cancellation cannot interrupt it, and retries are absent; the owner either repeats an entire multi-step task or manually reconstructs what happened. A repair-aware retry would make long Mac and browser work dependable while preserving completed side effects.
- **path:** mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background model for failure classification and repair drafting; use realtime only when the owner asks by voice or needs a short spoken verdict. Deterministic exit/signal parsing should happen before any model call.
- **latency:** Failure diagnosis under 2 s from retained job data; retry starts under 1 s after the owner asks; long-running repaired commands remain asynchronous with pendant status beacon updates.
- **cost:** Usually $0.005–$0.03 for a bounded failure excerpt and repair plan; deterministic retries cost no model tokens when the failed action has a declared repair recipe. Main cost is sending shell output/context, so hash and cap unchanged output.
- **security:** Honor the existing maximum-access/no-gate policy. Never claim a retry is safe merely because it is syntactically repeatable: label whether the step is idempotent, unknown, or already has an observable receipt. Redact secret values from diagnostic context while retaining variable names and presence. The owner decides whether to run high-impact repairs under their existing policy.
- **missing:** Capture shell exit code, signal, pid, true start/finish timestamps, argv-vs-shell form, and a bounded stdout/stderr artifact in the receipt; Wire the existing executionContext idempotency engine to /execute and map planMeta.jobId to the action ledger; close ledgers on success/failure; A repair endpoint that accepts jobId plus failed stepKey and produces a minimal runnable action list, with deterministic deduplication of completed steps; AbortSignal propagation into child processes so a failed or cancelled repair does not leave an orphaned shell running

### "Send this reply privately to my headphones, or play it on the Mac speakers instead, and remember the choice for this conversation."
- **useful because:** The owner currently has a fixed nRF9160 → ESP32 A2DP path and no unified, truthful route selector. A per-conversation audio destination would let them move between walking, desk, and shared-room contexts without restarting the conversation or accidentally speaking private content aloud.
- **path:** pendant → ESP32 audio bridge → mac-terminal → relay-realtime → dashboard
- **model tier:** Use realtime only for the spoken route command and acknowledgement; route selection, persistence, and health checks are deterministic. A cheap background model is unnecessary.
- **latency:** Apply a route change within 1 second when the target is available; if unavailable, report that locally within 500 ms and retain the current route.
- **cost:** Near-zero API cost; Bluetooth and local audio switching are device operations. Hardware cost is $0 for the prototype, though a product pendant may need a better audio multiplexer.
- **security:** Treat route as privacy-sensitive state. Never claim private playback if the bridge is disconnected or the output device is unknown. Persist only route identity and health, not audio. Require an explicit local status indication before falling back to Mac speakers.
- **missing:** A typed route registry spanning pendant, ESP32 Bluetooth output, Mac audio devices, and relay session state; A route-selection control message and acknowledgement over the USB/LTE transport; Mac audio-device enumeration and switching integrated with the bridge health state; A privacy-preserving fallback policy that distinguishes headphones, Mac speakers, and unavailable outputs

### "Keep working on this even if my Mac goes to sleep: wake it when needed, continue the local/browser steps, and tell me on the pendant whether it finished, is waiting for the Mac, or failed."
- **useful because:** A Mac-only agent currently disappears exactly when the owner closes the lid or walks away, while the relay and wearable can remain available. Sleep-aware escrow would make long browser and shell work genuinely unattended instead of leaving a job apparently running until the owner reopens the laptop.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use a cheap background model for queued task planning and completion summarization; use realtime only for the owner’s short request and final alert. Wake decisions and job lease handling are deterministic.
- **latency:** Acknowledge escrow immediately; wake attempt within 10 seconds of the required deadline; resume within 15 seconds after the Mac agent is healthy; no voice turn should block on sleep.
- **cost:** Low API cost while queued; roughly $0.01–$0.05 for eventual summarization. Requires a Mac networking/power integration, potentially a small always-on LAN helper or router Wake-on-LAN support; no pendant hardware change.
- **security:** Only wake the paired Mac and only resume a job whose signed lease and expected host fingerprint match. Do not transmit shell environment or private browser contents to the relay while the Mac is asleep. The pendant must show ‘waiting for Mac’ rather than implying progress.
- **missing:** A relay-side durable task escrow with leases, deadlines, and explicit sleep/wake states; A paired-Mac Wake-on-LAN or native power-management adapter and a boot-time local-agent resume handshake; A resumable cross-surface job protocol that records browser tab fingerprints and shell step idempotency before sleep; Pendant payloads for waiting-for-host, wake-requested, resumed, and expired states


## Changes it proposed to its own stack

### `firmware` — Add a closed-loop audio quality controller spanning nRF9160 firmware, ESP32 bridge, Mac serial harness, and relay: every audio frame carries a compact sequence/timing marker; the bridge reports underruns, Bluetooth queue depth, and resampler drift; the relay reports acknowledged-frame age. The pendant adapts Opus bitrate, packet duration, and playback jitter target within bounded profiles, with hysteresis and a persisted last-known-good profile. On USB bench mode the Mac harness runs the same controller without LTE, so the owner can validate it before wearing the device away from the Mac.
- **owner gets:** Speech should remain intelligible when Bluetooth or radio conditions change instead of silently stalling or sounding delayed. The owner gets graceful degradation and automatic recovery, not a one-time test that becomes stale as conditions change.
- effort: High: new framed telemetry and control messages on both chips, a small state machine in the pendant, relay quality feedback, and a Mac USB transport emulator/test harness. Requires end-to-end soak tests across USB, LTE, and Bluetooth fault injection.  ·  risk: Bad controller tuning could oscillate bitrate or add latency; protect against this with discrete profiles, minimum dwell times, upper latency bounds, and a hard fallback to today’s fixed configuration. If telemetry is malformed or absent, continue using the last-known-good profile and never invent link health.
- cost: Negligible API cost because decisions are deterministic; roughly 1–3% extra serial/radio telemetry bandwidth. Firmware RAM should stay under a few KB for counters and state. No new hardware required for the prototype.  ·  latency: Telemetry adds one small control interval, target under 500 ms; adaptation may temporarily increase buffering by at most one frame. Stable conditions incur no additional conversational latency.
- security: Telemetry contains sequence numbers and timing only, not microphone content. Authenticate control frames to prevent a local USB peer or relay spoof from forcing pathological settings; do not transmit raw audio for diagnostics.
- depends on: A CRC-framed serial protocol for the physically connected nRF9160 and ESP32; Bridge counters for SBC queue depth, underruns, and resampler drift; Relay acknowledgement-age telemetry; A Mac USB harness capable of injecting loss, delay, and reconnect faults


## What it asked for

### `t22-ib1b` (tool) — mac_usb_serial_diagnostics
- why: The nRF9160 and ESP32 are physically connected over USB now, but the live Mac diagnostics only cover host facts and authenticated HTTP endpoints. I need to establish whether either serial device is enumerated and read bounded, non-mutating health/counter frames before designing the bench audio and wearable continuity work.

```json
{
  "type": "object",
  "properties": {
    "ports": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "/dev/cu.usbmodem00096003658",
          "/dev/cu.usbmodem00096003658A",
          "/dev/cu.usbmodem00096003658B",
          "/dev/cu.usbserial-0287A9CA"
        ]
      },
      "maxItems": 4
    },
    "read_ms": {
      "type": "integer",
      "minimum": 50,
      "maximum": 5000
    },
    "max_bytes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 65536
    }
  },
  "required": [
    "ports"
  ]
}
```

