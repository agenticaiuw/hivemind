# Harness derivation — relay-realtime — round 288

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “fill this out from my voice,” have the pendant capture a structured answer, the relay validate and normalize it, and my Mac’s authenticated browser fill the current form field-by-field, read back a compact receipt of every value and leave the form unsent until I explicitly say “submit.”"
- **useful because:** Dictating a long form while away from the keyboard is a real wearable advantage: the browser session supplies authenticated context, the Mac supplies UI reach, and the relay supplies low-latency clarification. It prevents silent transcription mistakes without imposing confirmation on ordinary reversible edits.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Realtime for capture, clarification, and read-back; mac-planner/browser actions for deterministic field filling; no expensive model for straightforward normalization.
- **latency:** First field within 2 seconds; each clarification under 1 second; receipt within 5 seconds of the final field.
- **cost:** Usually one realtime turn plus a small planner/browser job, roughly $0.02–$0.10 depending on form length; browser latency dominates.
- **security:** Form contents and authenticated page state leave the Mac only as structured field metadata/transcript needed for relay confirmation. Never submit or upload without the explicit spoken submit phrase; redact password/card fields from read-back and logs.
- **missing:** A form-schema extractor that maps browser controls to labels, types, requiredness, and sensitive-field flags; A streaming field-fill protocol with pause/resume and idempotent field receipts; An explicit submit boundary in the browser action executor

### "Let me say “keep an eye on this page and tell me only if the meaning changes,” then have the authenticated browser snapshot the page on a schedule, compare semantic sections rather than pixels, and deliver one prioritized spoken alert to my pendant with the before/after evidence and a way to dismiss or snooze it."
- **useful because:** This turns the wearable into an always-available attention filter for pages the owner already has open: price changes, appointment slots, project dashboards, or policy updates become actionable without repeatedly checking a screen. It uses the browser’s session, the relay’s availability, and the pendant’s inbox together.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Cheap background model or deterministic DOM diff for extraction and change scoring; realtime only when the owner asks follow-up questions or receives the short alert.
- **latency:** Checks may run on a minute-scale cadence; alert delivery under 10 seconds after a meaningful change is detected.
- **cost:** Low per check with DOM extraction/diff; roughly $0.001–$0.02 per check, with model cost only for ambiguous semantic changes.
- **security:** Authenticated page content stays in the browser/Mac path and only a minimal diff is sent to the relay. Require per-watch domain and retention controls, suppress secrets and personal fields, and make alerts explain which section changed.
- **missing:** A scheduler that can run while the Mac/browser session is online; A semantic DOM snapshot and field-redaction layer; A durable watch-to-pendant alert binding with deduplication, snooze, and evidence retention

### "Give me a “walk-away handoff”: while I am wearing the pendant, let me dictate a goal and constraints, have the relay preserve the exact task contract, let the Mac and authenticated browser work whenever they become available, and later let me ask “what is the next decision?” to hear only unresolved choices with the relevant evidence—not a generic completion summary."
- **useful because:** The owner is usually away from the Mac, so ordinary computer automation fails at the handoff boundary. This makes a spoken request survive disconnection and resume safely, while prioritizing decisions that actually need the owner instead of replaying logs or announcing routine completion.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Realtime only to capture the contract and answer follow-up questions; background planner and cheap summarizer maintain the task state and extract unresolved decisions.
- **latency:** Capture acknowledgement under 2 seconds; resume automatically on reconnect; decision query under 3 seconds from stored state.
- **cost:** One short realtime capture plus background planning, about $0.01–$0.08 per handoff; storage and browser polling dominate at scale.
- **security:** Persist only the spoken contract, constraints, and task artifacts needed to resume; encrypt sensitive browser evidence; never infer approval from silence or a reconnect. The owner must explicitly choose among surfaced decisions, while routine reversible work may continue.
- **missing:** A durable task-contract record separate from transient job logs; Checkpoint/resume semantics for Mac and browser jobs with idempotency keys; A decision extractor that cites evidence and exposes only unresolved branches; A pendant query path into task state after the original voice session ends


## Changes it proposed to its own stack

### `hardware` — Add a low-profile rotary encoder with push switch and a silent haptic actuator to the pendant, with firmware events for rotate-left/right, press, and long-press. Use the encoder as a local navigation/control channel for streamed spoken lists and pending alerts: rotate changes item or adjusts a proposed value, press selects, long-press cancels. The relay must be able to attach a finite control model to the current voice turn, and the Mac/browser agents must expose choices with stable IDs and receipts.
- **owner gets:** The owner can operate a long-running computer task while walking without staring at a screen or repeating voice commands in public. They can choose a calendar slot, approve one of several form values, skip a spoken inbox item, or cancel an action by touch, even when speech recognition is noisy.
- effort: Moderate hardware enclosure/PCB revision and firmware input state machine; then a cross-surface control schema and pendant rendering/acknowledgement path.  ·  risk: Accidental rotation or press could alter a task; default rotation must be preview-only and every selection must be spoken back. Recover with cancel/undo and stable action receipts. Haptics may reduce battery life and the jewellery enclosure needs debouncing and water resistance.
- cost: Roughly $5–$20 in components and PCB/enclosure changes, plus small idle power and brief haptic bursts; negligible API cost.  ·  latency: Local tactile feedback under 100 ms; relay updates should arrive within about 500 ms when connected, with queued control events if the link drops.
- security: Adds an explicit local physical control channel, improving intentionality for sensitive choices. Do not treat a rotation as authorization to submit a purchase or send mail; require the existing explicit action semantics.
- depends on: A stable pendant control-event uplink/downlink schema; A spoken-list protocol that carries item IDs, labels, and available operations; Cross-surface task state that can reconcile a local selection with Mac/browser receipts


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals: voice-to-authenticated-form filling with an explicit submit boundary; semantic authenticated-page watches with evidence-backed pendant alerts; durable walk-away task contracts that surface only unresolved decisions; and a hardware rotary/haptic control channel for choosing among spoken alternatives. The cross-surface gaps are field/schema extraction, durable checkpoints, semantic diff/redaction, and a pendant control-event protocol.

**Biggest unknown:** The exact live existence and schemas of the watch routes and relay event delivery remain uncertain this round; I did not re-discover them per instruction. The rotary/haptic concept was recorded but the recorder flagged similarity to existing backlog, so it should be treated as lower-confidence novelty.

