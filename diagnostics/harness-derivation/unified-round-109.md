# Harness derivation — unified — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path-status** — The live pipeline already renders 24 kHz mono PCM (example 74.0 KiB, 1,578 ms, zero clipped samples) and relay accepts it, but the pendant capture path is 15,625 Hz and prototype decode reports 25.4 ms per 60 ms packet; there is no end-to-end quality verdict or synchronized stage telemetry.
  - evidence: GET /pipeline at 2026-08-07T14:37Z: TTS event metadata format=s16le, sampleRate=24000, clippedSamples=0; GET hardware audio: mic capture=15,625 Hz, uplink Opus=16 kHz, playback decode=24 kHz/60 ms, prototype.

## Capabilities it proposed

### "“Test my pendant audio end to end and tell me whether a real conversation will sound good; if it fails, show me exactly where and keep the failed sample for repair.”"
- **useful because:** The current prototype can claim decode/encode success while the owner hears dropouts, latency, clipping, or silence. This gives the owner a one-command, evidence-backed health check spanning the worn pendant, ESP32 audio bridge, relay transcoder, and Mac playback, with a repair artifact rather than guesswork. It also turns the owner's explicit 24 kHz audio goal into a repeatable acceptance test.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use deterministic signal generation, packet/clock measurements, and threshold checks first; use the cheaper background model only to summarize a failed run. Reserve realtime for the owner's spoken request and the final short explanation.
- **latency:** 20–30 seconds for a full loopback and report; under 2 seconds for an initial pendant/relay connectivity verdict. No model call is needed for measurement.
- **cost:** Near-zero model cost on passing runs; roughly $0.01–$0.05 for a background explanation of a failed run. Dominant cost is temporary audio upload/storage and relay CPU, not inference.
- **security:** Use synthetic speech/noise by default, never retain microphone content beyond the run, and encrypt any optional owner voice sample. Require confirmation before recording a real conversation or uploading a sample. Dashboard receipts must expose retention and hashes, not raw audio by default.
- **missing:** A firmware/bridge loopback and timestamped packet telemetry protocol; An audio validation tool that can inject loss, jitter, clock drift, clipping, and silence and compare decoded output to the reference; Authoritative 24 kHz end-to-end acceptance thresholds (MOS proxy, one-way latency, jitter, loss, CPU, and battery); A short-lived encrypted audio artifact store plus dashboard report with automatic deletion

### "“When I’m talking with someone who speaks another language, translate both sides through the pendant in near real time, preserve names and numbers from my calendar or browser context, and let me say ‘original’ to hear the last sentence unchanged.”"
- **useful because:** This would give the owner a genuinely hands-free interpreter that can follow a real conversation rather than translating isolated recordings. The pendant supplies immediate private audio in and out, the relay supplies low-latency turn handling, the Mac/browser supply optional names, reservations, addresses, and terminology that generic translation gets wrong, and the system can degrade safely when connectivity or confidence drops.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime translation for the active conversation only; use a cheaper background model to build a terminology pack from explicitly selected calendar/browser context before the conversation. Do not send unrelated account content.
- **latency:** First translated phrase within about 1.5 seconds after a speaker turn, with incremental partial audio where safe. Context-pack preparation can take seconds in the background.
- **cost:** Realtime translation dominates, roughly $0.02–$0.10 per conversational minute depending on languages and audio duration; context extraction should use the cheaper background tier and be negligible by comparison.
- **security:** A bystander’s speech is sensitive. Default to an on-device audible/LED consent cue, no retention of raw audio, explicit language selection, and a physical stop gesture. Only send the minimum selected names/terms from private Mac or browser pages, with a visible dashboard receipt and automatic expiry.
- **missing:** A bilingual realtime session protocol with turn boundaries, interruption handling, and replay of the last original utterance; Language identification and confidence signaling that can refuse to invent a translation; A user-approved, narrowly scoped terminology context packet sourced from Calendar/Mail/browser tabs; Pendant UX for language selection, stop, repeat-original, and low-confidence alerts; A low-latency duplex audio path meeting conversational latency and power targets


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio acceptance runner that coordinates the pendant firmware, ESP32 bridge, relay, and Mac harness. It should inject a deterministic 24 kHz multitone plus speech-shaped reference, stamp every frame at capture/encode/transmit/decode/playback, collect packet loss/jitter/clock drift/PLC counts/CPU and battery, and emit a signed receipt containing pass/fail per threshold. On failure, retain only a short encrypted diagnostic waveform and automatically delete it after 24 hours; expose a dashboard diff against the previous run.
- **owner gets:** The owner can know, before relying on the pendant, whether it will actually carry a conversation and whether a regression came from the wearable, bridge, network, relay, or Mac. A failed run becomes actionable evidence instead of another “audio path works” claim.
- effort: Medium-high: firmware telemetry and test mode, bridge packet forwarding, relay correlation and storage TTL, Mac playback capture, and a dashboard receipt. Build deterministic tests before adding any model summarization.  ·  risk: Test mode could accidentally stream microphone audio or leave diagnostics behind; gate it with a local button gesture and explicit server test token, use synthetic signals by default, cap duration, and enforce deletion. If one component drops stamps, report “inconclusive” rather than pass.
- cost: No recurring inference cost for measurements; modest relay CPU and temporary object storage. Failed-run summaries can use a cheap background model, estimated under $0.05 each.  ·  latency: Adds 20–30 seconds when explicitly run; no impact on normal conversation. Initial connectivity result can arrive in under 2 seconds.
- security: Synthetic signal by default, encrypted short-lived artifacts, signed receipts, and no raw microphone retention. A real-voice test requires confirmation.
- depends on: 24 kHz superwideband audio-path target architecture and acceptance thresholds; audio_link_fault_inject or equivalent deterministic impairment injection; audio_path_preflight_receipt; production pendant constraints beyond the current nRF9160 DK

### `hardware` — For the production pendant, replace the prototype nRF9160-DK audio arrangement with a codec/DSP path that natively captures and plays 24 kHz mono (or add a low-power audio DSP with DMA and hardware buffering), leaving the cellular MCU to handle transport and control. Keep the existing 60 ms Opus framing only if measured latency and power pass acceptance; otherwise make frame size configurable.
- **owner gets:** The owner gets clearer, more natural speech and fewer dropouts without spending most of the pendant CPU on simultaneous encode/decode. It makes the promised 24 kHz conversation a product property rather than a relay-side sample-rate conversion.
- effort: High: select production codec/DSP and microphone, redesign board/audio clocking, port Zephyr drivers and Opus buffers, then validate RF coexistence, thermal behavior, battery life, and enclosure acoustics.  ·  risk: A new clock domain or codec can introduce drift, wakeups, or RF noise; retain a bypass path to the current I2S chain, gate rollout behind hardware revision, and compare recordings in the acceptance runner before switching defaults.
- cost: Roughly $3–$12 BOM increase depending on codec/DSP and microphone; likely tens of milliwatts additional audio power, potentially offset by lower MCU duty cycle. No meaningful API cost.  ·  latency: Potentially lowers encode/decode CPU delay and buffering; configurable 20–60 ms frames may reduce conversational latency, but cellular RTT remains dominant.
- security: No new data leaves the device; DSP remains local. Firmware must verify signed codec/DSP configuration and avoid diagnostic recording by default.
- depends on: End-to-end audio acceptance runner; Authoritative 24 kHz acceptance thresholds; Production pendant constraints beyond the current nRF9160 DK; Audio-path power and thermal measurements

### `model-routing` — Add a dedicated bilingual-session router rather than sending translation through the ordinary planner. It should maintain a bounded rolling audio window, detect speaker turns, stream source and translated text/audio as separate sequence-numbered lanes, attach confidence and language metadata to every segment, and support an immediate “original” replay from the local ring buffer. Before a session, compile only owner-approved names and terms from selected Calendar/Mail/browser records into an expiring terminology pack; never place those records in the general realtime prompt.
- **owner gets:** The owner gets fast, intelligible translation that can be interrupted, corrected, or replayed without losing the conversation. Names, addresses, and booking details are translated consistently, while unrelated private information stays out of the session.
- effort: High: new realtime session state machine, duplex audio framing, turn detection, terminology-pack compiler, confidence UI/LED cues, and language-pair evaluation with noisy real-world speech.  ·  risk: Overlapping speakers, accents, poor connectivity, or low confidence could produce dangerous mistranslations. Mark uncertain segments audibly, fall back to original audio, never silently paraphrase numbers or proper nouns, and require the owner to confirm before using a translated value in an external action.
- cost: Realtime translation adds per-minute inference and audio egress cost, estimated $0.02–$0.10/minute; terminology compilation is a small background-model cost. Bounded buffers and expiring packs limit storage.  ·  latency: Adds roughly 0.5–1.5 seconds per turn beyond network round trip; local original replay is immediate. It requires duplex scheduling so translated output cannot starve incoming audio.
- security: Raw conversation should remain transient and encrypted; terminology packs need field-level allowlisting, provenance, expiry, and deletion receipts. A physical stop gesture must cut microphone upload immediately.
- depends on: A production duplex audio transport with reliable timestamps and interruption support; Language-pair quality and confidence thresholds; A narrowly scoped private-context extraction/consent mechanism; Pendant controls for language selection, stop, and original replay


## What it asked for

_Nothing._
