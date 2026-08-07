# Harness derivation — mac-planner — round 28

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner runtime** — Local agent is healthy at version 0.5.0 and /plan returns background-tier LLM plans with fullControl true. The newly granted mac_readonly_inspect tool currently has no implementation, so it cannot report running apps or foreground state.
  - evidence: GET /health returned ok=true, service AI Pendant Mac Local Agent, version 0.5.0; POST /plan returned status=instant, planner=llm, tier=background, fullControl=true; both mac_readonly_inspect calls returned 'has a schema but has no implementation yet'.

## Capabilities it proposed

### "“When you finish something on my Mac, tell me on the pendant what happened—even if I’ve left the desk.”"
- **useful because:** Today a Mac action can complete out of earshot with its result stranded on the screen. This creates a true Mac→relay→pendant completion channel: the Mac emits a short, structured receipt; the relay deduplicates and queues it; the pendant speaks it when connected, or stores a compact receipt for the next session. It is not another task runner—the value is reliable awareness across physical surfaces.
- **path:** Mac planner: execute the approved plan and emit a receipt containing job ID, outcome, changed paths/apps, and any unresolved error → Relay: persist a deduplicated receipt, apply quiet hours and priority rules, synthesize a short 24-kHz audio notification, and expose delivery state → Pendant: receive/play the notification during an active session and retain a small offline receipt index on microSD for next-connection replay → Dashboard: show receipt provenance and whether it was delivered, replayed, or expired
- **model tier:** Background model for receipt compression and prioritization; realtime only to speak it during an active pendant session. No expensive reasoning model is needed for routine success receipts.
- **latency:** Under 2 seconds from Mac completion to relay acknowledgement; under 500 ms to enqueue a short audio notification. Delivery waits for the next LTE-M session if the owner is away.
- **cost:** About $0.001–$0.01 per completion, dominated by audio synthesis/storage; near-zero for text-only receipts. Batch low-priority receipts to avoid repeated synthesis.
- **security:** Receipts may reveal filenames, app names, or private data. Default to a redacted one-sentence summary, retain source job IDs and details only on the Mac/dashboard, encrypt queued audio and expire it quickly. Never announce secrets or destructive-operation contents aloud.
- **missing:** A signed Mac→relay receipt endpoint with idempotency keys and delivery acknowledgements; A relay receipt queue with quiet hours, priority/coalescing, and short audio generation; A pendant offline receipt index/replay device skill using the microSD, bounded against the 211,608-byte RAM limit; Audio protocol negotiation so notifications can use the planned 24-kHz path while old devices fall back to the current path

### "“When the pendant hits a hardware or audio fault, file a useful bug report for me automatically.”"
- **useful because:** The owner already wants a pendant that files its own UART-log bug reports, but today a fault can disappear into serial output and require manual reproduction. This would turn failures encountered while worn into actionable reports: the pendant captures a bounded diagnostic window and device state, the relay correlates it with the conversation/session, and the Mac turns it into a reviewable issue draft in the owner’s workspace without silently publishing anything.
- **path:** Pendant: detect watchdog resets, Opus overruns, modem detach loops, I2S clock faults, and repeated button/audio errors; persist a bounded compressed event log and incident ID on microSD → Relay: receive incident bundles when LTE-M is available, redact secrets, deduplicate repeated incidents, and correlate timestamps with transport/session telemetry → Mac planner: retrieve the incident, inspect relevant local firmware/build metadata, generate a concise Markdown bug report under ~/AI-Pendant-Workspace, and optionally open it in VS Code → Pendant: announce only a short non-sensitive notice such as “I saved an audio fault report” and retain delivery status for later sync
- **model tier:** Background model for clustering logs and drafting the report; realtime only for a brief spoken notice. Deterministic firmware rules should detect incidents and never depend on an LLM.
- **latency:** Detection and local persistence under 1 second; upload opportunistic rather than blocking conversation; Mac report within 30 seconds after the next successful sync.
- **cost:** Usually under $0.01 per incident, dominated by one small background summarization call; deterministic duplicate suppression and text-only reports can be effectively free.
- **security:** UART logs may contain identifiers, URLs, transcripts, or tokens. Redact credentials and raw speech by default, encrypt the SD incident store, use per-device authenticated upload, retain only a short window, and create a local draft rather than filing externally. External issue submission must remain an explicit separate command.
- **missing:** A firmware incident ring buffer and fault taxonomy with bounded SD storage; Authenticated incident-upload and acknowledgement endpoints in the relay; A Mac read-only incident retrieval route plus build/firmware provenance lookup; A report writer that creates reviewable Markdown drafts in the owner’s workspace; A device skill for offline incident indexing and retry after LTE-M reconnection


## Changes it proposed to its own stack

### `hardware` — Replace the prototype audio chain with a native 24-kHz capture/playback design: a wearable-grade MCU with DSP headroom (nRF5340-class or equivalent), a digital I2S microphone clocked for 24 kHz, external low-power audio codec/DAC, and a bridge that accepts 24-kHz mono rather than forcing 31.25→44.1 kHz SBC resampling. Keep Opus 24-kHz packets end-to-end (or LC3 over a modern Bluetooth Audio bridge), with the nRF9160 retained only as the LTE-M modem during the transition.
- **owner gets:** The pendant would sound genuinely wideband in both directions instead of high-quality playback paired with a 15.625-kHz/16-kHz uplink, making spoken conversations and queued briefs clearer and less fatiguing. It also removes the current near-saturation point where encode and decode consume roughly 87% of one nRF9160 core.
- effort: Prototype a 24-kHz I2S mic/codec on the existing DK first, then spin a wearable board and port the modem/audio split; validate packet loss, clock drift, and headphone interoperability.  ·  risk: A new board and codec introduce RF, clocking, and battery bugs; LC3/Bluetooth Audio support may reduce compatibility with the current SBC-only ESP32 bridge. Recover by retaining the current Opus/SBC bridge as a compatibility mode and A/B testing before hardware replacement.
- cost: Roughly $15–$40 in prototype audio/MCU/PMIC parts per board, plus PCB and enclosure NRE; modest firmware/API cost. Higher peak current than the current idle path, but lower CPU duty cycle should reduce audio processing energy.  ·  latency: Potentially lower decode/transcode latency by eliminating resampling; LTE-M half-duplex remains the dominant conversational delay.
- security: No new cloud data class; raw audio still traverses LTE-M. A codec/MCU split requires authenticated firmware images and encrypted local queue storage.
- depends on: An audio protocol version negotiation between pendant, relay, Mac audio generation, and bridge; A measured 24-kHz Opus encode profile that fits LTE-M uplink budget; A compatibility fallback for the existing 16-kHz uplink and SBC-only ESP32 bridge


## What it asked for

_Nothing._
## Its own summary

Round 28 produced two new deliverables. First, I proposed a hardware-level native-24-kHz audio redesign grounded in the actual limits: current 15.625-kHz capture, 24-kHz playback, 87% nRF9160 core load, 31.25→44.1-kHz SBC bridge, and tight ESP32 buffers. It preserves a compatibility fallback while moving toward the owner’s requested end-to-end superwideband path. Second, I proposed a cross-node capability where every completed Mac job emits a redacted, deduplicated receipt through the relay to the pendant, with offline replay and delivery state. The live Mac agent is healthy (/health 0.5.0); /plan works and uses the background tier. The newly granted read-only inspection tool is not implemented despite its schema, so I could not inspect foreground apps or running apps.

**Biggest unknown:** The actual relay/firmware state of the 24-kHz path and whether the pendant can currently accept a signed receipt/delivery protocol. Still needed: a measured 24-kHz encode budget, protocol negotiation, signed Mac→relay receipt endpoint, relay queue/ack semantics, pendant SD-backed receipt replay skill, and an implementation behind mac_readonly_inspect.

