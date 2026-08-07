# Harness derivation — faculty-judgement — round 93

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving now—what do I need, where am I going, and is there anything I must handle before I go?”"
- **useful because:** A spoken departure checkpoint turns scattered calendar, private browser reservations, Mac files, and recent voice commitments into one short, actionable packet. It catches the practical failures that ordinary morning briefs miss: the ticket is in a logged-in tab, the document is on the Mac, or a promised reply is still unsent. The pendant can deliver it while the owner is putting on shoes, with no screen required.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime handles only the wake phrase, urgency classification, and the final short spoken response. A cheaper background planner gathers calendar and recent commitments, while browser extraction and Mac file lookup run in parallel; no expensive model is used for unchanged source data.
- **latency:** Acknowledge on the pendant in under 500 ms; return a first three-item answer in 8 seconds and continue enriching the queued packet for up to 30 seconds. If a source is offline, say so explicitly rather than blocking the whole answer.
- **cost:** Roughly one short realtime turn plus a small background synthesis per invocation; typically <$0.02 excluding any speech generation. Browser/Mac reads and cached unchanged sources dominate latency, not tokens.
- **security:** Private calendar, authenticated reservations, and local file names leave their respective surfaces only as bounded extracted fields. Never expose secrets in audio unless the owner asks. Creating a reminder is allowed by owner policy; sending mail, submitting a form, or changing a reservation requires explicit confirmation. Every source and failed surface is included in the receipt.
- **missing:** A departure-intent coordinator that can fan out bounded reads across Mac and authenticated browser tabs and merge them into an audio packet; A lightweight source freshness/availability check so stale calendar or browser data is labeled; A pendant playback queue with an interruptible first item and a durable completion receipt

### "“Before I join this meeting, tell me what information is safe to discuss, what I should keep private, and which open tabs or files I should close.”"
- **useful because:** The owner can enter a meeting with a privacy perimeter rather than accidentally exposing a customer name, credential, private document, or unrelated browser tab. The answer combines the meeting’s actual attendees and agenda with the Mac’s open work and authenticated browser context, then gives a short spoken warning and an optional reversible cleanup plan.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background classifier to compare attendee/domain and document sensitivity; reserve realtime for the owner’s short question and final spoken warning. Escalate only ambiguous sensitivity conflicts to the expensive judgement tier.
- **latency:** Acknowledge immediately, produce a preliminary two-item warning within 6 seconds, and finish the bounded scan within 15 seconds. Never block joining the meeting on a slow source.
- **cost:** Usually <$0.03 per check, dominated by bounded local/browser extraction and one small synthesis; no audio generation beyond a short response.
- **security:** Raw documents and page contents stay on their originating Mac/browser surface; the relay receives only sensitivity labels, hashes, attendee domains, and minimal snippets. Never speak secrets aloud by default. Closing tabs, hiding files, or changing sharing requires explicit confirmation, with a before/after receipt and undo.
- **missing:** A sensitivity taxonomy and local redaction service that can classify document/page regions without exporting raw contents; A meeting-context adapter joining calendar attendees, agenda, open tabs, and open files by correlation ID; A reversible “privacy sweep” action with a preview of exactly what would close or hide


## Changes it proposed to its own stack

### `integration` — Add a Departure Packet orchestrator between the existing event/audio, Mac, browser, watch, and job primitives. On a pendant event classified as departure, create one correlation ID, fan out bounded parallel reads (next calendar destination/time, authenticated reservation or ticket tabs, Mac files/reminders relevant to that event, and unresolved recent commitments), enforce a 3-item/20-second budget, attach per-field source+freshness, and publish an interruptible audio queue plus a durable receipt. Cache-key each source so unchanged pages/files are not re-summarized. If any surface fails, the packet marks that field unavailable and still closes with a truthful partial receipt.
- **owner gets:** The owner gets a reliable spoken “leave now” answer instead of a generic brief, even when one tab or the Mac is unavailable. It prevents missed tickets, documents, and promised follow-ups without taking irreversible action.
- effort: Medium: one coordinator/state machine, typed source adapters, correlation/receipt schema, and pendant queue integration; can be tested with synthetic offline surfaces before deployment.  ·  risk: A stale reservation or mistaken commitment could cause bad advice. Mitigate with timestamps, confidence labels, explicit “could not verify,” and never claiming readiness from a missing source. Recovery is replay by correlation ID, not duplicate side effects.
- cost: Low background-model cost; extraction and synthesis are bounded. Storage is a small packet plus receipt per invocation; caching reduces repeat token and browser work.  ·  latency: Parallel fan-out gives a first answer in seconds; a hard deadline prevents a slow browser from holding the pendant hostage.
- security: Only allowlisted fields cross surfaces; keep raw private page text and file contents local to their surface. Audio excludes secrets by default. No send/submit/delete operation is part of this coordinator.
- depends on: A typed cross-surface correlation/receipt envelope (the DeferredIntent proposal should be reused for identity and expiry, but this flow is read-only by default); A playback queue/ack primitive for pendant audio; A source freshness and partial-failure status contract

### `hardware` — Add a low-power coin haptic actuator with a dedicated GPIO/PWM driver and a physical long-press stop path that remains local to the pendant. Keep the existing single button, but use distinct haptic patterns for “packet ready,” “action awaiting approval,” “delivery acknowledged,” and “stop/cancel.” Reserve a hardware interrupt so stop works during audio playback or a dropped relay link.
- **owner gets:** The owner can notice and stop the assistant discreetly in a pocket or noisy environment without looking at a screen or trusting the network. It makes queued departure briefs and approval requests usable while moving, and gives confidence that a long press really stopped something.
- effort: Low-to-medium board revision and firmware driver work; add actuator, transistor/driver, ESD protection, and a small local state machine. Validate vibration comfort and false-trigger behavior in the enclosure.  ·  risk: Vibration can be annoying or drain the battery; debounce and quiet-hours patterns mitigate this. A hardware stop must fail closed locally, even if the server is unreachable. Recovery after accidental stop is an explicit resume request, never automatic replay.
- cost: Approximately $0.50–$2 in components and under 2 mA average only during short pulses; negligible API cost.  ·  latency: Local haptic/stop response under 50 ms; no relay round trip required.
- security: Improves safety: stop/cancel is local and does not transmit audio or context. Approval vibration must not itself authorize an action.
- depends on: Pendant firmware local interruption/stop latch; Audio delivery acknowledgement queue; A persisted event schema distinguishing acknowledged, stopped, and expired packets

### `integration` — Create a meeting privacy-perimeter compiler that correlates the active calendar event with attendee domains, agenda links, open browser tabs, and open Mac documents; run local sensitivity classification and return only labels, risk reasons, and redacted evidence. Before the meeting, publish a short pendant warning and a previewable reversible sweep plan. Require explicit confirmation for every tab close, file hide, or sharing change, and persist a before/after receipt with undo metadata.
- **owner gets:** The owner gets a concrete warning about accidental disclosure before it happens, instead of relying on memory to inspect every tab and document. They can clean up confidently without the assistant silently changing their workspace.
- effort: Medium-high: correlation across calendar/browser/Mac state, local sensitivity classifiers, redaction, preview UI, and reversible action receipts.  ·  risk: False positives could distract the owner; false negatives could expose sensitive information. Show confidence and evidence category, default to warning rather than action, and fail closed when a source cannot be inspected. Recovery is an explicit undo of the recorded sweep.
- cost: Moderate local compute and small synthesis calls; raw content remains local, reducing relay transfer and token cost.  ·  latency: Parallel local scans should yield a first warning in 5–10 seconds; classification of large files is deferred and cannot delay meeting entry.
- security: This is a privacy boundary feature: raw content never crosses surfaces unless explicitly approved, secrets are excluded from spoken output, and cleanup is confirmation-gated.
- depends on: A local sensitivity/redaction classifier; A stable correlation ID linking active calendar events to browser tabs and Mac documents; Reversible privacy-sweep actions with durable before/after receipts


## What it asked for

_Nothing._
