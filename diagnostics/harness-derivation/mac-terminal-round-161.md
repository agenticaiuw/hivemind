# Harness derivation — mac-terminal — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/USB posture** — The Mac bridge is online and Safari has 9 tabs, but the cloudflare-contract-test mobile device is offline. The pendant/bridge USB serial hardware is physically connected per current run context yet has no registered LTE relay identity; local USB integration remains the fastest path to owner-visible value.
  - evidence: discover:devices returned home-macbook-bridge online and cloudflare-contract-test offline; system context states nRF9160 /dev/cu.usbmodem00096003658* and ESP32 /dev/cu.usbserial-0287A9CA are connected and unregistered.

## Capabilities it proposed

### "“Do that Mac task, and if it fails, keep trying safely until it either succeeds or tell me exactly what stopped it.”"
- **useful because:** The current shell path runs one attempt, loses the exit code, and cancellation cannot stop a live process. A wearable owner needs a dependable outcome, not a confident one-shot response—especially when the Mac is briefly asleep, a network command flakes, or the agent restarts.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Use realtime only to interpret the spoken request and announce state; use a cheaper background worker for bounded retries and verification. The Mac executes; the relay persists the intent and result.
- **latency:** Acknowledge dispatch on the pendant within 1 s; retry with exponential backoff for up to the owner-specified deadline (default 5 min), with spoken updates only on state changes.
- **cost:** About one realtime turn for intent plus 2–6 cheap verifier/retry calls; shell execution dominates latency, not tokens.
- **security:** Maximum-access policy remains unchanged. Retries must be explicitly bounded and use the same action idempotency key; mutating actions need an owner-declared retry mode (never blindly repeat an email, purchase, delete, or send). Persist command, cwd, exit code, attempt number, and redacted output; never persist inherited secrets.
- **missing:** A durable retry supervisor that consumes the existing action ledger and execution receipts; Process-aware shell cancellation and a verifier hook per action; A pendant/USB command-status event carrying attempt, deadline, and terminal reason; A typed retry-safety annotation in the planner schema

### "“Stop the thing running on my Mac right now.”"
- **useful because:** Today cancellation only sets a cooperative flag; a running shell can continue for the full 120-second timeout and the pendant may say it stopped when it did not. This gives the owner a real emergency stop for a runaway command without adding approval gates to normal work.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → dashboard
- **model tier:** Realtime interprets the short command and confirms the target job from the cheap job-status lookup; the Mac agent performs the process-group termination; realtime speaks the verified result.
- **latency:** Return “stopping” locally in under 500 ms and terminate/verify the process group within 2 s. If the Mac is unreachable, cache the cancel intent on the pendant and relay it exactly once when connectivity returns.
- **cost:** One lightweight status lookup and one action call; no expensive model call after intent classification.
- **security:** Target only a job ID selected from the owner's active jobs, never arbitrary PIDs. Send SIGTERM to the shell's process group, wait briefly, then SIGKILL only that group; record signal, descendants, and final exit status. A stale cancel must not affect a reused PID. The pendant should show “cancel requested” until Mac verification, never “stopped” optimistically.
- **missing:** Run-shell process-group/PGID capture and signal-aware execution; A real cancel route that kills and verifies the child rather than only aborting between steps; USB/LTE delivery of a signed cancel intent with job-id and monotonic sequence; A durable terminal receipt for cancelled-by-owner

### "“When I press the pendant button while it is plugged into my Mac, run my configured ‘focus’ routine and tell me what it changed—even if the relay is offline.”"
- **useful because:** The hardware is physically present over USB today but unregistered with LTE relay. This turns the wearable into a useful local control surface now: one tactile press can invoke a safe, preconfigured routine, and the owner gets a truthful spoken/LED result rather than waiting for nonexistent LTE.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → dashboard
- **model tier:** No expensive realtime turn for the button event. The local Mac bridge maps a signed button event to a stored routine, executes it through the existing planner/action path, and sends a short result; realtime is used only if the owner asks a follow-up question.
- **latency:** LED/button acknowledgement under 100 ms; routine dispatch under 1 s; completion within the routine's normal duration. Queue the event locally if the USB link blips, with exactly-once sequence handling.
- **cost:** Zero model calls for a configured routine; one cheap summarization call only for an unusual failure. USB serial and routine execution dominate.
- **security:** Only pre-authorized routine IDs, not arbitrary shell from a raw button edge. Bind events to the pendant's device key, monotonic counter, and recent USB session; reject replayed counters. Expose the routine name and changed resources in the receipt. No microphone is opened by the button-to-routine path.
- **missing:** A USB serial event adapter for the live nRF9160 device at /dev/cu.usbmodem00096003658*; A local routine trigger endpoint that accepts authenticated device events and returns a receipt; Exactly-once event deduplication across USB reconnect and relay handoff; A compact routine-result packet that the pendant can render via the existing status beacon

### "“Start this work on my Mac, let me leave, and keep me updated through the pendant; if the browser or Mac becomes unavailable, pause at the exact step and resume when it returns.”"
- **useful because:** Today a multi-step task is tied to the live Mac worker: cancellation is cooperative, jobs can remain falsely processing after a restart, and authenticated browser work cannot be safely resumed as a portable conversation. The owner should be able to walk away without losing the task or receiving a fabricated completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use realtime only for the initial spoken intent and concise state changes. A durable background workflow worker owns step execution, browser-session affinity, checkpoints, and reconciliation; use a cheaper model for step summaries and recovery decisions.
- **latency:** Pendant acknowledgment under 1 s; status changes delivered within 2 s while connected. Recover after Mac/browser return within 10 s, reopening only the checkpointed step rather than replaying prior side effects.
- **cost:** One realtime interpretation, then inexpensive background orchestration and occasional summarization; browser and Mac execution time dominate cost.
- **security:** Browser cookies and page contents stay on the browser host; relay stores opaque workflow IDs and encrypted checkpoint metadata, not session secrets. Each checkpoint records whether a side effect was committed before resume. Never claim completion unless a postcondition is observed. The owner can say “stop” from the pendant, but normal execution remains ungated under the owner's maximum-access policy.
- **missing:** A durable workflow/checkpoint runner spanning relay, Mac, and browser sessions; Atomic step commit records joining job, ledger, browser command, and receipt IDs; Boot/reconnect reconciliation that distinguishes committed, interrupted, and unknown side effects; A pendant protocol for workflow status, pause, resume, and verified terminal outcomes; Browser-side checkpoint-safe actions and postcondition observers

### "“Why are you telling me that—what did you actually see, and what did you infer?”"
- **useful because:** The owner currently receives a spoken answer that can blend browser observations, Mac state, and model inference without a compact way to challenge it. A wearable provenance response would make the hive trustworthy: it could name the exact tab/file/job observation, its age, and the inference boundary without reading a giant log aloud.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap structured provenance formatter first; invoke realtime only to phrase the selected evidence naturally. Never ask a model to invent provenance from conversation history—the response must be assembled from signed observation records.
- **latency:** Return a two-sentence spoken provenance answer within 2 s, with an optional dashboard expansion to the full evidence chain.
- **cost:** Usually no additional model call beyond a small formatter; storage and indexing of observation metadata dominate.
- **security:** Speak only a redacted summary by default. Keep authenticated page contents and sensitive file paths on their originating host; relay carries opaque evidence IDs and hashes. Distinguish observed, stale, inferred, and unknown states, and never expose secrets merely because they contributed to an answer.
- **missing:** A common immutable observation-envelope schema for browser, Mac, relay, and pendant events; Evidence IDs and hashes attached to every planner claim and spoken response; A provenance query that joins browser command results, Mac receipts, and context-graph facts; Pendant speech/UI support for “observed versus inferred” and evidence age; Retention and redaction rules for sensitive evidence

### "“Before I send this, tell me exactly what private information is leaving my Mac and where it is going.”"
- **useful because:** Maximum-access execution does not mean the owner should be blind. The browser session, Mac files, and wearable are each able to see different parts of a send operation; together they can produce a last-moment data-flow explanation, including hidden attachments, copied text, recipients, and destination domain.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use deterministic extraction and host-side redaction classification first; use a cheap model only to summarize ambiguous content. Realtime speaks a short inventory, while the dashboard shows the full diff. This is advisory and does not add a gate unless the owner separately asks for one.
- **latency:** Show a preview within 3 s for ordinary text and under 10 s for an attachment; updates must identify changes if the browser page or clipboard changes before submission.
- **cost:** No realtime cost for deterministic fields; modest background classification cost for document snippets. Keep raw content on the Mac/browser host.
- **security:** The analyzer itself must not exfiltrate the private material it is inspecting. Process locally where possible; relay only categories, destination, hashes, and minimal redacted excerpts. Handle clipboard, hidden form fields, attachments, BCC, and browser redirects explicitly. Preserve the owner's maximum-access policy; this is visibility, not a mandatory blocker.
- **missing:** A browser send-preview hook that captures final destination, recipients, fields, attachments, and redirects; A Mac-side data-flow inspector for clipboard, selected text, files, and app-to-browser transfer; Cross-surface content hashes and a diff between what was drafted and what will be submitted; A redaction classifier with local-only execution for sensitive material; A pendant response format for concise destination-and-data summaries


## Changes it proposed to its own stack

### `mac-harness` — Replace run_shell's exec(string) implementation with a process-supervised runner that preserves the original submitted action, normalized argv when available, resolved cwd, redacted environment names plus a hash, PID/PGID, start/finish timestamps, exit code, signal, timeout reason, and bounded stdout/stderr tails in the receipt. Keep FULL_CONTROL_MODE and unrestricted execution exactly as-is; this is evidence, not a gate.
- **owner gets:** After asking the pendant to do something, the owner can know whether it actually ran, what failed, and what to say next. Today a non-zero shell exit is flattened into a message and the command may even be rewritten before the audit record, making debugging and trust impossible.
- effort: Medium: runner wrapper, receipt schema migration, redaction tests, and preserving a pre-rewrite action snapshot.  ·  risk: A wrapper could alter quoting or signal behavior. Shadow-record old and new execution metadata, retain the existing path as fallback, and test shell metacharacters, timeouts, and rewritten overlay/research commands.
- cost: Negligible storage (bounded tails and metadata); no additional model/API cost.  ·  latency: Under 10 ms bookkeeping per action; process execution unchanged.
- security: Improves auditability while not restricting access. Environment values are never stored; only allowlisted variable names and a one-way digest are retained.
- depends on: A durable versioned action-receipt schema; Job-to-ledger correlation by always passing planMeta.jobId

### `integration` — Add a local USB pendant bridge service that opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with explicit device identity, framing, CRC, monotonic event counters, and reconnect backoff. Translate a button event into a signed local job-intent record, invoke only a configured routine or planner intent, and return a compact receipt/status frame; when LTE later registers, forward unacknowledged records to the relay without replay.
- **owner gets:** The pendant and audio bridge are physically attached to the Mac now, so the owner can use the device today instead of waiting for LTE registration. A disconnect or reboot will not silently lose a button press or run it twice.
- effort: Medium-high: serial framing and discovery, daemon lifecycle, firmware counterpart, exactly-once store integration, and end-to-end tests across disconnects.  ·  risk: Bad framing or stale counters could duplicate an action. Require device/session handshake, CRC, monotonic sequence plus durable acknowledgement, and default to reporting an unrecognized event rather than executing it.
- cost: No API cost; one small always-on Mac process and negligible USB power.  ·  latency: Button acknowledgement <100 ms; routine dispatch typically <1 s after frame receipt.
- security: USB is a local trust boundary: authenticate the device key and bind events to the active user session. Do not expose a network listener or forward microphone/audio data through this path.
- depends on: A device-key handshake and serial protocol in firmware; A local routine-intent route between the serial bridge and POST /routines/:routineId/run; Exactly-once event receipts shared with the relay outbox; A live USB serial diagnostic/permission check


## What it asked for

_Nothing._
