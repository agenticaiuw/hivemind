# Harness derivation — faculty-judgement — round 12

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Don’t interrupt me unless it’s important; if I’m busy, queue it and tell me at the right moment.”"
- **useful because:** The pendant becomes considerate rather than merely loud: urgent changes reach the owner, while routine mail, job completions, and watch events wait for a safe conversational opening. It uses the wearable’s presence, the Mac’s current work state, browser task state, and the always-awake relay together—something no single surface can judge reliably.
- **path:** pendant: captures a local quiet/urgent override and delivers a one-sentence alert or haptic cue → relay: maintains the durable notification queue, deadlines, deduplication, and escalation while the Mac sleeps → mac-planner: reports coarse foreground-app/focus/meeting state and classifies whether an item truly needs interruption → browser: contributes authenticated page-watch urgency and evidence links without exposing page contents to the pendant → dashboard: lets the owner inspect, reprioritize, snooze, or replay queued items
- **model tier:** A cheap background model/rules engine classifies urgency and likely interruptibility; gpt-5.6-luna is used only for ambiguous prioritization or a requested digest; realtime is reserved for the final low-latency spoken delivery.
- **latency:** Urgent alerts should arrive within 2 seconds of a relay event; routine items may wait for the next inferred break (up to 30 minutes) and must expire rather than nag. A spoken “quiet until 3” override should take effect immediately.
- **cost:** Roughly $0.001–$0.01 per queued event, dominated by occasional classification; most events use deterministic rules and no model call. Delivery uses the existing realtime session, so there is no extra generation cost when already connected.
- **security:** Send only coarse state (focus/busy/meeting, not keystrokes or screenshots) and event metadata; keep authenticated page evidence on the Mac/browser unless the owner asks to hear it. No destructive action is taken. Creating or changing an external reminder still follows the owner’s existing confirmation policy; snooze/queue changes are reversible.
- **missing:** A shared event envelope with urgency, expiry, provenance, and sensitivity; A relay-side durable notification queue with dedupe and escalation rules; A Mac/browser interruptibility signal API that reports coarse state only; Pendant delivery semantics for haptic versus spoken alerts and an offline queue; A small owner policy surface for quiet windows, VIP sources, and escalation thresholds

### "“If I walk away, pause anything that could change the world, and only resume it when I’m back and the context is still valid.”"
- **useful because:** The owner can safely delegate multi-step work without worrying that a stale browser page, expired login, changed price, or unattended Mac will complete the wrong action. The pendant supplies real-world presence, the Mac and browser provide task state, and the relay preserves and revalidates the work while the owner is away.
- **path:** pendant: emits a privacy-preserving presence/return signal and gives a local pause/resume control → relay: freezes the job, records its exact checkpoint and expiry, and wakes it for revalidation when the owner returns → mac-planner: checkpoints the plan and verifies that files, app state, and assumptions are still current → browser: freezes authenticated tabs and rechecks URL, account, page fingerprint, and all irreversible fields before any continuation → dashboard: shows paused jobs, the reason they were held, what changed while away, and the exact next action requiring approval
- **model tier:** Deterministic state checks handle presence, lease expiry, page fingerprints, and checkpoint validation. gpt-5.6-luna is used only to explain changed assumptions or revise an ambiguous plan; realtime is used for the short return-time spoken summary.
- **latency:** Pause within 1 second of a reliable departure signal. On return, provide a brief status within 3 seconds, but never resume an irreversible step automatically; revalidation can take up to 10 seconds before presenting the owner with a confirmation.
- **cost:** Usually below $0.005 per pause/resume cycle, dominated by occasional model-based explanation. State checks and checkpoint storage are effectively negligible; browser revalidation is the main operational cost.
- **security:** Presence should be represented as a coarse local signal, not a location history. While away, no external side effects occur. On return, changed or destructive actions require explicit confirmation and show before/after evidence. Checkpoints may contain sensitive task data and must be encrypted with bounded retention.
- **missing:** Pendant presence and return events with reliability/uncertainty metadata; A resumable job lease and checkpoint protocol shared by relay, Mac, and browser; Browser page/account fingerprinting and stale-form invalidation; A return-time revalidation and approval UI; An explicit policy distinguishing safe reversible work from world-changing work


## Changes it proposed to its own stack

### `interaction` — Add an Interruptibility Broker shared by relay, pendant, Mac planner, and browser: every proactive event carries urgency, confidence, sensitivity, expiry, and evidence pointer; the broker combines that with coarse current-focus signals, applies owner-defined quiet windows, deduplicates related events, and selects immediate haptic, one-sentence speech, next-break digest, or silent expiry. Record the decision and reason so the owner can undo the policy or replay missed items.
- **owner gets:** The owner gets fewer badly timed interruptions and stops losing important results among harmless notifications; the system explains why it waited or interrupted.
- effort: Medium: typed event schema, relay persistence, Mac/browser state adapters, pendant delivery protocol, and dashboard controls.  ·  risk: A classifier could suppress something important or infer the wrong busy state. Mitigate with conservative urgent-source defaults, expiry warnings, a physical pendant override, and a visible missed-items queue; recover by replaying any suppressed event.
- cost: Low ongoing API cost; mostly rules, with model calls only for ambiguous urgency. Small storage and dashboard implementation cost.  ·  latency: Adds <100 ms for rule evaluation; model fallback may add 1–3 s only for ambiguous events. Urgent events bypass the fallback.
- security: Coarse activity metadata crosses surfaces; raw screen/audio/page content remains local unless explicitly needed for the event. Policy and decision logs should be sensitive and owner-visible only.
- depends on: A durable cross-surface event/job primitive; Mac and browser adapters that expose coarse focus state; Pendant haptic/audio delivery and offline buffering; Owner interruption preferences


## What it asked for

_Nothing._
