# Harness derivation — relay-realtime — round 233

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Take care of this until it is actually finished; if you get stuck, ask me one precise question.""
- **useful because:** Today a delegated Mac task is effectively a single job with a result. The owner cannot walk away while a multi-step browser/Mac workflow survives partial completion, records exactly what changed, and resumes after an answer. A durable saga would make the pendant a real remote operator rather than a one-shot voice remote.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to capture the goal and speak a question; use the cheaper planner/background workers for each checkpointed step.
- **latency:** Acknowledge in under 2 seconds; individual steps may take minutes, with a spoken or dashboard update only at checkpoints or when blocked.
- **cost:** About one realtime turn for intake, then roughly one planner call per checkpoint; cost is dominated by repeated computer-use screenshots and browser operations, not the relay acknowledgement.
- **security:** The saga can mutate many applications and may contain private browser state. Persist only action summaries and opaque session references, encrypt checkpoint data, and require explicit owner answers for irreversible or ambiguous branches; reversible actions can follow the owner's existing maximum-access policy.
- **missing:** A durable saga/state-machine record distinct from the existing one-shot job; Planner checkpoint and compensation/resume protocol across mac-planner, mac-vision, and browser-extension; A relay question inbox that can pause a saga and deliver one targeted question through the pendant; Dashboard visualization of checkpoint, pending question, and exact receipts

### ""If I say the emergency phrase, get me help and keep trying until a real person acknowledges it.""
- **useful because:** The worn pendant is the one surface available when the owner is away from the Mac, but today it cannot escalate beyond a relay conversation. A deliberate emergency phrase plus a physical confirmation could fan out through the relay, phone, and Mac, retrying delivery and telling the owner whether a human acknowledged it.
- **path:** pendant → relay → iOS → mac-planner → dashboard
- **model tier:** Use deterministic phrase/button recognition and a durable background escalation worker; no expensive realtime reasoning should sit in the critical path.
- **latency:** Local confirmation immediately, first delivery attempt under 5 seconds, retries and acknowledgement tracking for hours.
- **cost:** Low model cost; telephony/SMS/push provider fees and an always-on durable worker dominate.
- **security:** False positives and abuse are serious. Require a configured phrase plus deliberate button pattern, local audible/LED confirmation with a cancel window, encrypted emergency contacts and location, strict audit logs, and never expose contacts or location in normal transcripts.
- **missing:** A configured emergency-contact and location consent store; iOS push/SMS/voice-call integration and delivery receipts; Durable escalation timers/retries and human-acknowledgement protocol; Firmware emergency gesture that survives a dropped LTE/Mac link and an operator dashboard

### ""Don't interrupt me while I'm presenting or recording; if something urgent arrives, tell me at the first safe moment.""
- **useful because:** The owner currently has no shared notion of attention across the worn pendant, Mac audio/apps, browser, and relay. Notifications can arrive while they are presenting, recording in Ableton, or speaking with someone, and the pendant cannot defer or prioritize them based on real activity. This would make the system helpful without becoming an interruption source.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic state collection and a cheap classifier for urgency; reserve realtime for the one-sentence alert when the safe window opens.
- **latency:** State refresh within 2 seconds; urgent events evaluated in under 5 seconds; deferred alerts delivered at the first detected safe window.
- **cost:** Low model cost if activity signals are structured; most work is event ingestion and a small durable deferred-notification queue.
- **security:** Activity state reveals meetings, applications, and possibly document titles. Keep raw titles on the Mac, send only coarse states (presenting, recording, focused, idle), make urgency rules owner-editable, and provide an unmistakable cancel/snooze gesture.
- **missing:** A Mac activity/privacy adapter for microphone, camera/presentation, Ableton recording, calls, and focused-app state; A shared relay attention-state and deferred-alert queue with coalescing and expiry; Browser and Mac event subscriptions rather than periodic polling alone; Firmware behavior for quiet/deferred/unread urgency using the existing inbox and LED semantics


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: durable checkpointed multi-agent sagas with precise questions, emergency escalation with human acknowledgement, and attention-aware deferred interruptions. A browser draft/resume idea was rejected as a duplicate of an existing backlog item, so I did not rephrase it. I do not need another tool this round; these proposals explicitly identify the missing durable orchestration, escalation integrations, activity adapters, and cross-surface event queues.

**Biggest unknown:** Whether the existing watches/ops routes can already support the proposed attention and emergency event semantics; the recorder flagged them as not inventoried rather than confirmed absent.

