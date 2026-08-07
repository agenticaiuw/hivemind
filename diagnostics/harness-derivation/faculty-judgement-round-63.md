# Harness derivation — faculty-judgement — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the pendant’s audio path breaks or changes quality, keep the conversation going without making me repeat myself, and tell me clearly what happened.”"
- **useful because:** The current device captures at 15,625 Hz, uplinks Opus at 16 kHz, and plays back at 24 kHz; the observed pipeline has already shown a 15,625-Hz input beside a 24-kHz output. Today that mismatch can look like a successful turn while the owner hears degraded audio or loses an utterance. This capability makes audio failure recoverable instead of silently conversationally expensive.
- **path:** pendant → relay-realtime → mac-terminal → unified
- **model tier:** Realtime model only for the short session-health decision and the owner's one-sentence alert; a cheaper background model summarizes diagnostics and drafts a bug report after the session. Firmware/relay contract checks are deterministic and do not call a model.
- **latency:** A preflight probe must complete in under 300 ms before speaking. On a mid-session fault, locally preserve the current utterance, announce fallback within 1 s, and resume via text or a re-established audio contract without replaying already acknowledged turns.
- **cost:** Negligible model cost for healthy sessions; roughly one short realtime turn only on a fault, plus a cheap background diagnostic summary. Storage and relay overhead are small fixed-size telemetry records, not raw audio by default.
- **security:** Do not upload raw probe audio or buffered speech unless the owner explicitly asks for a bug report. Send sample-rate/codec/sequence metadata and hashes by default; encrypt any owner-approved diagnostic clip, expire it quickly, and require confirmation before sharing it off-device or attaching it to an issue.
- **missing:** A negotiated, typed audio-session contract shared by firmware, relay, and playback bridge; A small pendant utterance ring buffer that survives a dropped link and marks exactly which frames were acknowledged; A deterministic fallback transport/UI on the pendant (LED/button plus relay text response); A Mac diagnostic collector that can turn a failed contract into a repairable bug report

### "“Put me in a private bubble when I ask: keep sensitive answers and account details off nearby screens and speakers, let me review or act through the pendant, and automatically restore my normal workspace when I leave private mode.”"
- **useful because:** A wearable assistant sits in rooms where other people can hear, while the Mac and authenticated browser expose far more than the owner intended. Today privacy is a conversational promise, not an enforced cross-surface state. A real private bubble lets the owner use the hive mind in public, at work, or beside family without leaking a password, medical detail, message, or account page through the wrong surface.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use deterministic policy and surface controls for entry, redaction, routing, and exit; use the realtime model only to classify the requested answer's sensitivity when no explicit label exists. A cheap background model may audit the session afterward, but must not receive raw private content merely to enforce the bubble.
- **latency:** Enter within 500 ms of a button press or explicit phrase, acknowledge privately through the pendant, and enforce screen/audio suppression before any sensitive result is rendered. Exit on explicit command or a configurable timeout, with a 1-second restoration budget.
- **cost:** Near-zero model cost for explicit mode changes; occasional short realtime classification for unlabeled content. Main cost is engineering and OS/browser integration, not tokens.
- **security:** The mode must fail closed: if the Mac or browser cannot attest that masking/muting succeeded, do not display or speak sensitive content there. Keep the mode state and sensitivity labels encrypted, do not log raw answers or screenshots, and require confirmation before opening the bubble to a new surface. A physical long-press should override accidental voice exit.
- **missing:** A signed, shared privacy-mode lease with owner-selected sensitivity classes and expiry; Mac and browser adapters that can attest to screen masking, notification suppression, tab redaction, and speaker routing rather than merely claiming success; A pendant-local indicator and button gesture that work when the network is down; A policy engine that separates private answer delivery from private action execution and records only a minimal proof receipt


## Changes it proposed to its own stack

### `firmware` — Implement an end-to-end AudioContract v1 negotiated per session: the pendant advertises capture clock (currently 15,625 Hz), encoder rate, frame duration, playback target, firmware build, and monotonic sequence; it emits a deterministic 20-ms probe and CRC/sequence markers. The relay must validate the contract against actual frame metadata, reject or explicitly label a resample instead of silently accepting it, and return a typed fallback reason. Add a 2–4 second circular compressed-frame buffer with an acknowledged-sequence watermark so one interrupted utterance can be retransmitted exactly once. On the current nRF9160, budget the buffer in external/flash-backed storage or reduce it to metadata plus the last unacknowledged utterance; do not pretend the 211,608-B application RAM can hold arbitrary PCM.
- **owner gets:** The owner gets an honest “24 kHz is active” guarantee—or an immediate, actionable fallback—instead of a conversation that appears complete but has mismatched capture/playback quality. A dropped link costs at most the unacknowledged phrase, not a required repetition of the whole turn.
- effort: Medium-high: firmware framing and bounded buffering, relay schema/validation, bridge telemetry, integration tests with deliberately mismatched clocks, and a Mac diagnostic receipt. The existing 15,625-Hz microphone means true 24-kHz capture still requires a clock/ADC/bridge redesign; this change first makes the limitation explicit and safe.  ·  risk: A retransmission bug could duplicate a phrase or increase modem airtime. Sequence/watermark deduplication and a hard per-utterance byte cap recover safely; if negotiation fails, use the existing path but announce degraded mode. A firmware rollback must understand both legacy and v1 frames.
- cost: No per-turn model cost. Small modem airtime increase only on loss; prototype firmware RAM pressure is significant because Opus already uses about 87% of one core when encode and decode overlap. A product revision with a native 24-kHz mic/clock is likely a modest BOM increase, roughly $3–$10, plus bridge/board redesign.  ·  latency: Adds under 300 ms once per session for probe/negotiation; steady-state latency unchanged. Recovery adds at most one frame window plus network RTT, rather than a full repeated turn.
- security: Metadata and CRCs are low sensitivity. Keep buffered speech encrypted and device-local by default; delete it after acknowledgement or a short TTL. Diagnostic uploads require explicit owner approval and must redact payloads unless requested.
- depends on: A typed relay/bridge AudioContract schema and version negotiation; The end-to-end 24-kHz acceptance test (capture, uplink, decode, playback—not merely output sampling rate); Durable job/receipt linkage for a recovered utterance so it cannot be charged or spoken twice

### `hardware` — Add a physical privacy control to the product pendant: a latching microphone-power cutoff or hardware mute gate, a distinct haptic motor, and a two-color status indicator visible to the wearer. The control should generate a signed local mode transition even with no network; the relay and Mac must treat the lease as authoritative until physical re-enable or expiry. Do not rely on the current prototype’s single button/LED or on software muting alone.
- **owner gets:** The owner can know, by touch and without looking at a screen, that nearby people cannot be captured or that a private answer will not escape through the Mac. It remains trustworthy during a dropped link, crashed agent, or mistaken voice command—the exact moments software-only privacy fails.
- effort: Medium hardware spin plus firmware, enclosure, accessibility testing, and relay/Mac attestation integration. The current nRF9160 development kit is explicitly provisional, so this belongs in the product design rather than being forced into its existing enclosure.  ·  risk: A hard mute can interrupt an important request; provide a tactile acknowledge and a clearly distinct re-enable gesture. If the indicator fails, default to muted and report uncertainty on reconnect. Added components and enclosure changes require EMC, battery, and ingress testing.
- cost: Roughly $1–$4 in components at volume for a haptic motor, LED/light-pipe, and analog mute gate or switch, with transient draw under 20 mA and negligible idle draw; a redesigned mic/codec path could add more. No model/API cost.  ·  latency: Immediate local privacy transition (under 50 ms); no network round trip. Re-enabling capture may add one session handshake before speech resumes.
- security: Strengthens the trust boundary by making capture suppression physically enforceable. Signed mode events prevent a compromised relay from claiming privacy; avoid storing mode history beyond a short audit receipt.
- depends on: The shared privacy-mode lease and fail-closed policy from the proposed capability; Firmware support for an offline local mode state and signed event counter; Relay/Mac/browser attestation that the physical mode is honored


## What it asked for

_Nothing._
## Its own summary

I found the still-important gap behind the owner’s explicit 24-kHz goal: the system has pipeline/audio and job/receipt primitives, but no negotiated contract proving capture rate, uplink rate, decode rate, playback rate, sequence continuity, or recovery. I proposed (1) an owner-facing capability that preserves an interrupted utterance and explains degraded mode without forcing repetition, and (2) AudioContract v1 with probe frames, CRC/ack watermarks, explicit resampling labels, and bounded buffering. This is deliberately honest about the current 15,625-Hz mic and nRF9160 RAM/CPU limits.

**Biggest unknown:** The exact end-to-end acceptance test and persistence semantics for recovered audio are still missing: whether “24 kHz” means microphone capture, encoded stream, decoded samples, or only I2S playback, and where the acknowledged-sequence/diagnostic receipt should live. Until those are specified, a green output-side sample-rate probe could falsely claim success.

