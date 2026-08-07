# Harness derivation — faculty-perception — round 72

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-state** — At 2026-08-07T12:44:48Z the Mac bridge is reachable and AI Pendant Agent v0.5.0 is online; required automation permissions are granted, but Accessibility and Screen Recording are false, inputReachability is failed, and UI actions cannot be trusted.
  - evidence: GET /ops/status and GET /observe live responses
- **browser-state** — At 2026-08-07T12:44Z the home Chrome browser extension is offline with 0 tabs visible to the bridge and 5 pending browser commands; the Mac bridge still reports 3 durable browser sessions containing UTC and two test pages.
  - evidence: discover devices plus GET /ops/status and GET /observe
- **machine-timezone** — The Mac authoritative timezone is America/New_York.
  - evidence: GET /machine-context live response
- **pipeline-observability** — The live pipeline ledger contains a completed Mac-planned morning-news run whose TTS was 24,000 Hz mono s16le, 75,734 PCM bytes, 1,578 ms, no clipping, then accepted by relay for pendant download. It also contains a pendant-originated offline-store event where 2 held alerts were surfaced at uptime 323 s, and a later realtime audio-native plan with 937,500 PCM bytes at 15,625 Hz that uploaded successfully.
  - evidence: GET /pipeline live response at 2026-08-07T12:44Z

## Capabilities it proposed

### "When I say “did you hear me, and did I hear your reply?”, give me a trustworthy end-to-end receipt for that conversation turn—showing what the pendant captured, what the relay received, what the Mac produced, what audio was delivered, and any gap or duplicate—without pretending delivery means playback."
- **useful because:** Today the system has separate evidence in pendant-originated pipeline events, relay jobs, Mac logs, and generated audio, but the owner cannot answer the basic question “was that exchange actually completed?” A reconciled chain-of-custody receipt would expose silent LTE drops, stale queued replies, duplicate forwarding, and the crucial distinction between rendered, downloaded, and physically played audio.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux → unified
- **model tier:** Use a cheap background model (gpt-5.6-luna or equivalent) only to reconcile already-structured events; reserve gpt-realtime-2.1 for the live turn and do not resend raw audio to the reconciliation model.
- **latency:** Generate incrementally after a turn or reconnect; a preliminary receipt within 2 seconds and a finalized receipt after late device acknowledgements. Never delay live speech.
- **cost:** Low: one small structured reconciliation call per completed or recovered turn; dominated by event/context tokens, not audio. Raw PCM should remain out of the model path.
- **security:** Receipts may contain private speech metadata, timestamps, and logged-in-session references. Keep them in the existing authenticated D1/dashboard path, redact transcript text by default, hash audio rather than exposing it, and require confirmation before exporting or sharing a receipt.
- **missing:** A shared conversation-turn identifier propagated from pendant capture through relay job, Mac pipeline, TTS artifact, download, and local playback acknowledgement; A pendant-originated playback-start/playback-complete acknowledgement with monotonic sequence and interruption reason; A reconciler that joins late and duplicate events without treating server acceptance as physical delivery; A dashboard and spoken query that display confidence and explicitly label unknown stages

### "Keep me uninterrupted while I’m focused, but don’t make me miss something genuinely urgent: infer my current attention state from the pendant, Mac, calendar, and browser, hold ordinary notifications, and surface only urgency-qualified items with the reason they broke through."
- **useful because:** The owner currently gets disconnected alert handling and ordinary automation, but no single attention policy that understands whether they are in a meeting, presenting, coding, asleep, or merely away from the Mac. This would make the pendant a respectful gatekeeper instead of another notification channel, while preserving an auditable explanation for every interruption.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux → unified
- **model tier:** Use deterministic rules and a small background model for urgency classification and summarization; use gpt-realtime-2.1 only when the pendant actually speaks to the owner.
- **latency:** State changes within 5 seconds of a Mac/calendar/browser signal; urgent alert decision within 2 seconds; ordinary alerts can wait for a scheduled digest.
- **cost:** Low to moderate: mostly event filtering and one small classifier call per candidate alert; no audio or page contents need leave the Mac unless required for classification.
- **security:** This observes foreground apps, meeting times, browser account notifications, and possibly presence patterns. Keep raw page text and app titles local where possible, send only a sensitivity-tagged urgency fact to the relay, provide a visible pause switch, and never let the classifier bypass explicit safety categories without a user-defined policy.
- **missing:** A shared attention-state contract with states such as available, focused, meeting, asleep, and away, including source, confidence, expiry, and user override; A unified notification inbox that accepts Mac, browser, relay, and pendant events with urgency, sensitivity, deduplication, and quiet-hours metadata; A local browser notification reader that can classify urgency without uploading private page contents; A pendant acknowledgement protocol distinguishing surfaced, heard, dismissed, and deferred alerts


## Changes it proposed to its own stack

### `hardware` — Add a low-power ERM/LRA haptic actuator driven by a protected GPIO, plus a tiny 3-axis accelerometer with wake-on-motion and interrupt, to the pendant enclosure. Define firmware events for worn/removed, deliberate pickup, double-tap acknowledgement, and haptic patterns; retain the existing single button as the explicit conversation control.
- **owner gets:** The owner would receive and acknowledge alerts without looking at a screen or speaking aloud, and the system could stop claiming that an alert was noticed merely because it was downloaded. It would also avoid loudly interrupting meetings and make offline-held alerts discoverable through a tactile pattern.
- effort: Moderate hardware revision and enclosure work; add a small driver, calibration flow, and event schema. Validate false positives during walking, charging, and pocket carry.  ·  risk: Extra current can shorten battery life; motion sensing may misclassify handling as acknowledgement; vibration could be missed in a bag. Recover with conservative thresholds, explicit button fallback, battery-aware haptics, and an owner-test calibration mode.
- cost: Approximately $3–8 in components and PCB/enclosure changes at prototype volume. Haptic bursts are brief but materially higher than idle draw; accelerometer wake current should be in the low-µA range.  ·  latency: Sub-100 ms local acknowledgement and immediate tactile alerting, avoiding LTE round trips. No model latency for basic patterns.
- security: Motion and wear state are sensitive presence signals. Keep raw sensor data on-device, export only coarse state with explicit retention, and never infer location from it.
- depends on: A firmware event schema for local acknowledgement and worn-state transitions; Relay/pipeline reconciliation that distinguishes downloaded, surfaced, heard, and acknowledged; A user-configurable haptic policy for quiet hours and sensitive alerts


## What it asked for

_Nothing._
## Its own summary

Recorded three new items: an end-to-end conversation completion receipt, cross-surface attention-aware interruption gating, and a hardware revision adding haptics plus motion sensing for reliable offline alert acknowledgement. Each identifies missing protocol or hardware work rather than claiming existing routes are sufficient.

**Biggest unknown:** The backlog may contain a closely related attention/notification or haptic proposal not visible in its abbreviated listing; the new entries were framed around the unfilled cross-node acknowledgement and attention-state contracts.

