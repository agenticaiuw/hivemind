# Harness derivation — relay-realtime — round 130

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I ask you to do something on my Mac or in my browser, tell me right away what you’re doing, then keep track of it and update me when it finishes or fails."
- **useful because:** The owner gets immediate, clear feedback from the pendant, and a reliable status trail without needing to watch the Mac. It reduces confusion when the Mac is asleep, the browser extension is offline, or commands queue.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for the initial spoken acknowledgment; cheaper planner/executor models for Mac/browser work; relay reads status without invoking heavy models.
- **latency:** Under 300ms to acknowledge and confirm what was queued. Status updates can arrive later and should not block the conversation.
- **cost:** Low for the relay acknowledgement and status reads; Mac/browser execution costs dominate. Logging/receipts add small overhead.
- **security:** Status reads expose task names and metadata; keep them minimal and owner-only. Never claim completion unless status says done. Avoid leaking URLs or sensitive page content in spoken summaries.
- **missing:** relay_job_status implemented end-to-end with a stable job id mapping to Mac/browser receipts; a lightweight status event stream or polling route on the relay to push updates to the pendant without the owner re-asking; browser bridge recovery handshake that normalizes action parameters and replays queued commands after reconnect

### "When my Mac gets stuck or needs a choice while carrying out something I asked from the pendant, ask me the smallest possible question over the pendant, let me answer naturally, and resume the exact workflow without making me repeat the request."
- **useful because:** Today a Mac workflow can be queued or fail while the owner is away, leaving them to inspect logs or restart from scratch. This would make the worn pendant a true out-of-band operator console: the Mac can pause at an uncertainty, the relay can conduct a short voice turn, and the original plan can continue with its accumulated state.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay-realtime for the brief question and answer; mac-planner (gpt-5.6-luna) for plan continuation and validation; mac-vision (gpt-4.1-mini) only for visual steps. Do not spend the realtime tier on planning.
- **latency:** Speak the clarification within 2 seconds of the Mac reporting a blocker; resume within 5 seconds after the owner's answer. If the pendant is unreachable, retain the paused workflow and present it in the dashboard when connectivity returns.
- **cost:** About one short realtime turn plus one planner continuation per blocker; roughly $0.02–$0.10 per clarification depending on audio/transcript token size. The dominant cost is planner context replay, so store a compact checkpoint rather than resending the whole transcript.
- **security:** The question must expose only the minimum ambiguity and redact secrets from spoken prompts. Answers must be bound to the originating job, session, and checkpoint to prevent an old answer resuming the wrong task. Mutations remain subject to the owner's existing maximum-access policy, but every continuation needs an immutable receipt and an undo reference. Audio/transcripts should expire after the workflow completes unless explicitly retained.
- **missing:** A durable workflow checkpoint format containing plan step, observed state, pending question, and resumable inputs; A Mac-to-relay blocker event channel and relay-to-pendant prompt/answer channel (not polling-only job status); A continuation endpoint that atomically attaches the answer to one paused job and prevents duplicate resumes; Mac planner support for pausing at uncertainty and replaying from a checkpoint; Pendant UX for spoken clarification prompts, timeout, cancel, and answer confirmation

### "While a long task is running on my Mac, let me say 'pause that and do this now'; carry out the urgent request from the pendant, then offer to resume the paused task from exactly where it stopped."
- **useful because:** The owner is often away from the Mac and should not have to wait for a slow workflow or risk losing it to a new request. This creates genuine conversational multitasking across the worn device, always-awake relay, and Mac executor rather than treating each utterance as an unrelated job.
- **path:** pendant → relay → mac-planner → mac-vision → mac-terminal → dashboard
- **model tier:** Realtime relay-realtime only classifies the short preemption command and acknowledges it; mac-planner owns queue arbitration and checkpoint/resume; mac-vision and mac-terminal execute the selected work. Use a cheaper background model to summarize paused state for the dashboard.
- **latency:** Acknowledge pause within 500 ms, stop at the next action boundary within 3 seconds, and start the urgent task within 5 seconds. Resume is explicit or can be offered later; never silently resume after a conflicting request.
- **cost:** Usually one realtime classification and one planner call per preemption, about $0.01–$0.08, with storage/queue overhead dominating rather than audio.
- **security:** Only the job owner/session that created the task may preempt or resume it. Checkpoint before every externally visible mutation and record whether an action completed, so a resume cannot duplicate a send/delete/purchase. Spoken commands need a short confirmation only when the phrase is ambiguous; the owner's no-gates policy still applies to clear reversible or high-impact commands.
- **missing:** A priority-aware job queue with cooperative cancellation at typed action boundaries; Durable per-step checkpoints and idempotency keys shared by planner, Mac executor, and relay; A pendant command grammar that distinguishes pause/resume/cancel from a new task; A resume preview that states the next action and any stale assumptions; Cross-node locking so browser, Mac, and relay cannot execute two owners of the same job simultaneously

### "If I ask for a task that spans my authenticated browser and my Mac, start the parts that can run without the Mac, keep my browser session private, and finish the Mac-dependent parts automatically when my Mac returns—then tell me exactly what was completed and what is waiting."
- **useful because:** The pendant is used while the owner is away, but today's execution treats Mac availability as an all-or-nothing dependency. A capability-aware split lets the always-on relay and browser surface make useful progress while the Mac is asleep, without asking the owner to manually restart or expose browser credentials.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** mac-planner (gpt-5.6-luna) decomposes the goal into capability-tagged stages; server/browser harness performs only browser stages; mac-planner/mac-terminal performs local stages when online; relay-realtime gives a concise spoken status and uses a cheaper background model to reconcile stage receipts.
- **latency:** Return a stage plan/status in under 3 seconds. Start browser-only stages immediately; detect Mac unavailability in under 10 seconds; resume local stages within 10 seconds of a verified Mac heartbeat. Final spoken summary should be under 15 seconds unless the owner asks for detail.
- **cost:** One planner decomposition and one reconciliation call, roughly $0.03–$0.15 per multi-surface task; browser and Mac execution costs are infrastructure-level. Compact stage receipts avoid repeatedly sending full histories to the realtime tier.
- **security:** Browser stages must execute inside the existing authenticated session without exporting cookies, page contents, or credentials to the Mac. Each stage declares its data boundary and dependencies; receipts prove which surface acted. A stale browser page or changed Mac state must invalidate dependent stages rather than silently continuing. Sensitive result text should be summarized on the relay and expire according to session policy.
- **missing:** A capability graph and planner output format for splitting one goal into independently runnable browser/Mac stages; A durable dependency-aware runner that persists stage state across Mac offline periods; A cross-surface correlation ID and typed receipts that can be merged into one owner-facing result; A secure browser-result handoff that passes only selected fields to the Mac stage; Mac-online/offline readiness events rather than one-shot status polling; A spoken and dashboard view showing completed, blocked, and waiting stages


## Changes it proposed to its own stack

### `integration` — Implement an intent routing and status correlation layer at the relay: when a tool call routes work to the Mac or browser, the relay records a stable job id, the normalized intent, the target surface, and the queued command ids. Add a small status endpoint or event stream that consumers (pendant, dashboard) can use to subscribe, and map backend receipts back to the original intent. Include a recovery path that notices when the browser extension is offline, initiates a bridge normalization step, and replays queued commands once the heartbeat returns.
- **owner gets:** They can speak a request once and trust the system to keep working, recover from transient browser/Mac issues, and report the outcome without manual checking.
- effort: Medium. Requires relay storage for job correlation, updates to Mac/browser harness to emit normalized receipts, and a consumer path for pendant updates.  ·  risk: Mis-correlating receipts could report the wrong outcome. Mitigate with explicit intent ids, target surface tags, and idempotent replay tokens. Recovery from mismatch is to mark the job unknown and ask the owner for clarification.
- cost: Low ongoing API cost; primary cost is implementation time. Storage is small metadata per job.  ·  latency: Minimal added latency for initial acknowledgment; background status handling is asynchronous.
- security: Job metadata could expose sensitive app names or URLs; restrict to owner-only access and store minimal fields.
- depends on: relay_job_status implementation; browser bridge receipt normalization; a relay-visible route or storage for job correlation

### `relay` — Add a cross-surface stage ledger and lease protocol. Every plan is compiled into stages with required surface, input/output schemas, dependency IDs, idempotency key, and expiry. The relay owns durable stage state; browser and Mac executors claim a stage lease, publish started/completed/blocked receipts, and relinquish it on heartbeat loss. A reconciler advances only satisfied dependencies, so browser work can finish while the Mac is offline and later continue without replaying completed mutations.
- **owner gets:** A request made from the pendant would make dependable progress even when the owner is away from the Mac, while preserving a single truthful answer about what happened instead of scattered or duplicated actions.
- effort: Medium-high: define stage/lease/receipt schemas, add durable Worker storage (Durable Object or equivalent), adapt planner output and both executors, and add crash/replay integration tests.  ·  risk: A lease timeout could cause duplicate external actions if an executor loses its response after acting. Require idempotency keys at every mutating action, mark uncertain outcomes as unknown rather than retrying automatically, and expose a repair/reconcile state. Recover by replaying only uncommitted read-only stages.
- cost: Small Worker Durable Object/storage cost per stage and receipt; no meaningful model cost beyond one decomposition and reconciliation call. Storage grows with retained receipts, so apply owner-configurable retention.  ·  latency: Adds tens to hundreds of milliseconds for ledger writes and lease acquisition; removes long waits caused by treating offline surfaces as total failure.
- security: Stage outputs must be schema-filtered at surface boundaries; browser credentials stay in the browser session. Correlation IDs and per-surface authentication prevent one job from claiming another's stage. Logs should redact values marked secret.
- depends on: A durable Worker queue/DO alarm or equivalent runner (currently absent); Planner support for capability-tagged stages and idempotency keys; Mac and browser executors emitting typed lifecycle receipts; A verified Mac heartbeat/readiness event


## What it asked for

### `s18-i0h0` (skill) — status_update_listener
- does: Listens for status updates for jobs started from the pendant and plays a short spoken update or LED pattern when a job completes, fails, or needs attention.
- must be on-device because: The pendant must react even when the phone/Mac is asleep or the network is flaky; local behavior (LED, audio cues, button interactions) must be implemented on-device.
- trigger: server push or periodic link-layer heartbeat when connected; optional button press to cycle through pending statuses.
- storage: Small ring buffer of pending job ids and the last status message, stored in local flash.
- RAM budget: Very small; keep active state to a few entries and reuse buffers to fit within constrained RAM.

## Its own summary

Recorded three new owner-facing capabilities: (1) spoken blocker clarification that pauses and resumes the exact Mac workflow, (2) priority preemption of a running workflow with checkpointed resume, and (3) capability-aware splitting of browser/Mac tasks so browser work proceeds while the Mac is offline. Also recorded a concrete relay stage-ledger/lease protocol to make the third capability reliable, idempotent, and truthful across surfaces.

**Biggest unknown:** Whether the existing job/pipeline executors can persist and enforce per-action idempotency and checkpoints; the observed routes expose jobs and receipts, but not an end-to-end durable stage runner or cross-surface lease.

