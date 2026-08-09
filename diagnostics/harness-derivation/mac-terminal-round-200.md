# Harness derivation — mac-terminal — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **bench hardware reachability** — The granted mac_usb_serial_diagnostics schema is still unresolved in the live inventory; no serial capability is callable despite the two chips being physically connected. A bench test must currently use run_shell/capture scripts or implement a real serial action.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; best match action:get_mac_status score 0.226, inventory has no serial capability.

## Capabilities it proposed

### "When I press the pendant's button and say “handle this,” use whatever is in front of me to do the right thing — the current Mac project, focused window, or authenticated browser page — and tell me on the pendant exactly what happened."
- **useful because:** This is the core hive experience: the wearable supplies an interruption and voice, the Mac supplies physical context and actuation, the browser supplies sessions the relay cannot reach, and the relay keeps the request alive when one link drops. Today each surface can act, but none can make the same intent follow the owner's actual context end to end.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only for the short intent interpretation and spoken acknowledgement; background planner on the Mac for computer/browser actions, with a cheap relay classifier selecting Mac versus browser and a durable job state.
- **latency:** Acknowledge on the pendant in under 500 ms; choose the target in under 2 s; return a result or honest queued status within 10 s for ordinary actions. Long browser work continues asynchronously.
- **cost:** ~$0.01–$0.04 per interaction depending on whether a realtime turn and planner call are both needed; latency and cost are dominated by the planner/browser loop, not routing.
- **security:** The request may act inside authenticated browser sessions or modify files. Preserve the existing owner policy (no confirmation for routine actions, confirmation for destructive work), bind every action to a turn ID and target snapshot, and return the exact target URL/project/window in the spoken receipt. Do not send browser content to the relay unless the browser harness explicitly returns it.
- **missing:** A single intent envelope joining pendant turn ID, Mac context snapshot, browser session/page identity, and relay job ID; A router that chooses Mac or browser based on live presence and keeps the same job through failover; A result protocol that maps action receipts back to a pendant acknowledgement and truthful_action_status_beacon state; Mac snapshot capture of foreground app/window, active project, and browser tab at the button edge

### "Keep my conversation intelligible even when LTE-M is congested: if speech starts dropping, automatically trade fidelity for continuity, tell me what changed, and restore quality when the link is healthy again."
- **useful because:** The measured system loses about 7.8 seconds of uplink speech when downlink speech competes with it. This is a felt failure, not infrastructure: the owner should hear a complete lower-quality conversation rather than confident silence, and should know whether the Mac-connected bench bridge or LTE path is responsible.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** No expensive model in the control loop. Firmware/relay heuristics classify packet loss, queue age, and modem contention; a background model can summarize recurring link failures later.
- **latency:** Detect degradation within 300 ms, switch codec/frame policy within 1 s, and recover over 2–5 s of stable acknowledgements. Dashboard diagnostics can lag by 10 s.
- **cost:** Negligible inference cost; roughly 1–2 KB/s extra telemetry during a call. Engineering cost is in synchronized firmware, Worker, and ESP32 changes.
- **security:** Audio remains end-to-end on the existing TLS WebSocket; telemetry should contain counters and codec mode only, never speech. Never claim recovery until acknowledged audio frames resume. SD remains failure buffering only, respecting the owner's storage rule.
- **missing:** A negotiated quality-control message on the existing audio WebSocket with sequence, effective-at frame, and acknowledgement; A relay congestion controller that reserves uplink bandwidth for owner speech and can request a downlink bitrate/frame-duration change; nRF9160 encoder policy that can switch bitrate or packet duration without losing turn alignment; ESP32 bridge support for mode changes and an operator-visible quality timeline in the dashboard

### "When I plug the pendant and audio bridge into my Mac, run a one-command bench check and tell me whether the microphone, Opus timing, I2S path, Bluetooth audio, and relay handshake are actually healthy — and file a useful bug report if they are not."
- **useful because:** The hardware is connected now, but the system has no trustworthy end-to-end answer about the two chips. Existing capture scripts produce UART logs; they do not correlate both devices, parse frame timing, test the relay handshake, or turn a failure into an actionable report. This would make today's prototype testable by the owner rather than by reading raw logs.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Deterministic local parser and scripted probes first; use a cheap background model only to summarize correlated failures into a bug report. Realtime is unnecessary.
- **latency:** Start feedback within 2 s of the spoken request or dashboard click; complete the short smoke test in 30 s and a 60 s soak in under 2 min. Show incremental stage results on the dashboard and pendant beacon.
- **cost:** Near-zero model cost; local USB serial and audio checks dominate. Storage is a few hundred KB of bounded logs per run, with retention and redaction.
- **security:** USB logs can contain tokens, URLs, and audio metadata. Redact secrets before any relay upload; default to local retention and upload only a digest plus selected evidence after explicit bug-report intent. Do not open the microphone beyond the scripted test window.
- **missing:** A typed local bench-test action that opens the two known serial devices, runs bounded non-mutating probes, and returns framed records rather than opaque shell output; A shared timestamp/sequence format so nRF9160 UART, ESP32 UART, and relay pipeline events can be correlated; Deterministic assertions for Opus encode/decode budget, I2S underrun, resampler continuity, A2DP state, and WebSocket acknowledgement; A bug-report route accepting redacted evidence bundles and linking them to the dashboard run and pendant turn

### "After you act for me, show me a compact before-and-after proof of what changed — the file diff, browser field change, window/audio setting, or message draft — and let me ask about one specific change without replaying the whole job."
- **useful because:** Today the owner can receive success/failure and some receipts, but a spoken “done” is not enough to audit an autonomous action. A durable, source-linked change proof would make the system useful for consequential multi-step work without forcing the owner to watch the Mac.
- **path:** relay → mac-planner → browser → dashboard → pendant
- **model tier:** Deterministic before/after capture and diffing on the Mac/browser; a cheap summarizer turns the diff into one spoken sentence. Realtime is only needed for follow-up questions.
- **latency:** Capture pre-state before each mutation and render a first proof within 2 s of completion; follow-up answers under 3 s when evidence is local.
- **cost:** Low model cost; storage is bounded diffs and browser field metadata, not page copies. Large screenshots or files should be opt-in.
- **security:** Redact secrets, tokens, passwords, and unrelated browser content from evidence. Destructive or external side effects must be labeled as irreversible when no before-state exists. Preserve provenance and distinguish observed post-state from claimed success.
- **missing:** A mutation-aware before-state capture contract for file, browser, UI, and audio actions; A normalized change-evidence schema with redaction and size limits; A relay route that streams the evidence summary and stable evidence IDs to the pendant; Dashboard drill-down and a follow-up query that retrieves only the selected evidence item

### "Let me say “do not interrupt me until 3” (or “only interrupt for my partner or a meeting change”), and have the pendant, Mac notifications, browser alerts, and scheduled agent briefings all honor that boundary, then give me a quiet catch-up afterward."
- **useful because:** The owner cannot control interruption policy across the hive today: a pendant reply, Mac notification, browser page watch, and routine can each break concentration independently. One spoken attention boundary would make the system feel like an assistant rather than four competing alert sources.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap deterministic policy evaluation for time, sender, and event type; a background summarizer produces the deferred catch-up. Realtime handles only setting or changing the boundary.
- **latency:** Acknowledge the new boundary on the pendant within 500 ms and propagate it to connected surfaces within 2 s. Deferred digest can run at the release time or on demand.
- **cost:** Tiny inference cost; the dominant work is event filtering and durable policy state, not generation.
- **security:** The policy itself is sensitive (who may interrupt). Keep it encrypted/tenant-bound, fail closed for unclassified notifications, and never silently discard events: queue a timestamped digest with source and reason. External emergency channels should require explicit opt-in.
- **missing:** A durable attention-policy object with expiry, exceptions, timezone, and precedence rules; Relay fan-out to Mac notification suppression, browser page-watch delivery, pendant audio, and routine execution; An event inbox that queues suppressed items without marking them read or claiming delivery; A release digest with per-item source, urgency rationale, and an explicit clear/extend action


## Changes it proposed to its own stack

### `hardware` — Add a low-power I2C fuel-gauge IC and a protected Li-ion charger/power-path to the wearable revision, with a monotonic battery sample exposed to firmware and relay. Keep the gauge asleep between samples and reserve an interrupt for low-battery warning; do not infer charge from modem voltage.
- **owner gets:** The pendant currently cannot tell its wearer whether it will survive a call, and the agent cannot distinguish a dead radio from a depleted device. A spoken answer and truthful LED state would become trustworthy instead of guessing host or network failure.
- effort: Moderate hardware revision plus a small Zephyr driver, calibration table, relay field, and dashboard display. Validate under LTE transmit bursts and audio playback, not just idle USB power.  ·  risk: Gauge calibration or charger brownouts could create false alarms; recover with conservative thresholds, hysteresis, and a raw-voltage fallback explicitly labeled estimated. A board revision delays prototype testing but does not affect the current USB bench unit.
- cost: Approximately $2–$5 BOM increase at low volume and a few hundred microwatts average for periodic sampling; negligible API cost.  ·  latency: Battery samples every 30–60 s, with interrupt-driven critical-low warning under 100 ms. No call-path latency.
- security: Battery state is low sensitivity. Do not include serial numbers or location in the telemetry; bind samples to the device's authenticated session.
- depends on: A product wearable power-path design rather than the current nRF9160 DK USB/battery arrangement; A small authenticated battery-status field in the pendant↔relay protocol; Dashboard and spoken formatting that says unknown when no fresh sample exists

### `hardware` — Add a physical, power-domain microphone disconnect switch to the product pendant: a recessed two-position privacy shutter that removes mic power and presents a hardware-readable state to firmware, plus a visible mechanical indicator. Firmware must refuse to enter recording while the shutter is closed and relay/dashboard must display the state as authoritative, not inferred.
- **owner gets:** The owner could wear the pendant in meetings and around other people while having a physically provable guarantee that it cannot listen. Today the software LED, link state, and button behavior cannot provide that guarantee; a crash or stale UI could leave the owner unsure.
- effort: Product-board revision, microphone power gating, GPIO input/debounce, boot-time self-test, enclosure change, and protocol/dashboard support. Validate that closing the shutter during an active call cuts capture immediately and emits a clear end-of-capture event.  ·  risk: A failed switch or bounce could falsely report privacy. Use dual-polarity sensing and fail closed: disagreement means recording prohibited and state unknown. Cutting power mid-frame may discard the current frame, which is preferable to capturing after the owner's physical action.
- cost: Roughly $0.30–$1.50 BOM plus enclosure tooling; sub-milliamp leakage when off; no API/model cost.  ·  latency: Hardware cutoff under 20 ms; firmware state propagation on the next control frame, under 500 ms.
- security: Strongly improves privacy by creating a hardware boundary. The relay must never override the local state, and logs should record only open/closed transitions, not microphone data.
- depends on: A product pendant revision with independently switchable microphone power; A fail-closed capture state in nRF9160 firmware; A privacy-state field in the pendant↔relay protocol and dashboard


## What it asked for

_Nothing._
## Its own summary

Round 200 produced four owner-facing changes: (1) a cross-surface “handle this” intent that binds pendant turn, Mac context, authenticated browser session, relay job, and truthful result; (2) adaptive audio continuity that protects owner speech under LTE contention and restores quality only after acknowledged recovery; (3) a dual-chip Mac bench check that correlates nRF9160/ESP32 UART, Opus/I2S/A2DP timing, and relay events into a redacted bug report; and (4) a product-hardware fuel gauge/power-path revision so battery and radio failure are distinguishable. I also verified browser.status is currently offline and pipeline has a processing run. The newly granted serial diagnostic tool still does not resolve: there is no callable serial capability in the live inventory, so today’s bench test remains shell/capture-script based.

**Biggest unknown:** Whether the owner wants the immediate implementation priority to be the live USB bench test (which needs a real serial capability or a typed run-shell adapter) or the end-to-end “handle this” job envelope. The most concrete missing capability is bounded dual-port serial access with framed, redacted output and timestamps.

