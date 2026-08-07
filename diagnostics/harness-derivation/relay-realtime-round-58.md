# Harness derivation — relay-realtime — round 58

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this task from my pendant, keep working while I’m away, tell me when you reach a meaningful checkpoint, and let me interrupt, redirect, or ask ‘where are you?’ by voice—even if the LTE link briefly drops.”"
- **useful because:** Today a spoken request is effectively a one-shot handoff: the owner cannot maintain a conversational control channel to a running Mac/browser job while away from the Mac. This would make the pendant a reliable remote presence and control surface for long-running, multi-surface work, rather than merely a request button or final-result speaker.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Use relay-realtime only for utterance recognition, interruption handling, and concise spoken status. Send planning and execution to mac-planner/mac-vision, and use a cheaper background summarizer for checkpoint compression and final receipts.
- **latency:** Acknowledge speech in under 500 ms; interruption/cancel command should reach the active executor within 2 s when online. Checkpoint notices may arrive within 10–30 s of an executor event. On reconnect, replay only the newest unacknowledged status, not the whole transcript.
- **cost:** Roughly one realtime turn per owner utterance plus inexpensive background summarization per checkpoint; dominant cost is long-running Mac/browser execution and any repeated context, which should be avoided with a compact durable task state rather than resending conversation history.
- **security:** Task state and spoken status can expose private Mac/browser data over LTE. Persist opaque task identifiers and redacted checkpoint summaries by default, keep detailed evidence on the Mac/relay, encrypt the event stream, and let the owner explicitly enable sensitive-content readback. Cancellation and redirection should be honored as control messages, while ordinary reversible actions need no confirmation under the owner's policy.
- **missing:** A durable cross-surface task/session object with append-only event and checkpoint history, correlation to Mac and browser jobs, lease/heartbeat, reconnect replay, and idempotent interrupt/redirect commands; A relay-to-pendant downlink event channel with notification priority, acknowledgement, deduplication, and a compact spoken-status format; A Mac planner/executor protocol that can pause at safe checkpoints, report typed progress, accept redirect/cancel, and resume without losing state; Browser-session hooks that associate authenticated tab work with the same task object and report navigation/authentication failures without leaking page contents; Pendant-local short-lived outbound command and inbound-notification queue for link loss, plus a user-visible policy for which events may be spoken aloud; Dashboard controls to inspect the live task timeline, change notification verbosity, and recover or terminate orphaned tasks


## Changes it proposed to its own stack

### `integration` — Add a cross-surface continuity ledger for voice tasks: when relay hands a job to Mac or browser, it stores a compact task record (intent label, normalized utterance, target surface, jobId/sessionId links, start time, last heartbeat, and a rolling result summary). Pendant can ask for status later; relay answers from the ledger first, then fans out to Mac/browser only if needed. Include a small audio-first schema: what to say next, what changed since last check, and whether the owner needs to act.
- **owner gets:** They can ask "what happened with that?" hours later while away from the Mac and still get a coherent answer, even if the browser is offline or the Mac is asleep. It reduces confusion and prevents duplicate actions.
- effort: Medium: define typed records and lifecycle, add persistence (Durable Object or KV with DO), instrument relay handoff points, and add reconciliation hooks for Mac/browser receipts.  ·  risk: Ledger drift if receipts aren’t delivered. Mitigation: idempotent updates, explicit terminal states, and a human-readable conflict state that asks the owner what to do next.
- cost: Low ongoing API cost; storage in KV/DO is small. Biggest cost is engineering time and a few extra writes per task.  ·  latency: Improves perceived latency because most status checks resolve at relay without cross-surface calls.
- security: Stores task metadata and summaries; must minimize sensitive content, encrypt at rest if possible, and avoid storing full transcripts unless necessary.
- depends on: Reliable receipts from Mac/browser for terminal states (or a timeout policy).; A small persistence layer wired to the relay (Durable Object preferred).

### `hardware` — Add a tiny coin-cell haptic motor (with a dedicated low-side driver and firmware notification patterns) to the pendant, and expose a relay notification-priority channel that maps Mac/browser task events to silent, private haptic alerts. Keep the existing LED/button as fallback and make patterns locally renderable so an alert still fires during a brief uplink interruption after the event has been delivered.
- **owner gets:** The owner can be away from the Mac, in public, or unable to hear speech. They would still know that a genuinely urgent result, failure, or requested decision is waiting, without broadcasting private content or staring at a screen. Different short patterns could distinguish completion, failure, and “open the voice channel.”
- effort: Moderate hardware revision and enclosure/power validation; firmware driver, pattern table, acknowledgement semantics, relay event priority/coalescing, and Mac/browser event adapters. Requires end-to-end testing with LTE loss and low battery.  ·  risk: Added vibration may be distracting, drain the battery, or create false urgency. Limit intensity/duty cycle, coalesce repeated events, provide quiet hours and a physical dismiss gesture, and fall back to LED/audio when unavailable. Never include sensitive text in the notification payload.
- cost: Approximately $1–$3 in components and a small PCB/enclosure change; roughly 5–20 mA only while vibrating, with negligible idle draw. API cost is negligible; event summarization remains background-tier.  ·  latency: A delivered urgent event can alert in under 300 ms locally; LTE delivery remains network-dependent. Firmware must retain only a small bounded alert record, not a transcript.
- security: Improves privacy by replacing spoken sensitive alerts with opaque patterns, but requires authenticated downlink and replay protection so an attacker cannot nuisance-alert the owner.
- depends on: Authenticated relay-to-pendant downlink event channel with priority and acknowledgement; A durable event taxonomy shared by Mac planner, Mac vision, and browser sessions; Updated pendant hardware and firmware power-management support


## What it asked for

_Nothing._
## Its own summary

Recorded two non-backlog proposals: (1) a reconnectable, interruptible voice-controlled task session spanning pendant, relay, Mac, and authenticated browser work; (2) a haptic pendant plus prioritized private notification channel for urgent cross-surface events when speech or screens are unavailable. Both explicitly identify the missing infrastructure and hardware.

**Biggest unknown:** Whether the pendant enclosure, battery budget, and board revision can accommodate a haptic motor and driver without compromising its LTE/audio runtime.

