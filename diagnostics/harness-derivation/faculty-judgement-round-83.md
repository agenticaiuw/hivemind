# Harness derivation — faculty-judgement — round 83

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I promise someone something, remember it, help me do it, and tell me before I let it slip.”"
- **useful because:** People fail at the handoff between saying yes and actually completing the promise. The pendant can catch a commitment while it is fresh; the Mac and authenticated browser can find the relevant person, thread, calendar, or task; the relay can keep the obligation alive while the owner is away. It should distinguish a promise from a thought, ask one brief clarification only when needed, and never send anything without confirmation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime model only for the short, explicit pendant capture and clarification. Use a cheaper background model to extract the commitment, due window, people, evidence, and next action; use scheduled relay work for deadline checks and a compact realtime response only when an interruption is warranted.
- **latency:** Capture acknowledgement under 1 second; extraction and cross-surface linking within 30 seconds; deadline scans hourly or at user-chosen cadence; spoken interruption under 2 seconds after a high-confidence risk signal. Ordinary updates wait for the evening wrap-up.
- **cost:** About $0.005–$0.03 per captured commitment and <$0.01 per scheduled scan, dominated by transcription/LLM extraction; avoid sending full mail or page contents by first extracting local snippets and hashes.
- **security:** Default to explicit button/phrase capture, not continuous retention. Keep raw audio/transcript ephemeral; store only the commitment, sensitivity label, source/time, and confidence. Private browser data must stay on the authenticated Mac bridge; relay receives derived fields only. Require confirmation before sending mail, changing appointments, or submitting forms. Provide snooze, edit, delete, and a universal stop.
- **missing:** A durable commitment object with owner, counterpart, due window, evidence predicate, status (open/fulfilled/at-risk/waived), sensitivity, and provenance; Cross-surface linking that can search Mail/Calendar/Notes and authenticated browser tabs without exporting their contents; A postcondition verifier that re-reads the exact thread/task/calendar item and reports DONE, FAILED, or UNKNOWN rather than trusting dispatch receipts; Pendant-local capture queue and offline handoff marker so a promise is not lost when connectivity drops; An attention policy that batches low-risk nudges and escalates only high-confidence, time-sensitive obligations

### "“When I say ‘coach me,’ quietly help me navigate a difficult conversation: remind me of the relevant context, warn me if I am about to make a commitment I cannot keep, and give me one short option for what to say next.”"
- **useful because:** The owner can currently get summaries and execute tasks, but not discreet, situation-aware help while a human conversation is unfolding. A worn device can hear the immediate exchange, the relay can reason with low latency, and the Mac/browser can supply only the relevant prior thread, calendar context, or account details. This helps the owner stay truthful and measured without taking over the conversation or storing it as a transcript.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime reasoning for the explicitly activated coaching window only. Use a cheaper background model beforehand to prepare a compact context card from permitted Mail/Calendar/browser sources; never stream an ambient conversation continuously to the expensive tier.
- **latency:** Initial context card in 2–5 seconds; spoken or haptic cue in under 700 ms after an explicitly marked trigger phrase or button event; suggestions limited to one sentence so they do not derail the conversation.
- **cost:** Roughly $0.02–$0.10 per coaching session depending on duration; the dominant cost is realtime audio tokens. Keep sessions short, locally VAD-gated, and automatically expire after 10 minutes.
- **security:** Potentially sensitive third-party speech must not be retained or silently uploaded. Require a physical button or unmistakable activation phrase, an audible/haptic active indicator, local buffering only before activation, automatic timeout, and a hard stop. Context retrieval must be allowlisted; the system must not impersonate the owner, fabricate facts, or send messages. Give the owner a post-session deletion control.
- **missing:** An explicit coaching-session latch with physical and spoken activation, timeout, and universal stop; Low-latency local voice activity detection and private cue output on the pendant; A compact, permission-filtered context card compiler for the active person/topic; A policy evaluator that detects impending commitments or high-risk claims without making social or legal decisions for the owner; A third-party privacy mode that prevents storage and minimizes relay audio exposure


## Changes it proposed to its own stack

### `context` — Add a Commitment→Evidence graph and reconciliation worker. A captured commitment becomes a typed node with source transcript/time, counterpart, due window, sensitivity, and an explicit evidence predicate (for example: matching sent message, accepted calendar event, completed task, or browser field change). The worker resolves candidate Mail/Calendar/Notes/browser records on the Mac, asks for clarification on ambiguous matches, and periodically re-reads the bound source. It emits OPEN, DUE_SOON, FULFILLED, AT_RISK, WAIVED, or UNKNOWN events with citations; it never infers fulfillment from an attempted action receipt alone.
- **owner gets:** The owner gets one honest answer to “did I actually do what I said?” instead of a reminder that fires forever or false reassurance after a failed send. It catches commitments made away from the Mac and proves completion across the places where work really happens.
- effort: Medium/high: schema and encrypted persistence, local Mail/Calendar/Notes adapters, browser-session binding, predicate evaluation, deduplication, and a pendant/relay notification policy.  ·  risk: False matches could expose or misattribute private commitments; mitigate with provenance, confidence thresholds, source-specific permissions, explicit UNKNOWN, and confirmation before linking low-confidence records. A failed verifier must degrade to a review item, never silently mark fulfilled.
- cost: Low background API cost (cheap extraction and predicate checks); occasional realtime cost only for clarification or urgent spoken alert. Mac-local indexing minimizes relay transfer.  ·  latency: Capture stays immediate; initial linking typically under 30 seconds; verification is scheduled, with urgent due windows triggering a bounded scan.
- security: High privacy sensitivity: raw source content remains on Mac/browser; relay stores opaque IDs, derived status, and minimal snippets or hashes. Encrypt commitment records and support per-item deletion/export.
- depends on: A durable commitment object and offline capture queue; Exact-tab/source provenance and postcondition verification; Attention arbitration and owner interruption preferences

### `hardware` — Add a discreet coaching I/O path: a dedicated capacitive side strip or two-stage button with a short-range haptic motor, plus firmware support for three distinguishable vibration patterns and a hard-stop gesture. The pendant locally gates microphone capture until the owner deliberately activates coaching, shows an active-state LED/haptic acknowledgement, and drops all buffered third-party audio on timeout or stop.
- **owner gets:** The owner can receive private help in a live conversation without pulling out a phone, speaking a conspicuous command, or risking that an always-listening assistant records people around them. Distinct haptic patterns communicate “pause,” “check your facts,” and “safe to continue” without interrupting their speech.
- effort: Medium hardware revision and firmware work: one input, one vibration actuator, event debouncing, audio gate integration, and a small protocol for relay coaching state. If the current board already exposes suitable GPIO, a firmware-only prototype can validate the interaction before a PCB revision.  ·  risk: False activations or missed haptic cues could distract the owner; require deliberate press-and-hold, configurable sensitivity, and an immediate stop gesture. Haptic patterns must never be treated as authoritative advice. Component failure should leave ordinary pendant voice operation intact.
- cost: Approximately $2–$8 in components and under 10 mA peak during vibration, depending on actuator and enclosure changes; negligible API cost. A firmware-only prototype has no hardware cost.  ·  latency: Local activation and acknowledgement under 100 ms; no added latency to ordinary voice mode. The relay still needs to meet the coaching response budget separately.
- security: Improves privacy by making microphone activation physically explicit and locally enforced. Firmware must ensure the relay cannot silently enable coaching capture and must erase pre-activation audio buffers on stop/timeout.
- depends on: An explicit coaching-session protocol and relay-side privacy latch; A local interruption/stop mechanism; A bounded realtime coaching audio path


## What it asked for

_Nothing._
