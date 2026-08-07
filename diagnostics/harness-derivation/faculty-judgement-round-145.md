# Harness derivation — faculty-judgement — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep your answer private right now.” Automatically detect that I’m in a call, in a public place, or that audio would be unsafe, then stop spoken output, route the answer to my Mac/browser, and give only a discreet pendant cue; restore voice when I explicitly say it’s safe."
- **useful because:** The assistant becomes usable on a train, in a meeting, or beside another person without embarrassing leaks. It coordinates the wearable’s physical presence with the Mac’s call/browser state instead of guessing from one surface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short safety classification and cue; background model for environment evidence reconciliation.
- **latency:** Privacy cue under 500 ms; screen fallback under 2 s; no model call when a deterministic call/focus signal is sufficient.
- **cost:** Usually near-zero model cost; occasional realtime classification roughly $0.001–$0.01, dominated by audio processing.
- **security:** Ambient audio must not leave the device merely to classify privacy. Prefer local button state, Mac call/focus state, and audio-route metadata; require explicit opt-in for ambient classification. Never transmit the answer to a third-party display.
- **missing:** A typed privacy-state protocol shared by pendant, relay, and Mac; Local pendant cue/voice-output inhibit firmware behavior; Mac/browser signals for active call, focus, and current audio route; A durable user-visible privacy mode state and recovery after link loss

### "“Talk me through this, but don’t take over.” Inspect the page or app I’m looking at, give me one safe step at a time through the pendant, wait for my spoken confirmation, and recover if what I see no longer matches."
- **useful because:** It gives the owner the practical benefit of computer use even when automation is unavailable or undesirable: the owner retains control, while the browser’s private session and the pendant’s hands-free guidance work together.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background model extracts page structure; realtime model handles the single next instruction and confirmation.
- **latency:** First instruction under 3 s; each subsequent step under 1 s after confirmation.
- **cost:** About $0.002–$0.03 per step depending on screenshot/vision use; browser DOM extraction dominates, not text generation.
- **security:** Private page content stays in the authenticated browser path and is minimized before model use. Never click, submit, or send; confirmation means only ‘advance to next instruction,’ not permission for an irreversible action.
- **missing:** A read-only cross-app observation contract for browser and Mac; A step state machine with visual/DOM preconditions and mismatch recovery; Pendant confirmation/cancel gesture and spoken prompt queue; A way to expose current app context without Accessibility, with vision as optional enhancement

### "“Audit whether that really happened.” Check the relay record, Mac receipt, browser result, and—when tethered—the pendant’s serial event, then tell me in one sentence what is proven, what is only claimed, and what needs retrying."
- **useful because:** Today a route can report success while the UI did nothing or telemetry is stale. This gives the owner an honest answer before they rely on a missed reminder, unsent form, or supposedly completed task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model reconciles structured evidence; realtime is used only when the owner asks interactively.
- **latency:** Under 2 s for existing receipts; under 8 s when a serial or browser re-check is required.
- **cost:** Typically <$0.005 per audit; cost is dominated by a live re-check or screenshot, not synthesis.
- **security:** Evidence is scoped to the referenced job and redacted by field sensitivity. Never infer completion from a stale ‘processing’ event. Retrying an action requires a separate explicit confirmation if it could duplicate or send anything.
- **missing:** A common evidence schema with source, timestamp, freshness, and proof strength; Live USB serial event reader for the tethered nRF9160; Independent browser result verification rather than optimistic command acknowledgment; A duplicate-safe retry planner and owner-facing proof receipt

### "“Give me the answer silently.” When I’m in a meeting, beside someone, or I press the pendant’s privacy control, continue the conversation without speech: deliver a compact vibration/LED code for urgency and answer availability, while putting the full response on my Mac for reading and letting me reply with a button sequence or typed text."
- **useful because:** The owner can use the assistant in places where speaking is socially or professionally unsafe, rather than having to abandon the interaction.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime for short response classification and cue selection; no expensive model for deterministic notification encoding.
- **latency:** Urgency cue under 300 ms; full Mac response under 2 s; button acknowledgment under 500 ms.
- **cost:** Near-zero incremental model cost; dominated by ordinary response generation.
- **security:** No answer audio may be emitted while silent mode is active. Full text stays on the owner’s authenticated Mac; vibration patterns must not encode secrets in a way an observer can infer beyond urgency.
- **missing:** A haptic actuator and documented vibration patterns on the pendant; A bidirectional silent-mode protocol with durable state and timeout; Mac delivery surface that binds the response to the active voice session; Firmware button-sequence input and acknowledgement events

### "“Translate this conversation for me privately.” Use the pendant microphone and audio bridge for short utterances, translate them through the relay, show the transcript/translation on the Mac, and optionally speak only my translated reply after I approve it; keep a local rolling buffer so a dropped link does not lose the last exchange."
- **useful because:** The owner gets a hands-free travel and accessibility aid that combines the wearable’s proximity to speech, the Mac’s readable display, and the relay’s language capability without forcing an entire conversation into a cloud recording.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime speech translation for low latency; background model only for terminology correction or a saved transcript the owner explicitly requests.
- **latency:** Under 1.5 s for a short utterance; degrade to local transcript queue when disconnected.
- **cost:** Roughly $0.01–$0.08 per minute depending on audio and translation model; storage and transport are minor.
- **security:** Explicit per-session consent; default to no retention and no speaker identification. Encrypt the rolling buffer and erase it after successful delivery or a short TTL. Never auto-speak a translated reply without approval.
- **missing:** End-to-end 16/24 kHz audio format negotiation and bridge buffering; Translation session state shared by pendant, relay, and Mac; Offline encrypted rolling buffer with bounded flash use; An approval control that distinguishes display from speech output


## Changes it proposed to its own stack

### `integration` — Add a cross-surface privacy-state arbiter. It consumes deterministic Mac call/focus/audio-route state, browser heartbeat/session state, relay delivery state, and a pendant local privacy latch; emits one signed state (safe, discreet-only, blocked, unknown) with expiry. Every output route must consult it, and unknown must fail closed to discreet cue rather than spoken audio.
- **owner gets:** The owner can use the assistant around other people without accidentally broadcasting private answers.
- effort: Medium: typed state contract, adapters for existing status routes, relay enforcement, and a small pendant command.  ·  risk: A false positive suppresses speech; recover with a physical long press or explicit ‘voice is safe’ command. A stale state must expire rather than silently persist.
- cost: Negligible API cost; one small relay state record. Firmware change is under a few KB.  ·  latency: <100 ms for cached state; no model round trip.
- security: Improves confidentiality; fail-closed behavior may reduce availability. Do not upload ambient audio for classification.
- depends on: Local privacy latch firmware; Mac call/focus/audio-route status adapter; Signed privacy-state message consumed by audio delivery

### `interaction` — Build a read-only guided-step protocol: browser/Mac observers return a normalized current target, allowed next action, and precondition hash; relay speaks exactly one instruction; pendant button or spoken ‘done/cancel’ advances; observer rechecks the hash before every step and explains mismatch instead of acting.
- **owner gets:** The owner gets hands-free help with unfamiliar sites while keeping their own hands and authority in control, even when Accessibility automation is unavailable.
- effort: Medium-high: observer normalization, step/session persistence, pendant confirmation event, and mismatch UX.  ·  risk: Bad guidance can waste time; no step may mutate state, and a cancel/timeout must end the session. Recovery is to show the current page and restart from a fresh observation.
- cost: Low background model cost; vision/screenshot steps may cost $0.01–$0.05 each.  ·  latency: First step 2–3 s, later steps <1 s with cached DOM evidence.
- security: Read-only by construction; private page fields must be redacted before model calls.
- depends on: Cross-app observation route; Pendant confirmation/cancel event; Browser and Mac precondition hashes

### `relay` — Create an evidence ledger that joins job receipts, journal entries, browser results, pipeline events, and tethered pendant serial events by correlation ID. Each claim gets source, observedAt, freshness TTL, proof level (intent/accepted/executed/verified), and contradiction markers; expose an audit endpoint and prohibit ‘completed’ language unless verified evidence exists.
- **owner gets:** When the system says something is done, the owner can trust it—or immediately see the exact missing proof and safely retry.
- effort: High: schema, ingestion adapters, serial parser, verification probes, and duplicate-safe retry integration.  ·  risk: Missing or delayed telemetry may make successful work look uncertain; preserve raw evidence and permit a live recheck. Never auto-retry irreversible actions.
- cost: Small D1/R2 storage and occasional browser/serial rechecks; <$0.01 typical audit.  ·  latency: Existing audits <2 s; live verification can take several seconds.
- security: Evidence must inherit field sensitivity and be access-controlled; raw serial/audio data should expire quickly.
- depends on: USB serial event reader; Stable correlation IDs across relay/Mac/browser; Independent browser verification route; Proof-aware response renderer

### `hardware` — Add a low-current coin vibration motor (or equivalent haptic actuator with a protected driver) to the pendant revision, exposed as a three-level intensity and short-pattern API alongside the existing button and LED. Reserve a local fail-safe path so privacy and cancel cues work with no relay connection.
- **owner gets:** They gain a genuinely discreet channel for alerts, acknowledgements, and private interaction in meetings, transit, and shared rooms where audio is unusable.
- effort: Hardware revision, driver/transistor, enclosure and current-budget validation, then a small firmware API and pattern test suite.  ·  risk: Added power draw, vibration noise, and mechanical wear; cap duty cycle, provide LED-only fallback, and make patterns user-configurable. A failed driver must not block normal audio or button use.
- cost: Approximately $1–$4 in parts and PCB/enclosure changes; brief 10–30 mA pulses, with negligible idle draw.  ·  latency: Local cue latency can be below 50 ms; no network dependency.
- security: Positive for privacy because cues can replace spoken output; avoid patterns that reveal message content to bystanders.
- depends on: Pendant enclosure/PCB revision; Firmware pattern API; Cross-surface silent-mode protocol


## What it asked for

_Nothing._
## Its own summary

Round 145 produced three new owner-facing capabilities and three implementation changes. The highest-value one is “Audit whether that really happened”: reconcile relay/Mac/browser/USB evidence and distinguish intent, accepted, executed, and independently verified instead of trusting optimistic success. I also recorded privacy-safe modality switching (fail closed to discreet output in calls/public settings) and read-only, hands-free guided browsing where the owner performs every step. The corresponding missing work is connective: a signed privacy-state arbiter, a precondition-hashed guidance protocol, and a correlation-based evidence ledger with a live USB serial reader and independent browser verification. I did not re-request denied TCC grants or previously queued tools.

**Biggest unknown:** Whether the newly granted/orchestrated cross-surface primitives actually exist in the live backend this round: especially a pendant USB serial reader/event schema, authoritative Mac call/audio-route signals, and independent browser verification. The capability recorder accepted all proposals, but these dependencies remain unimplemented rather than available today.

