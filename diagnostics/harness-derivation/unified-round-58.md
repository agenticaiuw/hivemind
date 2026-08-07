# Harness derivation — unified — round 58

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current-reachability** — Relay and Mac bridge are online; Chrome extension is offline with 4 pending commands; Mac computer-use is not ready because Accessibility and Screen Recording are untrusted; relay reports durable audio and pendant speech capabilities; current prototype audio is 15.625 kHz capture, 24 kHz Opus playback, 87% combined CPU, and simultaneous LTE-M speech loss.
  - evidence: GET /ops/status, GET /capabilities, get_hardware_spec(all), and devices discovery in Round 58

## Capabilities it proposed

### "“If I ask you to do something across my pendant, Mac, and browser, tell me what you can actually reach right now, continue through any available surfaces, and leave a resumable handoff for the rest—never say it’s done unless the target surface proves completion.”"
- **useful because:** Today the browser is offline, Accessibility and Screen Recording are not trusted, and the Mac timezone conflicts with remembered owner data. The owner needs one honest answer and a recoverable task rather than a false success or a dead end. This is genuinely cross-node: the pendant provides the request and interruption channel, the relay owns durable state and truth about leases, the Mac executes local work, and the browser extension executes private logged-in work when it returns.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the realtime model only for the short spoken status and clarification; use a cheaper background planner for decomposition, reconciliation, retries, and completion verification.
- **latency:** Speak an initial reachability summary within 1 second; enqueue unavailable steps immediately; background retries use exponential backoff and report a concise receipt when a surface reconnects.
- **cost:** Approximately $0.01–$0.05 per multi-step task, dominated by background planning and any screenshot/vision verification; status checks and receipts are local/relay work.
- **security:** Private browser data remains on the authenticated browser bridge; relay stores only task metadata, opaque step IDs, hashes, and receipts. Never retry irreversible actions automatically. Require confirmation immediately before send/delete/purchase, and invalidate a lease if device identity or tab affinity changes.
- **missing:** A durable cross-surface task schema with per-step reachability, lease, dependency, and postcondition state; A relay-to-browser reconnect/resume protocol that survives the current four pending commands; Accessibility and Screen Recording permission for the exact AI Pendant Agent identity; A browser heartbeat that reports tab/session identity and acknowledges or rejects each queued command; A typed completion verifier that re-observes the target surface before marking a step complete

### "“Before you act on my behalf, give me a one-sentence reality check when the devices disagree—for example, if the Mac and my remembered timezone differ, a browser session is stale, or a permission is missing—and use the freshest evidence rather than silently guessing.”"
- **useful because:** The system currently has contradictory timezone evidence and can report a healthy bridge while GUI automation is unusable. A compact preflight would prevent wrong-time reminders, false claims about browser work, and actions based on stale tabs or permissions. This is more than ordinary status: it reconciles observations from the pendant, relay, Mac, and browser at the exact moment an action is considered, then blocks or downgrades confidence when they cannot agree.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use deterministic local/relay rules for freshness, identity, permission, and contradiction detection; use the inexpensive background model only to phrase the explanation. Reserve realtime for speaking the final one sentence.
- **latency:** Under 300 ms for deterministic preflight on a connected task; under 1 second for the spoken warning. Do not delay harmless reads, but require explicit confirmation for actions whose inputs are contradictory or stale.
- **cost:** Near-zero API cost for rule evaluation; roughly $0.001–$0.01 only when model phrasing or conflict summarization is needed. Storage is limited to compact evidence references and resolutions, not raw content.
- **security:** Evidence must be scoped to the proposed task: do not expose private tab titles or secret values merely to explain a conflict. Bind observations to device identity, session/tab ID, timestamp, and TTL. A stale or conflicting observation must fail closed for send, delete, purchase, or time-sensitive actions.
- **missing:** A typed observation envelope shared by pendant, relay, Mac, and browser with timestamp, source identity, freshness TTL, and confidence; A deterministic contradiction/preflight evaluator with action-specific blocking rules; A relay endpoint that returns the compact evidence references used in the decision and records the owner’s resolution; Browser and Mac heartbeats that distinguish reachable, authenticated, permission-ready, and merely last-seen states; A concise spoken/UI vocabulary for uncertainty that does not imply completion


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's split nRF9160-plus-ESP32 audio chain with a product audio front end: a low-power audio codec/DSP with native 24 kHz voice support, larger protected double-buffered I2S DMA, and a modem/MCU with enough headroom for concurrent Opus encode/decode. Keep the ESP32/A2DP bridge only as an optional compatibility accessory. Define an end-to-end quality contract (24 kHz payload, bounded jitter, packet-loss concealment, and measured interruption latency) and expose its counters to the relay.
- **owner gets:** The current wearable loses about 7.8 seconds of uplink speech during simultaneous talk, spends roughly 87% of one core on encode plus decode, and forces a 31.25 kHz-to-44.1 kHz SBC detour before headphones. The owner would get a conversation that does not drop their words when the agent speaks, cleaner audio, and predictable behavior instead of a prototype that silently degrades.
- effort: High: select codec/DSP and modem/MCU, redesign PCB and power, port Zephyr audio and secure update paths, rework bridge firmware, then run RF/audio regression and production enclosure tests. The existing firmware telemetry and relay pipeline can be reused as the acceptance harness.  ·  risk: New silicon, RF layout, power profile, and codec drivers can introduce bring-up or certification failures. Recover with a development-board phase, retain the current ESP32 bridge as a fallback, gate rollout behind negotiated device capabilities, and allow firmware rollback. Do not claim 24 kHz acceptance until measured end to end.
- cost: Rough prototype BOM increase of $15–$40 per unit (codec/DSP, PMIC, PCB, microphone/speaker path); likely 20–80 mW additional active draw depending on DSP choice. API cost is negligible; relay telemetry adds small storage/egress.  ·  latency: Could reduce encode/decode contention and resampling delay by roughly 20–60 ms while making jitter bounded; LTE-M half-duplex remains a network limit and still needs adaptive speaking turns.
- security: Adds firmware and possibly DSP attack surface. Require signed MCU/DSP images, encrypted telemetry identifiers, no raw audio in diagnostic counters, and secure erase of any local failure buffer.
- depends on: A measured 24 kHz end-to-end acceptance test and fault-injection harness; A negotiated audio capability/version handshake between pendant, relay, and bridge; A link-aware duplex governor for LTE-M contention; Production pendant constraints and power budget


## What it asked for

_Nothing._
