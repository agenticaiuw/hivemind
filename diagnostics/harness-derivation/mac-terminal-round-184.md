# Harness derivation — mac-terminal — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say 'finish this on my Mac', keep going across a reboot or dropped USB link and tell me exactly what remains when I come back."
- **useful because:** Today a job can remain falsely processing after restart, cancellation cannot stop a running shell, and the pendant/relay cannot resume a partially completed multi-step task. This would make spoken delegation dependable rather than fire-and-forget.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → dashboard
- **model tier:** background for checkpoint classification and recovery planning; realtime only for the owner's short status question
- **latency:** Acknowledge dispatch under 1 s; recover automatically within 10 s of Mac/USB return; status query under 2 s.
- **cost:** Usually <$0.01 per task using background reasoning; dominant cost is model calls only when a checkpoint needs interpretation, not every shell step.
- **security:** Commands remain unrestricted per owner policy. Persist only redacted action metadata and checkpoint outputs; never persist inherited secrets or raw environment. Require explicit owner confirmation before replaying an action whose prior completion is unknown.
- **missing:** boot-time reconciliation of pendant-jobs.json and open ledgers; jobId linkage into action ledgers; per-step idempotency/replay tokens and durable checkpoints; USB serial transport between pendant and Mac bridge; process-group cancellation for run_shell

### "Run this command and give me a trustworthy answer: what changed, how long it took, whether it really succeeded, and what I can undo."
- **useful because:** The current shell path loses exit codes, PIDs, environment provenance, and full timing semantics; rewrites can make the recorded action differ from the submitted command. A receipt that explains outcome would prevent confident but false answers after failures or timeouts.
- **path:** mac-planner → mac-vision → dashboard → relay-realtime → pendant
- **model tier:** No realtime model for collection; deterministic host instrumentation first, cheap background model only to summarize ambiguous stderr.
- **latency:** No more than 50 ms overhead per command; spoken summary within 1 s after completion.
- **cost:** Near-zero API cost for structured receipt generation; <$0.002 only when stderr needs summarization. Storage is bounded ring storage.
- **security:** Hash and redact env keys, never store values or tokens. Capture command, resolved executable/argv, cwd, start/finish, exit code, signal, pid/pgid, timeout, rewrite provenance, bounded stdout/stderr hashes and excerpts. Keep owner policy of unrestricted execution; this is observability, not a gate.
- **missing:** execFile/exec with process-group and exit/signal capture; pre-dispatch and post-rewrite command identity in receipts; redacted environment fingerprint; a single job-to-ledger correlation field; dashboard and spoken receipt renderer

### "Press the pendant and say 'what is my Mac doing right now?'—answer with the active app, current browser page, running delegated work, and whether the USB voice path is healthy, without opening my microphone."
- **useful because:** No single node can establish this: the pendant supplies immediate intent and local link state, the Mac sees foreground/UI and jobs, Safari holds private sessions, and relay stitches it into one current answer. It is the system's most useful everyday status interaction.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic aggregation for machine facts; realtime model only to phrase the final spoken answer, with background cache refreshes.
- **latency:** Button-to-first-tone under 300 ms; complete spoken answer under 2 s, using last-known facts if a surface is slow.
- **cost:** <$0.001 per query when deterministic; occasional realtime phrasing dominates. No page contents leave Safari unless the answer explicitly needs them.
- **security:** Default to tab title/origin and active-app metadata, not page text; redact URLs/query strings and secrets. Do not claim live state when stale—speak age and surface availability. No microphone open beyond the already-triggered button interaction.
- **missing:** USB serial bridge transport and pendant event ingestion; Mac route for active app/window and bounded browser tab metadata; relay-side freshness/availability aggregator; a read-only spoken-status intent distinct from conversation recording; stale-state policy shared by beacon and dashboard

### "I'm leaving my desk—take this task with me, and when I come back put me exactly where I left off."
- **useful because:** Today the Mac, browser, relay, and pendant each know fragments of a task but none can package an interrupted desktop moment into a portable, resumable handoff. The owner loses the active tab, selected text, terminal state, unfinished action, and the reason they were doing it. This would make the pendant a continuity device rather than only a remote microphone.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Background model creates a compact task handoff and identifies resumable versus unknown-completion steps; realtime model only answers a spoken resume request. Deterministic restore handles app/tab/window reopening.
- **latency:** Capture handoff in under 3 seconds; spoken resume under 2 seconds; restore the desktop context within 5 seconds after the Mac is available.
- **cost:** Usually <$0.01 per handoff, dominated by one background summarization call. Deterministic app/tab restoration and compressed state storage cost effectively nothing in API terms.
- **security:** Capture only the active window, selected text, tab origin/title, job identifiers, and explicitly permitted page context; never bulk-export authenticated page contents. Encrypt the handoff locally, expire it after a configurable period, and say when a step's completion is unknown instead of replaying it.
- **missing:** a cross-surface handoff object with versioned schema and expiry; Mac capture of active app/window, selection, terminal working directory, and focused browser tab; browser-extension capture and restore of an authenticated tab without exporting its contents; pendant button/event ingestion over the USB serial link; resume orchestration that distinguishes safe reopening from side-effecting replay; a dashboard view for handoffs and explicit discard/expiry

### "When I press the pendant twice, make this a private moment: stop sending desktop/browser context, hide sensitive windows, and tell me when privacy is actually active; restore everything when I release it."
- **useful because:** The current system has powerful access to Mac UI, authenticated Safari sessions, relay logs, and spoken output, but no single physical privacy boundary spanning all of them. A user should be able to enter a meeting, handle a password, or discuss something confidential without trusting that every surface independently noticed.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic firmware/relay state machine; no model call for activation or enforcement. Realtime phrasing is optional and only after privacy state is confirmed.
- **latency:** Local LED acknowledgment under 200 ms; Mac window masking and browser capture suspension under 1 second; restoration under 2 seconds.
- **cost:** Near-zero API cost. Main work is host integration and a small durable privacy-state record.
- **security:** Privacy must fail closed: if the relay cannot confirm Mac and browser suspension, the pendant must say 'not confirmed' rather than claim privacy. Block context capture, browser inspection, screenshots, spoken summaries, and queued replay while active; never delete evidence needed for an already-running external action. A physical release or explicit button action must be required to restore.
- **missing:** a firmware privacy-state command and distinct confirmation pattern that does not conflict with recording/status LED states; relay fan-out of privacy state to Mac planner, vision, and browser extension; host enforcement that suspends capture/inspection and masks or minimizes configured sensitive windows; a privacy audit record showing each surface's acknowledged state; a recovery rule for host/link loss while privacy is active


## Changes it proposed to its own stack

### `relay` — Add a bounded live execution telemetry channel: each Mac action emits phase events (queued, spawn, stdout/stderr heartbeat, exit/timeout, rewritten-from) keyed by jobId and actionId; relay coalesces them to at most one update per second and sends only phase, elapsed time, and redacted summaries to the pendant. Persist the last event and age so reconnects resume from a cursor rather than replaying the whole log.
- **owner gets:** While a long command or computer-use task runs, the owner can tell whether the Mac is alive, waiting, or stuck instead of pressing the pendant repeatedly or assuming silence means failure.
- effort: Medium: instrument executor and bridge event routes, add coalescing/cursor state, and map phases to the already accepted single-LED truth beacon plus spoken updates.  ·  risk: Telemetry can leak filenames or command output and can create noisy audio. Enforce redaction, bounded excerpts, rate limits, and stale-age wording; execution itself is unchanged and a dropped telemetry event must never imply completion.
- cost: Negligible storage and relay bandwidth; no model call for phase events. A cheap background summarizer is optional only for unusual stderr.  ·  latency: Under 1 second from a phase change to relay; up to 1 second coalescing delay.
- security: Redact stdout/stderr and URLs by default; send identifiers, phase, duration, and hashes unless the owner explicitly asks for detail.
- depends on: USB serial transport between the physically attached pendant and Mac bridge; a durable jobId/actionId correlation shared by receipts and ledger; process instrumentation that emits heartbeat and exit/signal data


## What it asked for

_Nothing._
