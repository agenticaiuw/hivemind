# Harness derivation — unified — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surfaces** — Safari on MacIntel is online with 5 tabs, and home-macbook-bridge is online; the cloudflare-contract-test mobile device is offline. Current Mac accessibility status from peer reports trusted for AI Pendant Agent, with Screen Recording true.
  - evidence: discover(devices) returned Safari online and home-macbook-bridge online; mac-planner reported fresh GET /observe permissions.

## Capabilities it proposed

### "Did my morning routine really happen, which steps were skipped, and should I rerun anything now?"
- **useful because:** A scheduled routine firing is not the same as its Mac actions completing. The owner needs a concise, step-level answer grounded in receipts, including whether the machine was asleep, a browser session was unavailable, or a step was intentionally skipped, with safe rerun recommendations rather than a vague success label.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** deterministic receipt aggregation first; background model only to summarize ambiguous failures; realtime for the spoken answer
- **latency:** Under 2 seconds for a completed routine; up to 10 seconds if browser receipts must be fetched.
- **cost:** Very low: mostly indexed route reads; model cost only for natural-language summarization of multiple failures.
- **security:** Show only the owner's bound routine and its receipts. Never infer completion from a queued job. Reruns must use the existing action risk classification and physical approval where required; clearly distinguish observed, inferred, and missing evidence.
- **missing:** A routine-run record that links schedule occurrence to every child job and browser command; A normalized completion predicate for each step (executed, receipt-confirmed, skipped, unknown); A voice/dashboard action to request a bounded rerun of only safe, failed steps

### "Fix whatever is preventing my browser or Mac task from finishing, but only make safe repairs, then tell me exactly what you changed and what still needs me."
- **useful because:** The owner currently gets separate offline, lease, and permission failures and has to guess which recovery is safe. This turns diagnosis into a bounded recovery conversation: repair only idempotent bridge/lease problems, stop at permissions or risky actions, and return a receipt rather than retrying blindly.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** deterministic health diagnosis and repair selection; realtime model only to explain the resulting plan and ask for confirmation when a human permission is needed
- **latency:** Diagnosis under 2 seconds; safe repair under 15 seconds; never block a live conversation waiting for a browser repair.
- **cost:** Low: health endpoints and repair operations dominate; no model call needed for the repair itself.
- **security:** Allow only the enumerated idempotent repairs (wake bridge, restart polling, clear stale lease). Never auto-open TCC settings or rerun an external action. Bind every repair to a job ID and idempotency key, and return before/after health evidence.
- **missing:** A single owner-facing command that composes diagnosis, dry-run plan, repair, and revalidation; A durable repair receipt linked to the original job and any browser command; A clear handoff when Accessibility/Screen Recording or account login requires owner action

### "Before you send or upload anything, show me exactly what data will leave my devices, which account and destination will receive it, how long it may persist, and let me remove fields without rebuilding the task."
- **useful because:** Today an action can be approved as a whole while the owner cannot see the complete cross-surface data payload: Mac files, browser form fields, pendant audio/transcript, and relay copies can cross different trust boundaries. A destination-aware manifest would make privacy a property the owner can actually inspect rather than a promise in the UI.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic taint/provenance analysis builds the manifest; background model may explain unfamiliar fields; realtime only reads the compact manifest aloud.
- **latency:** Preview in under 2 seconds for local files and known browser fields; under 5 seconds when relay retention metadata must be fetched. Submission waits for explicit owner confirmation only when a new destination or sensitive field is present.
- **cost:** Low to moderate: hashing and metadata inspection dominate; model use is optional and limited to explanation.
- **security:** Never send the unredacted payload to the preview service. Hash or locally summarize sensitive values, show destination/account bindings, and bind the final submission to the exact manifest digest. A changed page, file, or recipient invalidates the preview. This is a preview and minimization boundary, not a substitute for action approval.
- **missing:** A cross-surface data-flow manifest format covering files, browser fields, audio/transcripts, relay storage, and recipients; Pre-submit interception hooks in Mac actions, browser commands, and relay uploads; A field-level redaction transform that preserves task validity where possible; Retention declarations and a manifest-digest check immediately before dispatch

### "For the next hour, block every outbound message, upload, purchase, and browser submission except the one task I name; show me anything that was held and release it only when I say so."
- **useful because:** The owner has a privacy latch for audio and per-transaction approval, but no time-bounded, cross-surface hold on actions that can leave the device. A single spoken or physical policy would prevent an accidental send from a queued Mac job, a browser tab, or a sleeping relay while preserving safe local work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy enforcement and queue filtering; realtime model interprets the owner's scope and exception; no model decides whether an item is exempt after the policy is set.
- **latency:** Policy activation under 1 second locally and under 5 seconds at the relay; every newly queued outbound action is held before dispatch.
- **cost:** Low: policy propagation and queue metadata; no recurring model cost after activation.
- **security:** Default deny on uncertain classification. Bind exceptions to exact job/recipient/destination digests and expiry, require physical pendant confirmation for releasing held irreversible actions, and make the policy survive relay/Mac restarts. Held payloads must remain encrypted and must not be copied to a new store.
- **missing:** A replicated outbound-policy record with monotonic version and expiry; Pre-dispatch gates in relay jobs, Mac execution, and browser commands; A held-item inventory and per-item release/cancel operation; A conflict rule with the existing privacy latch and staged transaction approval

### "Give this task access only to these files and this browser tab for 30 minutes, then prove that access expired and nothing else was touched."
- **useful because:** Current bearer-token automation and broad Mac/browser reach make task scope implicit. The owner needs a practical least-privilege boundary: a task should not be able to discover unrelated files, tabs, accounts, or clipboard contents merely because the agent can reach them.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic capability token and scope enforcement; realtime model only translates the spoken scope into explicit paths, tab/session bindings, and expiry.
- **latency:** Scope issuance under 2 seconds; enforcement adds no perceptible latency; expiry and post-task audit available within 3 seconds.
- **cost:** Low: signed short-lived tokens and access checks; modest engineering effort for Mac/browser adapters.
- **security:** Fail closed on scope ambiguity. Tokens must be audience-bound, non-transferable, short-lived, and unable to widen themselves. Record path/tab hashes rather than contents. Physical approval is required when the requested scope includes an external submission or secrets.
- **missing:** A scoped capability-token format understood by relay, Mac executor, and browser bridge; Mac file and app adapters that reject reads/actions outside the token; Browser bridge enforcement for exact tab/session and allowed operation types; A post-task touched-resource audit and expiry receipt


## Changes it proposed to its own stack

### `memory` — Add a quarantine state for automatically extracted facts: new facts remain untrusted and non-routable until surfaced in the next owner briefing or explicitly confirmed; attach a compact evidence capsule and expiry, and auto-delete unconfirmed facts after the configured retention window. Explicitly requested facts bypass quarantine. Expose only the state transition and provenance, never raw unrelated audio.
- **owner gets:** The system stops silently turning overheard details into durable beliefs. It can still suggest useful context, but nothing inferred in the background can steer future actions until the owner has had a chance to recognize it.
- effort: Medium: extraction writer, context-graph query/routing filters, briefing presentation, and tests for expiry and confirmation.  ·  risk: A useful fact may expire before confirmation; recover by showing a pending-facts count and allowing extension. A bug could route quarantined data, so enforce the state at the graph query boundary, not only in the UI.
- cost: Negligible runtime cost; small metadata per fact and one background expiry pass.  ·  latency: No impact on live conversation; first-use context lookup may skip quarantined candidates.
- security: Improves privacy by default. Evidence capsules must inherit the fact's quarantine and deletion state; do not copy them into ordinary memory until confirmation.
- depends on: The existing context-graph entities/relations and memory projection need a trust/quarantine field; An owner-facing pending-facts surface; the existing generic memory listing proposal must be implemented as a prerequisite

### `integration` — Create a routine-run envelope that is opened when a scheduled routine claims work and closed only after every child Mac and browser operation reaches a terminal receipt. Store per-step evidence status (confirmed, skipped, failed, unavailable), sleep/bridge/browser availability snapshots, and a safe-rerun set. Publish the envelope to the relay so a later pendant question can answer from receipts rather than querying multiple live surfaces.
- **owner gets:** When the Mac sleeps or a browser tab disappears, the owner will hear exactly what did and did not happen instead of being told a routine succeeded because it was launched. They can rerun only the safe missing pieces.
- effort: Medium: scheduler/job schema linkage, browser command correlation, terminal-state reducer, and a small dashboard/voice readout.  ·  risk: A child job may never report; use an expiry to mark it unknown, never successful. Duplicate callbacks must be idempotent by command/job ID. Recovery is to retain raw receipts and rebuild the envelope.
- cost: Small persistent metadata records; negligible model cost because aggregation is deterministic.  ·  latency: No added latency to routine execution; finalization is asynchronous. A status query may wait briefly for receipt reads.
- security: Do not copy page contents into the envelope; retain IDs, statuses, and redacted error classes only. Rerun remains subject to existing risk and approval controls.
- depends on: A stable routine occurrence ID in the scheduler; Existing GET /jobs/:jobId/receipts and POST /browser/result/:commandId correlation; A relay-readable status endpoint or dashboard view


## What it asked for

_Nothing._
## Its own summary

This round established that Safari (5 tabs) and the home Mac bridge are online, while the mobile contract-test device is offline. I recorded three forward proposals: quarantine automatically extracted facts until the owner confirms them, proof-carrying routine-run envelopes with step-level receipts, and a bounded safe-repair concierge for stuck Mac/browser work. I also recorded a routine status capability tying scheduler, jobs, browser receipts, and journal evidence together.

**Biggest unknown:** I still need implementation of the missing joins rather than more discovery: a fact-quarantine field and owner-facing confirmation surface; a stable routine-occurrence/child-job correlation and terminal receipt reducer; and a single diagnose→safe-repair→revalidate endpoint with durable receipts. I also need an inventory/contract for /browser-jobs/:jobId, and the owner's policy for when a repair may interrupt an active conversation or require explicit confirmation.

