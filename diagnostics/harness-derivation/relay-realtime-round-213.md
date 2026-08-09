# Harness derivation — relay-realtime — round 213

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to the thing I asked you to do?"
- **useful because:** A quick spoken status check reduces anxiety and prevents duplicate actions. It’s perfect for voice: short, immediate, and reversible.
- **path:** relay-realtime → mac-planner
- **model tier:** Realtime only; it’s a short read.
- **latency:** Fast, ideally under a second; no need to wake other surfaces if job status is already recorded.
- **cost:** Very low. One status read and a short spoken reply.
- **security:** Status should name the job in a user-friendly way and avoid exposing sensitive paths or content unless requested.
- **missing:** A stable way to reference the last job (aliasing "that thing" to jobId) across turns if context is thin

### "Run a quick pendant-to-Mac audio check and tell me if the link is healthy."
- **useful because:** The owner can verify the wearable setup before a demo or work session, catching mic, bridge, or pipeline issues early.
- **path:** pendant → bridge → relay-realtime → mac-planner
- **model tier:** Realtime for guidance; diagnostics can be automated without heavy reasoning.
- **latency:** A few seconds end-to-end; short spoken steps if manual intervention is needed.
- **cost:** Low. A small diagnostic payload and a brief report.
- **security:** Diagnostics should avoid recording real content; use synthetic audio and discard it after the check.
- **missing:** A defined diagnostic verb on the USB bridge and relay pipeline to run loopback tests; Permissioned endpoint to invoke bridge work when attached

### "Move this conversation to my Mac, keep the context and unfinished plan, and let me continue there (or bring the result back to my pendant)."
- **useful because:** The owner should not have to repeat a long spoken request when they reach the Mac. This creates a real handoff between the worn front door and the machine with the browser session, rather than treating each surface as a separate chat.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay handles the handoff command and a short acknowledgement; mac-planner performs the work; a cheaper background summarizer compresses the transcript and pending decisions.
- **latency:** Acknowledge on the pendant in under 1 second; make the Mac session available within 3 seconds; later work may be asynchronous.
- **cost:** About one realtime turn plus one inexpensive summarization call per handoff; the dominant cost is the context compression, not the relay acknowledgement.
- **security:** The handoff must preserve the owner's existing authorization but not broadcast private browser contents to an untrusted surface. Require an explicit target (Mac versus pendant), expire handoff tokens, and redact secrets from the summary. No destructive action should be inferred merely because a conversation moved surfaces.
- **missing:** A durable conversation-handoff object containing transcript summary, unresolved questions, planned actions, and target surface; A Mac-side endpoint/UI to claim a handoff and return progress or a result; A pendant-visible return path for the final result, beyond ordinary job completion alerts

### "Use my already-open browser session to check this, but do not send the page or its sensitive contents through the relay; tell me only the answer and what action, if any, is needed."
- **useful because:** The browser can reach authenticated information while the relay is the always-awake voice front door, but today a browser result is effectively treated as ordinary relay context. A privacy-preserving answer capsule would let the owner use private sessions without making the relay a copy of every page.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** A small local browser-side extractor computes a narrowly typed answer; the realtime relay only verbalizes that answer. Use the expensive model only when the extractor cannot map the page to the requested fields.
- **latency:** Under 5 seconds for a simple page predicate or field extraction; fall back to an asynchronous job for a complex page.
- **cost:** Low for structured extraction; occasional model cost for ambiguous pages. Bandwidth and storage fall substantially because page HTML and screenshots do not leave the Mac.
- **security:** The browser extension must enforce an allowlisted output schema and never return cookies, tokens, full DOM, screenshots, or unrelated nearby fields. Display an audit record locally showing exactly which fields were released. The owner must be able to revoke the capsule.
- **missing:** A browser-local extraction primitive that returns typed fields or predicates rather than page text; A relay contract for schema-constrained, redacted result capsules; Per-session data-retention and revocation controls for browser capsules

### "Do not interrupt me for every update; learn my interruption rules and deliver one short, ranked digest when something truly matters, based on what I am doing on the Mac and what is waiting in my browser."
- **useful because:** The wearable is uniquely able to reach the owner while away, but unsolicited speech is costly and annoying. A policy-driven interrupt arbiter would combine job completions, page watches, and Mac state into one decision instead of making each subsystem compete for the pendant.
- **path:** relay → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic urgency, quiet-hours, deduplication, and active-application rules first; use a cheap background model only to rank genuinely ambiguous items. Realtime is reserved for the final spoken digest.
- **latency:** New alerts should be classified in under 500 ms; a digest should be available on the next button press or within 2 seconds of a high-urgency event.
- **cost:** Near-zero for rule-based events, with occasional low-cost ranking. This avoids paying a realtime turn for every background completion.
- **security:** The arbiter must never infer that a low-priority browser or work item is safe to speak aloud in public. Store policies and sensitivity labels, expose a local audit trail, and make the owner able to mute or clear the queue physically. Do not silently change an action's execution policy.
- **missing:** A single event bus that accepts job, watch, browser, and Mac-context events; A persistent interruption-policy model with quiet hours, sensitivity, deduplication, and escalation rules; A priority-aware delivery scheduler that can target the existing pendant inbox without speaking immediately; A feedback loop recording skip, replay, and interrupt outcomes without treating silence as consent


## Changes it proposed to its own stack

### `relay` — Implement a real relay-side completion notification pipeline. Track jobId -> delivery targets (pendant/phone/dashboard), monitor status transitions using the existing job status read path, and emit alerts into the existing offline alert inbox flow when sessions end.
- **owner gets:** They can fire off a task and get a spoken outcome later without babysitting the system.
- effort: Medium. Requires a persistent mapping table, a watcher loop, and integration with the device inbox format.  ·  risk: Alert spam or duplicate notifications. Mitigate with dedup receipts and per-job state machine.
- cost: Low. Polling is the main cost; bound it by exponential backoff and a hard cap per job.  ·  latency: Adds a small background delay; user-facing latency improves because they don’t wait in-session.
- security: Notification content could leak sensitive details; default to minimal summaries unless the owner opted in.
- depends on: job_completion_watch semantics clarified or replaced with a concrete watcher route; A real relay_event_push implementation or an alternative delivery verb

### `integration` — Add a USB-attached diagnostics path: relay can invoke a bridge work command that generates synthetic audio, routes it through the pipeline, and returns measurable health (levels, packet loss, decode errors).
- **owner gets:** A quick “is it healthy?” check before a demo prevents embarrassing failures.
- effort: Medium to high. Needs a new command verb and a small report schema.  ·  risk: Could interfere with a real conversation if triggered at the wrong time. Require idle state and a clear spoken confirmation.
- cost: Low ongoing; occasional diagnostics only.  ·  latency: A few seconds per run.
- security: Must avoid capturing real speech; synthetic only and discard artifacts.
- depends on: Permission to POST /v1/bridge/work; A defined bridge command set


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: cross-surface conversation handoff, privacy-preserving browser answer capsules, and a policy-driven interruption arbiter. The first two require new connective contracts despite existing sessions/actions; the third requires an event bus, policy store, and priority delivery scheduler. The owner still needs durable handoff state, browser-local redacted extraction, and unified alert arbitration before these are possible.

**Biggest unknown:** Whether the recorder considers the interruption arbiter too close to the existing pendant alert inbox or completion-watch work; its distinct proposal is the owner-controlled policy/ranking layer across all event sources, not another queue.

