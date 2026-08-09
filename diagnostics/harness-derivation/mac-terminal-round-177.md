# Harness derivation — mac-terminal — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-mac-browser-availability** — The Mac agent, relay, and Safari extension are online simultaneously; Safari has 9 tabs with active X tab and authenticated Gmail tab, and Accessibility, Screen Recording, and automation permissions are all granted.
  - evidence: GET /ops/status and GET /browser/status returned online=true, browser tabCount=9, relay.macBridgeOnline=true, permissions.ready=true.

## Capabilities it proposed

### "When I say “take care of this” into the pendant, have the system finish the task across my Mac and logged-in browser, then tell me exactly what changed and leave me a one-command way to undo or resume it if anything failed."
- **useful because:** Today the voice, browser, and Mac surfaces can each act, but the owner has to manually bridge them and cannot tell whether a partial result is safe. This makes the whole hive behave like one accountable assistant: inspect the active tab and project, execute the smallest complete workflow, produce evidence, and preserve a resumable recovery point.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use deterministic routing for status, tab listing, and receipts; use the background/planner tier for decomposition and verification; reserve realtime only for the short spoken acknowledgment and final result.
- **latency:** Acknowledge in under 1 second; gather context in 2 seconds; ordinary workflows under 20 seconds, with a spoken progress update at 5 seconds. Long jobs continue asynchronously and are queryable from the pendant.
- **cost:** Usually one planner call plus deterministic Mac/browser actions; roughly $0.01–$0.05 depending on verification context. The dominant cost is sending page/project context, so send only selected DOM/text and receipt summaries.
- **security:** Authenticated page text and local file paths may leave the Mac for planning; redact tokens, cookies, and unrelated tabs. Mutations remain allowed under the owner's maximum-access policy, but the spoken result must distinguish completed, partially completed, and merely proposed. Undo/resume must be explicit and idempotent.
- **missing:** A cross-surface transaction envelope joining one pendant turn, browser command IDs, Mac job IDs, and action-ledger receipts; A verifier that compares intended effects with observed post-state before claiming completion; A durable resume/undo bundle exposed as a single owner-facing job

### "If a terminal task fails, let me ask the pendant “why did that fail?” and get a useful diagnosis plus a safe, ready-to-run recovery—not just “exit 1.” Include the exact command, project directory, duration, exit code, relevant stderr, and what the agent would try next."
- **useful because:** The current Mac shell flattens failures, discards the exit code, has no argv or environment fingerprint, and cancellation cannot stop a running child. The owner currently has to reproduce failures manually. A forensic answer would turn a dead-end command into a recoverable action while preserving the owner's deliberate full-control policy.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Deterministic collection and classification first; a cheap background model summarizes stderr and proposes recovery; realtime only speaks the concise diagnosis. Escalate to planner only when multiple recovery branches or project context are needed.
- **latency:** Return the first diagnosis within 3 seconds of asking; recovery proposal within 8 seconds. Never rerun automatically merely because diagnosis is available; keep a long-running repair asynchronous.
- **cost:** Near-zero for receipt lookup and known exit-code classes; about $0.002–$0.01 for summarizing a bounded stderr excerpt. Cost is dominated by sending logs, so cap and redact output.
- **security:** Commands and stderr can contain secrets, paths, and credentials. Store a redacted forensic capsule, never the inherited environment; preserve a local hash and allow the owner to request raw output. Recovery commands inherit maximum access and must be clearly labeled as a new mutation, not an automatic retry.
- **missing:** Shell execution receipts with exit code, signal, pid, argv/cwd, timeout-vs-process-exit distinction, and redacted environment fingerprint; A failure taxonomy (nonzero exit, timeout, signal, output overflow, cancellation) and recovery planner that knows which failures are retryable; A pendant query that binds to the last failed Mac job and streams its diagnosis

### "Take the document I’m looking at in Safari, extract the useful fields, and file it on my Mac where it belongs—without uploading it anywhere else. Tell me which tab and file you used, what you extracted, and show me the destination before/after when I ask from the pendant."
- **useful because:** This is a genuinely cross-node job: only the browser has the authenticated document, only the Mac can manipulate the local filesystem, and only the pendant gives the owner a hands-free request and trustworthy completion signal. It eliminates download-find-open-copy-rename bookkeeping while keeping sensitive documents local after capture.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Use deterministic browser inspection/download and local file operations; use a background model for field extraction and destination classification; use realtime only for the spoken confirmation. Use vision only when the page is rendered and text extraction is insufficient.
- **latency:** Acknowledge in under 1 second, identify the active document within 3 seconds, and finish ordinary PDFs/images within 15 seconds. If a login challenge or ambiguous destination occurs, pause with a precise question rather than guessing.
- **cost:** About $0.005–$0.03 per document, mostly extraction/verification tokens; local file transfer and hashing are free. Keep the document bytes on the Mac and send only schema-limited extracted fields to the planner.
- **security:** The browser session may expose financial, medical, or work documents. Require origin/tab provenance, same-device transfer, MIME/size limits, malware scan, secret/PII redaction in model context, and an audit record of source hash, destination, and transformation. Never claim success until destination hash and readable file state verify.
- **missing:** A browser command that transfers a download or selected document bytes to the Mac agent without routing content through the relay/model; A local extraction and file-placement action with SHA-256 provenance, collision handling, and atomic write; A cross-surface privacy contract that restricts planner context to extracted fields while retaining full bytes locally

### "Let me give the pendant a bounded delegation such as “until Friday, watch my authenticated work tabs, keep a private queue of items that need me, and stop immediately when I say revoke that delegation.” Show me what it is allowed to do, let me revoke it from anywhere, and give me a daily spoken exception report rather than narrating every routine action."
- **useful because:** The owner cannot currently leave a multi-day, browser-authenticated objective running with an explicit scope, expiry, live revocation, and accountable exception queue. Existing routines can schedule work, but they do not create a revocable delegation spanning browser sessions, Mac execution, relay wakefulness, and a wearable control surface.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use a cheap background model for scheduled polling and exception ranking; deterministic rules enforce scope, expiry, and revocation; use realtime only for the owner's revoke command and the short daily report. Escalate to the planner only for ambiguous items.
- **latency:** Revoke acknowledgement under 2 seconds when the relay is reachable and under 1 minute after a reconnect. Daily report under 30 seconds. Polling must be asynchronous and never hold a voice session open.
- **cost:** Low recurring cost: deterministic page checks dominate, with one small background summarization call per report. A typical workday should cost roughly $0.01–$0.05 depending on page volume; transmit only changed snippets and hashes.
- **security:** This operates inside authenticated browser sessions and may see confidential work. The delegation needs an explicit allowlist of origins, actions, data fields, and destination folders; a hard expiry; a revocation record replicated to relay, Mac, and pendant; and a guarantee that no outbound message or irreversible mutation is sent without a separately granted capability. All observations should remain local unless the owner opts into relay summarization.
- **missing:** A first-class delegation object with scope, origin/action allowlists, expiry, purpose, and revocation epoch; A relay-backed revocation fanout that reaches browser and Mac workers even while a poll is active; An exception queue that correlates browser observations, Mac jobs, and pendant reports without treating routine polling as a voice conversation

### "Before I let you change anything across my Mac and logged-in browser, let me ask “what happens if you do that?” and hear a concrete impact preview: files, tabs, messages, and irreversible side effects, with a replayable simulation that uses the same inputs but performs no writes."
- **useful because:** Today the owner must trust a planner’s prose or inspect scattered previews. A cross-surface dry run would make powerful automation understandable before it acts, especially when one request spans an authenticated tab and local files. It is not an approval gate: the owner can still choose maximum-access execution, but gets a factual diff and explicit side-effect inventory first.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Run deterministic read-only inspection and filesystem/browser snapshotting first; use a background planner to explain the resulting diff; realtime speaks only the compact impact summary. Do not invoke the expensive tier unless the simulation is ambiguous.
- **latency:** For ordinary workflows, preview within 5 seconds and execution can begin immediately afterward if requested. Large projects or pages may continue asynchronously, with the pendant stating exactly which inputs remain uninspected.
- **cost:** Usually no model call for the raw diff and one small explanation call, around $0.002–$0.02. Store hashes and structural summaries rather than duplicating file or page contents.
- **security:** Simulation must not trigger downloads, network writes, form submissions, clipboard changes, or shell side effects. Authenticated content stays on-device by default. The preview must disclose uncertainty, stale snapshots, hidden scripts, and any action that cannot be faithfully simulated.
- **missing:** A universal dry-run contract for Mac, browser, shell, and computer-use actions that returns predicted effects and confidence; Snapshot isolation and diffing for browser state plus local files, including a freshness/version check immediately before execution; A receipt that binds the preview input hashes to the later real execution so the owner knows whether the world changed between them

### "When I say “private mode” into the pendant, keep doing the task but stop speaking names, message contents, and sensitive page text aloud; give me only neutral progress tones and coded summaries until I say “normal mode.” Apply it consistently to the pendant, Mac notifications, browser overlays, and dashboard."
- **useful because:** The owner cannot safely use the system in a meeting, on transit, or around another person because privacy is currently a per-surface guess. A single wearable command should change disclosure policy everywhere while preserving task execution and truthful completion/failure signals.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic policy propagation and redaction; no model call for mode changes. Background summarization may continue only over already-authorized local data, producing a redacted exception digest. Realtime is limited to neutral confirmations.
- **latency:** Mode change acknowledgement under 500 ms locally and under 2 seconds across the relay. Every surface must converge within 3 seconds; stale surfaces must fail closed to neutral output.
- **cost:** Negligible model cost; local redaction and policy fanout dominate. A small persistent state record is cheaper than repeatedly sending privacy instructions in prompts.
- **security:** Privacy mode must be enforced below model prompting so a model cannot accidentally reveal sensitive text. Redact TTS, logs, overlays, browser command results, and dashboard previews; preserve encrypted local records for later owner review. The pendant needs an offline cached mode and age indicator so it never claims remote enforcement when disconnected.
- **missing:** A signed privacy-policy epoch propagated from pendant through relay to Mac, browser, and dashboard; Central redaction middleware covering TTS, logs, overlays, browser results, and spoken job receipts; An offline-safe pendant state machine that distinguishes locally active privacy mode from remotely acknowledged mode


## Changes it proposed to its own stack

### `mac-harness` — Instrument run_shell at the child-process boundary with spawn/execFile-style metadata while preserving the raw command capability: capture pid, normalized cwd, start/finish monotonic times, timeout and signal cause, numeric exit code, bounded stdout/stderr digests, and a redacted environment fingerprint. Persist the raw submitted action and any pre-dispatch rewrite beside the executed action, link the receipt to its job and ledger IDs, pass AbortSignal to the child, and reconcile processing jobs on boot as interrupted rather than leaving them permanently running.
- **owner gets:** When the owner asks what happened, the system can answer truthfully, stop a hung command, and resume or diagnose work after the Mac agent restarts. It makes maximum access more useful rather than restricting it: every command remains possible, but failures and partial completion stop being mysteries.
- effort: Medium-high: replace exec with a signal-aware child process wrapper, extend receipt/job schemas and redaction, close ledgers on all orchestrator paths, add boot reconciliation, and test timeout/cancel/restart/rewritten-action cases.  ·  risk: Changing process execution can alter shell quoting, signal behavior, and output timing. Roll back behind a feature flag to the existing exec path; keep the original command string and result so a failed migration is diagnosable.
- cost: Negligible storage and CPU for metadata/hashes; no additional model call. Bounded output retention may reduce disk pressure compared with current unbounded result strings.  ·  latency: Under 10 ms instrumentation overhead; cancellation becomes effective during a command instead of waiting up to 120 seconds.
- security: Improves auditability without adding gates. Redact environment values and sensitive output, retain only names/fingerprints by default, and ensure AGENT_TOKEN/LLM keys never enter receipts.
- depends on: A schema migration for action receipts and job records; A tested child-process wrapper that preserves /bin/sh command semantics; Ledger close and job-to-ledger correlation in orchestrator.js


## What it asked for

### `t23-233q` (tool) — browser_export_local_artifact
- why: The browser extension is the only node that can access an authenticated document, while the Mac agent is the only node that can safely place and process the bytes locally. Existing browser actions expose tabs/pages and command results but do not provide a same-device, provenance-preserving artifact transfer.

```json
{
  "type": "object",
  "properties": {
    "tab_id": {
      "type": "integer",
      "minimum": 1
    },
    "locator": {
      "type": "string",
      "maxLength": 512
    },
    "destination": {
      "type": "string",
      "maxLength": 1024
    },
    "max_bytes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 52428800
    },
    "expected_mime_types": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "maxItems": 10
    },
    "sha256": {
      "type": "string",
      "pattern": "^[a-fA-F0-9]{64}$"
    }
  },
  "required": [
    "tab_id",
    "destination",
    "max_bytes"
  ]
}
```

