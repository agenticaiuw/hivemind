# Harness derivation — relay-realtime — round 33

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that after I walk away, and tell me exactly what happened when it’s done."
- **useful because:** The owner can start a long task by voice and then leave. They get a reliable spoken outcome later without babysitting a screen, even if the Mac sleeps or the browser session changes.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the initial conversation, cheaper planner/executor for the long work, and a lightweight relay formatter for status updates.
- **latency:** Start quickly (under a second to acknowledge), then run asynchronously. Status updates can be delayed but must be clear and final.
- **cost:** Low for the relay acknowledgement; medium for planning; variable for browser/Mac execution depending on steps and extraction.
- **security:** Must not claim completion without a verified receipt. Sensitive data from authenticated pages stays on the Mac/browser harness; only minimal status text and evidence hashes should leave.
- **missing:** durable job runner across relay and browser/Mac; typed receipts with source evidence; reliable notification channel back to the pendant (or a queue the pendant can poll)

### "While I’m away from my Mac, let me say “what did you find?” or “change the second one” and have the pendant continue the exact Mac/browser task that produced the result, using the prior evidence and current session—not start over."
- **useful because:** Today a voice request is effectively a one-shot handoff: once the Mac or browser acts, the owner cannot naturally inspect, disambiguate, or revise the result from the pendant. This would make remote work feel like an ongoing conversation and would be especially valuable for authenticated browser tasks and ambiguous search results.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use relay-realtime only to resolve the short follow-up and identify the active task; use the cheaper Mac planner for action planning and browser harness for session-bound work. Use a background model only to compress large evidence into a spoken-sized summary.
- **latency:** Acknowledge the follow-up in under 500 ms; return a concise evidence summary in 2–4 s when cached, or stream progress while Mac/browser work runs. The owner should be able to interrupt, correct, or cancel by voice.
- **cost:** Roughly one realtime turn for intent resolution plus one planner call per actual continuation; dominant cost is planner context and any browser vision, not the short relay exchange. Cache typed receipts/evidence so ordinary follow-ups avoid resending full transcripts or screenshots.
- **security:** The relay must bind follow-ups to the owner’s authenticated pendant session and an explicit task handle, never infer a sensitive task from vague history. Browser evidence may contain private mail/work data; retain only encrypted, redacted summaries by default, with configurable expiry. Destructive continuation should be announced, while reversible actions can follow the owner’s stated maximum-access policy.
- **missing:** A durable task ledger with owner-scoped handles, lifecycle/expiry, evidence snapshots, and parent-child continuation links across relay, Mac planner, and browser sessions.; A typed continuation protocol carrying task handle, evidence references, current browser tab/session identity, and planner state; it must support pause, cancel, correction, and conflict detection when the underlying page or Mac state changed.; A pendant-facing notification and interruption channel for completion, ambiguity, failure, and cancellation, plus compact spoken summaries and a way to select items by ordinal.; A dashboard view showing active/paused/expired tasks and exactly what evidence is retained, without exposing raw authenticated content by default.


## Changes it proposed to its own stack

### `routines` — Add a cross-surface durable job ledger with receipts. A submitted job gets a stable id, typed steps, and a receipt trail (status, timestamps, evidence references). The relay can query it at any time and read back a short, pre-approved spoken summary.
- **owner gets:** They can ask “what happened with that?” and get a truthful answer even if the Mac slept, the browser session rotated, or the network dropped.
- effort: Medium-large: define a job schema, implement a durable store (Durable Object or D1), unify receipts from Mac and browser harnesses, and add relay read APIs.  ·  risk: Schema drift and partial failures. Mitigate with idempotency keys, step retries, and a ‘stuck’ state with recovery actions.
- cost: Small per job (metadata + receipts). Storage grows with history; add retention policies.  ·  latency: Adds a small write on each step; reads are fast and local to the relay store.
- security: Receipts must avoid leaking sensitive content; store hashes and pointers, not raw secrets.
- depends on: typed result receipts from Mac/browser actions; a persistent store available to the relay

### `integration` — Add an ambiguity-resolution loop between mac-planner/browser and relay-realtime. Downstream agents should return a typed `needs_owner_input` event containing the competing interpretations, minimal evidence excerpts, confidence, expiry, and safe default; relay turns that into a one-sentence spoken question, maps the owner’s ordinal/free-form answer back to the same job, and resumes without replaying completed steps. If the owner is unavailable, the job pauses rather than guessing.
- **owner gets:** A remote voice request often encounters exactly one missing fact— which account, which document, which of two matching contacts, or what “latest” means. Today the system either guesses or fails after handing work away. The owner could answer one tiny question from wherever they are and avoid reopening the whole task or touching the Mac.
- effort: Medium-high: typed event schema and state machine in relay/bridge, planner prompt and resume support, browser evidence extraction, pendant interruption/timeout handling, and dashboard observability. Test with stale tabs, duplicate search results, network loss, and an answer arriving after expiry.  ·  risk: A badly phrased question could expose sensitive page content or cause the owner to choose the wrong item. Limit excerpts to redacted labels, include source/app and a short ordinal list, expire questions, and record the selected interpretation in the job receipt. On timeout, pause and report rather than act on a guessed default.
- cost: Small additional relay realtime turn only when ambiguity occurs; planner/browser costs are otherwise unchanged. Storing compact typed alternatives is cheaper than repeatedly sending screenshots or full transcripts.  ·  latency: Fast acknowledgement immediately; clarification should reach the pendant within 1 s of downstream detection and resume within normal planner latency after the answer.
- security: Improves security by preventing silent guesses, but requires owner-session binding and encrypted, short-lived ambiguity payloads. Do not put raw authenticated browser text in push notifications or durable logs.
- depends on: A durable continuation/task ledger and task handles shared by relay, Mac planner, and browser harness.; A pendant notification/interruption channel and typed downstream event transport.; Redaction and ordinal-selection support for browser/Mac evidence.

### `hardware` — Add a coin vibration motor with a low-side driver and expose three firmware patterns (acknowledged, needs-answer, completed/failed) to the relay task channel. Keep the existing LED/button as fallback, and make haptics opt-in per notification class with a local long-press mute. Firmware should queue at most one compact event while LTE is unavailable and clear stale low-priority events after reconnection.
- **owner gets:** The owner is often away from the Mac and may be unable to hear speech in a meeting, on a street, or in a noisy room. A private vibration can tell them that a delegated browser/Mac task needs a decision or finished, without reading sensitive content aloud or requiring them to stare at the pendant.
- effort: Medium hardware revision and firmware work: motor, transistor/driver, flyback protection, enclosure/acoustic isolation, battery characterization, event queue, and relay notification mapping. Validate comfort, false triggers, and operation during LTE reconnects.  ·  risk: Vibration consumes battery, can be missed through clothing, and an urgent pattern could still reveal that sensitive work is occurring. Provide disable/mute, conservative duty cycles, no content in the pattern, and LED/audio fallback only when configured. Recovery is firmware OTA disabling the motor or reverting to LED.
- cost: Approximately $1–3 in added BOM at volume (more for enclosure/assembly), plus a few mA only while vibrating; negligible API cost. Battery-life impact should be measured under a realistic notification rate.  ·  latency: Local acknowledgement can be sub-100 ms; remote task events remain subject to LTE-M latency. No model latency added.
- security: Improves privacy versus spoken notifications because patterns carry no task content. The relay must still authenticate event delivery and avoid encoding sensitive distinctions in overly elaborate patterns.
- depends on: A durable task ledger and typed task event/continuation channel.; Pendant firmware event queue and OTA update path.; Relay policy for notification priority, mute state, and owner-session binding.

### `context` — Introduce a task-evidence capsule format rather than replaying conversation history on every relay turn. Each downstream result is normalized into a small signed capsule: goal, completed actions, current state, selectable entities with redacted labels, source references, unresolved questions, and expiry. Relay sends only the capsule plus the owner’s latest utterance; planners fetch full artifacts by reference only when continuation requires them.
- **owner gets:** Follow-up voice conversations would remain fast and coherent even after long Mac/browser work, while the system remembers exactly what “the second one” means. It also makes private browser content less likely to be repeatedly injected into the expensive realtime model.
- effort: Medium: define versioned schema, artifact-reference store, redaction/compression pipeline, planner and relay adapters, integrity checks, and migration for existing receipts. Add tests for stale capsules, changed tabs, duplicate entities, and partial failures.  ·  risk: Over-compression can omit the fact needed for a safe continuation, and a stale capsule can misrepresent the current page. Include source timestamps, confidence, explicit unknowns, and a mandatory refresh when state-sensitive fields changed. Fall back to the full artifact only on a typed insufficiency event.
- cost: Reduces repeated realtime and planner input tokens; adds low-cost storage and capsule-generation work. The dominant expense shifts to occasional artifact fetches rather than every conversational turn.  ·  latency: Usually lowers latency by shrinking prompts; a refresh may add one browser/Mac round trip when the capsule is stale.
- security: Capsules should be encrypted, owner-scoped, redacted by default, and short-lived. References must not be usable without the authenticated task session; audit access to unredacted artifacts.
- depends on: Durable continuation/task ledger with stable task and artifact handles.; Typed downstream receipts and ambiguity events.; An encrypted artifact store shared by relay, Mac bridge, and browser harness.


## What it asked for

_Nothing._
## Its own summary

Recorded four new items: a cross-surface conversational continuation capability; an ambiguity-resolution loop so the owner can answer one focused question remotely; a private haptic notification channel on the pendant; and signed, redacted evidence capsules to preserve task context without replaying expensive/private history. The owner needs a durable task ledger, typed continuation/ambiguity events, encrypted artifact references, pendant notification delivery, and capsule-aware planner/relay adapters before these are possible.

**Biggest unknown:** Whether any existing backlog item already implements part of durable continuation or evidence-capsule storage; I was instructed not to discover further this round, so the proposals intentionally state those as dependencies rather than assuming they exist.

