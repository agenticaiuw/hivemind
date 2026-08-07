# Harness derivation — unified — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path-status** — The pipeline already renders 24 kHz mono PCM end-to-end at Mac TTS (example 164,650 bytes, 3.43 s, 24,000 Hz), while the pendant decodes 24 kHz Opus and outputs through a 31,250 Hz I2S wire clock; uplink remains 15,625 Hz capture / 16 kHz Opus. Both encode/decode together consume ~87% of one nRF9160 core, so natural interruption needs careful scheduling.
  - evidence: GET /pipeline returned completed TTS event with 24 kHz metadata; hardware audio description reports 15,625 Hz capture, 24 kHz decode, 31,250 Hz I2S, and 87% combined CPU.

## Capabilities it proposed

### "Let me interrupt you naturally while you’re speaking—when I start talking, stop the reply, listen to what I said, and continue from there without making me press the button again."
- **useful because:** The pendant is currently effectively half-duplex: the owner must wait through speech or use the single button. Barge-in makes it usable in real life, especially when a reply is long, wrong, or unsafe to act on. It relies on the pendant for immediate acoustic interruption, the relay for stream cancellation, and the Mac/voice model for a fresh turn; no single node can provide a responsive, coherent experience alone.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** gpt-realtime-2.1 for the active turn and interruption transcript; no additional model call for VAD/cancellation. Use a cheaper background model only to summarize abandoned speech turns for diagnostics, if enabled.
- **latency:** Local playback duck/stop within 120 ms of voice onset; relay cancellation within 300 ms; new listening state announced or captured within 500 ms. Engineering time is dominated by race-proofing cancellation, packet sequencing, and testing LTE-M loss—not inference.
- **cost:** Negligible incremental API cost for the interrupted turn (the already-running realtime stream is cancelled); modest extra audio uplink for the new turn. Main cost is implementation and test coverage, not tokens.
- **security:** Raw microphone audio remains on the pendant/relay path under existing retention policy; accidental household speech could trigger interruption. Keep VAD local, upload only after speech onset, discard the cancelled assistant audio, and require confirmation only if the interrupted reply had an irreversible action pending.
- **missing:** Local playback-side VAD with an interrupt event and debounce; A relay protocol carrying generation IDs plus idempotent cancel/ack; Mac bridge support for cancelling queued TTS and publishing an interruption receipt; A user-visible setting for sensitivity and a test fixture for speech-over-TTS in LTE-M loss conditions

### "Give me a spoken emergency stop for the whole hive: when I say my private stop phrase, immediately cancel queued Mac/browser work, revoke pending approvals, stop outgoing audio, and tell me exactly what was prevented or already irreversible."
- **useful because:** Today cancellation is surface- or job-specific and may require reaching the Mac. A worn-device stop phrase gives the owner a reliable last-resort control when a browser action looks wrong, the pendant is misplaced, or a queued routine starts behaving unexpectedly. It is useful precisely because the relay stays awake, the pendant is always with the owner, and the Mac/browser may be remote or asleep.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No realtime model call for recognition after a local wake/phrase detector; use a small fixed command grammar and relay-side authentication. Use the expensive realtime tier only if the phrase is unclear, never to decide whether an emergency stop is valid.
- **latency:** Pendant should enter a local muted/stop state within 150 ms; relay revocation fan-out within 500 ms when online; Mac/browser acknowledgements within 2 seconds. Cost is dominated by reliable fan-out and recovery testing, not inference.
- **cost:** Negligible per invocation: one authenticated control message and a few metadata receipts. No audio upload is needed for a confident local phrase match.
- **security:** A thief or nearby speaker must not be able to trigger or learn the phrase. Store only a salted verifier/derived local matcher, support an optional button-held gesture for high assurance, rate-limit attempts, and never speak sensitive job details until the owner re-authenticates. Stopping cannot undo an already submitted external action; the response must distinguish cancelled, blocked, and irreversible.
- **missing:** A pendant-local fixed-phrase detector and authenticated emergency control frame; Relay-wide revocation registry with monotonic epoch numbers; Mac/browser hooks that subscribe to revocation epochs and terminate queued/active work; A dashboard recovery flow to review what was stopped and re-enable normal operation


## Changes it proposed to its own stack

### `firmware` — Add a low-cost playback-side barge-in detector on the nRF9160: maintain a short rolling microphone RMS/zero-crossing window while Opus playback runs, subtract a playback-energy reference when available, and emit an interrupt frame containing generation_id, monotonic sample index, confidence, and 120 ms pre-roll. Stop or duck the decoder immediately; never run a second Opus encoder concurrently with decode. If confidence is below threshold, keep playback and do not upload.
- **owner gets:** They can say “no, that’s wrong” over the pendant and be heard immediately instead of waiting or pressing the only button. The pre-roll preserves the first syllable that would otherwise be clipped.
- effort: Medium-high: fixed-point VAD, acoustic tuning against the bridge speaker/mic path, ring-buffer integration, and power tests. Reserve roughly 8–12 kB RAM for the pre-roll and feature state; schedule around the documented ~87% encode/decode CPU load.  ·  risk: False triggers from TV/music or playback echo could cut off replies. Recover by configurable confidence/hangover thresholds, a long-press override, and generation-scoped cancel so a late packet cannot stop a newer turn.
- cost: No API cost; a few kB flash/RAM and a small CPU duty increase. No new hardware cost or meaningful idle power draw; interruption listening adds mic processing only during playback.  ·  latency: Local stop/duck target under 120 ms; VAD adds no latency to normal capture.
- security: VAD decisions stay local; upload only the interrupt event plus deliberate speech pre-roll. Do not persist microphone windows to SD except under the existing failed-upload buffer policy.
- depends on: 24 kHz playback path acceptance test; A relay interrupt/cancel protocol with generation IDs

### `relay` — Introduce an interruption-safe audio session state machine shared by relay and Mac bridge: PLAYING(generation), INTERRUPT_PENDING, CANCEL_ACKED, LISTENING(next_generation), with idempotent cancel keys and sequence numbers. On interrupt, invalidate queued TTS chunks at the relay, tell the Mac bridge to cancel synthesis/output, acknowledge to the pendant, and reject stale audio from the prior generation. Persist only compact receipts, not discarded PCM.
- **owner gets:** A fast interruption will actually work even when LTE-M packets arrive late: old speech will not resume over the owner’s new question, and the device can recover cleanly after a dropped connection.
- effort: Medium: protocol/schema changes, bridge cancellation hooks, reconnect replay rules, and fault-injection tests for duplicate/late packets.  ·  risk: A lost cancel acknowledgement could leave the pendant silent or in the wrong state. Use bounded timeouts, local pendant fallback to LISTENING, and a reconciler that expires orphaned generations.
- cost: Negligible inference cost and a few D1 receipt rows per interruption; no audio retention for cancelled generations. Slight relay CPU for state handling.  ·  latency: Adds one small control round trip, but local playback stop does not wait for it; target cancel acknowledgement under 300 ms.
- security: Generation IDs and opaque job IDs only; do not put transcript text in control frames. Existing auth and retention rules remain authoritative.
- depends on: Pendant interrupt event format; Mac bridge cancellable TTS/output API

### `dashboard-ux` — Add an “audio session” inspector showing current generation, capture/playback sample rates, codec queue depth, interruption confidence, cancel/ack timing, stale-packet drops, and whether any audio was buffered to SD. Include a one-click replay of the state-machine trace with PCM content excluded by default.
- **owner gets:** When the pendant talks over itself, misses a word, or seems slow, the owner can see whether the cause was speech detection, LTE-M delay, or audio buffering instead of guessing—and can verify that private audio was not retained.
- effort: Medium: event schema, compact visualization, and a synthetic speech-over-TTS test view.  ·  risk: Telemetry could expose sensitive content if transcripts or audio are logged. Keep the default trace metadata-only, redact text, gate raw waveform access behind an explicit local action, and expire detailed traces quickly.
- cost: Small D1/storage increase for metadata; no model cost. Avoid storing PCM or transcript payloads in the inspector.  ·  latency: None on the live audio path if events are sampled and emitted asynchronously.
- security: Improves auditability while reducing data exposure; enforce owner authentication and local-only raw diagnostics.
- depends on: Relay generation/cancel state machine; Firmware interrupt telemetry; 24 kHz validation harness

### `interaction` — Add a voice-approval capability bound cryptographically to one exact pending browser mutation: the Mac/browser workbench computes a canonical action digest and short human-readable summary, the relay sends a one-time challenge to the pendant, and the owner can approve, reject, or request a readback by voice. The pendant signs/returns only the challenge decision; the browser executes only if the digest, tab/session, expiry, and risk class still match, then returns a receipt. Any DOM/value change invalidates the approval.
- **owner gets:** The owner can safely approve a prepared private-account action while away from the Mac—without exposing the logged-in page to the pendant, repeating the whole task, or trusting an ambiguous “yes.” This is a genuinely joint capability: browser access supplies the private transaction, Mac supplies the diff and receipt, relay binds the challenge, and the worn device supplies deliberate presence and voice intent.
- effort: High: canonicalization of browser mutations, challenge lifecycle and replay protection, pendant confirmation UX, relay signing/verification, and tests for stale tabs, navigation, reconnects, and speech ambiguity.  ·  risk: A mistaken spoken approval could authorize an unwanted action, or a compromised browser session could attempt substitution. Require a concise readback for high-risk classes, explicit confirm words rather than generic assent, short expiry (for example 60 seconds), digest-bound execution, and a visible undo/receipt path where the site supports it. Never approve sending mail, purchases, deletion, or external submission without the existing confirmation policy.
- cost: Small relay/D1 metadata cost per approval and negligible model cost; the expensive work is security engineering and browser test coverage. No raw page contents or voice recording need be retained after the decision receipt.  ·  latency: About one relay round trip plus spoken confirmation; target under 3 seconds from the owner’s approval to browser execution. No effect on ordinary conversations or browser reads.
- security: Improves security versus unbound voice commands: least-privilege one-time decisions, exact action digests, tab/session affinity, expiry, replay resistance, and an audit receipt. Voice audio should be discarded after intent extraction under the existing retention policy.
- depends on: A shared canonical representation for browser field mutations and action digests; A pendant-to-relay authenticated challenge response; Browser execution receipts that include the precondition digest and post-action evidence


## What it asked for

_Nothing._
## Its own summary

Round 17 produced a new cross-surface capability: natural barge-in. I confirmed the current path is already producing 24 kHz mono TTS (3.43 s example) but the pendant remains half-duplex, with 15,625 Hz capture, 24 kHz decode, 31,250 Hz I2S output, and ~87% nRF9160 CPU when encoding and decoding overlap. I proposed local playback-side VAD with pre-roll, a generation-scoped relay/Mac cancellation state machine, and metadata-only audio-session diagnostics. The owner benefit is immediate interruption without the single-button press, with stale LTE-M audio prevented from resuming.

**Biggest unknown:** I still need the authoritative 24 kHz acceptance criteria and target architecture, plus an executable audio-pipeline validation/fault-injection harness and firmware/bridge build access. Specifically, we need measured end-to-end stop latency, acceptable false-trigger rate, packet-loss behavior, and confirmation that the nRF9160 scheduling budget remains safe under barge-in. The live Mac agent is healthy (v0.5.0, 120 routes), but no granted validation tool or hardware-build permission is visible this round.

