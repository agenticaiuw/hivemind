# Harness derivation — mac-planner — round 294

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button, save what I was doing so I can later ask, “What was I in the middle of?”"
- **useful because:** This is the highest-value missing handoff: a physical, zero-speech interruption marker becomes a recoverable snapshot of the owner's work. The pendant supplies the exact moment even when the owner cannot talk; the relay preserves it; the Mac contributes calendar, foreground app, document, and browser context; later the owner gets one short spoken answer and can reopen the relevant work.
- **path:** pendant offline_moment_bookmark queues a timestamped marker → relay stores and correlates the marker, then requests Mac context capture → Mac reads Calendar/Mail only if relevant, inspects foreground app and browser tabs, and writes an immutable context capsule under ~/AI-Pendant-Workspace → relay-realtime summarizes the capsule on a later voice query → mac-planner optionally reopens the cited document or browser tab after the owner asks
- **model tier:** Use the cheap background model to normalize and index each bookmark; use realtime only for the later spoken retrieval and only send the selected capsule, not the whole history.
- **latency:** Bookmark acknowledgement must be local and immediate. Context capture should finish within 5 seconds; later spoken retrieval under 1.5 seconds after the capsule is indexed.
- **cost:** About $0.001–$0.01 per bookmark for background extraction, dominated by summarization; retrieval is a small realtime turn. Mac workbench storage is negligible.
- **security:** Context can contain document names, URLs, and snippets. Default to app/title/URL metadata with redacted text; do not capture microphone audio. Reopening or editing anything requires an explicit later request, and destructive actions remain confirmation-gated by owner policy.
- **missing:** A relay route to accept offline_moment_bookmark records and correlate them with a Mac context snapshot; A redacted semantic context reader for selected document/window identity; current inspect gives only coarse UI/browser state; A durable bookmark-to-capsule index and retrieval endpoint

### "If my Mac restarts or my browser crashes, restore the work session I was using—including the right tabs, files, and a short explanation of what was unfinished."
- **useful because:** A browser crash currently destroys the invisible state that makes a work session useful. This makes the hive resilient: the browser extension contributes authenticated tab identity without exporting page contents, the Mac contributes open files and workspace state, and the relay keeps a compact checkpoint that survives the reboot. The owner returns to the task rather than reconstructing it.
- **path:** browser extension periodically reports a privacy-filtered tab manifest and session heartbeat → Mac planner checkpoints open workspace files, VS Code project, and foreground app into the relay workbench → relay stores a deduplicated checkpoint and marks it stale on missing heartbeats → on Mac/browser recovery, mac-planner restores only the selected session's tabs and files, then asks the relay model for a three-line unfinished-work explanation → pendant alert inbox announces that recovery is ready, with a button-triggered spoken summary
- **model tier:** Cheap background model extracts task title and unfinished clues from checkpoint metadata; realtime is used only if the owner asks for the spoken recovery summary.
- **latency:** Checkpoint updates should be asynchronous and under 2 seconds. Recovery should restore the workspace within 10 seconds and speak the summary within 2 seconds after the owner requests it.
- **cost:** Low: mostly metadata and hashes; roughly $0.001–$0.02 per recovery, with storage and browser polling dominating rather than model tokens.
- **security:** Never persist cookies, passwords, page bodies, or selected text by default. Store origin/title/tab IDs and local file paths with redaction. Restoring a tab may recreate an authenticated session, so recovery must target the owner's explicitly selected session and destructive or submission pages must never auto-open.
- **missing:** A browser-side export of restorable tab descriptors that excludes secrets; A Mac workspace checkpoint reader for open VS Code files and unsaved buffers; A recovery coordinator that can distinguish a crash from an intentional shutdown and perform idempotent restore

### "Run a complete pendant health check now and tell me, in one sentence, whether the radio, audio, buttons, and storage are healthy; if not, file a reproducible bug report in my workspace."
- **useful because:** The pendant is physically attached to this Mac over USB today even though LTE is unregistered, so this can deliver value immediately rather than waiting for the product link. It turns opaque UART and audio counters into an actionable verdict: the Mac runs a bounded diagnostic, the relay compares measurements to acceptance thresholds, and the owner receives a short spoken result plus a durable report only when something fails.
- **path:** Mac planner launches the allowlisted bench diagnostic against /dev/cu.usbmodem00096003658* and the ESP32 bridge port, with a fixed timeout and captured stdout → pendant audio_path_diagnostic_fixture exercises synthetic uplink and 24 kHz downlink without recording owner speech → relay-realtime or a background evaluator checks packet drops, decode/encode timings, alias rejection, underruns, and button/LED events against the known acceptance criteria → mac_workbench_transaction atomically writes a timestamped report, raw log hash, and remediation hints under ~/AI-Pendant-Workspace when a check fails → pendant alert inbox can surface the failure on the next connected session
- **model tier:** Use no expensive model for healthy runs: deterministic threshold evaluation first. Use the background model only to turn a failed structured result into a concise bug report; realtime is only for the owner's spoken question.
- **latency:** Start-to-verdict under 60 seconds, including the deliberate diagnostic fixture. Report writing is asynchronous but must be atomic before claiming failure capture.
- **cost:** Near-zero model cost for pass/fail; roughly $0.001–$0.02 for a failed-run explanation. USB serial and fixture execution dominate latency.
- **security:** The bench command must be allowlisted and restricted to the two known USB serial devices; never read microphone content or arbitrary files. Raw logs may contain identifiers, so retain hashes plus redacted excerpts by default. Firmware flashing and destructive commands are out of scope and require a separate explicit operation.
- **missing:** A bounded, receipt-bearing USB diagnostic runner that can open both known serial ports and return exit status plus captured counters; A parser/threshold evaluator for the fixture's structured output, including alias rejection and packet-loss criteria; A report template that links the diagnostic receipt, firmware revision, and exact reproduction steps

### "Before I send this message, check the draft against the recipient and the linked files, point out accidental secrets or wrong attachments, and let me approve the final send with one press of the pendant."
- **useful because:** Today the Mac can type or send and the browser can hold the session, but no single operation verifies the whole outgoing package. This would prevent the most expensive everyday mistakes: replying to the wrong person, attaching an internal file, leaking a secret copied from a terminal, or following a stale link. The pendant provides an unmistakable physical approval channel while the Mac performs the actual send.
- **path:** Mac planner reads the active draft from Mail, Messages, the browser composer, or the editor without transmitting it → browser bridge resolves recipient identity, attachment names, destination domain, and link targets from the authenticated page → relay background model performs a redacted risk and consistency review, returning structured findings rather than making a decision → pendant alert inbox presents a short warning; the owner presses the existing button to approve or rejects by voice → Mac planner re-reads the draft hash immediately before send, then executes the exact send action and records a receipt
- **model tier:** Background model for the review; realtime only for explaining a warning by voice. The send itself is deterministic and must not be delegated to a model.
- **latency:** Review under 3 seconds for a normal draft; approval-to-send under 1 second. Any changed draft or recipient invalidates the review and requires a new one.
- **cost:** Approximately $0.005–$0.03 per review, dominated by the redacted draft and attachment metadata. No recurring cost when the owner does not send.
- **security:** Draft bodies and attachment metadata leave the Mac only after local redaction, with secrets and unrelated message content removed. Never auto-send. Approval must bind to a hash of recipient, body, attachments, and destination; stale approvals, changed drafts, and duplicate button events must fail closed. The existing owner rule to confirm destructive actions remains mandatory.
- **missing:** A typed, read-only composer inspection API spanning Mail, Messages, editor, and authenticated browser pages; A local secret/PII detector and attachment/link manifest generator; A relay review endpoint that accepts only the redacted manifest and returns stable finding IDs; A pendant approval event bound cryptographically to the exact outgoing-package hash; A send executor that verifies the hash immediately before dispatch and emits a durable receipt


## What it asked for

_Nothing._
## Its own summary

Discovered the live inventory and current grants: Safari is online with one tab, the Mac bridge is online, while the nRF9160 pendant is offline from the relay but physically USB-testable. I proposed three distinct owner-facing capabilities: bookmark-to-work-context recovery, crash/reboot session restoration, and a bounded USB pendant health check that files a reproducible report. The first and third were flagged as close to prior ideas, so implementation should explicitly differentiate them: bookmark recovery must capture task context rather than just a timestamp, and health check must cover both chips plus deterministic acceptance thresholds.

**Biggest unknown:** The remaining blockers are concrete interfaces, not model capability: a redacted semantic Mac context reader, a browser tab-descriptor export suitable for restore, and a bounded receipt-bearing USB diagnostic runner for the two live serial ports. I still need those capabilities (or their exact route contracts) before I can execute these end to end; I do not need Accessibility permission for the metadata-first versions.

