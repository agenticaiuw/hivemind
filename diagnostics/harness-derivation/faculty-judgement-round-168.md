# Harness derivation — faculty-judgement — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Pretend the pendant has lost LTE, run a 10-minute link-loss rehearsal over USB, and tell me exactly what survived, what was queued, and whether replay is safe.""
- **useful because:** The hardware is physically present but unregistered, so this gives the owner confidence in offline behavior today rather than a false green LTE test. It exercises the real pendant, Mac bridge, relay queues, stop latch, and delivery acknowledgements together.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Background model for the test plan and receipt summary; realtime only for the owner's spoken start/stop interaction.
- **latency:** Start acknowledgement under 2 seconds; rehearsal runs asynchronously for up to 10 minutes; final report under 30 seconds after reconnect/replay.
- **cost:** Usually <$0.03 per rehearsal; model cost is dominated by the final anomaly summary, not the serial replay.
- **security:** Use synthetic payloads by default, never owner speech; USB serial logs and ACK metadata remain local unless the owner explicitly asks for a relay report. A stop-latch event must abort the rehearsal. No external filing without confirmation.
- **missing:** A Mac USB-serial harness that can deliberately blackhole LTE-equivalent delivery while preserving authenticated pendant session semantics; A deterministic replay simulator for the signed stop token, audio ACK queue, and duplicate events; A single rehearsal receipt joining relay job ID, Mac job ID, UART cursor, and pendant event IDs

### ""Forget everything this website taught you about me, and show me a receipt proving it is gone from the browser, Mac memory, graph, and relay.""
- **useful because:** Today revoking a browser evidence capsule does not remove derived facts or context-graph copies. The owner needs a real, source-scoped privacy action rather than a misleading tombstone that leaves usable claims behind.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Background model only for identifying linked provenance; deterministic deletion and verification should not spend realtime tokens.
- **latency:** Preview in under 3 seconds; deletion and verification within 15 seconds, with explicit partial-failure status.
- **cost:** <$0.01 when links are indexed; cost is dominated by one verification pass if a large graph must be scanned.
- **security:** Default to preview and require confirmation for destructive deletion. Never speak the deleted content. Scope by origin/capsule IDs, preserve minimal tombstones and audit hashes, and fail closed if a store cannot be reached.
- **missing:** Persist capsuleId/source links on derived memory facts and context-graph entities; A cross-store forget executor that reaches browser provenance, facts, graph, fleet-memory retractions, and relay copies; A signed deletion receipt with per-store counts and an unresolved-items list

### ""Before you give me a morning brief, detect duplicate routines and untrusted empty sources, choose one canonical brief, and tell me what you skipped and why.""
- **useful because:** The owner currently has multiple overlapping daily briefs, and unauthorized EventKit reads can look like an all-clear calendar. This prevents duplicate audio and makes a missing permission audible instead of silently suppressing urgent information.
- **path:** relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Deterministic scheduler/reconciler for duplicate detection, permission provenance, and selection; cheap background model only to summarize the canonical result.
- **latency:** Decision under 3 seconds at scheduled time; one spoken sentence immediately, with the full provenance report available in the dashboard.
- **cost:** <$0.01 per run; most work is local route reads and hashing, not model inference.
- **security:** Read-only by default. Never delete a routine automatically; quarantine duplicates into a review list. Do not claim calendar silence when EventKit authorization is unknown. Sensitive mail/calendar content follows the existing redaction gate before audio.
- **missing:** A semantic routine deduper that compares commands, schedules, and output destinations; A scheduler hook that runs reconcile_personal_state before briefing generation; A canonical-brief lock/idempotency key shared by routine, relay job, audio artifact, and pendant delivery ACK

### ""That's wrong—remember the correction, show me the source you changed, and don't repeat the old claim in future briefs.""
- **useful because:** A spoken briefing is currently disposable: the owner can interrupt or note an item, but there is no durable, source-linked correction that updates future judgement. This turns trust repair into a one-sentence interaction across pendant audio position, relay provenance, and Mac memory.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime model binds the utterance to the active audio item; deterministic storage and suppression rules handle the correction; background model may reconcile competing sources later.
- **latency:** Acknowledge the correction within 1 second and persist a reviewable correction within 5 seconds.
- **cost:** <$0.01 per correction; one short realtime turn dominates.
- **security:** Never overwrite source evidence. Store the owner's correction as an assertion linked to the item and source, mark the old claim disputed rather than deleted, and require confirmation before the correction drives an external mutation. Spoken acknowledgement must omit sensitive quoted content.
- **missing:** A typed correction event and durable conflict-resolution rule in fleet memory or local facts; A link from audio item cursor/token to provenance and the future briefing planner; A user-visible state showing disputed, accepted, or unresolved corrections

### ""Only let my Mac or browser carry out an external action while my pendant is physically present; if it disappears, pause safely and tell me what was prevented.""
- **useful because:** A one-time approval is not enough: a stale browser session or unattended Mac can continue acting after the owner walks away. A continuously renewed, cryptographically bound pendant-presence lease would make physical proximity a live safety boundary across the wearable, Mac, browser, and relay.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic lease verification and fail-closed policy; realtime model only explains a blocked action in the owner's short spoken reply.
- **latency:** Presence loss detected within 2 seconds; reversible work pauses immediately; dashboard explanation under 5 seconds.
- **cost:** Near-zero model cost; small authenticated heartbeat traffic and local state only.
- **security:** The lease proves device possession, not the owner's identity or consent, so it must never replace physical transaction approval for irreversible actions. Bind it to a rotating session key, expire aggressively, and avoid logging location. USB is the current transport; LTE/BLE can be added later.
- **missing:** A pendant-to-Mac authenticated proximity lease with monotonic counters and replay resistance; Mac and browser execution gates that check the lease before every external-side-effect step; Relay handling for lease expiry, reconnect, and owner-visible blocked-action receipts

### ""Tell me what happened while I was away: which actions ran, which were blocked, what the pendant heard or played, and where the record is uncertain.""
- **useful because:** Today the owner can inspect isolated job, browser, pipeline, and catch-up records, but cannot obtain one honest absence interval with explicit gaps and cross-surface joins. This is a life-level answer, not another job status page.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic interval assembler first; background model compresses the verified timeline into one short spoken sentence and a cited dashboard view.
- **latency:** Generate a 30-minute absence report in under 10 seconds; spoken summary under 2 seconds after request.
- **cost:** <$0.02 per report; model spend is only the final compression.
- **security:** Default to local-only and redact message contents. Explicitly label inferred versus observed events, never turn missing telemetry into 'nothing happened,' and require confirmation before exposing private browser or mail details aloud.
- **missing:** A durable cross-surface event join keyed across relay, Mac, browser, and pendant (not merely telemetry metadata); An absence interval API that records observation gaps and clock uncertainty; A timeline renderer with provenance links and privacy-aware spoken summarization


## Changes it proposed to its own stack

### `memory` — Wire the existing shared fleetMemory writer from the Mac bridge, emitting only normalized preference/task/entity/event deltas after owner-approved interactions, with retraction events for corrections and source IDs retained in the projection.
- **owner gets:** When the owner corrects the pendant, the Mac, relay, and browser will actually learn the same bounded correction instead of each body reverting to its own stale memory.
- effort: Medium: one bridge call path plus schema migration verification and tests for retries, byte budgets, and retractions.  ·  risk: Duplicate or malformed events could pollute shared memory; use event IDs, fail-closed validation, and never replace inheritedText until a projection receipt verifies the write.
- cost: Negligible storage and one small relay write per event; no model cost.  ·  latency: A few hundred milliseconds after an interaction; do not block spoken acknowledgement on relay availability.
- security: Apply the existing three-class classifier and source/surface fields, but do not treat sensitivity as authorization. Emit redacted normalized values, never raw quotes or credentials.
- depends on: Apply relay_memory_events migration to the live D1 schema; Add capsule/source linkage to local facts before emitting derived claims; Define owner correction semantics for retract versus supersede

### `interaction` — Make every generated spoken brief item carry an opaque item token and provenance handle through synthesis, playback, interruption, and ACK; on a barge-in correction, freeze playback position, bind the utterance to that token, and resume only after the correction is durably queued or explicitly declined.
- **owner gets:** Saying “wrong” or “make a note of that” will act on the sentence they just heard, not whichever job happens to finish next, without forcing them to repeat a URL or title.
- effort: Medium-high: thread the token through audio generation and pendant delivery, then add a relay-side idempotent correction endpoint and Mac memory adapter.  ·  risk: A stale token could attach a correction to the wrong item; expire tokens quickly, return the item title/source on confirmation, and fail closed when cursor evidence is missing.
- cost: Tiny metadata overhead; one cheap model call only when the utterance is ambiguous.  ·  latency: Immediate pause; under 1 second to confirm the bound item; background persistence can complete asynchronously.
- security: Tokens reveal no content. Provenance details stay on the dashboard unless the owner requests them; spoken confirmation uses sensitivity-safe wording.
- depends on: Use the accepted spoken_status_interrupt primitive; Use audio_brief_item_action for pause/resume/create_note or append_to_draft; Use record_pendant_delivery_event for authoritative playback position; Use explain_action_provenance for source display

### `interaction` — Add a deliberate 'away mode' and 'present mode' state to the pendant's existing local privacy/stop control, with a signed presence lease consumed by Mac and browser policy. Away mode must not erase data or approve anything; it simply makes external side effects fail closed until the pendant returns and renews the lease.
- **owner gets:** Walking away from the computer becomes a real boundary: queued drafts can remain safe, while sending, purchasing, publishing, or changing accounts cannot continue unattended.
- effort: High: firmware state and signing, USB framing first, then Mac/browser middleware and durable receipts.  ·  risk: A dropped USB cable could interrupt legitimate work; provide a clear local indication and preserve reversible drafts, never silently retry a blocked mutation.
- cost: Tiny firmware/storage overhead; no recurring API cost.  ·  latency: One heartbeat interval, target under 2 seconds; no added latency while present beyond a local signature check.
- security: Strengthens fail-closed behavior without claiming presence equals consent. Lease identifiers must be opaque and logs must avoid location or microphone data.
- depends on: Accepted universal_stop_latch and physical_transaction_approval_latch semantics; A new authenticated USB serial lease protocol; Integration into autonomy_policy_evaluate and cross_surface_preflight


## What it asked for

_Nothing._
## Its own summary

Round 168 produced six proposals, including a cross-body “that’s wrong” correction flow and source-linked playback tokens, plus a USB link-loss rehearsal, privacy deletion cascade, canonical briefing integrity gate, and fleet-memory wiring. The recorder flagged several as close to existing backlog, so the genuinely distinct direction is the audio-item correction token and its interaction contract; the others should be treated as implementation amendments, not new products.

**Biggest unknown:** I still need owner decisions, not more infrastructure discovery: which timezone governs the owner personally (memory says America/Chicago while the Mac-authoritative routine zone is America/New_York), whether notification content may ever be spoken in public, and which trusted destinations may receive derived claims. I also need the owner to grant EventKit calendar/reminder access if trustworthy calendar briefs are desired; Accessibility/Screen Recording remain manually blocked.

