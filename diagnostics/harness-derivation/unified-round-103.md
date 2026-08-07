# Harness derivation — unified — round 103

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path** — The live Mac pipeline is already rendering 24 kHz mono s16le PCM and handing it to relay successfully: a recent run produced 75,734 PCM bytes, 1,578 ms duration, zero clipped samples, and relay_result=done. The remaining unverified boundary is relay-to-pendant playback and reconnect/duplicate behavior; the current prototype captures 15,625 Hz and decodes 24 kHz through a 31,250 Hz I2S wire clock.
  - evidence: GET /pipeline and GET /ops/status on 2026-08-07; GET /pipeline showed tts metadata and relay_result done; recalled audio hardware specification.

## Capabilities it proposed

### "“Talk to me through the pendant for a full conversation even when LTE is unreliable; keep the reply natural, never repeat audio, and tell me if anything was lost.”"
- **useful because:** The current pipeline already renders 24 kHz PCM and stores durable responses, but it does not yet present a user-visible, end-to-end conversation contract across the worn device, relay, and Mac. A sequence-numbered jitter buffer with resumable chunks lets the pendant play smoothly, resume after a drop, and give a concise delivery receipt instead of silently losing or duplicating speech.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** gpt-realtime-2.1 only for the live turn; deterministic relay/firmware buffering and receipt logic for transport; no model for recovery or status
- **latency:** Begin playback within 250 ms after the first complete audio frame; tolerate 5 s LTE gaps; recovery status under 1 s after reconnect. The expensive model is invoked once per turn, not per chunk.
- **cost:** Negligible incremental API cost beyond the live turn; relay storage/egress and a small amount of D1 metadata dominate, with generated PCM retained only for the configured short window.
- **security:** Audio and transcript remain bearer/pairing protected. Chunk IDs must be opaque and scoped to a session; expired PCM must be deleted. Never expose raw audio in a dashboard by default. Ask confirmation only for changing retention or exporting a recording.
- **missing:** A firmware sequence-numbered PCM jitter buffer and duplicate suppression; Relay resumable audio-chunk protocol with per-session acknowledgements; Mac pipeline emission of chunk metadata and a final delivery receipt; An explicit owner-facing interrupted/complete indicator on the pendant

### "“Learn how I pronounce the people, places, products, and technical terms in my life, and use those pronunciations consistently when speaking through the pendant or Mac.”"
- **useful because:** Generic speech synthesis repeatedly mispronounces names and specialist vocabulary, making a wearable assistant feel unreliable. The owner should be able to correct a pronunciation once by voice and have that correction follow the same person or term across relay replies, Mac-generated briefings, browser summaries, and scheduled audio.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use the realtime model only to interpret an explicit correction; use deterministic lookup and macOS speech pronunciation overrides for subsequent turns. No model call is needed to apply a known pronunciation.
- **latency:** A known term must add less than 20 ms to speech preparation. Learning a correction can complete within one conversational turn.
- **cost:** Near-zero recurring model cost after a correction; storage is a small private dictionary. Occasional correction interpretation uses one short realtime turn.
- **security:** Pronunciation entries may reveal contacts or private projects, so store them as sensitive personal memory with provenance and deletion controls. Do not upload the full dictionary on every turn; send only entries relevant to the current text. Require explicit confirmation before sharing the dictionary or applying it to exported audio.
- **missing:** A shared pronunciation-lexicon schema with scoped entries, confidence, language, and provenance; A relay-to-Mac speech rendering hook that applies the selected pronunciation without rewriting visible text; A voice command and dashboard control to correct, test, list, or delete an entry


## Changes it proposed to its own stack

### `integration` — Build an end-to-end 24 kHz audio conformance runner that injects a marked PCM test utterance at the Mac pipeline, follows it through relay upload/download to the pendant, and emits a signed receipt containing sequence continuity, first-play latency, underruns, duplicates, dropped chunks, sample-rate/format, peak/RMS/clipping, and reconnect recovery. Run it in CI and as a preflight before enabling a new firmware or relay audio build; fail closed on format mismatch or missing final receipt.
- **owner gets:** The owner gets a trustworthy answer to “can I rely on the pendant right now?” instead of hearing a response that was rendered successfully but never arrived or played correctly. Regressions in the 24 kHz path are caught before they ruin a real conversation.
- effort: Medium: a deterministic PCM fixture, relay test mode, Mac pipeline instrumentation, a small firmware test endpoint, and dashboard/CI receipt rendering.  ·  risk: A test-mode route could accidentally expose or retain audio; isolate it behind pairing and a nonce, use synthetic audio only, and expire artifacts immediately. False failures from transient LTE should distinguish transport failure from codec failure and permit a controlled retry.
- cost: No per-turn model cost; modest CI bandwidth and short-lived relay storage. Engineering work is the main cost.  ·  latency: No production-path latency; preflight adds roughly 10–30 seconds when run manually, depending on LTE and reconnect testing.
- security: Synthetic payloads only, authenticated test nonce, no owner transcript. Receipts should contain hashes and metrics rather than raw PCM.
- depends on: A relay audio chunk/ack contract with explicit final delivery state; Pendant-side playback counters and a durable last-receipt index; The already-requested audio_pipeline_validate and audio_link_fault_inject tools

### `hardware` — Replace the prototype nRF9160-DK-plus-ESP32 audio arrangement in the product design with an LTE-M/NB-IoT module paired to an audio-capable MCU/codec that provides at least 512 kB application SRAM (preferably 1 MB), DMA-backed I2S at a native 24 kHz or 48 kHz family clock, and a hardware audio FIFO. Keep the nRF9160 path as the bring-up target, but do not size production buffering around its 211,608 B application RAM: five seconds of 24 kHz mono s16 PCM is already 240 kB before Opus, stacks, and modem sharing.
- **owner gets:** The pendant can absorb a several-second LTE gap and play 24 kHz speech without underruns, pitch-changing resampling, or sacrificing conversation state to fit the development board’s memory. It also makes the promised audio quality achievable in a comfortable, smaller wearable rather than a fragile prototype.
- effort: High: select a certified cellular module plus MCU/audio codec, redesign power and PCB, port Zephyr audio and modem interfaces, and requalify RF, acoustics, and battery life.  ·  risk: More silicon and clock domains create integration risk; retain the current DK as a hardware-in-loop reference, gate rollout behind the conformance runner, and fall back to short-buffer streaming if external memory fails. Certification and enclosure acoustics are schedule risks.
- cost: Roughly +$8–25 BOM versus the DK prototype, plus PCB/certification NRE; active audio buffering adds roughly 10–40 mW depending on MCU/codec.  ·  latency: Native clocking and DMA should reduce jitter and resampling delay; larger buffering adds no startup delay if playback begins from a small playout threshold.
- security: More firmware surface and external memory require secure boot, encrypted/fail-closed audio buffers, and explicit zeroization of expired PCM. Cellular credentials remain in the certified module’s secure storage.
- depends on: The end-to-end 24 kHz conformance runner; A measured target for acceptable offline gap duration and battery life; Production pendant constraints beyond the current nRF9160 DK (already requested)

### `model-routing` — Add a compact, provenance-aware pronunciation layer between response text and every speech renderer. Normalize only for synthesis (never mutate the displayed transcript), resolve exact terms and contact/project aliases from a private lexicon, emit SSML/phoneme hints for macOS say and relay fallback TTS, and log the applied lexicon entry plus renderer version in the audio receipt. A spoken “say X like Y” command creates a pending entry; the owner confirms by hearing a test phrase before it becomes active.
- **owner gets:** Names and technical terms will sound right in morning briefs, browser readouts, and live pendant replies instead of needing correction every time. The owner can hear and fix the result without editing text or learning a speech-markup system.
- effort: Medium: schema and retrieval, voice correction intent, macOS say integration, relay fallback support, and a small test-phrase UI.  ·  risk: Bad corrections could make common words sound wrong or leak a private name into unrelated speech. Scope entries by speaker/profile and context, require test confirmation, support immediate deletion, and fall back to ordinary text synthesis when confidence is low.
- cost: Minimal storage and negligible inference cost; only explicit corrections consume a realtime interpretation.  ·  latency: Under 20 ms for lookup and hint generation; no additional model round trip for known entries.
- security: The lexicon is sensitive memory. Encrypt at rest, project only matching entries into a turn, redact names from general logs, and provide a one-command wipe.
- depends on: A shared typed personal-memory projection with sensitivity and TTL; A speech-renderer interface that accepts pronunciation hints; The capability’s owner-confirmed correction interaction


## What it asked for

_Nothing._
