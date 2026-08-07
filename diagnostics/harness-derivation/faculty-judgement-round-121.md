# Harness derivation — faculty-judgement — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my pendant’s speech clear automatically as I move between a quiet room, a noisy street, and a Mac/browser call—without making me run a calibration each time."
- **useful because:** The owner gets consistent intelligibility during the moments they actually rely on the pendant. A tiny device can sense acoustic conditions, the relay can choose a safe low-latency profile, and the Mac/browser can apply the matching input/output route; each change is reversible and reported in one short receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a deterministic/on-device classifier and cheap relay DSP scorer for routine environment changes; reserve realtime model only for ambiguous transitions or when the owner asks why audio changed. No background LLM call is needed for ordinary profile switches.
- **latency:** Classify locally in under 100 ms; relay decision and profile push under 300 ms; Mac/browser application under 1 s. Never interrupt speech for a profile change; queue it until an utterance boundary.
- **cost:** Usually <$0.001 per transition (telemetry plus deterministic DSP); occasional explanation costs one realtime turn. Storage is a few hundred bytes per transition plus profile definitions.
- **security:** Transmit features/levels, not raw room audio, by default; discard any calibration snippets immediately after scoring. Call apps and browser tab identity are sensitive, so expose only the selected route/profile in receipts. Require confirmation before changing a call’s active microphone or camera; volume/EQ and reversible device selection may follow the owner’s existing automation policy.
- **missing:** A versioned audio-profile schema shared by firmware, relay, Mac, and browser (input gain, AGC, noise suppression, codec mode, output EQ, route);; a firmware acoustic-feature sampler that fits the 211,608 B application-RAM budget and emits no raw audio;; a relay profile state machine with hysteresis, utterance-boundary application, rollback, and durable receipts;; Mac/browser adapters that can apply and verify profiles through the existing granted AppleScript/high-level actions, plus a dashboard timeline of profile changes;; acceptance tests for 24 kHz speech intelligibility, transition latency, clipping, and privacy deletion.

### "If the pendant or relay is unsure what I said, catch the bad phrase before anything happens, ask me for only that phrase, and then continue the original request without making me start over."
- **useful because:** Today a noisy or clipped word can turn a perfectly good spoken request into a failed action or, worse, the wrong action. The owner should experience a two-second, targeted repair instead of repeating an entire multi-step thought or discovering the mistake afterward.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Use streaming ASR confidence, acoustic clipping features, and deterministic entity/action validation first. Invoke the realtime model only to formulate the shortest repair question and reconcile the corrected span; use a cheaper background model for post-action quality analytics.
- **latency:** Detect a suspect span within 250 ms of the utterance end and ask within 700 ms. Preserve the original intent for up to 30 seconds while waiting; never block unrelated audio or silently guess after the repair window expires.
- **cost:** Routine turns add negligible DSP/metadata cost; roughly one extra realtime turn only when a repair is needed, typically <$0.01 per repair. Keep only the original and corrected transcript spans plus hashes, not raw audio.
- **security:** The system must not execute an irreversible action while any required slot is uncertain. Show the owner the exact disputed word/field on the Mac when available, speak no sensitive surrounding transcript aloud in public, and expire the pending intent locally and server-side after 30 seconds. Confirmation remains mandatory for sending, deleting, purchasing, or other destructive actions.
- **missing:** A typed utterance-repair protocol carrying span offsets, confidence, acoustic-failure reason, preserved intent, expiry, and corrected value across pendant and relay; A deterministic pre-action validator that marks which slots are safety-critical and refuses to fill them by best guess; A low-memory pendant clipping/noise feature stream and a local retry tone/button path that works through a dropped link; A faculty-action transaction hold that can resume the same plan after one corrected span, with a receipt showing original, repair, and final values; Mac/browser UI support for highlighting the disputed field without replaying the entire request


## Changes it proposed to its own stack

### `firmware` — Add an event-boundary audio adaptation service: compute 10 Hz bands/level/noise-floor/clipping features locally, classify quiet/voice-noise/music/wind with hysteresis, and publish only a signed profile recommendation (not raw audio) over the existing audio/events path. Keep two profiles and a rollback record in flash; apply only between utterances and expose a physical-button long-press to freeze the current profile.
- **owner gets:** Speech remains understandable without the owner fiddling with settings, while a long press gives them an immediate, dependable way to stop automation in a sensitive environment.
- effort: Medium firmware work plus relay contract and Mac/browser adapters; 2–3 weeks including acoustic acceptance tests.  ·  risk: A wrong classifier could make audio worse or change during a call. Hysteresis, confidence thresholds, utterance-boundary application, profile rollback, and a freeze gesture recover safely; default profile remains unchanged on link loss.
- cost: No meaningful API cost; roughly 8–16 KB code, under 6 KB RAM, and negligible flash writes if recommendations are rate-limited. Hardware cost $0 on prototype.  ·  latency: Feature windows add 100 ms; profile changes take effect within 1 s but never mid-utterance.
- security: Only coarse acoustic features and signed recommendations leave the pendant; no raw room audio is retained. Freeze gesture is local and works offline.
- depends on: A versioned cross-surface audio-profile schema and relay state machine; A 24 kHz intelligibility/clipping acceptance scorer; Mac/browser profile apply-and-verify adapters

### `hardware` — For the product revision (not the current nRF9160 DK prototype), add a matched dual-microphone pair with physical windscreen/acoustic isolation and a low-power audio codec path capable of verified 24 kHz capture/playback; retain the single button as the local profile-freeze/stop control.
- **owner gets:** The pendant would remain intelligible outdoors and while walking, rather than asking software to recover speech that a single exposed microphone never captured cleanly.
- effort: Product-level acoustic/mechanical redesign, codec validation, enclosure spin, and firmware driver work; prototype evaluation in 4–6 weeks.  ·  risk: More acoustic tuning and power draw; two microphones can amplify enclosure mismatch. Recover by shipping a single-mic fallback profile and factory self-test, with no automatic dual-mic use when confidence is low.
- cost: Approx. $3–8 BOM increase at volume for microphones, codec/analog front end, and acoustic parts; estimated 10–25 mW additional active audio power, subject to codec choice.  ·  latency: Negligible codec latency change if designed around the existing low-latency path; beamforming adds under 10 ms with a fixed-point implementation.
- security: No new network data; local second-mic signals are processed transiently and never retained by default.
- depends on: 24 kHz end-to-end audio acceptance criteria; Audio-profile schema and runtime adaptation state machine; Acoustic enclosure and wind-noise test fixtures

### `interaction` — Introduce a first-class 'uncertain span' transaction state between perception and action. The planner must carry the original intent and all resolved slots, mark only low-confidence spans, ask one targeted spoken repair, then re-run validation and produce a diff before releasing the action. If the link drops, the pendant stores a compact repair token and gives a local retry tone; it never guesses or expires into execution.
- **owner gets:** A clipped name, number, or date no longer forces the owner to repeat an entire request or risk the wrong real-world action. They get a fast, understandable repair and continuity across the pendant, relay, Mac, and browser.
- effort: Medium protocol and UX work across perception/action/relay plus a small firmware queue; extensive adversarial tests for stale repairs, duplicate delivery, and destructive actions.  ·  risk: A stale correction could be attached to the wrong request, or repeated prompts could annoy the owner. Bind every repair to an intent hash, tab/job/session ID, and short expiry; cap retries at one and fall back to a clear failure receipt.
- cost: Minimal persistent storage (under 1 KB per pending repair); one additional realtime turn only on uncertain speech; no new hardware required.  ·  latency: Adds under 700 ms when repair is needed; zero added latency to high-confidence utterances.
- security: This is a safety barrier: uncertain destructive fields cannot pass. Sensitive transcript spans remain encrypted and expire; only the disputed span is spoken or displayed.
- depends on: Typed utterance-repair protocol; Pre-action slot-confidence validator; Durable intent hash and job/session binding; Offline pendant retry token


## What it asked for

### `t25-p9ni` (tool) — audio_profile_apply_verify
- why: The owner wants 24 kHz speech that stays clear across environments. A profile transition must be applied and verified atomically across the Mac audio stack and the active browser call, with rollback if verification fails.

```json
{
  "profileId": "string",
  "profileVersion": "string",
  "target": "mac_system|browser_tab|both",
  "expected": {
    "sampleRateHz": "number",
    "inputRoute": "string|null",
    "outputRoute": "string|null",
    "maxInputLevelDbfs": "number|null",
    "minSpeechScore": "number|null"
  },
  "applyAt": "now|utterance_boundary",
  "rollbackProfileId": "string|null",
  "idempotencyKey": "string"
}
```

## Its own summary

This round I moved the 24 kHz work from a generic calibration idea to runtime, privacy-preserving adaptation: the pendant classifies acoustic conditions locally, the relay selects a versioned profile with hysteresis, and Mac/browser apply it only at utterance boundaries with rollback. I recorded the firmware change, a product-hardware direction, and queued a precise `audio_profile_apply_verify` tool because current Mac/browser actions cannot atomically apply or verify OS-level DSP/call routes. What I still need is implementation of the shared profile schema/state machine, the 24 kHz speech/clipping scorer, and adapters that can verify and roll back profiles. No new orchestrator grants appeared in the granted category this round.

**Biggest unknown:** The actual 24 kHz audio chain and acceptance thresholds remain unverified: codec/sample-rate support, current capture/playback route, and whether the Mac/browser can expose measurable speech-quality telemetry without raw audio leaving the device.

