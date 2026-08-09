# Harness derivation — relay-realtime — round 260

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Let me know when that finishes, even if I walk away."
- **useful because:** This is the daily-driver feature: the owner can start a task by voice, then stop thinking about it and get a spoken update when it finishes or needs attention.
- **path:** relay → mac-bridge → pendant
- **model tier:** relay realtime for the initial voice, cheaper background model for status polling and summarization
- **latency:** Start is immediate; completion can arrive minutes or hours later. Spoken summary should be under 2 seconds.
- **cost:** Low per start; ongoing cost is periodic job status reads and a short summary render.
- **security:** Job status may include filenames or recipients; summaries should be minimal and avoid sensitive content unless the owner asks.
- **missing:** A real implementation for asynchronous event delivery from relay to pendant/phone; A durable watcher that survives voice session end and polls job state without a live conversation

### "Open the thing I was working on and get it ready."
- **useful because:** The owner can resume context quickly: the browser or app is opened, relevant tabs or files are focused, and a short status is spoken back.
- **path:** relay → mac-bridge → browser → mac-vision
- **model tier:** relay for intent capture, mac planner for actions, browser extension for session control
- **latency:** 1-3 seconds to start; longer to stabilize browser session.
- **cost:** Planning cost dominates; execution is bounded to a small action list.
- **security:** Opening work may expose private content; only operate on the owner’s machine and avoid sharing content off-device.
- **missing:** A reliable intent routing implementation at relay (current schema is not wired); Server-side browser fallback if the Mac is offline

### "“When I’m away, keep working on this exact task across my logged-in browser and Mac; when it is ready, tell me what changed and give me a one-sentence decision to make.”"
- **useful because:** Today a voice request can be handed off, but a long task loses the owner's intent and context when the live turn ends. This would turn the pendant into a durable, resumable work session: browser research, Mac edits, and a concise decision-ready handoff rather than a dead job or a generic completion ping.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime handles intent capture and one clarifying question; a cheaper background planner coordinates the Mac/browser steps, with a small final summarizer for the decision packet.
- **latency:** Immediate spoken acceptance under 1 second; work may run for minutes or hours; completion should be pushed without polling and include checkpoint updates only on meaningful state changes.
- **cost:** Moderate: planner calls scale with checkpoints, but summaries should use a cheaper tier and only send diffs/evidence, not full transcripts or pages.
- **security:** Authenticated browser sessions and local files are sensitive. Persist only the minimum task state, redact secrets from checkpoints, bind jobs to the owner and originating pendant session, and make external sends/purchases/deletions explicit decisions rather than inferred completion.
- **missing:** A durable task/session record containing intent, constraints, evidence, checkpoints, and resumable cursor; A coordinator that can pause and resume across Mac availability and browser-session availability; A decision-packet format with claims, evidence links, unresolved risks, and exactly one next decision; Reliable completion delivery through the existing inbox/event path

### "“Put my Mac and browser into ‘leave-home’ mode, and let me undo it from the pendant if I change my mind.”"
- **useful because:** A worn, always-present physical control can close the gap between leaving the desk and remembering to secure work: pause distracting apps, lock or hide sensitive windows, save browser work, and record exactly what was changed. A later pendant press can reverse the reversible subset without finding the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime interprets the named mode; a deterministic action bundle executes the reversible steps, while a cheap planner resolves the current app/tab state and produces a receipt.
- **latency:** Spoken confirmation in under 1 second; apply in under 10 seconds; undo should begin immediately and report per-action failures.
- **cost:** Low to moderate: one planning call plus Mac/browser actions; cost is dominated by state inspection and any app-specific save/restore work.
- **security:** Locking, hiding, and closing apps can interrupt unsaved work. Default to save/minimize/lock rather than kill, retain an undo journal, never expose secrets in spoken receipts, and require a deliberate long press or spoken confirmation for irreversible close/logout actions.
- **missing:** A named mode/action-bundle registry with preflight and inverse actions; Mac/browser state capture sufficient for reliable undo; A pendant command path for authenticated mode activation and undo while the Mac is unattended; An atomic receipt that distinguishes applied, skipped, and failed actions

### "“If I walk away from my Mac while the pendant is still in an active work session, automatically save a checkpoint, pause anything risky, and tell me on the pendant what was secured.”"
- **useful because:** The pendant is the one surface that travels with the owner, so physical departure can close the dangerous gap between leaving the desk and leaving browser sessions or unsaved work exposed. This is not a timer or a generic lock command: it binds a real proximity transition to a cross-device checkpoint, with a truthful spoken result and recovery when the owner returns.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** A deterministic proximity/session policy handles the trigger and safe reversible actions; use the realtime model only to explain exceptions, and a cheaper planner for app/browser checkpoint reconciliation.
- **latency:** Detect departure within 5–15 seconds; start protection immediately; spoken pendant status within 10 seconds. Return should not replay or undo anything without an explicit owner request.
- **cost:** Low steady-state cost if proximity is firmware/bridge telemetry; occasional planner calls on departure and return. The main cost is implementation and encrypted event storage, not inference.
- **security:** False departures must not close or destroy work. Default to save/minimize/pause/lock, never terminate processes; require an enrolled pendant and authenticated pairing; keep a tamper-evident action receipt and let the owner undo only reversible changes. Do not use the proximity signal to infer location beyond the local session.
- **missing:** A reliable pendant-to-Mac proximity signal beyond the current USB serial attachment, with hysteresis and reconnect semantics; An active-work-session registry spanning relay, Mac, and browser; A safe checkpoint policy with per-action inverse operations and unsaved-document handling; A device-directed result path that can distinguish secured, skipped, and failed actions


## What it asked for

_Nothing._
