# Harness derivation — mac-terminal — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Run this Mac task, and keep me informed until I know whether it really finished—even if the Mac or link drops.""
- **useful because:** Today a shell can run unattended but cancellation cannot stop a running process, jobs can remain 'processing' forever after restart, and the pendant can only show the last coarse state. This would make remote execution trustworthy: the owner gets truthful progress, a durable outcome, and exactly-once recovery across the worn device, Mac, and relay.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** Use the realtime tier only for the initial spoken acknowledgement and final short result; use a background relay worker for polling, reconciliation, and retry.
- **latency:** Acknowledge in under 1 second; status heartbeat every 2–5 seconds; recovery after reconnect within 10 seconds; no extra model call for each heartbeat.
- **cost:** Low API cost: mostly typed HTTP and local process supervision; one short realtime turn per request. Dominant cost is occasional background summarization when stdout is large.
- **security:** The Mac still retains maximum owner-authorized execution. Do not transmit raw environment variables or command output by default; send redacted receipts and hashes, with full output available only through the authenticated dashboard. Require explicit idempotency keys before replaying side effects.
- **missing:** A process-group-aware executor that records exit code, signal, pid, and durable checkpoints; Boot reconciliation that marks orphaned jobs and closes ledgers before offering resume; A relay state machine joining pendant request IDs, Mac job IDs, and ledger IDs; Pendant status beacon integration for queued/running/stale/recovered states

### ""Save a receipt for this task that lets me or another agent reproduce exactly what happened on my Mac.""
- **useful because:** Shell history is not a reproducibility record: the current system loses exit codes and pids, passes an unrecorded full environment, can rewrite commands before dispatch, and cannot reliably join a job to its action ledger. A compact signed run bundle would turn an opaque one-off command into something the owner can inspect, hand to another agent, or rerun safely.
- **path:** mac-planner → mac-vision → browser-extension → relay → dashboard
- **model tier:** Background/cheap model for redaction and summarization; no realtime model unless the owner asks for a spoken explanation.
- **latency:** Capture synchronously with execution; receipt visible within 2 seconds after completion; summaries under 3 seconds for ordinary jobs.
- **cost:** Near-zero model cost for typed metadata and hashes; background summarization costs one small request only when requested. Storage is the dominant cost, bounded by a per-run size cap.
- **security:** Never persist secrets from env, cookies, browser content, or command output without an explicit opt-in. Store an environment allowlist plus hashes, cwd, git revision/diff summary, effective rewritten action, exit status, signal, timing, and output digests. Any replay must display side-effect classification and use the existing owner-authorized maximum-access policy.
- **missing:** A canonical run-bundle schema and redaction layer; Capture of effective (post-rewrite) action alongside the originally submitted action; Exit code/signal/pid and process-tree capture for run_shell; Stable jobId↔ledgerId↔receiptId correlation and a GET /runs/:id export route

### ""Pick up where I left off.""
- **useful because:** The owner should not have to remember which terminal job, project, browser tab, or voice turn contained the unfinished work. This would reconstruct a bounded, inspectable handoff from the last pendant marker plus Mac execution receipts, active project, and authenticated browser session, then state the next safe step before doing it. It is useful precisely because no single node can see all of that context.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard → unified
- **model tier:** Cheap background model builds the candidate handoff from structured records; realtime tier only speaks the two-sentence confirmation when requested from the pendant.
- **latency:** Candidate in 2 seconds from cached records; browser/session inspection under 5 seconds; ask one concise clarification only when confidence is low.
- **cost:** Low: structured joins dominate, with one small background synthesis call. Browser inspection and Mac status are the latency costs, not model tokens.
- **security:** Authenticated browser data must remain on the Mac/browser boundary; send only titles, URLs, and explicitly selected snippets. Never silently resume a mutation. Show source records and stale ages, and distinguish an unfinished process from a merely open tab.
- **missing:** A cross-surface handoff record keyed by the existing pendant moment marker; A join service for pendant marker, Mac job/receipt, active project, browser session, and voice turn IDs; A freshness/confidence score and stale-context warning; A bounded resume planner that can propose but not silently replay prior side effects

### ""I’m about to close the lid—tell me what I’d lose, and leave everything in a state I can resume tomorrow.""
- **useful because:** Today the owner cannot get one truthful pre-sleep handoff spanning unsaved Mac work, active terminal jobs, authenticated browser tabs, queued pendant audio, and the current voice turn. This would prevent the expensive failure mode of closing the lid and discovering tomorrow that a job, draft, browser workflow, or spoken instruction was lost.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay → dashboard
- **model tier:** Background model assembles a structured risk report; realtime model speaks only the short result over the pendant.
- **latency:** A cached risk scan in under 3 seconds; a full browser/tab and job reconciliation in under 15 seconds. The owner can close the lid only after the report has a durable receipt.
- **cost:** Low model cost; the work is host inspection and typed state capture. Storage is bounded to one handoff record per sleep event.
- **security:** Do not copy document contents or authenticated page bodies into the relay. Keep sensitive details on the Mac, send counts, titles, hashes, and stale ages. Never claim a document is saved without an application-specific acknowledgement.
- **missing:** A Mac sleep/lid event hook exposed to the local agent; Application adapters that can distinguish saved, dirty, and conflicted documents; A cross-surface sleep-handoff transaction joining jobs, browser sessions, pendant outbox, and voice turn state; A durable resume manifest and a dashboard view of what was guaranteed versus merely observed

### ""My Mac may be compromised or lost. Lock down my digital life now, and tell me exactly what you managed to revoke.""
- **useful because:** There is no single owner-facing emergency action that coordinates the Mac agent, authenticated browser sessions, relay jobs, and pendant. A compromised or missing Mac leaves stale browser sessions, running work, and queued sensitive audio with no unified, truthful containment report.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime tier handles the urgent spoken acknowledgement; deterministic background workers perform revocation and produce the receipt. No generative model is needed for the actual lockdown.
- **latency:** Acknowledge locally in under 1 second; revoke reachable browser sessions and cancel queued relay work within 10 seconds; report unreachable surfaces separately rather than waiting indefinitely.
- **cost:** Minimal model cost. The dominant cost is provider-specific session revocation and retrying unreachable nodes.
- **security:** This is intentionally destructive and must require an explicit owner phrase or dedicated physical action, with a second spoken confirmation when the Mac is still reachable. Never transmit credentials to the relay. Store only revocation receipts, timestamps, and failure reasons; retain no page contents.
- **missing:** Provider-aware browser session revocation rather than only deleting local session records; A relay-side emergency-stop endpoint for queued and in-flight work; A pendant-side emergency command that survives a missing Mac and LTE reconnection; A cryptographically chained containment receipt that distinguishes requested, attempted, confirmed, and unreachable

### ""Find the exact thing I was looking at or talking about yesterday, and open the source—not a guess.""
- **useful because:** The owner currently has fragments in browser tabs, terminal output, project state, captured voice turns, and relay records, but no provenance-first search across them. This would answer with the exact source, timestamp, and confidence, then open it on the Mac or browser, instead of hallucinating from a summary.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard → unified
- **model tier:** Cheap background retrieval/reranking over local indexes; realtime tier only reads the final answer. Use the expensive model only when the retrieved evidence conflicts.
- **latency:** Return top evidence in 3 seconds from indexes; open the selected source within 5 seconds; if confidence is low, ask one clarifying question rather than fabricate.
- **cost:** Low recurring cost after local indexing; occasional embedding/index maintenance is the dominant compute. Do not send raw local files or authenticated page bodies off-device.
- **security:** Index metadata and content locally on the Mac. Browser session material stays inside the extension. Relay receives opaque result IDs and small redacted snippets only. Every answer must include provenance and age; opening a private page should require the owner’s ordinary request context.
- **missing:** A local unified index over shell receipts/stdout, browser tab metadata, project files, captures, pipeline turns, and relay briefings; Stable provenance IDs that survive job rotation and browser tab closure; A cross-surface retrieval route returning source, timestamp, excerpt, and confidence; Mac/browser actions that open a cited source by provenance ID


## Changes it proposed to its own stack

### `mac-harness` — Replace run_shell's exec(string) supervision with a process-group supervisor while preserving FULL_CONTROL_MODE: launch through a dedicated group, capture pid/exit code/signal/start-finish/duration, pass AbortSignal to the child, and on cancel terminate the whole group. Persist the originally submitted action and the effective rewritten action side by side, then close the orchestrator ledger and link it to the job before settlement.
- **owner gets:** A command that hangs, spawns children, or is interrupted by Mac sleep would stop predictably instead of running invisibly for two minutes or leaving a forever-running record. The owner could tell what actually ran and resume only the unfinished work after reconnect.
- effort: Medium: executor and receipt schema changes, boot reconciliation, ledger close/join tests, and macOS process-group edge cases.  ·  risk: A group kill could terminate a child the owner wanted to survive; preserve current behavior behind an action flag and report descendants before kill. Existing jobs remain readable through a migration adapter. Crash recovery must mark uncertain jobs 'interrupted', never 'completed'.
- cost: Negligible API cost; a few kilobytes of metadata per action and bounded receipt storage.  ·  latency: No meaningful latency change; cancellation becomes immediate rather than waiting for the command timeout.
- security: No new authority. Avoid recording environment values; record only an allowlisted key fingerprint and redacted metadata.
- depends on: A durable run-bundle/correlation schema; A boot-time job/ledger reconciliation pass


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) trustworthy cross-device task completion and recovery when the Mac/link drops, (2) reproducible run receipts for shell/browser work, and (3) 'Pick up where I left off' handoff joining the pendant marker, Mac jobs, active project, browser session, and voice turn. I also recorded the concrete Mac-harness change for process-group supervision, exit-code/signal capture, effective-vs-submitted action recording, cancellation, and ledger closure. What these need is connective work between already-live routes, not another planner surface.

**Biggest unknown:** The live route inventory still does not establish whether a run-bundle export or ledger-resume implementation is actually callable end-to-end; the recorder specifically warned not to assume GET /ledger/:ledgerId/resume is absent. The pending mac_usb_serial_diagnostics request remains unavailable, so I still cannot verify the physically connected pendant/ESP32 serial state from this agent.

