# Harness derivation — mac-terminal — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness** — Live /ops/snapshot shows FULL_CONTROL_MODE and token configured, but machine readiness is false because Accessibility is untrusted and Screen Recording is missing; browser extension is offline with 3 pending commands. Relay is reachable and Mac bridge online.
  - evidence: GET /ops/snapshot HTTP 200, status.agent.permissions and status.agent.browser fields

## Capabilities it proposed

### "“Run this terminal workflow in the background, keep me posted at meaningful milestones, and if it fails, explain the exact failing command and let me resume from there.”"
- **useful because:** Today a long shell command is an opaque one-shot job: the owner cannot tell whether it is progressing, what it changed, or where to restart after a timeout/crash. This makes the Mac genuinely useful while the owner is away, with the pendant as the status/control surface rather than requiring them to reopen the Mac.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Use the normal planner only to decompose the request and classify milestones; execute commands directly on the Mac. Use the relay's durable state for job events and a cheap background model to summarize stdout/stderr on completion or failure. Realtime is only for the owner's live follow-up.
- **latency:** Acknowledge immediately (<1 s); first milestone within 2 s; stream only phase transitions and bounded failure excerpts, not every output line. Completion/failure summary within 5 s of process exit.
- **cost:** Low: one planner call per handoff and a small background summarization call only when output is large; dominant cost is the existing realtime turn if the owner asks follow-ups. Raw command output remains on the Mac unless explicitly summarized.
- **security:** This preserves the owner's deliberate unrestricted FULL_CONTROL_MODE and adds no gate. Shell output may contain secrets, tokens, or personal paths, so relay events should carry redacted metadata plus short excerpts by default; full output stays local and is fetched only on request. Never silently rerun a non-idempotent command; resume must use explicit checkpoint IDs and the original command hash.
- **missing:** A durable Mac shell-session/job protocol with command IDs, phase/checkpoint events, stdout/stderr capture limits, heartbeat, cancellation, and restart-safe resume; Relay event storage and pendant notifications for Mac job milestones; A planner-visible command manifest that marks each step idempotent, retryable, or manual-resume-only; A local redaction and artifact store so large logs do not enter model context

### "“While I’m away, keep a private change ledger for my Mac, and when I ask ‘what changed?’ give me a concise, trustworthy answer with the commands, apps, and files involved—separating changes made by you from changes made by everything else.”"
- **useful because:** The owner cannot currently distinguish an agent's effects from changes made by sync tools, installers, editors, or other processes. Existing action receipts explain completed agent jobs, but they do not provide a time-bounded baseline of the whole Mac or explain unexplained drift. A pendant request on return should produce an evidence-backed answer without uploading the owner's files by default.
- **path:** mac-planner → relay → pendant → dashboard-ux
- **model tier:** Use a local Mac collector for filesystem/process/app event metadata and hashes; use a cheap background model to summarize the resulting event set. Use realtime only to answer the owner's spoken follow-up. Keep file contents local unless the owner explicitly asks for one.
- **latency:** Low-overhead collection continuously or in bounded sampling windows; answer a normal query in under 3 seconds from the local ledger, with deeper historical analysis taking under 30 seconds.
- **cost:** Near-zero model cost for collection; one small summarization call per query when event volume is high. Disk cost is a rotating metadata ledger, with configurable retention.
- **security:** The ledger itself can reveal filenames, applications, and private activity. Store it encrypted/local-first, redact sensitive paths in relay summaries, and transmit only aggregates and evidence references by default. Hashes must not be presented as proof of authorship; show confidence and distinguish observed process identity from inferred causality.
- **missing:** A local filesystem/process/app event collector with bounded, rotating retention; A causal attribution schema linking observed events to agent job IDs, receipts, and known external processes; A privacy-preserving relay query that returns summaries and evidence references without copying file contents; Pendant and dashboard views for time-window selection and confidence-aware change reports


## Changes it proposed to its own stack

### `mac-harness` — Add a resumable shell-runner beneath run_shell: create a job manifest with stable step IDs and a command hash, execute each step in its own process group, persist bounded stdout/stderr and exit metadata locally, emit heartbeat/phase events, and write a checkpoint only after successful completion. Expose status, tail, cancel, retry-failed, and resume-from-checkpoint operations; resume refuses to replay a completed step unless the planner explicitly marks it idempotent. Attach these events to the existing action receipts and relay job stream rather than replacing receipts or adding approval gates.
- **owner gets:** A terminal task can continue safely after the owner leaves, show real progress on the pendant, and recover from a failed step without rerunning the entire workflow or guessing what happened.
- effort: Medium-high: new local-agent shell job runner plus event persistence, relay forwarding, planner schema, and pendant status controls; integration tests for timeout, crash, cancellation, and non-idempotent steps.  ·  risk: A process may leave child processes or partial side effects after cancellation; use process-group teardown, explicit dirty/unknown state, and never auto-resume an uncertain step. Log truncation could hide useful context, so retain a local full artifact with bounded relay excerpts. Existing one-shot run_shell remains unchanged as a fallback.
- cost: Small local disk usage with rotating per-job artifacts; negligible API cost for event transport, with optional cheap summarization of large logs.  ·  latency: Immediate acknowledgement and low-latency milestone events; process startup adds roughly tens of milliseconds per step, while resume avoids repeating long work.
- security: No new authority and no reduction of FULL_CONTROL_MODE. Keep full logs local by default, redact common credentials before relay/model transmission, and record command hashes plus touched paths in the existing receipts.
- depends on: The existing action receipt/undo implementation (chg-5fc73ce3); A relay endpoint and durable event schema for Mac job progress; Planner support for step idempotency and checkpoint manifests

### `dashboard-ux` — Add a live Mac readiness panel and machine-readable readiness contract: distinguish required permissions from optional capabilities, show the exact blocked operation (for example, mac-vision unavailable because Accessibility and Screen Recording are not granted), last heartbeat, browser connectivity, and the safest recovery action. Let mac-planner request a one-click/open-System-Settings route and re-probe automatically after the owner changes a permission; publish the same concise state to the pendant instead of exposing raw ops JSON.
- **owner gets:** The owner currently experiences a silent failure or an agent that says it cannot see the screen. They should immediately know what is missing, where to fix it, and when the Mac has become usable again—especially when they are wearing the pendant away from the dashboard.
- effort: Small-medium: normalize /ops/status into a versioned readiness schema, add dashboard cards and pendant-friendly summaries, and implement a permission-change re-probe loop.  ·  risk: Permission labels can become stale or incorrectly imply that a capability is available; timestamp every probe and keep the raw diagnostic detail available. Opening System Settings should be reversible and never claim success until a fresh probe confirms it.
- cost: Negligible API/model cost; a few local probes after a settings change.  ·  latency: Adds one lightweight probe after recovery, typically sub-second; no impact on ordinary shell execution.
- security: Only reports permission state and app names already visible to the local agent; do not transmit window contents or screen frames. No execution gates are introduced.
- depends on: A stable /ops/status readiness schema; Existing Mac dashboard and relay-to-pendant status path

### `mac-harness` — Build a local-first change ledger independent of action receipts: sample filesystem metadata and process/app activity into rotating time buckets, correlate events with agent job/action IDs when available, and label attribution as direct, likely, or unknown. Store only paths, sizes, timestamps, hashes, process identity, and event references by default; retain file contents nowhere unless explicitly captured. Add a query API that returns a signed time-window manifest and evidence pointers for the planner and relay.
- **owner gets:** After leaving the Mac unattended, the owner can ask exactly what changed and get a useful answer even when the agent did not cause it, instead of relying on guesses or a partial list of agent receipts.
- effort: High: native event collection and permission-aware fallbacks, local encrypted rotation, correlation with existing jobs, query/signature format, and tests across sync, editor, installer, and agent activity.  ·  risk: Event streams may be incomplete or noisy, and process attribution can be ambiguous; report coverage and confidence rather than claiming certainty. Metadata can expose sensitive filenames, so default retention must be short and deletion must be verifiable. Collection should degrade gracefully when permissions are absent.
- cost: Low ongoing CPU/disk overhead if event sampling is bounded; no routine model cost. A modest local encrypted ledger is required, with configurable retention.  ·  latency: Minimal background overhead; common time-window queries should be near-instant from indexes, while correlation across large windows may take seconds.
- security: Improves accountability without granting new control authority. Keep raw ledger on the Mac, encrypt at rest, and send only redacted aggregates/evidence references through relay unless explicitly requested.
- depends on: A local encrypted metadata store and retention/deletion mechanism; Correlation hooks into existing action receipts and job IDs; A versioned relay query/result contract and confidence-aware summary UI


## What it asked for

_Nothing._
