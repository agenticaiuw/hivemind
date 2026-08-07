# Harness derivation — faculty-judgement — round 82

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I accept or schedule a meeting, tell me how it affects the rest of my day and suggest the least disruptive time, including travel and preparation; never book or move anything without my approval."
- **useful because:** The owner gets protection from hidden calendar costs: collisions, lost focus time, preparation gaps, and impossible travel. The pendant can give a short recommendation while the Mac/browser gather the authoritative details, and approval remains explicit.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use a cheap background model to collect and normalize calendar, location, and preparation facts; use realtime judgement only to resolve genuine tradeoffs and phrase the short recommendation. The Mac planner executes only after approval.
- **latency:** Initial impact scan under 8 seconds when calendar and browser sessions are warm; a spoken recommendation under 2 seconds after facts are cached. Approval and any write happen only after the owner says yes.
- **cost:** Roughly $0.01–$0.05 per scan, dominated by authenticated-page extraction and the occasional judgement call; routine calendar normalization should use the cheap tier.
- **security:** Calendar, travel, and possibly private meeting details leave the Mac/browser boundary only as minimized facts. Do not expose attendee or meeting content in open-air speech unless the owner asks. Moving or creating an event always requires confirmation and a final before/after diff.
- **missing:** A calendar-impact evaluator that models preparation, travel buffers, focus-block fragmentation, and time-zone changes rather than merely detecting overlaps.; A write-free approval card/audio item containing proposed slot, assumptions, confidence, and exact eventual mutation.; A reliable calendar adapter for both Apple Calendar and authenticated web calendars, with source precedence when they disagree.

### "I’m overloaded today—make me a graceful degradation plan: tell me what I can safely skip, defer, shorten, or delegate, explain who will be affected and why, draft any needed messages, and let me approve changes one at a time."
- **useful because:** Today assistants either list obligations or execute isolated tasks; they do not help a person preserve the most important outcomes when the day becomes impossible. This gives the owner a humane, socially aware way to reduce load without silently breaking promises.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a background model to assemble commitments and affected parties from calendar, reminders, mail, notes, and open browser work. Use the realtime judgement tier only for tradeoffs the owner has not specified. Use a cheap drafting model for proposed messages; never autonomously send or reschedule.
- **latency:** A first plan within 10 seconds from warm local sources, with each individual approval response under 2 seconds. Browser-only sources may continue asynchronously while the owner receives a provisional plan marked incomplete.
- **cost:** Approximately $0.03–$0.12 per plan, dominated by cross-source extraction and one judgement pass; drafting and routine classification should be background-tier.
- **security:** This necessarily exposes relationship and commitment metadata across surfaces, so retain source pointers and derived impact rather than copying full message bodies to the relay. Open-air speech must avoid names and sensitive reasons by default. Every proposed skip, deferment, delegation, or message needs a separate explicit approval; sending, deleting, or moving events remains prohibited without it.
- **missing:** A commitment model that represents not only due dates but reversibility, social impact, minimum viable completion, and delegation candidates.; A consequence simulator that can produce alternatives (skip/defer/shorten/delegate) and identify downstream conflicts before any mutation.; A review surface that presents one proposed change at a time with affected people, exact text or calendar diff, confidence, and undo/receipt linkage.; A policy memory for the owner's personal thresholds (what may be dropped, what must be protected, and acceptable explanations), learned only from explicit corrections.


## Changes it proposed to its own stack

### `integration` — Add a read-only calendar-impact pipeline between /plan and /execute: normalize candidate events from Apple Calendar and authenticated browser calendars, compute travel/prep/focus fragmentation and timezone effects, rank alternatives, and emit a signed approval artifact. /execute must reject calendar mutations unless the artifact is explicitly approved and its source snapshot is still fresh.
- **owner gets:** Instead of discovering after booking that a meeting makes the day impossible, the owner gets one short, actionable recommendation with the real consequences and can approve a safe change confidently.
- effort: Medium: calendar adapters and location normalization, an impact-scoring service, stale-snapshot checks, and a dashboard/pendant approval presentation.  ·  risk: Wrong travel assumptions or stale calendars could produce bad advice; keep it read-only by default, show assumptions and confidence, expire artifacts quickly, and require a fresh before/after diff plus explicit approval for every write. If an adapter fails, say which source was unavailable rather than guessing.
- cost: Low API cost (mostly structured extraction and cheap scoring, typically under $0.02 per scan); storage is a small event snapshot and approval record.  ·  latency: About 3–8 seconds for a warm scan, longer only when an authenticated browser source must be opened. No impact on ordinary voice turns unless requested.
- security: Meeting metadata stays on the Mac where possible; relay receives minimized event IDs, times, locations, and derived impact. Approval artifacts must be scoped to one event and one mutation, with audit receipts.
- depends on: A calendar source-precedence rule and location/travel provider; A typed approval artifact and freshness/expiry check; The existing /plan and /execute job/receipt path

### `hardware` — Replace the provisional single-button pendant input with a two-control interaction: retain the action button and add a physically latching microphone privacy slider with a visible mechanical position (and firmware state). The slider should cut microphone power locally, not merely send a software mute event; the relay and Mac must receive the mute state and refuse capture until it is reopened.
- **owner gets:** The owner can silence an always-worn microphone instantly and verify by touch, even when the network, firmware, or model is misbehaving. This makes private spaces and approval-sensitive workflows trustworthy enough to use every day.
- effort: Moderate enclosure/PCB revision and firmware/audio-state integration; validate debounce, wake behavior, and a clear tactile/LED indication.  ·  risk: A slider accidentally left muted could make commands appear broken; announce mute/unmute locally, show state in the dashboard, and let the owner query it. A hard cut may interrupt an utterance, which is preferable to recording unexpectedly.
- cost: Approximately $0.20–$1.00 incremental switch and PCB/enclosure work at volume; negligible steady-state power change, with slightly lower draw while muted.  ·  latency: Immediate local mute (electrical), with state propagation on the next link frame.
- security: Strongly improves privacy because the microphone path is physically disabled; the server must treat missing audio and explicit mute differently and never infer consent from stale state.
- depends on: Production pendant enclosure/PCB redesign (current Nordic development kit and single-button layout are provisional); Firmware audio state propagation and relay privacy-state handling

### `context` — Create a consequence-simulation layer that converts a proposed life change into a typed, reversible decision graph: affected commitments and people, minimum viable alternatives, deadlines, social impact, source evidence, confidence, and exact mutations. It must support branch comparison (skip/defer/shorten/delegate), expire when source facts change, and hand only one approved branch to /execute.
- **owner gets:** The owner can reduce an impossible day without guessing which promise matters least or discovering hidden fallout afterward. They see the human consequences before anything is sent, moved, or cancelled.
- effort: High: cross-source entity resolution, a graph of causal consequences, branch scoring calibrated by owner corrections, and a one-change-at-a-time approval UX on pendant and dashboard.  ·  risk: The model may misjudge importance or social cost. Default to recommendations only, display the evidence and uncertainty, require approval per mutation, preserve the original state, and provide an immediate undo receipt. If source freshness or identity resolution is weak, refuse to rank rather than invent certainty.
- cost: Moderate background inference cost, roughly $0.05–$0.20 for a multi-commitment simulation; most cost is extracting and reconciling private sources, not the final short judgement.  ·  latency: Warm local inputs: 5–15 seconds for a plan; individual branch comparison under 3 seconds. Long browser extraction runs as a durable job and returns a provisional, explicitly incomplete result.
- security: Keep message bodies and sensitive attendee details on the Mac/browser; relay receives minimized entities and derived effects. Store branches and evidence with short retention and sensitivity labels. No branch may invoke an irreversible action without a fresh owner approval token.
- depends on: A typed commitment/consequence schema with source, freshness, confidence, reversibility, and social-impact fields; A durable branch/approval/receipt store shared by pendant, relay, Mac, and browser; Owner-configurable protection rules and quiet-hours/interruption policy; Existing planner/executor paths must accept only a selected, still-fresh branch


## What it asked for

_Nothing._
## Its own summary

I found no new granted tools this round (the granted category is empty), but the live Mac bridge is online. The useful gap beyond the repeated browser/watch/brief backlog is a read-only calendar-impact evaluator wired between the existing planner/executor: before a meeting is booked or moved, it computes prep, travel, focus fragmentation, time zones, ranks alternatives, and emits an expiring approval artifact. I recorded both the owner-facing capability and the integration change. I also recorded a hardware privacy control, though the system flagged it as close to an existing backlog idea, so it should not be treated as novel until reconciled.

**Biggest unknown:** The authoritative calendar sources and travel/location data available to the Mac/browser are still unknown, as are the owner's rules for acceptable buffers, focus fragmentation, and meeting tradeoffs. I still need those policy facts (and the pending cross-surface persistence/approval primitives) before this can be made reliable; I did not re-request already-pending grants or the denied TCC permissions.

