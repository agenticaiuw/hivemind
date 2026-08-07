# Harness derivation — faculty-action — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current action reachability** — Mac bridge and relay are online and relay advertises pendantPipelineTelemetry, pendantSpeech, and durableAudio, but Mac agent is not ready because Accessibility and Screen Recording are untrusted; browser extension is offline with 3 pending commands.
  - evidence: GET /ops/status returned relay.macBridgeOnline=true, capabilities.pendantPipelineTelemetry=true/durableAudio=true; permissions.ready=false with accessibility.trusted=false and screenRecording.granted=false; browser.online=false and pendingCommands=3.

## Capabilities it proposed

### "“Is my pendant audio healthy?”"
- **useful because:** Instead of vague failures, the owner gets a one-sentence answer plus a receipt showing whether the fault is microphone capture, relay transport, Opus decode, resampling, or Bluetooth output, and a suggested recovery step.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Background/cheap model summarizes deterministic measurements; realtime is used only if the owner asks this while wearing the pendant.
- **latency:** 10–20 seconds for a live 10-second diagnostic; under 2 seconds for cached last-known health. The test fixture and DSP run locally; only metrics cross nodes.
- **cost:** Near-zero API cost for local signal checks; <$0.01 for optional natural-language summary. Dominant cost is a short diagnostic capture and Bluetooth playback.
- **security:** Use synthetic tones or a locally stored consented fixture, never owner speech. Require explicit confirmation before emitting audible tones; redact UART and transcript data. Dashboard access must be paired/authenticated.
- **missing:** The 24 kHz conformance harness and sample-counter telemetry proposed above; A user-facing health endpoint that correlates pendant, relay, and ESP32/BT receipts; A quiet diagnostic mode (headphone loopback or owner-confirmed audible test)

### "“Prepare this action on my Mac, and let me approve it from the pendant when you’re ready.”"
- **useful because:** The owner can start a complicated task from a spoken request, walk away from the Mac, and approve the exact final action from the device they are wearing. The Mac/browser can gather context and fill reversible fields, while the pendant provides a clear, local final commit instead of requiring the owner to return to the screen.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background/model routing handles preparation and evidence extraction; realtime is used only for the initial spoken request or clarification. The final approval is a deterministic protocol, not an LLM decision.
- **latency:** Preparation may take tens of seconds in the background; approval acknowledgement should reach the pendant within 1 second when connected. An approval remains valid for only a short, explicit lease window.
- **cost:** Usually <$0.01 per preparation, dominated by browser/Mac work; negligible cost for the approval handshake and receipt.
- **security:** The approval payload must be cryptographically bound to the exact target, account, fields, and irreversible effects, with a digest and human-readable summary spoken/displayed before commit. Expire approvals on content, tab, or account changes; require a second confirmation for sending mail, deletion, purchases, or other destructive actions. Do not expose secrets on the pendant; store only a short-lived nonce and receipt.
- **missing:** A relay-mediated two-phase commit protocol binding Mac/browser evidence to a pendant approval nonce; A compact pendant confirmation UX using the single button and LED, including cancellation and timeout semantics; A durable, tamper-evident before/after receipt that the Mac and relay can reconcile after reconnect; Mac/browser adapters that can pause exactly before submission and resume only with the matching approval


## Changes it proposed to its own stack

### `integration` — Build a 24 kHz duplex audio conformance harness spanning all four bodies: inject deterministic swept-tone and speech fixtures at the pendant I2S/UART test point, tag every Opus frame with a monotonic sample counter, collect relay packet/jitter telemetry, capture the Mac/ESP32 output, and compare end-to-end sample rate, drift, loss concealment, latency, and spectral error. Emit a signed receipt with per-stage timestamps and automatically quarantine/revert the last audio firmware or relay codec change when thresholds fail; keep raw audio local and upload only hashes/metrics.
- **owner gets:** The owner gets speech that stays intelligible and in sync after real reconnects, instead of discovering a broken 24 kHz path during a conversation. A concise pass/fail receipt makes “audio is fixed” trustworthy and catches regressions across the pendant, network relay, and headphone bridge—not just in one node.
- effort: Medium-high: firmware test instrumentation and sample counters, relay telemetry schema, Mac/ESP32 capture adapter, golden fixtures, CI/nightly runner, and rollback integration. Requires a safe UART/J-Link test mode and a small hardware loopback fixture.  ·  risk: Test mode must be impossible to enter from normal button presses and must never transmit fixture audio as owner speech. Clock-counter bugs could falsely fail builds; gate rollout on a known-good baseline and retain the previous codec config for one-click rollback. No raw owner audio leaves the Mac; fixtures and aggregate metrics only.
- cost: Low recurring API cost (local DSP and deterministic fixtures; occasional cheap background analysis). Rough hardware fixture cost $20–50, negligible power outside tests.  ·  latency: No production latency when instrumentation is disabled; frame counters add 4–8 bytes per packet and telemetry is sampled asynchronously.
- security: Counters and hashes are non-sensitive, but UART logs can contain transcripts; redact payloads before storage and require local pairing/authentication for test control.
- depends on: 24 kHz codec path implementation and explicit acceptance thresholds; durable pipeline telemetry at pendant, relay, and Mac/bridge; a safe firmware test-mode trigger and rollback-capable deployment

### `hardware` — For the product pendant, add a low-power haptic actuator and a fuel-gauge IC with an interrupt line, while retaining the single button and LED. Expose signed battery and haptic-event state to the relay so a pending Mac/browser action can be acknowledged, rejected, or timed out without relying on an ambiguous LED-only signal.
- **owner gets:** The owner can approve or cancel an action confidently while walking, in a pocket, or in bright sunlight, and can be warned before a conversation dies from an empty battery. This makes the wearable a dependable hand for the Mac rather than a remote microphone with an unreliable visual indicator.
- effort: Moderate hardware revision, enclosure/acoustic redesign, driver and power-management work, haptic patterns, battery calibration, and relay protocol integration. Prototype on the current dev kit with an external actuator and gauge before committing a board spin.  ·  risk: Haptics could be distracting or drain the battery; provide quiet hours, intensity limits, and LED fallback. Incorrect fuel-gauge calibration could report false charge, so retain voltage-based fallback and calibration diagnostics. Never treat a haptic event as approval without a button edge and nonce match.
- cost: Approximately $2–6 in added components and PCB area at prototype volume, plus roughly 5–20 mA only during short haptic pulses and under 100 µA for the gauge. No meaningful API cost.  ·  latency: A local approval acknowledgement can be immediate; the gauge interrupt adds no conversation-path latency.
- security: Battery state is low sensitivity. Approval events must remain authenticated and nonce-bound; actuator patterns must not encode secrets or serve as the sole authorization signal.
- depends on: The relay-mediated approval protocol and short-lived action lease; A product-board revision beyond the current nRF9160 development kit; Firmware power and GPIO budget review


## What it asked for

_Nothing._
