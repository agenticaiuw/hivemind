# Harness derivation — unified — round 133

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m switching devices—give me the exact thread I was in, with what I saw, what I decided, and the next action, on whichever surface I open.”"
- **useful because:** The owner can move from pendant to Mac to iPhone without reconstructing context. It turns the hive into one continuous workspace rather than several assistants that forget each other.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background/small model builds the capsule from structured evidence; realtime is used only to answer the owner’s handoff request and read the concise capsule aloud.
- **latency:** Under 5 seconds for a handoff capsule; under 1 second to retrieve an existing capsule.
- **cost:** ~$0.01–0.04 per handoff, dominated by summarizing only changed evidence; retrieval is near-zero.
- **security:** Capsules may contain private tab titles, calendar items, and spoken decisions. Encrypt at rest, expire by task, keep browser content out of the pendant unless explicitly requested, and require confirmation before resuming an external action.
- **missing:** A user-facing handoff-capsule schema and cross-surface resume API; A reliable current-task join across Mac context, browser tab evidence, pendant session, and queued jobs; Dashboard/iOS resume picker

### "“Keep track of promises I make out loud or in my private tabs, and when the evidence says I owe someone something, ask me for the smallest next step.”"
- **useful because:** Important commitments currently disappear into conversation, email, and web sessions. The owner gets a timely, evidence-linked nudge instead of a generic task list, without the system sending anything on its own.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background extraction identifies candidate commitments; a judgement model reconciles dates, people, and evidence; realtime only handles the owner’s short clarification.
- **latency:** Capture within 30 seconds of a session/event; reminders delivered at the chosen quiet-time boundary; clarification under 2 seconds.
- **cost:** ~$0.02–0.08 per daily commitment pass, dominated by private-source extraction; event deduplication is inexpensive.
- **security:** Spoken commitments and relationship data are sensitive. Store source snippets and confidence, not raw audio by default; never infer a promise as fact without showing the quote/page evidence; no outbound message or calendar mutation without explicit approval.
- **missing:** Commitment entity/evidence data model with confidence and expiry; Event joiner across speech sessions, Mail/Calendar, browser inspections, and Mac notes; Owner-configurable reminder/quiet-hour policy

### "“Only interrupt me when something is urgent in the context of what I’m doing; otherwise queue it, explain why it can wait, and let me dismiss or defer it from the pendant.”"
- **useful because:** A wearable that speaks every notification is unusable. This makes the pendant a context-aware gate: urgent travel, access, or human messages can break through, while everything else waits for a coherent review.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard → iOS
- **model tier:** Background classifier and rules rank incoming events; realtime is reserved for the rare interrupt and one-sentence explanation. A slower model periodically rechecks deferred items.
- **latency:** Classify within 10 seconds of an event; urgent alert reaches the pendant within 3 seconds; defer/dismiss acknowledgement under 1 second.
- **cost:** ~$0.01–0.05 per event batch; realtime cost only for actual spoken interruptions.
- **security:** Urgency classification sees private notifications and may expose them aloud. Use redacted titles by default, require an owner-set allowlist for sources, provide a physical local mute, retain decisions briefly, and never let urgency alone trigger external actions.
- **missing:** Cross-source event ingestion from Mac, authenticated browser, and relay sessions; A persistent interruption queue with defer/dismiss state and policy controls; Pendant event delivery and local mute/defer protocol

### "“While I’m in this meeting, quietly verify questions against the documents and private tabs I choose, then whisper the answer or a source link to me—never speak for me.”"
- **useful because:** The owner gets an evidence-backed private research assistant during a live conversation. The pendant supplies the question and discreet audio; the Mac/browser reach files and logged-in sources; the relay answers without taking over the meeting.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime handles the short spoken query and response; background retrieval and source reconciliation use a cheaper model, escalating only when sources conflict.
- **latency:** Answer in 4–8 seconds for already-open material; clearly say “still checking” rather than inventing an answer.
- **cost:** ~$0.03–0.15 per question, dominated by retrieval and a short realtime response.
- **security:** Meeting audio, private tabs, and displayed answers must remain private. Require explicit meeting mode and a selected-source allowlist, indicate when an answer is inferred or stale, retain citations briefly, and prohibit outbound actions.
- **missing:** Meeting-mode source selection and temporary access scope; Low-latency retrieval over selected Mac files and authenticated tabs; Discreet audio channel state and a spoken cancel command

### "“Tell me when two things I’m doing conflict—like a calendar promise, browser form, or message contradicting another—and show me the smallest safe way to resolve it.”"
- **useful because:** The hive can see across surfaces where contradictions are otherwise invisible: overlapping commitments, different addresses or dates, incompatible instructions, or a stale form. It prevents embarrassing or costly mistakes without silently changing anything.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Background model continuously normalizes dates, people, places, and commitments; judgement model verifies genuine conflicts; realtime is used only for an urgent spoken warning.
- **latency:** Detect within one minute of a changed source; urgent conflict warning within 3 seconds; resolution preview under 10 seconds.
- **cost:** ~$0.02–0.10 per daily change batch, dominated by private-source normalization; most checks are deterministic.
- **security:** Cross-source comparison exposes sensitive relationships and account data. Use per-source consent, minimize stored values through hashes/redacted snippets, explain the exact conflicting evidence, and require approval for every correction or submission.
- **missing:** Cross-surface entity/date normalization with provenance; Conflict rules that distinguish harmless differences from actionable contradictions; A resolution preview that can span Calendar, browser forms, and drafts without mutating them

### "“When I’m stuck on a screen, describe the relevant controls and the safest next step through the pendant, using the page structure and my current task—not a noisy screenshot dump.”"
- **useful because:** The owner gets an accessible, hands-free explanation of unfamiliar web screens. The browser can inspect DOM structure and authenticated content while the Mac contributes the current task; the pendant gives a concise spoken route without requiring Accessibility permission or taking control.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Cheap structured extraction identifies controls and page state; realtime produces the short spoken explanation; a stronger model is used only when the page is ambiguous or the owner asks for reasoning.
- **latency:** Initial orientation under 4 seconds; follow-up control lookup under 1.5 seconds.
- **cost:** ~$0.01–0.08 per screen orientation, dominated by difficult pages; structured DOM extraction is inexpensive.
- **security:** Authenticated pages may contain financial or health information. Inspect only the active/explicitly selected tab, redact secrets and hidden fields, do not transmit screenshots by default, announce when content leaves the Mac, and require confirmation before any click or submission.
- **missing:** A semantic page-narration contract returning landmarks, controls, state, and safe next actions; A browser-to-pendant query loop with active-tab scoping; A no-Accessibility fallback based on browser DOM/accessibility-tree inspection


## Changes it proposed to its own stack

### `hardware` — Replace the prototype’s single-button/LED control with two tactile buttons plus a small haptic motor and a fuel-gauge IC: one button remains conversation, the other is a hard local privacy/mute control; short/long press patterns provide defer, dismiss, and emergency stop, while the gauge reports battery state to the relay.
- **owner gets:** They can silence the microphone or stop playback instantly without trusting LTE, a model, or a screen, and the pendant can warn before a call dies from battery. Two controls make interruption handling dependable while wearing it.
- effort: Pendant PCB/enclosure revision, Zephyr GPIO/haptic/fuel-gauge drivers, protocol fields, and accessibility testing; moderate hardware revision plus firmware work.  ·  risk: More controls can cause accidental presses and increase size. Use recessed/tactile differentiation, debounce, long-press for destructive actions, and retain the current one-button mapping as a fallback firmware mode.
- cost: Roughly $3–8 BOM increase in volume, plus PCB/NRE; haptic and gauge add tens of milliamps only during actuation/measurement, negligible idle draw.  ·  latency: Local mute/stop is sub-100 ms and independent of network; battery telemetry adds no audio latency.
- security: Improves privacy because the mute latch is physically enforced. Firmware must expose latch state to relay and make it impossible for remote commands to clear it without a deliberate local gesture.
- depends on: A pendant control protocol carrying local mute/defer state; Firmware support for haptic and fuel-gauge devices; Interruption queue semantics for defer/dismiss


## What it asked for

_Nothing._
