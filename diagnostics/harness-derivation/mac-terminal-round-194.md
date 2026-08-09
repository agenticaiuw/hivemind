# Harness derivation — mac-terminal — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this Mac task even if the USB/LTE link drops, resume it exactly once when the Mac comes back, and tell me what actually happened.”"
- **useful because:** This is the single most useful missing promise: a spoken request becomes a durable transaction rather than a command that silently dies or repeats after a crash. The pendant can enqueue intent, the always-awake relay can track it, and the Mac can resume only the unfinished step with evidence.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Background model for reconciliation and retry planning; realtime only for the initial spoken acknowledgement and final concise result.
- **latency:** Acknowledge within 1 second; resume within 10 seconds of Mac/link recovery; final answer after verified completion or an explicit blocked state.
- **cost:** Roughly $0.002–$0.02 per transaction depending on whether replanning is needed; most retries should be deterministic/local and free of model calls.
- **security:** The owner deliberately allows unrestricted Mac execution. Persist intent and step metadata, but never persist raw inherited environment values or command secrets; record redacted fingerprints. A retry must require an idempotency key and mark non-replayable steps as needing a new plan, not guess. Final speech must distinguish completed, partially completed, and unknown.
- **missing:** Wire the existing pendant outbox intent item into relay job creation when USB is available, not only LTE.; Close the orchestrator ledger on every terminal path and join it to the durable jobId.; Make the existing executionContext idempotency engine authoritative for /execute.; Persist a replay classification and checkpoint per action, and reconcile processing jobs at Mac-agent boot.; Pass an abort signal to child processes and record whether a stopped process was reaped.

### "“Why didn't that request work? Give me one honest explanation across the pendant, link, relay, and Mac, and tell me the next safe action.”"
- **useful because:** Today each surface can report a fragment—stale pendant state, relay job status, Mac failure text, or browser result—but nobody synthesizes the causal chain. This capability turns a confusing failure into an actionable answer, especially when the owner is away from the Mac and cannot inspect logs.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Cheap background model for correlating structured events; realtime only when the owner asks verbally. Deterministic rules should identify transport loss, timeout, process exit, stale session, and partial completion before any model call.
- **latency:** Return a first diagnosis in under 2 seconds from retained records; deeper correlation under 10 seconds. Never wait for a missing node indefinitely—say which evidence is absent.
- **cost:** $0.001–$0.01 per diagnosis; the dominant cost is context if raw logs are resent, so send compact event digests and hashes instead.
- **security:** Do not expose bearer tokens, inherited environment, raw microphone audio, or private browser content in a cross-node report. Preserve provenance and confidence for every claim. A suggested retry or undo must remain advisory unless the owner explicitly asks for execution.
- **missing:** A normalized cross-node event envelope with monotonic sequence, wall time, turn/job/action IDs, and source transport.; A relay-side correlation endpoint that joins pendant delivery events, pipeline events, job receipts, ledger steps, browser commands, and Mac process outcomes.; Mac shell receipts with exit code, signal, PID/process-group lifetime, timeout reason, and output digests.; A compact redacted evidence projection suitable for spoken output.

### "“After you change anything, show me the small before-and-after: what files, apps, browser state, and pendant request state changed—and what definitely did not.”"
- **useful because:** The owner should not have to trust a vague 'done'. A compact cross-surface delta catches wrong-project edits, stale browser sessions, partial shell effects, and duplicate execution. It is especially valuable with unrestricted Mac control because observability is more useful here than another gate.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → faculty-perception
- **model tier:** Deterministic snapshot/diff first; a cheap background model turns the diff into a short spoken explanation. Realtime is unnecessary except for the final response in an active turn.
- **latency:** Capture pre-state before dispatch in under 500 ms; post-state within 2 seconds of completion; spoken delta within 3 seconds.
- **cost:** Usually <$0.005 per invocation; filesystem/app/browser snapshots dominate latency, not model tokens. Hash metadata rather than sending file contents.
- **security:** Respect private browser sessions and secrets: record URL origin/title and DOM/state hashes, not cookies or page text by default. Hash file contents and redact paths marked sensitive. Make snapshots immutable and tied to the exact action id; do not imply absence from an incomplete snapshot.
- **missing:** A cross-surface snapshot schema for Mac process/app/window, selected file metadata, browser tab/session metadata, pendant delivery state, and relay job state.; Pre/post snapshot hooks in /execute and browser command execution, with bounded capture budgets.; A diff endpoint that emits changed/unchanged/unknown with provenance and confidence.; Pendant speech/UI rendering for a compact result and a way to request the full report later.

### "“When I walk away with the pendant, put my Mac into privacy mode, and when I come back, restore exactly what you changed.”"
- **useful because:** The wearable is the one surface that physically knows the owner has left; the Mac knows which windows, audio streams, and authenticated browser sessions are exposed. Combining them gives automatic privacy protection without making the owner remember a command, while reversible state capture prevents an annoying permanent lockdown.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime
- **model tier:** Deterministic local policy and state capture; no expensive model call for entry/exit. Use realtime only if the owner asks what was changed.
- **latency:** Detect departure within 3 seconds; apply privacy posture within 2 seconds; restore within 3 seconds of confirmed return.
- **cost:** Near-zero API cost; local serial/BLE presence and Mac automation dominate. Occasional background model use for selecting ambiguous browser/app state should be avoided or explicitly configurable.
- **security:** Presence must be authenticated, not inferred from an arbitrary serial disconnect. Never close or submit browser work; pause/lock and preserve exact pre-state. Encrypt the restore capsule locally, expire it after a bounded period, and require an explicit owner action before restoring sensitive authenticated sessions if the Mac rebooted.
- **missing:** Authenticated proximity/occupancy signal from the pendant independent of the voice button.; A Mac privacy-policy executor covering display lock, audio mute, notification suppression, and browser tab/session redaction.; Atomic pre-state/restore capsules spanning Mac windows, audio, and browser sessions.; A crash-safe state machine that distinguishes departure, cable loss, Mac sleep, and pendant power loss, with truthful pendant status.

### "“While I’m on a sensitive site or handling private files, keep my voice and screen context on this Mac only; tell me when cloud processing is disabled and restore normal mode when I leave.”"
- **useful because:** The browser and Mac know which authenticated/private context is active, while the pendant currently cannot truthfully tell the owner where a turn will be processed. This gives a practical privacy boundary without requiring the owner to remember a mute command, and it prevents accidental cloud leakage during banking, health, legal, or work sessions.
- **path:** browser-extension → mac-terminal → mac-planner → pendant → relay-realtime
- **model tier:** Deterministic domain/path policy and local routing; no model call to classify configured sensitive contexts. Realtime is used only for local processing when enabled.
- **latency:** Policy reaction under 200 ms on tab/navigation events; pendant indication under 500 ms; no cloud transmission after policy activation.
- **cost:** Negligible incremental API cost; local policy evaluation and serial status updates only.
- **security:** Fail closed when policy state is unknown, but do not pretend a local model is available if it is not. Never send URL query strings, page text, screenshots, or audio upstream in local-only mode. The owner must be able to inspect and override the policy, with every override logged locally.
- **missing:** A signed browser-to-Mac sensitivity event containing origin/path class but not page contents.; A hard routing barrier that prevents audio, transcript, screen capture, and browser inspection from entering relay/cloud while local-only is active.; An on-device or Mac-local speech/reasoning fallback with bounded capability.; A pendant status indication that distinguishes local-only, cloud-enabled, and unknown routing.

### "“After this private task, find every copy of its secrets or sensitive output across the Mac, relay, browser, and pendant buffers, remove or quarantine them, and prove what remains.”"
- **useful because:** Unrestricted shell, browser sessions, pipeline audio, job receipts, and relay logs can each retain different fragments. Today the owner cannot request a cross-surface retention sweep or receive a trustworthy proof of coverage. This capability would make privacy recoverable after an accidental paste, diagnostic command, or spoken secret.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** Deterministic secret fingerprinting, retention inventory, and deletion/quarantine; a background model may summarize findings but must not decide deletion targets from raw secrets.
- **latency:** Inventory within 5 seconds for normal job/session scope; quarantine immediately; complete broader workspace/relay sweep asynchronously with progress reported to the pendant.
- **cost:** Low API cost; local hashing and indexed record search dominate. Storage overhead is modest for encrypted manifests and deletion receipts.
- **security:** Never echo the secret into a model prompt or spoken response. Use local fingerprints, structured redaction, and explicit scope. Destructive deletion needs a recoverable quarantine window and immutable proof of what was searched; cloud/third-party retention outside the system must be reported as unknown, not claimed deleted.
- **missing:** A retention index covering shell stdout/stderr, job receipts, pipeline audio/transcripts, browser inspection results, relay payloads, and pendant outbox/cache.; Secret fingerprinting/redaction that works before persistence, plus retroactive quarantine for existing records.; Authenticated deletion/quarantine operations on relay and browser stores with receipts.; A spoken-safe proof report listing stores, time ranges, hashes, and unknown external copies without revealing content.


## Changes it proposed to its own stack

### `context` — Add a cross-surface evidence projection layer: after each action, store a compact typed event (IDs, timestamps, status, hashes, provenance, and bounded redacted excerpt) and let planners request only the relevant event window instead of resending whole job logs, pipeline records, browser inspections, and Mac context every turn.
- **owner gets:** Answers become faster, cheaper, and more accurate: the system can explain a failure or confirm a change without flooding the expensive model with unrelated history, while still retaining a drill-down report when the owner asks.
- effort: Medium: define an event schema and projection index, emit adapters for execute/jobs, pipeline, browser, pendant delivery, and machine context, then add context selection and retention tests.  ·  risk: An overly aggressive projection can omit the one clue needed for diagnosis. Preserve links to immutable full records, mark missing/unknown fields explicitly, and fall back to raw retrieval when confidence is low.
- cost: Reduces repeated input-token cost substantially; small local storage/index overhead. No new model call required for deterministic projection.  ·  latency: Usually improves latency by shrinking context; projection adds under 50 ms per event.
- security: Redact tokens, cookies, environment values, raw audio, and private page/file contents at projection time. Keep provenance and access scope on every event so cross-node correlation does not broaden visibility.
- depends on: Stable job/action/turn IDs across relay, pendant, browser, and Mac; A versioned event schema; Existing GET /jobs/:jobId, GET /journal/:jobId, GET /pipeline, GET /browser/inspections, and pendant delivery event records


## What it asked for

_Nothing._
## Its own summary

This round produced three non-identical owner capabilities: (1) durable exactly-once cross-node Mac work that resumes after link/host failure, (2) an evidence-backed failure explanation spanning pendant, relay, browser, and Mac, and (3) a before/after cross-surface change report. I also recorded a context/evidence projection change to reduce repeated model context and protect secrets. The process-supervised shell receipt idea was rejected as already present in the backlog, so I did not count or repeat it. The most important capability is the first: today a spoken request can be left processing forever, duplicated on retry, or lose its job/ledger join.

**Biggest unknown:** The USB serial protocol and actual bridge state remain unverified. The pendant and ESP32 are physically attached, but I still need the already-requested mac_usb_serial_diagnostics capability (or an equivalent bounded diagnostic) to read device enumeration, framing/firmware identity, and whether either serial endpoint is currently producing events. I also need relay-realtime's answer on whether turn migration/local USB event routes already exist, to avoid another rejected local-control proposal.

