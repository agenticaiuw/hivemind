# Harness derivation — faculty-judgement — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“After you do something for me, check whether it actually worked and, if it didn't, tell me and offer the safest undo.”"
- **useful because:** Today a receipt means the Mac accepted an action, not that the world changed as intended. A browser can reject a click, a reminder can land in the wrong list, or a staged audio job can never be heard. This closes the loop across executor, browser, relay, and pendant instead of making the owner audit every result.
- **path:** mac-planner → browser-extension → relay → pendant → dashboard
- **model tier:** background for postcondition checks; realtime only for the one-sentence exception spoken on the pendant
- **latency:** Check reversible local actions within 10 seconds; browser postconditions within 30 seconds; no interruption unless policy marks the mismatch urgent.
- **cost:** About $0.002–$0.02 per checked action, dominated by browser/page interpretation; deterministic receipt and selector checks should be free.
- **security:** Read-only verification must not submit forms or mutate pages. External side effects remain behind autonomy_policy_evaluate and physical_transaction_approval_latch. Send only redacted mismatch summaries to TTS; require confirmation before undoing anything not mechanically reversible.
- **missing:** typed postcondition declarations on plans/actions; a verifier that joins relay job IDs to Mac action IDs; browser result snapshots retained long enough to compare before/after; a safe undo mapping for each action kind

### "“When I walk away from my Mac, stop anything that could surprise me; keep only safe read-only work running, and tell me what was paused when I come back.”"
- **useful because:** The system currently knows Mac HID idle time and job state but does not turn physical absence into a safety boundary. A USB-tethered pendant gives a second, independent presence signal: unplugging it or losing its serial heartbeat should stop pending mutations while allowing research and diagnostics to finish. The owner returns to a concise, trustworthy handoff rather than discovering a stale browser or an accidental send.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** deterministic local policy for the stop/hold decision; background model only to summarize paused work
- **latency:** Freeze new mutating work within 1 second of serial-heartbeat loss; surface the handoff on reconnect within 5 seconds.
- **cost:** Near-zero model cost for the gate; $0.001–$0.01 for a reconnect summary.
- **security:** Fail closed on ambiguous link loss: pause, never cancel destructively. Do not infer physical absence from idle time alone; require a signed pendant heartbeat or explicit owner setting. Existing approved physical approval remains required after resumption, and sensitive work is summarized without content.
- **missing:** authenticated USB heartbeat and reconnect events from the live pendant; a durable per-job HOLD state distinct from processing/queued; an executor hook that refuses new mutations while held; an owner-configurable exception list for safe read-only jobs

### "“Give me a morning brief that is allowed to say ‘I don’t know’; never tell me my calendar is clear unless you proved the calendar was readable, and label what is stale or conflicting.”"
- **useful because:** The current day-plan and notification paths can confidently say ‘nothing waiting’ when EventKit returned an empty result because permission was missing. A brief that carries source freshness, permission provenance, and conflict status would prevent the most dangerous kind of personal assistant error: a calm, polished lie that causes the owner to miss something.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** deterministic reconciliation and policy first; a cheaper background model compresses only the verified findings; realtime speaks the final short sentence
- **latency:** Under 15 seconds for local sources; if a source is unreadable, say so immediately rather than waiting for speculative synthesis.
- **cost:** $0.001–$0.01 per brief; most work is local reads and deterministic conflict detection.
- **security:** Do not send raw mail/calendar bodies to the relay by default. Carry source IDs, timestamps, permission verdicts, and redacted summaries. The owner can explicitly request sensitive detail on the local dashboard. Every spoken claim needs an evidence reference and an explanation path.
- **missing:** make routine briefing jobs call reconciliation before day-plan/notification triage; fix EventKit empty-result handling in /day-plan and /notifications; a freshness/provenance envelope on each spoken item; a scheduler-to-attention handoff that prevents duplicate daily briefings

### "“Before I rely on the pendant, tell me whether it is healthy enough right now—link quality, audio underruns, battery, and whether the last thing I heard was actually delivered.”"
- **useful because:** A green Mac/relay status is not the same as a trustworthy wearable: the pendant can be connected over USB while audio is starving, a checksum failed, or playback never finished. This gives the owner one honest readiness verdict grounded in UART metrics, authenticated delivery ACKs, pipeline state, and power—not a generic online badge.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** deterministic health scoring and evidence aggregation; no expensive model unless the owner asks for a natural-language diagnosis
- **latency:** Under 2 seconds for a live USB check; under 10 seconds when reconciling recent delivery history.
- **cost:** No model cost for normal checks; under $0.001 for an optional concise explanation.
- **security:** Expose opaque artifact IDs and aggregate metrics, not audio or UART payloads. A failed health check must prevent claiming playback success but must not silently retry or mutate owner work.
- **missing:** a live authenticated USB diagnostic transport and battery/power readout; a unified readiness schema joining UART metrics, pipeline status, and delivery ACKs; a durable mapping from spoken item to artifact ID; a dashboard and one-sentence pendant-safe verdict

### "“Show me how your behavior would change before I change a policy—using my recent real situations, not an abstract explanation.”"
- **useful because:** The owner can set interruption and autonomy policies, but cannot see the consequences of a proposed threshold or quiet window before living through it. A policy simulator would replay recent, redacted events and show which would have been spoken, deferred, blocked, or escalated under the new policy. That makes the system legible and lets the owner correct a bad rule without waiting for the next failure.
- **path:** dashboard → relay → mac-planner → pendant
- **model tier:** deterministic policy evaluation over stored event summaries; background model only to phrase the comparison
- **latency:** Under 5 seconds for a 7-day replay; never interrupt the owner while simulating.
- **cost:** Usually no model cost; under $0.01 when natural-language explanation is requested.
- **security:** Replay only redacted event metadata by default. Do not expose mail, calendar, or browser bodies to the relay. Simulation must be side-effect-free and clearly labeled as hypothetical.
- **missing:** a durable, redacted decision-event log rather than only final receipts; a policy version attached to every historical decision; a replay endpoint that evaluates old events against candidate policy versions; dashboard visualization of changed decisions and explanations

### "“Tell me what personal information is scheduled to expire, what copies will remain, and let me approve one complete deletion that follows the information across every surface.”"
- **useful because:** Today deletion is fragmented: a capture can survive in the context graph, a browser-derived fact can survive evidence revocation, and relay memory has no live writer. The owner cannot know whether ‘forget this’ actually forgot it. A deletion preview plus verified cascade would make privacy an observable result rather than a promise.
- **path:** dashboard → mac-planner → browser-extension → relay → pendant
- **model tier:** deterministic inventory, lineage, and cascade execution; realtime only confirms the final result in one short sentence
- **latency:** Preview in 3 seconds; execute only after explicit confirmation; verify all stores within 30 seconds and report any residue.
- **cost:** No model cost for inventory/cascade; under $0.01 for a concise residue explanation.
- **security:** Default to metadata-only previews and redact secret values. Destructive deletion requires explicit confirmation and an idempotency key. If a surface is offline or cannot prove deletion, fail visibly rather than claiming completion; retain only a tombstone and deletion receipt.
- **missing:** provenance links from derived facts and graph entities back to source capsules; a cross-store deletion coordinator with durable progress and retries; relay/fleet-memory tombstone propagation; read-only verification endpoints for each local and browser store

### "“When you recommend an action, show me the cheapest safe way to get the same result and what I am paying—in time, model calls, battery, and privacy exposure.”"
- **useful because:** The owner currently gets a result, not a choice among execution strategies. A browser route, Mac route, or delayed routine can have radically different latency, cost, battery, and disclosure consequences. A resource-aware alternative chooser would make the assistant feel like a steward of the owner's life and devices rather than an opaque executor.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** deterministic route/cost estimation first; background model ranks genuinely incomparable alternatives; realtime speaks only the selected one-line recommendation
- **latency:** Under 2 seconds for known action classes; under 10 seconds when comparing browser and Mac plans.
- **cost:** $0.001–$0.02 per comparison, dominated by optional planning; route estimates and battery accounting are local.
- **security:** Never choose a cheaper route that expands disclosure or weakens confirmation. Show destination and data class for every alternative. External side effects still require the existing policy and physical consent rules.
- **missing:** a normalized cost model for model tokens, wall time, battery draw, and data exposure; capability advertisements from relay, Mac, browser, and pendant with freshness; side-by-side plan generation without executing either plan; a user-visible preference for whether time, privacy, money, or battery wins ties


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing capabilities: post-action outcome verification with safe undo, a walk-away safety boundary driven by pendant serial presence, a source-honest morning brief that refuses false all-clear claims, and a unified wearable readiness verdict grounded in UART/audio delivery evidence. The recorder repeatedly flagged the first three as connective work because their ingredients already exist; the real missing work is the joins and enforcement points, not more standalone routes. The pendant and Mac bridge are online now, so USB heartbeat, readiness, and walk-away behavior can be prototyped today without pretending LTE registration exists.

**Biggest unknown:** I still need an authoritative answer on USB-tethered local voice feasibility—the outstanding orchestrator request. Specifically: can the live nRF9160 serial path carry authenticated heartbeat/control concurrently with audio, what event/latency budget is achievable, and can battery/power metrics be read? I also still need the owner to choose the policy values that were explicitly declined: what counts as safe read-only work while away, whether a readiness failure should suppress speech, and which brief sources may be treated as authoritative.

