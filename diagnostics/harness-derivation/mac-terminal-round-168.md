# Harness derivation — mac-terminal — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “stop that” into the pendant, immediately stop the Mac command that is currently running, even if the network is down."
- **useful because:** A runaway shell, stuck build, or destructive-looking automation should have a physical emergency stop that works while the pendant is USB-attached today. The current cancel route only signals between steps and cannot interrupt a running exec child.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Realtime only to resolve the spoken stop phrase; the Mac performs a local constant-time cancellation without another model call.
- **latency:** Under 300 ms from button/voice intent to SIGTERM of the process group over USB; relay fallback is best effort when USB is absent.
- **cost:** Negligible per stop (one realtime intent turn if speech is used); engineering cost is USB framing, process-group ownership, and a small local dispatcher.
- **security:** Must target only the active job ID and process group, never broad kill patterns. Record request ID, target PID/PGID, and outcome. A stale or replayed stop frame must be rejected. No command output or secrets leave the Mac.
- **missing:** Versioned authenticated USB command/ACK framing between pendant and Mac; A run_shell executor that uses spawn/execFile with detached process-group tracking and SIGTERM→bounded SIGKILL; A local active-job registry shared with the HTTP cancel route; A pendant stop-intent firmware record and explicit stop acknowledgement pattern

### "Finish the task I asked for earlier, but first tell me what survived the Mac restart and continue only the steps that are safe to repeat."
- **useful because:** Long work should not disappear into a permanently “processing” record after a reboot. The owner gets a truthful spoken continuation: completed steps are not repeated, interrupted steps are identified, and only replay-safe work resumes.
- **path:** relay-realtime → mac-planner → pendant
- **model tier:** Background/cheap model reconciles ledgers and classifies replay safety; realtime is used only for the owner's short confirmation or status question.
- **latency:** On Mac startup, reconcile in under 2 seconds; spoken status within 1 second of the pendant request. Resume begins only after the durable plan is assembled.
- **cost:** Low background inference cost per interrupted job; most work is local JSON/ledger processing. No cost for jobs that completed normally.
- **security:** Never infer completion from a stale processing record. Bind ledger to job ID and action digest; mark unknown/in-flight steps as interrupted. Non-idempotent steps remain paused and are reported, not silently retried. Keep shell output local and redact environment values.
- **missing:** Boot-time reconciliation that marks processing jobs interrupted and closes orphaned ledgers; A real jobId↔ledgerId association in planMeta and execute records; Wiring executionContext's existing exactly-once/retry engine into /execute; A resumable endpoint that returns typed runnable steps with replaySafety and requires the owner's explicit resume request; A truthful pendant status payload for interrupted versus completed

### "If the Mac command fails, diagnose the failure, fix the obvious local problem, and try the smallest safe recovery once; then tell me exactly what changed and whether it worked."
- **useful because:** Today a shell failure loses the exit code and useful cause, and nothing retries. This turns common transient failures (wrong project directory, stale lock, unavailable app, timeout) into a useful result instead of an opaque “Failed” message, without pretending an arbitrary mutation is safe.
- **path:** mac-planner → relay-realtime → pendant
- **model tier:** Cheap background classifier handles exit code/stderr and chooses from a fixed recovery catalog; realtime speaks only the concise result.
- **latency:** Capture failure immediately; diagnosis under 500 ms. One recovery attempt may add up to 30 seconds, never the full 120-second timeout twice.
- **cost:** Usually one cheap classifier call plus local execution; cost dominated by the optional second command, not conversation inference.
- **security:** Recovery catalog must be explicit and auditable (retry after app launch, re-resolve known project cwd, remove only a lock created by this job). Never invent a cleanup command from stderr. Preserve original and recovery receipts, exit status, signal, duration, PID/PGID, and redacted environment fingerprint.
- **missing:** Capture shell exit code, terminating signal, PID/PGID, duration, and bounded stdout/stderr tails; A typed recovery catalog with pre/postconditions and per-action replay safety; A per-job one-recovery-attempt budget and linkage between original/recovery receipts; A spoken result formatter that distinguishes original failure, recovered success, and unrecovered failure

### "When the pendant is plugged into my Mac, let me ask it to do local Mac things even with no LTE or cloud connection, and speak back whether it worked."
- **useful because:** The hardware is physically usable today but is not relay-registered. A local USB path makes the pendant genuinely useful in the failure mode where the owner needs it most: no network, no browser tab, or cloud outage. The Mac can execute local actions while the pendant supplies the always-at-hand interaction and truthful result.
- **path:** pendant → mac-planner → mac-vision → relay-realtime
- **model tier:** A small local intent parser/classifier on the Mac handles the constrained offline command set; use the expensive realtime model only when the USB link is online and cloud interpretation is needed.
- **latency:** Button-to-ack under 150 ms; local intent result under 2 seconds. If interpretation is ambiguous offline, say so locally rather than uploading audio or guessing.
- **cost:** Zero API cost for local intents; engineering cost is serial framing, a small offline grammar/model, and audio response routing through the ESP32 bridge.
- **security:** USB HELLO must bind the physical device identity and boot counter; frames need CRC plus replay-resistant sequence/request IDs. Keep offline utterances and command results on-device/Mac unless the owner explicitly enables cloud fallback. Destructive commands still follow the owner's existing maximum-access policy but must be truthfully reported.
- **missing:** A versioned USB transport between nRF9160, ESP32 bridge, and local-agent with HELLO/ACK/replay handling; A local offline intent subset and dispatcher that maps to existing typed Mac actions; Mac-side speech/audio routing that does not require relay registration; A bounded local result cache so the pendant can report completion after a transient serial drop

### "After you use my Mac or an authenticated browser session, tell me in one short spoken receipt what private data was read, what left the device, which service received it, and whether any secrets were exposed."
- **useful because:** The system currently records that an action ran, but the owner cannot reliably know the privacy boundary crossed by a shell command, browser session, or model handoff. A post-action data-flow receipt makes the hive trustworthy without blocking the owner's maximum-access policy: it reports reality after execution, including accidental exposure.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** A deterministic local tracer/redactor records file origins, network destinations, browser session identifiers, and secret-pattern matches; a cheap background model compresses the event graph into a spoken receipt. Realtime is used only to answer a follow-up question.
- **latency:** Raw receipt is available within 500 ms of action completion; concise speech within 2 seconds. Deep historical queries can run in the background.
- **cost:** Low per action: local event collection dominates; one short summarization call only when the owner asks for spoken detail. Storage is a bounded rolling event graph, not raw content.
- **security:** The receipt itself must never contain secret values, cookies, tokens, or raw private text. Store hashes, classifications, byte counts, and destinations; redact before any relay/model upload. Browser extension and Mac agent must distinguish owner data from model-generated data and label uncertainty instead of claiming complete OS-level tracing.
- **missing:** OS-level, process-scoped file and network provenance for shell, vision, and browser actions; Browser-extension instrumentation that reports authenticated origin, fields read, downloads, uploads, and navigation destinations without exporting page contents; A shared redaction/classification schema for credentials, personal data, and model context; A durable cross-surface data-flow event graph joined to action/job IDs; A spoken receipt renderer and owner-facing historical query for “what left my Mac?”

### "Undo the last thing you did for me, even if it was a shell command or a browser action, and put my Mac and authenticated tabs back exactly as they were before it."
- **useful because:** Current undo only covers a small set of reversible action types; arbitrary shell and browser mutations are permanent from the owner's point of view. A pre-action semantic checkpoint would make delegation safer and let the owner recover from a wrong interpretation without manually reconstructing files, settings, or tabs.
- **path:** mac-planner → browser-extension → mac-vision → relay-realtime → pendant
- **model tier:** A deterministic snapshot/diff engine performs restore; a background model maps the owner's natural-language target to a checkpoint and explains conflicts. Realtime only handles the short spoken request.
- **latency:** Checkpoint creation should add under 1 second for metadata and copy-on-write filesystem state; restore preview under 2 seconds, with large file rollback continuing in background while the pendant reports progress.
- **cost:** Local disk is the main cost: bounded copy-on-write snapshots and browser session metadata. No per-invocation API cost unless the owner asks for a natural-language conflict explanation.
- **security:** Never silently overwrite changes made after the checkpoint. Keep immutable before/after hashes, action IDs, and a conflict list; secrets and page contents stay local. Browser cookies/passwords must not be copied into the snapshot. Some irreversible external effects (sent email, uploads, payments) must be explicitly reported as non-restorable rather than falsely claiming success.
- **missing:** A copy-on-write, bounded Mac checkpoint facility covering files, app settings, and process-owned state; Browser extension support for tab/window/form/navigation snapshots without copying credentials; A reversible-action manifest that declares external side effects and restoration limits; Three-way restore with conflict detection and durable checkpoint-to-job linkage; A pendant command and truthful progress/result receipt for rollback

### "When the Mac, browser, and relay disagree about what is on screen or what happened, tell me that they disagree, show me the competing evidence, and let me choose which interpretation to act on."
- **useful because:** A hive can have stale browser tabs, a changed foreground app, delayed relay receipts, and conflicting model guesses. Today the owner receives a single blended answer and cannot tell whether it is observed fact or an inference. Explicit disagreement handling prevents confident action on stale state while preserving the system's ability to act.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap deterministic evidence merger first; a background model summarizes the disagreement and ranks observations by freshness and source reliability. Realtime speaks only the compact conflict and collects the owner's choice.
- **latency:** Detect conflicts before action dispatch, under 300 ms when receipts are already present; spoken explanation under 2 seconds. No extra model call when all sources agree.
- **cost:** Low: event normalization and freshness checks are local. Model cost occurs only for genuinely ambiguous conflicts and is bounded to a short summary.
- **security:** Evidence references should be hashes, timestamps, app/tab origins, and redacted snippets—not raw authenticated page contents. Never let a low-confidence inference override a newer direct observation. Record the chosen interpretation and all rejected alternatives for later audit.
- **missing:** A shared typed observation envelope with source, capture time, freshness deadline, confidence, and evidence reference; Cross-surface correlation of Mac vision frames, browser inspections, relay job receipts, and action results; A conflict policy that blocks only the affected action while leaving unrelated work running; A pendant choice protocol with stable interpretation IDs and exactly-once action dispatch; A spoken uncertainty/result format that distinguishes observed, inferred, stale, and owner-selected facts


## What it asked for

_Nothing._
## Its own summary

Produced four distinct owner-facing capabilities: a physical pendant emergency stop that actually kills the active Mac process group; reboot-safe job continuation using the existing ledger/exactly-once machinery; bounded failure diagnosis and one safe recovery attempt with truthful exit metadata; and an offline USB-tethered pendant mode for local Mac control when LTE/cloud is unavailable. I also sent faculty-action the concrete USB HELLO/frame/ACK/CRC/replay fields and clearly separated what exists today (physical serial links, OUTBOX, status/audio recovery) from what is missing.

**Biggest unknown:** The remaining blocker is not another model or route: it is the unverified USB serial protocol and firmware/host wiring. I still need a real read-only serial inventory/handshake probe for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the previously requested mac_usb_serial_diagnostics remains pending/should not be re-requested), plus confirmation whether either device currently emits a known framed stream. Until that exists, the offline pendant and emergency-stop proposals are specified but not runnable end-to-end.

