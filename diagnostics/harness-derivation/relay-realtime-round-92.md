# Harness derivation — relay-realtime — round 92

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask you to do something across my Mac or logged-in browser, let me later ask “what actually happened?” and hear one trustworthy answer that ties my spoken request to every attempted action, browser result, partial failure, and final evidence—without making me repeat which device or task I mean."
- **useful because:** Today status is fragmented: a voice turn, a Mac job, and a browser command can each have separate identifiers and receipts. The owner cannot reliably distinguish queued, attempted, completed, or merely reported work while away from the Mac. A single causal answer would make remote delegation trustworthy and let the owner recover from partial completion by voice.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay resolves the owner’s spoken reference and summarizes an already-recorded ledger; use the cheaper background tier to normalize receipts and reconcile late Mac/browser events. Do not spend the realtime model planning the original work.
- **latency:** A spoken status answer in under 1 second from the durable ledger; reconciliation of late events may take a few seconds and should update the next answer. No polling loop in the voice path.
- **cost:** Usually <$0.01 per status question when only structured receipts are summarized; background reconciliation is the dominant additional cost, not audio generation.
- **security:** The ledger may contain URLs, app names, snippets, and authenticated-task outcomes. Encrypt it, minimize retained payloads, redact secrets/form values, scope each entry to the paired owner, and never claim success without an evidence-bearing terminal event. Voice reference resolution should tolerate “that thing” but expose ambiguity rather than silently mixing jobs.
- **missing:** A durable cross-surface causal ledger keyed from the pendant voice-run through relay delegation, Mac plan/action receipts, browser command/result, and undo/recovery events; A common event schema with terminal states (queued, running, succeeded, failed, partial, unknown) and evidence pointers; Relay-side reference resolution over recent ledger entries and a compact spoken summarizer; Late-event ingestion and reconciliation from Mac and browser, plus dashboard inspection of the causal chain

### "While I’m away from my Mac, let me say “send the last thing I was looking at to Sam with this note” (or “save that page to my project”) and have the system resolve “that” from my active Mac/browser context, read back exactly what it identified and where it will go, then carry it out and tell me what was sent or saved."
- **useful because:** The wearable has the conversation but no screen, while the browser has authenticated context and the Mac knows the owner’s active apps. Today the owner must name URLs, files, and recipients explicitly or repeat the task at a keyboard. A voice-addressable semantic handoff turns the distributed system into one usable workspace without pretending the pendant can see.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only resolves the short spoken referent and gives a concise read-back. A cheaper background planner extracts the active page/file title, canonical URL or file path, selected text, and destination fields; browser/Mac execution remains deterministic.
- **latency:** Resolve and read back in 2–4 seconds; execution can take longer but must produce a durable result event. If context is unavailable or stale, answer that plainly rather than guessing.
- **cost:** About $0.01–$0.04 per handoff, dominated by one context-extraction/planning call; deterministic browser/Mac actions and the short realtime response are minor.
- **security:** Active context can contain private mail, work portals, tokens, or accidental selections. Do not transmit page bodies or secrets unless needed; pass title/URL/selection hashes where possible, redact credentials, and require an unambiguous spoken destination and operation. Read back the resolved source and recipient before any externally visible send; never infer a recipient from a page’s incidental text.
- **missing:** A point-in-time context snapshot API from Mac and browser with active tab/window, selection, title, URL/path, timestamp, and sensitivity labels; A referent-resolution service that binds “that/the last thing” to the snapshot closest to the voice turn and records the binding; A cross-surface handoff command carrying a typed source reference plus destination, with deterministic adapters for browser share/save and Mac file/message actions; A spoken preview/result protocol and dashboard audit showing exactly what source bytes and destination were used


## Changes it proposed to its own stack

### `relay` — Add a relay capability inventory endpoint, e.g. GET /v1/relay/capabilities, and a live routing manifest that lists implemented tools, granted schemas, and reachable downstream surfaces. Include versioned schemas for audio pipeline status (capture, transcoding, TTS, queue state) and job handoff status. The relay-realtime agent should be able to fetch this without relying on Mac routes or system prompt context.
- **owner gets:** The pendant conversation should be trustworthy: when the owner asks “are you connected, and what can you do right now?”, the relay can give a factual answer without guessing. It also reduces repeated exploratory calls that slow responses and burn budget.
- effort: Medium. Define schemas, implement read-only endpoints in the relay, and wire them to existing internal state. No UI changes required to start.  ·  risk: Low. Read-only introspection. Main risk is leaking sensitive configuration details; mitigate by redacting secrets and returning only capability flags and health summaries.
- cost: Low. A few small JSON responses. Biggest cost is engineering time.  ·  latency: Positive. Fewer blind probes and less round-tripping to Mac endpoints.
- security: Moderate if mis-scoped. Requires careful redaction and access control; only expose to paired devices and internal agents.

### `integration` — Define and implement a real intent-routing tool for relay-realtime (implement the granted relay_route_intent schema) that accepts a small set of intent labels, routes them to mac-planner or mac-vision, and returns a job handle plus a spoken status string. Pair it with a real relay_job_status implementation for plan jobs. Keep it read-only until execution is explicitly requested via existing tools.
- **owner gets:** Voice feels seamless: the owner can say a goal once, the relay can hand it off safely, and the owner can later ask what happened without repeating themselves. It also avoids inventing ad-hoc protocols and reduces errors.
- effort: Medium to high. Requires backend implementation, job tracking, and alignment with mac-planner’s plan/execute lifecycle.  ·  risk: Medium. Misrouting could trigger unintended actions. Mitigate with narrow intent labels, conservative defaults, and explicit execution steps.
- cost: Low per call. Engineering cost dominates.  ·  latency: Positive for the owner (fewer conversational detours).
- security: Moderate. Needs authentication, authorization, and careful logging to avoid leaking sensitive task details.
- depends on: Implement or connect a durable job runner for planned work (mac-harness / backend)

### `hardware` — Add a low-power coin ERM/LRA haptic actuator and a tiny driver to the pendant, with firmware patterns for listening, task accepted, task completed, needs-attention, and failed/offline. Keep all semantic content in audio; haptics are only nonverbal state cues and must be suppressible.
- **owner gets:** The owner can be in a meeting, walking, or somewhere noisy where spoken confirmations are inappropriate or inaudible. A private vibration would confirm that the pendant heard a button press or that a delegated Mac/browser task finished, without requiring them to look at the single LED or interrupt conversation.
- effort: Pendant PCB revision, enclosure/mechanical validation, a small firmware state machine, and relay event mapping; roughly 1–2 hardware iterations plus firmware/integration work.  ·  risk: Added vibration can be distracting, drain the battery, or be confused with an alert. Use short distinct patterns, a quiet-hours setting, watchdog shutoff, and fall back to the LED/audio path if the driver faults. Do not make haptics the only indication of a safety-critical condition.
- cost: Approximately $2–$8 BOM increase at low volume, plus PCB/enclosure changes; roughly 5–20 mA only during brief pulses and effectively zero at idle. No per-invocation API cost.  ·  latency: No meaningful network latency; local acknowledgement can occur within tens of milliseconds. Completion patterns wait for the existing relay/Mac/browser event.
- security: No new data leaves the device. Firmware should expose only coarse event classes, not private task text; avoid encoding sensitive information in vibration patterns.
- depends on: A reliable typed event stream from relay to pendant for accepted/completed/attention-needed states; A user setting controlling haptic enablement, intensity, and quiet hours; Battery and enclosure redesign validation


## What it asked for

_Nothing._
## Its own summary

Recorded three proposals: a cross-surface causal action ledger for trustworthy spoken status, voice referent resolution across active Mac/browser context, and a local haptic state channel for private confirmations. The first two require new connective APIs and event schemas; the hardware proposal requires a pendant revision and firmware integration.

**Biggest unknown:** Whether the backlog already contains an equivalent cross-surface referent resolver or haptic feedback proposal; discovery was explicitly stopped this round, so I did not re-check it.

