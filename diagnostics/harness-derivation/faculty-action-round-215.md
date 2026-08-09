# Harness derivation — faculty-action — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Send this form” (or “publish this change”) after I have described the intended action aloud."
- **useful because:** This is the system’s highest-value trustworthy action: the pendant carries the owner’s intent, the Mac/browser carries private sessions and form contents, relay coordinates, the owner physically approves a concise risk summary, and an independent verifier proves the specific postcondition. No single surface can safely do all of that.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Realtime only for the short spoken summary and approval dialogue; background/local models extract fields and plan the browser/Mac steps. Verification is deterministic/read-only.
- **latency:** Draft in under 5 s; approval summary under 1 s; execution may take up to 30 s with progress haptics; never claim success until verification returns.
- **cost:** About $0.01–$0.05 per ordinary invocation, dominated by planning and final spoken summary; browser/Mac execution and verification are local.
- **security:** The pendant receives only an opaque transaction ID, risk summary, expiry, and digest—not secrets or page contents. Require the existing physical approval latch for submission, short expiry, idempotency, and verify_operation_step against fresh browser state. If verification is unknown, report unknown and do not retry automatically.
- **missing:** A first-class composed transaction route that binds plan step IDs, executor receipts, approval nonce, and verifier evidence into one durable operation record.; A browser-side submit action that accepts an approved transaction digest without exposing credentials to the relay.; Owner policy data for which risk classes may be staged versus requiring approval (default conservatively).

### "“File this thought under [project/person], and remind me what I meant when I’m back at my Mac.”"
- **useful because:** A fleeting pendant utterance becomes a searchable, correctly filed workspace artifact rather than an undifferentiated audio memo. The pendant captures immediately, relay preserves it, Mac reads the owner’s existing notes/files, and the owner later receives a concise spoken callback with a link to the exact source.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-perception → faculty-action
- **model tier:** Small/background model for transcription cleanup, entity/project classification, and deduplication; realtime only for a one-sentence confirmation and later callback.
- **latency:** Capture acknowledgement under 500 ms; durable spool immediately; classification and filing within 60 s when Mac is online; callback can be on-demand or scheduled.
- **cost:** Roughly $0.002–$0.02 per memo, mainly transcription and classification; local file/Notes operations dominate no API cost.
- **security:** Store audio only on the existing failure-path SD queue when upload fails; otherwise retain a relay object with expiry. Never put secrets into the spoken confirmation. Show the destination and confidence; if classification is ambiguous, create an inbox draft rather than silently filing. Destructive moves/deletes require confirmation.
- **missing:** A typed semantic-capture command with destination selector, confidence, source checksum, and idempotency key.; A Mac filing adapter that can write Notes/files with a durable receipt and return the canonical artifact URL.; A later callback lookup keyed by source artifact ID, not by approximate transcript text.

### "“Start this job, and keep going even if my laptop or link disappears; tell me exactly where it stopped and let me resume.”"
- **useful because:** Long actions become dependable instead of silently abandoned: relay owns the durable plan, Mac executes only bounded steps, the pendant receives compact progress/outcome signals, and reconnection resumes only from an idempotent checkpoint. This lets the owner start work while walking away and still know what actually happened.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action → faculty-perception
- **model tier:** Cheap background planner for decomposition and checkpoint compaction; realtime only for owner edits, interruptions, and the final spoken status. Deterministic executor and verifier handle step state.
- **latency:** Acknowledge and persist the plan under 2 s; each checkpoint under 5 s after a step; reconnect reconciliation under 10 s; no false completion if the last step is unverified.
- **cost:** About $0.005–$0.03 per job, dominated by planning and reconciliation; local execution is otherwise free.
- **security:** Each step has an idempotency key, lease expiry, bounded retry count, and explicit side-effect class. Never replay an unknown side effect automatically. Require physical approval again when a lease expires or the planned target changes. Send only progress summaries and hashes to the pendant; retain sensitive content on Mac/browser.
- **missing:** A durable cross-surface checkpoint/lease protocol with step states pending, running, committed, failed, and unknown.; Executor receipts that include operation_id and step_id, plus a read-only verifier invocation before commit.; A reconnect reconciler that compares Mac/browser reality to the checkpoint and presents one safe resume/cancel choice.

### "“If I’m incapacitated or miss two check-ins, notify [specific person] with my last known status, but never send my location unless I explicitly enabled it.”"
- **useful because:** This gives the wearable a real safety role without making it an always-on tracker. The pendant detects missed check-ins locally, the relay handles timeouts while the Mac is absent, and the phone/contact surface sends a constrained notification only after the owner configured the policy.
- **path:** pendant → relay-realtime → iOS → mac-planner → faculty-judgement → faculty-action
- **model tier:** Deterministic firmware timer and relay policy; a cheap model may phrase the notification, but must not decide whether the safety policy fired.
- **latency:** Local check-in acknowledgement under 300 ms; relay escalation within 30 s of the configured deadline; delivery receipt within 2 min when cellular is available.
- **cost:** Low ongoing cost; roughly $0.001–$0.01 per escalation plus SMS/push provider fees. Battery impact is a periodic timer and tiny status packets.
- **security:** Opt-in only, explicit recipient and message preview, no location by default, encrypted status envelope, cancellation window, rate limits, and a physical pendant gesture to cancel a pending escalation. The system must distinguish “device offline” from “owner missed check-in” and never infer incapacitation from silence alone.
- **missing:** A pendant-resident signed check-in timer and cancellation state machine; A relay safety-policy evaluator with offline/unknown semantics and escalation deduplication; An iOS notification/contact delivery surface and owner-configurable recipient policy; A durable audit trail showing why an escalation fired or was suppressed

### "“When I get to the studio, quietly prepare the project brief and let me know it’s ready—don’t send or publish anything.”"
- **useful because:** The owner gets useful preparation at the moment it matters without turning the pendant into a surveillance device. A phone supplies opt-in coarse geofence context, the relay schedules reliably, and the Mac/browser gather private materials while the pendant only receives a compact ready signal.
- **path:** pendant → iOS → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Deterministic geofence and schedule logic; a background model summarizes and assembles the brief; realtime is unnecessary unless the owner asks a follow-up.
- **latency:** Arrival event to preparation start under 15 s; brief ready within 2 min for ordinary projects; no action if location freshness or consent is unknown.
- **cost:** Approximately $0.005–$0.03 per preparation, mostly summarization; iOS location and Mac/browser work are local or platform-costed.
- **security:** Coarse location only, no continuous history, explicit per-place consent, on-device geofence matching where possible, immediate expiry after preparation, and no outbound side effect. If location is stale, say unknown rather than triggering.
- **missing:** An iOS coarse-geofence event source with per-place consent and no location-history export; A relay trigger that binds one arrival event to one expiring preparation job; A workspace/project resolver that can gather only the owner-approved folders and browser sessions; A pendant privacy indicator and one-gesture disable for the current place

### "“Give Alex permission to approve only this one purchase draft until 6 PM, and show me when Alex uses it.”"
- **useful because:** The owner can delegate a narrowly bounded decision without handing over account access or making the assistant omnipotent. Relay issues a single-purpose capability, the browser/Mac performs the action, and the pendant reports issuance, use, expiry, and revocation.
- **path:** pendant → relay-realtime → iOS → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Deterministic capability-token and policy evaluation; a model may explain the scope in plain language but cannot widen it.
- **latency:** Issue/revoke under 2 s; recipient notification under 10 s; action verification under 30 s; expiry is enforced even if the Mac was offline.
- **cost:** Roughly $0.005–$0.02 per delegation, dominated by notification and any short explanation generation.
- **security:** Single operation digest, recipient-bound public key or verified contact, absolute expiry, one use, no credential sharing, no delegation onward, revocation, replay protection, and independent postcondition verification. The pendant must show only a redacted scope summary.
- **missing:** A capability-token service with recipient binding, one-use counters, expiry, revocation, and audit events; An iOS contact-verification/notification surface; Executor enforcement that checks the token against the exact browser/Mac operation digest; A policy language for allowed risk classes and a clear owner-visible delegation history


## Changes it proposed to its own stack

### `hardware` — Add a low-profile detented rotary encoder with integrated push switch to the jewellery enclosure, wire it to two interrupt-capable GPIOs plus one button input, and expose a firmware event stream for rotate, press, and press-and-hold. Keep sw0/sw1 semantics unchanged; use the encoder as selection/navigation for pending actions, destinations, and repeat-last-response.
- **owner gets:** The owner currently has many possible actions but no safe way to select among them without inventing more long-press gestures. A wheel makes the pendant usable one-handed and lets it distinguish “which action?” before the owner approves it.
- effort: Medium hardware/firmware integration: select a debounced encoder, prototype GPIO wiring, add ISR/debounce/state machine, update enclosure and haptic language, then bench-test accidental-rotation and approval flows.  ·  risk: Bounce, accidental rotation in clothing, and cramped jewellery ergonomics. Mitigate with detent thresholds, a short interaction timeout, haptic tick feedback, and requiring the existing deliberate approval gesture for side effects. Recover by ignoring uncommitted selections after expiry.
- cost: Approximately $3–$15 for a quality low-profile encoder and PCB/wiring; negligible power when idle, brief GPIO pull-up current while active.  ·  latency: Local event-to-haptic feedback under 50 ms; no relay/model latency for navigation.
- security: Improves safety by separating selection from approval; encoder motion alone must never execute an action. The firmware should persist only a small selected transaction ID/index, never content or secrets.
- depends on: Owner approves enclosure/input direction; Firmware GPIO allocation and debounce implementation; Extend physical_transaction_approval_latch to bind the selected item digest

### `integration` — Add a truthful host lock/wake state adapter on the Mac bridge using a local launchd helper that observes session-lock/unlock and sleep/wake notifications, publishes signed state transitions with observedAt and freshness, and never fabricates a current state when the helper is stale.
- **owner gets:** Deferred pendant-approved work can stop before a sleeping or locked Mac and resume only when it is genuinely usable, instead of acting against an unknown desktop or claiming a job is stuck for the wrong reason.
- effort: Medium: launchd helper, authenticated local IPC to the bridge, state transition journal, stale/unknown handling, and tests across sleep, fast-user-switch, lock, and bridge restart.  ·  risk: Notification loss or helper crashes could report stale state. Treat stale as unknown, cancel leases conservatively, and require a fresh observe before resuming side effects. Never use this as evidence that a browser session is still valid.
- cost: No API cost; low CPU (<1% idle) and negligible storage (bounded transition journal).  ·  latency: Sleep/wake and lock transitions visible within about 1–2 s; resume still requires planner/verifier latency.
- security: Lock state is sensitive host metadata; keep it local to the Mac bridge and expose only boolean state plus freshness, not usernames or screen contents. Authenticate IPC and rotate the bridge credential with existing policy.
- depends on: A local Mac bridge extension point for signed host observations; A durable operation lease/reconciler that consumes unknown versus unlocked/awake states; Owner approval of whether any action may resume automatically after unlock


## What it asked for

_Nothing._
