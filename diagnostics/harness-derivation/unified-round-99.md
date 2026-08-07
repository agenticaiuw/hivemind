# Harness derivation — unified — round 99

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Show me exactly what the hive knows about this request and what it did with my data, then let me export a redacted, tamper-evident record.”"
- **useful because:** Today the owner can receive action receipts and browser provenance, but cannot obtain one comprehensible, cross-surface data-flow record. This would let them audit a voice request spanning pendant audio, relay transcription, Mac planning, browser reads, generated files, and queued delivery—without exposing unrelated secrets.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic aggregation and redaction by default; use the background model only to turn the verified event graph into a short plain-language explanation. Realtime is needed only when the owner asks verbally and is waiting for the answer.
- **latency:** A spoken summary in under 2 seconds from cached event records; export generation under 10 seconds. No model call if the owner only requests the raw manifest.
- **cost:** Near-zero model cost for aggregation; modest local/relay storage and hashing. Background explanation costs one small completion only when requested.
- **security:** The export itself can contain sensitive URLs, transcripts, account names, and device identifiers. Redaction must happen before rendering; secret-classified memory and raw audio are excluded by default. Require an explicit confirmation for including sensitive fields or writing outside the private workspace. Sign the canonical event manifest so later edits are detectable.
- **missing:** A cross-surface event ledger with stable request and data-object IDs; A typed data-flow relation (captured, transcribed, sent, read, generated, played, deleted); A deterministic redaction/export route; A user-facing spoken audit command and dashboard view; Retention/deletion events emitted by pendant, relay, Mac, and browser


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160-DK audio front end for the product with a low-power application MCU/DSP plus an external 24 kHz-capable audio codec (or a modem/application SoC combination with a dedicated audio DSP). Set capture and playback to a real 24 kHz/16-bit mono contract, with DMA ping-pong buffers and hardware clocking; retain the LTE-M modem as a separate transport. Do not attempt to reach the target by further squeezing the current 64 MHz Cortex-M33.
- **owner gets:** The pendant would capture speech at the same superwideband quality it plays, instead of permanently losing high frequencies at the microphone. It would remain responsive during duplex speech rather than spending roughly 87% of one core on current encode/decode, and it would have enough headroom for adaptation and local privacy controls.
- effort: High: select a production-qualified MCU/codec and power budget, redesign PCB and clocks, port Zephyr audio/DMA and Opus, then run RF/audio coexistence and wearer trials. Prototype firmware can first validate the codec on an evaluation board.  ·  risk: New silicon, drivers, clocking, and RF layout can introduce bring-up delays and battery regressions. Recovery is to retain the current DK build as a transport-compatible test fixture and gate rollout on measured capture rate, packet loss, latency, and battery tests.
- cost: Roughly $8–$25 incremental prototype BOM for codec, MCU/DSP, clocks, and board changes, plus engineering NRE; likely tens of milliwatts additional peak draw, offset by shorter CPU occupancy. API cost unchanged.  ·  latency: Should reduce local audio processing contention and permit lower buffering; target under 60 ms added device-side audio latency, subject to modem scheduling.
- security: Audio remains encoded before transport; a dedicated application MCU must have secure boot, signed firmware, erased failure buffers, and no debug UART in production. More components increase firmware attack surface.
- depends on: 24 kHz superwideband audio-path acceptance criteria; product audio compatibility target; end-to-end audio acceptance thresholds; audio pipeline validation and fault injection; production pendant constraints beyond the current nRF9160 DK

### `memory` — Add an append-only, hash-chained cross-surface data-flow ledger separate from conversational memory. Every request receives a stable ID; pendant, relay, Mac, browser, and storage emit compact events naming only data-class, source surface, destination, operation, retention deadline, and receipt hash. Keep raw transcript/audio out of the ledger. Provide deterministic redaction and canonical JSON export, with verification that detects missing or altered events.
- **owner gets:** They could answer “what did you send where?” with evidence rather than trusting a summary, and prove that an exported history has not been rewritten. This is especially valuable for private logged-in pages and voice recordings that cross several machines.
- effort: Medium-high: define the event schema, add emitters and durable storage, handle offline pendant sequence numbers and relay reconciliation, then build export/verification UI and retention tests.  ·  risk: Dropped or duplicated events could make the history appear incomplete; use device sequence numbers, idempotency keys, and explicit unknown gaps instead of silently claiming completeness. A compromised node could still omit events before signing, so the UI must distinguish cryptographic integrity from completeness.
- cost: Small D1/R2 and microSD footprint per event; no recurring model cost. Export hashing is inexpensive.  ·  latency: Asynchronous writes; at most a few milliseconds on the Mac/relay path. Pendant emission must be a bounded queue operation and never block audio.
- security: Improves accountability but creates metadata about owner activity. Encrypt at rest, minimize fields, apply existing sensitivity labels, and require confirmation for sensitive exports. Device signing keys must be provisioned securely.
- depends on: A stable cross-surface request ID propagated through relay and Mac jobs; A retention/deletion event contract; A deterministic redaction policy; Offline sequence reconciliation for pendant events


## What it asked for

_Nothing._
