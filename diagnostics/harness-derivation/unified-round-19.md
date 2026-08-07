# Harness derivation — unified — round 19

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-health** — The live Mac local agent is reachable and healthy at GET /health, reporting version 0.5.0; it exposes pipeline audio routes and job receipt routes, but the relay /v1/health path is not present on this backend.
  - evidence: probe_http GET /health returned 200 {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0'}; GET /v1/health returned 404.

## Capabilities it proposed

### "“Keep the conversation understandable when the connection gets bad, and make sure I don't lose what I said or what you said.”"
- **useful because:** The current LTE-M half-duplex path demonstrably drops about 7.8 seconds of uplink during simultaneous speech. This gives the owner graceful degradation instead of silent loss: the pendant reports quality locally, the relay negotiates a smaller/ordered audio mode, the Mac can recover the missing intent from a transcript, and the owner gets a short spoken completion/recovery receipt rather than guessing whether the system heard them.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-4.1-mini for packet-loss classification, transcript reconciliation, and receipt generation; gpt-realtime-2.1 only for the live turn and interruption decisions; gpt-5.6-luna on the Mac only if recovery requires a multi-step browser or filesystem action.
- **latency:** Local packet-loss/jitter detection under 100 ms; relay mode switch within one 60 ms audio frame; no more than 250 ms added to live speech. Recovery receipt within 5 s after link restoration. Background transcript reconciliation can take seconds.
- **cost:** Approximately $0.002–$0.02 per affected call, dominated by any recovery transcription/reasoning; healthy calls add negligible model cost because quality decisions are deterministic telemetry.
- **security:** Audio and packet diagnostics leave the pendant over TLS as they do today; SD is used only as the existing failed-upload buffer and must be encrypted or cryptographically erased after delivery. Never replay recovered private text aloud without the owner's normal conversation authorization; browser actions remain gated by existing destructive-action confirmation. Persist only sequence numbers, loss windows, hashes, and a short-lived transcript pointer by default.
- **missing:** A versioned audio-session protocol with sequence numbers, timestamps, acknowledgements, jitter-buffer targets, and negotiated bitrate/sample-rate modes; Pendant firmware telemetry and a local LED/error pattern for degraded mode, plus bounded SD spool metadata and replay deduplication; Relay-side selective retransmission/FEC policy that respects the ~2 kB TLS record limit and half-duplex LTE-M behavior; A Mac bridge recovery endpoint that can reconcile partial voice turns and produce a completion receipt; End-to-end 24 kHz acceptance tests measuring intelligibility, loss concealment, latency, and CPU/RAM/power on the actual nRF9160 + ESP32 path

### "“When I say ‘this’ while I’m looking at something on my Mac, use the pendant to bind my words to the exact browser tab or screen I mean, then tell me what it is and prepare the next step without making me describe or read it aloud.”"
- **useful because:** Today voice, the Mac screen, and authenticated browser sessions are separate contexts, so deictic requests like “handle this” are ambiguous or fail. This would let the owner keep their eyes and hands on the work: a button press or short spoken marker creates a cryptographically linked handoff from the pendant’s utterance to the active Mac window/tab, while the browser supplies private-page evidence and the relay preserves the task if the Mac briefly disconnects.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-realtime-2.1 only for the short live utterance and marker timing; gpt-4.1-mini for window/tab identity matching, OCR/DOM evidence alignment, and ambiguity scoring; gpt-5.6-luna on Mac for planning a multi-step follow-up. No expensive model is needed for the normal exact-match path.
- **latency:** Marker acknowledgement under 150 ms; active-tab identity and a first evidence snippet within 1 s; ask a spoken clarification within 2 s if confidence is below threshold. Preparing a multi-step action may continue asynchronously.
- **cost:** About $0.001–$0.01 per handoff, dominated by OCR or model-based ambiguity resolution; exact active-tab binding is deterministic and nearly free. Browser extraction and any later action are separate costs.
- **security:** The binding must be scoped to the owner’s authenticated Mac session and expire quickly. Send tab ID, origin, title, and a minimal selected/visible-region hash to the relay—not arbitrary page contents—until the owner asks to inspect it. Never infer consent to submit, send, delete, purchase, or disclose secrets from the marker; preserve the existing confirmation gate. Dashboard and spoken receipts must redact sensitive values.
- **missing:** A Mac accessibility/screen-observation adapter that emits the focused window, active tab, selection, and stable page-region identifiers with owner consent; A pendant-to-Mac marker protocol carrying monotonic time, utterance ID, and a one-button disambiguation event; A relay task-envelope format that joins audio, device event, Mac observation, and browser evidence with expiry and provenance; Browser-bridge support for returning a stable tab/session identity and a minimal DOM or screenshot-region proof; A user-facing ambiguity flow that offers ‘the tab I’m on’, ‘the selected text’, or ‘the window in front’ and lets one button choose among them


## Changes it proposed to its own stack

### `firmware` — Make audio sessions explicitly negotiated and instrumented end to end: retain the existing 15.625 kHz physical mic clock but encode a declared 16 kHz uplink; keep 24 kHz decoded downlink; add per-frame sequence/timestamp/codec-mode headers, bounded jitter buffering, packet-loss concealment, and a deterministic quality ladder (full duplex -> downlink-priority -> uplink-priority) selected from measured loss/queue depth. Add a loopback and live acceptance harness that verifies 24 kHz decoded audio through the 31.25 kHz I2S wire clock and ESP32 44.1 kHz SBC path, while recording CPU, queue depth, drops, and current mode.
- **owner gets:** The owner hears a stable conversation and knows when quality has degraded instead of receiving clipped or silently missing speech. It honestly labels the current asymmetric path as superwideband playback rather than pretending the microphone is 24 kHz, and creates the evidence needed to decide whether a future microphone/SoC replacement is worthwhile.
- effort: Medium-high: protocol changes in pendant_ws/audio_opus, relay transcoding and session negotiation, ESP32 bridge telemetry, and hardware-in-the-loop tests. First deliverable can be telemetry and mode negotiation without changing the physical sample clock; true 24 kHz capture requires a different I2S microphone/clock path and likely a product-board redesign.  ·  risk: Changing framing can desynchronize old firmware; deploy a protocol version handshake and retain the legacy decoder for rollback. More buffering increases conversational latency; cap it at 120 ms and fall back on sustained loss. The nRF9160 has only 211,608 B app RAM and Opus already consumes roughly 87% of a core when encoding and decoding, so avoid duplicate full audio buffers. Test modem reconnect, SD-full, and ESP32 Bluetooth starvation before enabling adaptive modes by default.
- cost: No per-call API increase for deterministic telemetry; modest engineering/test cost. A future true-24-kHz mic revision is roughly $5–$20 in prototype BOM plus board/layout work and may increase power draw. Current firmware change uses tens of kilobytes at most if buffers are bounded.  ·  latency: Adds 20–60 ms jitter buffering in degraded mode; healthy mode target remains under 250 ms added end to end. Recovery and diagnostics are asynchronous.
- security: Sequence numbers and quality telemetry reveal timing but not content; send over the existing TLS WebSocket. SD spool records need authenticated encryption and deletion receipts; do not persist raw audio beyond the existing failed-upload policy.
- depends on: 24 kHz superwideband acceptance criteria; 24 kHz audio target architecture; A versioned audio frame schema shared by pendant, relay, and ESP32 bridge; Hardware-in-the-loop packet-loss and Bluetooth starvation test fixture


## What it asked for

_Nothing._
## Its own summary

Discovered the live system and built beyond the backlog. The pendant is asymmetric today: 15.625 kHz mic / 16 kHz Opus uplink, 24 kHz decoded downlink resampled to 31.25 kHz I2S, while LTE-M contention has already dropped about 7.8 seconds of uplink in one call. I proposed (1) a cross-surface degraded-link recovery capability spanning pendant telemetry, relay negotiation, Mac reconciliation, and dashboard/browser evidence, and (2) a firmware/protocol change with versioned frames, bounded jitter buffering, a quality ladder, and hardware-in-the-loop 24 kHz acceptance tests. I also verified the Mac agent is live at version 0.5.0 and has pipeline-audio and job-receipt routes.

**Biggest unknown:** I still need the orchestrator's authoritative 24 kHz superwideband acceptance criteria and target architecture (already requested, not re-requested), plus an agreed versioned audio-frame/session schema and access to the actual pendant/ESP32 hardware-in-the-loop test run. Without those, I can specify the change but cannot honestly claim the end-to-end path is shipped or accepted.

