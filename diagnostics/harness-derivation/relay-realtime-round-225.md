# Harness derivation — relay-realtime — round 225

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Read me the newest thing I need to know from my browser session."
- **useful because:** Combines the browser’s authenticated context with voice, so the owner can stay hands-free and still get updates from where they were working.
- **path:** relay → browser → mac-bridge
- **model tier:** Realtime for the request; browser actions run on the Mac and return a summary.
- **latency:** A few seconds; depends on page load and extraction.
- **cost:** Moderate; dominated by browser automation and page parsing.
- **security:** Authenticated pages may contain sensitive data. Require confirmation before reading or sending anything beyond a short summary, and avoid storing page content.
- **missing:** 

### "When I say “take care of this,” have the system carry out the task across my Mac and browser, show me the exact evidence it used, and stop at the first ambiguity with one spoken question instead of guessing."
- **useful because:** This would turn the pendant from a command launcher into a trustworthy remote operator: the owner can delegate a messy task while away, yet recover from ambiguity without starting over or discovering a wrong result later.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only for intent capture and the one clarification question; use mac-planner for decomposition, mac-vision/browser harness for execution, and a cheaper background verifier for evidence and final summarization.
- **latency:** Acknowledge in under 1 second, ask clarification within 5 seconds of reaching ambiguity, and deliver completion within the task's normal execution time.
- **cost:** Roughly $0.02–$0.10 per delegated task; planner and verifier calls dominate, while relay speech should remain one short turn.
- **security:** Screenshots, page text, and local files may leave the Mac to the relay/model. Store only redacted evidence and a receipt; the owner has authorized broad access, but the system must never claim success without a concrete receipt.
- **missing:** A planner/vision/browser execution contract that emits typed ambiguity events rather than silently failing; Evidence capture and redaction attached to POST /execute job receipts; A relay loop that can suspend a job, ask one question, and resume it with the answer

### "When I say “I still need to decide this,” remember the decision, the alternatives, and what would make it relevant; when I later reopen the related app, page, or person, tell me the unresolved choice and let me resolve it by voice."
- **useful because:** The owner loses decisions between a hallway thought and the moment the work returns. This would preserve intent rather than merely storing a transcript, and surface it at the exact Mac or browser context where it matters.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Relay-realtime extracts the decision in one short turn; a cheaper background model normalizes alternatives and relevance; Mac/browser agents emit context-open events and relay-realtime speaks only when the match is strong.
- **latency:** Capture under 2 seconds; context matching under 500 ms after an app/page-open event; no unsolicited speech for weak matches.
- **cost:** About $0.005–$0.03 per capture and under $0.01 per context match; storage and event matching dominate only at scale.
- **security:** Decision text can contain sensitive people, projects, or pages. Keep scope and expiry on each record, avoid sending unrelated browser content to the model, and expose a spoken “forget that decision” command.
- **missing:** A first-class decision record with alternatives, trigger entities, confidence, and expiry; Mac/browser context-open events carrying app, URL, document, and entity identifiers; A relevance matcher and a quiet wearable notification policy distinct from generic completion alerts

### "When I say “bring back what I was working on,” find the most likely unfinished document, browser tab, or app state from my recent Mac activity, tell me why you chose it, and reopen it exactly where I left off."
- **useful because:** The owner often remembers an intention but not its filename, app, or tab. A wearable should recover the work context from a vague sentence while they are away from the keyboard, rather than forcing them to search manually.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap retrieval/ranking model over local activity metadata and browser tab titles; use relay-realtime only to disambiguate the top two candidates; use mac-planner/vision for reopening and verifying the restored state.
- **latency:** Speak the top candidate within 3 seconds and reopen within 8 seconds once the owner says “yes”; silently return “not enough evidence” rather than inventing a match.
- **cost:** About $0.01–$0.04 per recovery; local metadata extraction is cheap, with model cost concentrated in ranking ambiguous candidates.
- **security:** Activity history can reveal private documents and accounts. Keep raw paths and page content on the Mac, send only hashed IDs/titles and minimal snippets for ranking, and provide a one-command history purge.
- **missing:** A local activity index spanning recent documents, focused-app transitions, and browser tabs with timestamps; A resumable app/browser snapshot contract (cursor, scroll position, draft state) rather than just open_url; A confidence-ranked recovery response and verification receipt


## Changes it proposed to its own stack

### `relay` — Add a real, durable completion notification pipeline: when a job is created, the relay can register a watch, persist it, and emit a short spoken result to the pendant/phone/dashboard when the job reaches a terminal state. This replaces the current unresolved relay_event_push schema with a concrete implementation and routes it through the existing inbox/alert surface on the device.
- **owner gets:** They can start a task, leave, and still get a reliable, hands-free outcome — the system feels like an assistant, not a thing to babysit.
- effort: Medium to high: needs persistence for watches, a watcher loop keyed off job state changes, and delivery integration.  ·  risk: False or duplicate notifications. Mitigate with idempotent watch records, terminal-state checks, and receipts. If delivery fails, keep the alert queued on-device using the existing inbox behavior.
- cost: Low operational cost per job; dominated by job state polling or event hooks and occasional alert delivery.  ·  latency: Fast acknowledgement; completion latency depends on job duration and watch cadence.
- security: Risk of leaking sensitive task outcomes. Keep spoken summaries minimal, redact content, and respect per-device delivery targets.
- depends on: A resolvable delivery mechanism for pendant/phone/dashboard alerts (relay_event_push replacement).; Access to job state changes via GET /jobs/:jobId or an event source.

### `hardware` — Add a low-profile rotary encoder with press plus a small haptic actuator to the pendant, and define a local interaction protocol: rotate to choose among relay-provided alternatives or queued alerts, press to answer, and long-press to cancel; relay messages carry numbered choices and the firmware acknowledges the selected choice offline-safe.
- **owner gets:** The owner could resolve a Mac/browser ambiguity, skip a queued alert, or cancel a runaway task without taking out a phone or looking at the pendant. The current single button can start/stop speech but cannot express a choice while the owner is away.
- effort: Moderate hardware revision and enclosure/firmware work: encoder debounce, haptic driver, interaction state machine, and relay choice messages; test accidental rotations and wet/gloved use.  ·  risk: A false press or rotation could select the wrong option. Default to no selection until a deliberate encoder press, announce the selected label before committing when the choice is consequential, and retain the existing button as cancel. Recovery is a receipt plus replayable choice event.
- cost: Approximately $2–$6 in components and PCB/enclosure changes, with a few mA only during interaction; negligible API cost beyond a short choice event and optional spoken label.  ·  latency: Local selection feedback under 100 ms; relay round trip remains unchanged, and the pendant can answer queued binary choices even during a brief link outage.
- security: A physical selection becomes an authenticated owner action, but should be scoped to the displayed job/session and expire; never let a stale queued choice apply to a different job.
- depends on: A relay-side ambiguity/choice event schema; Firmware integration with the existing offline inbox/outbox and spoken-status interrupt; Mac/browser jobs exposing stable choice IDs and idempotent resume endpoints


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing proposals: evidence-backed delegated execution with spoken ambiguity recovery; context-triggered unresolved-decision memory; and vague “bring back what I was working on” recovery. Also recorded a hardware change adding an encoder plus haptics for glance-free choice/cancel control. The common missing work is not another route: it is cross-surface event contracts, local activity/context indexing, resumable job/choice state, and relay orchestration that connects existing plan/execute, memory, browser, receipts, and wearable inbox pieces.

**Biggest unknown:** Whether the Mac already exposes a complete local activity index and context-open event stream. No further discovery was possible this round, so that is the key implementation question before estimating the recovery and decision features accurately.

