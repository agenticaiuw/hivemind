# Harness derivation — mac-terminal — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac action receipts** — Implemented receipts cover action identity, effect, touched resources, duration, reversibility and undo snapshots, but the established schema does not include bounded stdout/stderr tails, failure classification, or an idempotency/retry decision.
  - evidence: describe(chg-5fc73ce3): receipt fields list actionId, receiptId, effect, touched, duration, reversibility, reversedBy/irreversibleReason; implementation note contains no stdout/stderr or retry fields.

## Capabilities it proposed

### "When I tell you to take care of something, verify that it actually stuck everywhere, and tell me exactly what is still unfinished."
- **useful because:** Today an agent can report that a Mac command, browser edit, or relay job completed even when the application rejected it, a page reverted it, sync was delayed, or the Mac went offline. This gives the owner a closed-loop result about the real outcome rather than a claim that steps were attempted. It is especially valuable for cross-surface tasks where Safari, a local app, the relay, and the pendant can each show different state.
- **path:** pendant: capture the goal and speak a concise final status or an exception → relay: own the goal, schedule delayed verification, correlate all attempts, and notify when the outcome changes → mac-bridge: inspect application/file/system postconditions and re-check after sync delays → browser: inspect authenticated page state and compare the resulting semantic fields with the intended change → dashboard-ux: show an evidence timeline of intended state, observed state, pending checks, and unresolved discrepancies
- **model tier:** Use the realtime model only for the initial conversation and short spoken explanation. Use a cheaper background model for postcondition planning, evidence reconciliation, delayed rechecks, and discrepancy summaries; use deterministic typed checks before invoking a model.
- **latency:** Immediate acknowledgement in under 2 seconds; first result after the action completes; delayed verification should run at configurable intervals (for example 10 seconds, 2 minutes, and 15 minutes) without keeping the voice session open. The pendant should interrupt only for a meaningful failure or eventual success after an earlier uncertain result.
- **cost:** Usually well below one realtime turn: deterministic Mac/browser checks dominate latency but not API cost, with one small background reconciliation call only when observations disagree. Roughly $0.005–$0.05 per task depending on the number of delayed checks and page evidence size; authenticated browser screenshots or large DOM captures dominate transfer and processing cost.
- **security:** Verification may read private browser pages, local files, and application state, so evidence must inherit the originating job's permissions, remain local-first where possible, and redact secrets from dashboard and spoken output. The system must distinguish 'verified', 'not yet observable', and 'failed' rather than claiming success. It should never submit an additional irreversible action merely to verify; verification is read-only unless the owner separately requested a repair.
- **missing:** A durable goal/postcondition schema that expresses what success means independently of the action sequence; Mac and browser adapters for typed, read-only postcondition checks with freshness timestamps; Relay scheduling and deduplication for delayed verification attempts; Evidence reconciliation that can represent conflicting observations without collapsing them into success; Dashboard and pendant status vocabulary for verified, pending, uncertain, and failed outcomes


## Changes it proposed to its own stack

### `mac-harness` — Add a failure-aware execution journal and recovery loop around run_shell and typed Mac actions. For every invocation, persist a compact, redacted execution capsule (request/job ID, argv or action type, cwd, selected environment fingerprint, start/end/duration, exit/signal, stdout/stderr hashes plus bounded tails, and filesystem/network/process diagnostics collected only on failure). When a command fails, classify likely causes (missing executable, wrong cwd, permission, transient network, lock/contention, timeout), automatically retry only when the planner marks the action idempotent, and otherwise generate a concrete recovery plan. Link the capsule to the relay job receipt and expose a one-click 'retry with suggested fix / open artifact' view in the shared dashboard; send the pendant only a terse failure and next step, never raw logs.
- **owner gets:** A failed 'handle this' request would stop being a dead end or require the owner to reproduce an invisible terminal error. The agent can find the project, repair a stale path or transient connection, resume safely after a timeout, and tell the owner exactly what happened when it cannot. Cross-surface linkage means the spoken pendant answer, Mac evidence, and durable relay history agree.
- effort: Medium: local-agent journal schema and bounded collectors, planner failure classifier/retry policy, relay receipt fields and dashboard detail view, plus pendant notification formatting and tests for redaction/idempotency.  ·  risk: Diagnostic data can contain secrets or personal paths; redact environment values and cap/TTL raw tails, hash by default, and keep capsules local unless the job is explicitly relay-visible. Automatic retries can duplicate side effects, so require an explicit idempotency annotation from the planner and never retry unknown commands. Recovery is straightforward: disable the retry worker and retain the original receipt.
- cost: Small storage and CPU cost on the Mac; relay adds a few D1 rows and occasional short R2 artifacts. No extra model call for ordinary success; a cheap classifier or the existing planner is invoked only on failures.  ·  latency: No meaningful success-path delay beyond journal write; failure diagnosis adds roughly 1–5 seconds locally, with relay/dashboard synchronization asynchronous.
- security: Improves auditability without adding an approval gate (preserves the owner's maximum-access policy). Must implement secret redaction, local-first retention, per-job access control, and explicit deletion of capsules alongside existing audio/job retention.
- depends on: Existing action receipts (chg-5fc73ce3); Durable job/result linkage and relay receipt APIs; A typed/idempotency annotation in the Mac planner; Dashboard job detail UI


## What it asked for

_Nothing._
