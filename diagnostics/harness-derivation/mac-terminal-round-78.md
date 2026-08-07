# Harness derivation — mac-terminal — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac observability tools** — The newly granted mac_read_diagnostics/mac_readonly_diagnostics interfaces still return 'no implementation yet', so live host diagnostics must currently come from authenticated HTTP snapshots or existing run actions.
  - evidence: Three calls in Round 78 to mac_readonly_diagnostics(query=permissions/processes/disk) all returned tool-granted schema but no implementation; mac_read_diagnostics likewise returned the same.

## Capabilities it proposed

### "“Keep this terminal task alive while I leave, and when I come back let me continue it from exactly where it stopped—without starting over.”"
- **useful because:** Today a long shell task is tied to a request/HTTP lifetime and can disappear behind a timeout or bridge disconnect. The owner cannot reliably leave a build, export, backup, or research command running, return later through the pendant, inspect only the unseen output, and resume after a Mac or agent restart. This would make the pendant a dependable remote terminal companion rather than a one-shot command launcher.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background for status, deterministic for cursor/lease bookkeeping, planner only when the owner asks to interpret a failure or choose a continuation command; realtime is used only to speak the concise status through the pendant.
- **latency:** Acknowledge launch or reconnect in under 500 ms; status and unseen-output retrieval in under 2 seconds. Interpretation or continuation planning may take 2–5 seconds.
- **cost:** Near-zero for launch/status/reconnect because these are deterministic. Occasional background/planner call costs roughly one short request only when interpreting output or constructing a continuation; local spool and relay metadata dominate storage, not API spend.
- **security:** A detached process can continue using CPU, files, credentials, or network after the owner leaves. Require explicit long-running intent, a maximum lifetime and disk quota, visible lease status, and pendant cancellation; do not auto-retry. Keep raw output on the Mac with TTL deletion and send only redacted tails/summaries to relay. Restrict status access to the paired owner.
- **missing:** A Mac process supervisor that owns process groups independently of HTTP requests; Durable lease, output-cursor, and bounded spool records surviving bridge/agent restart; Reconnect/unseen-output and explicit process-group-cancel operations; Pendant/relay protocol for long-running job status and cancellation; Dashboard UI for active leases, age, resource use, and last output cursor


## Changes it proposed to its own stack

### `mac-harness` — Add a reconnectable process lease for long-running run_shell work. When a shell action is intentionally marked long-running, launch it under a local supervisor with a durable jobId/lease, process-group ID, monotonic output cursor, heartbeat, and bounded spool on disk; decouple process lifetime from the HTTP request and Mac bridge connection. GET /jobs/:jobId and relay_job_status should report running/stalled/exited with the last cursor and timestamps; a reconnect operation should stream only unseen output, and cancel should terminate the whole process group. Do not auto-retry or change FULL_CONTROL_MODE; this is continuity and explicit recovery, not a gate.
- **owner gets:** A research, build, export, or backup task keeps working when the pendant conversation ends or the relay briefly disconnects. On return, the owner hears exactly whether it finished, where it stopped, and the new output only—without accidentally launching a second copy or losing the useful tail of a long command.
- effort: Medium-high: supervisor process, durable spool/lease state, cursor API, bridge reconnect handling, process-group cancellation, crash recovery and cleanup, dashboard and relay status integration.  ·  risk: Detached processes can outlive the owner's intent or consume CPU/disk. Require an explicit long-running intent in the action payload, enforce an owner-configured maximum duration and spool quota, mark leases stale after heartbeat loss, and expose cancel; on agent restart, reconcile child processes by supervisor metadata and report unknowns rather than killing unrelated processes. Output may contain secrets, so local-only raw spool with redacted summaries to relay and TTL deletion.
- cost: No additional model calls for normal execution; small local disk/RAM spool and one supervisor process per active job. Relay status remains a cheap read.  ·  latency: Immediate acknowledgement in under 100 ms; reconnect status is sub-second plus output transfer, instead of waiting for a 120-second request timeout.
- security: Preserves the owner's deliberate unrestricted execution while adding lifecycle visibility, not permission checks. Process IDs, cwd, and output tails need local access controls; never expose raw spool to unauthenticated relay clients.
- depends on: GET /jobs/:jobId; POST /jobs/:jobId/cancel; GET /journal/:jobId; GET /ops/snapshot; describe:relay_job_status; existing action receipts and durable job tracker


## What it asked for

_Nothing._
## Its own summary

Recorded the owner-facing capability for explicit, reconnectable long-running terminal work: launch from the pendant, survive bridge/request disconnects, return only unseen output, survive agent restart, and cancel the process group explicitly. This is narrower and more concrete than generic background-job status, and requires a Mac supervisor, durable lease/cursor spool, relay protocol, and pendant/dashboard controls.

**Biggest unknown:** Whether an existing implementation already covers durable process supervision and output cursors; discovery tools were removed before that could be checked.

