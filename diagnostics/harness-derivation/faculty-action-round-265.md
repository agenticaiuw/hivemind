# Harness derivation — faculty-action — round 265

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you send that message or submit that form, give me a short spoken summary and let me approve it from the pendant; if I do nothing, cancel it automatically.”"
- **useful because:** This makes high-risk computer actions understandable and safely finishable while walking: judgement composes the intent, Mac/browser performs only after approval, the pendant conveys a concise summary without receiving secrets, and faculty-perception verifies the postcondition. It is the single most useful end-to-end trust feature because it turns automation from silent delegation into a bounded transaction.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** realtime for the brief spoken summary only; background/cheap model for action classification and summarization; no model needed for verification
- **latency:** Summary in under 2 s; approval window 30 s; execution and independent verification under 10 s after approval.
- **cost:** One short realtime generation per risky action; verification and execution are otherwise local/route calls. Browser and Mac state reads dominate latency.
- **security:** Use the existing opaque transaction nonce, expiry, monotonic counter, and physical approval latch. The pendant receives only a redacted human summary and digest, never form secrets. Default to cancel on timeout, digest mismatch, stale browser session, or unverifiable postcondition.
- **missing:** wire the existing physical_transaction_approval_latch into browser/Mac execute orchestration; redaction policy that produces safe spoken summaries; a dashboard transaction timeline joining executor receipt and verify_operation_step provenance

### "“When I bookmark a moment, later tell me what was on my Mac and in my browser at that exact moment, and let me open the relevant note.”"
- **useful because:** A physical bookmark becomes a trustworthy cross-surface memory instead of an unlabeled timestamp. The pendant marks the moment, the relay orders the event, Mac perception captures host/browser state, and the owner gets a compact spoken or dashboard recap later.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for summarization and entity linking; realtime only when the owner asks to hear the recap
- **latency:** Bookmark acknowledgement under 200 ms; state snapshot within 2 s; recap available within 10 s.
- **cost:** One small background summarization per bookmark batch; storage and browser snapshot size dominate, with aggressive redaction and hashes by default.
- **security:** Capture only explicitly enabled apps/domains; default to hashes and titles, never page text or passwords. Bind each bookmark to a monotonic pendant event ID and observedAt timestamps, and label missing/stale surfaces rather than inferring them.
- **missing:** firmware bookmark event upload with monotonic timestamp and link correlation; Mac/browser snapshot endpoint that accepts the bookmark ID and returns redacted provenance; owner-configurable capture allowlist and retention

### "“I was away for an hour—tell me only what changed on my Mac and in my open browser sessions since I left.”"
- **useful because:** The owner gets a concise, actionable re-entry brief instead of a transcript or generic notification list. The relay schedules a baseline snapshot, Mac perception and browser sessions produce redacted change records, and the pendant can speak the digest hands-free when the owner returns.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for diff clustering and summarization; realtime only to speak the final digest
- **latency:** Baseline write under 2 s; incremental collection every 5 minutes; spoken digest ready within 5 s of request.
- **cost:** Low background summarization cost per diff window; storage and polling dominate. Keep only hashes/titles and changed fields unless the owner explicitly expands an item.
- **security:** Never infer presence from browser heartbeat. Bind the window to explicit owner start/stop times, report stale/offline surfaces, redact message bodies and page secrets by default, and require confirmation before opening or acting on a changed item.
- **missing:** a persistent cross-surface snapshot/diff store keyed by owner-declared time windows; browser and Mac change events with stable object IDs rather than only current snapshots; a return-brief route that can stream a compact digest to the pendant

### "“For every answer, choose the safest available place to speak it: private AirPods for sensitive content, the pendant for ordinary content, and ask me before using an open speaker.”"
- **useful because:** Today the system can deliver audio, but it cannot make a reliable privacy decision about where an answer will be heard. This would let the owner use automation in public without accidentally speaking messages, form contents, or personal data aloud, while preserving instant pendant replies for harmless status updates.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** cheap background classifier for sensitivity labels; realtime only for the answer itself; deterministic routing once the label is present
- **latency:** Route decision under 100 ms after the answer is classified; no extra audible delay for ordinary replies; sensitive replies wait up to 2 s for private-route confirmation.
- **cost:** Small classification cost per response; bridge control and short-lived routing metadata dominate, with no duplicate TTS generation.
- **security:** Classify before playback, fail closed when sensitivity or route availability is unknown, and never downgrade private content to an open speaker automatically. The pendant receives only the redacted label and route status. Require a deliberate physical confirmation to override a private-route failure; retain only route/audit metadata.
- **missing:** a sensitivity taxonomy attached to every generated response and action receipt; a verified private-output route between relay, ESP32 AirPods bridge, and the owner's paired AirPods; a route arbiter that can pause delivery, request physical override, and record where playback actually occurred; a firmware/bridge privacy status beacon that distinguishes private playback, pendant playback, and unknown


## Changes it proposed to its own stack

### `firmware` — Complete the already-defined device_playback reporter in the nRF9160 firmware and correlate each downloaded audio artifact to a pipeline/job ID: emit started, finished, interrupted, and checksum-mismatch events into the existing outbound queue; have relay delivery state advance from held_by_relay only on signed device receipts, never on download acceptance alone.
- **owner gets:** The system can honestly tell the owner whether an answer was heard, rather than claiming success when audio is merely waiting at the relay. Missed or interrupted answers become replayable and stale held responses stop accumulating invisibly.
- effort: Medium: wire reporter calls around the existing Opus playback lifecycle, persist a compact correlation record, add relay state transitions and an integration test for drop/retry/interruption.  ·  risk: A crash during playback can leave an unknown state; represent unknown explicitly and retry idempotently by event ID. Never convert missing telemetry into heard=true. Roll back by retaining current held_by_relay behavior.
- cost: Negligible model/API cost; a few hundred bytes of metadata per delivery and small relay storage overhead.  ·  latency: No audible-path delay; one receipt round trip (typically sub-second when connected) before status becomes verified.
- security: Receipts contain opaque artifact/job IDs, ranges/checksums, and event types only—not transcript or page content. Sign or MAC device events and reject duplicate/replayed counters.
- depends on: existing audio_delivery_ack_queue (s9-vtxc); existing offline_audio_delivery_retry (s10-qrm2); firmware playback reporter hooks and relay device_playback contract

### `integration` — Make audio delivery two-phase: classify and reserve an output route before rendering or releasing PCM. The relay issues a short-lived route lease (private AirPods, pendant, or explicit open-speaker approval); the bridge acknowledges the lease with device identity and privacy level; only then may the artifact become downloadable. A failed or stale lease cancels the release rather than silently falling back.
- **owner gets:** Sensitive answers will not be rendered into an audio artifact and then accidentally played through the wrong device. The owner gets a real privacy guarantee, not a best-effort label after the fact.
- effort: High: add route lease state to pipeline records, bridge capability/identity reporting, pre-TTS gating, expiry and recovery paths, and end-to-end tests for AirPods disconnects and relay retries.  ·  risk: A false offline/private report can delay ordinary speech; expire leases quickly and allow ordinary low-sensitivity responses to use the pendant. Never fall back for sensitive content. Roll back by disabling leases only for explicitly low-sensitivity responses.
- cost: Small metadata and control traffic; possible extra latency and occasional wasted classification, but avoid duplicate TTS by classifying before rendering.  ·  latency: Adds roughly 100–500 ms for route negotiation; sensitive responses may wait for private-device confirmation.
- security: Improves confidentiality by preventing unbound audio release. Device identity and route receipts must be authenticated; do not store raw audio solely for route retries.
- depends on: response sensitivity taxonomy; verified ESP32/AirPods route capability; pipeline delivery receipts and playback provenance


## What it asked for

_Nothing._
## Its own summary

Produced three new owner-facing capabilities and one concrete firmware change. The strongest is approval-gated, independently verified cross-surface transactions. I also proposed bookmark-linked context and a return-from-absence change digest. Live probing found Mac and Safari online with Accessibility/Screen Recording working, but the pendant remains offline. More importantly, pipeline state shows a real delivery-truth gap: 24 kHz audio is accepted by the relay and marked held_by_relay, while no device_playback event has ever been emitted. I proposed wiring that reporter and correlating playback receipts.

**Biggest unknown:** I still need an actual LTE-registered pendant and a verified firmware-to-relay playback event path. Until then, the system can prove relay acceptance but not that the owner heard anything. Product hardware also still needs the rotary encoder/second button before wheel-based interaction can be implemented.

