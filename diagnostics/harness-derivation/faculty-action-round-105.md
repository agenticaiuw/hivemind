# Harness derivation — faculty-action — round 105

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Do this across my Mac and logged-in browser, and only tell me it worked when an independent check proves the intended change actually happened; if anything is unreachable or only partly done, say exactly what remains."
- **useful because:** Today an executor receipt can say success even when Accessibility/input reachability is false. This gives the owner an honest completion answer: the Mac or browser performs the reversible steps, a separate perception pass checks the resulting app/page state, and the relay/pendant reports verified, unverified, blocked, partial, or rolled-back rather than claiming success. It is genuinely cross-surface: the pendant can remain the request/status channel while the relay keeps the lease alive, the Mac acts, the browser bridge reaches private tabs, and faculty-perception supplies independent proof.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background planner for decomposition and a cheap verifier for stable UI/state predicates; reserve realtime for the owner's short spoken request and the final one-sentence status. Escalate to the expensive model only when the proof is contradictory or ambiguous.
- **latency:** Acknowledge intent immediately; first action within 2 seconds; verification within 5 seconds per step. Long browser waits become resumable background jobs, with pendant status updates and a final spoken result when the lease finishes or expires.
- **cost:** About 2–4 inexpensive model calls per multi-step job (plan, per-batch verification, reconciliation); dominant cost is screenshots/page text and repeated context, not execution. Keep evidence as hashes/snippets and send only the failing step to the expensive tier.
- **security:** Proof must not expose private page content beyond the minimum cited snippet/hash. Never treat an executor receipt as proof. Destructive sends, deletes, purchases, or external submissions still require the owner's existing confirmation policy; verification can report them but cannot authorize them. Expired leases must stop retries and mark the job incomplete.
- **missing:** A shared action-outcome schema consumed by faculty-action, relay, Mac, browser, and perception; Independent postcondition probes for typed Mac actions and browser commands; Lease/heartbeat expiry that stops retries and emits a pendant-visible incomplete state; A durable evidence record linking intent, actionId, before state, postcondition, and proof timestamp

### "Start this on the pendant, let my Mac and private browser carry it out while I move around, and bring the exact unfinished step back to me when I reconnect—without restarting anything or guessing what already happened."
- **useful because:** Today a disconnected wearable, sleeping Mac, or lost browser session turns a partially completed task into an ambiguous retry. The owner should be able to walk away and return to a truthful, resumable handoff: the relay preserves a compact continuation token, the Mac/browser checkpoint the last proven state, and the pendant announces exactly where work stopped when it comes back in range.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → faculty-judgement
- **model tier:** Use deterministic state-machine code and a small background model for continuation selection; use realtime only when the pendant reconnects and needs a concise spoken/tactile status. Escalate only if the saved checkpoint conflicts with observed state.
- **latency:** Instant local acknowledgment; reconnect status within 2 seconds; resume or pause decision within 10 seconds after both relay and Mac are reachable. No blocking voice turn while the task runs.
- **cost:** Low: one compact continuation record per active task and one inexpensive reconciliation call on reconnect. Dominant cost is occasional browser/Mac observation, not model generation.
- **security:** Bind continuation tokens to the owner's authenticated pendant session and task scope; expire them and require revalidation after a long absence. Never replay external submissions from a stale checkpoint. Private browser evidence remains on the authenticated bridge, with only a digest and next-step summary sent to the relay.
- **missing:** A signed, durable continuation-token protocol spanning pendant, relay, Mac agent, and browser session; Checkpoint semantics that distinguish proven completion from attempted execution for every step; Reconnect reconciliation that compares the checkpoint against fresh Mac/browser observations before resuming; A pendant-visible unresolved-state UI for paused, expired, and conflict outcomes


## Changes it proposed to its own stack

### `integration` — Introduce an ActionOutcome v1 envelope shared by executor, browser bridge, relay, and faculty-perception. Every step must transition queued→running→(completed_verified | completed_unverified | blocked_unreachable | failed_no_effect | partial | rolled_back), carrying actionId, lease expiry, preflight reachability, before-state digest, postcondition predicate, proof source/timestamp, and retry/repair hint. Make the relay refuse a spoken 'done' when the terminal state is not completed_verified; publish state transitions via /pipeline/events, persist the evidence pointer alongside /jobs/:jobId/receipts, and have the Mac/browser adapters emit blocked_unreachable when their preflight says input or session access is unavailable instead of returning success.
- **owner gets:** The owner stops hearing false success and can distinguish 'the Mac never had control', 'the browser step partly ran', and 'the requested state is now proven'. A dropped pendant link or sleeping Mac no longer causes blind retries or duplicate submissions; the next interaction resumes from the last proven action.
- effort: Medium: define and validate the envelope, add adapter mappings and a postcondition verifier, then update relay speech/status rendering and dashboard tests. No hardware change required.  ·  risk: Older receipts and adapters may lack proof fields; map them to completed_unverified rather than silently upgrading them. A bad predicate could reject a real change, so preserve raw evidence and offer a retry/inspect path. Lease expiry must prevent duplicate external actions.
- cost: Negligible API storage (small digests and evidence pointers); one inexpensive verification call or deterministic probe per mutating step. Avoid resending full screenshots/context.  ·  latency: Adds roughly 0.5–3 seconds for deterministic observation or a small verifier; long waits become asynchronous rather than blocking the voice turn.
- security: Reduces accidental duplicate/destructive actions and limits private evidence to hashes/minimal snippets. Does not weaken existing confirmation rules; proof is never permission.
- depends on: mac-terminal's preflight/input-reachability signal; A deterministic postcondition probe for each typed Mac/browser action; Durable resumable leases for browser and Mac jobs; faculty-perception consuming evidence records and emitting verification verdicts

### `relay` — Add a signed cross-surface continuation ledger for active actions. Each step writes an append-only checkpoint containing taskId, actionId, surface/session binding, before-state digest, execution attempt, observed outcome, and an expiry. On reconnect, the relay requests fresh observations from the Mac and browser, computes a three-way merge (checkpoint vs current state vs intended postcondition), and emits resume, pause-conflict, or already-complete; it must never infer completion from a missing heartbeat. The pendant receives only the compact state and next safe action, while private page evidence stays at the browser bridge.
- **owner gets:** The owner can begin a real task from the wearable, lose connectivity or leave the Mac, and return to the exact unfinished step instead of duplicate clicks, duplicate submissions, or an unexplained failure. It makes the hive behave as one continuing assistant rather than several forgetful sessions.
- effort: High: durable signed ledger, session-bound checkpoint writers for both adapters, reconnect reconciliation, expiry handling, and pendant status rendering; requires protocol work across relay, Mac, browser, and device firmware.  ·  risk: Stale or conflicting checkpoints could cause unsafe replay. Default to pause-conflict and require fresh owner intent for irreversible operations; retain raw evidence for repair. Ledger corruption recovers by marking the task unresolved, never by replaying the last action.
- cost: Small durable storage and cryptographic verification overhead; one observation pass per reconnect. No persistent expensive-model usage.  ·  latency: Normal actions unchanged; reconnect adds roughly 1–5 seconds for fresh observations and reconciliation.
- security: Continuation tokens are scoped, signed, short-lived, and non-exportable across owners/sessions. Browser secrets never enter the relay ledger; only hashes, state labels, and pointers do.
- depends on: Pendant transport identity and reconnect event; Mac and browser adapters emitting durable per-step checkpoints; Fresh observation endpoints on both surfaces; A relay-side append-only store with expiry and key rotation


## What it asked for

_Nothing._
## Its own summary

I discovered the live tools/devices and recorded a new cross-surface capability plus an integration change: ActionOutcome v1 with explicit terminal states and independent postcondition proof. The key correction is that executor receipts are not evidence; faculty-action should only speak “done” for completed_verified, and should surface blocked_unreachable, partial, failed_no_effect, or completed_unverified honestly. I also sent the contract to mac-terminal and faculty-judgement.

**Biggest unknown:** The exact preflight and postcondition signals available from the Mac/browser adapters, and whether resumable lease/heartbeat primitives already exist. Current physical constraints remain: no pendant is connected, home Chrome is offline, and Accessibility/Screen Recording grants are still owner-blocked. I still need those adapter signals and a deterministic verifier before this can be implemented end to end.

