# Harness derivation — unified — round 84

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **pendant link and I/O constraints** — The prototype has one full-duplex I2S peripheral, one button, one LED, LTE-M over a single TLS WebSocket, and measured uplink loss under simultaneous 16 kbps uplink/24 kbps downlink. I2C/SPI are currently unused, so a haptic driver is feasible without consuming the audio bus.
  - evidence: get_hardware_spec(pendant), get_hardware_spec(network), get_hardware_spec(io) in Round 84

## Capabilities it proposed

### "If my pendant connection gets bad while we are talking, keep the conversation from disappearing: finish the useful answer somewhere I can see, then resume spoken audio when the link recovers."
- **useful because:** The current LTE-M path is half-duplex in practice and measured contention drops about 7.8 seconds of uplink speech. Today that feels like the assistant forgot me. This makes a degraded call recoverable across the pendant, always-awake relay, Mac/dashboard, and (when relevant) the browser.
- **path:** pendant → relay-realtime → dashboard-ux → mac-planner → browser-extension
- **model tier:** Realtime model only for the live turn; a cheaper background model can compress the interrupted answer and generate the recovery brief.
- **latency:** Detect degradation within 1 second; show a text fallback within 3 seconds; resume audio only after 2 seconds of stable bidirectional link.
- **cost:** Small per-interruption cost: one realtime turn plus an inexpensive summarization pass; dominant cost is the original audio inference, not the fallback.
- **security:** The fallback transcript may expose private speech on the Mac/dashboard, so it must inherit the call's sensitivity and expire with the audio retention policy. Never mirror browser-private content to a non-authenticated surface; require confirmation before any queued action is executed.
- **missing:** A link-quality state machine shared by firmware and relay; A resumable answer cursor/sequence protocol so audio and text cannot duplicate or reorder; A dashboard notification/card for an interrupted turn; An end-to-end test that injects downlink contention and verifies recovery

### "When I say “that’s wrong” or “check that again,” trace the answer back to the exact browser page, Mac file, or conversation evidence it used, re-check the conflicting facts across the available surfaces, tell me precisely what changed, and only update my memory if I approve."
- **useful because:** Today an incorrect answer is difficult to repair: the pendant, relay, Mac, and authenticated browser each know only part of the evidence trail. This would turn a spoken correction into a verifiable, source-linked repair instead of silently compounding an error.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime handles the short acknowledgement and final spoken correction; a cheaper background model performs evidence retrieval, contradiction comparison, and draft memory changes.
- **latency:** Acknowledge within 1 second; return a compact correction within 10 seconds for up to three sources. Longer investigations become a durable job and notify the pendant when complete.
- **cost:** One inexpensive retrieval/comparison pass plus a short realtime response; cost scales with the number of cited sources, not with an always-running watcher.
- **security:** Evidence may include private browser pages, files, or sensitive memories. Keep source access authenticated per surface, redact citations on shared displays, retain an audit trail, and require explicit approval before changing durable memory or taking any external action.
- **missing:** A provenance envelope attached to every model claim, including source surface, timestamp, locator, and excerpt hash; A contradiction/recheck planner that can query Mac and browser evidence in parallel; A user-facing proposed-memory-diff with approve/reject semantics; A durable correction record linked to the original conversation and job


## Changes it proposed to its own stack

### `hardware` — Add a tiny ERM/LRA haptic actuator with a dedicated low-side driver and reserve one GPIO (or an I2C haptic driver) for four short patterns: recording, assistant speaking, link degraded/queued, and local mute. Keep the existing LED as a secondary debug signal. Define a firmware event API so relay state changes and local button events produce patterns without touching the full-duplex I2S path.
- **owner gets:** The owner can know—silently and in a pocket or noisy street—whether the pendant is listening, speaking, muted, or holding a response. This is especially important when LTE-M contention makes audio unreliable and speaking a status aloud would be awkward or unsafe.
- effort: Prototype with a coin vibration motor, transistor, flyback protection, and a PWM GPIO; then characterize comfort, audible buzz, and current draw. Add a small event queue and rate limiter in Zephyr. Product revision can use an LRA for quieter, more distinct patterns.  ·  risk: Motor noise can leak into the microphone and false-trigger speech; isolate mechanically, gate the mic during the 20–60 ms onset, and test echo. Excessive vibration drains the battery or annoys the owner; cap duty cycle and provide a dashboard setting to disable patterns. Recover by falling back to LED-only if the driver self-test fails.
- cost: Rough prototype BOM $2–6 and about 15–80 mA only during pulses; negligible API cost. A production LRA plus driver is roughly $1–3 at volume.  ·  latency: Pattern starts within 50 ms of a local event; relay-originated state depends on WebSocket latency and should not block audio.
- security: No new data leaves the device. Local mute must be enforced in firmware before uplink, not merely represented by a haptic pattern.
- depends on: Define authoritative conversation/link states in the relay and firmware; Share one event sequencing format across POST /pipeline/events and the pendant WebSocket; Validate mic isolation against the existing single full-duplex I2S peripheral


## What it asked for

_Nothing._
