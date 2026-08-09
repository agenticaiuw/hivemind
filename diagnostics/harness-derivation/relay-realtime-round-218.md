# Harness derivation — relay-realtime — round 218

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""While I’m away from my Mac, keep a private handoff of what I was doing: when I press the pendant, tell me the one-line change in my Mac work, browser sessions, and delegated jobs since the last handoff, and let me say ‘pick up there’ to continue the most relevant thread.""
- **useful because:** The owner often leaves the Mac while work continues. Today the wearable, Mac, browser, and relay each know fragments, but no one can turn those fragments into a continuity moment. This makes the pendant a genuine remote control for unfinished work rather than a voice-only terminal.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime for the one-line spoken delta and intent disambiguation; a background/cheap model should normalize journals and rank the continuation candidates.
- **latency:** Under 2 seconds for the spoken delta; continuation can acknowledge immediately and complete asynchronously.
- **cost:** About $0.01-$0.04 per handoff, dominated by summarizing changed Mac/browser/job receipts; cache stable journal prefixes to avoid resending context.
- **security:** The handoff may expose browser titles or work content over the voice channel. Store only short redacted deltas, scope browser facts to the active task, and require an explicit owner phrase (‘pick up there’) before issuing mutations.
- **missing:** A cross-surface handoff cursor and change journal that records last-seen sequence per owner; A relay endpoint that joins Mac state, browser findings, and job receipts into one ranked delta; A continuation resolver that maps ‘there/that thread’ to a concrete job or planner goal

### ""When I’m walking and remember something about the project, let me say ‘attach this to what I was doing’ and have the pendant’s memo become a timestamped, searchable annotation on the exact Mac job, browser page, or conversation that was active when I left.""
- **useful because:** A voice memo by itself becomes another inbox. Anchoring it to the actual work item makes it actionable when the owner returns, even if the Mac and browser have moved on. This uses the worn device for capture and the Mac/browser for durable context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only transcribes and confirms the short annotation; a cheaper background model resolves the target against recent job receipts, browser findings, and conversation turns.
- **latency:** Confirm the captured annotation in under 2 seconds; target resolution may take up to 10 seconds and should report ambiguity rather than guess silently.
- **cost:** Roughly $0.01-$0.03 per annotation, mostly transcription plus target ranking; no expensive vision call unless the candidate is genuinely ambiguous.
- **security:** Annotations can contain sensitive speech and may attach to the wrong project. Encrypt at rest, retain the raw audio only under the existing failure-path rule, show the resolved target in the next spoken confirmation, and expire unresolved candidates.
- **missing:** An annotation record linking a memo to immutable job/page/conversation identifiers; A relay-side target resolver over voice history, receipts, and browser findings; A Mac/dashboard view and search route for annotations

### ""Let me ask the pendant ‘is this safe to leave running?’ and get a plain answer based on the real Mac, browser, and delegated-job state—including what is waiting for me, what is actively changing, and what will stop if I close the lid.""
- **useful because:** Today the owner cannot reliably distinguish an active long task from a queued or dead one while away. A single spoken readiness judgment would prevent abandoned work and unnecessary checking, using facts no one node can see alone.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the question and verbalizes a structured state snapshot; deterministic checks produce facts, with a cheap model only for prioritization and wording.
- **latency:** 2-3 seconds for the first answer, with a short ‘still checking’ update if browser or Mac state takes longer.
- **cost:** Under $0.01 for normal checks; cost rises only when an active vision/browser inspection is required.
- **security:** Do not claim safety from stale heartbeats. Include timestamps and explicit unknowns, distinguish ‘not running’ from ‘not observed,’ and avoid reading sensitive page contents unless the owner asks.
- **missing:** A unified liveness/termination contract across relay jobs, Mac agent sessions, and browser commands; A state sampler that records observed-at and expected-next-event for each activity; A spoken status schema with confidence and stale-data handling


## Changes it proposed to its own stack

### `relay` — Add a real, durable outbound notification pipeline on the relay that can target the pendant/phone/dashboard with TTL, retries, and acknowledgement, and wire it to job state changes. Keep messages short and pre-rendered for the pendant speaker.
- **owner gets:** They can start a task and walk away, and still reliably hear the outcome later without polling.
- effort: Medium to high: requires new relay routes/storage and integration with job lifecycle.  ·  risk: Notification loss or duplication. Mitigate with idempotent message IDs, receipts, and dedupe on the device inbox.
- cost: Low per notification; storage for queued messages scales with backlog.  ·  latency: Adds negligible latency to job completion; delivery happens asynchronously.
- security: Must enforce per-owner/device scoping and avoid leaking sensitive content; encrypt at rest if stored.
- depends on: Implementing a resolvable event delivery mechanism (relay_event_push is currently unresolved); Existing device inbox mechanism as the delivery sink

### `model-routing` — Introduce a lightweight intent enum at the relay for common voice requests (status_check, read_public_page, start_mac_task, summarize_result) that maps directly to existing tools, so routing decisions are observable and testable without inventing a protocol.
- **owner gets:** More predictable behavior and fewer misroutes, which means faster, smoother conversations.
- effort: Medium: schema definition plus logging and tests; no new capabilities required to start.  ·  risk: If the enum is too rigid it could block novel requests; mitigate by allowing a fallback path to mac_delegate.
- cost: Minimal; mostly logging and validation.  ·  latency: Minimal; classification happens inline.
- security: Low; improves auditing.
- depends on: A resolvable routing tool or internal dispatcher (current relay_route_intent schema is unresolved)


## What it asked for

_Nothing._
