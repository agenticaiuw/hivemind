# Harness derivation — faculty-action — round 210

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “I’m leaving,” make the Mac safe: lock it, mute audio, and close only the browser tabs I explicitly marked private; then tell me through the pendant exactly what was changed and what could not be verified."
- **useful because:** A wearable can trigger a real departure routine without requiring the owner to find the Mac, while browser sessions and the Mac each contribute state the pendant cannot see. It reduces accidental exposure when leaving a desk and reports partial failure honestly.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** background for planning; realtime only to recognize the spoken command and return the short status
- **latency:** Plan under 1 s; execution and verification under 10 s; pendant outcome must distinguish verified, partial, and unknown.
- **cost:** Usually one cheap planner call plus 3–8 Mac/browser actions and verifier calls; roughly $0.01–$0.05 depending on planning context. Dominant cost is browser/Mac verification, not audio.
- **security:** Never infer private tabs from page contents alone: use an owner-maintained mark or explicit tab IDs. Locking is high impact and should require the existing physical transaction approval latch unless the owner explicitly configures this phrase as proactive. Do not transmit page contents to the pendant. A failed close must not be reported as success.
- **missing:** A durable owner-defined set of browser tabs/windows marked private; A lock-screen action with a verifiable postcondition in the Mac action manifest; A batch transaction wrapper that records per-step receipts and compensating actions

### "Stage this multi-step change and commit it only if every step can be verified: for example, update a browser form, save the resulting file, and send the message; if any step fails, undo the reversible steps and leave me a concise pendant status."
- **useful because:** Today the mind can plan and execute steps, but a partial workflow can leave the owner unsure what actually happened. A transaction-level action gives the owner one truthful result across Mac, browser, and relay instead of a misleading final sentence.
- **path:** faculty-judgement → faculty-action → mac-planner → browser-extension → relay → pendant → faculty-perception
- **model tier:** background model for decomposition and compensation planning; realtime only for owner interaction or urgent confirmation
- **latency:** Preview within 2 s; execute each step serially with verification; return a final verified/rolled-back/unknown status within 30 s for ordinary workflows.
- **cost:** One planning call plus one verifier call per step and receipt storage; approximately $0.03–$0.15 for a 3–8 step workflow. Mac/browser action latency dominates.
- **security:** Each step needs an explicit risk class, locator, precondition, postcondition, and whether it is reversible. Irreversible sends/submissions require the existing physical approval latch immediately before that step. Compensation must never claim success if undo is unverified; secrets and page contents stay on their owning surface.
- **missing:** A transaction coordinator joining POST /execute receipts, browser command IDs, and verify_operation_step results; A declared compensation action for each reversible step; An owner-visible operation journal with final state and provenance, not just individual receipts

### "While I am wearing the pendant, let me say “check that” after an action and have the system independently re-check the Mac or browser, then speak whether it is verified, changed, or unknown without repeating the action."
- **useful because:** Owners often need confidence after an action but do not want a second execution or to inspect the screen. The pendant supplies the request and the Mac/browser supplies fresh evidence; this is especially valuable after a dropped link or an ambiguous receipt.
- **path:** pendant → relay → faculty-action → faculty-perception → mac-planner → browser-extension
- **model tier:** Realtime for the short follow-up command and spoken result; use a cheaper background model for selecting the saved postcondition when needed
- **latency:** Fresh verification and a concise answer within 3 s; no mutation during the check.
- **cost:** One small perception/verifier call, typically under $0.01; latency is dominated by a fresh Mac/browser observation.
- **security:** The follow-up must be bound to a specific operation and step, not “whatever was last.” Read-only verifier calls must honor sensitivity and evidence mode; never read or speak secrets. If provenance is stale or the target disappeared, return unknown rather than guessing.
- **missing:** A pendant-to-operation correlation token for a spoken follow-up; A compact spoken rendering of verifier provenance and unknown reasons; A retention policy for postconditions that avoids persisting sensitive expected values

### "If I say “I may have exposed something,” have the pendant start a privacy containment and audit run: freeze queued actions, revoke the affected browser session, preserve a tamper-evident timeline of what the Mac, browser, relay, and pendant actually transmitted, and tell me what was contained versus unknowable."
- **useful because:** Today the owner cannot obtain a trustworthy answer or containment action after a suspected accidental send, open tab, or compromised session. This gives the wearable an emergency control surface spanning the browser’s private session, the Mac executor, and the always-awake relay, without pretending that missing telemetry can be reconstructed.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-action
- **model tier:** Realtime only to recognize the emergency phrase and deliver the first acknowledgement; a background model should classify the incident and summarize the evidence.
- **latency:** Freeze and revoke within 5 seconds; preserve the first signed timeline entries immediately; produce an initial containment result within 15 seconds and a fuller audit later.
- **cost:** One classification/summarization call plus several read-only evidence calls and 1–3 containment mutations; roughly $0.03–$0.20 per incident, dominated by evidence collection and browser session operations.
- **security:** The audit must contain hashes, destinations, timestamps, action IDs, and byte counts by default—not page contents, microphone audio, passwords, or message bodies. Revocation is disruptive and must use the existing physical transaction approval latch unless the owner explicitly configures an emergency phrase. If telemetry is absent, report unknown rather than infer non-exposure. Audit records need append-only integrity protection and bounded retention.
- **missing:** A relay-wide emergency freeze switch that stops not-yet-started jobs and browser commands; Browser-session revocation and Mac credential/session containment actions with independently verifiable postconditions; Signed cross-surface transmission receipts emitted at the point data leaves each surface; An append-only, tamper-evident incident journal with redacted evidence and retention controls


## Changes it proposed to its own stack

### `integration` — Make every mutating operation a durable operation graph: assign operation_id and step_id before execution, persist the intended postconditions and sensitivity, join Mac receipts and browser command IDs to those IDs, and expose a read-only “still true?” lookup that calls verify_operation_step. Keep compensation links for reversible steps and mark the graph committed only after independent verification.
- **owner gets:** After saying “do it,” the owner can ask the pendant what really happened and get a trustworthy verified/rolled-back/unknown answer instead of a conversational guess, even when Mac and browser steps partially fail.
- effort: Medium: extend actionLedger, approvalHandoff, policyRouter, and the existing job/receipt schema; add correlation fields to browser commands and the verifier adapter; build a small operation-graph persistence layer.  ·  risk: Schema migration and old jobs without IDs; recover by treating legacy receipts as unknown and never auto-committing them. Compensation can itself fail, so surface partial rollback rather than hiding it.
- cost: Negligible storage and API cost; one extra verifier call per committed step, typically cents or less.  ·  latency: Adds roughly 100–500 ms per verification plus browser/Mac observation latency; irreversible actions should wait for the result.
- security: Improves least-privilege and auditability. Store hashes/locators and sensitivity labels by default, not form secrets or page contents. Require the existing physical approval latch for irreversible steps.
- depends on: Existing actionLedger and approvalHandoff schemas; verify_operation_step correlation fields (actionId/attemptId addition); Browser command and POST /execute receipt correlation; Owner policy for which action classes may run proactively

### `relay` — Add a signed egress ledger at every boundary (pendant→relay, relay→Mac, Mac→browser, browser→remote service): each record contains operation_id, step_id, destination class, timestamp, byte count, content hash, sensitivity label, and delivery outcome, with a hash-chain anchor held by the relay. Expose only redacted projections to the owner and let an emergency containment run atomically freeze unsent work and append a reason.
- **owner gets:** When something may have leaked, the owner can learn exactly what the system can prove, revoke work that has not left, and see honest unknowns instead of receiving false reassurance or an unusable raw log.
- effort: High: instrument relay, Mac action receipts, browser command results, and pendant queue acknowledgements; define clock/skew semantics, key rotation, redaction, and durable storage.  ·  risk: Telemetry itself can become sensitive and clock disagreement can produce misleading ordering. Recover with monotonic per-surface sequence numbers, signed receipt gaps marked unknown, encrypted retention, and fail-closed logging when a receipt cannot be emitted.
- cost: Small per-action storage and signing overhead; modest relay storage growth. No model cost for normal operation; audit summarization adds an occasional background call.  ·  latency: Adds milliseconds per boundary and may delay irreversible actions until an egress receipt exists; emergency freeze is faster than audit completion.
- security: Strongly improves accountability but introduces a high-value audit store. Use device-bound keys, encrypted-at-rest redacted records, strict retention, and never log payloads or secrets.
- depends on: Durable operation_id/step_id propagation; A relay emergency freeze primitive; Per-surface signing keys and key rotation; Owner-configurable audit retention and emergency approval policy


## What it asked for

_Nothing._
## Its own summary

Recorded four non-identical deliverables: a departure-safe routine spanning pendant/relay/Mac/browser, a verified multi-step transaction with compensation, a read-only pendant “check that” follow-up, and an operation-graph integration change binding receipts to independent postcondition verification. The system still needs a transaction coordinator, operation/step correlation persisted across browser and Mac receipts, owner-defined private-tab markers, a verifiable Mac lock action, and a retention-safe way to speak verifier provenance. I did not re-request the queued motion safety skill.

**Biggest unknown:** Whether the existing Mac/browser action manifests already expose a verifiable lock-screen action and durable owner-maintained private-tab identifiers; no agent has established those concrete implementations yet.

