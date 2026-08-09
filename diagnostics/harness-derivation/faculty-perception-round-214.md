# Harness derivation — faculty-perception — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS control and browser perception are now live** — At 2026-08-09T00:16:32Z the exact AI Pendant Agent identity is Accessibility-trusted, Screen Recording-granted, inputReachability=verified, and uiActionsWillReachTheScreen=true; Safari browser bridge is online with four durable sessions and zero pending commands. This is Mac/browser truth only: no pendant is registered.
  - evidence: GET /observe HTTP 200: accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, eventsPost=true, browser.sessions=4; device discovery lists only home-macbook-bridge online and cloudflare-contract-test offline.

## Capabilities it proposed

### "“When I ask what happened, show me only actions you can prove: what the Mac changed, what the browser changed, what the relay accepted, and whether the pendant actually played it.”"
- **useful because:** Today 'completed' can mean only that the Mac ran; browser evidence and relay delivery are separate, and no playback acknowledgement exists. This gives the owner a claim-level truth report instead of a plausible narrative, explicitly separating observed, socket-delivered, and physically-heard.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for assembling the evidence ledger; realtime only to speak the short result
- **latency:** Under 2 seconds for a recent job; up to 8 seconds when joining browser provenance and historical receipts
- **cost:** Low: one background aggregation and a short realtime utterance; dominated by context transfer, not generation
- **security:** Expose only redacted capsule claims and action summaries, never page bodies or secrets. Require confirmation before showing sensitive before/after values. If the pendant has no playback event, say unknown rather than infer hearing.
- **missing:** Relay-to-Mac stable IDs and content hashes for cloud browser reads; A mounted browserProvenance route for claim joins; Firmware emission and relay consumption of the already-designed playback event

### "“If you did not hear me cleanly, do not execute anything—tell me exactly what was unclear and ask for a repeat, unless the request is harmless.”"
- **useful because:** A wearable can produce a transcript that looks valid while clipping, packet gaps, or noise changed the intent. The pendant's local quality sentinel can catch unusable speech before cloud interpretation, while the Mac can detect whether a meeting/call or noisy audio context makes a repeat safer. This prevents the most expensive failure: a confident action on corrupted speech.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime for the one-turn repeat decision; no background model unless the owner asks for quality trends
- **latency:** Local verdict in under 150 ms at utterance end; repeat prompt within 1 second; no cloud round-trip for clearly unusable audio
- **cost:** Near-zero for clean audio; one short realtime turn only for degraded/ambiguous samples
- **security:** Send only quality metrics and a transcript candidate, not raw audio by default. Never allow a degraded utterance to trigger destructive actions. The owner can opt into harmless actions proceeding on degraded audio.
- **missing:** Relay policy that gates tool execution on the sentinel verdict; Mac-side ambient/app context adapter (meeting, call, volume, input route); A durable quality trend view without retaining raw speech

### "“While I am away from the pendant, prepare things but do not send, buy, delete, or publish; when I reconnect, give me the queue and let one button tap release each item.”"
- **useful because:** The Mac and browser can keep working while the owner is absent, but confirmation-sensitive work currently depends on conversational timing. A physical return-to-presence signal gives the system a hard boundary: research and drafts continue, irreversible effects wait, and the owner can release exactly one prepared operation rather than trusting a stale voice turn.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background models prepare drafts and previews; realtime only presents the pending queue when the pendant returns
- **latency:** Queueing is immediate; reconnect summary under 3 seconds; each release should show a concise preview before execution
- **cost:** Low to moderate: background planning dominates; no model call for simple hold/release; one realtime turn for the return briefing
- **security:** The pendant's reconnect/physical button must be authenticated and replay-resistant. Treat disconnect as fail-closed only for confirmation-sensitive operations, not as proof the owner is absent. Keep drafts local where possible; require explicit per-item release for mail, deletion, purchases, and publishing.
- **missing:** A relay/mac 'held for presence' job state and durable queue; A signed pendant presence/reconnect event and one-shot release token; Browser and Mac action planners must honor the hold state before dispatch

### "“Private mode now.”"
- **useful because:** The owner needs a physical, unmistakable way to stop the hive from listening, reading, or acting across every surface—not merely mute the current audio stream. A pendant gesture should immediately close the capture window, suspend relay transcription and queued announcements, pause browser observation, and prevent Mac actions until the owner explicitly exits private mode.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model for entering or enforcing the mode; realtime only confirms the state when the owner asks
- **latency:** Local audio cutoff under 100 ms; relay and Mac/browser enforcement under 1 second; visible dashboard state must converge within 2 seconds
- **cost:** Negligible runtime cost; occasional heartbeat/state propagation dominates
- **security:** The pendant must enforce the first barrier offline, with a latched physical indicator and monotonic state counter. Fail closed on ambiguous link state. Do not rely on a spoken command to exit; require the same deliberate gesture plus an audible/visual confirmation. Existing stored audio and browser capsules are not retroactively erased without a separate owner command.
- **missing:** An offline pendant privacy latch and authenticated state-change event; Relay-wide privacy gate checked by realtime, announcements, routines, and jobs; Mac/browser adapters that stop observation and reject new commands while latched

### "“I think this account or session is compromised—lock the hive down.”"
- **useful because:** Today the owner would have to remember which relay jobs, browser commands, Mac jobs, and device credentials to revoke. One spoken/physical emergency action should stop new work everywhere, cancel pending browser and Mac operations, invalidate device/session tokens, and leave a durable incident receipt without deleting evidence.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only to authenticate and confirm the emergency command; deterministic policy and background cleanup do the containment
- **latency:** Reject new actions within 250 ms at the relay; cancel/disable Mac and browser work within 2 seconds; produce a containment receipt within 5 seconds
- **cost:** Low: deterministic fan-out and one short confirmation; no expensive model needed
- **security:** This is intentionally destructive to in-flight work and must require a physical pendant gesture or a pre-authorized emergency phrase plus a second confirmation. Preserve immutable audit metadata, redact secrets, rotate only scoped credentials, and provide an offline recovery code so a relay outage does not trap the owner.
- **missing:** Relay kill-switch state checked by every action/job/browser route; A device/session credential rotation and revocation endpoint; Mac and extension listeners that cancel pending commands and refuse new ones; A pendant-local emergency state and authenticated replay-resistant event

### "“If the Mac disappears during a task, keep the conversation alive and finish safely when it returns—without repeating anything.”"
- **useful because:** The relay can stay awake while the Mac bridge vanishes, but today a mid-task disconnect leaves ambiguous state: a browser click or file change may have happened without a trustworthy continuation. A resumable handoff would freeze the exact step, preserve idempotency keys and preconditions, tell the owner what is known, and resume only after the Mac reports the same task lease.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model summarizes the handoff; realtime speaks only the immediate interruption and recovery notice; deterministic leases/idempotency govern execution
- **latency:** Detect bridge loss within 2 seconds; speak status within 3 seconds; resume within 5 seconds of reconnection after precondition checks
- **cost:** Low to moderate: state storage and reconciliation dominate; model use is a short summary, not every retry
- **security:** Never replay a side effect merely because a job was incomplete. Persist per-step idempotency keys, before-state hashes, and a lease owner; require confirmation when post-state cannot be proven. Encrypt handoff contents because browser and file context may be sensitive.
- **missing:** Relay durable task leases and per-step idempotency/precondition protocol; Mac bridge reconnect handshake that reports completed step receipts and post-state hashes; Browser command cancellation/reconciliation semantics; Pendant-visible offline interruption and recovery events


## What it asked for

_Nothing._
## Its own summary

Round 214 established a major change: the Mac agent now has verified Accessibility, Screen Recording, and input reachability, and Safari has four live durable sessions with no pending commands. The pendant is still absent from the relay registry, so pendant behavior remains unverified. I recorded that fact and proposed three distinct owner-facing capabilities: claim-level proof of actions/hearing, quality-gated execution that refuses corrupted speech, and a physical-presence release queue that holds irreversible work while the owner is away.

**Biggest unknown:** Whether the physical nRF9160/ESP32 pair can now be connected and made to emit authenticated presence, capture-quality, and playback events; until a pendant registers, relay delivery and actual hearing remain unknown.

