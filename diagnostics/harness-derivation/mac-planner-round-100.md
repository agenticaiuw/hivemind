# Harness derivation — mac-planner — round 100

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Live browser bridge is offline with 7 pending commands; no tab is attached. Browser-dependent jobs need explicit defer/fallback rather than continuing to enqueue.
  - evidence: GET /browser/status returned online:false, tabId:null, pendingCommands:7 at round 100.

## Capabilities it proposed

### "If I say “pause that” or press the pendant button while a Mac/browser task is running, stop safely, save exactly where it got to, and let me say “resume it” later—even after the browser reconnects or the Mac was asleep."
- **useful because:** Today a long job can outlive the browser connection, leave pending commands, or require the owner to remember what was already done. A cross-surface task lease gives the owner a dependable pause/resume control and prevents duplicate clicks, submissions, or stale browser actions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the short spoken pause/resume interaction. Use a cheaper background worker for checkpoint compaction, stale-step validation, and retry planning; use the Mac local planner only to expand the next concrete step.
- **latency:** A pause acknowledgement should be under 1 second when the relay is reachable; checkpoint persistence under 2 seconds. Resume may take 2–5 seconds to validate Mac/browser availability before acting. If browser is offline, acknowledge and defer without issuing another command.
- **cost:** About $0.001–$0.01 per pause/resume interaction depending on realtime audio duration; background checkpointing is negligible. The dominant cost is only the spoken interaction, not the persisted state.
- **security:** Checkpoint data can contain URLs, page snippets, file paths, and draft text, so encrypt or redact sensitive fields and retain only the minimum needed to resume. Never replay an irreversible browser step from a checkpoint without an explicit fresh confirmation; invalidate leases on tab/session changes and mark unknown outcomes for review.
- **missing:** A durable task-lease/checkpoint schema shared by relay, Mac job runner, and browser bridge; A pendant button/event route that targets the active job rather than starting a new command; Browser command cancellation and idempotent step keys, including an offline queue TTL and supersession rule; Mac-side checkpoint hooks around each action and a resume endpoint that reports the last verified receipt; A dashboard/voice status view showing paused, stale, unknown-outcome, and resumable states

### "After you do something important for me—send a message, change a record, submit a form, or create an appointment—prove that it actually took effect and tell me if the result is confirmed, contradicted, or unknown."
- **useful because:** Today an action receipt mostly reports what the executor attempted. The owner still cannot reliably distinguish “the click ran” from “the remote service accepted and persisted the change,” especially when a browser disconnects or a Mac action times out. A postcondition verifier would prevent false completion claims and surface ambiguous outcomes immediately.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to acknowledge the result briefly. Use a cheaper background verifier for re-reading the target state and comparing it with the intended mutation; use a stronger model only when the returned evidence is structurally inconsistent or ambiguous.
- **latency:** For local Mac changes, verify within 1 second. For browser-backed mutations, verify within 3–10 seconds, with a bounded retry after navigation or session recovery. Speak immediately when the state is unknown rather than waiting indefinitely.
- **cost:** Typically $0.001–$0.02 per verification, dominated by browser/page retrieval and occasional model-based comparison; local structured checks should require no model call.
- **security:** Verification may re-read private mail, account pages, files, or calendar records. Limit it to the exact target and fields involved, redact evidence in spoken output, encrypt retained before/after hashes, and never treat a failed verification as permission to retry an irreversible action automatically. Sending, deletion, purchases, and submissions still require the owner's existing confirmation policy.
- **missing:** A postcondition contract attached to every mutating action: target, expected state, verification method, deadline, and safe-failure behavior; Independent read-after-write adapters for Mac files/Notes/Calendar/Mail and authenticated browser pages; A durable evidence record linking intent, action receipt, verification read, and normalized before/after values; A reconciliation policy for timeouts and duplicate-risk outcomes that marks the job unknown instead of replaying it; Pendant and dashboard result states for confirmed, contradicted, and unknown, with a concise evidence link


## What it asked for

_Nothing._
