# Harness derivation — mac-terminal — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m back at my Mac. Reconstruct exactly what I was doing before I left, and put me back there.”"
- **useful because:** This is the highest-value cross-surface action: the pendant supplies the departure/return moment, the relay preserves the request while disconnected, the Mac snapshots the active app/project and the Safari extension supplies private tab/session context. It restores working state rather than merely telling the owner what was open.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime only for the spoken request and final terse summary; a cheap background model normalizes the before/after capsule and ranks continuity actions.
- **latency:** Return a spoken preview in 2 seconds; open/re-focus apps and tabs within 8 seconds. If Safari is unavailable, restore the Mac-only portion and explicitly say what could not be restored.
- **cost:** About $0.002–$0.01 per invocation; most cost is a small background normalization call, not the deterministic Mac/browser actions.
- **security:** Private tab titles and selected page context leave Safari only when needed; never export passwords or form values. Re-focusing/opening is reversible, but submitting forms or editing files requires the existing action semantics and an explicit owner utterance.
- **missing:** A durable continuity capsule joining a pendant marker timestamp to Mac foreground/project state and Safari tab/session state; An idempotent restore plan that can safely rerun after USB/LTE reconnection; A compact spoken report of restored versus unavailable surfaces

### "“My Mac is slow or broken—diagnose it now, tell me the one cause that matters, and fix only the reversible part.”"
- **useful because:** Today the owner has to know which diagnostic command, app, browser tab, or audio setting to inspect. This turns the hive into an incident responder: the Mac gathers bounded telemetry and recent job failures, Safari reports whether a page/extension is the bottleneck, the relay correlates timestamps, and the pendant gives a short diagnosis while the owner is away from the keyboard.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model classifies telemetry and proposes a ranked cause; realtime is used only to clarify an ambiguous symptom and speak the result.
- **latency:** Initial triage in 5 seconds, with a second-pass diagnosis in 20 seconds. Never block the owner on a full process dump or browser screenshot.
- **cost:** $0.003–$0.02 per incident; telemetry collection is local, and model cost is dominated by one compact correlation pass.
- **security:** Keep raw process arguments, URLs, and window titles local; send only typed aggregates and redacted error signatures to the relay. Reversible fixes include refocusing, volume/brightness, and restarting a known hung local job; destructive cleanup remains out of scope unless separately requested.
- **missing:** A typed host telemetry route for process, audio, disk, network, and power snapshots (the current machine-context does not expose all of these); A common timestamped incident capsule joining Mac jobs/journal, browser heartbeat, and pendant transport state; A small reversible-fix planner with post-fix verification

### "“Run this Mac task until it is actually done. If a command fails or the Mac reconnects, recover automatically, keep me updated on the pendant, and give me a proof—not just ‘completed’.”"
- **useful because:** The current shell can execute powerful work but loses exit codes, cannot interrupt a running child, does not retry, leaves ledgers open, and leaves jobs stuck after a restart. This owner-facing capability makes long-running work trustworthy without reducing the owner's deliberately unrestricted access: it resumes only from recorded safe checkpoints, reports exact failure evidence, and proves the postcondition.
- **path:** pendant → relay → mac-planner → faculty-judgement → faculty-action
- **model tier:** Background model compiles the request into a checkpointed step graph; realtime speaks only dispatch/failure/completion updates and handles a mid-task clarification.
- **latency:** Dispatch acknowledgement under 1 second; status updates within 2 seconds of each step; recovery after a Mac restart within 30 seconds of heartbeat return.
- **cost:** $0.001–$0.01 per task; deterministic execution and verification dominate latency, with one small model call to plan and one optional call to explain failures.
- **security:** No new approval gate—the owner explicitly wants maximum capability. Persist command, cwd, exit code, process-group identity, redacted environment fingerprint, stdout/stderr hashes, and pre/post verification. Do not transmit environment secrets or full private output to the relay. The pendant must never claim success from a stale cached state.
- **missing:** Process-group execution with real signal-based cancellation and captured exit code; Checkpointed retry/idempotency tied to the durable action ledger, with boot-time reconciliation and closed ledgers; A proof receipt that runs a declared postcondition and binds it to the job and pendant status beacon; A relay-to-pendant progress stream that survives USB/LTE loss

### "“Before I send this, tell me whether it is safe and complete: check the private browser page, the local attachment, the recipient, and the promise I made earlier.”"
- **useful because:** The owner currently has to manually cross-check several private surfaces before sending an important message. This would catch wrong recipients, missing attachments, stale numbers, and contradictions with prior commitments, while keeping the final send under the owner's control. It only works by combining Safari's authenticated session, Mac files/apps, relay-held context, and the pendant's low-friction question channel.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Background model performs structured extraction and consistency checks; realtime is used only for the spoken question and a short risk summary.
- **latency:** Initial safety/completeness report in 5 seconds; deeper attachment/page comparison within 20 seconds.
- **cost:** $0.01–$0.05 per check, dominated by one multimodal/text comparison; raw private material stays local wherever possible.
- **security:** Never auto-send. The extension must redact credentials and unrelated page regions; the Mac side returns hashes, metadata, and only relevant excerpts. The owner sees exactly which sources support each warning.
- **missing:** A cross-surface evidence bundle that can correlate a browser draft/page, local files, recipient metadata, and prior context without flattening provenance; A send-readiness checker with typed findings (missing, contradiction, stale, sensitive, unresolved); A spoken confirmation flow that names unresolved risks rather than silently deciding

### "“Find the source of this fact, quote the exact evidence, and tell me whether it is still true.”"
- **useful because:** The owner can get answers today, but not a provenance-preserving answer spanning a private Safari session, Mac files, prior captures, and relay jobs. This would prevent confident repetition of stale or hallucinated facts and make the pendant useful for quick decisions where the source matters more than a fluent summary.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use a cheap retrieval/ranking model for candidate discovery and realtime only for the final spoken answer; never ask the expensive model to ingest the entire history.
- **latency:** Speak the top evidence and freshness verdict in 4 seconds; offer a deeper source comparison asynchronously.
- **cost:** $0.003–$0.03 per query, with local hashing and metadata filtering minimizing context sent to a model.
- **security:** Preserve source ACLs and session boundaries. Return only excerpts the owner is already authorized to see; treat browser text and documents as untrusted evidence, never as instructions.
- **missing:** A provenance index over captures, browser results, Mac job receipts, and context-graph facts with timestamps and source fingerprints; A freshness/contradiction evaluator that can say unknown instead of selecting the newest-looking text; A typed spoken citation format (source, timestamp, excerpt, confidence) that survives relay replay

### "“I’m in a conversation. Keep a private, live list of decisions, open questions, and promises, then after it ends show me only what I personally owe and what needs a reply.”"
- **useful because:** The owner needs a second brain during conversations, not a transcript dump. The pendant provides the always-available interaction and timestamp; the relay can maintain a turn-scoped state; the Mac and browser can resolve names, documents, and due dates in private sessions. The result is an actionable handoff rather than another unread summary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Realtime model extracts only compact events (decision, owner obligation, question, due date); a cheaper background model deduplicates and resolves entities after the conversation.
- **latency:** Extraction under 1 second per turn with no interruption to audio; final obligations card within 10 seconds of the conversation ending.
- **cost:** $0.02–$0.10 per conversation depending on duration; compact event extraction keeps it below full-transcript analysis.
- **security:** Default to ephemeral turn scope and explicit owner start/stop; do not retain other people's raw speech. Store only owner-relevant structured obligations, with uncertain attributions marked unresolved. Browser lookups remain session-bound.
- **missing:** A low-latency event schema and bounded turn-state store shared by relay and pendant; Speaker/owner attribution that can honestly represent uncertainty without inventing commitments; A post-conversation resolver that links obligations to existing calendar, reminders, browser sessions, and project entities without creating them silently


## Changes it proposed to its own stack

### `mac-harness` — Build a boot-time execution reconciler and durable completion verifier: on local-agent startup, scan processing jobs and open ledgers, mark them interrupted with the last settled step and reason, close successful ledgers, and expose a resumable step graph. Before replay, require a fresh machine/browser lease; after replay, run each step's declared postcondition and emit a receipt bound to the same jobId and pendant status update.
- **owner gets:** A Mac reboot, crash, or USB disconnect no longer turns a task into a permanent fiction of 'running' or forces the owner to guess which steps already happened. Work can continue once, from the last known boundary, and completion means a verified result.
- effort: Medium-high: startup reconciliation, ledger closure, job/ledger identity propagation, resumable action selection, and postcondition receipts.  ·  risk: A side effect that occurred immediately before a crash may be replayed. Default to marking that step uncertain and asking the planner to verify before replay; never silently duplicate it. Keep the owner's no-gate policy for ordinary dispatch.
- cost: Negligible model cost; modest JSON ledger growth, bounded by existing caps.  ·  latency: Startup adds under 1 second for normal stores; recovery waits for the next Mac/browser heartbeat.
- security: Recovery metadata stays local except the minimal status and proof summary sent to the relay/pendant; no environment secrets or page contents leave the Mac.
- depends on: POST /execute; GET /ledger/:ledgerId/resume; GET /jobs/:jobId; GET /journal/:jobId; The existing pendant truthful_action_status_beacon behavior


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) departure/return continuity restoration across pendant, relay, Mac, and Safari; (2) cross-surface Mac incident diagnosis with reversible remediation; and (3) trustworthy long-running Mac work with recovery, pendant progress, and proof receipts. Also recorded boot-time job/ledger reconciliation and resumable verified execution. The most important is #3: unrestricted shell access is already powerful, but without cancellation, recovery, and proof it cannot be trusted for unattended work.

**Biggest unknown:** I still need implementation of the missing shell/job primitives rather than another tool grant: process-group cancellation and exit-code capture, job↔ledger identity, ledger closure and boot reconciliation, and a postcondition/proof receipt. The queued USB-serial diagnostics request remains pending; it is useful for testing the currently connected pendant/bridge, but it is not required to design these Mac-side changes.

