# Harness derivation — mac-terminal — round 70

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read this private log or folder and tell me what matters, but do not send the raw contents off my Mac.”"
- **useful because:** Today a terminal agent can read local material, but the owner cannot reliably ask for a useful cross-device answer while guaranteeing that raw secrets, source code, credentials, or personal documents stay local. This would make the Mac a privacy boundary: the owner gets a concise answer and evidence without exporting the underlying data to the relay or model.
- **path:** mac-planner → mac-terminal → faculty-perception → relay-realtime → pendant
- **model tier:** Use a small local deterministic redaction/classification pass first; use a local Mac model for summarization when available, and only send a typed, lossy finding or approved snippets to the slower background model/relay. Realtime is only needed to speak the final short answer through the pendant.
- **latency:** 2–10 seconds for ordinary logs, with immediate progress on the pendant; large folders may run as a background job and notify when the local digest is ready.
- **cost:** Near-zero relay/model cost when local summarization succeeds; otherwise a small request containing only the redacted digest. Dominant cost is local CPU and optional local-model memory, not tokens.
- **security:** The local pass must detect and suppress credentials, tokens, private keys, health/financial identifiers, and configured path classes before any network call. Keep raw input and intermediate parses on disk only under short retention, show the owner exactly what categories and snippets would leave the Mac, and make network export opt-in per request. A failed classifier must fail closed for export, while still allowing a fully local answer.
- **missing:** A local privacy-boundary pipeline that can parse files/logs and produce typed findings without sending raw content; A local summarizer or constrained on-device model on the Mac; Redaction scanners for secrets and owner-configured sensitive paths; A typed relay payload that accepts only findings/citations rather than arbitrary terminal output; A pendant response that states “kept local” and identifies the local evidence used


## Changes it proposed to its own stack

### `mac-harness` — Add a first-class persistent terminal-session backend for long-running shell work. A run_shell action may opt into a named session with a process-group ID and bounded ring buffer; expose authenticated attach/read (offset or last N lines), stdin write, SIGINT/TERM, and explicit close endpoints, with heartbeats and orphan cleanup after lease expiry. Keep ordinary one-shot commands unchanged. Link session events to the existing job/action receipt and relay job status so a pendant query can say whether the process is still running, show recent output, or offer stop/resume rather than launching a duplicate command.
- **owner gets:** Builds, exports, downloads, tests, and other work that outlasts a voice turn keep running when the owner walks away or the network drops. The owner can ask from the pendant what is happening, see the last useful lines, stop a stuck process, and reconnect later without losing the Mac's terminal context or accidentally starting the work twice.
- effort: Medium-high: local process supervisor/PTY or pipes, authenticated streaming endpoints, lease/orphan handling, bounded persistence, and relay_job_status integration. Add tests for reconnect, cancellation, crash recovery, and duplicate-session prevention.  ·  risk: A detached process can continue consuming CPU, hold files, or expose output; enforce resource/time limits, redact persisted output, kill the process group on lease expiry by default, and make persistence opt-in per session. PTY behavior differs from noninteractive commands, so retain the current executor as fallback. Never replay stdin automatically after reconnect.
- cost: Small local CPU/RAM overhead while active and bounded disk for the ring buffer; no extra model calls. It can reduce API/model cost by avoiding repeated polling and re-running failed long jobs.  ·  latency: Immediate status reads over the existing Mac-agent connection; streaming can be SSE/WebSocket. Session startup adds only PTY/process setup time, while one-shot commands are unchanged.
- security: Adds a privileged control surface for stdin/signals. Require the existing bearer auth, per-session unguessable IDs, owner/job binding, strict output retention, and audit every attach/write/signal/close event. Do not expose raw terminal sessions to unauthenticated relay clients.
- depends on: existing POST /execute and GET /jobs/:jobId lifecycle; existing action receipts and undo records from chg-5fc73ce3; authenticated Mac-agent route middleware; relay_job_status integration

### `context` — Create a Mac-local privacy boundary between terminal execution and model/relay context. Every file/log read is first converted into a typed local finding (category, severity, line/span hash, local citation, confidence, and redaction reason); raw bytes never enter the normal job result or fleet context. Add an explicit export manifest containing only the finding fields/snippets approved by a local policy, and make /plan, /execute, job receipts, and relay status consume that manifest rather than arbitrary stdout. Keep a local-only answer path for requests whose manifest is empty.
- **owner gets:** The owner can ask for analysis of genuinely private Mac material and receive a useful answer without trusting that raw terminal output will be forwarded. They get citations back to local files and a clear statement of what stayed on the Mac, instead of having to choose between no help and data export.
- effort: High: local parser/redactor and secret detectors, typed result schemas, context-routing changes, local citation storage, export preview, and tests against source code, credentials, and personal documents. Requires a local summarizer or a deterministic extractive fallback.  ·  risk: False negatives could leak sensitive data; default to no export when classification is uncertain and let the owner explicitly inspect/override the manifest. False positives reduce usefulness but preserve privacy. Local citations must not expose contents in logs or receipts. Add deletion/retention controls for raw local intermediates.
- cost: Adds local CPU, disk, and possibly a one-time local-model download; normally reduces remote token and relay costs because only compact findings travel. No additional remote call for a local-only answer.  ·  latency: Adds roughly 0.5–3 seconds for scanning typical logs and potentially longer for folders; remote summarization starts only after the manifest is produced. Existing non-private actions can bypass this path.
- security: Strongly reduces exfiltration risk by making raw stdout ineligible for context propagation, but introduces a sensitive local index. Encrypt or permission-lock the index, bind manifests to job IDs, and audit every export decision without storing the blocked content.
- depends on: new typed local-finding schema; secret/path classification engine; local summarization or extractive fallback; changes to /execute result projection and job receipt serialization; relay and faculty context accepting manifests instead of raw command output


## What it asked for

_Nothing._
## Its own summary

Discovered the current Mac surface and granted diagnostics/tools. The existing receipt work already covers execution capsules, so I did not duplicate it. I recorded a new mac-harness change: persistent, reconnectable terminal sessions for long-running commands, with bounded output, process-group control, heartbeat/lease cleanup, authenticated attach/read/stdin/signal/close, and relay-linked status. This preserves FULL_CONTROL_MODE while letting the owner monitor or stop work from the pendant without duplicate launches.

**Biggest unknown:** The exact local-agent job lifecycle and route contract for streaming/controlling a live process is still unavailable; the previously requested mac_shell_job_control and observability permissions/tools have not arrived. No additional permission request is needed this round.

