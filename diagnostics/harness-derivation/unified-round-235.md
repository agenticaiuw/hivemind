# Harness derivation — unified — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the answer I missed after the connection dropped—don’t repeat what I already heard.”"
- **useful because:** Relay acceptance is not playback, and playback is not hearing. A durable delivery cursor lets a reconnect resume at the first unacknowledged audio boundary instead of restarting an answer, duplicating speech, or silently losing it.
- **path:** relay-realtime → pendant → mac-planner → mac-vision
- **model tier:** Deterministic cursor/reconciliation logic; background model only to summarize an answer that expired, never to decide byte ranges.
- **latency:** On reconnect, reconcile in under 500 ms and begin from the first missing 60 ms frame; if the cursor is ambiguous, stop and ask rather than replaying.
- **cost:** Negligible model cost; bounded relay retention and approximately 4 KB device metadata per 32 delivery records dominate.
- **security:** Bind cursors to conversation, artifact ID, and monotonic sequence; reject stale/replayed ACKs; retain PCM/Opus only under the existing delivery-retention policy and encrypt relay storage. Never infer 'heard' from download completion.
- **missing:** A relay-owned resumable audio manifest with chunk hashes and expiry; Pendant/bridge emission of playback-start, playback-finish, interruption, and bridge-ack events into the existing bounded delivery ACK queue; A reconnect reconciler that requests only missing ranges and emits a user-visible receipt

### "“Stage that browser or Mac action, tell me exactly what will happen, and let me approve it by holding the pendant button.”"
- **useful because:** The current blocked-plan path says it is waiting for approval but discards the actionable handoff. This closes the loop: the browser/Mac plan remains staged, the pendant shows the exact transaction, and a deliberate physical approval authorizes only that unchanged plan.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard-ux
- **model tier:** Planner tier for the action plan; deterministic digest/world checks and execution; realtime only for the spoken readback.
- **latency:** Stage and speak a bounded plan in under 3 seconds; after the physical hold, execute within 2 seconds. Expire unattended approvals after 30 minutes.
- **cost:** One planner call for ambiguous requests; negligible deterministic verification cost. Relay durable approval state and receipts dominate.
- **security:** Bind approval to plan digest, world fingerprint, nonce, expiry, and owner session. Physical approval must never carry secrets or page contents. If the plan/world changes, expiry elapses, or delivery was not confirmed, refuse rather than guessing; keep approval and execution credentials separate when possible.
- **missing:** Implement the relay half of APPROVAL_STORE_CONTRACT and make approval state durable; Route blocked plans into prepare/readback instead of discarding awaitingApproval; A delivery path that records spoken readback before accepting approval, plus the existing physical_transaction_approval_latch event consumer; A real dashboard pending/approve status and an orchestrator closeLedger call so completed plans are not falsely resumable

### "“When I reconnect, give me one honest continuity card: what I said, what you heard, what the Mac finished, and what still needs me.”"
- **useful because:** A dropped link currently leaves the owner to guess whether a turn was captured, transcribed, acted on, or lost. This is a turn-level reconciliation, not audio replay: it joins pendant capture events, relay job receipts, Mac workbench handoff, and browser results into a short owner-facing state card with explicit unknowns.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic event join first; background model only compresses already-proven facts into a short card, with no invented completion claims.
- **latency:** Render within 2 seconds of reconnect for the last 10 minutes of activity; if evidence is incomplete, show UNKNOWN immediately rather than waiting for a model.
- **cost:** Low: bounded event query and one small summarization call only when there are more than three evidence items; storage is bounded by turn IDs and receipts.
- **security:** Bind every statement to a conversation/turn nonce and source receipt. Redact browser page content and sensitive parameters; expose only action titles and outcomes. Never turn missing telemetry into success.
- **missing:** A shared turn correlation ID propagated from pendant capture through relay pipeline, Mac job, and browser command; A read-only join route that returns evidence candidates plus explicit missing-source states; A reconnect trigger and pendant-readable compact card format; the card must remain available until acknowledged

### "“If my flight, delivery, or appointment changes, keep watching it, tell me on the pendant, and prepare the next steps—but never send or change anything without my approval.”"
- **useful because:** This would turn the hive into a bounded personal operator rather than a collection of one-shot actions: browser sessions observe the source of truth, the relay survives sleep, the Mac prepares calendar/messages/files, and the pendant provides the interruption and approval surface.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard-ux
- **model tier:** Background model for extracting the monitored condition and proposing next steps; deterministic event matching, expiry, and approval enforcement; realtime only for a genuinely urgent pendant notification.
- **latency:** Source changes detected within 2 minutes when a bound browser session is online; ordinary updates delivered at the next safe attention window; no more than one spoken interruption per monitored item until acknowledged.
- **cost:** Low-to-moderate background model cost per source change; browser polling and relay retention dominate. Avoid continuous realtime inference.
- **security:** Each monitor is explicitly bound to a site/session and expires. Store only the minimum change summary, never credentials or full page contents. Every proposed side effect carries an action digest and requires the physical approval latch or an existing owner-approved policy.
- **missing:** A durable monitor/subscription object with source binding, polling schedule, expiry, and deduplication; A relay event watcher that remains active when the Mac sleeps and queues a compact pendant alert; A staged multi-action plan that can be approved as one transaction while preserving per-action receipts; A policy editor for urgency, quiet hours, and whether a class of changes may auto-prepare but never auto-submit

### "“Show me everything this system is currently allowed to do on my behalf, where, until when, and revoke any one permission.”"
- **useful because:** Today authority is scattered across routines, browser sessions, approval leases, staged plans, queued jobs, and device state. A single authority map would let the owner answer ‘what can happen while I am away?’ and revoke a specific capability without deleting unrelated history.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard-ux
- **model tier:** Deterministic inventory and revocation; no model required except optional plain-language explanation.
- **latency:** Inventory under 1 second; revocation receipt under 3 seconds, with an explicit pending state if a sleeping surface must reconnect.
- **cost:** Negligible model cost; small bounded metadata index and revocation fan-out.
- **security:** The map must expose capability scope without secrets: domain/session labels, action classes, expiry, last use, and owner-granted basis. Revocation must be idempotent, kill queued execution, invalidate approval leases, and prevent stale browser commands from being replayed.
- **missing:** A common authority-grant schema spanning routines, browser sessions, staged approvals, jobs, and device inbox/outbox; A revocation endpoint with generation counters propagated to relay, Mac, browser, and pendant; A dashboard and pendant-readable summary that distinguishes observation permission from mutation permission; Receipt evidence proving revocation converged on every online surface

### "“Tell me the exact local time of anything I schedule, and label it honestly when I am traveling—without silently moving my routines.”"
- **useful because:** The Mac zone is authoritative for firing routines, while the owner’s physical location is unknown. This gives the owner a clear distinction between ‘fires at 7:00 America/New_York’ and ‘you are currently elsewhere,’ preventing dangerous silent timezone reinterpretation.
- **path:** mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Deterministic timezone and schedule logic; background model only for parsing ambiguous natural-language time requests.
- **latency:** Immediate confirmation for creation or edits; routine firing remains scheduler-precise with no model in the execution path.
- **cost:** Negligible model cost for explicit timezone requests; small persistent preference and audit metadata.
- **security:** Never infer a pendant timezone from its zoneless clock or from the Mac. Show the named IANA zone on every schedule confirmation, require explicit owner action to change it, and preserve the prior schedule when a travel/location signal is uncertain.
- **missing:** A first-class owner timezone preference distinct from the Mac execution zone; Schedule responses and pendant speech that always include the effective IANA zone for ambiguous times; An explicit travel/location label that changes presentation only unless the owner separately changes routine zone; Tests covering DST transitions, zoneless pendant timestamps, and Mac sleep/wake catch-up


## Changes it proposed to its own stack

### `relay` — Add a delivery-cursor reconciler for downlink audio: persist per-artifact chunk hashes, accepted playback boundaries, expiry, and a monotonic ACK watermark; on reconnect return only the missing range and emit a final heard/not-heard receipt.
- **owner gets:** A dropped link no longer makes the pendant repeat half an answer or lose the rest; it can continue naturally from the point the owner actually heard.
- effort: Medium-high: relay schema/store changes, firmware/bridge event plumbing, reconnect tests under loss and jitter, and integration with the existing delivery ACK queue.  ·  risk: Bad cursor reconciliation could skip speech or replay it. Default to replaying the smallest uncertain 60 ms frame and expose an explicit gap receipt; expire abandoned artifacts rather than retaining them indefinitely.
- cost: Low compute/model cost; bounded encrypted relay retention proportional to active responses.  ·  latency: Adds one manifest/cursor lookup on reconnect, target under 500 ms; no steady-state audio-path cost.
- security: Chunk hashes and conversation-bound opaque IDs prevent cross-session mixing; retention and deletion rules must apply to the manifest and audio together.
- depends on: audio_delivery_ack_queue; duplex_audio_congestion_guard; hardware-verified 24 kHz / 60 ms framing


## What it asked for

_Nothing._
