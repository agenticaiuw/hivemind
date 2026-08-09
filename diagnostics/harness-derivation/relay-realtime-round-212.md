# Harness derivation — relay-realtime — round 212

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If a task needs my approval or extra info, ask me at the right moment, even after the session ends."
- **useful because:** This turns stalled jobs into a smooth conversation. The owner doesn’t have to remember to check; the system prompts them when it’s actually blocked, and only for what’s needed.
- **path:** mac-planner → relay-realtime → pendant → phone → dashboard
- **model tier:** Background tier monitors and detects needs_attention; realtime handles the follow-up question when the owner responds.
- **latency:** Monitoring can be slow; once blocked, the prompt should arrive within a few seconds to a minute depending on connectivity.
- **cost:** Dominated by periodic job-state checks and a second short conversation turn.
- **security:** Prompts may reveal sensitive context; keep them minimal and avoid reading content unless requested. Confirm before doing anything destructive.
- **missing:** A reliable delivery channel for needs_attention events to pendant/phone/dashboard.; An implemented relay event API (current relay_event_push is schema-only).; A policy for how long to keep blocked prompts and how to avoid duplicate nags.

### "“Make this a one-sentence decision for me: compare the document on my Mac, the relevant authenticated browser page, and my previous notes, tell me what conflicts, and recommend what I should do.”"
- **useful because:** Today each surface can be queried, but nobody fuses local files, live browser state, and durable memory into a grounded conflict report. This would turn the pendant into a decision front door while preserving evidence and avoiding a vague chatbot answer.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to clarify the owner's question; use mac-planner and browser automation for collection, then a background faculty-judgement pass for comparison and recommendation.
- **latency:** Acknowledge in under 1 second; gather in 10–45 seconds; speak a one-sentence recommendation first and queue evidence for follow-up.
- **cost:** Roughly $0.03–$0.15 per invocation, dominated by planner/vision turns and browser extraction; no need to resend full documents to the realtime model.
- **security:** Authenticated browser content and local files leave their surfaces and enter the relay's job context. Keep source locators and hashes rather than duplicating full content where possible; never claim a conflict without quoting both source snippets. No destructive action occurs without a separate request.
- **missing:** A cross-surface evidence bundle/job schema that can reference Mac files, browser pages, and memory facts without flattening everything into the realtime prompt; A faculty-judgement comparison worker with provenance-aware contradiction output; A spoken-result plus dashboard evidence view

### "“Keep working on that investigation while I walk away. If you hit an ambiguity, ask me one short question on the pendant; let me answer and continue without restarting or losing the work.”"
- **useful because:** The current system can queue work and eventually report completion, but a long Mac/browser task either blocks the conversation or forces the owner to restart after an ambiguity. This makes the wearable a real remote control for an ongoing agent rather than a one-shot command button.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the cheaper background planner/computer-use tiers for execution; use realtime only for the short clarification exchange and final spoken update.
- **latency:** Immediate acknowledgement under 1 second; ambiguity question within 5 seconds of detection; resume within 2 seconds of the owner's answer; tolerate multi-minute total execution.
- **cost:** About $0.05–$0.30 per task, mainly planner/computer-use turns; clarification turns are small and should not resend the whole job transcript.
- **security:** The relay must bind every answer to the exact paused job and expire unanswered questions. Do not let a stale spoken answer mutate a later job. Browser pages and local files remain in the job's existing security boundary; dashboard should show the pending question and action history.
- **missing:** A resumable job state machine with explicit pause/question/resume transitions and a compact state checkpoint; A relay-to-pendant question channel and answer correlation that works after the original voice session ends; Planner support for returning a single ambiguity instead of guessing; A user-visible timeline showing what was done before and after the answer

### "“Undo the last thing you did for me—wherever it happened—and tell me exactly what was restored.”"
- **useful because:** Computer and browser actions can span apps, tabs, files, and settings, yet the owner has no single spoken recovery command. A durable inverse-action record would make the system safer to trust and dramatically reduce the cost of a mistaken voice command.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic inverse handlers first; use a background planner only to assemble a multi-step rollback. Realtime should identify the target receipt and speak the result, not reason over raw action history.
- **latency:** Resolve the most recent eligible receipt in under 1 second; execute a simple inverse in under 5 seconds; for compound rollback, report progress and finish within 30 seconds.
- **cost:** Near-zero for typed inverse handlers; $0.01–$0.10 when a planner must reconstruct a rollback. Storage and receipt indexing dominate rather than model tokens.
- **security:** Some operations are inherently irreversible (sending mail, external purchases, destructive deletes). Mark them non-undoable instead of pretending. Store inverse data locally where possible, redact secrets, bind rollback to the original job and owner session, and provide a spoken preview for ambiguous multi-action undo.
- **missing:** Receipt records need explicit inverse operations and before-state snapshots, not just success text; Browser and Mac action adapters that expose atomic undo/restore endpoints; A deterministic selection rule for 'last thing' across concurrent jobs and surfaces; A rollback result that the pendant inbox can deliver after a dropped connection


## Changes it proposed to its own stack

### `hardware` — Add a concealed capacitive skin/contact sensor (or clasp continuity sensor) and a tiny haptic actuator to the pendant, expose worn/unworn and deliberate-private-mode events to firmware, and have the relay propagate a signed presence state to Mac and browser surfaces. When unworn or privacy mode is active, suppress spoken sensitive content, pause alert delivery, and require the pendant to be worn again before resuming.
- **owner gets:** The owner can wear the pendant in a room, hand it to someone, set it on a desk, or fall asleep without private mail, browser results, or computer-control details being spoken aloud. It would also make unattended asynchronous work safe to return to: the relay can wait until the pendant is physically with its owner.
- effort: Medium hardware revision plus firmware driver/calibration, relay presence state, and Mac/browser policy hooks; prototype with a conductive clasp or capacitive breakout before committing to a jewelry enclosure.  ·  risk: False unworn readings could suppress useful alerts; recover with a short haptic prompt and a manual button override. Sensor readings are not identity proof, so never treat presence alone as authorization for destructive actions. Handle sweat, clothing, and metal enclosure effects in calibration.
- cost: Approximately $1–$4 in parts and a few milliwatts while sensing, depending on sensor choice; small firmware and relay cost, no per-turn model cost.  ·  latency: Presence transitions should reach the relay in under 1 second over the attached serial path and under several seconds over LTE; no impact on normal speech latency.
- security: Improves privacy by default but adds a physical-state signal that must be authenticated and freshness-checked. Do not upload raw capacitance data; send only signed state transitions and timestamps.
- depends on: A firmware presence-event driver and haptic event path; A relay presence lease with expiry and reconnect semantics; Mac/browser hooks that can suppress or defer sensitive speech and queued alerts; A clear owner-configurable policy for which content is sensitive


## What it asked for

_Nothing._
## Its own summary

Recorded four non-duplicate proposals: cross-surface conflict-based decision packets; resumable investigations with pendant clarification; a physical worn/privacy state propagated across relay, Mac, and browser; and spoken cross-surface undo backed by inverse receipts. The most owner-visible missing capability is resumable remote work: the pendant can ask one focused question while the Mac/browser continue, then resume without restarting.

**Biggest unknown:** Whether the existing receipt and browser/Mac action schemas already preserve enough before-state data to implement reliable inverse actions; the proposal explicitly treats that as missing until verified.

