# Harness derivation — mac-terminal — round 110

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac/browser execution readiness** — At 2026-08-07T14:19Z, /ops/status reports fullControlMode=true but browser extension online=false with 10 pending commands; computerUse loop disabled, accessibility and screen recording not trusted. A browser_navigate job failed after ~45 seconds rather than fast-failing.
  - evidence: GET /ops/status, GET /browser/status, GET /jobs live responses

## Capabilities it proposed

### "“Why did you do that, and what exactly happened?” Give me a trustworthy, chronological explanation of everything the pendant, relay, Mac, and browser saw, decided, attempted, changed, and failed to do for one request, with links or spoken evidence for each step and a clear list of uncertainties."
- **useful because:** Today the system may have individual job receipts and browser evidence, but the owner cannot reconstruct one request across surfaces: which voice turn caused which relay job, planner decision, Mac command, browser tab operation, and final result. A causal replay makes unattended autonomy understandable, exposes silent partial failures, and lets the owner correct the specific mistaken step rather than rerunning the whole task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified → dashboard
- **model tier:** Use a cheap background model to compress and explain the already-recorded event graph; reserve realtime only for the owner's spoken follow-up. Never ask a model to invent missing evidence: render gaps as unknown.
- **latency:** The event ledger should be written synchronously with each action (under 20 ms local overhead). A concise explanation should arrive in 1–3 seconds from cached events; deep replay can be a background job.
- **cost:** Usually less than one small text-model call per replay (roughly $0.005–$0.03 depending on event volume); most cost is tokenizing long command/output evidence, controlled by hashes, snippets, and tiered retrieval. No speech-model call unless the owner asks by voice.
- **security:** The graph can contain private URLs, page text, voice transcripts, shell commands, and account metadata. Store sensitive payloads locally by default, encrypt ledger segments, send only redacted summaries to relay, enforce per-owner/session access, and require explicit confirmation before revealing secret-shaped fields. Evidence must distinguish observed output from model interpretation.
- **missing:** A single append-only, encrypted cross-surface event ledger with globally unique request/step IDs and causal parent links; An adapter in pendant/relay, planner, browser bridge, and run_shell that emits start, observation, decision, action, result, timeout, and recovery events; A provenance schema linking existing job IDs, action receipts, browser tab/session IDs, audio/pipeline IDs, and shell execution envelopes; A replay API that returns an ordered evidence graph with redaction and confidence/unknown markers; Dashboard and pendant-friendly renderers for concise spoken explanations and drill-down citations


## Changes it proposed to its own stack

### `integration` — Add a cross-surface execution-readiness preflight and short-lived health cache. Before mac-planner or relay enqueues browser_* or computer-use work, query the local agent's /ops/status and /browser/status (with a heartbeat-age check), classify the requested action's prerequisites, and return a typed blocker immediately when the surface is offline, permissions are missing, or the queue is saturated. Include last-seen time, pending-command count, required user remedy, and a retry-after estimate; reconcile/mark stale browser commands so a dead extension cannot accumulate work. Relay and pendant should speak this result instead of waiting for a 45-second timeout. Do not gate or restrict FULL_CONTROL shell actions.
- **owner gets:** The owner gets an honest answer in under a second—“Chrome bridge is offline; enable the extension”—instead of waiting nearly a minute for a failed browser action. It prevents repeated stale commands and makes it clear whether a request can run now, while preserving the owner's maximum-access Mac shell policy.
- effort: Medium: shared readiness schema in mac-planner/local-agent, preflight hooks in browser action dispatch and mac_delegate, stale-queue reconciliation, and relay/pendant rendering. Add tests for offline, stale heartbeat, missing permission, queue saturation, and recovery.  ·  risk: A false offline reading could refuse a task that would have succeeded, so preflight must be advisory for shell and retry once for browser after a fresh heartbeat. Stale-command cleanup must only remove commands with expired leases and retain receipts/audit history. Recovery is automatic on the next heartbeat.
- cost: Negligible API cost; avoids wasting expensive planner/realtime turns and 45-second local waits. Small local state for health snapshots and leases.  ·  latency: Adds roughly 50–200 ms for a cached/local status check, while reducing failed browser attempts from ~45 s to sub-second truthful feedback.
- security: Read-only health metadata crosses Mac→relay (surface state, timestamps, counts), never page contents or credentials. Keep URLs/titles out of the readiness payload and redact permission details to capability names.
- depends on: Existing authenticated /ops/status and /browser/status routes; Existing browser heartbeat/poll and command receipts; Existing relay job status / pendant event path; A durable browser queue/runner or lease semantics (chg-16bc5dee)

### `mac-harness` — Instrument the existing unrestricted run_shell path with a shell execution envelope without changing authorization: normalize the command into an invocation record (cwd, argv-or-raw command, timeout, selected environment keys), capture start/end monotonic times, exit code/signal, timeout flag, bounded stdout/stderr plus full-output hashes, and a best-effort effect class (read, reversible, irreversible, unknown). Attach the envelope to the existing job journal and receipt, and expose a compact version through relay_job_status. For raw shell pipelines that cannot be parsed, preserve the exact command and mark classification unknown rather than pretending it is safe.
- **owner gets:** When the agent runs a command unattended, the owner can finally tell what actually happened, where it ran, whether it timed out, and what output was produced—especially for permanent operations that undo.js cannot reverse. Failures become diagnosable instead of opaque.
- effort: Medium: wrapper around computerControl.runShell, redaction/bounded-output utility, journal/receipt schema migration, and status rendering. Add regression tests for cwd inheritance, timeout, nonzero exit, multiline output, and commands containing secrets.  ·  risk: Command text and output may contain credentials or private data; redact known secret-shaped values, cap inline output, hash/archive only under existing local retention, and never send full stdout/stderr to the relay by default. Parsing must not alter execution semantics. If instrumentation fails, execution should still return its original result with an instrumentation_error field.
- cost: Near-zero model/API cost; modest local disk for bounded receipts. Avoids repeated expensive planner retries by making failures actionable.  ·  latency: Typically under 5 ms plus bounded capture overhead; no additional model round trip and no confirmation gate.
- security: Improves auditability while retaining FULL_CONTROL_MODE and unrestricted network/env as the owner requires. Treat command/output fields as sensitive, apply local-only default, and expose only redacted summaries remotely.
- depends on: Existing /jobs, /journal, and receipt endpoints; Existing actionReceipt schema (chg-5fc73ce3); computerControl.runShell wrapper and job lifecycle


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery: /ops/status and /browser/status show the Mac agent is in FULL_CONTROL_MODE, but the browser bridge is offline, computer-use is disabled, Accessibility and Screen Recording are not trusted, and 10 browser commands are pending. A browser navigation actually waited ~45 seconds before failing. I recorded this finding and proposed two implementation changes: (1) cross-surface readiness/heartbeat preflight with stale-command lease cleanup and truthful pendant/relay feedback, without gating shell; (2) an execution envelope for unrestricted run_shell that records cwd, timing, timeout, exit status, bounded/redacted output, and effect classification in receipts. I also told mac-planner about the live blockers. I do not need another permission this round; the useful next step is implementation of those changes and durable browser queue lease semantics. The granted diagnostic tools still have no implementation, so they cannot provide additional Mac facts.

**Biggest unknown:** Whether the browser extension can be made online and polling without owner interaction, and the exact browser-command lease/heartbeat contract needed to distinguish stale work from an active command.

