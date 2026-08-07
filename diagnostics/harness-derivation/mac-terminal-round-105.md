# Harness derivation — mac-terminal — round 105

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser queue health** — At live inspection, /ops/status reports browser extension online with 9 pending commands, while /browser/poll returns a command created at 09:11:42, claimed at 13:56:44 by home-chrome, status processing, attempts=15. Prior jobs show browser_navigate failures taking ~45 seconds due to offline/no-answer.
  - evidence: GET /ops/status 200; GET /browser/poll 200; GET /jobs and GET /logs 200 showing failed browser_navigate receipts.

## Capabilities it proposed

### "When I leave my Mac in the middle of something, remember exactly where I stopped; when I come back, give me a short spoken 'resume here' briefing and offer to restore the relevant tabs, app, and draft without losing unsaved work."
- **useful because:** Today the owner has to reconstruct interrupted work manually. This would turn the pendant, Mac, browser, and always-on relay into a continuity system: leaving becomes a safe checkpoint, and returning becomes an immediate, low-friction resumption rather than another planning session.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use deterministic local state capture and a cheap background model to summarize the checkpoint; reserve realtime only for the owner's return conversation or ambiguous resume instruction.
- **latency:** Checkpoint capture under 2 seconds after a leave event; return briefing available within 3 seconds of the pendant reconnecting, with restoration actions offered incrementally.
- **cost:** Near-zero for capture and retrieval; roughly $0.001–$0.01 per return summary depending on context size. Cost is dominated by summarizing large browser/app state, so use hashes and deltas rather than resending documents.
- **security:** The checkpoint may contain private page titles, drafts, clipboard content, and window screenshots. Keep raw content on the Mac, encrypt the relay projection, redact secrets/password fields, expire checkpoints, and require an explicit pendant confirmation before reopening tabs or replacing drafts. Never snapshot keystrokes or send unsaved text off-device by default.
- **missing:** Pendant proximity/leave-return events with reliable debounce and a user-configurable privacy mode; Mac checkpoint collector for focused app, window/document identity, unsaved-state indicators, and active task metadata; Browser extension snapshot and restore protocol keyed to tab/session IDs, with draft-safe restoration that never overwrites a page; A durable cross-surface checkpoint schema with local raw state, relay metadata, TTL, and resumability confidence; A resume orchestrator that can compare the old checkpoint with current Mac/browser state and present a reversible restoration plan

### "When I press the pendant button and say “save this moment,” save my words together with what is currently on my Mac screen and in my active browser tab, then later let me ask “what was that thing I saved?” and jump back to the exact evidence and context."
- **useful because:** A spoken thought is often meaningless without the page, code, selection, or document that prompted it. This gives the owner a private, searchable bridge between an in-the-moment pendant note and the exact digital context on the Mac, without requiring them to stop and organize it.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use deterministic capture and local OCR/metadata extraction first; use a cheap background model to title, tag, and embed the bundle; use realtime only when the owner asks to retrieve or disambiguate one.
- **latency:** Acknowledge capture in under 1 second and finish local context collection within 3 seconds. Retrieval should return the matching bundles in under 2 seconds before any optional model explanation.
- **cost:** Usually under $0.005 per capture/retrieval; local screenshot/OCR dominates device work, while cloud cost is limited to short transcription and compact tags. Keep raw screenshots local to avoid repeated upload cost.
- **security:** Screens and browser tabs can contain credentials, health data, or other private material. Capture must be explicitly button-triggered, mask password/secret fields, default to local encrypted storage, attach URL/tab/app/timestamp provenance, and require confirmation before opening or sharing a saved bundle. Provide expiration and delete-all controls.
- **missing:** A pendant button-triggered capture event carrying a short audio clip and monotonic timestamp; A Mac context collector that atomically captures focused window identity, selection/document metadata, and a privacy-filtered screen region; A browser extension command for active-tab DOM/selection capture with sensitive-field masking and session provenance; A unified encrypted evidence-bundle index that links audio transcript, screenshot/DOM snapshot, source URL, app, and timestamp; A retrieval route that can return a cited bundle to the pendant and optionally ask Mac/browser to reopen it


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge liveness controller around the existing command queue: persist command lease/heartbeat timestamps, cap or back off retries, quarantine commands whose lease is stale or whose attempt count exceeds a threshold, and expose queue health (oldest age, claimed duration, attempts, last heartbeat, per-device online state) in /ops/status and the dashboard. When the bridge is offline or repeatedly times out, fail fast with a typed 'bridge_unhealthy' receipt instead of spending ~45 seconds per navigate and leaving nine commands pending; automatically requeue only after a fresh heartbeat, with idempotency preserved.
- **owner gets:** Safari tasks stop hanging for nearly a minute and do not silently accumulate stale work. The owner gets a truthful, immediate explanation and can recover by reopening the extension, while healthy commands still run unattended and maximum Mac access is unchanged.
- effort: Medium: queue schema migration, lease watchdog, retry policy, status aggregation, dashboard card, and tests for crash/reconnect/idempotent requeue.  ·  risk: A slow but valid page could be quarantined too early; use generous lease limits, explicit heartbeat extension, and manual/retry recovery. A process crash during the transition could leave a command in quarantine; provide requeue/quarantine-clear endpoints and retain receipts.
- cost: Negligible API cost; fewer wasted browser action round trips and fewer planner retries. Small local persistence and watchdog overhead.  ·  latency: Healthy actions unchanged; unhealthy actions fail in seconds rather than ~45s, and reconnect recovery is bounded by the next heartbeat.
- security: No new data access. Queue diagnostics should redact URLs/query strings by default and retain full details only in the existing authenticated job record.
- depends on: chg-14accc01 request IDs/idempotency/tab affinity; browser extension heartbeat/poll/result routes; existing action receipts and /ops/status observability

### `mac-harness` — Extend run_shell job receipts with bounded execution telemetry and recovery metadata: argv/command hash, resolved cwd, start/end/queue timestamps, exit code or signal, timeout classification, stdout/stderr tails with secret-pattern redaction, and a captured child-process summary on timeout. Run shell commands in a tracked process group so a timed-out command can be terminated and marked cleanly; expose a 'retry with same inputs' operation that links to the failed receipt and never duplicates a completed job.
- **owner gets:** When a Mac task fails, the owner hears what actually happened—wrong directory, missing binary, permission error, or timeout—instead of a generic failure. The agent can recover faster from the known project-location problem and avoid leaving hidden child processes running after a timeout.
- effort: Medium: instrument computerControl.runShell/executor, add bounded/redacted output storage and process-group cleanup, extend receipt schema and dashboard/job API, and test exit/timeout/partial-output cases.  ·  risk: Command output can contain secrets or large logs; cap bytes, redact common tokens, and keep full raw output out of relay/pendant responses. Process-group termination can kill children intentionally spawned by a command; record the signal and make retry explicit in the job API. Existing old jobs remain readable with absent telemetry.
- cost: Near-zero model cost; a small local disk increase bounded per receipt and less repeated planner work after failures.  ·  latency: A few milliseconds of instrumentation; timeout failures become promptly diagnosable and cleanup is deterministic.
- security: Improves auditability without reducing FULL_CONTROL_MODE. Store telemetry locally behind existing bearer auth; send only a sanitized summary to relay.
- depends on: existing action receipts at local-agent/actionReceipts.js; existing GET /jobs and GET /jobs/:jobId/receipts; computerControl.runShell timeout path and current unrestricted FULL_CONTROL_MODE


## What it asked for

_Nothing._
## Its own summary

I re-discovered the live routes, grants, backlog, and Mac observability. The key fresh fact is a browser queue pathology: the extension currently reports online, but there are 9 pending commands and /browser/poll returns a command created hours earlier, still processing after 15 attempts. Recent browser navigations consumed ~45 seconds before failing. I recorded this and proposed a health-aware lease/circuit-breaker queue. I also proposed bounded shell telemetry and process-group cleanup/retry metadata, preserving the owner's deliberate FULL_CONTROL_MODE and adding no gates. Live Mac status is otherwise healthy; relay is reachable. No additional permission request is needed from me this round.

**Biggest unknown:** The actual browser extension heartbeat/result implementation and lease semantics remain unverified; the route table advertises heartbeat/cancel endpoints, but the describe responses expose a GET/POST mismatch. Implementers need to confirm the POST contracts, stale-lease thresholds, and whether the 15-attempt command can be safely quarantined/requeued without duplicating a browser action.

