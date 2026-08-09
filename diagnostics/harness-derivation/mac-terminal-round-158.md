# Harness derivation — mac-terminal — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run this command and keep me updated on the pendant: tell me when it starts, read the meaningful progress as it happens, and let my next button press cancel it."
- **useful because:** Today a shell job can run for two minutes with no live feedback, and cancellation only takes effect between actions. This makes long Mac work feel trustworthy and controllable from the wearable rather than requiring the owner to stare at a dashboard.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime only for interpreting the initial request and compressing notable output; deterministic Mac execution and progress filtering should be local code.
- **latency:** Start acknowledgement under 500 ms; progress events under 1 s behind stdout; cancellation acknowledgement under 1 s after the child actually exits.
- **cost:** Low: one realtime turn plus streamed relay events; dominant cost is any initial voice transcription, not progress forwarding.
- **security:** Command output may contain secrets and should be redacted before relay/audio; never speak raw environment variables or untrusted terminal control sequences. Button cancellation must be scoped to the active job ID and never cancel an unrelated job.
- **missing:** An abortable run_shell executor using AbortSignal/child_process.spawn rather than execAsync without a signal; A bounded stdout/stderr event stream with secret and ANSI redaction; Relay route binding a pendant button event to the active Mac job and returning final exit code; Firmware mapping for a distinct 'cancel requested' state (building on truthful_action_status_beacon)

### "If my Mac went to sleep or restarted while doing something for me, tell me exactly what finished, what did not, and safely continue only the unfinished steps when I say 'resume'."
- **useful because:** The current durable job record can remain 'processing' forever after a restart, while the ledger is left open and its job ID is not linked. The owner otherwise cannot distinguish a completed file move from a half-completed multi-step task, and repeating it can duplicate side effects.
- **path:** mac-planner → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Background deterministic reconciler for boot/reconnect and ledger comparison; realtime only to explain the concise recovery report and obtain the explicit spoken resume command.
- **latency:** Reconcile within 10 seconds of local-agent boot or bridge reconnect; spoken status in the next conversation turn.
- **cost:** Near-zero model cost for reconciliation; occasional realtime explanation. Storage is a bounded local journal, not cloud transcript.
- **security:** Recovery must never infer permission to rerun an external mutation. Store hashes of sensitive parameters rather than raw secrets; only expose paths and effects that the original job already exposed. Resume requires an explicit owner request and an idempotency key per step.
- **missing:** Boot-time reconciliation that marks orphaned processing jobs interrupted; Orchestrator closeLedger and a durable jobId-to-ledger association; A resume planner that consults completed receipt IDs and skips only proven-complete idempotent steps; Relay/pendant event carrying a recovery summary when the Mac reconnects

### "Take the thing I am looking at in Safari, do the necessary download or command-line processing on my Mac, and give me a spoken answer with links to the exact files and source page."
- **useful because:** This joins the browser's authenticated session to the Mac's filesystem and shell: the owner can ask from the pendant without explaining which tab, manually downloading, locating, converting, or summarizing anything. Neither a browser agent nor a shell agent alone can complete the whole task reliably.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → unified
- **model tier:** Realtime for resolving the user's intent and final spoken summary; deterministic browser extraction/download plus typed local processing; background model only for long document summarization.
- **latency:** Identify the active tab and acknowledge in 1 second; ordinary download/process in under 30 seconds; stream a concise completion or failure state to the pendant.
- **cost:** Usually one short realtime turn; browser and local processing dominate latency, with no document bytes sent to the cloud unless summarization is explicitly requested.
- **security:** Keep authenticated page contents and downloaded files on the Mac by default. Require the browser extension to return origin URL, download path, MIME/hash, and a bounded text excerpt; reject cross-origin redirects or executable downloads unless explicitly requested. Spoken output should never read credentials or full sensitive documents.
- **missing:** A correlation contract tying one pendant request to an active Safari tab, browser command, and subsequent /execute job; A local download handoff that returns a verified path and SHA-256 to the Mac planner; A safe local document inspection/conversion action with size/type limits and structured receipts; A final relay event containing source URL, artifact path, and completion status

### "When I leave my Mac, pause any in-progress AI work that could expose private browser or file data, lock the Mac, and resume only when I am back and explicitly say 'continue' through the pendant."
- **useful because:** A voice command can currently launch work, but it cannot establish that the person wearing the pendant is still physically present while an authenticated browser session or shell process continues. This would make unattended work safe without taking away the owner's maximum-access policy: it pauses only the designated sensitive workflow and leaves ordinary background jobs alone.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic presence/session coordinator; realtime model only interprets the initial sensitivity scope and the spoken continue command.
- **latency:** Detect USB/pendant departure or Mac lock within 2 seconds; stop browser polling and pause eligible jobs within 5 seconds; resume only after an explicit spoken confirmation.
- **cost:** Near-zero model cost after setup; local event processing and a small persistent policy/session record dominate.
- **security:** Presence must be based on a cryptographically correlated pendant link, not microphone or browser focus alone. Do not transmit page contents to determine presence. A reconnect must not equal consent to resume; require a fresh pendant button/voice confirmation and show a stale/paused state locally.
- **missing:** A signed pendant-presence lease shared by the USB bridge, relay, and Mac agent; Sensitivity labels and pause/resume hooks for browser sessions, pipeline jobs, and shell/PTY jobs; A Mac lock/unlock and browser-session suspension integration; An exactly-once pause/resume state machine with an auditable owner confirmation

### "At the start of my day, tell me what changed in the projects and web work I touched yesterday, what is still unresolved, and give me the exact evidence without rereading everything."
- **useful because:** The system can inspect a current Mac, active browser tabs, and individual jobs, but it cannot join yesterday's terminal outcomes, authenticated web actions, and spoken decisions into a bounded, evidence-backed delta. The owner gets continuity instead of repeatedly reconstructing context from tabs, logs, and memory.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → browser-extension → unified
- **model tier:** Background scheduled indexer computes hashes, diffs, and unresolved-item extraction locally; a cheaper synthesis model prepares the briefing; realtime only speaks or answers follow-up questions.
- **latency:** Incremental capture under 1 second per completed job/browser action; morning briefing ready before the scheduled alarm, with a 3-second spoken summary and on-demand evidence expansion.
- **cost:** Low ongoing cost if indexing is local and incremental; one small synthesis invocation per briefing. Storage is bounded by rolling summaries and content hashes, not full command output by default.
- **security:** Keep authenticated page bodies and shell output on the Mac; store only redacted excerpts, hashes, project identifiers, and source pointers unless the owner opts into archival. Never infer that a failed command is resolved; every claim must cite a job receipt, browser inspection, or explicit owner decision.
- **missing:** A durable cross-surface activity schema with common correlation IDs and source citations; Local incremental project/browser diff capture with redaction and retention controls; An unresolved-work model that distinguishes failure, pending owner decision, and completed outcome; A scheduled briefing route that can cite and drill into the evidence through the pendant


## Changes it proposed to its own stack

### `mac-harness` — Add a persistent, bounded terminal-session executor alongside one-shot run_shell: spawn with child_process.spawn, capture PID/argv/cwd/exit code, stream framed stdout/stderr, accept signal/resize/input only for an explicitly correlated session, and persist a compact session manifest that survives local-agent restarts. Keep arbitrary FULL_CONTROL access; this is an additional capability, not a gate.
- **owner gets:** Commands such as git rebase, ssh-like local prompts, test watchers, and long builds stop being opaque one-shot jobs. The owner can start work from the pendant, hear meaningful progress, and return later without losing the terminal's actual state.
- effort: Medium-high: new session route and process registry, PTY dependency, framing/redaction, reconnect and cleanup tests, relay correlation, and pendant status integration.  ·  risk: Orphaned processes, output leaks, and accidental input to the wrong session. Recover by refusing ambiguous session IDs, recording process death, applying idle/maximum lifetimes, and exposing a kill/reap operation; do not pretend a detached session is still alive.
- cost: Negligible API cost; modest local CPU/RAM per active PTY and bounded journal storage.  ·  latency: Interactive output can arrive sub-second instead of waiting for command completion.
- security: The existing maximum-access policy remains; however, session input is more powerful than one-shot commands, so bind it to unguessable capability tokens and redact output at the relay boundary. No command restriction is proposed.
- depends on: Abortable process execution and job correlation; A relay stream carrying framed terminal events; truthful_action_status_beacon for disconnected/stale state

### `integration` — Create a cross-surface transaction envelope that stages browser downloads, file mutations, and Mac commands into an owner-visible artifact bundle before committing: capture pre-state hashes, source tab URL, exact action receipts, and post-state hashes; expose one spoken 'undo that bundle' or 'commit' operation, with automatic expiry for uncommitted staging areas.
- **owner gets:** The owner can ask for a risky multi-step task conversationally and recover the whole outcome as one unit instead of trying to remember which downloaded file, rename, browser click, or shell command changed what. It turns the system from a sequence of opaque actions into a recoverable result.
- effort: High: transactional adapters for browser and filesystem actions, copy-on-write or snapshots for supported paths, cross-agent receipt joining, expiry cleanup, and a pendant-friendly summary/undo protocol.  ·  risk: Some external browser actions cannot be rolled back and files may be too large to snapshot. Mark those steps irreversible before execution, keep the rest staged, and report partial rollback honestly. Storage pressure is handled with quotas and automatic expiry rather than silent deletion of committed evidence.
- cost: No meaningful model cost; local disk overhead proportional to staged artifacts, with configurable quota and optional external-volume storage.  ·  latency: Adds milliseconds for hashes and metadata, and seconds for large snapshots; the owner gains reliable recovery instead of rerunning work.
- security: Bundles can contain sensitive URLs and files, so encrypt or permission them locally, redact spoken summaries, and never upload artifact contents by default.
- depends on: A common correlation ID spanning pendant request, browser command, and /execute job; Cross-surface receipts with pre/post state hashes; Typed snapshot/restore adapters for the Mac and browser; A durable owner confirmation and expiry state machine


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one stack change: live pendant progress plus cancellation for long Mac jobs; crash/restart reconciliation with explicit resume; a browser-authenticated active-tab-to-local-file workflow; and persistent PTY terminal sessions. The most useful is the active-tab-to-artifact workflow: it combines the browser session, Mac execution, relay, and pendant into one request the owner cannot get from any single node. I also confirmed the Mac bridge and Safari extension are online, while the cellular device remains offline.

**Biggest unknown:** I still need a live USB-serial/device diagnostic path to verify the nRF9160 and ESP32 ports and exercise pendant-to-Mac event correlation. The previously queued mac_usb_serial_diagnostics request remains unresolved and should not be re-asked; absent that, the proposed pendant paths can only be validated through the existing bridge/relay interfaces.

