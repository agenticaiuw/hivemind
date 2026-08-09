# Harness derivation — mac-terminal — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is my pendant bench-ready right now?” Press the pendant button or ask the Mac; run a bounded dual-chip USB self-test and tell me which link, firmware heartbeat, audio counters, and capture path are healthy, with the exact failing port and a one-command recovery if not."
- **useful because:** The hardware is physically present today but neither the relay nor the existing inventory can inspect serial ports. This turns an opaque bench setup into a truthful answer the owner can get before relying on the wearable, and it exercises the real nRF9160 and ESP32 together rather than testing each in isolation.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Use deterministic Mac shell scripts/parsers for port discovery, UART framing, timestamps, and thresholds; use the cheap background model only to summarize the structured report. Realtime is needed only to speak the result through the pendant.
- **latency:** Start detection within 1 s; collect 2–5 s of bounded frames; speak a result within 8 s. A failed or absent port must be reported as unknown/failed, never inferred from Mac bridge online state.
- **cost:** Near-zero model cost for a healthy run; roughly $0.001–$0.01 only when a model must explain an unusual structured failure. Dominant cost is 2–5 s of serial capture and local parsing.
- **security:** USB reads are local and read-only. Do not upload raw UART logs by default; send only a redacted structured report and hashes. Firmware versions and counters can identify the device, so require explicit opt-in before relay persistence. Recovery commands such as reset or flash must remain separate, explicit actions.
- **missing:** A real bounded serial diagnostic executor; the granted mac_usb_serial_diagnostics schema is unresolved because no serial capability exists.; A small host parser for the dual_chip_autocapture output and a stable health-frame format from both firmwares.; A relay event/audio handoff that can speak a Mac-originated result while the pendant is USB-attached but LTE-unregistered.

### "“What did you do on my Mac after I asked you to fix that?” Give me a causal, spoken timeline that joins the pendant turn, relay request, Mac job, shell/browser actions, outputs, and final state; distinguish completed, failed, cancelled, and merely planned work."
- **useful because:** Today a job ID, action receipt, browser command, and pendant turn are separate islands. The owner can be told “done” without being able to reconstruct what actually happened, especially after a restart. A causal answer is more useful than another raw log endpoint and makes unattended maximum-control execution intelligible.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Build the timeline deterministically from IDs, timestamps, receipts, browser provenance, and pipeline events; use a cheap background model to compress it into speech. Realtime only verbalizes the already-verified timeline.
- **latency:** Return a first status in 1 s from durable records; assemble the full timeline in under 4 s. If a join is missing, explicitly say “unlinked” rather than guessing.
- **cost:** Usually <$0.005 per request; most work is local JSON/index reads. Model cost is only the final compression, not log interpretation.
- **security:** Never speak command arguments or stdout that contain tokens, cookies, or private page contents; apply field-level redaction before model input and preserve raw evidence locally. The owner’s authenticated browser provenance must not be exported to the relay by default.
- **missing:** A durable correlation ID propagated from the pendant turn through relay, /execute, browser commands, and receipts; current planMeta.jobId is null and ledgers remain unjoined.; A read-only timeline endpoint that merges GET /jobs/:jobId, GET /jobs/:jobId/receipts, GET /journal/:jobId, GET /logs, GET /browser/provenance, and pipeline events.; A crash-safe event index and explicit planned-vs-executed state so POST /plan and POST /prepare cannot be mistaken for execution.

### "“The Mac restarted—continue anything that was safely in progress, and tell me what you deliberately did not resume.” Have the pendant report the recovery result without making me remember job IDs."
- **useful because:** A reboot currently leaves durable jobs stuck at processing, orphaned commands unreconciled, and every historical open ledger looking interrupted. The owner loses work or risks manually repeating side effects. A recovery pass that uses the existing ledger and idempotency data would make the always-available hive survive the most ordinary failure.
- **path:** mac-planner → relay-realtime → pendant → faculty-action
- **model tier:** Use deterministic reconciliation and idempotency checks; use a cheaper model only to rank human-readable explanations. Realtime speaks the compact recovery report; no expensive model is needed to decide whether an action was completed.
- **latency:** On agent boot, reconcile in under 3 s; resume only after the ledger is classified. Report recovered/skipped/unknown within 5 s of the pendant reconnecting. Long-running work continues in background with truthful_action_status_beacon state.
- **cost:** Negligible API cost for local reconciliation; <$0.002 for optional spoken summarization. The engineering cost is durable process metadata and safe subprocess handling, not inference.
- **security:** Never replay an action whose completion is unknown when it can cause an external side effect; classify shell/browser actions by replay safety and preserve the owner’s maximum-control policy without silently duplicating mutations. Keep raw command output local and redact secrets from the pendant.
- **missing:** Boot-time reconciliation that marks stale processing jobs and closes or classifies ledgers instead of leaving them permanently open.; Wire executionContext’s existing fresh/retry/completed/rerun engine into real /execute actions, with a persisted job↔ledger correlation ID.; A resumable action protocol that records PID/exit code/signal and uses execFile/AbortSignal or an equivalent process supervisor for shell steps.; A relay/pendant recovery summary event that works when the pendant was offline and replays exactly once on reconnect.

### "“Package the failure I just experienced for the developer.” Create a local, reproducible incident bundle containing the pendant turn ID, Mac/browser timeline, relevant shell and UART excerpts, machine state, exact reproduction steps, and a redacted Markdown report; give me a short spoken summary and a local path, without uploading anything unless I ask."
- **useful because:** Today the owner can inspect scattered jobs, logs, browser provenance, and bench captures, but cannot turn one lived failure into a portable bug report. This would make the hive improve itself from real incidents while keeping private data on the Mac by default.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** Deterministic collectors select evidence by correlation ID and time window; a cheap background model drafts the report after secret redaction. Realtime only reads the concise result.
- **latency:** Collect and redact in under 10 seconds for a normal incident; never block on a missing source. Say exactly which evidence was unavailable.
- **cost:** Usually <$0.01, dominated by optional report drafting; collection and bundle creation are local.
- **security:** The bundle may contain authenticated URLs, command arguments, page text, and device identifiers. Default to local-only storage, redact tokens/cookies and unrelated tabs, show an evidence manifest before any upload, and require explicit confirmation for export.
- **missing:** A correlation-aware evidence collector spanning pendant turns, Mac jobs, browser provenance, pipeline events, and UART capture files.; A deterministic secret/PII redactor with an evidence manifest and content hashes.; A local incident-bundle writer and a spoken handoff event that works when the pendant is USB-attached but not LTE-registered.

### "“Before you send anything off this Mac, tell me exactly what will leave it and what will stay local.” Produce a data-egress manifest for the current request, including relay/audio payloads, browser-derived fields, file names, retention, and the redactions applied; let me say “local only” and still complete the task where possible."
- **useful because:** The system can act across an authenticated browser, unrestricted Mac shell, relay, and wearable, but the owner has no single answer to what crosses those boundaries. Existing job receipts describe actions, not the data flows they create. This makes the hive trustworthy without weakening its maximum-capability execution policy.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** Use a deterministic taint/data-flow manifest for known action inputs and outputs; use a small model only to explain it in plain language. Realtime speaks the summary.
- **latency:** Manifest in under 1 second for known payloads; unknown or dynamically generated content must be labeled unknown before dispatch.
- **cost:** Near-zero inference cost; local manifest generation is the dominant work.
- **security:** The manifest itself must not include secrets it is describing. Hash or classify sensitive values, never echo them. “Local only” must be an enforceable routing mode, not merely a spoken preference, and any inability to honor it must be reported before transmission.
- **missing:** A taint-tracking envelope attached to pipeline, browser, shell, and relay payloads.; A route-aware egress planner that distinguishes local disk, Mac bridge, relay, model provider, and pendant audio destinations.; A local-only execution mode for tasks whose computation can remain on the Mac, plus a compact pendant-readable manifest format.

### "“Privacy stop.” Immediately stop outgoing audio and browser automation, cancel queued-but-not-started Mac work, close or hide sensitive browser tabs, and tell me what could not be stopped because it was already running."
- **useful because:** There is no single emergency boundary across the pendant transport, relay conversation, Mac jobs, and authenticated browser. The owner currently has to remember separate controls and cannot know whether a remote action is still active. This is a human-scale safety capability for a system that can act unattended, not a restriction on ordinary maximum-control use.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action
- **model tier:** Deterministic emergency controller with no model in the stop path; a cheap model may summarize residual activity afterward. Realtime speaks only after each surface returns an acknowledged state.
- **latency:** Local audio mute and pendant indication within 200 ms; dispatch stop commands within 1 s; residual-state report within 3 s. Never claim stopped without an acknowledgement or explicit unknown state.
- **cost:** Negligible API cost; the main work is bounded control messages and durable state updates.
- **security:** The stop command must be authenticated, replay-resistant, and fail closed for outgoing audio. Do not delete browser data or kill arbitrary processes silently; close/hide only declared sessions and preserve an auditable residual list. If the Mac is offline, cache the stop intent on the pendant and apply it on reconnect.
- **missing:** A single authenticated emergency intent propagated from pendant/relay to Mac and browser extension.; Abortable process and browser-command control with explicit acknowledged, already-running, and unknown states.; A transport-level audio mute that does not depend on the model or relay completing a turn.; A durable exactly-once emergency record and pendant indication that survives a dropped link.


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) a truthful “Is my pendant bench-ready?” dual-chip USB self-test, (2) a spoken causal timeline joining pendant turn → relay → Mac/browser execution → outcome, and (3) reboot recovery that resumes only safely classifiable work and reports skipped/unknown tasks through the pendant. The first two were noted as close to existing backlog themes, so they should be treated as connective implementations, not claimed as wholly novel infrastructure. I also attempted the granted serial diagnostic tool; it is still unresolved because no serial capability exists in the live inventory. A proposed shell-supervisor change was rejected as an existing proposal.

**Biggest unknown:** There is still no callable, bounded serial-port reader or host UART parser. The only practical route today is unrestricted POST /execute run_shell invoking the existing dual-chip capture scripts, but its receipts cannot reliably expose exit code, PID, or raw port-open failures.

