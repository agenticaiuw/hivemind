# Harness derivation — relay-realtime — round 166

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a quick situational summary: what’s running, what’s waiting, and what needs my attention?”"
- **useful because:** A short spoken snapshot prevents context switching. It’s the fastest way to reorient after a pause, especially while walking.
- **path:** relay → mac-bridge
- **model tier:** Cheaper model for summarization; realtime only for conversational refinement.
- **latency:** 1–3 seconds for a concise spoken summary; longer only if the owner asks for details.
- **cost:** Low; dominated by reading job state and receipts and synthesizing a short summary.
- **security:** Summaries can expose private app names or documents. Default to high-level status and let the owner ask for details.
- **missing:** A relay-visible status snapshot route that doesn’t require the Mac to be awake, or a job/status cache in the relay; A standard summary format for jobs, receipts, and pending alerts

### "While you are doing something on my Mac or in my browser, let me interrupt and redirect it: 'skip that', 'use the other tab', 'stop and tell me what you found', or 'continue'. The current job should change course rather than making me wait for completion."
- **useful because:** A wearable conversation cannot be useful for real work if the owner has to let a mistaken multi-step plan run to the end. This makes the pendant a live steering wheel for Mac and authenticated-browser work, not a one-shot remote control.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime handles the short interruption and intent classification; mac-planner replans, while mac-vision/browser-extension carry out the revised steps. Do not spend realtime tokens narrating every step.
- **latency:** Acknowledge the interruption in under 500 ms; pause/cancel the current action within 2 s; speak the revised next step within 4 s.
- **cost:** Usually one short realtime turn plus one planner call, roughly $0.02-$0.10 depending on replanning depth; the dominant cost is the planner context and any fresh page/screen observations.
- **security:** The relay must bind the interruption to the owner's active session and job, not an old job. Stopping is always immediate; redirection can mutate apps or authenticated pages under the owner's existing maximum-access policy. Send only the minimum active-plan and current observation needed to the planner.
- **missing:** A cancellable job/control protocol exposed by the relay and Mac agent; Action-level abort checkpoints in mac-planner/mac-vision/browser-extension; A way for the pendant session to address the currently running job, rather than only submit a new plan; A concise spoken acknowledgement path for pause, cancelled, and replanned states

### "After you change something on my Mac or in a logged-in browser, tell me exactly what changed and why you believe it worked: read back the before/after value or a short page excerpt, not just 'done'. If the evidence conflicts, say 'uncertain' and leave me the job for inspection."
- **useful because:** A spoken 'done' is dangerous when the owner cannot see the screen. Evidence attached to the spoken result lets the owner trust useful remote actions and catch a wrong tab, stale page, or partial failure while away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** mac-vision or browser-extension collects bounded before/after evidence; mac-planner judges whether it supports the intended result; realtime only compresses the verified delta into speech.
- **latency:** No more than 3 seconds after the final action for common app/browser tasks; long evidence collection can become an asynchronous job with a short pendant acknowledgement.
- **cost:** About $0.01-$0.08 per task, dominated by screenshots/page extraction and planner comparison; no extra realtime generation beyond the final sentence.
- **security:** Evidence can contain email, financial, or private page content. Store only a redacted, bounded diff and references to the source tab/app; encrypt it, expire it quickly, and never speak secrets such as full tokens or message bodies. Mutations remain governed by existing owner policy.
- **missing:** A typed before/after observation schema shared by Mac and browser surfaces; Automatic redaction and size limits for screenshots, DOM excerpts, and app state; A planner-level assertion/evidence result distinct from an action receipt; Relay storage and pendant delivery for an evidence-backed result

### "When I dictate a task while away from my Mac, keep it as an actionable job—not just a memo—and automatically continue it the moment I plug the pendant into the Mac over USB. For example: 'When I get back, put the three things I just said into a VS Code issue and open the relevant browser tab'; then tell me what was completed and what could not be done."
- **useful because:** The pendant is genuinely wearable and the Mac is often absent, while USB attachment is a real, testable return signal today. This turns an otherwise disconnected voice interaction into continuity across leaving and returning, without pretending LTE registration or a permanently online Mac.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime extracts a compact structured job and confirms only ambiguities; relay persists it cheaply; mac-planner/mac-terminal/browser-extension execute when the USB companion announces presence. Realtime is used again only for the completion summary.
- **latency:** Store the job and acknowledge in under 1 s. Detect USB attachment and begin within 5 s; common jobs should produce a first result within 30 s.
- **cost:** Roughly $0.01-$0.06 per deferred job, mostly one planner call; USB presence detection and persistence are negligible. Failed jobs should not repeatedly consume model calls.
- **security:** The handoff must be scoped to this pendant's authenticated session and an explicit owner-created job, with idempotency so reconnects cannot duplicate mutations. Keep dictated content encrypted at rest; show the Mac-side action receipt and speak only a bounded summary.
- **missing:** A USB companion protocol for /dev/cu.usbmodem00096003658* and the ESP32 bridge, including authenticated announce, sequence, acknowledgement, and reconnect deduplication; A durable relay job record that can wait for a device-presence event (not a wall-clock scheduler); Mac agent intake that claims one pending job and reports progress/results; A typed distinction between a memo and an executable deferred job at voice capture time


## Changes it proposed to its own stack

### `relay` — Publish a relay capability manifest endpoint (e.g., GET /capabilities) that lists tool schemas, routes, and event delivery endpoints available on the relay surface, including stability levels.
- **owner gets:** This makes the system more reliable: the voice agent can stop guessing what exists, which reduces broken behaviors and weird failures mid-conversation.
- effort: Medium. Define manifest schema, wire to router, include versioning and feature flags.  ·  risk: Low. Risk is exposing internal details; mitigate by redacting secrets, only listing callable surfaces, and gating behind auth.
- cost: Small runtime cost; one endpoint and occasional refresh.  ·  latency: Improves responsiveness by avoiding failed calls and retries.
- security: Requires careful filtering to avoid leaking sensitive internal routes.
- depends on: None, but benefits from a durable job runner for event delivery

### `model-routing` — Introduce an intent ENUM and typed routing contract for relay routing tools so resolution is value-by-value against real action types (e.g., launch_app, open_url, browser_navigate) instead of free-form strings.
- **owner gets:** Fewer misroutes means fewer frustrating “I thought you meant…” moments. The owner gets predictable results when they ask for common actions.
- effort: Medium. Requires aligning the enum with the Mac action vocabulary and updating validators.  ·  risk: Moderate. A mismatched enum could block valid actions; mitigate by including an escape hatch that falls back to mac_delegate.
- cost: Minimal runtime cost; primarily development and testing.  ·  latency: Slight improvement by reducing ambiguity and re-planning.
- security: Typed intents improve observability without adding gates.
- depends on: Manifest of action types from the Mac agent or shared schema

### `integration` — Add a relay-side job status cache and summary builder that can answer “what’s running/waiting/needs attention” even when the Mac is asleep, using receipts and last-known state.
- **owner gets:** The owner can get a quick spoken reorientation without waking the Mac, which is perfect while away from the desk.
- effort: Medium. Needs storage, cache invalidation, and a small summarizer.  ·  risk: Moderate. Stale summaries could mislead; mitigate with timestamps and clear “as of” wording.
- cost: Low ongoing cost; storage proportional to recent jobs and receipts.  ·  latency: Improves by avoiding Mac round trips.
- security: Must ensure job metadata is scoped to the owner and does not leak content unnecessarily.
- depends on: Access to job receipts/events stream (GET /jobs/:jobId/receipts or equivalent)


## What it asked for

_Nothing._
