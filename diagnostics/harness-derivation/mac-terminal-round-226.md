# Harness derivation — mac-terminal — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state and execution receipts** — At 2026-08-09T00:00Z the Mac agent reports browser online with current Safari tab YouTube (Max Hodak video) while affinity remains url:https://news.google.com/search. A recent run_shell job now exposes shell argv, exitCode, signal, killed, timedOut, durationMs, outputTruncated, and interruptible in its result, but its receipt evidence is still source:'unlinked'.
  - evidence: GET /ops/status and GET /jobs

## Capabilities it proposed

### "“Stop whatever you are doing right now.” The pendant should halt the active Mac command, browser command, relay audio/job, and any queued follow-up, then tell me exactly what stopped and what could not be stopped."
- **useful because:** The owner needs an immediate, physical escape hatch when an action is wrong or unexpectedly long. It only becomes dependable when the worn button, always-awake relay, Mac executor, and authenticated browser session all participate; a Mac-only cancel cannot stop a browser command or a relay-held audio turn.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic routing and typed cancellation; use realtime only for the short spoken acknowledgement, never for deciding which jobs to kill
- **latency:** Emit the local pendant cancel indication immediately; relay fan-out under 300 ms; Mac/browser cancellation receipts under 2 s, with an honest 'stop requested; process still unwinding' state for non-interruptible work.
- **cost:** Near-zero model cost for the cancel path; one small authenticated relay write and ordinary Mac/browser requests dominate.
- **security:** A physical cancel must be scoped to this owner's paired active work, not arbitrary historical jobs. Persist a cancellation nonce and return per-surface results; never claim a shell was killed when current cancellation is only cooperative between steps. Require no conversational confirmation because the point is emergency control.
- **missing:** A relay fan-out cancellation primitive keyed by turn/job/session; Mac run_shell propagation of AbortSignal to the child process plus truthful killed-vs-requested outcome; Browser command cancellation keyed by commandId and turnId; A shared active-work index joining pendant turn, relay job, Mac job, and browser command

### "“Continue where I left off.” The system should reconstruct the last unfinished task across my pendant conversation, frontmost Mac project, and the exact browser tab/session, then ask only the one missing question before resuming."
- **useful because:** Today a dropped audio turn, stale browser affinity, or a Mac restart loses the thread even though each node retains fragments. A compact, time-bounded resume capsule would let the owner pick up work while walking away from the desk without repeating the setup.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background model to periodically compress completed turns into a capsule; deterministic retrieval and consistency checks on resume; realtime only to speak the recovered one-sentence state
- **latency:** Capture incrementally without delaying actions; resume lookup under 500 ms and speak within 2 s. If evidence disagrees, do not resume silently—state the conflict in one sentence.
- **cost:** Low: one background compression per completed multi-surface task, with retrieval usually zero additional model calls. Storage is a few KB per capsule, bounded to recent unfinished tasks.
- **security:** Capsules must be encrypted/paired and expire; do not store page text or secrets when a URL/title/selection hash suffices. Require an explicit owner resume phrase or button event, and mark a capsule consumed so a side effect is never replayed merely because it was resumed.
- **missing:** A shared capsule schema with turnId, unfinished intent, last safe checkpoint, Mac job/ledger IDs, browser session/command IDs, active project, and evidence timestamps; Atomic checkpoint writes from relay, Mac, and browser before a link loss or process exit; A resume planner that distinguishes informational continuation from a side effect that must be re-confirmed; A pendant spoken/button resume entry point that already has access to the paired capsule

### "“Try this, but make it completely reversible.” Before acting, the system should capture a restorable checkpoint of my relevant Mac files and app state, browser tabs/session state, active project, and pending pendant/relay work; after the experiment I can say “put everything back exactly as it was.”"
- **useful because:** The owner can currently undo a few typed actions, but cannot safely experiment across a browser session, local files, an app workflow, and an active voice task as one unit. This would make the system useful for high-leverage changes without forcing the owner to remember every tab, file, and pending action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic checkpoint/restore engine with a cheap background model only for identifying the relevant task scope and explaining the final diff; realtime is unnecessary except for the pendant acknowledgement.
- **latency:** Create a lightweight checkpoint in under 2 seconds for ordinary app/browser state; file snapshots may continue asynchronously but must reach a committed state before mutation begins. Restore should begin within 1 second and report item-by-item progress.
- **cost:** Low model cost. Storage is the dominant cost: content-addressed local snapshots for selected files plus small browser/session metadata. Retain only the latest few owner-requested checkpoints and garbage-collect unreferenced blobs.
- **security:** Never snapshot secrets or entire home directories by default. Show the exact scope before committing the checkpoint, preserve permissions and extended attributes, keep data local to the Mac where possible, and cryptographically bind restore operations to the owner's paired device and checkpoint nonce. A restore must distinguish successfully restored, externally changed, and impossible-to-restore items.
- **missing:** A cross-surface checkpoint manifest with stable object IDs, hashes, timestamps, and dependency ordering; Mac snapshot adapters for files, app/window state, active project, and reversible shell effects; Browser adapters for tabs, navigation/session metadata, form state where safely available, and pending command cancellation; Relay/pendant adapters for queued work and the active audio turn without replaying consumed audio; A two-phase restore engine with conflict detection rather than blind overwrite; A user-facing checkpoint diff and retention policy

### "“Keep this entirely private.” For the next task, the system should prove before execution which data stays on the Mac/pendant, which model runs locally or in the cloud, and which browser/session content is exposed; it should complete the task without sending protected content to the relay, or clearly say that it cannot."
- **useful because:** The owner cannot currently make a spoken, task-scoped decision about data locality. A browser page, shell output, audio turn, and model prompt cross different trust boundaries, while the owner gets no durable proof of what left the machine. This would make sensitive work usable rather than requiring the owner to understand the architecture each time.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic data-flow classifier and routing policy; use a background model to explain the resulting data map in plain language. Realtime must be bypassed for protected turns unless an explicitly approved redacted route exists.
- **latency:** Produce the privacy/data-flow preview within 500 ms before execution. If local execution is possible, begin normally; if a remote model is required, explain the blocking dependency in under 2 seconds.
- **cost:** Minimal extra model cost when classification is schema-based. Local storage for signed policy decisions and redaction manifests is negligible; local inference or a private model may add hardware/model cost.
- **security:** Privacy mode must be enforced below the planner, not as a prompt instruction. Redact secrets and page bodies before telemetry, prevent protected audio from entering cloud STT, and provide a tamper-evident local receipt of destinations, fields, and hashes. The owner must be able to explicitly permit a named host/model for one task.
- **missing:** A task-scoped privacy contract carried from pendant through relay to Mac and browser; A data-flow inventory describing every field sent to relay, STT, TTS, planner, browser, and logs; Local/offline speech and language fallback or a truthful refusal when unavailable; Field-level redaction before pipeline/audio, browser provenance, job logs, and model prompts; A signed owner-readable privacy receipt and policy-expiry mechanism

### "“Handle this until it is genuinely done; only interrupt me if you are blocked.” The system should run a bounded multi-step objective across my browser and Mac, survive sleep or a lost pendant link, verify the result against an explicit completion test, and notify me only on completion, expiry, or a real blocker."
- **useful because:** The owner currently gets individual actions and jobs, not dependable ownership of an objective. This is the difference between “click these steps” and having an assistant that can finish a research, filing, or cleanup task without making the owner supervise every intermediate operation.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background planner for decomposition and periodic progress compression; deterministic executor for approved steps and completion predicates; realtime only for exception alerts or the final short result.
- **latency:** Start within 2 seconds, then operate asynchronously. Check progress after each step and at a bounded heartbeat (for example 30 seconds); alert immediately on a blocker, deadline breach, or unsafe ambiguity.
- **cost:** One planning call per objective plus cheap background checks; most steps use deterministic Mac/browser actions. Storage is a small durable objective record and evidence trail.
- **security:** The objective must have a scope, deadline, allowed surfaces, and stop conditions before it runs. Never broaden permissions because a step failed; pause on authentication, destructive ambiguity, or changed page semantics. Persist every attempt and distinguish verified completion from mere action dispatch.
- **missing:** A durable objective state machine separate from one-shot jobs, with deadline, scope, retry budget, and completion predicate; A relay scheduler that continues while the Mac or pendant is temporarily offline; Browser and Mac step executors that checkpoint after every side effect and resume idempotently; A verifier that can test a concrete outcome using fresh evidence rather than trusting the last action; Exception-only notification routing to the pendant and a final owner-readable evidence summary


## Changes it proposed to its own stack

### `integration` — Add a turn-scoped causal receipt that joins every relay dispatch, Mac action receipt, browser command/provenance record, and audio delivery into one append-only graph. Each node records before/after observations, exact timestamps, outcome (including exit code, signal, timeout, and browser acknowledgement), and an explicit 'not observed' state. Expose a small owner-facing diff such as “opened YouTube; no download occurred; spoken reply delivered to pendant,” rather than dumping logs.
- **owner gets:** When the owner asks “did you actually do that?”, the system can answer from one honest chain of evidence instead of conflicting Mac jobs, stale browser affinity, and audio text. This is felt as trust: completed means observed, not merely dispatched.
- effort: Medium: define the receipt graph and turn correlation, add adapters at relay job creation, POST /execute completion, browser/result, and pipeline audio; add a summarizer and retention/redaction tests.  ·  risk: Existing receipts must remain readable during migration. Missing or delayed telemetry could make a receipt say unknown rather than false success; use dual-write and a repair job. Avoid storing page bodies, shell environment values, or audio contents—retain hashes, titles, URLs, and bounded status fields.
- cost: Small storage increase (bounded records per turn); no extra model call for raw receipts. Optional natural-language diff uses a cheap background model, not realtime.  ·  latency: No meaningful action-path delay if events are queued; owner-facing verification adds under 300 ms when all records are local, longer only when waiting for browser acknowledgement.
- security: Receipts may reveal sensitive URLs and filenames, so redact query secrets and hash paths by default, with local-only detail available to the owner. Keep the existing bearer/paired-device boundaries.
- depends on: A stable turnId/jobId correlation propagated into POST /execute and browser commands; Close the currently open action ledger and link planMeta.jobId to it; A bounded event store with monotonic sequence numbers and crash-safe append; A read endpoint or dashboard panel for the causal diff


## What it asked for

_Nothing._
