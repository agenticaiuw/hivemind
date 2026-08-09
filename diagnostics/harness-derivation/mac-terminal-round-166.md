# Harness derivation — mac-terminal — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m back at my Mac. What changed since I left, and is anything waiting for me?”"
- **useful because:** The owner gets a concise, actionable delta instead of reopening every app and guessing whether an earlier pendant request finished. A departure snapshot on the Mac is compared with the return state across local jobs, browser sessions, active project, and relay events; only meaningful changes are spoken.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model computes and ranks the delta; realtime model only turns the already-ranked result into a short spoken answer when the owner asks.
- **latency:** Capture snapshot in under 2 seconds at departure; return answer under 4 seconds, dominated by authenticated browser and Mac reads.
- **cost:** About $0.01–$0.04 per return summary; most cost is one small background comparison, not realtime reasoning.
- **security:** Browser tab titles, URLs, local project names, and job outputs stay in the owner’s relay/account boundary. Never send page bodies or shell stdout unless the delta needs it; redact secrets and allow an explicit ‘private apps excluded’ list.
- **missing:** A departure/return lifecycle event from the pendant or Mac idle/lock watcher; A durable snapshot schema with per-source cursors and privacy exclusions; A relay endpoint to request a delta across Mac, browser, and pendant event streams

### "“Run that long Mac task and keep me updated without making me ask; if I press the pendant button, stop it now.”"
- **useful because:** Long shell and browser work is currently silent and cancellation is only cooperative between steps; the owner cannot tell whether a job is alive or safely stop a command already running. This gives one durable conversation: immediate dispatch, milestone-only spoken updates, truthful LED state, and a real interrupt that terminates the child process and records whether termination succeeded.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → dashboard
- **model tier:** Background model summarizes output into milestones and detects hangs; realtime handles only the short spoken update and button interaction. No expensive model is used for every output line.
- **latency:** Dispatch acknowledgment under 500 ms; milestones within 2 seconds of detection; button-to-SIGTERM under 300 ms with SIGKILL fallback after a bounded grace period.
- **cost:** $0.005–$0.03 per long task; local output parsing dominates latency, with model calls batched per milestone.
- **security:** Stream only redacted, bounded output summaries, never raw environment values or credentials. A stop press must identify the active job and require no ambiguous language confirmation; log signal, exit status, and partial side effects so the final spoken result is honest.
- **missing:** An execution stream carrying bounded stdout/stderr chunks and milestone events from /execute to relay; AbortSignal wiring from POST /jobs/:jobId/cancel through exec/execFile to the actual child process, with exit code and signal captured; A pendant-to-job stop intent that is exactly-once and scoped to the currently announced job, plus relay fanout to the Mac

### "“Do this when the Mac is ready—when Wi‑Fi is back and the right browser login is available—then tell me, even if I’m away.”"
- **useful because:** The owner should not have to retry a task after a network outage, sleeping Mac, or expired browser session. The relay keeps a durable conditional mission, the Mac reports readiness, the browser extension proves the required authenticated state without exposing credentials, and the pendant receives completion or a precise blocker later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background scheduler evaluates predicates and wakes the Mac/browser; realtime is reserved for creating the mission and speaking the final outcome. Use no model while waiting.
- **latency:** Create the mission in under 2 seconds. Predicate checks every 30–60 seconds, with immediate wake on Mac/browser heartbeats; completion notification within 3 seconds of readiness.
- **cost:** Near-zero while waiting; roughly $0.01–$0.05 when a model is needed to resolve an ambiguous blocker or summarize the result.
- **security:** Store predicates and capability scopes, not passwords or page bodies. Browser proves ‘session authenticated and matching origin’ via a nonce-bound heartbeat. Require explicit owner wording for destructive queued work, expire stale missions, and never run against a different tab/account than the one bound at creation.
- **missing:** A durable conditional-job record with predicates, expiry, wake sources, and exactly-once execution state; Mac and browser readiness events with nonce/session binding rather than polling-only status; Relay scheduler and notification fanout to the pendant, with a clear offline/away delivery policy

### "“Don’t interrupt me while I’m focused. Keep watching my Mac and browser, and tell me only the things that became urgent when I naturally pause.”"
- **useful because:** The owner gets the benefit of an always-awake assistant without being constantly broken out of concentration. The Mac contributes foreground-app and idle transitions, the browser contributes authenticated-session changes, the relay ranks events over time, and the pendant delivers one compact digest at a safe attention boundary rather than a stream of alerts.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A small background model classifies and ages events; realtime is used only for the brief spoken digest at an attention boundary.
- **latency:** Capture events immediately; classify within 10 seconds; deliver within 2 seconds of a verified pause or app-switch boundary.
- **cost:** Approximately $0.01–$0.05 per digest, mostly background ranking; event capture and quiet-period tracking are local and cheap.
- **security:** Keep event bodies local or encrypted; send the relay only redacted titles, urgency, source, and expiry. Never infer availability from keystrokes alone. Let the owner define apps and browser origins that are always private, and expire stale alerts rather than escalating them indefinitely.
- **missing:** A Mac attention-state stream (foreground app, lock/unlock, idle and app-switch boundaries) with privacy-preserving event summaries; A browser event feed for session/page changes that can be bound to the active authenticated session without exporting page content; A relay-side attention ledger that deduplicates, ages, suppresses, and releases events exactly once to the pendant


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: (1) a departure/return delta briefing spanning Mac jobs, active project, browser sessions, and relay events; (2) live long-task milestones plus a pendant stop button that actually interrupts the child process; and (3) conditional missions that wait for Wi‑Fi/browser readiness and finish while the owner is away. I also confirmed the shipped Mac surface is still POST /execute with GET /jobs/:jobId and receipts, while /pipeline/stream timed out during probing. The rejected repair-loop idea collided with an existing backlog item, so I did not rephrase it.

**Biggest unknown:** Whether the relay already has a durable conditional scheduler and whether browser heartbeats expose enough authenticated-origin/session identity to bind a queued mission safely; both need an implementation-level inventory before being claimed as merely connective work.

