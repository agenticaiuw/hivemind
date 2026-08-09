# Harness derivation — mac-terminal — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **ledger-recovery** — GET /ledger/interrupted is live and currently returns two owner-gone ledgers, including one with a joined jobId and one with jobId null; both remain status open. This confirms recovery needs a user-facing explanation and deduplication, not merely a scanner.
  - evidence: Authenticated GET /ledger/interrupted at 2026-08-08T22:53:21Z returned count 2, both status open, why owner-gone; one progress inflight=1 and one done=1.

## Capabilities it proposed

### ""Run a 30-second bench health check on both chips and tell me exactly which side is unhealthy.""
- **useful because:** The pendant and ESP32 are physically attached today, but there is no owner-facing way to distinguish firmware silence, UART enumeration, audio-bridge failure, or a healthy idle device. This turns the live bench into a testable product instead of guesswork.
- **path:** mac-terminal → relay-realtime → unified
- **model tier:** background
- **latency:** Return a first verdict within 5 seconds, then finish the bounded 30-second capture; no low-latency model is needed.
- **cost:** <$0.02 per run; dominated by one small synthesis call after local logs are collected.
- **security:** Read-only USB/UART probes and local log reads only. Do not upload raw audio or environment variables; send only parsed counters, timestamps, port identity, and bounded error lines. No confirmation needed because it cannot mutate hardware.
- **missing:** A real serial/UART diagnostic tool (the granted schema is still unresolved) or a narrowly scoped run_shell wrapper that can invoke the existing dual_chip_autocapture.sh; A parser for the nRF9160 and ESP32 diagnostic frames; A relay job type that returns a durable health receipt

### ""Keep working on that task after the Mac restarts, and tell me exactly what was completed and what still needs me.""
- **useful because:** Today a reboot leaves jobs permanently marked processing, loses the in-memory worker, and gives no safe continuation path. A durable handoff lets the owner leave a long browser/Mac task unattended without returning to an ambiguous half-finished state.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** background
- **latency:** Checkpoint each side effect in under 1 second; after reboot, resume discovery within 10 seconds and report a truthful partial result immediately.
- **cost:** <$0.05 per task; storage and one cheap summarization call dominate.
- **security:** Persist only action metadata, hashes, and redacted outputs; never persist inherited secrets or page contents by default. Resume shell/browser mutations only from an explicit idempotency key and verified precondition; otherwise stop and ask the owner.
- **missing:** Boot reconciliation that marks orphaned jobs interrupted rather than forever processing; A real process-group cancellation/reattachment strategy for run_shell; Wire executionContext idempotency to POST /execute and close the action ledger on every terminal path; A resume planner that consumes the ledger and browser provenance, then emits a completion/needs-owner report

### ""Move this exact page and where I am in it to my Mac, then continue the task there.""
- **useful because:** Today the browser extension, Mac agent, and pendant can each act, but they cannot hand off a live web task with its exact tab, scroll position, selected text, form draft, and authenticated session. The owner must manually find the page and reconstruct context, which is precisely what a wearable hive should eliminate.
- **path:** relay-realtime → pendant → browser-extension → mac-planner → mac-vision → unified
- **model tier:** planner
- **latency:** Acknowledge the handoff in under 2 seconds and land the Mac-side session within 8 seconds; ask before submitting any form or sending anything.
- **cost:** <$0.03 per handoff; dominated by one planner call if the destination task is ambiguous. Structured tab/session transfer should be deterministic.
- **security:** Transfer only a short-lived encrypted handoff capsule, never raw cookies or passwords. The browser extension keeps the authenticated session local and issues a scoped capability to the Mac agent. Selected text and form drafts may be sensitive, so show the destination and scope in the pendant response and expire the capsule after one use.
- **missing:** A browser-extension export primitive for tab identity, URL, DOM anchor/selection, scroll position, draft fields, and a scoped session handoff token; A Mac import action that attaches to the existing Safari tab or opens the page without leaking session cookies; A relay handoff record with one-time expiry, provenance, and replay protection; A unified continuation planner that verifies the DOM anchor still exists before acting

### ""Prove exactly what you changed and what evidence you used.""
- **useful because:** The system can act through the Mac and authenticated browser, but the owner cannot receive one coherent, human-readable proof tying the spoken request to the exact page state, extracted claims, files changed, and resulting action. This makes autonomous work auditable rather than trust-me automation.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → unified
- **model tier:** background
- **latency:** Return a compact spoken summary within 3 seconds, with a link or local artifact for the detailed evidence packet.
- **cost:** <$0.02 for deterministic assembly; use a cheap summarizer only when the packet exceeds a few events.
- **security:** Redact credentials, cookies, tokens, private page text, and unrelated terminal output. Store a content-addressed local evidence bundle with short retention; transmit claims and hashes rather than raw documents unless the owner explicitly requests them.
- **missing:** A cross-surface evidence schema joining browser provenance records, Mac action receipts, file hashes, and the original request; A redaction and sensitivity classifier that runs before relay upload; A durable evidence-bundle route with expiry and owner-readable rendering; A spoken 'prove it' intent that retrieves and summarizes the bundle without rerunning the action

### ""Reconcile the draft on my Mac with the version in the authenticated web app, show me the meaningful differences, and apply the safer merge.""
- **useful because:** The owner currently has separate local-file and browser agents, but no way to compare two live versions while preserving provenance, handling conflicts, and carrying the chosen result back into the authenticated app. This prevents silent overwrites and saves the manual copy/paste loop.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → browser-extension → mac-vision → unified
- **model tier:** planner
- **latency:** Discover both versions within 5 seconds, produce a semantic diff within 15 seconds, and require an explicit spoken choice before any remote write.
- **cost:** <$0.08 per reconciliation; one planner call plus optional background extraction dominates.
- **security:** Keep authenticated web contents in the browser unless necessary; send normalized sections and hashes to the planner. Never overwrite either source automatically. Preserve both originals, record the selected merge and target URL, and expire extracted sensitive content after completion.
- **missing:** Structured browser extraction and write-back for the specific editor types, including conflict-safe version tokens; A local file snapshot/diff adapter that preserves encoding and metadata; A semantic merge engine with citation of which source supplied each changed section; A transaction record and rollback artifact spanning the local file and browser write


## Changes it proposed to its own stack

### `mac-harness` — Add a task lease that spans relay, Mac, and browser: before a long-running action, Mac reports its sleep/display-lock risk and creates a resumable checkpoint; it renews while progress receipts arrive, ends on success/failure, and on wake/reboot emits one reconciled result rather than leaving a phantom processing job. The lease must use a process group so cancellation can actually terminate run_shell, and it must attach ledgerId to jobId on creation.
- **owner gets:** Long tasks stop being silent time sinks. The owner can close the lid or lose power and later hear a truthful answer—finished, partially finished, or stopped at a named step—with a safe next action.
- effort: Medium-high: launchd/wake handling, process-group execution, checkpoint schema, boot reconciliation, and browser session revalidation.  ·  risk: A resumed step could repeat a side effect. Recover by requiring idempotency keys and precondition checks; mark unverifiable steps blocked for owner choice instead of guessing. Existing orphaned ledgers must be labeled historical and never auto-run.
- cost: Negligible API cost; modest local disk for checkpoints and periodic receipts.  ·  latency: <100 ms per checkpoint; wake recovery usually under 10 seconds, with no impact on short actions.
- security: Do not persist inherited environment or raw page contents. Checkpoints contain redacted action metadata, hashes, and bounded output only; process groups still retain the owner's deliberate full-control policy.
- depends on: Wire executionContext's existing idempotency engine into POST /execute; Call closeLedger on every terminal /execute path; Add boot reconciliation for pendant-jobs.json and GET /ledger/interrupted; Run shell via a killable process group and preserve exit code


## What it asked for

_Nothing._
