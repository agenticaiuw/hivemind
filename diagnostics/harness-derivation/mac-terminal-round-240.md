# Harness derivation — mac-terminal — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **bench USB diagnostics** — The granted mac_usb_serial_diagnostics schema still does not resolve to a live capability; no serial/USB inventory exists. Both physical ports remain known from system context, but no bounded read was performed.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; nearest action:get_mac_status score 0.226, and explicitly said no serial/usb/tty capability is in inventory.

## Capabilities it proposed

### "Stop the thing I just asked you to do, even if my Mac is in the middle of a long command."
- **useful because:** Today cancellation is a polite flag: a running shell can continue for up to two minutes and the pendant cannot make it stop. A physical stop request should halt the actual process tree, prevent later queued steps, and tell the owner truthfully whether it stopped or had already completed. This is the single most useful safety-and-control behavior for an always-acting wearable.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime only to authenticate/route the tiny stop intent; no LLM is needed to select the active job. The Mac executor owns process-group termination and receipt generation.
- **latency:** Under 500 ms from button press or spoken stop to SIGTERM of the active process group; hard escalation after 2 s, with a final state within 3 s.
- **cost:** Negligible model/API cost; one authenticated relay event and one Mac job-state lookup. Engineering cost is process-group tracking, a stop-intent route, and pendant mapping.
- **security:** The stop intent must be scoped to the owner's most recent active job, not arbitrary PIDs. Never report success until the child and descendants are reaped; if termination fails, expose that fact on the pendant and dashboard. No command contents leave the Mac.
- **missing:** A relay stop-intent event carrying active-job scope and monotonic request id; run_shell execution in a spawned process group with SIGTERM/SIGKILL escalation and captured termination cause; Mac-to-pendant completion receipt for stop_requested/stopped/already_finished/failed_to_stop

### "Find the document I downloaded yesterday about the contract, prove it came from the page I was on, and open the right copy on my Mac."
- **useful because:** Downloads are currently split between browser provenance and loose Mac files. The owner should not have to remember a filename, distinguish a partial download from a finished one, or trust a duplicate blindly. This joins semantic browser evidence to a local hash/provenance check and returns the exact artifact, not a guessed search result.
- **path:** browser-extension → mac-planner → mac-terminal → relay → dashboard
- **model tier:** Use deterministic sweep/hash/provenance joins first; invoke a cheap background model only to rank document text or titles when several candidates remain. Realtime is unnecessary except for the final spoken answer.
- **latency:** Under 5 s for the common case; up to 20 s if local candidates need text extraction. Never open a candidate before the URL/title/hash match is shown in the receipt.
- **cost:** Usually zero model calls; local filesystem hashing and browser provenance lookup dominate. Small background inference only for ambiguous document ranking.
- **security:** Search only the owner's local Downloads and explicitly selected project folders. Do not upload document bytes or page contents. Return source URL, download timestamp, SHA-256, and candidate path; opening a file is reversible but must never silently send it anywhere.
- **missing:** A typed join service between GET /sweep/survey, local file metadata/hash, and GET /browser/provenance or POST /browser/provenance/trace; A safe document-content index that can rank candidates without exporting bytes; A receipt that binds source URL, browser provenance record, local path, size, and hash; A Mac action that opens the selected verified path

### "If the Mac task gets stuck or fails while I'm away, figure out why, retry only the safe part, and tell me what changed when I come back."
- **useful because:** A long-running personal agent is only useful if failure is handled rather than left as a red job. The current executor runs each action once, cancellation cannot interrupt a shell, and a restart can leave a job permanently 'processing'. This capability would turn unattended work into a truthful, recoverable result without blindly repeating side effects.
- **path:** mac-terminal → mac-planner → relay → pendant → dashboard
- **model tier:** A deterministic supervisor classifies timeout/exit/process-loss and checks the action receipt before retrying. A cheap background model may propose a repair for read-only or explicitly idempotent steps; realtime is reserved for an owner asking for status.
- **latency:** Detect a lost worker within 10 s; produce a diagnosis within 30 s; retry only after a postcondition check. Pendant summary should be available on the next button press without waking a large model.
- **cost:** Low: watchdog and receipt logic are local. One background inference only for ambiguous repair suggestions; no inference for standard timeout, missing-file, or worker-restart cases.
- **security:** Never replay an unknown mutation merely because a job disappeared. Persist pre/post-state and idempotency key, mark uncertainty when post-state cannot be verified, and say 'unknown' rather than claiming failure or completion. Repair proposals must not transmit shell output or sensitive files off-device.
- **missing:** Boot-time reconciliation of processing jobs with child-PID/process-group state; A durable per-action idempotency/postcondition record connected to the job and ledger IDs; An explicit retry class for read-only and owner-declared idempotent actions, with bounded backoff; A pendant/relay failure summary that survives a Mac restart and distinguishes repaired, abandoned, and uncertain

### "Finish this logged-in browser workflow while I’m away from the Mac; if you reach a field only I can answer, ask me through the pendant, then continue without making me repeat the task."
- **useful because:** Today the browser agent can drive a session and the pendant can converse, but they are not one resumable workflow: a browser task that encounters an unknown field either stalls at the Mac or forces the owner to restart and re-explain it. This would make the system feel like one assistant that can carry a task across distance and time, while preserving the browser’s private session and only interrupting for genuinely missing owner input.
- **path:** browser-extension → mac-planner → relay → relay-realtime → pendant → dashboard
- **model tier:** A durable workflow state machine owns navigation, field detection, and resume. Realtime handles only the short question/answer exchange over the pendant; a cheaper background model extracts the answer into a typed field and validates it against the page before resuming.
- **latency:** Detect a blocked field within 2 seconds, ask on the next available voice turn, and resume within 3 seconds after the owner's answer. A workflow may remain parked for days without losing its session or state.
- **cost:** Low-to-moderate: browser polling and durable state dominate; realtime is used only for one concise clarification, with a small background extraction call when the answer is ambiguous.
- **security:** The browser session and page contents stay on the Mac/browser surface; send only the minimum question and the owner's answer through the relay. Never infer sensitive values silently. Every resumed field needs a source tag (owner-spoken, page-derived, or planner-derived), and the dashboard must show exactly what was filled and which step remains.
- **missing:** A durable browser workflow object with paused/awaiting-owner/resumed states, step cursor, and expiry; A relay message type for a browser job to ask one scoped question and correlate the answer to workflow id plus field id; A browser-extension command to return a structured blocked-field descriptor and resume from an exact cursor without replaying prior mutations; A cross-surface receipt that binds the question, answer, field, page URL, and final browser result


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities: (1) a real physical/voice “stop the thing I just asked” that terminates the active Mac process group and reports stopped vs already-finished vs unable-to-stop; (2) provenance-bound retrieval of a downloaded document, joining browser source evidence to local hashes before opening it; and (3) unattended Mac-job recovery that reconciles restarts, diagnoses failures, and retries only verified safe/idempotent steps. I also tested the newly granted USB diagnostic schema: it is still unresolved, so no serial bytes were read.

**Biggest unknown:** The system still lacks a live serial reader/framing parser and stable diagnostic protocol for the physically connected nRF9160 and ESP32. Until that exists, we cannot truthfully report bench hardware health or correlate UART counters with pipeline/action receipts.

