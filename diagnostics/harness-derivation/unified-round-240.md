# Harness derivation — unified — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Show me every fact you inferred about me, tell me what source supports each one, and let me erase exactly one."
- **useful because:** The owner currently cannot see facts extracted into facts.json/context graph, so cannot exercise the stated deletion policy. This makes unrequested memory the highest privacy risk. A provenance-backed list and one-item erase would make memory accountable rather than invisible.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** background for indexing and provenance joins; realtime only to explain the selected fact aloud
- **latency:** List in under 2 s from local index; erase acknowledgement under 3 s, with off-machine replication reported as pending rather than falsely complete.
- **cost:** Low: deterministic joins and hashing dominate; one short realtime utterance only when spoken.
- **security:** Never expose secret-valued facts by default; require explicit owner selection for deletion. Delete the extracted fact, derived copies, and evidence capsule, but preserve job history. Relay/D1 and R2 deletion must return requested-and-pending until confirmed.
- **missing:** owner-facing fact inventory route with stable fact IDs and provenance capsules; single-item erase transaction spanning facts.json, context graph, and relay replicas; dashboard/pendant presentation of pending remote deletion

### "Pause all spoken briefings and routine audio until tomorrow morning, without deleting or losing the scheduled work, then resume them automatically."
- **useful because:** The owner travels and has several daily routines that can produce overlapping spoken output. There is no single attention hold that preserves scheduled work while suppressing delivery. A temporary, visible hold avoids deleting routines or silently losing results, and the Mac timezone remains authoritative for the expiry.
- **path:** relay-realtime → mac-planner → pendant → dashboard-ux
- **model tier:** deterministic background scheduler; no expensive model needed except an optional one-sentence confirmation
- **latency:** Latch acknowledgement under 1 s; all queued audio delivery suppressed immediately; automatic release at the next Mac-local morning boundary.
- **cost:** Negligible: one durable hold record and scheduler checks; no model call required.
- **security:** This must suppress playback/delivery, not erase jobs or audio receipts. Show exact start and expiry in America/New_York/Mac-local time, preserve urgent physical safety/transaction approval signals, and require an explicit release if the owner changes their mind. Do not infer the owner's travel timezone.
- **missing:** durable routine-delivery hold with an expiry and owner-visible state; relay scheduler and pendant inbox checks that honor the hold; resume receipt proving no scheduled jobs were deleted or duplicated

### "I missed what happened while briefings were paused—give me one catch-up summary of completed routine results, and mark only those results as reviewed without rerunning anything."
- **useful because:** A delivery hold should not force the owner to replay several audio items or rerun routines. The system already records jobs and briefing artifacts, but lacks a safe read-only aggregation that turns them into one catch-up while preserving each source receipt and avoiding duplicate execution.
- **path:** relay-realtime → mac-planner → pendant → dashboard-ux
- **model tier:** background model over a deterministic, bounded result set; realtime only for the final spoken summary
- **latency:** Under 5 s for up to 24 hours of held results; immediately refuse or paginate beyond the bound rather than silently omit items.
- **cost:** Low: one summarization call over compact extracted results; no audio regeneration unless the owner explicitly asks.
- **security:** Only include artifacts addressed to this owner and within the hold window. Mark each source complete/failed/partial, preserve original timestamps and receipts, and make 'reviewed' idempotent. Never rerun an external action as part of catch-up.
- **missing:** read-only held-result aggregation keyed to a delivery-hold window; review acknowledgement that does not mutate job execution state; pendant playback item linking the summary to source receipts


## Changes it proposed to its own stack

### `integration` — Add a cross-surface 'source-backed answer' envelope for owner questions: relay assigns a request ID, Mac/browser workers attach bounded evidence references and timestamps, and the pendant speaks only the conclusion plus an optional short evidence cue. Persist the evidence references with the job receipt, not raw page contents or audio.
- **owner gets:** When the system says a reading-list item, file, routine result, or device event exists, the owner can immediately ask 'based on what?' and receive a trustworthy answer instead of an unsupported assertion. It also makes repeated failed browser requests diagnosable without exposing unrelated logged-in content.
- effort: Medium: define an evidence-reference schema, propagate request IDs through relay jobs and Mac/browser results, and add a compact pendant response formatter.  ·  risk: Stale or partial evidence could sound authoritative. Every answer must state source and age, mark missing evidence, and never synthesize a success from a timed-out worker. Recovery is to return the raw receipt/status for inspection.
- cost: Small storage and serialization overhead; lower model cost because evidence selection is deterministic and summaries can be shorter.  ·  latency: Adds roughly tens of milliseconds for envelope assembly; no extra model call for ordinary answers.
- security: Positive if references are capability-scoped and redacted; never copy page secrets into relay or pendant. Browser evidence must remain bound to the originating tab/session.
- depends on: A typed cross-surface receipt join (existing GET /jobs/:jobId/receipts plus browser result records); browser_identity_attestation request already pending; Owner-facing display or spoken command to request evidence details

### `firmware` — Give every pendant-originated control event (privacy-latch transitions, moment marks, physical approvals, and delivery acknowledgements) a device-bound monotonic event counter and authenticated envelope, with a compact key identifier and boot-generation field. The relay rejects reused counters, records gaps, and exposes the authenticated event chain to Mac/browser receipts; non-sensitive events may queue offline and upload later.
- **owner gets:** The owner can trust that a spoken 'privacy is on', approval, or 'you heard this' status came from the pendant they are wearing rather than a stale relay replay or an uncorrelated Mac claim. Gaps become visible instead of silently turning a link outage into false certainty.
- effort: Medium-high: protected key storage or a secure-element integration, firmware envelope and counter persistence, relay verification, and receipt propagation across Mac/browser jobs.  ·  risk: Counter wear, reset, or key loss could strand events. Use boot-generation plus a recovery ceremony that requires the physical transaction latch; never silently reset counters. During verification outage, fail closed for approvals/privacy claims and label ordinary telemetry unverified.
- cost: Firmware flash/RAM and a small persistent counter write; optional secure element roughly $1–3 BOM and milliwatts only during signing, with no model/API cost.  ·  latency: Sub-millisecond envelope creation on the nRF9160; relay verification adds a small network/server step, not audio-path latency.
- security: Strongly improves provenance and replay resistance, but introduces key provisioning, rotation, backup, and recovery obligations. Never transmit private keys or raw audio; bind signatures to event type, session, and payload hash.
- depends on: A provisioned device identity/key store (secure element or protected modem storage); Relay event verification and counter-gap persistence; Joining pendant event IDs to existing audio_delivery_ack_queue and physical_transaction_approval_latch receipts


## What it asked for

_Nothing._
## Its own summary

This round recorded three owner-facing additions: (1) transparent, provenance-backed listing and deletion of inferred facts without deleting action history; (2) a durable temporary hold for routine spoken delivery that preserves scheduled work; and (3) a bounded catch-up summary that marks held results reviewed without rerunning jobs. I also recorded a cross-surface evidence envelope so answers can expose source and age without leaking page contents. The existing routes are mostly present; the missing work is the connective policy/state between them.

**Biggest unknown:** Whether the owner wants routine holds to suppress only spoken playback or also pendant inbox surfacing. I did not invent that policy. The other concrete blockers remain implementation: relay persistence for the hold and deletion request, typed cross-surface receipt joins, and the already-pending browser identity attestation.

