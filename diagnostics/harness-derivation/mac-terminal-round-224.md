# Harness derivation — mac-terminal — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-mac-agent** — At 2026-08-08T23:54Z the Mac agent and relay are healthy, browser extension online with 2 Safari tabs, full control and computer-use enabled, but GET /jobs shows a live processing job local_b753870c... ('ios session watch') with no receipts yet. The granted USB serial diagnostic tool still has no implementation and cannot inspect the physically connected chips.
  - evidence: GET /ops/status returned agent.ready=true, relay.reachable=true, browser.online=true; GET /jobs returned processing job; mac_usb_serial_diagnostics returned resolution=unresolved.

## Capabilities it proposed

### "When something I asked the pendant to do fails, say what actually failed and recover it automatically if the failure is transient—otherwise give me one clear next action."
- **useful because:** Today a shell failure loses its exit code, cancellation is not forceful, and browser/Mac work can fail in different places. This turns an opaque 'failed' beacon into a useful outcome, using the node that can inspect the failure and the pendant that can report it without opening a screen.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background diagnosis/classification; realtime only for the short spoken explanation. Deterministic retry recipes should run without an LLM.
- **latency:** Initial failure explanation under 2 seconds after the job receipt; one automatic retry within 10 seconds, never an unbounded loop.
- **cost:** Usually <$0.01 per failure; most cases are deterministic exit-code/network classification. LLM cost only for novel stderr or cross-surface diagnosis.
- **security:** A retry can duplicate a side effect. Retry only idempotent/read or explicitly replay-safe actions, attach the original job and action IDs, and expose the exact command/browser URL and stderr in the dashboard. No secrets in diagnostic prompts.
- **missing:** Per-action exit code, signal, and termination reason in run_shell receipts; AbortSignal wired to the child process so cancellation can stop a running command; A retry/idempotency decision attached to every action, not only bridge polling; A durable failure-recovery state machine joining Mac jobs to pendant turn IDs

### "Give me a 'prove what happened' answer for any task: show the exact Mac command and project, the browser page or session used, what changed, and the evidence that says it succeeded—not just 'done'."
- **useful because:** The owner cannot trust a completion badge when shell rewrites commands, receipts omit exit codes, and browser work has separate provenance. A single evidence capsule lets the owner verify a consequential result from the pendant or dashboard without reconstructing the run.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic evidence collection first; a small background model compresses it into a spoken summary. Realtime only reads the final capsule aloud.
- **latency:** Receipt available within 1 second of completion; evidence collection may continue for 5 seconds and update the capsule asynchronously.
- **cost:** <$0.005 for deterministic collection and hashing; occasional small-model summarization under $0.01. Storage is bounded by retaining hashes, short excerpts, and URLs rather than full files.
- **security:** Evidence can contain sensitive paths, URLs, or stderr. Redact tokens and environment values, keep full artifacts local, and require explicit owner request to export anything. Hash files and record byte ranges instead of uploading them.
- **missing:** A pre-dispatch immutable action record preserving the submitted action and the rewritten action; Shell receipt fields for argv/cwd, exit code, signal, start/end/duration, and redacted environment fingerprint; A jobId↔ledgerId join and a closed ledger on every terminal path; One cross-surface evidence schema consumed by pendant speech, relay, and dashboard

### "While you are doing a long task on my Mac, keep me updated only at meaningful milestones, and let me pause, cancel, or ask for a progress snapshot from the pendant without opening the dashboard."
- **useful because:** The current system is effectively silent until completion, and cancelling a running shell does not stop the child. This gives the owner control over a long build, download, export, or browser workflow while preserving the pendant's hands-free reach.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic process/job telemetry and milestone detection; a cheap background model compresses noisy output into milestone text. Realtime is used only to speak a short update or interpret a live button/voice command.
- **latency:** Button/voice state response under 500 ms when the Mac is reachable; milestone updates no more often than every 30 seconds unless the job fails. Pause/cancel acknowledgement under 1 second, with honest 'stop requested' versus 'stopped' states.
- **cost:** Near-zero for timers, exit/byte counters, and structured progress. Under $0.01 per long job for occasional summarization; no continuous realtime model stream.
- **security:** Progress output may contain secrets or private URLs; redact before relay and retain full logs locally. Pause/cancel must be bound to the exact job and action ID, reject stale pendant commands, and never claim a process stopped until its PID/receipt confirms it.
- **missing:** A live job telemetry stream with byte/time milestones and bounded stdout/stderr tails; Child PID/process-group capture and signal-aware cancellation for run_shell; A pendant command channel mapping button/voice intent to a specific active job; Relay delivery acknowledgements and stale-command rejection for control intents; A compact progress event schema shared by shell and browser actions

### "Let me start a task while I am away from my Mac, keep talking to the pendant while the link is unavailable, and have the Mac later continue the exact task in the right browser session or project—with the conversation, pending decisions, and result preserved as one thread."
- **useful because:** Today offline handling can preserve audio or a button intent, but it cannot preserve a semantically complete task across the pendant, relay, Mac, and authenticated browser. The owner loses the task boundary precisely when moving between rooms or losing connectivity—the moment a wearable assistant should be strongest.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only handles the live short voice exchange. A cheaper background model on reconnect reconstructs the queued turn, resolves the task against the current Mac/browser sessions, and summarizes what changed.
- **latency:** Offline acknowledgement must be local and immediate. On reconnect, restore the task thread within 5 seconds; defer expensive reconstruction until the Mac and browser are both online.
- **cost:** Small encrypted local queue and relay metadata are negligible. Reconnection classification and summarization should usually cost under $0.02 per interrupted task; do not resend raw audio once a compact transcript and intent are available.
- **security:** Queued speech may contain credentials, private context, or commands. Encrypt it at rest on the pendant and relay, bind every queued item to the paired device and original turn, expire stale intents, and keep authenticated browser content on the Mac. Never silently apply a decision made against an old page state.
- **missing:** A durable cross-surface task-thread identifier spanning pendant turn, relay job, Mac job, browser session, and final result; An offline semantic envelope containing transcript/intent, pending questions, replay cursor, age, and required surface—not merely audio or a button event; Reconnect reconciliation that compares the saved task context with current browser tabs, project state, and Mac job state before continuing; A relay-to-pendant and Mac-to-browser handoff protocol that preserves ordering and exactly-once completion; A compact owner-facing thread view and spoken resume prompt that can say what was saved, what changed, and what needs a decision

### "If my calendar, email, browser portal, and local files disagree about a deadline, amount, or appointment, tell me there is a conflict and read me the competing evidence instead of choosing one silently."
- **useful because:** A confident answer assembled from one stale source can cause a missed deadline or wrong payment. The owner needs the hive's different authenticated surfaces to act as independent witnesses, with the pendant surfacing uncertainty while the Mac and browser retain the evidence.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic extraction and date/amount normalization first; a cheap model clusters claims and explains the disagreement. Realtime only speaks the concise conflict and asks which source should win.
- **latency:** On explicit request, under 5 seconds for a small set of sources. Proactive monitoring should run in the background and speak only newly material conflicts, never every update.
- **cost:** Usually under $0.02 per conflict check; most work is local parsing and existing browser reads. Keep evidence capsules and source snippets bounded rather than sending whole pages to a model.
- **security:** Cross-source comparison can reveal sensitive mail and portal data. Keep raw evidence on the Mac, send only normalized claims and minimal excerpts to the relay, encrypt cached findings, and preserve source URLs and timestamps so the owner can revoke stale evidence.
- **missing:** A common claim schema for dates, amounts, people, and locations with source timestamp and freshness; A connector that reads authenticated browser claims alongside Calendar/Mail/files without flattening provenance; Conflict clustering and change detection across sources, including timezone and recurring-event handling; A pendant policy for urgent versus quiet contradictions and an explicit source-preference record; A durable evidence bundle that lets the owner inspect the competing claims later

### "Before I let a complicated request touch my real Mac or logged-in browser, run it in a disposable shadow workspace and tell me what files, tabs, form fields, and external effects it would produce; then apply that same plan to reality when I say go."
- **useful because:** The current preview paths can describe or stage some actions, but they cannot execute a whole cross-surface task against a faithful disposable state. A shadow run would make ambitious automation testable without forcing the owner to choose between blind trust and doing every step manually.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic snapshot/replay harness for filesystem and browser state; a background model explains the predicted diff. Realtime only summarizes the result or hears 'go'.
- **latency:** Small tasks preview in under 10 seconds; large projects may run asynchronously with milestone updates. Applying an accepted shadow plan should reuse its recorded action identities rather than re-plan from scratch.
- **cost:** Local disk and browser-profile snapshot costs dominate; model usage should remain under $0.02 per preview. Cloud receives only a plan/diff summary, never a clone of the authenticated profile or private files.
- **security:** A browser clone must not expose cookies or accidentally send real network requests. Use an isolated profile with network interception and explicit mock boundaries; mark every effect as simulated, predicted, or real. Expire snapshots and securely delete them.
- **missing:** Filesystem snapshot/overlay support with a bounded project scope; An isolated browser profile/session replay layer that can mock submissions and downloads; A unified predicted-diff format for files, UI state, browser navigation, and external requests; A plan-binding mechanism proving that the applied actions are the reviewed shadow actions; A pendant-readable preview and explicit owner transition from simulation to real execution


## What it asked for

_Nothing._
