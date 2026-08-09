# Harness derivation — faculty-perception — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At 2026-08-08T23:25Z, the authenticated continuity snapshot reports AI Pendant Agent accessibility and screen recording trusted, all required automation grants present, permissions.ready=true; Safari browser bridge online with 3 tabs and 0 pending commands; relay reachable with D1 store and mac bridge online. No pendant telemetry is present in this snapshot.
  - evidence: read_continuity_snapshot(include=['relay','pipeline'], since=2026-08-08T22:00Z) resolved GET /ops/snapshot HTTP 200; body status.permissions and browser/relay fields.

## Capabilities it proposed

### "“Do this task for me, and show me proof it really happened—not just that the Mac said it ran.”"
- **useful because:** This would be the system's most useful trustworthy behavior: a spoken request could cross the relay, authenticated browser, and Mac, then return a concise result grounded in before/after evidence. It would distinguish planned, attempted, verified, and owner-heard instead of calling a Mac-side completion “done.”
- **path:** pendant voice request and (when connected) spoken result → relay intent/job correlation and policy gate → Mac planner and action ledger for reversible execution → browser extension for authenticated page state and mutation → Mac vision for visual before/after verification when DOM evidence is insufficient → relay receipt returned to the pendant
- **model tier:** Realtime only for the short conversational turn; a cheaper background planner/verifier model for multi-step execution and evidence comparison.
- **latency:** Acknowledge in under 1 s; execute in the existing job budget (roughly 10–60 s); speak a 1-sentence verdict plus an optional evidence detail. Destructive or irreversible steps still require confirmation.
- **cost:** Usually <$0.03 per task with planner/verifier calls; browser and Mac execution dominate latency, not tokens. Screenshot verification adds one vision call only when structured state cannot prove the result.
- **security:** Evidence must be redacted before relay storage and retain source URL, timestamp, and content hash. Never expose secrets from authenticated tabs. Require confirmation for send/delete/purchase. If verification is unavailable or state changed, say “attempted, not verified,” never infer success.
- **missing:** A single cross-surface receipt schema joining actionLedger step keys, browser command IDs, evidence capsule IDs, relay job IDs, and verification outcome; A relay-side reader that refuses completed=true unless an independent postcondition verifier passes; A pendant playback/consumption event when a real pendant is deployed; current relay delivery is only bytes-to-socket

### "“Before you click or submit anything in my browser, tell me whether the page you are relying on is still the same page I approved.”"
- **useful because:** Authenticated web pages can change after the owner approves an action. A cross-surface freshness fence would prevent submitting to a changed tab, wrong account, or altered form, while giving the owner a concrete reason for any pause instead of a vague failure.
- **path:** pendant for the approval and spoken stale-page warning → browser extension for authenticated DOM snapshot, tab identity, and postcondition check → Mac vision for a visual fallback when DOM capture is incomplete → relay for policy, approval token, and tamper-evident correlation → Mac planner/action ledger for the actual mutation and undo path
- **model tier:** Use a cheap deterministic hash/diff first; invoke a small verifier model only for semantic changes (for example, whether a changed total or recipient is material). Realtime speaks only the warning or final confirmation.
- **latency:** Capture and compare in <500 ms before a click; semantic verification under 2 s. If the tab, URL, account identity, or relevant field changes, pause and ask rather than proceed.
- **cost:** Near-zero for hashes and structured diffs; <$0.01 for ambiguous semantic comparison. Browser snapshot transfer and one optional screenshot dominate latency.
- **security:** Hash only redacted relevant fields, never upload passwords, tokens, or full page bodies to the relay. Bind approval to tab/session pseudonym, URL origin, locator, content hash, and short expiry. A changed page invalidates approval; destructive actions remain confirmation-gated.
- **missing:** A browser-side approval token bound to the evidence capsule/content hash and expiring after one mutation; A preflight hook in browser_run_actions and Mac action execution that enforces the token instead of merely recording provenance; A shared semantic-diff contract so browser DOM and Mac vision can agree on what changed

### "“Is the thing I’m seeing on my Mac actually the same thing the relay and browser think is happening?”"
- **useful because:** The system currently exposes several partial truths: relay job state, Mac receipts, browser tab state, and pipeline traces can disagree or go stale. A spoken discrepancy report would identify the first contradictory observation, its age, and the safest next check instead of silently choosing one source.
- **path:** pendant for a short discrepancy alert and follow-up question → relay for job/session state and server timestamps → Mac agent for permissions, process reachability, action receipts, and pipeline trace → browser extension for live tab/session identity and pending command state → Mac vision for a visual confirmation of what is actually rendered
- **model tier:** Deterministic rules should align timestamps, IDs, hashes, and freshness first; use a low-cost reasoning model only to summarize contradictions. Realtime is reserved for the spoken answer.
- **latency:** Routine check in 1–2 s; visual fallback under 5 s. It must return “consistent,” “contradictory,” or “not observable,” with the oldest observation age.
- **cost:** <$0.01 when structured snapshots suffice; one vision call costs more and is used only on disagreement or missing DOM evidence.
- **security:** Keep raw authenticated page content on the Mac; send only redacted claims, hashes, IDs, and timestamps to relay. Treat a missing source as unknown, not false. Never let a consistency check authorize a destructive action by itself.
- **missing:** A normalized observation envelope with source, capturedAt, freshness policy, subject ID, content hash, and confidence; A contradiction detector that compares relay jobs, Mac receipts, browser state, and pipeline events without treating completed as heard; A user-facing explanation format that names which source won and why, or explicitly reports unresolved disagreement

### "“Give me a temporary permission to do exactly this one kind of thing across my Mac and logged-in browser, and let me revoke it from the pendant at any time.”"
- **useful because:** Today consent is fragmented: the relay, Mac planner, and browser extension can each be trusted, but there is no owner-visible, scope-limited delegation that follows one request across all three. This would let the owner safely authorize a bounded task without repeatedly confirming harmless steps, while retaining an immediate physical stop control.
- **path:** pendant button/voice to display, confirm, and revoke a short-lived delegation → relay to mint a signed, single-purpose capability token and enforce its expiry, audience, and action limits → Mac planner/action ledger to require and record the token before each action → browser extension to enforce the same token against tab origin, session, and allowed mutation types → Mac vision only as a read-only verifier that cannot expand the delegation
- **model tier:** Deterministic policy and signature checks; no expensive model for authorization. Realtime is used only to explain the scope and expiry in one short sentence.
- **latency:** Issuing or revoking under 300 ms when connected; every action adds under 50 ms for local token validation. Offline pendant revocation must be queued monotonically and honored on the next link before any new delegated action.
- **cost:** Negligible API cost; cryptographic checks and small event records dominate. Hardware work is firmware button/LED state plus a bounded revocation journal, not routine SD writes.
- **security:** Bind the token to owner identity, task ID, allowed verbs, target origins/apps, maximum count, expiry, and a nonce; prevent model text from widening scope. Revocation must fail closed, survive relay restart, and be visible in receipts. Never delegate password extraction, arbitrary shell, purchases, deletion, or message sending without a separate confirmation.
- **missing:** A shared capability-token format and verifier implemented by relay, Mac, and browser; A pendant-side bounded revocation record and a relay endpoint that accepts device-authenticated revocations; Action and browser harness enforcement hooks; recording a token in the ledger is insufficient if executors do not reject missing or mismatched tokens; A user-facing scope preview that names the exact apps, sites, and verbs before approval

### "“When you use a personal fact about me, show me where it came from, whether I said it, and let me correct only that fact without rewriting my whole memory.”"
- **useful because:** A machine-derived preference can currently look indistinguishable from owner intent, remain pinned indefinitely, and be injected into every prompt. The owner needs a provenance-aware correction interaction—especially for timezone, permissions, and routines—so a stale or sampled value cannot quietly steer actions.
- **path:** pendant voice for “why do you think that?” and a short correction → Mac memory store for source.origin, confidence, use history, expiry, and targeted replacement/tombstone → relay context projection so corrected provenance propagates to realtime voice and scheduled work → Mac planner/judgement to downgrade or quarantine machine-derived facts until resolved → browser only when a fact was inferred from an authenticated page, linking the source capsule without exposing its secret contents
- **model tier:** Deterministic provenance display, conflict detection, and targeted fact mutation; a cheap summarizer can turn the record into one spoken sentence. Realtime is not needed for background reconciliation.
- **latency:** Answer provenance in under 1 s from local memory; apply a confirmed correction and invalidate projections within 2 s. Scheduled jobs must use the new value on their next invocation.
- **cost:** Negligible API cost; invalidating cached projections and propagating a tombstone are the main engineering work.
- **security:** Do not speak secret fact values by default. Distinguish owner, machine, browser, and inferred origins; never let a low-authority browser observation overwrite an owner fact automatically. Require confirmation to delete or replace an owner-origin fact, and retain an audit tombstone without retaining sensitive body text.
- **missing:** A first-class provenance and authority field in every memory projection consumer, not just the stored fact; A targeted owner correction route that atomically replaces/quarantines one key and invalidates relay/Mac caches; Conflict policy for owner versus machine-derived values, including a visible warning instead of confidence-only sorting; Voice-safe redaction for secrets and a compact “source and last confirmed” explanation


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found a major state change: the exact AI Pendant Agent binary now has Accessibility, Screen Recording, and required automation grants; permissions.ready=true. Safari bridge is online with three tabs and zero pending commands, relay is reachable with D1, while no pendant is registered. I recorded that fact and proposed three distinct owner-facing capabilities: proof-backed cross-surface task completion, approval invalidation when an authenticated browser page changes, and a contradiction report that compares relay/Mac/browser reality instead of guessing. The remaining work is not basic reachability: it is the missing connective contracts—cross-surface receipts, evidence-bound approval enforcement, and normalized contradiction detection—and eventual device-originated playback telemetry.

**Biggest unknown:** Whether a physical pendant will be registered and emit telemetry; until then, spoken delivery and owner-heard status remain unverifiable even though the Mac/browser/relay surfaces are live.

