# Harness derivation — mac-terminal — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving—keep an eye on the task, recover from transient Mac or browser failures yourself, and tell me on the pendant only when it is truly done or needs me.”"
- **useful because:** Today the job store shows repeated browser_navigate/read failures (12/12 and 8/8) but the owner has no compact, truthful way to know whether work is still progressing. This would let a long task survive tab loss, bridge restarts, and temporary Mac errors without either silent failure or noisy updates.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for polling, classification, and retry planning; realtime only for the owner's spoken request and final interruption
- **latency:** A retry decision within 5 seconds of a failure; final pendant notice within 15 seconds of terminal success/failure; no foreground model call while unattended.
- **cost:** Roughly $0.01–$0.08 per multi-step task depending on retries; background classification and deterministic health checks dominate, not realtime conversation.
- **security:** Private tab contents and Mac command outputs remain on the local agent unless the task explicitly asks for cloud reasoning. Never silently repeat a non-idempotent browser submit or destructive shell command; retries are limited to reads and explicitly idempotent steps. Pendant notices should contain summaries, not page contents.
- **missing:** A durable step-level retry/compensation runner that distinguishes safe read retries from non-repeatable mutations; Browser bridge health/reconnect and tab reattachment inside the runner; A pendant push/status channel that reports queued, retrying, blocked, and completed truthfully; Failure classification using exit code, stderr, browser error, and last known tab heartbeat

### "“That CI-failure email is important—trace it all the way through: open the authenticated notification, inspect the matching repository and workflow on my Mac, run only diagnostic checks, correlate the evidence, and leave me a cited spoken incident report with the next command I should approve.”"
- **useful because:** The live Gmail tab already exposes repeated buckymatch workflow failures, while the Mac is the only place with the repository and local environment. Today those facts remain disconnected: the system can read the email or run a Mac command, but cannot produce one evidence-backed diagnosis tied to the exact commit, local branch, and observed failure. This would turn a passive alert into an actionable report without making changes.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background for deterministic email/thread extraction and repository diagnostics; planner only for cross-source correlation and a concise incident narrative; realtime only if the owner asks follow-up questions
- **latency:** Initial triage under 45 seconds, with a progress update after 10 seconds; diagnostics may continue as a durable job after the owner leaves.
- **cost:** About $0.02–$0.10 per incident, dominated by one planner correlation call and any cited page extraction; deterministic status checks are cheap.
- **security:** Authenticated mail and source code are sensitive. Keep raw email/page text and repository output on the Mac/relay, pass only bounded excerpts and hashes to the planner, and never run a repair, push, merge, or workflow rerun without a separate explicit request. Cite Gmail message URL, commit SHA, command, cwd, exit code, and timestamp so the owner can verify every claim.
- **missing:** A cross-surface incident object linking a browser message/thread to a repository/commit and Mac job; A safe diagnostic recipe registry (git status/log, test discovery, workflow metadata) with bounded output and no mutation; Citation-capable correlation output that can be rendered both on dashboard and as a short pendant audio briefing; A durable continuation path if Safari or the Mac bridge disconnects

### "“If I press and hold the pendant button, stop the currently running Mac or browser task immediately, tell me which step was halted, and leave a resumable checkpoint for later.”"
- **useful because:** The pendant has one real button and is physically USB-connected to the Mac today, but an unattended job has no fast physical escape when the owner notices the wrong app, a runaway retry, or sensitive content on screen. This gives the owner a reliable, local-feeling stop control without opening the dashboard or speaking a command; the next request can resume from the last completed idempotent step instead of starting over.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic firmware event and local cancellation path; background model only to summarize the halted step and produce a checkpoint explanation.
- **latency:** Hardware event acknowledged by LED within 100 ms; Mac/browser cancellation attempted within 500 ms over USB; spoken/dashboard receipt within 5 seconds. If USB is absent, record the event locally and apply it on reconnection.
- **cost:** Near-zero model cost for cancellation; under $0.01 for an optional background checkpoint summary. Firmware storage is a few hundred bytes per pending stop event.
- **security:** Cancellation must be fail-safe: kill/abort only the job identified as foreground for that pendant session, never an unrelated shell process. Do not treat a delayed or missing USB acknowledgement as success; LED patterns must distinguish requested, confirmed, and offline. Checkpoints may contain URLs or paths, so keep them local and redact them from spoken output by default.
- **missing:** Firmware long-press gesture and a small persistent stop-event record; A local-agent cancellation endpoint that maps pendant session to active job and propagates AbortSignal to shell/browser actions; A resumable step graph with idempotency and checkpoint persistence; Truthful USB acknowledgement and LED status integration

### "“Why is my computer slow right now? Check the Mac, open browser tabs, network, disk, and the pendant audio link together, identify the actual bottleneck, and fix only a reversible cause.”"
- **useful because:** The owner currently gets isolated battery/network/process answers, not one diagnosis that explains an interactive slowdown across the Mac, Safari, bridge, and pendant path. A single spoken answer could distinguish a runaway tab, saturated disk, stuck local agent, audio bridge backlog, or network degradation and apply a reversible fix instead of guessing.
- **path:** pendant → relay-realtime → mac-terminal → browser-extension → dashboard
- **model tier:** Deterministic diagnostics first; background model to rank symptoms; realtime only to explain the result or ask one narrowly scoped clarification.
- **latency:** First spoken hypothesis within 8 seconds; full diagnosis within 30 seconds; reversible fix and verification within 60 seconds.
- **cost:** $0.00–$0.03 per invocation; most checks are local and deterministic, with one small background synthesis call when signals conflict.
- **security:** Process names, URLs, and local paths are sensitive; keep raw diagnostics on the Mac and send only summarized evidence to the relay. Never kill a process or change settings until the owner explicitly asked to fix; limit automatic fixes to an allowlisted reversible action and verify restoration.
- **missing:** A correlated diagnostic snapshot spanning Mac, Safari tabs, local agent, and USB audio bridge; A bottleneck scoring model grounded in measured baselines rather than generic advice; A reversible-fix catalog with before/after verification; A bridge health endpoint and truthful pendant audio-path status

### "“Make this reproducible.” Capture the exact pendant request, model/routing decision, browser tabs and URLs, Mac cwd and environment fingerprint, commands, outputs, and timing into a private replay bundle I can inspect or hand to you later."
- **useful because:** When a task succeeds once and fails later, the owner cannot currently reconstruct the conditions that made it work. A replay bundle would turn mysterious intermittent behavior into a concrete artifact: the system could resume or diagnose it without asking the owner to remember which tab, branch, directory, or prompt was involved.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic capture and redaction; background model only to write a short replay synopsis and identify nondeterministic inputs.
- **latency:** Begin capture immediately and stream metadata without delaying the task; finalize within 2 seconds of completion. Replay preparation can run in background.
- **cost:** Under $0.01 for capture; storage is the main cost, approximately 20–200 KB per bundle after output caps and compression.
- **security:** Raw cookies, tokens, email bodies, audio, and secrets must never enter the bundle by default. Store hashes and redacted excerpts, mark each field's sensitivity, encrypt locally, and require an explicit export action before anything leaves the Mac. Replay must default to dry-run for mutations.
- **missing:** A cross-surface trace schema with one correlation ID from pendant event through relay, browser, planner, and Mac executor; Secret-aware environment and output redaction with configurable retention; A replay engine that can substitute current tabs and filesystem state while preserving the original evidence; A dashboard viewer showing the timeline and deterministic versus nondeterministic inputs

### "“Before I send this, check every attachment, quoted passage, browser field, and local file for secrets or private data, explain the risks in plain language, and prepare a clean redacted version without sending anything.”"
- **useful because:** The owner can currently draft or fill a browser transaction, but has no unified privacy review across the message, authenticated page, clipboard-like text, and Mac files it references. This would catch API keys, personal identifiers, private URLs, hidden metadata, and accidental unrelated attachments before they leave an authenticated session.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic secret-pattern and metadata scanner first; background model for contextual sensitivity classification; realtime only for the owner's final spoken explanation.
- **latency:** Preview findings within 10 seconds for ordinary text and under 45 seconds for local attachments; redacted draft should remain editable and never auto-submit.
- **cost:** $0.01–$0.05 per review depending on attachment size; local scanning dominates and can avoid a model call for obvious matches.
- **security:** The scanner itself handles the most sensitive content. Keep files and page text local, pass only redacted spans and feature labels to the classifier, never upload originals, and preserve the original untouched. Any redaction that changes meaning must be highlighted; submission remains a separate owner action.
- **missing:** A unified pre-send object linking browser fields, attachments, quoted text, and local file paths; Local high-entropy/credential/PII and document-metadata scanners with explainable findings; A reversible redaction editor that preserves evidence and supports owner corrections; Browser integration that can preview the exact post-redaction payload without submitting


## Changes it proposed to its own stack

### `mac-harness` — Add a shell execution forensic envelope to every run_shell receipt: argv/command hash (with secrets redacted), resolved cwd, start/end monotonic timestamps, timeout, exit code, stdout/stderr byte counts plus capped tails, files/artifacts created, network-process indicators, and an explicit undoability verdict. Persist the envelope beside the existing job receipt and expose a compact diff view in the dashboard. For failures, automatically attach the last 3 successful envelopes with the same command family so the planner can choose a repair instead of blindly repeating it.
- **owner gets:** When something fails while the owner is away, they can see what actually ran and why, rather than a vague failed job. The agent can recover faster from the real cause (wrong cwd, timeout, missing permission, or a changed repo) and the owner can audit permanent shell effects without losing the maximum-access policy.
- effort: Medium: instrument computerControl.runShell/executor and actionReceipts, add redaction and command-family hashing, then add a read-only receipt projection and dashboard panel.  ·  risk: Command output can contain secrets or personal data; redact known environment/token patterns and cap tails, while retaining hashes and exit metadata. Instrumentation must never alter command exit behavior; if receipt writing fails, execution result still returns and marks telemetry incomplete.
- cost: Negligible API cost; local JSON/D1 growth roughly 2–10 KB per shell job after caps, with periodic retention cleanup needed.  ·  latency: About 5–20 ms local overhead per action; no extra model call.
- security: Improves accountability without restricting execution. Keep raw stdout local and make cloud projections metadata-only by default.
- depends on: Existing POST /jobs/:jobId/receipts and actionReceipts.js; A redaction utility shared by shell and browser receipts; A retention policy for capped forensic envelopes


## What it asked for

_Nothing._
## Its own summary

Round 140 produced three owner-facing capabilities: unattended jobs that self-recover and report truthful terminal status, cross-surface CI incident triage from authenticated Gmail into Mac diagnostics and a cited pendant briefing, and a physical pendant long-press that cancels the active Mac/browser job with a resumable checkpoint. I also proposed richer shell forensic envelopes, though it was flagged as close to an existing evidence-ledger idea. Live evidence: the Mac journal has 120 retained jobs, 111 actions, 38 failures, zero undoable actions; one browser navigate family failed 12/12 and one read family failed 8/8, while other read families succeed. The Gmail tab visibly contains repeated buckymatch workflow failures. I notified mac-planner.

**Biggest unknown:** The exact cancellation and retry contracts are still missing: whether local-agent actions accept AbortSignal, how an active job is mapped to the physically connected pendant session, and whether browser tabs can be reattached after the bridge heartbeat returns. I still need those implementation contracts plus a truthful USB acknowledgement path; no additional discovery call is useful until they are exposed.

