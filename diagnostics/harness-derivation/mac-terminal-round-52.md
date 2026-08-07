# Harness derivation — mac-terminal — round 52

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution observability gap** — FULL_CONTROL_MODE is active and /ops/status reports browser offline with 3 pending commands; /jobs shows browser_navigate failures taking ~45s and receipts only say failed/no change. Routing shows planner requests spend ~8.6k prompt tokens versus background ~2.2k. There is no structured shell failure diagnosis or command-level resource/stream metadata.
  - evidence: GET /ops/status, GET /jobs, GET /routing on 2026-08-07

## Capabilities it proposed

### "Run this on my Mac, and if anything goes wrong, keep investigating until you can tell me exactly what happened and whether it is safe to retry."
- **useful because:** Today a failed unattended shell job can end as a generic error or timeout, leaving the owner unsure whether it never started, partially changed files, or can be retried. This would turn the pendant into a reliable remote operator: the owner can walk away, then receive a precise, evidence-backed outcome rather than manually reconstructing Mac state.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Use deterministic local classification and probes first; use a cheaper background model only to synthesize an ambiguous diagnosis. Use realtime only to speak concise progress or the final receipt during conversation.
- **latency:** Start acknowledgement under 1 second; stream queued/started/completed phases as available. Deterministic failure diagnosis under 1 second after command exit; no automatic long retry unless the owner explicitly asks for it.
- **cost:** Usually negligible API cost: local execution and classifiers do the work. Ambiguous cases may use one small background call (roughly 2k–4k context tokens); realtime cost is limited to the spoken summary.
- **security:** Shell authority remains unrestricted by owner policy. Raw command output may contain credentials or private data, so keep full output on the Mac, redact credential-shaped values in relay payloads, send bounded tails and hashes by default, and require explicit owner direction before exposing raw logs or retrying a possibly mutating command.
- **missing:** A shared shell execution receipt schema carrying cwd, command hash, exit code/signal, timeout, duration, bounded stdout/stderr, and reversibility metadata; An executor-level event stream from Mac to relay and pendant, rather than only a final job record; Deterministic failure classifiers and bounded post-failure diagnostics for cwd/path, permissions, timeout, missing app, network, and nonzero exit; Explicit retry/idempotency metadata so the planner can distinguish diagnosis from safe replay; Dashboard and spoken rendering for evidence, partial completion, and a clear retry recommendation


## Changes it proposed to its own stack

### `mac-harness` — Add a non-gating Shell Execution Envelope around the existing FULL_CONTROL run_shell path. Preserve arbitrary commands and unattended execution, but emit a typed per-command receipt: command ID and SHA-256 (not plaintext in cross-surface summaries), resolved cwd, start/queue times, timeout, exit code/signal, duration, stdout/stderr byte counts plus bounded tails, touched-file hints where observable, and whether the result is reversible. On failure, run a small deterministic diagnosis pass (ENOENT/cwd, permission, timeout, missing app, network/DNS, nonzero exit) and attach concrete next-step or retry parameters; stream phase events to relay/pendant and dashboard, and persist full detail locally with configurable retention. Add idempotency metadata so the planner can deliberately retry a failed command without accidentally replaying a mutation.
- **owner gets:** When the owner says “do it” from the pendant, they get a useful completion or failure explanation instead of a vague timeout—especially after the Mac has gone offline, a path is wrong, or a command partially ran. They can leave the Mac unattended and later hear exactly what happened, where it ran, and whether retrying is safe, without sacrificing the maximum-access policy.
- effort: Medium: executor wrapper, streaming event schema, local receipt storage/retention, deterministic classifier, relay/dashboard rendering, and planner prompt/tool result integration.  ·  risk: Capturing output can expose secrets, and touched-file inference can be incomplete. Redact known credential-shaped values, keep full stdout/stderr local by default, cap tails, and mark inference as best-effort. A retry recommendation must never imply success; duplicate mutation risk is handled by explicit idempotency/retry metadata, not by blocking execution.
- cost: Near-zero model/API cost for deterministic classification; modest local disk for bounded receipts. A small background model call is optional only when deterministic diagnosis is inconclusive.  ·  latency: No meaningful added latency on success if events are written asynchronously; failure diagnosis should be under 200 ms, with no automatic long retry.
- security: Improves auditability without narrowing authority. Cross-surface payloads carry hashes, redacted summaries, and bounded tails; raw command/output remains on the Mac unless the owner explicitly requests it.
- depends on: Existing job receipts and /jobs/:jobId/receipts; Relay pipeline event delivery and dashboard job view; A shared action/result schema used by Mac planner, relay, and pendant


## What it asked for

_Nothing._
## Its own summary

Fresh probes confirm the Mac is in deliberate FULL_CONTROL_MODE, while the browser is offline with 3 queued commands and recent browser jobs fail only after ~45 seconds. I recorded this and proposed a new, non-gating Shell Execution Envelope: structured command receipts, bounded/redacted output, deterministic failure diagnosis, streamed pendant/dashboard progress, retention, and explicit retry/idempotency metadata. It preserves maximum access and adds no approval gates. I do not need another permission or tool this round; implementation needs a shared receipt/event schema plus relay/dashboard integration.

**Biggest unknown:** Whether the existing receipt implementation can be extended at the executor boundary without breaking current /jobs and /jobs/:id/receipts consumers; the local-agent route/job lifecycle contract remains unavailable.

