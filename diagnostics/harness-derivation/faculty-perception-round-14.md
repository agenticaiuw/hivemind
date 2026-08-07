# Harness derivation — faculty-perception — round 14

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness** — Mac local agent v0.5.0 is live and relay reachable, but not ready: Accessibility trusted=false, Screen Recording granted=false, computer-use loop disabled; browser extension home-chrome offline with 2 pending commands.
  - evidence: GET /ops/status at 2026-08-07T09:34Z returned these exact fields.
- **24 kHz audio path** — The observed end-to-end response path is producing 24,000 Hz mono PCM: 164,650 bytes for 3,430 ms, then relay accepts it for nRF9160 playback; pendant audio spec says Opus decode 24 kHz/60 ms frames resampled to 31,250 Hz I2S wire clock. Capture remains 15,625 Hz and uplink Opus 16 kHz/16 kbps.
  - evidence: GET /pipeline latest runs plus describe(audio) show TTS 24 kHz PCM and device decode/resampling facts.
- **Pendant pipeline state** — Pipeline telemetry is active and includes offline-store events: held alerts surfaced from microSD and moment bookmarks held while link down. A cloud response can arrive late and be forwarded after connection recovery.
  - evidence: GET /pipeline returned nrf9160 alert_delivered/bookmark events and cloud-relay late response event.

## Capabilities it proposed

### "“Did you actually hear my last question, and did I hear your answer?”"
- **useful because:** The owner currently has to infer success from silence. A cross-device evidence answer would distinguish microphone capture, LTE upload, relay transcription, Mac planning, 24 kHz rendering, relay delivery, pendant playback, and interruption—then say exactly where the chain stopped, with timestamps and confidence.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use a cheap background/status model to summarize structured telemetry; reserve realtime only for the owner's live follow-up. No LLM is needed for raw event correlation.
- **latency:** Under 1 second for recent jobs from indexed telemetry; under 5 seconds if reconstructing a historical run and generating a spoken explanation.
- **cost:** Near-zero model cost for correlation; roughly $0.001–$0.01 only when a natural-language summary is generated. Storage/indexing and telemetry bandwidth dominate.
- **security:** Expose only the owner's paired pipeline IDs and redacted event metadata, never raw audio by default. Require confirmation before revealing or exporting recordings. Handle offline events as pending rather than falsely successful.
- **missing:** Pendant playback lifecycle telemetry (start, first audio, completion, underrun, abort, reason) with sequence IDs; A shared pipeline state machine and correlation IDs spanning capture, upload, transcription, plan, TTS, delivery, decode, and playback; Relay/mac endpoint that returns a compact signed evidence receipt for one conversation; Dashboard and spoken rendering for confidence/unknown states

### "“Show me what I was doing around the moment I pressed the pendant, even if I was offline.”"
- **useful because:** Today an offline pendant bookmark is only a held event; it does not become a useful, privacy-bounded account of the surrounding moment. The owner should be able to recover a time-aligned episode—what the pendant heard, which Mac app or browser tab was active, network state, and what later synced—while clearly separating observed facts from inference.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event joining and a cheap background model for the concise narrative; use realtime only if the owner asks for it conversationally while wearing the pendant.
- **latency:** If the episode is already synced, under 3 seconds; after reconnection and upload, under 30 seconds to assemble all available evidence.
- **cost:** Very low model cost, roughly $0.001–$0.02 per episode summary. The meaningful cost is bounded event/audio metadata storage and one short LTE sync, not inference.
- **security:** The pendant must record only when explicitly bookmarked or conversation-triggered, with a visible/physical indication and a short retention limit. Browser URLs and app names are sensitive: encrypt them to the paired relay, redact page contents by default, and require confirmation before including raw audio or private page text. Narratives must label unknowns and never imply location or activity that was not observed.
- **missing:** A pendant bookmark envelope containing monotonic time, link state, local sequence numbers, and optional short audio window; Mac-side periodic active-app/window metadata snapshots and browser tab metadata with consent and TTL; Relay reconciliation that deduplicates offline envelopes and aligns pendant, Mac, browser, and network clocks; A provenance-first episode viewer that shows raw observations, gaps, and inferred links separately


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio conformance probe that runs a short synthetic 24 kHz calibration frame through Mac TTS → relay → pendant decode/I2S → bridge capture, carrying a correlation ID and a checksum/sequence marker. Compare expected versus observed sample rate, frame duration, dropped/duplicated frames, clipping, and playback completion; publish a machine-readable pass/fail receipt and automatically quarantine responses when the path is not trustworthy.
- **owner gets:** The owner gets a dependable pendant rather than a path that merely claims 24 kHz. A broken resampler, half-duplex collision, or truncated response is detected before it causes confusing conversations, and the spoken status can say “audio path healthy” or “answer held for retry.”
- effort: Medium-high: firmware test mode and playback markers, bridge loopback/capture, relay correlation and receipt schema, plus a scheduled or on-demand dashboard job.  ·  risk: Calibration audio must never leak into the owner's recordings or be mistaken for speech. Run only when idle, bound by a timeout, and fall back to normal playback if the probe fails. If bridge capture is unavailable, report partial verification instead of pass.
- cost: Negligible API cost; a few seconds of LTE and roughly one small temporary audio object per probe, deleted immediately. Engineering/storage work is the main cost.  ·  latency: No impact on ordinary conversations; an on-demand probe takes roughly 5–15 seconds and may briefly occupy the half-duplex link.
- security: Synthetic signal only, no owner content. Receipts should contain hashes and metrics, not audio, and use paired-device authentication.
- depends on: Playback-lifecycle telemetry on the pendant; Stable 24 kHz PCM/Opus framing and shared sequence IDs; A bridge-side audio loopback or electrical test point

### `hardware` — Add a low-power RTC crystal and a tiny monotonic-event journal (FRAM or a reserved wear-leveled microSD journal) to the pendant, with a tamper-evident boot/session counter. On every bookmark, capture start/end sequence, local monotonic time, link state, and clock-sync provenance; reconcile wall time only when LTE or the Mac bridge supplies an anchor.
- **owner gets:** Offline moments would remain correctly ordered across reboots, dead zones, and delayed delivery. The owner could trust that “what happened around then” is genuinely adjacent in time instead of a cloud timestamp guessed after reconnection.
- effort: Medium hardware revision plus firmware timestamping, clock-anchor protocol, crash-safe journal, and factory/field validation across battery removal and modem reconnects.  ·  risk: A failed RTC or exhausted backup reserve could create a clock gap; never fabricate wall time—surface monotonic order and uncertainty. Journal wear and corrupted records require checksums, bounded retention, and recovery to the last valid entry.
- cost: Approximately $1–$3 added BOM for crystal, backup/hold-up parts, and small FRAM if used; negligible average power for the RTC, with microamp-scale standby target. No per-call API cost.  ·  latency: No conversational latency; a few milliseconds per bookmark and a small reconnect synchronization exchange.
- security: The journal contains timing/link metadata, not content. Encrypt or authenticate records and erase them with the owner's retention controls; the boot/session counter helps detect rollback or replay.
- depends on: An offline bookmark envelope and reconciliation protocol; A paired Mac/relay clock-anchor endpoint; A user-visible retention and export/delete policy


## What it asked for

_Nothing._
## Its own summary

Established live facts: Mac agent v0.5.0 and relay are reachable, but Mac automation is not ready (Accessibility and Screen Recording missing; computer-use disabled) and the browser extension is offline with two queued commands. The observed response path renders 24 kHz mono PCM and the pendant specification decodes 24 kHz before 31.25 kHz I2S output; telemetry also proves offline bookmarks/alerts are held and later delivery can be delayed. Recorded all three findings, informed judgement/action/realtime peers, and proposed two new cross-node capabilities: an evidence-backed answer to “did you hear me/hear your answer?” and a synthetic end-to-end 24 kHz conformance probe.

**Biggest unknown:** Whether the pendant actually starts, completes, underruns, or aborts playback for a delivered response. I still need playback lifecycle telemetry and a shared correlation/state receipt; without those, delivery is established but audibility is not.

