# Harness derivation — mac-terminal — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Read the page I mean in Safari and give me a trustworthy answer, even if the first extraction fails."
- **useful because:** Live evidence shows browser_read_page has an 80% failure rate for one repeated action family (8 failures in 10 runs), while the browser is online and authenticated. Today the system can confidently return a failed or partial read instead of recovering. A browser task should automatically retry with a bounded alternate path (refresh, re-target tab, screenshot/computer-use extraction, then report the exact evidence and failure reason) while keeping the same tab/session affinity. This is the single most useful capability: it turns the wearable's request to 'check this' into an answer that is either grounded or explicitly unavailable, not a brittle one-shot.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use the cheap planner/model for intent and failure classification; use the browser harness for DOM/text; escalate to mac-vision only when DOM extraction fails; reserve realtime for the spoken request and short result.
- **latency:** Normal success under 3 seconds; one recovery attempt under 8 seconds; vision fallback under 20 seconds, with a concise progress status to the pendant.
- **cost:** Usually no extra model cost; failed DOM recovery may add one vision inference and screenshot upload, roughly $0.01-$0.08 depending on image tokens. Browser actions and relay traffic dominate latency, not text generation.
- **security:** The browser may contain authenticated financial, mail, or work pages. Keep the existing tab/session affinity, never send page contents to the cloud model unless the task requires it, redact secrets from receipts, and state which tab and timestamp supplied the evidence. No confirmation is needed for reads.
- **missing:** A failure-aware browser read orchestrator with bounded fallback strategies; Typed browser evidence receipts containing tabId, URL/title, extraction method, timestamp, and confidence; A computer-use fallback that can be invoked specifically after browser_read_page failure without losing session affinity

### "Start this multi-step job on my Mac and keep going until it is finished, even if the agent or link restarts; tell me exactly what was completed and what remains."
- **useful because:** The current job store can report 120 recent jobs, but execution has no retries, cancellation cannot interrupt a running shell, ledgers remain open, job IDs do not join to ledgers, and a restart leaves jobs stuck in processing forever. For a real wearable, 'I asked you to do it' must survive a laptop sleep/restart and a dropped relay link. A durable runner would checkpoint each action, retry only idempotent failures, resume from the first unknown step, and produce a spoken completion receipt instead of silently repeating side effects.
- **path:** relay-realtime → mac-planner → mac-terminal → unified
- **model tier:** Use a cheap background planner to materialize and checkpoint the action graph; use realtime only to accept the request and summarize; use deterministic typed execution for retries and resume, not another expensive model turn.
- **latency:** Immediate acknowledgement under 1 second; each step executes at normal local speed; after restart, resume within 10 seconds of agent health returning. Never claim completion until a durable receipt exists.
- **cost:** Near-zero model cost for deterministic retries; occasional planner call ~$0.01-$0.05 when a failed step needs replanning. Storage is a few KB per job plus existing receipts.
- **security:** Maximum-access policy remains unchanged. The runner must classify steps for replay safety and never blindly repeat non-idempotent shell, email, purchase, or deletion actions; mark them unknown and ask the owner through the pendant. Persist only redacted command metadata and do not write inherited secrets into the job record.
- **missing:** Boot-time reconciliation of processing jobs and orphaned children; Actual wiring of executionContext idempotency/retry into /execute; closeLedger and a durable jobId-to-ledger mapping on every execution; Per-step retry policy and process-group cancellation for run_shell; A resume endpoint/worker that can execute the existing runnable ledger rather than merely returning it

### "Why did that Mac or browser task fail, and what is the safest concrete next attempt?"
- **useful because:** The live journal shows 53 failed actions in the 120-job window, but failures are flattened into messages and the owner has to reconstruct the cause. A spoken failure explainer would correlate the job, action receipt, stderr, browser tab/session, timeout, and environment-independent diagnostics; classify the failure as transient, target mismatch, permission, timeout, or irreversible unknown; then propose one exact retry or tell the owner what must be fixed. It saves the owner from repeating a vague request and avoids burning realtime turns on raw logs.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use deterministic extraction and a cheap background classifier first; invoke realtime only to explain the already-built diagnosis in a short spoken answer. Escalate to the expensive model only when logs disagree or the recovery is ambiguous.
- **latency:** Return a first diagnosis in 2 seconds from stored receipts; gather one bounded read-only diagnostic within 5 seconds; no automatic mutation. If a retry is clearly idempotent, offer it as the next action rather than silently running it.
- **cost:** Usually <$0.01 per incident for a small classifier/context; most work is local parsing. No screenshot or page content leaves the Mac unless the original failure already required vision.
- **security:** Do not expose inherited environment variables, tokens, raw authenticated page contents, or full stderr to the relay. Redact secrets and provide only command class, exit status, path/app, and a bounded error excerpt. Never recommend repeating a non-idempotent mutation without explicitly labeling its unknown state.
- **missing:** Normalized failure taxonomy and redaction layer for shell, browser, vision, and AppleScript results; Exit code/signal and process timing capture for run_shell receipts; A correlation join across job, action receipt, journal, browser command, and ledger IDs; Read-only repair-plan output that is separate from action execution

### "Take the attachment from the email or web page I mean, verify what it is, place it in the correct project folder, and tell me exactly where it went and what it contains."
- **useful because:** Today the browser can see authenticated pages and the Mac can manipulate files, but the owner cannot ask for this as one trustworthy operation. This would bridge the browser's private session to the Mac's filesystem: identify the intended attachment from the spoken reference, download it, verify filename/type/hash and destination, avoid accidental duplicate overwrites, and return a provenance receipt. It eliminates the tedious and error-prone handoff between Safari and Finder/Terminal.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → unified
- **model tier:** Use a cheap planner for reference resolution and file classification; deterministic browser download and filesystem operations do the work; use realtime only for the spoken request and concise receipt.
- **latency:** Locate and inspect within 5 seconds; download/file within 15 seconds for normal attachments; report progress if a large file takes longer.
- **cost:** Usually <$0.02 in model calls; browser and local file I/O dominate. Hashing and metadata inspection are local.
- **security:** Authenticated content and downloaded files remain local unless the owner explicitly asks for cloud analysis. Never overwrite silently; preserve the source URL, tab ID, timestamp, SHA-256, MIME type, and destination. Treat archives and executable files as opaque unless explicitly requested.
- **missing:** A browser-to-filesystem attachment transfer primitive with explicit source-tab affinity; Download completion detection and file identity verification; Destination resolver based on active project/session context; A provenance receipt linking browser command, local path, hash, and content summary

### "Find the issue or failed check in my authenticated developer tools, reproduce it in the matching local project, and give me a minimal evidence-backed fix plan without changing code unless I ask."
- **useful because:** When a CI failure or issue is visible only in a logged-in browser, the owner currently has to manually copy it into the Mac project and reproduce it. This capability would connect browser evidence, project identity, local shell diagnostics, and the spoken interface. It would report the exact failing check, local reproduction command, environmental differences, and smallest proposed change, while keeping mutation separate from diagnosis.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → unified → faculty-perception → faculty-judgement
- **model tier:** Use deterministic extraction for issue/CI metadata and local test execution; use a cheaper reasoning model to compare traces and formulate the plan; reserve realtime for interaction and summary.
- **latency:** Extract browser evidence under 4 seconds; run bounded local reproduction under 30 seconds; for longer tests return a durable job receipt and continue in background.
- **cost:** $0.01-$0.10 per investigation depending on trace size and whether reasoning is needed; shell/test execution is local. No source code or private logs should leave the Mac by default.
- **security:** Authenticated issue pages and repositories are sensitive. Keep browser content and source local, redact tokens and secrets from test output, and enforce a read-only diagnostic mode until the owner explicitly asks to modify code. The plan must distinguish browser-reported failure from locally reproduced failure.
- **missing:** A typed browser-to-project evidence handoff for issue URLs, checks, logs, and revision IDs; A project resolver that maps repository/revision to a local checkout; Bounded test execution with structured exit codes, diffs, and environment fingerprints; A diagnosis object that cites browser evidence and local reproduction separately

### "Since the last time I worked on this project, tell me what changed across the local checkout and its authenticated issue/PR pages, what is unfinished, and what I should do next."
- **useful because:** The owner should not need to remember whether a change happened locally, in a pull request, or in a CI dashboard. This creates a time-bounded project delta across the Mac checkout and authenticated browser, joins commits/files/PR comments/checks, and presents only meaningful changes with exact evidence and an unfinished-work list. It is a personal continuity function rather than another generic status page.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → unified
- **model tier:** Use local git and browser extraction deterministically; use a low-cost summarizer for diffs and issue/check deltas; use realtime only to answer the owner and ask a clarifying question when multiple projects match.
- **latency:** Known active project under 5 seconds; a large repository or many PR pages under 20 seconds with a background receipt and incremental spoken update.
- **cost:** Typically <$0.03 for compact diffs and metadata; local git work is free. Large diffs should be summarized locally or chunked rather than uploaded wholesale.
- **security:** Source code, private PR discussion, and repository URLs stay on the Mac by default. Store only redacted snapshots and hashes, not full source. Make the comparison window explicit and never infer that an untracked file is safe to delete or publish.
- **missing:** Durable project snapshots with commit/tree/file hashes and a user-visible comparison timestamp; Authenticated browser extraction for the matching repository, PR, issue, and check records; A cross-source join keyed by repository and revision rather than tab or job alone; A compact delta report with citations to local paths and browser evidence


## Changes it proposed to its own stack

### `context` — Add a live `wearable_presence` context provider in the Mac agent that probes the two known USB serial identities, bridge heartbeat, pendant link state, and relay registration, then exposes one freshness-stamped state object to relay-realtime and unified. Inject only the compact state (attached/disconnected, audio path, last ack, age, current turn id) rather than raw serial output. When the pendant is attached by USB but LTE is absent, the assistant should explicitly say 'your pendant is connected locally; cellular is unavailable' instead of treating it as offline without qualification.
- **owner gets:** The owner gets truthful answers about whether the thing they are wearing is actually reachable right now, and the system can choose the local Mac path instead of needlessly failing over to an unavailable cellular path. This is especially valuable today because both boards are physically plugged in while the nRF9160 is not registered with the relay.
- effort: Medium: a small serial-presence probe and bridge adapter, freshness/lease state, and context projection into the relay turn; then fault-injection tests for unplug, stale heartbeat, and reconnect.  ·  risk: A stale cached presence could cause the assistant to promise a path that has died. Every field needs an age and expiry; after expiry report unknown, never connected. Serial probing must not contend with the audio reader or consume the device stream. Recover by restarting only the probe, not the audio session.
- cost: Negligible API cost and a few periodic local reads; modest engineering/testing time. No new hardware cost.  ·  latency: Adds under 50 ms to local context lookup; polling can run in the background and not touch turn latency.
- security: USB device identity and serial metadata stay local; only coarse health crosses to relay. Pair the device identity to prevent another USB serial device being mistaken for the pendant.
- depends on: A real USB serial diagnostics/transport implementation (the already queued mac_usb_serial_diagnostics request is still needed); A bridge heartbeat/status adapter; Relay context projection for a freshness-stamped wearable_presence object


## What it asked for

_Nothing._
