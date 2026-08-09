# Harness derivation — mac-terminal — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tell you to do something on my Mac, make it finish even if the local agent or laptop restarts; if it cannot safely resume, tell me exactly where it stopped on the pendant."
- **useful because:** Today a long shell or browser job can remain falsely 'processing' after a restart, and the durable ledger is never automatically reconciled or resumed. This gives the owner one reliable mental model: a request is either completed, explicitly paused at a named step, or failed with evidence—not silently lost.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → unified
- **model tier:** background for reconciliation and resume planning; realtime only for the short spoken status and the owner's follow-up
- **latency:** Immediate dispatch acknowledgement under 1 s; restart recovery within 5 s of the Mac agent boot; spoken final status under 2 s after each resumed step
- **cost:** Usually one cheap planner call only when a step failed or needs re-planning; roughly $0.001–$0.01 per recovery, dominated by model reasoning rather than storage or polling
- **security:** The agent retains the owner's deliberate FULL_CONTROL_MODE and does not add approval gates. Resume must require an idempotency key and replaySafety check, never blindly repeat non-reversible shell/file/browser mutations. The relay receives command labels, step state, and bounded error text; redact stdout/stderr secrets before sending to the pendant.
- **missing:** boot-time reconciliation that marks processing jobs interrupted; closing the orchestrator ledger on every terminal path; a durable jobId-to-ledgerId link in planMeta; step-level idempotency/replay decisions wired into /execute; a resume worker that submits only safe runnable steps; pendant delivery of paused/resumed state over the existing status beacon

### "What changed because of that last request? Give me a short spoken answer, and let me inspect the exact evidence on my Mac."
- **useful because:** A success boolean is not enough for an unattended shell/browser action. The owner needs a human answer (which files, apps, tabs, and external effects changed) plus a durable evidence bundle when something surprising happens. This correlates the Mac receipt with the browser inspection and the pendant turn instead of making the owner reconstruct it from logs.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard
- **model tier:** cheap background summarizer over structured diffs; realtime only to speak the result and answer a follow-up
- **latency:** Collect pre/post snapshots opportunistically; final summary in under 3 s for a normal action, with a dashboard evidence card available within 10 s
- **cost:** Near-zero for collection; about $0.001–$0.005 for a structured diff summary, dominated by model tokens when stdout or browser state is large
- **security:** Never upload raw environment variables, cookies, page bodies, or unrestricted stdout. Store sensitive evidence locally with a short retention period, send only redacted paths, app/tab titles, hashes, exit status, and explicitly requested excerpts. No new confirmation gate is required under the owner's policy.
- **missing:** pre/post snapshots tied to one request across filesystem/git, running app, and browser tab state; a receipt schema containing real exit code, pid, argv, effective cwd, timeout, and output hashes; redaction and retention rules for evidence bundles; a dashboard route to open the evidence bundle from a spoken result

### "How far along is that? Give me one honest progress update for the whole Mac-and-browser task, including the current step, elapsed time, what is waiting on the browser, and what still needs to happen."
- **useful because:** The owner currently gets job status or a final result, but multi-step work is opaque while it runs. A step-aware digest prevents repeated voice queries, exposes a browser extension that has gone offline, and lets the owner decide whether to wait without opening the dashboard.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic aggregation of receipts, ledger steps, browser heartbeat, and job state; cheap summarization only for a natural spoken sentence, never the realtime tier for polling
- **latency:** Answer from local state in under 300 ms; browser heartbeat freshness under 2 s; no extra polling storm or model call for repeated requests
- **cost:** Essentially zero per update; optional short summarizer call under $0.001, dominated by voice synthesis if spoken
- **security:** Expose labels and durations, not command strings, cookies, page bodies, or stdout. Bind the query to the owner's session/job handle and mark stale data explicitly. It is read-only and adds no approval gate.
- **missing:** one normalized progress event schema for shell, browser, and computer-use steps; ledger/job join and a live current-step record; browser heartbeat freshness and command acknowledgement in the same job timeline; a compact relay query that aggregates without resending full receipts or model context

### "While I am presenting or in a call, keep the pendant silent unless something is urgent; queue the rest and give me a one-sentence digest when I leave the call."
- **useful because:** A wearable that speaks whenever a Mac job or browser watch changes is actively disruptive. The Mac knows the foreground meeting/presentation state, the browser knows which session generated the event, the relay can rank urgency, and the pendant can defer audio without losing the event. No single node can make that decision reliably.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic local policy for detecting presentation/call state and queueing; background model only for digest grouping; realtime reserved for an actually urgent alert
- **latency:** Enter quiet mode within 1 s of the Mac entering a call/presentation app; urgent alert under 2 s; digest within 5 s of leaving quiet mode
- **cost:** Near-zero for state detection and queueing; under $0.005 for an occasional grouped digest, dominated by summarization and speech
- **security:** Keep meeting titles, browser URLs, and event text local by default; send only urgency class and a redacted digest to the relay. The owner explicitly opts into which events count as urgent. Never infer or announce private call content.
- **missing:** Mac foreground-app and call/presentation detection exposed as a signed event stream; a relay-side per-owner quiet-mode policy with urgency classes and expiry; browser events carrying source/session and urgency metadata; pendant deferred-audio inbox with an explicit 'quiet but not lost' state; dashboard controls to inspect, reprioritize, or discard queued notifications

### "Before I send this, check the open browser draft and any attached Mac files for secrets, private data, wrong recipients, and mismatched numbers; give me a spoken risk summary and leave the draft untouched."
- **useful because:** Today the browser can hold the authenticated draft and the Mac can hold the source files, but neither can reliably compare them and explain accidental disclosure before submission. This is a genuinely cross-surface preflight: it prevents a costly send without taking ownership of the final send action.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard
- **model tier:** Background model over locally extracted text and structured recipient/file metadata; realtime only for the short result
- **latency:** Under 10 s for a normal draft plus up to five local attachments; immediately report which attachment or page could not be inspected
- **cost:** Roughly $0.01–$0.05 per preflight depending on attachment text and OCR volume; local extraction dominates latency, model tokens dominate API cost
- **security:** This processes highly sensitive drafts and files. Keep raw content on the Mac/browser bridge, pass only encrypted bounded excerpts or local findings to the model, redact credentials and financial identifiers, retain no copy after the result, and never mutate or submit the draft. The owner remains the final sender.
- **missing:** a browser route that extracts the current draft, recipients, and attachment references without submitting; a Mac-local attachment reader and secret/PII detector; cross-source numeric and recipient consistency checks; a privacy-preserving analysis contract with deletion/retention guarantees; a pendant response that can state 'not inspected' rather than implying safety

### "After any task, tell me exactly what left my Mac or browser session, which model or service saw it, and let me erase the local record without undoing the work."
- **useful because:** The owner currently has no plain-language data-egress account across shell output, browser pages, relay events, and model context. A privacy receipt makes the hive trustworthy: useful work can remain unrestricted, while the owner can see whether a page, file excerpt, URL, or secret crossed a boundary.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → unified → dashboard
- **model tier:** Deterministic egress classification and local accounting; no model needed except an optional cheap natural-language summary
- **latency:** Receipt generated alongside each event with under 100 ms overhead; spoken summary under 2 s on request; deletion action acknowledged immediately and completed within 5 s
- **cost:** Near-zero compute and model cost; bounded local metadata storage, with optional $0.001 summary
- **security:** The receipt itself is sensitive and must never contain the secret it describes. Store content hashes, data classes, destination, purpose, and retention—not raw tokens or page bodies. Deletion must erase local receipt payloads without pretending remote services forgot data; the pendant must say when deletion cannot be verified.
- **missing:** a shared data-classification vocabulary across Mac, browser, relay, and model calls; egress hooks around shell stdout, browser inspection/results, pipeline audio/events, and prompt assembly; a local append-only privacy receipt with bounded retention and verified deletion; a dashboard and pendant query for per-task egress summaries; explicit remote-retention disclosures from each model/service


## Changes it proposed to its own stack

### `mac-harness` — Instrument every run_shell action with a truthful execution envelope: invoke through a process API that records argv (while preserving the owner's unrestricted command capability), effective cwd, start/finish monotonic timestamps, pid/process-group, timeout, signal, numeric exit code, stdout/stderr byte counts and hashes, and a redacted environment fingerprint. Record the original submitted action and any silent rewrite separately, then link the envelope to jobId, ledgerId, and receiptId. Make cancellation send the signal to the process group and settle the receipt only after reaping or explicitly marking the process unknown.
- **owner gets:** When the agent says a command failed, stopped, or changed something, the owner can trust exactly what happened and recover without guessing. It also makes the pendant's running/completed/failed beacon truthful instead of merely reflecting a request flag.
- effort: Medium: computerControl executor, actionReceipts, jobTracker, ledger close paths, and boot reconciliation; add a small local evidence viewer rather than a new model.  ·  risk: Changing exec plumbing can break shell semantics, especially pipelines and shell built-ins. Preserve a compatibility mode using /bin/sh -c but still capture the spawned shell's pid/group; test rewrites and timeout behavior. If telemetry fails, execution should continue but mark the receipt incomplete.
- cost: Negligible storage (roughly 1–4 KB per action plus bounded output metadata); no extra model calls. Periodic pruning is needed for the existing 120-job/1 MiB stores.  ·  latency: Under 20 ms bookkeeping overhead per action; cancellation becomes faster and deterministic instead of waiting up to 120 s.
- security: No gates or reduction of FULL_CONTROL_MODE. Do not persist raw env or secrets; hash variable names/values after redaction. Treat command strings, paths, and output as sensitive local data with bounded retention.
- depends on: A reliable jobId-to-ledgerId association; orchestrator calling closeLedger on all terminal paths; process-group tracking in run_shell; boot-time reconciliation of processing jobs


## What it asked for

_Nothing._
## Its own summary

This round produced four non-gating proposals. The highest-value one is restart-proof execution: a Mac/browser request must end completed, explicitly paused at a named step, or failed with evidence, and the pendant must say which—not leave a durable job falsely processing. I also proposed an evidence-backed “what changed?” report, a truthful execution envelope for shell actions (exit code, pid/group, timing, rewrite, bounded redacted evidence), and a compact whole-task progress digest spanning Mac and browser. The attempted emergency-stop proposal collided with an existing backlog item, so I did not count or restate it.

**Biggest unknown:** I still lack live USB-serial diagnostics for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; that request is already queued and must not be re-asked. For the Mac work, the remaining product gaps are implementation rather than access: close/reconcile ledgers, join job↔ledger IDs, capture real shell process metadata and exit status, normalize browser/shell progress events, and preserve the owner's unrestricted FULL_CONTROL_MODE without adding gates.

