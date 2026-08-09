# Harness derivation — mac-terminal — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stop whatever you just started, even if the Mac is still in the middle of a shell command, and tell me exactly what was stopped and what I can safely resume.”"
- **useful because:** This is the single most useful missing safety-and-control primitive: the owner can interrupt a runaway command from the worn device rather than finding the Mac, while receiving a truthful receipt instead of the current misleading 'cancel signal sent' behavior. It only becomes real when the pendant button, relay, Mac process supervisor, and durable job journal cooperate.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → unified
- **model tier:** Realtime only for intent recognition and a one-sentence spoken receipt; no background LLM is needed. The Mac supervisor performs deterministic process control and journal reconstruction.
- **latency:** Button-to-kill acknowledgement under 1 second on USB today and under 2 seconds over LTE when registered; spoken summary can follow within 3 seconds.
- **cost:** Negligible model cost for a fixed receipt; one relay event and one Mac control request dominate, not tokens.
- **security:** The cancel command must be bound to the active owner session/job and reject stale or ambiguous job IDs. Killing a process can leave partial files or external side effects; report the exact step, signal, cwd and whether it exited, and require a separate explicit request to resume. No command output or secrets need leave the Mac.
- **missing:** A durable active-job identity propagated into the action ledger (planMeta.jobId is currently null); A real process supervisor using execFile/spawn with pid/process-group tracking and signal escalation; current cancel is cooperative between steps and does not kill run_shell; A pendant cancel-intent event over USB/LTE, with exactly-once deduplication and acknowledgement; Boot reconciliation that marks interrupted jobs and exposes a safe resume plan instead of leaving processing forever; A deterministic spoken receipt joining /jobs, /journal and action receipts

### "“What needs me right now? Combine anything waiting in my authenticated browser tabs with failed or paused Mac work, rank it by consequence, and let me resolve each item by voice.”"
- **useful because:** The owner currently has separate blind spots: browser sessions can hold authenticated work, while Mac jobs can fail or stall. A single spoken queue would surface only actionable exceptions, cite the source tab/job, and let the owner say “retry that,” “open it,” or “dismiss it” without hunting through windows.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → unified
- **model tier:** Use a cheap background classifier to normalize and rank queued items; use realtime only for the brief spoken digest and the owner's selected resolution. Deterministic rules should suppress routine successes and duplicates.
- **latency:** Refresh on browser heartbeat/job events; digest available in under 2 seconds when asked, with action acknowledgement under 3 seconds.
- **cost:** Low: event-driven summaries and a small classifier over short metadata; avoid sending page bodies or shell output unless the owner selects an item.
- **security:** Authenticated page titles and job metadata are sensitive. Keep page contents on the Mac/browser agent, send only redacted item cards and source handles to relay, and require the browser session affinity to resolve an item. Never speak secrets aloud by default; say which app/tab contains them.
- **missing:** A durable cross-surface attention-item schema with deduplication and expiration; Browser page-watch events delivered to the relay rather than only polled status; Mac job failure/stall events with stable job-to-ledger joins; Voice intents that resolve an item handle to browser or Mac actions without re-planning the whole task; A privacy/redaction policy for titles, URLs, stderr and authenticated page snippets

### "“Turn the thing I’m looking at in the browser into a ready-to-review change in my active project: extract the relevant requirements, edit the right files on the Mac, run the tests, and tell me what changed.”"
- **useful because:** This closes the most valuable gap between authenticated context and local action. Today the browser can hold a session and the Mac can edit/run commands, but the owner must manually carry requirements across them. The pendant provides a natural ‘do this’ trigger and a concise review receipt; the system preserves citations and test evidence rather than pretending a generic shell succeeded.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime → unified
- **model tier:** Background/cheap model extracts and normalizes requirements from the selected page; realtime handles clarification and final spoken summary. Use deterministic Mac actions for file edits/tests where possible, escalating to the planner only for ambiguity.
- **latency:** Capture and acknowledge the selected tab in under 1 second; planning may take 5–15 seconds; edits and tests are allowed to run longer with live status and a truthful completion/failure receipt.
- **cost:** Moderate, dominated by one requirement-extraction call and possibly one planner call; do not resend the full page after the initial browser-side extraction. Test execution costs no model tokens.
- **security:** Page content and local source are both private. Keep raw authenticated HTML and source on-device; relay receives only a bounded requirement digest, file diff summary, and test result. Require the owner to explicitly say apply/commit before destructive edits; never transmit credentials or hidden tab state.
- **missing:** A browser command that returns a bounded, cited selection plus stable tab/session handle to the Mac planner; A cross-surface work context carrying page citations, active project, and session ID; A patch/diff action with precondition checks and an undoable receipt, rather than unconstrained text edits; Test execution records containing exit code, argv, cwd and duration; A review artifact presented on the pendant/voice path (diff summary, failing test names, source citations)

### "“I’m leaving my desk—put everything into away mode: pause resumable Mac work, freeze authenticated browser sessions without logging me out, save exactly where each task was, and tell me on the pendant what will resume when I return.”"
- **useful because:** Today the owner must manually decide which jobs to stop, which browser tabs are safe to leave open, and how to recover context after sleep or travel. A single physical departure command would make the system behave like a trusted assistant: preserve work without losing authenticated state, reduce exposure, and provide a clear return point. This is distinct from cancelling one job because it coordinates the whole live workspace and produces a resumable inventory.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime → unified
- **model tier:** Deterministic state machine for process/session handling and resume capsules; a cheap model summarizes the capsules. Realtime is only needed for the owner's short command and spoken inventory.
- **latency:** Acknowledge locally within 500 ms; freeze or checkpoint all eligible work within 5 seconds, then report stragglers. Return-mode restoration should begin within 2 seconds of USB reconnection or a spoken command.
- **cost:** Very low model cost; storage and process/session inspection dominate. Summaries can be generated from compact metadata rather than page contents or shell logs.
- **security:** Away mode must not copy authenticated page contents or credentials to relay. Browser sessions remain on-device and are marked frozen, not exported. The owner needs an explicit policy for whether notifications are muted and whether sensitive apps may be closed. Every checkpoint needs a timestamp, process/session identity, and a clear 'not saved' state for work that could not be checkpointed.
- **missing:** A first-class away/return mode spanning the pendant, Mac agent, and browser extension; Checkpoint adapters for shell jobs, browser commands, and active planner sessions, each with a safe resume boundary; A browser freeze primitive that preserves session cookies locally while preventing new commands; A durable workspace manifest keyed by project/session/job, with freshness and unsaved-work status; A return handshake over USB/LTE that lets the pendant announce restoration progress without claiming completion prematurely

### "“Finish this overnight, but only while my Mac is plugged in and idle; use the authenticated browser session if needed, stop before my morning routine, and leave me a spoken result or the exact blocker.”"
- **useful because:** The owner cannot currently delegate a bounded, unattended workflow that respects physical machine conditions and a deadline. This would turn the Mac, browser, relay, and pendant into a reliable overnight worker instead of a one-shot command: it waits for power/idle, uses existing sessions without exposing them, checkpoints between steps, and gives a useful blocker rather than silently timing out.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → unified
- **model tier:** Cheap background planner plus deterministic scheduler and host-state checks; realtime is only for initial confirmation and the morning result. No expensive model should run while merely waiting for power or idle.
- **latency:** Accept the request in under 2 seconds, begin when conditions become true, and deliver a result before the owner’s stated deadline with periodic pendant status only on meaningful state changes.
- **cost:** Low-to-moderate: model calls happen per workflow step and failure recovery, not during waits. Host telemetry and browser metadata remain local.
- **security:** The task needs a hard deadline, allowed applications/sessions, and a bounded side-effect policy. Keep authenticated browser data on-device; send only step status. The system must stop rather than improvise when power, network, session validity, or deadline conditions fail, and must report partial changes precisely.
- **missing:** A durable deadline-aware scheduler that can wait on Mac power, idle, network and browser-session conditions; A workflow capsule with per-step checkpoints, leases, and a stop-before-deadline guard; Host telemetry routes for power/idle and browser session validity; A relay wake/resume mechanism that can deliver the final result if the Mac sleeps or reconnects late; A compact morning receipt containing changed artifacts, test evidence, and blockers


## What it asked for

_Nothing._
## Its own summary

Round 149 produced three owner-facing capabilities. The highest priority is a real pendant-triggered emergency stop: propagate a stable job ID, kill the actual Mac process group (not merely signal cooperative cancellation), reconcile the durable ledger after crashes, and speak a truthful stopped/resumable receipt. I also proposed a unified voice attention queue combining authenticated browser exceptions with failed/paused Mac work, and a cited browser-to-project workflow that turns the selected page into a local patch, runs tests, and reports a reviewable diff. The latter two are connective rather than wholly new routes, so their value depends on implementing the missing handoff/event schemas rather than adding more planner UI. I told mac-planner the concrete primitives to prioritize.

**Biggest unknown:** Whether the live browser inspection/session implementation can already export a bounded, cited selection (not just metadata) and whether any existing event stream can carry browser and Mac exception cards; the route inventory proves endpoints but not those payload semantics. The pending USB-serial diagnostic grant is still unavailable, so I cannot verify the physical link or test the cancel path end-to-end this round.

