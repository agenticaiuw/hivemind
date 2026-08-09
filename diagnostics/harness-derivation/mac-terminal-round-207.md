# Harness derivation — mac-terminal — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_mac_browser_execution_state** — Authenticated Mac agent and Safari extension are online; the extension sees 2 tabs with active tab DoorDash, pendingCommands=0, and there is a pendant-origin execute job currently processing for the news briefing.
  - evidence: GET /ops/status and GET /browser/status returned online=true, browser lastSeenAt 2026-08-08T22:33:01.141Z, pendingCommands=0; GET /jobs returned local_2ecfe81b-d22e-46fd-89ab-bf5fb8baa814 status=processing source=pendant.

## Capabilities it proposed

### "From the pendant, say “stop that” or “how far along is it” and have the exact Mac/browser task stop or report verified progress, even if the original voice turn has ended."
- **useful because:** This is the highest-value missing behavior: the owner can launch work away from the keyboard and still regain control from the device they are wearing. It must distinguish queued, running, completed, failed, and stale rather than claiming cancellation when the Mac process is still alive.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only for the short intent parse and spoken acknowledgement; a cheaper background worker owns job supervision, postcondition checks, and durable reconciliation.
- **latency:** Acknowledge the pendant within 500 ms; progress within 2 s; cancellation should reach the Mac process group within 1 s, not merely set a cooperative flag.
- **cost:** About $0.001–$0.01 per control turn depending on speech length; supervision is mostly local polling and costs negligible API tokens.
- **security:** The relay must bind the spoken command to the originating job/turn and never cancel a similarly named job. Return only redacted progress. Killing a process group can discard unsaved work, so the spoken acknowledgement must state whether termination is requested, confirmed, or unavailable.
- **missing:** Mac executor must retain a real child PID/process-group handle and kill it on cancellation; POST /jobs/:jobId/cancel currently only signals between steps.; Durable job-to-ledger and job-to-pendant-turn IDs, plus boot reconciliation of processing jobs.; Browser commands need abort propagation and a final observable postcondition, not just command deletion.

### "When I press the second button after being away, tell me “where I left off” and give me one concrete next action, using the last Mac project/window and the authenticated browser page I was actually on."
- **useful because:** The pendant is the only surface present during a walk and the browser is the only surface that can see private sessions. A compact, spoken re-entry cue would eliminate the daily cost of reconstructing context across the Mac and browser, without reading or uploading page contents unnecessarily.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Cheap background summarizer builds a short-lived handoff; realtime only speaks it on button press. Do not resend whole pages: use structured tab metadata, active project, and existing context entities.
- **latency:** Snapshot on each meaningful focus/project change in under 300 ms; spoken answer within 2 s of the button press; stale snapshots must be labeled with age.
- **cost:** Near-zero for capture and storage; roughly $0.001–$0.005 for an occasional 3–5 sentence summary.
- **security:** Keep page text and cookies local to the browser/Mac. Store only URL origin, title, project/session identifiers, timestamp, and an explicitly selected next-step claim. Never infer a private page's contents from a title alone; say “I only know the title” when that is all that is available.
- **missing:** A Mac focus/project-change event stream that emits compact snapshots rather than requiring a poll at button time.; A browser-extension snapshot command for active tab metadata and the last authenticated task state, with provenance and expiry.; A durable handoff record keyed to the pendant's existing moment/bookmark payload, plus a spoken stale-data policy.

### "While my Mac is asleep or disconnected, say “when it’s back, open the invoice page, download the newest invoice, and tell me when it is safely saved”; run it once when the Mac and authenticated browser return, then speak the verified result."
- **useful because:** The owner should not have to remember and reissue a task just because the machine was unavailable. The pendant can capture intent now, the always-awake relay can hold it, and the browser can use its private session later—this cannot be done by any one node alone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime extracts a bounded intent and confirmation-free, reversible navigation; a low-cost scheduled/background worker waits for presence and performs the task. Use the expensive model only when the target is ambiguous.
- **latency:** Capture and local queue within 1 s; wake/presence polling every 30–60 s; announce completion within 5 s of browser confirmation. Expire unrun tasks after an owner-visible deadline.
- **cost:** Usually under $0.01 per task; relay storage and presence polling dominate, with one cheap summarization call only if the page has multiple candidate invoices.
- **security:** Persist the task, not cookies or page text. Require a host/origin allowlist and an exact target predicate (invoice date/number). Re-check the page before download, hash the resulting local file, retain browser provenance, and report “not completed” if any predicate is missing. Destructive or externally visible actions remain out of this unattended mode.
- **missing:** A durable relay-held deferred-intent queue with expiry, deduplication, and wake conditions for Mac/browser presence.; A browser command that can select a download by typed predicate, wait for completion, hash the local artifact, and return provenance.; A completion callback to the pendant and a local-file verification route; current browser result and Mac job records do not form one exactly-once chain.

### "Say “is everything in sync?” and have the pendant give me one truthful answer about whether the pendant, relay, Mac job, and authenticated browser agree on the last action—identifying any contradiction instead of choosing one state silently."
- **useful because:** Today each surface can independently claim a different truth: a Mac job can remain processing after a restart, a browser command can be stale, and the pendant can retain an older status. The owner needs a single confidence-bearing answer before trusting an action or walking away from it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a cheap deterministic consistency checker for IDs, timestamps, sequence numbers, and terminal states; use realtime only to explain the result in speech. No large context resend is needed.
- **latency:** Return a local cached answer within 500 ms when offline; with all nodes online, reconcile in under 3 s. Mark data stale by age rather than waiting indefinitely.
- **cost:** Negligible API cost for normal checks; occasional low-cost explanation generation under $0.001 per query.
- **security:** Compare opaque job and turn identifiers, not private page contents or credentials. Never expose browser URLs in an unsolicited spoken response unless the owner asks. Treat disagreement as unknown, never as completion, and preserve the conflicting receipts for audit.
- **missing:** A relay reconciliation endpoint that joins pendant turn IDs, relay events, Mac job IDs, browser command IDs, and terminal receipts into one consistency result.; Monotonic sequence/heartbeat propagation from the pendant and browser, with explicit stale and partitioned states.; A compact spoken-status contract and pendant cache that can represent conflict rather than only success/failure.

### "Ask “what exactly happened after I said that?” and have the system reconstruct a short, ordered account from my spoken turn through relay dispatch, Mac execution, browser activity, and the final observable state, including gaps and timestamps."
- **useful because:** The owner currently gets fragments from different logs and cannot tell whether a spoken request was planned, dispatched, executed, or merely claimed. A causal timeline makes the system trustworthy and makes failed or partially completed work recoverable without guessing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic event correlation and redaction first; a cheap text model compresses the verified timeline into speech. Realtime is unnecessary except for the final answer.
- **latency:** For recent work, answer in under 2 s from cached events; for older work, under 10 s. Never fabricate missing intervals—say “no record.”
- **cost:** Usually below $0.002 per query; the dominant cost is local event retention and correlation, not model inference.
- **security:** Return only events belonging to the authenticated owner and requested turn. Redact tokens, cookies, command environment, and sensitive page contents. Keep raw evidence local and expose hashes/labels in spoken output.
- **missing:** A shared event envelope with immutable event ID, source node, turn ID, monotonic time, wall time, and causal parent.; Relay and browser events must be durably retained alongside Mac receipts instead of being independently summarized.; A read-only correlation route that can identify missing, duplicated, and reordered events.

### "Say “do these three things” and have the system schedule them across my Mac and authenticated browser without stealing focus from the task I am using, serialize conflicting actions, and tell me when all three are actually finished."
- **useful because:** The owner should be able to delegate a small batch while continuing work. Today jobs can overlap without a concurrency limit or shared resource claim, so one task can hijack the browser or invalidate another task's assumptions. A resource-aware scheduler would make delegation dependable rather than fragile.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** A deterministic scheduler handles resource claims, dependencies, and retries; use a cheap planner only to split an ambiguous spoken batch into typed steps. Realtime only confirms the plan and final result.
- **latency:** Acknowledge and show the schedule within 1 s; begin non-conflicting work immediately; serialize browser focus-sensitive work with less than 500 ms arbitration overhead.
- **cost:** Typically under $0.005 per batch; most work is local scheduling and status polling.
- **security:** The scheduler must not silently reorder externally visible or destructive actions. Keep browser-session affinity explicit, isolate credentials by session, and report skipped or blocked steps. Persist only task metadata and opaque handles, not page contents or secrets.
- **missing:** A shared resource-lock service for browser session, focused UI, filesystem paths, audio pipeline, and Mac job classes.; A dependency-aware batch schema with idempotency keys, per-step postconditions, and owner-visible ordering.; Pendant progress aggregation that can summarize several jobs without collapsing partial failure into success.


## Changes it proposed to its own stack

### `mac-harness` — Add a postcondition-driven recovery runner for every Mac/browser action chain: capture exit code, stderr, child PID, and a typed postcondition; on failure classify transient versus semantic failure, retry only the failed step with bounded exponential backoff or an explicitly different strategy, and reconcile the final state after restart. Link the execution ledger, job ID, browser command ID, and pendant turn ID in one causal receipt.
- **owner gets:** “Do the thing” becomes reliable instead of silently becoming a failed job that must be manually reconstructed. The owner gets a truthful explanation—completed, partially completed, or not attempted—and a safe continuation point after sleep, crash, or network loss.
- effort: Medium-high: replace exec with process-group-aware spawning, add receipt fields and postcondition adapters, wire browser abort/result callbacks, and add boot-time reconciliation. The existing ledger and job stores reduce greenfield work.  ·  risk: A mistaken postcondition or retry can duplicate a side effect. Default retries to read/inspect and idempotent operations; require an explicit idempotency key for mutations, and mark ambiguous outcomes as unknown rather than replaying. Recover by exposing the exact command and receipt for manual continuation.
- cost: No meaningful per-call API cost; modest local CPU/disk for receipts and one extra verification step. Background retry may add a cheap model call only for ambiguous semantic failures.  ·  latency: Successful actions gain tens of milliseconds for process and postcondition capture; transient failures may take seconds due to backoff, with immediate progress updates to the pendant.
- security: Do not persist inherited secrets or full environment. Record a redacted environment fingerprint and command classification, with raw sensitive output retained locally only when needed for recovery.
- depends on: Close the orchestrator ledger on every terminal path and populate planMeta.jobId.; Implement real process cancellation and exit-code/PID capture for run_shell.; Add exactly-once/idempotency wiring to the existing executionContext engine.; Add browser command abort and durable final-result callbacks.


## What it asked for

_Nothing._
