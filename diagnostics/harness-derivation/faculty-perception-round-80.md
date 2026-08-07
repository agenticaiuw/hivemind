# Harness derivation — faculty-perception — round 80

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-presence** — At 2026-08-07T13:14Z, the reachable fleet contains an online Mac bridge (last seen 13:14:05Z), an offline Chrome browser extension (last seen 12:58:09Z, 7 pending commands), and an offline mobile test device (last seen 2026-07-31); no pendant is registered or online.
  - evidence: discover:devices returned home-macbook-bridge online, home-chrome offline, cloudflare-contract-test offline; GET /ops/status reports browser online=false and relay macBridgeOnline=true.
- **mac-permissions** — The Mac agent's required automation permissions are granted, but Accessibility and Screen Recording are both untrusted/missing; /ops/status reports permissions.ready=false and computer-use loop disabled.
  - evidence: GET /ops/status at 2026-08-07T13:14Z: accessibility.trusted=false, screenRecording.granted=false, requiredMissing=[]; computerUse.loopEnabled=false.
- **relay-and-audio** — The relay is reachable and configured for speech, durable audio, and persistent state, but no pendant is live; pendant audio records in /pipeline are historical rather than evidence of current wearable connectivity.
  - evidence: GET /ops/status relay.payload: reachable=true, pendantPipelineTelemetry=true, durableAudio=true, macBridgeOnline=true; discover:devices has no pendant and current browser/bridge statuses show only Mac online.
- **ui-input-reachability** — At 2026-08-07T13:14:33Z, synthesized UI input from the running AI Pendant Agent does not reach the screen: Accessibility is untrusted, inputReachability.status=failed, and UI action receipts cannot be trusted. Automation APIs are otherwise granted.
  - evidence: GET /observe: accessibility.trusted=false, eventsPost=false, uiActionsWillReachTheScreen=false, consequence explicitly says ui_click/type_text/press_keys may report success while doing nothing.
- **browser-staleness** — The Mac retains three browser session records with tabs last used between 05:40 and 06:26Z, but the browser extension is offline at 13:14Z with seven pending commands; these tabs are not proof of current browser reachability.
  - evidence: GET /observe lists 3 sessions with old lastUsedAt values; GET /browser/status says online=false, pendingCommands=7; GET /jobs records recent browser actions failing due to offline/timeout.
- **historical-pipeline-not-live** — The latest pipeline history includes a 12:00Z response marked “waiting for the pendant” and a 07:22Z nRF9160 alert-delivered event from pendant-offline-store, while current device discovery has no pendant. These are historical delivery records, not current delivery.
  - evidence: GET /pipeline returned relay_result detail “The nRF9160 can now download and play it” at 12:00:39Z and offline-store event at 07:22Z; discover:devices has no pendant.

## Capabilities it proposed

### "Let me interrupt you naturally while you are speaking, and have you hear the interruption completely without dropping seconds of my speech or waiting for the answer to finish."
- **useful because:** Today the wearable conversation competes for one constrained LTE-M path: when the agent speaks while the owner talks, measured loss reached about 7.8 seconds. A genuinely conversational assistant must preserve the owner's interruption, stop obsolete playback quickly, and continue from what was actually said.
- **path:** pendant → relay-realtime → mac-planner → unified
- **model tier:** gpt-realtime-2.1 for the live turn only; no background model is needed. The relay handles barge-in state, while the pendant performs local playback ducking and capture buffering.
- **latency:** Local ducking and capture must begin within 80 ms of speech/barge-in detection; relay turn cancellation and replacement audio should begin within 300 ms. The owner's full interruption must survive a transient LTE-M contention window.
- **cost:** Negligible incremental model cost per turn; likely 1 extra realtime event per interruption. Hardware prototype cost roughly $15–$35 for a production-grade dual-radio/audio front end, plus firmware and relay engineering. Ongoing power draw rises during concurrent capture/playback, dominated by the radio and Bluetooth bridge.
- **security:** Transmit only the interruption audio already authorized for the conversation; discard superseded response audio and local buffers after the turn. Sequence numbers and opaque turn IDs must prevent replaying stale speech. Require explicit pairing and authenticate the second radio/audio path.
- **missing:** A pendant audio architecture with independent capture and playback scheduling rather than one saturated LTE-M WebSocket; Local barge-in detector and bounded pre-roll ring buffer in firmware; Relay turn cancellation/replacement protocol keyed by monotonic conversation and audio sequence IDs; A transport that can carry uplink speech while downlink playback is active (for example a second radio path, stronger LTE-M scheduling, or a local phone relay); Mac/ESP32 bridge support for immediate playback stop and resume without corrupting the audio stream


## Changes it proposed to its own stack

### `context` — Add a cross-surface reality ledger that periodically samples /ops/status, /browser/status, /pipeline, /machine-context, relay device presence, and (when paired) pendant heartbeats into immutable observation records. Each record must carry source, observedAt, expiresAt, connectivity epoch, and an explicit absence/unknown state; derived claims (for example “a live pendant is connected” or “this audio is current”) are valid only while their evidence is fresh and must expose contradictions such as live Mac bridge versus offline browser. Historical pipeline rows must never satisfy a live-device claim.
- **owner gets:** The owner can ask whether the system is actually reachable and get an honest answer instead of hearing a historical recording presented as live. It prevents silent failures—especially acting on stale browser tabs or believing a pendant is connected when it is not—and makes every faculty member consume the same current truth.
- effort: Medium: shared observation schema and TTL evaluator in relay/local agent, one sampler, dashboard rendering, and adapters for future pendant heartbeat; no new model required.  ·  risk: Incorrect TTLs could mark a healthy but quiet device stale, or a transient race could produce UNKNOWN. Recover by retaining raw observations, showing age and source, and never converting UNKNOWN into false. No action is taken from this ledger.
- cost: Negligible storage/CPU; a few small status requests per sampling interval. No model/API cost unless a user asks for a natural-language summary.  ·  latency: Sub-second local reads; relay freshness is bounded by sampling interval. User answers can be generated from structured facts without realtime-model context replay.
- security: Store only device IDs, status, timestamps, and opaque correlation IDs—never audio or page contents. Keep relay and Mac bearer authentication; redact host inventory from user-facing summaries.
- depends on: A relay device-presence/heartbeat endpoint with authenticated reads; A shared typed context projection (chg-a82e0b13 family); Existing GET /ops/status, GET /browser/status, GET /pipeline, GET /machine-context and future pendant ACK/heartbeat telemetry

### `integration` — Make action receipts capability-aware: before and after any synthesized-input action (click, menu, type, keypress), attach the latest /observe inputReachability record and classify the receipt as verified, unverified, or blocked. If uiActionsWillReachTheScreen=false or the observation is stale, do not report success; quarantine the result for review and require a non-UI verification route (AppleScript state, app document readback, or explicit owner confirmation).
- **owner gets:** The owner will stop being told that an email was typed, a button clicked, or a form changed when macOS silently ignored the input. Failures become obvious and recoverable instead of creating false confidence in automation.
- effort: Small-to-medium local-agent change: enrich executor receipts, add a freshness check, and provide readback adapters for the already-granted AppleScript apps; dashboard can display the classification.  ·  risk: Some real actions will be marked unverified when permissions or probes are temporarily stale, reducing automation convenience. Recovery is safe retry after a fresh probe or owner confirmation; never silently upgrade an unverified receipt.
- cost: No model cost; a local /observe read and occasional AppleScript readback. Minimal JSON receipt growth.  ·  latency: Adds one local observation read and, only for UI actions, optional readback (tens to hundreds of milliseconds).
- security: Receipts should store only action type, reachability state, app bundle, and hashes—not typed secrets or screen content. Existing bearer authentication remains required.
- depends on: Existing GET /observe inputReachability fields; Existing job receipts at GET /jobs/:jobId/receipts; Existing execution journal and AppleScript automation routes; Owner-granted Accessibility if verified UI automation is desired


## What it asked for

_Nothing._
## Its own summary

Established fresh, cited reality: Mac bridge online at 13:14Z; no pendant registered; Chrome bridge offline with 7 queued commands despite three stale browser session records; relay reachable; Accessibility and Screen Recording missing, so synthesized UI receipts are untrustworthy; pipeline entries are historical and include offline-store/waiting-for-pendant states. Recorded these findings. Proposed a cross-surface freshness/absence reality ledger and capability-aware UI receipt quarantine, both grounded in live routes.

**Biggest unknown:** Authoritative relay-side device registry and delivery ACK semantics: whether any pendant/ESP32 has received, begun, or finished playback cannot currently be established from Mac-local routes. Also still missing a single shared perception snapshot API that joins relay presence, Mac readiness, browser freshness, pipeline history, and action reachability.

