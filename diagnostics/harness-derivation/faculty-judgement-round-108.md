# Harness derivation — faculty-judgement — round 108

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a meeting starts, quietly get me ready, help me capture commitments during it, and leave me a reviewable follow-up packet afterward."
- **useful because:** Today preparation, live capture, and follow-up are disconnected. This would turn the pendant into a low-friction meeting companion: it uses the Mac's calendar and private browser context for preparation, the pendant for discreet capture while walking or away from the keyboard, and the relay to finish the packet after the meeting. It never sends anything without approval.
- **path:** mac-planner reads the next calendar event and gathers its agenda, attendees, related notes, and open browser tabs; browser-extension reads only already-open authenticated tabs relevant to that event and cites each fact; relay-realtime gives a brief spoken or LED-only pre-meeting cue and accepts short pendant utterances such as “commitment: send the estimate Friday” or “park that”; unified correlates utterances with the meeting's time window and participant context; mac-planner writes a dated meeting packet into ~/AI-Pendant-Workspace containing decisions, commitments, owners, due dates, unresolved questions, evidence links, and confidence; pendant plays a short post-meeting summary when the owner is available.
- **model tier:** Use the cheaper background model for pre-meeting retrieval, transcript cleanup, deduplication, and packet assembly; reserve realtime only for the brief cue and live utterance acknowledgement. Escalate to the expensive judgement tier only when owner, due date, or commitment attribution is ambiguous.
- **latency:** Pre-meeting packet ready 2 minutes before the event or on explicit request; pendant acknowledgement under 1 second; post-meeting packet within 2 minutes of the event ending. If calendar/browser access is unavailable, produce a clearly incomplete packet rather than inventing facts.
- **cost:** About $0.01–$0.05 per meeting for background extraction and summarization, depending on transcript length; realtime cost is limited to a few short turns. Mac and browser work dominate operational complexity, not tokens.
- **security:** Meeting speech and private-tab data may leave the device to the relay/model, so default to local Mac notes and redact unrelated tab content. Do not infer or expose attendee-sensitive details beyond the meeting packet. Require explicit approval before sending follow-up email, creating external tickets, or changing calendar events; show source snippets and proposed recipients.
- **missing:** A calendar-event identity and time-window correlation service shared by relay, Mac, and browser; A pendant capture mode that queues timestamped utterances offline and syncs them when the link returns; A meeting packet schema with provenance, confidence, owner/due-date fields, and a review UI; A reliable post-event trigger and availability check so the summary is not spoken during another conversation

### "Before I commit to a time, deadline, or promise anywhere, quietly tell me if it will make another commitment impossible and suggest the safest wording or alternative."
- **useful because:** People often make commitments in separate contexts—an email, a calendar invite, a private portal, or a conversation—and only discover the collision afterward. This would give the owner a last-second, evidence-backed judgment before a promise becomes real, while leaving the final decision with them.
- **path:** browser-extension detects a proposed date, deadline, recipient, or submission in the currently active authenticated page without submitting it; mac-planner checks Calendar, reminders, travel context, and existing reviewable commitments; relay holds a short-lived cross-surface conflict assessment and sends a discreet spoken or LED warning through the pendant when confidence is high; unified presents two or three feasible alternatives with the exact conflicting sources; browser or Mac fills only the chosen revised wording/time after explicit owner approval, then stores a receipt.
- **model tier:** Use a cheap background model to normalize dates and compare candidate times. Use the realtime tier only when the owner is actively composing or speaking and needs an immediate warning. Escalate ambiguous interpretation to judgement rather than silently blocking.
- **latency:** Warn within 1–2 seconds of a detected candidate commitment; if evidence is incomplete, say so and do not interrupt. A detailed alternative list may arrive asynchronously before submission.
- **cost:** Under $0.01 for most checks with compact structured context; occasional long-page extraction may cost $0.03–$0.08. The dominant cost is private-context retrieval and browser/Mac orchestration, not generation.
- **security:** Commitment data is highly personal. Keep raw drafts and unrelated page text local where possible, send only normalized candidate facts and minimally necessary sources, and never transmit or submit revised wording without confirmation. Do not infer obligations from sensitive messages unless the owner has enabled that source.
- **missing:** A commitment candidate extractor that works on draft text and spoken utterances without taking control of submission; A temporal feasibility evaluator that distinguishes hard conflicts from movable commitments and exposes its evidence; A low-disruption pendant warning channel with suppression during conversations or quiet hours; A confirmation-linked mutation path that can revise the originating draft and record before/after provenance


## Changes it proposed to its own stack

### `integration` — Add a durable Meeting Episode Coordinator spanning calendar event IDs, browser tab/session provenance, pendant utterance timestamps, and Mac packet files. It opens an episode shortly before an event, accepts append-only capture records during the event (including offline records with monotonic sequence numbers), closes it at event end, and emits a reviewable packet with every claim linked to its source or explicitly marked owner-spoken. Reopening an episode is idempotent; unrelated tabs and speech are excluded by default.
- **owner gets:** The owner can say a commitment once while their hands are busy and later find exactly what was decided, who owns it, and why the system believes it—without trusting a vague AI summary or losing notes when the network drops.
- effort: Medium-high: shared event identity and lifecycle service, pendant queue/sync protocol, Mac packet renderer, and tests for overlapping meetings, timezone changes, missed close events, and duplicate delivery.  ·  risk: A wrong calendar match could attach private notes to the wrong meeting. Fail closed when identity or timing is ambiguous, show the event title before capture begins, encrypt local records, and retain append-only raw captures only briefly. If closure fails, leave the episode explicitly open rather than silently summarizing.
- cost: Small persistent metadata and local file storage; background model calls roughly $0.01–$0.05 per meeting. Pendant firmware adds a bounded queue, likely tens of KB, with no meaningful ongoing power cost beyond normal radio sync.  ·  latency: Capture acknowledgement remains sub-second; packet assembly can complete asynchronously within two minutes. Offline utterances become visible after reconnect rather than being dropped.
- security: Calendar titles, attendee names, and spoken commitments are sensitive. Use event-scoped least-privilege projections, redact unrelated browser content, encrypt queued captures, and require approval for any outbound follow-up.
- depends on: A shared durable event/episode identifier across relay and Mac; An offline pendant capture queue and reconnect protocol; A provenance-aware meeting packet schema and review surface; A post-event trigger plus owner availability/quiet-hours check

### `hardware` — Add a dedicated, electrically hard-wired microphone privacy slider to the pendant with a visible red mechanical position and a firmware-readable state. The mute path should disconnect or gate the microphone before the application processor, emit a local click/LED confirmation, and include the mute state in every relay presence/status event. It must remain muted across reconnects and reboot until physically switched back.
- **owner gets:** The owner can carry an always-listening device in meetings, at home, or around other people without having to trust software or remember a spoken command. They get an unmistakable physical guarantee that no audio is being captured.
- effort: Medium hardware revision plus enclosure, PCB, firmware, and relay status handling; validate that boot, brownout, and reconnect paths cannot silently unmute.  ·  risk: The switch could be bumped and cause missed commands, or its state could disagree with software. Fail safe toward muted, announce “microphone muted” locally, and show the state in the pendant LED and Mac dashboard. A self-test should detect switch/wiring disagreement.
- cost: Roughly $0.20–$1.00 in switch, PCB, and enclosure changes at prototype quantities; negligible steady-state power draw, with a small GPIO/input pull resistor cost.  ·  latency: No network latency; local mute takes effect electrically in milliseconds. Re-enabling capture may require a one-time handshake so the relay does not assume audio is available prematurely.
- security: Substantially reduces accidental audio exfiltration and gives the owner a trustworthy hardware boundary. The relay must treat missing or stale mute telemetry as unknown, never as unmuted.
- depends on: Pendant PCB/enclosure revision; Firmware boot and reconnect fail-closed behavior; Relay presence/status schema carrying microphone state; Dashboard and spoken-status handling for mute state


## What it asked for

_Nothing._
## Its own summary

Discovered the current backlog and owner constraints, then added a new end-to-end capability: a discreet meeting companion that prepares from Calendar/private browser context, accepts timestamped pendant commitment captures (including offline), and produces a cited, reviewable follow-up packet without sending anything automatically. I also proposed the Meeting Episode Coordinator integration to make event identity, provenance, offline sync, and safe closure durable. I do not need Accessibility permissions for this design.

**Biggest unknown:** Whether the current stack already has authoritative Calendar event IDs, a durable pendant capture queue, and an owner-availability/quiet-hours signal. Those determine whether this can be implemented mostly from existing routes or needs new primitives.

