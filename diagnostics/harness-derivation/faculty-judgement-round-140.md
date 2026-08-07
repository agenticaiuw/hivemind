# Harness derivation — faculty-judgement — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep an eye on the commitments I care about, and warn me only when something genuinely threatens them.”"
- **useful because:** The owner can name outcomes rather than micromanage tasks. The relay maintains the goals, Mac reconciles Calendar, Mail, Notes and local files, the browser checks private work portals, and the pendant delivers one brief warning with the evidence and the smallest suggested intervention. It detects a changed deadline, a conflicting booking, or an unanswered dependency as a threat—not merely another notification.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-action
- **model tier:** background for periodic reconciliation; realtime only to explain a surfaced threat
- **latency:** Background scans within 5 minutes of a relevant change; spoken warning starts in under 2 seconds after arbitration
- **cost:** Roughly $0.01–$0.05 per daily goal scan, dominated by private-page extraction and synthesis; near-zero when no source changed
- **security:** Goal names and evidence may include sensitive work or health data. Keep source excerpts on the Mac, send only normalized threat facts to relay, and require confirmation before external edits, messages, or bookings.
- **missing:** goal definitions with owner-set priority and expiry; cross-source dependency/impact inference; change-triggered reconciliation rather than fixed polling; a concise pendant threat card with dismiss/snooze/escalate

### "“Before I commit to this, show me what it will break, what it will postpone, and the least disruptive way to do it.”"
- **useful because:** This gives the owner a consequence map before saying yes: calendar conflicts, deadlines, travel time, dependent tasks, and private-account changes are read across surfaces, then the system presents two or three reversible alternatives. It is not a generic to-do list or a draft transaction; it answers the human question “what happens if I accept this?”
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for evidence collection and schedule simulation; realtime for the final short explanation
- **latency:** Return a first consequence sketch in 5 seconds for local sources; allow up to 30 seconds for authenticated portals and travel data
- **cost:** About $0.03–$0.15 per invocation, mostly model reasoning over extracted evidence; cache unchanged calendar and portal facts
- **security:** Simulation must be read-only and label inferred consequences versus confirmed facts. Keep sensitive page contents on Mac where possible; require explicit confirmation before applying any reschedule, cancellation, or message.
- **missing:** a read-only impact simulator over Calendar, reminders, files and browser sessions; dependency edges with confidence and time-window arithmetic; a compact before/after consequence card and alternative ranking; a hard no-mutation execution mode for simulation

### "“Put me in work mode, and make sure nothing from my personal life leaks into work—or comes back the other way.”"
- **useful because:** The owner gets a practical boundary between identities, not merely a privacy setting: the pendant, relay, Mac projects, and authenticated browser sessions cooperate to classify the current context, suppress cross-context facts and suggestions, and warn before a draft, reminder, or lookup crosses the boundary. It protects against the uniquely human failure of saying the right thing in the wrong account or carrying a private detail into a work action.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A cheap background classifier maintains context boundaries; realtime is used only when a boundary conflict needs an immediate spoken explanation.
- **latency:** Mode changes should take effect in under one second; conflict checks under 300 ms for local actions and under 2 seconds for browser preparation.
- **cost:** Approximately $0.005–$0.03 per context transition and action check, dominated by classification; local Mac rules can make routine checks effectively free.
- **security:** This is security-sensitive: classification must fail closed for uncertain destinations, never transmit excluded source content to relay, and show the owner the exact boundary decision. Switching modes should require an explicit pendant button/voice confirmation, with an emergency local lockout.
- **missing:** first-class named contexts with separate fact, session, and action scopes; per-context allow/deny rules enforced by relay, Mac, and browser before retrieval and mutation; a context transition audit trail and owner-visible explanation; safe handling of ambiguous mixed-context requests


## Changes it proposed to its own stack

### `hardware` — Add a low-current vibration motor (with a transistor driver and flyback protection) to the pendant, expose a three-pattern haptic API, and reserve one pattern for an authenticated relay/Mac attention event. Add a firmware kill switch and duty-cycle limiter so the motor cannot drain the cell or buzz continuously.
- **owner gets:** The owner gets a genuinely silent, glance-free signal in a meeting, while walking, or when audio is unavailable. A short pulse can mean “your requested job is ready” without making them listen to every notification.
- effort: Small PCB spin or daughterboard, one GPIO and driver transistor, firmware PWM pattern task, and relay event mapping; validate current draw and accessibility with the owner.  ·  risk: Motor noise may leak into the microphone, vibration may be mistaken for a fault, and a stuck GPIO could drain power. Recover with hardware timeout, watchdog-off default, explicit test mode, and audio/LED fallback.
- cost: Approximately $2–$6 in components/board area and 10–80 mA only during pulses; no model/API cost.  ·  latency: Under 100 ms from a received event to the first pulse when the link is live.
- security: Haptic events must be limited to authenticated, typed event classes; never encode secrets in pulse patterns. A local physical stop should cancel it.
- depends on: a live pendant transport over the currently real USB serial connection; typed attention events and delivery acknowledgements; firmware GPIO allocation and power-budget validation


## What it asked for

_Nothing._
## Its own summary

Round 140 produced three non-duplicate directions. 1) Goal Guardian: continuously reconcile owner-named outcomes against Calendar, Mail, Notes/files, and authenticated browser changes, surfacing only evidence-backed threats and the smallest intervention. This is the strongest candidate for the system’s most useful everyday behavior. 2) Counterfactual Commitment Preview: before accepting an invitation or commitment, simulate conflicts, postponed dependencies, and alternatives in a strictly read-only mode. 3) Silent Haptic Attention: add a low-current vibration motor and authenticated typed event patterns so the pendant can signal a completed job or urgent threat without interrupting a meeting. All were recorded.

**Biggest unknown:** The missing connective primitives are still the real blockers: durable goal definitions/expiry, cross-source dependency and impact inference, a read-only simulation/no-mutation mode, typed attention delivery acknowledgements, and a live pendant transport. The pendant and ESP32 are physically USB-connected today, but the pendant is not relay-registered; haptics also need a hardware spin and power/GPIO validation.

