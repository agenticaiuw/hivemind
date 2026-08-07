# Harness derivation — relay-realtime — round 71

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use high-fidelity mode for this conversation.” The pendant should preserve a 24 kHz voice path end-to-end when the owner needs accurate dictation or audio understanding, while automatically falling back to the normal low-latency mode when the link or device cannot sustain it."
- **useful because:** Today the owner cannot know or control whether speech is being downsampled or silently degraded between the worn microphone, LTE relay, model, and playback. A negotiated, observable 24 kHz mode would improve dictation of names, music/code terms, and noisy environments without making every conversation expensive or high-latency.
- **path:** pendant → relay → mac-planner → unified
- **model tier:** Realtime for the live voice turn and codec negotiation; use a cheaper background model only if the owner asks for post-call transcription or audio cleanup.
- **latency:** Mode selection and capability handshake under 150 ms; preserve the current conversational latency in normal mode. High-fidelity mode may add at most 100 ms buffering, with immediate downgrade on loss or congestion.
- **cost:** Small per-turn increase from 24 kHz audio bandwidth and realtime input tokens/compute; dominant cost is the longer audio stream, so default remains normal mode and high-fidelity is explicit or triggered by confidence/noise heuristics.
- **security:** Raw microphone audio still leaves the pendant over LTE and is processed by the relay/model; expose a spoken indication when high-fidelity capture is active, never retain raw audio by default, and attach mode/codec/sample-rate metadata to the transcript and receipt.
- **missing:** A pendant-to-relay audio capability handshake reporting actual capture/playback sample rate and codec; A relay media path that preserves 24 kHz instead of silently resampling at an intermediate hop; Realtime session negotiation and downgrade/recovery state machine; An owner-visible spoken/status signal and per-turn audio metadata in history


## Changes it proposed to its own stack

### `integration` — Build an end-to-end audio rate/codec contract and a relay transcoding path so the system can reliably support 24 kHz playback and higher-quality voice features without mismatched assumptions. Define: capture rate, network payload rate, relay internal processing rate, and device playback rate, plus required resamplers and buffer sizes. Implement relay-side transcoding and buffering that can convert from the pendant’s current uplink (Opus at 16 kHz) to a 24 kHz stream for downstream TTS/playback, and from 24 kHz TTS output back to the device’s expected decode/resample path. Add explicit capability negotiation during session setup (what rates the pendant supports now vs. can accept) and a fallback to current 16 kHz behavior.
- **owner gets:** Cleaner, more consistent voice and fewer audio glitches. The owner can get higher-quality spoken replies when available, while still working today with the current prototype hardware.
- effort: Medium to high. Needs protocol changes, relay buffering/transcoding work, and test fixtures for packet loss, jitter, and rate mismatch.  ·  risk: Audio drift, stutter, or increased latency if buffering is wrong. Mitigate with explicit buffer targets, backpressure, and a conservative fallback to existing 16 kHz mode.
- cost: Moderate. More CPU at the relay for transcoding/resampling; potentially higher bandwidth if 24 kHz is used end-to-end.  ·  latency: Small but real. Transcoding and resampling add processing time; keep under a tight budget and prefer streaming chunked responses.
- security: Low. Audio is already transmitted; ensure logs do not retain raw audio longer than necessary and keep capability negotiation authenticated.
- depends on: A defined session capability negotiation schema between pendant, relay, and downstream TTS/LLM; explicit audio buffer sizing and jitter handling in the relay.


## What it asked for

_Nothing._
