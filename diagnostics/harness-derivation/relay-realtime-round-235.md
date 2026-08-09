# Harness derivation — relay-realtime — round 235

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with my devices right now?"
- **useful because:** Quick reassurance: pendant voice agent can report relay health, Mac bridge status, and whether the system is ready without requiring the Mac to be in front.
- **path:** relay → mac-bridge
- **model tier:** Realtime
- **latency:** Under a second; read-only status queries.
- **cost:** Very low; single health/status read.
- **security:** Status endpoints should avoid exposing secrets; redact tokens and internal configuration.
- **missing:** A standardized status summary endpoint for relay + mac bridge + device registration (pieces exist, but summary is not guaranteed)

### "Find the thing I asked for earlier and continue it."
- **useful because:** Lets the owner refer to past tasks naturally; the system can resolve the job and resume or report without them remembering IDs.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for the reference; mac-planner for the work if needed.
- **latency:** A few seconds when lookup is needed; longer only if the Mac must run a workflow.
- **cost:** Low for lookup; higher only when delegating to the Mac to continue work.
- **security:** Be careful not to reveal details of prior tasks without context; confirm before resuming high-impact actions.
- **missing:** Better job indexing and retrieval by natural-language reference; relay_job_status handles status but not continuation

### "“Take care of whatever is currently in this browser tab, and keep going even if I walk away.” The relay should read the authenticated Safari tab, infer the concrete task from my speech plus page state, have the Mac planner act across the browser and local apps, pause on an ambiguity, and resume after the Mac or browser reconnects without losing the task."
- **useful because:** Today the pendant can hand off a goal or a short action list, but it cannot turn the owner's private, already-authenticated page context into a durable, resumable job. This would make the worn device a real front door to work that spans browser sessions and Mac applications rather than merely a remote button.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay for intent capture and one-sentence clarification; gpt-5.6-luna mac-planner for planning and recovery; gpt-4.1-mini computer-use only when visual interaction is unavoidable; cheap background model for extracting page state and checking whether a paused job can safely resume.
- **latency:** Acknowledge in under 1 second, first page/task interpretation in 3-5 seconds, then background execution with spoken interruption available.
- **cost:** Roughly $0.02-$0.10 for a normal task; planner calls and screenshots dominate, while relay speech should remain one short turn.
- **security:** Authenticated page contents and any resulting local data leave the Mac only through the relay's task context. The system must bind the job to the captured tab/session, redact secrets from receipts, re-check page identity after reconnect, and never silently continue after a material page or target change. Reversible actions may proceed under owner policy; irreversible external sends or purchases still need an explicit spoken checkpoint.
- **missing:** A durable cross-surface job state machine with checkpointed browser identity, planner state, and reconnect recovery; A relay endpoint that can capture the current Safari tab and attach it to POST /plan rather than requiring a manually authored action list; Mac-side lease/heartbeat and safe resume semantics for jobs when the Mac or browser goes offline; A compact pendant interaction for answering an ambiguity and cancelling or resuming a paused job

### "“Privacy curtain.” The pendant should immediately stop using browser-page context, cancel or suspend active computer-use jobs, clear transient spoken-task context from the relay, and tell me when the curtain is active; saying “resume” or a deliberate button gesture should restore normal operation."
- **useful because:** The owner wears the microphone away from the screen and may enter a sensitive conversation without being able to reach the Mac. There is currently no single, obvious physical or spoken action that makes the whole hive stop looking at private pages or continuing a job. This is a user-visible privacy control, not a tidying refactor.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive model is needed for activation: firmware event plus deterministic relay state. Use the realtime tier only to acknowledge; downstream agents consume a signed privacy-state event and stop immediately.
- **latency:** The pendant LED/acknowledgement in under 250 ms and downstream cancellation in under 1 second.
- **cost:** Negligible per invocation; this is mostly firmware and relay state propagation, not inference.
- **security:** The curtain must be fail-closed on relay uncertainty, survive a dropped Mac link, and be visible in the dashboard. It should revoke browser inspection and job continuation leases, prevent new memory projection of browser findings, and avoid claiming that already-uploaded data was erased. Resume must require a deliberate physical gesture or an unambiguous spoken command after the owner knows the state.
- **missing:** A relay-wide privacy epoch/token checked by browser and Mac agents before every read or action; Cancellation and lease revocation semantics in the job executor, including a truthful stopped-versus-unreachable receipt; A firmware gesture/state for curtain active that does not conflict with recording and inbox playback; A browser-extension hook that blocks page capture and clears its transient command context

### "“Use the other account,” or “No, put it in Downloads instead.” While a Mac/browser job is running, the pendant should let me correct one parameter by voice, identify which active job I mean, validate the change against the current step, and continue without restarting the whole task."
- **useful because:** Long computer tasks fail today at the first wrong assumption: the owner must wait, cancel, and explain the entire goal again. A wearable is uniquely suited to low-latency steering while the owner is away from the Mac. This is not a completion notification; it changes an in-flight plan safely and preserves its progress.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay resolves the utterance to the active job and extracts a small patch; gpt-5.6-luna evaluates the patch against the planner state and replans only the remaining steps. Use a cheap classifier for whether the utterance is a steering correction, a new task, or a cancellation.
- **latency:** Acknowledge the correction in under 1 second, show the affected step in under 3 seconds, and resume within 5 seconds when the patch is unambiguous.
- **cost:** About $0.01-$0.05 per correction, dominated by a targeted planner re-evaluation rather than a full task restart.
- **security:** Never apply an ambiguous correction to the wrong job. The relay should speak back the selected job and changed target when needed, preserve an immutable before/after plan diff, and stop at an external-send boundary if the correction materially changes who receives data. The owner policy permits reversible actions without an extra gate, but the system must truthfully report if the job was already past the affected step.
- **missing:** An active-job registry exposed to the realtime relay with owner-facing short names and current step; A versioned planner state plus patch/replan API; current plan/execute is effectively one-shot from this surface; A pendant protocol for a correction response and a compact disambiguation prompt; Receipts that distinguish applied, superseded, too-late, and rejected steering patches


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) a durable “take care of this authenticated browser task” workflow spanning pendant, Safari, relay, and Mac with reconnect recovery; (2) a physical/privacy curtain that immediately revokes page context and active computer jobs; and (3) voice steering of an in-flight Mac/browser job without restarting it. The recorder noted that each is connective work over existing routes, so the real missing work is the state/lease/checkpoint layer between them—not another endpoint or another notification queue.

**Biggest unknown:** Whether the existing planner/executor already has an unobserved versioned plan state and cancellation lease. If it does not, that is the central prerequisite for both resumable browser work and mid-job voice steering; if it does, the next implementation should expose those controls to the relay and pendant.

