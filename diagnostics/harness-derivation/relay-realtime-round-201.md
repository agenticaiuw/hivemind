# Harness derivation — relay-realtime — round 201

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Summarize what you’re about to do before you do it, and let me approve or change it.”"
- **useful because:** When the system spans a wearable, a Mac, and browser sessions, a quick, spoken preflight summary helps prevent wrong turns and builds trust without requiring the owner to watch a screen.
- **path:** relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime for the brief spoken preflight. Mac-planner handles the plan details.
- **latency:** Preflight should be under 2 seconds. Approval adds only the owner’s response time.
- **cost:** Mostly planning cost; the spoken summary is lightweight.
- **security:** Do not expose secrets from authenticated sessions. Summaries should be high-level and omit sensitive content unless the owner explicitly asked for it.
- **missing:** A standardized plan preview format that is safe to speak; A reversible approval flow that can pause execution between plan and run; A relay-visible plan receipt so the correct job is approved

### "“If I sound lost, help me recover: suggest the next sensible step based on what I last asked and what’s actually happening.”"
- **useful because:** In voice, confusion is expensive. A gentle recovery that uses recent context and real job state can prevent repeated commands and frustration.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime to detect confusion cues; cheaper tier to reason over context and propose next steps.
- **latency:** Short hint within ~1 second. Heavier reasoning deferred to a cheaper tier if needed.
- **cost:** Low most of the time; occasional escalations to a larger model to resolve ambiguity.
- **security:** Hints must not hallucinate job state. If state is unknown, say so and offer to check.
- **missing:** A shared, low-cost context projection accessible across surfaces; A standardized confusion/repair signal emitted by the relay; A policy for when to auto-check status vs ask the owner

### "“Handle this job until it is truly finished. If you hit an ambiguity, ask me one precise question through the pendant, use my answer, and keep going; when done, tell me exactly what changed and what remains.”"
- **useful because:** Today a delegated Mac task either guesses through ambiguity or stops as an opaque job. This would make the worn device a genuinely interactive supervisor: the owner can walk away, answer a single spoken clarification later, and receive a truthful completion rather than restarting the whole request.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use relay-realtime only for the short clarification and final spoken turn; mac-planner handles planning and state, mac-vision/browser-extension perform UI work, and a slower background planner evaluates whether the clarification is actually necessary.
- **latency:** Immediate acknowledgement under 500 ms; clarification delivery within 2 s of the blocker; task continuation within 5 s after the answer. Long actions may run asynchronously.
- **cost:** About $0.01–$0.08 per task depending on planner turns; the dominant cost is repeated planner context and screenshots, not the relay clarification.
- **security:** The planner must attach the exact blocked step, candidate interpretations, and evidence to each question so the owner is not approving an invisible action. The answer and resulting actions leave the pendant for the relay/Mac; no new secrets should be copied into the question. Reversible actions remain automatic under the owner's maximum-access policy.
- **missing:** A planner-to-relay clarification event with a resumable job state; A pendant reply correlation to the blocked job; A durable state machine that can pause a Mac/browser job without losing session context; An end-to-end completion receipt that includes changed objects and unresolved steps

### "“Before you act, reconcile what I said with what is actually open on my Mac and in my signed-in browser, then give me one spoken plan with the supporting evidence; if the two surfaces disagree, tell me the conflict instead of choosing silently.”"
- **useful because:** The owner currently has separate Mac and browser agents that can each act, but no owner-facing cross-surface truth pass. This prevents dangerous stale-tab or stale-file decisions and makes a spoken answer defensible: the pendant can say which tab, document, timestamp, or local state it relied on.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** faculty-perception or a cheap background model gathers and normalizes observations; faculty-judgement produces the compact recommendation; relay-realtime only speaks the result and routes an explicit action request.
- **latency:** Read-only reconciliation in 3–8 s; speak an initial conflict warning as soon as the first contradictory pair is found. Never block the owner on a full scan when a local, bounded evidence set is sufficient.
- **cost:** Roughly $0.02–$0.12 per invocation; screenshots/page extraction and re-sent evidence dominate. Cache hashes and timestamps locally so unchanged surfaces are not resent.
- **security:** Authenticated browser content and local files must remain scoped to the specific request and be redacted before cross-surface model calls. Return provenance and freshness timestamps. Acting on the recommendation must be a separate explicit downstream action, not an accidental side effect of inspection.
- **missing:** A cross-surface observation envelope with source, timestamp, freshness, and confidence; Parallel read-only fan-out to Mac and browser with bounded scope; A conflict detector and spoken evidence/provenance formatter; A relay turn that can present the recommendation without invoking execution

### "“Give me a silent status of my active jobs: one vibration for working, two for blocked, and three for verified completion; if I press once, speak only the most urgent one.”"
- **useful because:** A worn computer assistant should communicate without forcing the owner to expose private audio in public. Today the one LED and spoken audio are poor asynchronous channels, so the owner either misses progress or hears it at the wrong moment. This becomes especially useful once several Mac/browser tasks overlap.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** No expensive model for the vibration classification: relay-side job state and receipts map directly to patterns. Use relay-realtime only when the owner presses and requests the spoken summary; use the existing planner/browser receipts as evidence.
- **latency:** Pattern within 1 s of a state transition; pressed spoken summary begins within 2 s. Coalesce repeated heartbeats so the owner is not buzzed continuously.
- **cost:** Under $0.01 per job-state update; mostly event delivery and device power, with model cost only for an optional natural-language summary.
- **security:** Vibration patterns must reveal urgency, not content. Do not vibrate private titles or account names. Persist only a job ID, state, expiry, and urgency on the inbox; audio remains relay-rendered and follows existing storage rules.
- **missing:** A physical haptic actuator (proposed above); Relay job-state fan-out to the pendant inbox; A compact urgency/state encoding shared by planner, browser, and relay; A press-time summary endpoint that reads verified receipts

### "“When I say ‘continue that,’ find the last unfinished job I mentioned, show me the exact checkpoint and unresolved side effect in one sentence, then continue only from there.”"
- **useful because:** The owner should not have to remember job IDs or repeat a long request after a dropped link, sleep, or interrupted voice turn. This is a user-facing continuation primitive, not a generic status poll: it binds a natural spoken reference to the last verified checkpoint and prevents replaying completed mutations.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A cheap relay-side resolver ranks recent jobs by session, spoken references, and last state; the planner resumes from a structured checkpoint. relay-realtime speaks only the one-sentence checkpoint and asks for no extra model work unless references are ambiguous.
- **latency:** Resolve and speak checkpoint in under 2 s; resume execution within 5 s after the owner's implicit continuation. If more than one candidate is plausible, speak the top two names and wait rather than guessing.
- **cost:** About $0.005–$0.03 per continuation; job metadata lookup dominates, with a small model call only for ambiguous natural-language references.
- **security:** The checkpoint must state what was already changed and what will happen next. Resume tokens must be bound to the owner session and expire. Never infer that an old high-impact action is still authorized merely because it was previously requested.
- **missing:** A natural-language recent-job resolver; Structured, durable per-action checkpoints in receipts; An idempotent resume operation for partially executed plans; A spoken disambiguation turn when several jobs match


## Changes it proposed to its own stack

### `interaction` — Add a physical 'attention lease' protocol spanning pendant, relay, Mac, and browser: when a task begins, the pendant announces whether it is merely observing, waiting for the owner, or actively changing state; the lease expires unless the relay receives heartbeats from the executing surface, and expiry causes a spoken/LED interruption with the last verified checkpoint. A resumed button press renews the lease and continues from that checkpoint rather than replaying earlier actions.
- **owner gets:** The owner can walk away knowing whether a request is safely waiting, still working, or has gone stale. If Wi‑Fi, the Mac, or a browser session dies, they hear the last fact that was actually verified instead of a confident but obsolete completion.
- effort: Medium-high: define a shared lease/checkpoint record, instrument planner/browser execution, add relay expiry handling, and teach pendant LED/audio surfaces the three states. This is not a scheduler; expiry is tied to an already-running job and can be evaluated on incoming traffic or a Durable Object alarm.  ·  risk: A lost heartbeat could interrupt a genuinely healthy long action. Recovery is to retain the checkpoint and allow one button-press renewal; every action receipt must be idempotent so renewal cannot duplicate mutations. Clock skew is avoided by relay-issued monotonic lease tokens.
- cost: Negligible API cost; a small durable record and occasional heartbeat traffic. Durable Object alarm support would add modest Worker storage/runtime usage.  ·  latency: No added latency to ordinary speech. Heartbeats are asynchronous; a lease-state spoken update can be emitted within one voice turn.
- security: Improves safety without adding an approval gate: the owner sees the execution boundary and stale-state transition. Tokens must be unguessable and scoped to the session/job; do not put browser secrets in the pendant record.
- depends on: A resumable clarification/checkpoint state machine; An implemented planner-to-relay event path; A durable relay alarm or equivalent expiry mechanism; The existing truthful_action_status_beacon and offline_alert_inbox behaviours

### `hardware` — Add a tiny coin vibration motor with a low-side driver and a dedicated GPIO/PWM channel to the nRF9160 pendant, with firmware patterns for acknowledgement, unread inbox, task blocked, and verified completion. Keep audio and the existing single LED as fallbacks, and gate vibration behind a local silent/public-mode setting.
- **owner gets:** The owner can receive a discreet confirmation or urgent blocked-task signal in a meeting, on public transit, or while listening to someone else without broadcasting speech or staring at the LED. It makes asynchronous work usable away from the Mac rather than merely technically complete.
- effort: Medium hardware revision and firmware work: select a 3 V coin motor, transistor/MOSFET, flyback protection, mechanical mounting, current budgeting, and four short patterns. Validate RF/audio noise and battery impact on the live USB setup before a board spin.  ·  risk: Vibration can be missed or become annoying; cap duration and provide a physical long-press way to disable it. Motor transients could brown out or inject audio/RF noise; isolate supply, add bulk capacitance, and recover by falling back to LED/audio if self-test fails.
- cost: Approximately $1–$4 BOM increase and roughly 60–120 mA only during short pulses; negligible average draw if patterns are capped. Board spin and enclosure work dominate.  ·  latency: Sub-100 ms local acknowledgement; no relay round trip for basic patterns.
- security: No new data leaves the device. A local public-mode flag prevents private spoken content from being triggered by an ordinary status event.
- depends on: Existing offline_alert_inbox urgency fields; Existing truthful_action_status_beacon states; A firmware settings path for silent/public mode


## What it asked for

_Nothing._
## Its own summary

Recorded six non-duplicate proposals. The strongest owner-facing gaps are an interactive clarification/resume loop for delegated work, cross-surface evidence reconciliation, lease/checkpoint expiry so stale jobs cannot masquerade as complete, discreet haptic job-state signaling, and natural-language continuation from the last verified checkpoint. The most immediate physical addition is a vibration motor, but its pattern vocabulary overlaps an existing backlog item, so the genuinely new value is the silent multi-job status contract and checkpoint semantics rather than the actuator alone.

**Biggest unknown:** Whether the existing relay already has an undocumented durable recent-job resolver, structured per-action checkpoints, or planner-to-pendant clarification events. Those are the specific missing seams I would verify next; without them, the owner cannot safely resume or answer a blocked task by voice.

