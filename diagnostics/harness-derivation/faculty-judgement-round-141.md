# Harness derivation — faculty-judgement — round 141

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Why did I decide to do this?” Then, when I revisit a project, remind me of the short voice note I left about the decision and show the files, calendar event, or private web page that informed it."
- **useful because:** People lose the reasoning behind decisions, not just the decision itself. A pendant makes capturing the rationale effortless; the Mac and browser can attach evidence so the reminder is useful rather than a decontextualized note. This is especially valuable months later when the owner is about to reverse or repeat a decision.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to capture/transcribe the brief voice note; use a cheaper background model to extract the decision, link evidence, and retrieve it later.
- **latency:** Capture should acknowledge locally in under 300 ms; transcription and evidence linking may take 5–20 s in background. Retrieval should return a spoken answer in under 3 s.
- **cost:** Roughly $0.005–$0.03 per note, dominated by transcription and background linking; retrieval is usually under $0.01.
- **security:** Voice notes and linked private pages may contain sensitive information. Store encrypted, retain the owner's explicit note, keep source snippets and URLs instead of full page copies where possible, and never expose private evidence in a shared surface without confirmation.
- **missing:** A rationale-specific record type with immutable capture timestamp, confidence, and links to source evidence; A cross-surface retrieval command that can search rationale records by project/entity; A Mac/browser evidence linker that records provenance without retaining unnecessary page content

### "“Teach me how to do this once, then let me do the next one.” Have the Mac or browser perform the first safe example while the pendant explains each meaningful step, then hand me the next instance and check my result before I submit anything."
- **useful because:** Automation normally hides the skill and leaves the owner dependent on the system. An apprenticeship mode converts one-off computer use into durable competence: the owner gets a narrated example, a practice instance, and a safe correction loop across the exact private tools they use.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles only short spoken explanations and questions; a cheaper background model derives the procedure and evaluates the practice result from structured action receipts and browser evidence.
- **latency:** Each explanation should arrive within 1 s of the demonstrated step. Procedure extraction and practice scoring can take 2–10 s.
- **cost:** About $0.02–$0.15 per lesson, dominated by screenshots/page extraction and the narrated realtime turns; subsequent practice checks should be pennies.
- **security:** The system may see private work data while teaching. Redact unrelated fields, restrict evidence to the active tab/file, never submit or send without the owner's existing confirmation policy, and retain the procedure only if explicitly saved.
- **missing:** A step-level demonstration recorder that pairs actions with plain-language intent; A practice-mode executor that can compare the owner's result with expected state without mutating external systems; A lesson state machine shared by pendant audio, Mac actions, and browser tab evidence

### "“What am I looking at, and what is the next safe step?” Have the pendant give me a concise spoken explanation of the currently focused Mac window or browser tab, identify the relevant controls or missing information, and offer one reversible next action—without changing anything until I say go."
- **useful because:** When the owner is confused in a private app or unfamiliar webpage, they need orientation before automation. This makes the wearable a just-in-time visual guide: the Mac supplies the focused window, browser supplies authenticated page structure, and the pendant turns it into a short answer while preserving control.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheaper vision/background model to inspect and summarize the screen or DOM; use realtime only for the owner's short question and spoken response. Escalate to the expensive tier only when the screen is ambiguous.
- **latency:** A first spoken orientation in 2–4 s; a proposed action in another 1–2 s. No action should run before explicit approval.
- **cost:** Approximately $0.01–$0.08 per request, dominated by an occasional screenshot/vision call; DOM-only browser views should be much cheaper.
- **security:** Screen and authenticated-tab contents are highly private. Capture only the focused window/tab, redact passwords and payment fields, do not persist screenshots by default, and require approval before any mutation or navigation with side effects.
- **missing:** A focused-window capture API that works with the existing accessibility-free AppleScript path; A shared visual/DOM grounding schema mapping explanations to controls and source coordinates; A spoken proposal/approval handshake that expires if the screen changes

### "“Keep this commitment moving with the other person until it is actually settled.” From my spoken intention and existing calendar/email/browser context, identify the unresolved coordination, prepare a small set of realistic options, draft the appropriate messages, track replies and conflicts across surfaces, and tell me only when my decision or approval is needed."
- **useful because:** A commitment is not complete when a draft exists or a calendar slot is proposed; it is complete when the other person has agreed and the owner's calendar reflects reality. Today the owner must manually remember which threads are awaiting replies, reconcile changing availability, and notice conflicts. This would close that social coordination loop while keeping the owner in control of sending and final choices.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Use a cheaper background model to monitor thread state, compare calendars, and generate options; use realtime only when the owner is interrupted for a concise decision or approval.
- **latency:** Initial coordination packet within 30 seconds; reply changes processed in the background within 2 minutes. Spoken interruptions should be under 3 seconds and only occur at a genuine decision point.
- **cost:** Roughly $0.03–$0.20 per coordination episode, dominated by private-page reads and periodic reply reconciliation; idle monitoring should use scheduled cheap work.
- **security:** This handles private correspondence and may infer relationships, availability, and commitments. Never send without explicit approval, show recipients and exact message text, minimize retained thread content, and pause monitoring on request. Calendar changes and external submissions need the owner's existing confirmation policy.
- **missing:** A durable coordination object representing participants, outstanding proposal, response deadline, and settled outcome; Cross-surface reply correlation that can associate an email or authenticated web response with the coordination object without relying on brittle wording; A background watcher that re-plans options when replies, calendar availability, or travel constraints change; A single owner approval packet for message text, recipients, and calendar mutations, with stale-state invalidation before send

### "“Notice when I keep correcting the same kind of task, and make the next one easier.” Compare my repeated Mac/browser corrections and aborted attempts, infer a safer reusable workflow, demonstrate it on a dry run, and ask me whether to save it as a named routine."
- **useful because:** The system currently executes tasks but does not learn from the owner's corrections. Repeated friction is the clearest evidence of what should be improved, yet the owner must diagnose it and specify an automation from scratch. Turning corrections into a reviewed routine compounds value without silently changing behavior.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a background model to cluster receipts and corrections and draft a candidate workflow; use realtime only to explain the dry run and ask for save/decline.
- **latency:** Candidate suggestion after 3–5 similar corrections or within a weekly review; dry-run explanation under 5 seconds; no automatic persistence.
- **cost:** About $0.02–$0.10 per candidate, mostly receipt clustering and one dry-run inspection; saved routines reduce future cost.
- **security:** Behavioral traces can reveal work habits and private destinations. Keep analysis local where possible, redact values and credentials, require explicit approval to save, and never generalize a routine across accounts or recipients without a scope review.
- **missing:** A correction/abort taxonomy attached to action receipts; Workflow-diff generation that exposes exactly what would be generalized and what remains fixed; A sandbox or preview executor for candidate routines; A routine approval UI with scope, expiry, and undo


## Changes it proposed to its own stack

### `hardware` — Add a low-power coin vibration motor with a dedicated driver and a second tactile input (or capacitive touch strip) to the pendant, and define a small local haptic vocabulary: one pulse = acknowledgement, two = action ready, escalating pulses = attention required, long press = cancel/stop. The current board has one button/LED and free I2C/SPI; the motor driver can use a GPIO and the second input an available GPIO/I2C controller. Keep all haptic acknowledgements local so they work while the LTE link or Mac is absent.
- **owner gets:** The owner can interact discreetly in a meeting, while walking, or when audio is inappropriate. A silent acknowledgement and a reliable physical stop signal are more dependable than an LED they cannot see, and make long-running Mac/browser work feel present without forcing spoken interruptions.
- effort: Medium hardware revision plus firmware event API, haptic patterns, current limiting, enclosure and wear testing. Prototype with an off-board motor/driver on the dev kit first.  ·  risk: Motor noise or accidental presses could annoy or trigger an unintended stop; default to acknowledgement-only patterns and require a deliberate long press for cancel. Add a firmware watchdog and fall back to LED/button if the driver fails.
- cost: Approximately $1–$4 in components at volume (more for enclosure/assembly), under 20 mA peak during short pulses and negligible average draw if duty-cycled; no model/API cost.  ·  latency: Local pulses can begin under 50 ms after an event, avoiding a network round trip.
- security: Improves privacy because status need not be spoken or displayed. A physical cancel must be treated as a high-priority local safety event and authenticated against accidental activation.
- depends on: A pendant event protocol distinguishing acknowledgement, attention, and cancel; Firmware-safe GPIO allocation and electrical validation on the prototype board; Relay/Mac mapping of job lifecycle events to haptic patterns


## What it asked for

_Nothing._
## Its own summary

Round 141 produced three distinct owner-facing capabilities: (1) evidence-linked decision rationale retrieval, (2) apprenticeship mode that demonstrates one computer task then lets the owner practice safely, and (3) focused-window/browser spoken orientation with an expiring approval handshake. I also proposed a haptic motor plus second tactile input for discreet acknowledgement and a physical stop signal. The owner can feel these only after the connective layers are built; the routes exist, but the orchestration does not.

**Biggest unknown:** Whether the Mac agent can currently provide a focused-window screenshot or structured accessibility-free window identity, and whether the pendant audio path has completed 24 kHz end-to-end acceptance. I still need a focused-window capture/grounding API, step-level demonstration and practice state, rationale records linked to evidence, and a shared approval handshake that invalidates when the screen changes.

