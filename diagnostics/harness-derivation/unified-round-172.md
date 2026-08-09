# Harness derivation — unified — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — AI Pendant Agent now has Accessibility and Screen Recording granted; input reachability is verified, Safari browser bridge is online, relay reachable, and both USB-connected chips are physically present though pendant remains unregistered with LTE.
  - evidence: GET /ops/status and GET /observe on 2026-08-08: accessibility.trusted=true, screenRecording.granted=true, inputReachability.status=verified, browser.online=true, relay.reachable=true; established hardware context names both serial devices.

## Capabilities it proposed

### "“If an action needs approval, stage it so I can hear exactly what will happen on the pendant, approve it with the pendant’s deliberate hold, and know it either executed once or was cancelled—never silently disappear.”"
- **useful because:** Today the system literally says “Waiting for your approval on the dashboard” while no approval control or durable relay half exists. This closes the owner-facing safety loop across relay, Mac, browser, and the already-accepted physical_transaction_approval_latch.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short spoken readback and confirmation turn; deterministic code for digest/nonce/expiry and execution; background planner only to summarize a complex plan.
- **latency:** Stage/readback under 2 s; physical approval receipt under 1 s when linked; execution status spoken within 3 s. No approval is assumed if the pendant is offline.
- **cost:** Usually <$0.01 per staged action; dominated by one short realtime turn, with no model cost for cryptographic verification or receipts.
- **security:** The relay must persist the approval record, bind it to plan digest and world fingerprint, enforce expiry and deliveredAt, and separate approval authority from execution credentials. Never send page contents or secrets to the pendant. A held approval must be idempotent and rejected on nonce reuse, plan change, world movement, or expired lease.
- **missing:** Implement the APPROVAL_STORE_CONTRACT in the relay/D1 rather than leaving it as documentation; Deliver the readback on the owner’s next pendant conversation (unprompted push is unavailable) and mark deliveredAt; Wire physical approval/cancel events into the relay and execute only after verification; Add a real dashboard approve/status view as a secondary surface, not the sole path; Close ordinary action ledgers and add a relay job lease before treating staged work as resumable

### "“Finish that task even if the Mac sleeps or the browser disappears, but do not repeat an email, purchase, or other one-shot action.”"
- **useful because:** A relay job can remain processing for up to 24 hours with no lease, while browser leases are not swept and local ledgers are falsely reported as interrupted. The owner needs a truthful outcome instead of a task that silently stalls or replays a one-shot side effect.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic lease/reconciliation engine; background model only when a human-readable recovery explanation is needed; realtime for a concise pendant status update.
- **latency:** Detect a dead Mac/browser within 45–90 s; requeue idempotent/additive work within 2 min; mark unrepeatable work “needs owner” immediately rather than retrying.
- **cost:** Negligible model cost for normal operation; <$0.01 only for an exceptional spoken recovery explanation. D1 writes and polling dominate.
- **security:** Lease ownership must be opaque and authenticated; stale workers cannot commit after lease expiry. Resume gates on replaySafety (idempotent/additive only), not reversibility. Unrepeatable/unknown steps become blocked with an explicit owner decision. Preserve receipts and never expose sensitive parameters in pendant alerts.
- **missing:** relay_jobs lease_until, lease owner, and expiry/requeue sweep modeled on routine leases; orchestrator closeLedger call so completed plans are not false positives; startup reconciliation that calls existing planResume safely rather than executing every historical open ledger; browser bridge supervisor invocation so 45-second command leases are actually swept; A status surface that sends the final stalled/recovered/blocked state to the pendant inbox

### "“Before an important call, test the actual microphone, 24 kHz downlink, ESP32/Bluetooth bridge, and LTE contention, then tell me in plain language whether I can trust the next conversation.”"
- **useful because:** The diagnostic fixture exists as an explicitly triggered engineering test, but there is no owner-facing invocation or verdict. This turns the shipped acceptance measurements into a one-command preflight on the real USB-connected hardware, without adding a test to the latency-sensitive hot path.
- **path:** pendant → mac-terminal → relay-realtime → dashboard
- **model tier:** Deterministic synthetic audio and counter checks; background model only to phrase the result; realtime is unnecessary unless the owner asks by voice and needs a short reply.
- **latency:** Run in under 20 s with a progress indicator; fail closed if any direction is not measured. Report HEALTHY/DEGRADED/FAILED plus the exact failing counter.
- **cost:** Near-zero model cost; local serial and relay test traffic dominate. A 20-second test consumes modest LTE data and should require explicit owner invocation.
- **security:** Synthetic fixtures must never record room audio or persist test PCM. Mark test traffic so it cannot be mistaken for a real conversation. Do not claim LTE health when the pendant is only USB-connected; report transport coverage explicitly.
- **missing:** Expose s16-dbfs audio_path_diagnostic_fixture through a safe owner-triggered route; Mac serial driver for the currently connected nRF9160 and ESP32 boards; A relay test mode that injects controlled contention/loss and correlates bridge acknowledgements; A compact spoken/dashboard verdict with measured sample rate, frame continuity, clipping, mic drops, tx starvation, and bridge buffer safety; Explicit distinction between USB-only, relay-connected, and full LTE coverage

### "“During a meeting, let me privately ask the pendant for a quick summary, fact check, or suggested reply without speaking to the room or changing what the meeting participants hear.”"
- **useful because:** The pendant is currently a conversation endpoint, while the Mac and browser can reach the meeting session but cannot provide a private, turn-bounded whisper channel. This would give the owner an entirely new ability: participant audio stays in the meeting, the owner’s deliberate pendant request goes to the assistant, and the answer returns only to the owner’s ear.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime for low-latency whisper exchanges; a cheaper background model for rolling meeting notes and retrieval; deterministic audio routing and mute state around both.
- **latency:** Owner request starts within 250 ms of a deliberate button action; concise whisper response within 2–4 s; never inject assistant audio into the meeting path.
- **cost:** Approximately $0.02–$0.10 per whisper depending on duration and model; meeting-length transcription and retrieval dominate cost. Explicit whisper mode avoids processing when inactive.
- **security:** Require an unmistakable local whisper-mode latch and visible dashboard indicator. Do not record or transmit meeting audio until the owner deliberately enables the session; keep participant audio ephemeral unless separately saved. Bind the browser target to one explicitly selected meeting tab, redact credentials, and fail closed if routing cannot prove that output is private.
- **missing:** A browser integration that identifies and binds one meeting tab’s media/session without granting the assistant arbitrary tab access; A Mac audio-router endpoint that can receive meeting audio while keeping assistant output out of the meeting’s playback device; A pendant whisper-mode firmware/session state with a local enter/exit indication and bounded turn counter; Relay session semantics for ephemeral meeting context, separate from ordinary conversation history; A privacy receipt proving which audio direction was captured, where it went, and that whisper output was not injected into the meeting

### "“Give me a single, chronological account of what you did across my Mac, browser, relay, and pendant while I was away— including blocked, failed, and never-attempted work—without making me inspect four dashboards.”"
- **useful because:** Today evidence is fragmented across jobs, pipeline events, browser results, and device receipts. A unified owner-facing account would distinguish intent, dispatch, external acceptance, physical delivery, and actual playback instead of presenting a misleading success label.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic event join and state machine; background model only to compress the timeline into a spoken summary. No realtime model needed unless the owner asks live.
- **latency:** Assemble a 24-hour timeline in under 2 s; speak a three-sentence summary in under 5 s; preserve drill-down receipts on demand.
- **cost:** Near-zero for normal queries; storage/indexing dominates. Optional summarization costs <$0.01 per digest.
- **security:** Use opaque IDs and redact command parameters, page contents, tokens, and audio. Preserve provenance and confidence for inferred states. Never turn a missing receipt into a success.
- **missing:** A shared event identity and clock model across relay, Mac, browser, pendant, and bridge; A joiner that correlates pipeline events, action receipts, browser command results, audio delivery acknowledgements, and physical events; Explicit terminal states for not-attempted, blocked, expired, delivered, heard, and unknown; Retention and deletion controls for the resulting timeline; Dashboard and pendant readback views

### "“If my Mac or browser is lost, let me hold the pendant and revoke this device’s browser sessions and relay access immediately, then tell me exactly what was cut off.”"
- **useful because:** The existing privacy latch stops local capture and playback, but it does not revoke remote browser sessions, relay credentials, queued commands, or Mac execution authority. A physical, offline-safe revocation path would remain useful when the dashboard and Mac are no longer trustworthy.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Deterministic revocation and receipt processing; realtime only to speak the compact result after the link returns.
- **latency:** Local pendant latch response within one audio frame; relay revocation within 5 s after reconnect; stale browser commands rejected immediately on the next poll.
- **cost:** Negligible model cost; a few authenticated relay writes and browser heartbeats dominate.
- **security:** The revocation credential must be device-bound and stored separately from the ordinary bearer token. Support a local offline decision retained until reconnect, monotonic anti-replay counters, and an unmistakable LED/haptic pattern. Revoke browser command leases, pending jobs, relay session tokens, and Mac bridge authority without deleting evidence needed for audit.
- **missing:** A device-bound revocation key and relay endpoint that accepts the pendant’s physical revocation event; Relay-side token/session epoch invalidation and pending-command cancellation; Browser bridge enforcement of a revocation epoch before polling or posting results; Mac bridge quarantine that refuses new work while quarantined; A post-reconnect revocation receipt and recovery ceremony requiring deliberate local action


## What it asked for

_Nothing._
