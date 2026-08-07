# Harness derivation — relay-realtime — round 59

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While you are carrying out a long request, let me interrupt naturally from the pendant and immediately change or cancel it; keep listening through the interruption and tell me exactly what happened."
- **useful because:** Today a spoken correction can be lost or arrive after a queued Mac/browser job has already completed. A wearable owner needs conversational control while away from the Mac: barge-in should stop stale work, preserve the useful partial result, and avoid duplicate actions.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles VAD, interruption detection, and a short acknowledgement; relay/job orchestration and receipt summarization use a cheaper background model. Mac-planner/mac-vision/browser-extension receive a cancellation or supersession signal and return a typed partial receipt.
- **latency:** Local audio interruption detection under 150 ms; pendant acknowledgement under 500 ms; downstream cancellation attempt within 1 s, with a spoken fallback if the action cannot be stopped. 24 kHz superwideband audio should remain full duplex during listening and speech playback, with ducking rather than hard mute.
- **cost:** About $0.001–$0.01 per interruption depending on realtime audio duration; dominant cost is the additional realtime audio turn and receipt summarization, not the cancellation signal.
- **security:** An accidental sound must not cancel or supersede a consequential action without being recognized as the owner's speech. The relay should bind interruption to the active job/session, record an immutable cancellation/supersession receipt, and disclose when a remote action was already irreversible. Audio/transcript leaves the pendant only for the active session and should expire with it.
- **missing:** Pendant firmware full-duplex 24 kHz audio with robust barge-in/VAD and an interruption event that survives playback; Relay active-turn state machine with cancel/supersede tokens and audio ducking/interruption semantics; A common cancellation/status protocol implemented by mac-planner, mac-vision, and browser-extension, including partial-result receipts; Job runner support for cooperative cancellation and explicit 'already committed' boundaries; End-to-end interruption tests under LTE-M jitter, packet loss, and dropped Mac/browser links

### "If LTE drops while you are working, let me reconnect later and say “continue” or ask a follow-up without repeating myself; give me a trustworthy summary of what was heard, what ran, and what still needs doing."
- **useful because:** A worn device will routinely cross dead zones. Today a dropped voice link can strand the owner's request or make them repeat it, risking duplicate Mac/browser actions. Durable, replay-safe conversational recovery would make the pendant dependable rather than a best-effort intercom.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Relay realtime handles only reconnection greeting and short state selection. A cheaper background model compacts the interrupted transcript and action receipts into a bounded resume card; downstream agents provide authoritative job state rather than the model guessing.
- **latency:** Persist each utterance and action transition before acknowledgement (under 200 ms target); on reconnect, resume card spoken within 1.5 s. Duplicate suppression must be immediate even if the owner reconnects from a second session.
- **cost:** Roughly $0.001–$0.02 per disrupted session, dominated by one compacted resume summary; durable metadata and replay checks are negligible.
- **security:** Resume data contains spoken content and possibly authenticated browser results. Encrypt it, bind it to the owner's device/session, expire completed cards, and never replay an action merely because an audio packet was retried. The owner should hear whether a command was accepted, started, committed, or unknown.
- **missing:** Durable per-turn journal on the relay with idempotency keys and a bounded encrypted resume-card store; Pendant reconnect handshake that reports session identity and asks whether to resume, discard, or start fresh; Downstream agents' authoritative state transitions and idempotent execution for Mac and browser jobs; A reconciliation endpoint that compares relay intent, agent execution, and receipts after a partition; Dashboard view and tests for LTE loss, duplicate packets, reconnect during irreversible work, and concurrent sessions

### "Just tell me to do something once—like look up a page, save a note, or open a document—and have the hive choose the best reachable surface, move the task between relay, browser, and Mac if one disappears, and report one combined result instead of making me know which device is online."
- **useful because:** The pendant is worn away from the Mac, browser sessions may be authenticated while the Mac is asleep, and the relay is the only always-on node. Today routing is surface-specific and a failure can leave the owner guessing whether anything happened. Capability-aware failover would make one spoken request dependable without duplicate actions.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A cheap deterministic capability/health router selects and leases a surface; realtime only speaks the short acknowledgement. Background planning translates the same intent into the selected surface's typed operation and reconciles receipts. Realtime is not used to reason about the whole task.
- **latency:** Health/capability selection under 250 ms; acknowledgement under 500 ms; fallback launch within 2 s. Never silently launch a second mutation until the first surface's receipt is reconciled or explicitly marked unknown.
- **cost:** Usually under $0.005 per request; router and health checks are negligible, with model cost only for translating an intent that changes surfaces or summarizing conflicting receipts.
- **security:** Authenticated browser sessions and Mac data must not be copied to an alternate surface unless its declared scope permits it. Surface leases need device/session binding, replay keys, and expiry. For mutations, the owner should be told which surface acted and whether failover occurred.
- **missing:** A machine-readable capability/health registry for relay, Mac, and browser with freshness and data-scope declarations; Portable intent and typed-operation schemas with idempotency keys across all surfaces; A lease/reconciliation coordinator that handles offline, timeout, and unknown-commit states without duplicate mutations; Policy for which reads may fall back to server/browser and which data must remain on the Mac; Unified receipt format and dashboard trace showing attempted surfaces and final authority


## Changes it proposed to its own stack

### `hardware` — Add a low-power haptic actuator and an audio-path interrupt line to the pendant, alongside the existing single button/LED. Firmware should expose short patterns for listening, accepted, completed, failed, and remote-cancelled states, and a hardware-level barge-in event that can preempt speaker playback even when the LTE link is impaired.
- **owner gets:** The owner can use the pendant discreetly in public or noisy places without staring at it: they feel that a request was accepted, that a remote Mac/browser action finished, or that it failed. A tactile barge-in cue also makes interruption reliable when speech is masked by the speaker or surroundings.
- effort: Hardware revision, enclosure/acoustic redesign, firmware driver and power policy, relay event mapping, and end-to-end field testing. Prototype in 2–4 weeks; production integration longer.  ·  risk: Added vibration can be audible or uncomfortable and may reduce battery life. Provide intensity/off settings, rate-limit patterns, and retain LED/audio fallback. A spurious interrupt must only pause local playback; it must not cancel a downstream action without a separately recognized command.
- cost: Approximately $1–$4 BOM increase for actuator, driver, and mechanical integration; brief 10–30 mA vibration pulses with negligible average draw if limited to status patterns. No meaningful API cost.  ·  latency: Local tactile acknowledgement can occur in tens of milliseconds, improving perceived response; no added network latency. Hardware preemption avoids waiting for a round trip.
- security: No new data needs to leave the device. Firmware updates must authenticate the pattern/event mapping so a malformed remote message cannot trigger arbitrary behavior.
- depends on: Relay active-turn and cancellation/supersession protocol; Pendant full-duplex audio/barge-in firmware design; A persisted, typed action receipt/state vocabulary shared by downstream agents


## What it asked for

_Nothing._
