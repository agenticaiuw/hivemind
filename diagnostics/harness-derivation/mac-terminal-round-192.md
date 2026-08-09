# Harness derivation — mac-terminal — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What did you actually change on my Mac for that request?” Give me a concise, trustworthy before/after answer, including files, apps, browser tabs, and anything that failed."
- **useful because:** Today a shell job's stdout and a generic receipt do not tell the owner what the combined Mac/browser workflow changed. This gives a spoken, human-impact diff instead of forcing them to inspect logs, and catches silent rewrites or partial completion.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for snapshot diffing; realtime only to speak the final 2–3 sentence answer
- **latency:** Capture baseline in under 1 s, execute normally, capture final within 2 s; spoken answer under 5 s after completion
- **cost:** Usually <$0.01 per invocation; most cost is storage and a small summarization call, not realtime inference
- **security:** Snapshots may contain filenames, URLs, window titles, and sensitive browser metadata. Keep raw snapshots on the Mac, redact secrets, send only a minimal diff to relay, and require explicit opt-in for page text or file contents.
- **missing:** pre/post Mac snapshot route for process/window/filesystem metadata; browser tab/session snapshot with stable hashes; a durable correlation ID attached to every execute ledger and browser command; diff summarizer that distinguishes intended from incidental changes

### "“Run this long Mac task, but pause safely if the laptop sleeps, loses Wi‑Fi, or drops below 20% battery; resume when it is safe and tell me if anything was skipped.”"
- **useful because:** Long shell and browser work currently has one timeout, no process-group cancellation, and no awareness of power or connectivity. The owner gets unattended work that survives ordinary laptop conditions instead of a false success or a half-written result.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background event-driven supervisor; realtime only for a short spoken warning or completion
- **latency:** Condition checks every 5–15 s; pause decision under 1 s; resume after wake/network recovery without a new conversation
- **cost:** <$0.005 per task beyond existing Mac polling; no model call needed for state transitions, optional cheap summarization at the end
- **security:** The supervisor observes battery, network, sleep, process, and browser state. Keep telemetry local, send only state transitions and final outcome, and never resume a mutation whose checkpoint cannot prove idempotence.
- **missing:** Mac power/network/sleep event stream; process-group pause/resume or checkpoint adapters for shell actions; browser command checkpoints and exactly-once resume tokens; job state machine with explicit paused/skipped/ resumed receipts

### "“Stop whatever the Mac is doing for me right now.” I want one press on the pendant to halt the active shell/browser workflow, leave the Mac usable, and hear exactly what was stopped."
- **useful because:** A spoken cancellation is impossible when the workflow is the thing blocking attention, and the current cancel signal does not kill a running shell. A physical, cross-surface stop is the safest way to regain control during a runaway command or browser loop.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No model for the stop path; deterministic relay dispatch and Mac process-group termination. Cheap background model may summarize the stopped step afterward.
- **latency:** Button edge to termination request under 300 ms; process-tree termination and truthful LED/audio state under 2 s
- **cost:** Negligible API cost; one durable event and a small receipt per stop
- **security:** A global stop can interrupt an unrelated user process if scope is ambiguous. Bind it only to jobs launched by this agent, use process groups and a durable job nonce, preserve cleanup metadata, and never claim completion—only stopped/unknown.
- **missing:** firmware mapping for a dedicated stop edge or a safe second-button action; relay stop-intent endpoint with replay protection; Mac process-group IDs and a killable execution handle in each receipt; browser harness cancellation that propagates to in-flight commands; pendant spoken acknowledgment path when audio is unavailable

### "“Fill out this form from my notes, then read every field back to me on the pendant in plain language. Let me correct individual fields by voice, and only submit the exact version I approved.”"
- **useful because:** The owner cannot safely delegate authenticated, high-consequence browser forms today: the browser can act and the Mac can type, but there is no wearable-native field-level review and correction loop that preserves the exact proposed payload. This would make the system useful for applications, reimbursements, travel, and account changes without forcing the owner back to a screen.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model extracts and normalizes source notes; realtime model handles the short spoken review and corrections; deterministic browser executor applies only the approved field patch.
- **latency:** Initial extraction under 10 seconds; each field correction acknowledged within 2 seconds; no submission until the owner says an explicit final phrase.
- **cost:** Approximately $0.02–$0.10 per form depending on field count and source-document OCR; browser and relay work dominate, not Mac shell execution.
- **security:** Authenticated page values and personal data must stay on the Mac/browser where possible. Send the relay only the minimum masked field labels and values needed for speech, never passwords or full payment identifiers. Persist an encrypted, expiring approval hash and an immutable submitted-payload receipt; require re-review if the page changes.
- **missing:** Browser DOM/form extraction that returns stable field identifiers, labels, current values, validation errors, and sensitive-field classifications; A relay protocol for chunked field review with replay-safe voice corrections; A deterministic field-patch executor that refuses to submit any value not covered by the latest approval hash; Pendant speech playback with interruption and correction targeting; A final receipt containing the exact submitted fields and page state hash

### "“After you submit something important in the browser, independently verify that it really took effect—not just that the button clicked—and tell me if the site, network, or returned record disagrees.”"
- **useful because:** A browser command can report success while a site rejects validation, loses a session, or never commits the change. The owner needs a second, evidence-based answer for consequential actions, especially when the Mac and browser are unattended.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic verification first (URL/state/record reread and network result); cheap background model reconciles conflicting evidence; realtime only speaks the final verdict.
- **latency:** Verification within 5 seconds of submission for ordinary forms; continue asynchronously for delayed systems and notify the pendant when evidence arrives.
- **cost:** <$0.02 per verification; mostly browser round trips, with model cost only when evidence conflicts.
- **security:** Verification can expose private confirmation pages. Keep raw evidence local, hash and redact payloads before relay, and never treat a visual success banner as proof without a stable server-side or record-level signal.
- **missing:** A browser postcondition DSL that can reread a record, detect a durable identifier, or compare a before/after state; Network/HTTP response capture correlated to the browser command; A conflict resolver that reports unknown instead of guessing; Delayed verification watches with expiry and deduplication; A pendant notification that distinguishes confirmed, rejected, and unverifiable

### "“Before you send or upload anything from my Mac, show me exactly what leaves the device, automatically hide secrets and unrelated personal data, and let me say ‘remove the second attachment’ or ‘replace my phone number’ on the pendant.”"
- **useful because:** The owner cannot currently see a reliable, cross-app data boundary for agent actions. A shell command, browser upload, or form submission can move more than intended, and a screen-only preview is unavailable when wearing the pendant. This makes delegation safe without reducing the agent's capability.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model performs local data classification and redaction suggestions; realtime model handles the short spoken review; deterministic executor sends only the approved manifest.
- **latency:** Generate a manifest in under 5 seconds for ordinary text/files; voice edits apply in under 2 seconds; upload waits until the final manifest hash is approved.
- **cost:** $0.01–$0.08 per outbound action depending on document OCR/classification; local hashing and redaction should dominate latency.
- **security:** The preview engine itself must not leak the sensitive data it is protecting. Keep originals local, use masked previews, encrypt the expiring manifest, classify passwords/tokens/payment data conservatively, and mark unknown content as unknown rather than safe.
- **missing:** A universal outbound-data interception point covering browser uploads, form submits, mail, and shell network commands; Local file/content classifier with secret and personal-data labels; Manifest-based executor that binds the actual bytes/fields to an approval hash; Pendant-readable masked preview with field/item targeting; Durable audit receipt of exactly what was transmitted and to which destination


## Changes it proposed to its own stack

### `mac-harness` — Make every run_shell execution use a tracked process group with a durable execution handle: capture pid/pgid, argv-equivalent metadata, start/finish/exit status, timeout cause, and a monotonic event stream; wire POST /jobs/:jobId/cancel to terminate that group, and reconcile processing jobs on boot as stopped-unknown rather than forever-running.
- **owner gets:** The owner can finally stop a hung task, know whether it exited or was killed, and trust that a restart will not leave a phantom 'running' job or cause an accidental duplicate resume.
- effort: Medium: replace exec with spawn/execFile-compatible process-group handling, extend receipts and job reconciliation, then add browser cancellation adapters.  ·  risk: Killing a process group can terminate child cleanup unexpectedly; use a grace period (SIGTERM then SIGKILL), record every signal, and leave the job explicitly unknown when termination cannot be verified. Existing jobs without handles remain cooperative-only.
- cost: No meaningful API cost; small durable metadata increase per action, bounded by existing receipt/job caps.  ·  latency: Negligible on normal commands; cancellation becomes sub-second to a few seconds instead of waiting up to 120 s.
- security: Does not narrow owner-approved FULL_CONTROL_MODE. It improves auditability, but pid/command metadata must redact inherited secrets and never persist the full environment.
- depends on: A process-group-aware shell executor; Durable job↔ledger correlation IDs; Boot-time reconciliation of processing jobs; Browser harness cancellation hook


## What it asked for

_Nothing._
## Its own summary

Completed this round with three owner-facing cross-surface capabilities: (1) spoken before/after impact receipts for Mac plus browser work, (2) power/network/sleep-aware pausing and safe resumption, and (3) a physical pendant emergency stop that terminates only agent-launched work and reports stopped-versus-unknown truthfully. Also proposed tracked process groups, durable execution handles, exit status, cancellation escalation, and boot reconciliation on the Mac. Live discovery confirms the Mac agent and relay are healthy, FULL_CONTROL_MODE and computer-use are enabled, Accessibility/Screen Recording/automation permissions are ready, Safari browser bridge is online with one ChatGPT tab, and there are no pending browser commands.

**Biggest unknown:** I still need the granted USB-serial diagnostics implementation to inspect the physically attached nRF9160 and ESP32 and validate the pendant-to-Mac stop/status path end to end. The newly granted mac_read_diagnostics schema did not resolve in this inventory (nearest GET /health), so host facts beyond the live /ops/status payload remain unavailable through that tool. I also still need the orchestrator's response on the already-queued browser artifact export request; I will not re-ask this round.

