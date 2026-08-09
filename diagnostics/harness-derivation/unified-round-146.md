# Harness derivation — unified — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this sensitive thing for me, but don’t commit it until I physically approve it on the pendant; if the Mac or browser drops, recover without duplicating the action.”"
- **useful because:** This would make the wearable a real safety boundary for actions that span the Mac and authenticated browser, instead of promising approval and silently discarding blocked plans. The owner gets a durable staged transaction, a visible physical decision, and honest crash recovery.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for staging and recovery analysis; realtime only to explain the pending transaction in the next conversation
- **latency:** Stage in under 3 s; physical approval receipt under 2 s after reconnect; recovery decision on worker restart under 5 s
- **cost:** ~$0.01–$0.05 per staged action, dominated by planner/model calls; relay persistence and receipts are negligible
- **security:** The relay must persist the action-bound digest, world fingerprint, nonce, expiry, and delivery state; never send page secrets to the pendant. Approval must be least-privilege and distinct from the executor credential. Require explicit confirmation for irreversible-write, off-machine, and uncontained tiers; stale or changed world must refuse rather than guess.
- **missing:** Implement the APPROVAL_STORE_CONTRACT on the relay and connect it to the existing prepare/approve routes; Add a delivery path that can present pending approval on the owner’s next conversation (the pendant cannot receive unprompted push today); Close ordinary orchestrator ledgers correctly and add relay job leases/requeue before any automatic recovery; Bind the accepted physical_transaction_approval_latch events to approval records and consume each nonce exactly once

### "“Before I rely on the pendant for an important conversation, run a short hardware confidence check and tell me whether the mic, 24 kHz codec, modem path, bridge, and headphones are all actually healthy.”"
- **useful because:** The owner currently has to interpret raw counters and hope the path is healthy. A deliberate USB-triggered check would catch the exact classes of failures that previously caused silence, distortion, and preamble clicks, and would produce a compact pass/degraded/fail decision before a real conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background/deterministic; no realtime model is needed except optional spoken explanation
- **latency:** 30–60 s for the complete fixture; show progressive results within 2 s and never run automatically on the audio hot path
- **cost:** Near-zero API cost; one synthetic audio fixture and local measurements dominate
- **security:** Use synthetic tones and speech-shaped fixtures only; never retain room audio. Mark every result with firmware/build IDs and monotonic sequence numbers. A failed check must recommend a safe fallback, not silently change the owner’s transport.
- **missing:** Actually wire the accepted audio_path_diagnostic_fixture to the USB fallback session and ESP32 bridge acknowledgement path; Add a bridge-side SBC/A2DP delivery receipt that distinguishes packet accepted by ESP32 from playback started and interrupted; Expose a signed, timestamped result bundle to the relay/dashboard and make the result readable through the existing pipeline records

### "“If I give you a clear instruction while the relay is down, remember the instruction—not the room audio—then carry it through the browser when connectivity returns and tell me exactly what happened.”"
- **useful because:** The pendant is already physically testable over USB even while LTE is unregistered, but today an offline conversation either disappears or becomes an audio memo. This would turn a deliberate spoken instruction into a durable, redacted intent that survives relay outage, executes only after the right browser session is reachable, and returns a receipt instead of silently losing the request.
- **path:** pendant → mac-bridge → relay → browser → dashboard
- **model tier:** realtime for the short offline transcription/confirmation; background for routing, deduplication, and later browser execution
- **latency:** Acknowledge capture locally within 1 s; enqueue a compact intent within 3 s; resume within 1 minute of relay/browser recovery, subject to approval and session reachability
- **cost:** ~$0.01–$0.08 per intent, dominated by transcription/planning; storage and relay polling are negligible
- **security:** Do not retain raw audio after transcription confirmation. Show the owner a concise normalized intent and destination before queueing when ambiguity or sensitivity is detected. Bind an idempotency key, origin sequence, expiry, target browser binding, and approval requirement; never replay unrepeatable actions. Encrypt the local queue and make deletion auditable.
- **missing:** A local USB intent queue distinct from the existing audio OUTBOX, with crash-safe records and explicit owner deletion; Relay-side intent ingestion and a lease/requeue worker rather than treating a disconnected Mac job as permanently processing; A browser-session availability trigger and action-bound approval handoff using physical_transaction_approval_latch; A receipt that joins transcription, relay acceptance, browser result, and final owner acknowledgement

### "“Show me, for this conversation, exactly what audio, transcript, plan, browser content, and receipts were retained on each surface—and delete the parts I choose everywhere they exist.”"
- **useful because:** The owner cannot today answer the basic privacy question of where a conversation went after it crossed the pendant, Mac, relay, and browser. This would provide a human-readable data lineage view and execute a scoped deletion with per-surface receipts, rather than relying on a generic privacy latch that only stops future capture.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background/deterministic; use realtime only if the owner asks verbally during an active conversation
- **latency:** Lineage summary within 5 s; deletion receipts within 30 s, with unresolved offline surfaces explicitly marked pending
- **cost:** ~$0.01 per inspection/deletion request; storage indexing and authenticated reads dominate, not model inference
- **security:** Deletion must be bound to a conversation ID and authenticated surface manifest, never a broad filesystem or account search. Browser deletion must be limited to explicitly bound tabs/apps. Preserve only a minimal deletion receipt, not the deleted content. If a surface is offline, do not claim deletion—queue and report pending.
- **missing:** A cross-surface retention index that links capture, transcript, pipeline, relay job, browser exposure, and playback artifacts without storing extra audio; Typed deletion operations for each artifact class, including relay and browser records; An authenticated dashboard view showing retention state and deletion receipts; An owner-set retention policy, including whether audit receipts themselves may persist

### "“Before you tell me a task is done, prove that the result in the browser and on the Mac matches the exact outcome I asked for, and call out any contradiction instead of guessing.”"
- **useful because:** Today completion is fragmented: a relay job can succeed while a browser command fails, a page can change after inspection, or the action can produce a different result than the spoken commitment. The owner needs a pre-answer semantic and provenance check, not another optimistic “done.”
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for evidence collection and deterministic comparison; realtime only for the final spoken answer
- **latency:** Under 5 s for common checks; up to 20 s for multiple bound tabs/apps, with a concise pending state rather than a fabricated success
- **cost:** ~$0.01–$0.06 per verification, dominated by evidence extraction and one small comparison call
- **security:** Query only explicitly bound tabs/apps and the commitment’s permitted evidence scope. Return citations, timestamps, and confidence; do not expose unrelated page contents. A contradiction must block completion language and, where relevant, block subsequent dependent actions.
- **missing:** A typed join that combines commitment_evidence_query results with relay receipts, Mac receipts, and browser inspection results; A declared expected-outcome schema for common actions rather than free-form semantic guessing; A durable contradiction receipt linked to the original commitment and job; A policy for what evidence threshold permits the spoken word “done”


## Changes it proposed to its own stack

### `relay` — Implement durable relay job leases and the approval handoff loop: add lease_until/claimedBy/claimedAt to relay_jobs, atomically reclaim expired processing jobs, persist approval records keyed by the existing approvalStateKey, and expose a worker that delivers pending approval on the next authenticated conversation. Preserve planDigest/world fingerprint/expiry and reject changed or replayed transactions.
- **owner gets:** A Mac crash, browser disconnect, or relay restart would stop being an invisible dead end. Sensitive work would either complete once with a physical receipt or remain clearly pending/expired for the owner.
- effort: Medium: schema migration, D1/memory-store parity, worker sweep, and integration tests across prepare/approve/execute.  ·  risk: A bad lease could duplicate an action; default recovery must consult replaySafety and only auto-rerun idempotent/additive steps. Any ask/unknown/unrepeatable step blocks later steps and requires a new approval. Roll back by disabling reclaim and leave rows queued.
- cost: Low storage and worker CPU; roughly cents per thousand jobs, with model cost unchanged.  ·  latency: Adds at most one poll interval after recovery; normal execution unchanged.
- security: Improves least-privilege and auditability, but requires separate approval credentials or a clearly enforced approval boundary; never put page contents or secrets in relay approval payloads.
- depends on: orchestrator must call closeLedger for completed plans; accepted physical_transaction_approval_latch firmware events; next-conversation pendant delivery path; owner-defined retention/deletion policy

### `hardware` — Replace the ESP32 HUZZAH32 prototype bridge’s oversized fixed audio buffer with a measured, bounded jitter buffer and a small hardware-timed playback FIFO: keep the 24 kHz pendant/Opus timing untouched, resample only at the bridge’s required 31.25→44.1 kHz boundary, expose underrun/overflow and A2DP packet-delivery counters, and size the FIFO from observed SBC scheduler slack rather than a 44 kB buffer that can starve Bluedroid.
- **owner gets:** Fewer silent Bluetooth dropouts and a trustworthy answer to “did that sentence reach my headphones?” without sacrificing the shipped 24 kHz speech path.
- effort: Medium firmware work plus hardware-in-loop testing; if the HUZZAH32 cannot provide stable timing under SBC load, move the bridge role to an ESP32-S3 with more RAM/I2S DMA while retaining the same protocol.  ·  risk: A too-small FIFO creates clicks; a too-large one recreates silence from Bluetooth starvation. Recover with conservative fixed sizing and a compile-time fallback, and gate deployment on measured underrun rate and end-to-end latency.
- cost: Prototype software cost is low; an ESP32-S3 replacement is roughly $8–$20 and modestly higher power. No API/model cost.  ·  latency: Target under 120 ms added buffering; adaptive bounds must never grow without a cap.
- security: No new data leaves the device; counters should be opaque, sequence-bound, and avoid carrying audio content.
- depends on: accepted audio_path_diagnostic_fixture; audio_delivery_ack_queue amendments for bridge receipts; duplex_audio_congestion_guard profile reporting

### `integration` — Create a cross-surface outcome verifier that consumes a commitment ID, its declared expected outcome, relay/job receipts, Mac action receipts, browser inspection evidence, and pipeline/playback status, then emits one signed verdict: satisfied, contradicted, incomplete, or unverifiable. Make the verdict the only source allowed to produce owner-facing “done” language.
- **owner gets:** The owner gets honest completion reports. A browser failure, stale page, partial Mac action, or audio delivery problem becomes visible instead of being hidden behind a successful planner response.
- effort: Medium: define the expected-outcome schema, implement joins and timestamp/identity checks, add browser/Mac evidence adapters, and test deliberate contradiction cases.  ·  risk: Overly strict matching could report incomplete when the task genuinely succeeded. Recover by showing the conflicting evidence and allowing the owner to ask for a fresh inspection; never silently downgrade contradiction to success.
- cost: Low storage and compute; roughly one small comparison-model call only when deterministic matching cannot decide.  ·  latency: Adds 1–5 seconds to completion responses; can run asynchronously for low-risk tasks while suppressing premature completion speech.
- security: Evidence must remain scoped to bound tabs/apps and redact secrets. Signed verdicts should contain references and hashes, not page contents or raw audio.
- depends on: A commitment-to-expected-outcome record; Typed browser and Mac receipts with stable action IDs; Owner policy defining the evidence threshold for “done”


## What it asked for

_Nothing._
