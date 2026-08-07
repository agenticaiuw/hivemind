# Harness derivation — faculty-perception — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Mac local agent is live (v0.5.0), relay reachable, but readiness is false because Accessibility is untrusted and Screen Recording permission is missing; no required permissions are missing, and computer-use loop is disabled.
  - evidence: GET /ops/status returned 200: permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false, computerUse.loopEnabled=false.
- **browser bridge status** — Authenticated browser extension is currently offline; the Mac agent reports two pending browser commands and only the offline fanout-probe-cleanup device.
  - evidence: GET /ops/status returned browser.online=false, devices[0].online=false, pendingCommands=2.
- **audio path current implementation** — Pendant uplink captures at 15,625 Hz and Opus-encodes as 16 kHz/16 kbps; playback decodes 24 kHz in 60 ms frames then resamples to a 31,250 Hz I2S wire clock. Both encode and decode together use about 87% of one Cortex-M33 core.
  - evidence: hardware audio description from firmware/nrf9160/src/audio_opus.c and cloud-relay/opusTranscode.js.
- **relay status** — Cloud relay v1.1.0 is reachable, paired, API key and speech-to-text configured, D1-backed, with durable audio and pendant telemetry; Mac bridge was online at 2026-08-07T09:16:33.809Z.
  - evidence: GET /ops/status returned relay.reachable=true and relay.payload with those fields.

## Capabilities it proposed

### "“Before I rely on it, tell me whether my pendant can hear me and play a reply right now.”"
- **useful because:** The owner currently cannot distinguish a dead browser bridge, missing Mac permissions, LTE/relay failure, or a broken audio path. A single spoken verdict with the failing hop and last-seen time would prevent silent failures and wasted retries.
- **path:** pendant: run a short local mic/playback loopback and report codec/frame counters over the next uplink → relay: correlate the pendant session, LTE/relay receipt, STT arrival, and TTS delivery into one diagnostic trace → mac-bridge: report bridge reachability, Bluetooth sink state, and whether the Mac agent is actually ready (including Accessibility/Screen Recording) → dashboard: render the hop-by-hop trace and preserve the last successful check for support
- **model tier:** background for scheduled checks and gpt-5.6-luna for interpreting an on-demand trace; do not spend gpt-realtime on this unless the owner asks during an active call
- **latency:** On-demand spoken result within 5 seconds; local loopback under 500 ms; no repeated cloud polling beyond one diagnostic session.
- **cost:** About $0.01–$0.04 per on-demand check, dominated by one short transcription/interpretation call; scheduled checks can be rule-based and near-zero model cost.
- **security:** Audio test samples and device identifiers leave the pendant only if the owner approves the remote test; default to synthetic playback plus signal statistics, retain the trace for 24 hours, and require confirmation before uploading raw microphone audio.
- **missing:** A pendant diagnostic command/report protocol that exposes capture level, Opus encode/decode counters, LTE state, and playback underruns; A relay correlation ID spanning pendant frames, STT, TTS, and Mac bridge delivery; A Mac bridge health endpoint that includes Bluetooth sink status and actionable permission remediation; A dashboard and spoken-result formatter for the diagnostic trace

### "“If I lose signal or walk away from my Mac in the middle of a conversation, keep my place and resume the same conversation when either the pendant or Mac becomes reachable—tell me exactly what was heard, what was answered, and what still needs me.”"
- **useful because:** Today a dropped LTE link or unavailable browser bridge can turn a useful spoken exchange into an ambiguous failure. The owner should get continuity with an explicit boundary, not a duplicate command or a silently lost turn.
- **path:** pendant: assign each spoken turn a monotonic conversation/turn ID, persist the unsent utterance and playback acknowledgment locally, and show a distinct queued/resumed signal with the single button/LED → relay: durably checkpoint turn state, transcript confidence, generated response, and delivery acknowledgments; deduplicate retries and expire sensitive unfinished turns → mac-bridge: when reachable, reconcile the same turn ID, optionally present the pending result in the local agent/dashboard, and return delivery acknowledgment without pretending the pendant heard it → browser: if the interrupted turn concerned a logged-in page, preserve the exact tab/session provenance and prevent re-execution until reconciliation → dashboard: show one timeline of heard, processed, delivered, and confirmed states with a clear unresolved state
- **model tier:** Use deterministic state reconciliation and a cheaper background model for summarizing recovery; reserve gpt-realtime-2.1 for the live turn itself, not retries or status narration.
- **latency:** Normal handoff acknowledgment under 1 second when a path is available; durable checkpoint before accepting the next turn; resume within 3 seconds after reconnection. Never block indefinitely on the absent surface.
- **cost:** Roughly $0.005–$0.03 per recovered turn for a compact retry summary or transcript repair; most reconnects should be rule-based with no additional model call. Storage and telemetry dominate at scale.
- **security:** Unfinished speech and private page context must be encrypted at rest and scoped to the paired owner; unfinished turns should expire quickly (for example 24 hours), never replay an irreversible browser action automatically, and require confirmation if recovery would send, buy, delete, or submit.
- **missing:** A cross-surface durable turn ledger with idempotency keys and delivery acknowledgments; Pendant flash/SD queue semantics and firmware UI for queued versus delivered audio; Relay APIs for checkpoint, resume, conflict resolution, and expiry; Mac/browser adapters that can consume a pending turn without duplicating side effects; A recovery-specific spoken and dashboard receipt format


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's 15.625 kHz I2S microphone path plus nRF9160-side 16 kHz Opus uplink with a low-power audio front end that can deliver native 24 kHz mono PCM (or 24 kHz Opus input) to the system; keep the nRF9160 for LTE-M control and move resampling/packet preparation to the ESP32-class audio processor or a small dedicated DSP. Specify a clocked, timestamped audio contract at 24,000 Hz end to end, rather than the current 31,250 Hz wire-clock workaround.
- **owner gets:** The owner gets genuinely superwideband speech capture instead of 15.625/16 kHz capture upsampled only on playback, with fewer resampling artifacts and more headroom for intelligibility in noisy everyday use. It also removes the current near-single-core CPU budget that makes simultaneous encode/decode fragile.
- effort: High: select an audio codec/DSP and microphone, redesign the I2S clocking and enclosure/power rails, implement timestamped transport and Opus profiles, then validate LTE coexistence and Bluetooth playback. A staged firmware-only 24 kHz uplink experiment should precede the board spin.  ·  risk: A new clock domain can introduce drift, buffer growth, or dropouts; LTE transmit bursts may brown out the audio rail; added DSP firmware may regress the current path. Recover with a negotiated capability flag and fall back to the existing 16 kHz uplink/24 kHz playback mode, with recorded A/B fixtures in CI.
- cost: Prototype hardware roughly $15–$40 in codec/DSP, mic, regulator, and PCB changes, plus perhaps 10–40 mW active audio power; API cost is unchanged or slightly lower if fewer retransmits occur.  ·  latency: Potentially 5–15 ms lower audio buffering if the 60 ms Opus framing is reduced, but initial implementation may add one 10–20 ms DSP buffer. Keep 60 ms as a compatibility mode.
- security: No new cloud data class; higher-fidelity microphone audio is more sensitive, so preserve the existing retention policy and make raw capture diagnostics opt-in.
- depends on: Define and instrument a versioned 24 kHz audio contract across pendant, relay, and bridge; Measure current packet loss, underruns, and clock drift before changing hardware; Add negotiated fallback so prototype nRF9160 units remain usable


## What it asked for

_Nothing._
## Its own summary

Established live truth: the Mac agent is healthy at HTTP level and relay-connected, but operationally not ready because Accessibility and Screen Recording are missing; the browser extension is offline with two queued commands. The audio path is not end-to-end 24 kHz: capture is 15,625 Hz, uplink is 16 kHz Opus, playback decodes 24 kHz and resamples to 31,250 Hz, while encode+decode consume about 87% of one nRF9160 core. Recorded these facts. Proposed an owner-facing hop-by-hop pendant health check and a hardware/audio architecture change for native 24 kHz with negotiated fallback.

**Biggest unknown:** I still cannot establish live pendant firmware counters, LTE/audio underruns, or the actual deployed 24 kHz implementation because the requested pendant diagnostics/observability and implementation-status context have not arrived. I also need a real 24 kHz test trace before anyone should claim the owner's stated audio objective is shipped.

