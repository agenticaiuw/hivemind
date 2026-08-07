# Harness derivation — unified — round 65

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-and-cross-surface-status** — Relay is reachable and Mac bridge online; current pipeline proves downlink TTS is 24,000 Hz mono PCM, while an actual pendant uplink remains 15,625 Hz PCM (937,500 bytes, audio-native realtime). Browser extension is offline with five pending commands. Accessibility and Screen Recording remain absent, but AppleScript automation is granted.
  - evidence: GET /ops/status, GET /pipeline, GET /browser/status at 2026-08-07T12:03Z

## Capabilities it proposed

### "When something goes wrong, say “capture this incident”; the pendant should preserve the moment, the relay should correlate it with the live audio/link/job evidence, the Mac should collect UART and agent logs, and I should receive a short sourced diagnosis plus a repair ticket I can review."
- **useful because:** No single surface can establish what the owner experienced, what the network delivered, and what the Mac actually did. This turns a fleeting wearable failure into an evidence-backed, reviewable repair item instead of an unrepeatable complaint.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → unified
- **model tier:** Use realtime only to acknowledge the capture and ask one clarifying question if needed; use a cheaper background model to correlate logs, classify the incident, and draft the ticket. Keep raw audio local/short-lived and send only the selected incident window plus metadata.
- **latency:** Immediate acknowledgement under 1 second; evidence collection 5–20 seconds depending on Mac availability; diagnosis and draft ticket under 2 minutes, with a durable pending state if the Mac or pendant link is offline.
- **cost:** Low per incident: one short realtime turn plus a background summarization/classification call; dominant cost is log/audio upload and context, bounded by a configurable incident window and compact typed metadata.
- **security:** Incident audio and logs can contain private speech, tokens, and account data. Default to a 30–60 second window, redact secrets before relay storage, show exactly which files/snippets leave the Mac, require confirmation before opening a ticket externally or changing software, and retain a local receipt even when upload fails.
- **missing:** A device-side incident-capture trigger and bounded local spool (the requested incident_capture_and_delivery_receipt skill is still not granted); A relay correlation API joining pendant event, audio pipeline run, job id, and delivery receipt; A Mac allowlisted log collector that can read UART and agent logs without Accessibility or Screen Recording; A durable repair-ticket destination and review UI

### "Move this conversation to my Mac without starting over."
- **useful because:** Today the pendant, relay, Mac, and browser can each hold fragments of a task, but the owner cannot deliberately transfer the live interaction with its current transcript, pending question, evidence, and approval state. A true handoff would let them switch from voice to a private screen without repeating themselves.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use realtime only for the short handoff acknowledgement. The relay should package the existing turn and state; a cheaper background model can produce the compact Mac workspace summary and citations. No new expensive reasoning is needed unless the owner asks a follow-up.
- **latency:** Acknowledge the button/voice handoff in under 500 ms; Mac workspace should appear within 3 seconds when online. If the Mac is unavailable, retain a resumable handoff token and tell the owner locally.
- **cost:** Usually one small state-packaging call, dominated by transcript/context serialization rather than model inference; near-zero cost for the local handoff and no need to resend the full conversation.
- **security:** The handoff may expose private voice content on the Mac or authenticated browser. Encrypt the token, bind it to the paired Mac and session, expire it quickly, and display only the minimum relevant transcript/evidence. Never carry secret fields into browser forms automatically.
- **missing:** A first-class handoff token/state schema spanning pendant session, relay job, Mac workspace, and browser tabs; A Mac route that opens or focuses a resumable workspace without Accessibility (AppleScript can open the workspace); A browser-side session binding that can attach relevant tabs without losing provenance; A pendant-local fallback message when the destination is offline


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio profile handshake and conformance receipt spanning pendant, bridge, relay, and client: the pendant advertises its actual capture rate/codec, relay records the negotiated profile and packet-loss/jitter metrics, and each completed conversation exposes a compact receipt stating capture rate, encoded rate, decode status, underruns, and fallback reason. Include a synthetic loopback test route that can run without a live conversation.
- **owner gets:** The owner can finally tell whether “24 kHz audio” is genuinely working at the ear, rather than trusting a setting that silently falls back to today’s 15,625 Hz capture or 16 kHz Opus path. Failures become actionable instead of subjective.
- effort: Medium: protocol/schema update, pendant and bridge telemetry, relay persistence/API, and a small automated loopback test; no Accessibility or Screen Recording needed.  ·  risk: Older clients may omit profile fields; treat missing telemetry as unknown, not success. A malformed negotiation must fall back to the known 16 kHz profile and preserve a receipt. Recover with versioned schemas and a server-side feature flag.
- cost: Negligible API cost; a few hundred bytes of metadata per run and modest test traffic. Hardware cost is zero for telemetry, but true 24 kHz capture still depends on a production microphone/clock path not present in the current DK.  ·  latency: Handshake adds at most one control round trip before audio; receipt generation is asynchronous and does not delay playback.
- security: Telemetry should contain no raw speech; use coarse metrics and opaque run IDs. Audio test fixtures must be synthetic and must not upload owner recordings.
- depends on: 24 kHz audio target architecture and end-to-end acceptance thresholds (still not supplied); audio_pipeline_validate tool (still not supplied); A production pendant audio front end capable of a 24 kHz capture profile; current hardware reports 15,625 Hz capture

### `hardware` — Add a tiny low-power haptic actuator with a dedicated driver (or a piezo/buzzer fallback) to the production pendant, and define a local tactile status vocabulary: one pulse for capture started, two for response ready, long pulse for waiting approval, repeating pulse for link failure, and a cancellable warning pattern for sensitive output. Drive these patterns locally from the pendant state machine, not from the relay.
- **owner gets:** The owner can use the pendant in a meeting, walking, or a noisy room without speaking aloud or staring at a screen. They will know whether they are recording, whether a response is ready, or whether an action is blocked—even when audio is muted or the LTE link drops.
- effort: Medium hardware and firmware change: actuator, transistor/driver, board layout, enclosure coupling, calibrated patterns, and state-machine tests. It must be added to the production design because the current nRF9160 DK exposes only one button and an LED.  ·  risk: Poor coupling can make patterns imperceptible or drain power; excessive vibration can be annoying. Provide a firmware-disable setting, conservative duty cycle, and LED/audio fallback. Never use haptics as proof that an irreversible action happened; completion must still require a delivery receipt.
- cost: Approximately $0.30–$1.50 in components plus PCB/enclosure revision; roughly 1–8 mA only during short pulses and negligible idle draw. No per-invocation API cost.  ·  latency: Local indication can begin within tens of milliseconds and remains available offline; no relay round trip.
- security: Improves privacy by replacing spoken status announcements. Patterns must not encode message contents or secrets; only coarse state categories may be signaled.
- depends on: A production pendant hardware revision beyond the current nRF9160 DK; A firmware state taxonomy shared with relay receipts and approval states; Owner-configurable privacy and interruption policy


## What it asked for

_Nothing._
## Its own summary

Recorded two forward-looking proposals: a production pendant haptic state channel for private, offline status feedback, and an explicit live conversation handoff between pendant, relay, Mac, and browser using resumable state. Both require new connective or hardware work rather than assuming today’s wiring is sufficient.

**Biggest unknown:** Whether the owner would accept a haptic actuator and which physical patterns feel distinguishable without becoming distracting; no further discovery is available this round.

