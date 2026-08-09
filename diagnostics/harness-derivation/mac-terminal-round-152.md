# Harness derivation — mac-terminal — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run that Mac command, and if it fails, figure out why and recover without asking me.”"
- **useful because:** Today a failed shell step loses the numeric exit code, signal, PID, and environment context, and cancellation cannot stop a running child. This would turn the Mac from a fire-and-forget executor into a useful recovery agent: classify the failure, apply a model-chosen repair (for example select the discovered project directory or refresh a stale browser bridge), retry only when the intended effect is still safe, and report exactly what changed.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Use the realtime tier only to understand the spoken intent and announce state; use a cheaper background model for failure diagnosis and retry planning. The Mac executes and the relay persists the recovery state.
- **latency:** Initial dispatch under 2 seconds; failure diagnosis 3–10 seconds; recovery may run for the original command timeout. Pendant gets immediate failed/retrying/completed status rather than waiting silently.
- **cost:** About $0.01–$0.05 per failed invocation depending on output and diagnosis depth; the dominant cost is resending command output and browser context, so cap and hash unchanged evidence.
- **security:** The owner deliberately permits unattended maximum access. A repair can still create side effects; preserve the original and repaired commands, cwd, redacted environment fingerprint, exit code, and before/after state in the job receipt, and announce any non-reversible mutation after the fact. Do not send inherited secrets to the relay or model.
- **missing:** Process-supervised shell execution that captures exit code, signal, PID, start/end/duration, and kills the process group on cancellation; Failure classifier plus idempotency-aware recovery planner wired to /jobs/:jobId and action receipts; A relay-to-pendant retrying status stream with attempt numbers

### "“What exactly did you do on my Mac and in Safari while I was away? Give me one replayable report, not a vague summary.”"
- **useful because:** Jobs, receipts, browser inspections, and shell output currently live in separate records and cannot be joined reliably. A single evidence bundle would show the original intent, every command and tab action, timestamps and durations, stdout/stderr and exit status, screenshots or cited page snippets, files touched, retries, and the final state. The owner can audit a task after leaving the machine without reconstructing it from logs.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → unified → pendant
- **model tier:** Generate the bundle in the background with a cheap model; use realtime only when the owner asks a follow-up such as “show me the step that changed the file.” Keep raw evidence local and summarize only selected, redacted excerpts through the relay.
- **latency:** Receipt is incrementally available within 1 second of each step; a complete report should be ready within 5 seconds after job completion, regardless of whether the Mac or Safari bridge had transient outages.
- **cost:** $0.005–$0.03 per completed task; storage and screenshot retention dominate, not inference. Deduplicate repeated stdout and store hashes plus local paths for large artifacts.
- **security:** Shell inherits secrets today and browser pages may contain passwords, health, or financial data. Store raw evidence only on the Mac, redact environment values and sensitive DOM regions before relay export, bind every record to job/session/tab IDs, and make the owner explicitly request raw local evidence.
- **missing:** A tamper-evident cross-surface execution envelope joining jobId, ledgerId, receiptId, shell attempt, and browser request ID; Shell exit-code/PID/environment-fingerprint capture and browser screenshot/DOM citation references; GET /jobs/:id/report (local raw and redacted relay views) plus retention/size controls

### "“Keep this whole task alive while I move between my Mac, Safari, and the pendant; if any link drops, resume from the last verified step and tell me only what still needs me.”"
- **useful because:** This is the highest-value hive behavior: a spoken task should not die because Safari stopped heartbeating, the Mac agent restarted, or the pendant moved off USB. The relay would hold a step graph; the Mac and extension would checkpoint verified state; the pendant would carry the task identity and truthful stale/offline indication. On reconnect, the system resumes only from a proof-bearing checkpoint instead of repeating a side effect or claiming success.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime handles the initial conversation and terse exceptions. A background model plans/reconciles checkpoints and produces the final 'needs you' list. Deterministic Mac/browser dispatch performs already-approved steps; the model is not called for every heartbeat.
- **latency:** Dispatch and link-loss notification under 2 seconds. Reconciliation within 10 seconds of a bridge heartbeat. Long tasks can run for hours while the owner is away; no polling conversation is required.
- **cost:** Roughly $0.02–$0.10 per multi-step task, mostly checkpoint reconciliation and final summarization. Heartbeats and state hashes should be non-LLM and cheap.
- **security:** A stale browser tab or changed DOM can make a resumed click dangerous. Every mutation needs target fingerprint, expected pre-state, idempotency key, and post-state evidence; never replay a step whose state is unknown. Keep private page contents local and require the owner only for genuinely ambiguous or irreversible steps, not routine progress.
- **missing:** Boot-time reconciliation of processing jobs and closure of the currently always-open action ledger; A durable cross-surface checkpoint graph with job↔ledger↔browser request joins, leases, and exactly-once step identities; Process-group cancellation/reaping and resumable shell semantics, plus browser heartbeat lease handoff; A relay task stream consumed by the pendant's truthful_action_status_beacon and offline outbox

### "“Undo everything that task changed, across my Mac and Safari, and leave anything you couldn’t safely undo untouched.”"
- **useful because:** The current receipt/undo machinery can reverse only a few action types; a multi-step task can leave half-applied files, settings, and browser mutations with no owner-level rollback. A task-scoped compensating transaction would let the owner recover from a bad autonomous run without pretending that irreversible effects are reversible. It would enumerate each effect, apply only proven compensations, and report the residuals.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → unified → faculty-judgement → faculty-action
- **model tier:** Use deterministic compensation handlers first; use a background model only to explain residual effects and order independent compensations. Realtime is reserved for the owner's request and a concise result.
- **latency:** Start rollback within 2 seconds; complete local/browser compensations within the original task's bounded timeout, with pendant progress for each residual. No waiting for a conversational turn.
- **cost:** $0.005–$0.03 per rollback for residual classification; local snapshots and receipts dominate storage, not model tokens.
- **security:** Rollback itself mutates the machine and can destroy legitimate later work. Scope it to the task's effect IDs, require pre/post-state evidence, refuse compensation when post-state diverged, and keep irreversible actions (messages sent, external purchases, deletions without snapshots) explicitly residual rather than fabricating success.
- **missing:** Task-scoped effect manifests with pre-state snapshots or hashes for files, settings, and browser fields; Compensation handlers for shell file mutations and Safari actions, with divergence checks; A rollback route that consumes one task ID and returns compensated, skipped, and irreversible residual effects

### "“Before you act, prove you’re in the right account and workspace; if Mac and Safari disagree, stop and tell me exactly which identity is wrong.”"
- **useful because:** A logged-in Safari tab, the Mac project, and the relay session can all be individually healthy while pointing at the wrong account, profile, or repository. Today the system can execute against a live tab but cannot establish that the tab identity, Mac workspace, and spoken owner intent refer to the same principal. This capability prevents the most dangerous class of apparently successful automation: doing the right action for the wrong person or tenant.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use deterministic local/browser identity probes and exact workspace markers first; use a cheap background model to reconcile conflicting labels. Realtime only asks the owner one precise disambiguation question when evidence conflicts.
- **latency:** Under 3 seconds for cached identity checks; up to 8 seconds for a fresh Safari/Mac probe. No action dispatch occurs before the check reaches verified or explicitly ambiguous.
- **cost:** Usually under $0.01; most checks are local metadata and DOM markers. Model cost occurs only for conflicting evidence.
- **security:** Identity markers themselves can be sensitive. Keep raw emails, tenant IDs, and page contents on the Mac; send only salted fingerprints and human-readable labels to the relay. Never infer identity from a page title alone; require two independent markers and expire them when the tab/profile changes.
- **missing:** A privacy-preserving identity attestation API in the Safari extension and Mac agent; Workspace/account fingerprints bound to browser tab generation, Mac project, relay session, and pendant turn; A pre-dispatch identity-consistency result understood by faculty-action, with a targeted clarification path


## Changes it proposed to its own stack

### `mac-harness` — Instrument run_shell without reducing owner access: use a supervised child process (still permitting arbitrary shell) that records pid/process-group, resolved cwd, start/finish/duration, numeric exit code or terminating signal, timeout cause, and a redacted environment fingerprint; pass AbortController through so cancel terminates the process group. Preserve the exact pre-rewrite submitted action alongside the rewritten action.
- **owner gets:** When a command fails or hangs, the owner can hear whether it timed out, crashed, or was killed and the agent can recover instead of guessing. Cancellation actually stops work rather than merely promising to stop before the next step.
- effort: Medium: replace exec promisify wrapper, extend receipt schema, and wire abort signal; add tests for timeout, SIGTERM/SIGKILL escalation, output caps, and command rewrite provenance.  ·  risk: A process-group kill may terminate descendants the owner expected to survive; retain current behavior behind an explicit execution mode and fall back to parent kill if group setup fails. Never record secret environment values.
- cost: Negligible API cost; modest local CPU/storage for process metadata and capped output.  ·  latency: Near-zero startup overhead; cancellation becomes immediate instead of waiting up to 120 seconds.
- security: No new restriction. Redacted fingerprints improve secrecy, while the exact command remains auditable locally.
- depends on: cross-surface execution envelope with stable attempt IDs

### `context` — Create a single execution envelope at /execute admission and propagate its stable jobId, ledgerId, attemptId, browser requestId, and pendant turnId through every Mac and Safari step. Close the ledger in a finally block, and on boot reconcile processing jobs/open ledgers into explicit interrupted states with a resumable checkpoint rather than leaving them falsely running.
- **owner gets:** A spoken task finally has one answer to “what happened?” and can resume after a Mac crash or bridge outage without silently repeating clicks, shell mutations, or claiming completion. The pendant can display the same task identity and stale age as the Mac dashboard.
- effort: Medium-high: thread IDs through orchestrator and browser bridge, add boot reconciliation, and expose a joined report/checkpoint endpoint.  ·  risk: Incorrect checkpoint classification could skip a needed step or repeat a side effect. Default unknown state to paused and retain the last verified evidence; reconciliation must never auto-replay an unknown mutation.
- cost: Small local JSON/database growth; no per-heartbeat model calls. One extra persisted record per step.  ·  latency: Milliseconds per step for IDs and fsync; recovery adds a few seconds only after restart.
- security: Enables precise access control and redaction boundaries between local raw logs and relay summaries; no increase in action privilege.
- depends on: supervised shell telemetry; browser command lease and request-id propagation; relay task stream for pendant status

### `integration` — Add a pre-dispatch identity-consistency handshake: Safari extension returns a signed tab/profile generation plus privacy-preserving account/tenant fingerprint; Mac agent returns project/workspace fingerprint; relay binds both to the pendant turn and expires the assertion on tab switch, logout signal, or heartbeat gap. Faculty-action receives verified, ambiguous, or mismatch—not a guessed string—and cannot silently dispatch on mismatch.
- **owner gets:** The owner gets a reliable answer to “are you about to do this in the right account?” before an action changes anything, eliminating silent cross-tenant or wrong-project mistakes.
- effort: Medium: extension and Mac probes, signed nonce exchange, session binding, and one new action precondition/result type.  ·  risk: Some sites expose no stable identity marker or intentionally hide it; classify those as unknown and explain the limitation rather than blocking unrelated local work. Handle account switching and Safari private windows explicitly.
- cost: Tiny local CPU and one small heartbeat payload; no recurring model cost.  ·  latency: 1–8 seconds before the first mutation, then cached until the tab generation changes.
- security: Improves isolation, but fingerprints must be salted, short-lived, and never include raw email, cookies, tokens, or page text.
- depends on: Safari extension identity probe; Mac workspace fingerprint probe; relay nonce/session binding


## What it asked for

_Nothing._
## Its own summary

This round I proposed three owner-facing capabilities: automatic Mac shell failure diagnosis/recovery, a unified replayable Mac+Safari evidence report, and the highest-value cross-surface behavior—resume an in-progress task after Mac/Safari/pendant link loss from verified checkpoints. I also proposed two concrete changes: supervised shell telemetry/process-group cancellation without reducing FULL_CONTROL access, and a joined execution envelope with ledger closure and boot-time interruption reconciliation. Current devices show Safari online and the Mac bridge online; the LTE device remains offline. I still need process-supervised shell telemetry, stable job↔ledger↔browser↔pendant IDs, boot reconciliation, and a durable relay task/checkpoint stream. The newly granted mac_read_diagnostics schema still failed resolution, so I could not obtain fresh disk/health facts through that tool.

**Biggest unknown:** Whether the existing browser and ledger routes already expose enough step/checkpoint data to implement the joined envelope, or whether new authenticated report/checkpoint routes are required; no agent has yet inventoried those route payloads end to end.

