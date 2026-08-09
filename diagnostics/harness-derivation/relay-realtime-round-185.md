# Harness derivation — relay-realtime — round 185

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say a plan out loud, capture it and turn it into a Mac workflow I can approve, then run it."
- **useful because:** This turns the pendant into a hands-free orchestrator: the owner can describe multi-step work while away from the Mac, then approve and execute when ready.
- **path:** pendant → relay → mac-bridge → mac-vision → browser
- **model tier:** Realtime to capture and structure the request; mac-planner (cheaper than realtime for long planning) to build the workflow; browser/vision only if needed for UI steps.
- **latency:** Fast capture and confirmation under 2 seconds; planning can take longer and should happen off the realtime path.
- **cost:** Moderate. Most cost is the planner and any UI automation; relay stays lightweight.
- **security:** A spoken plan may include sensitive data. Keep drafts private, require approval before execution, and log actions for audit.
- **missing:** A durable draft store for pending workflows; A clear approval UX (voice or on Mac) that doesn’t rely on long relay sessions; Better tool-schema coverage for planning categories beyond short action lists

### ""Take this bug from my voice description all the way to a tested patch, and tell me only when it is actually fixed.""
- **useful because:** The owner can report a problem while away from the Mac and receive an outcome rather than a plan. The pendant supplies the terse intent and clarification loop; the Mac terminal edits and tests the project; the browser can inspect authenticated issue/PR context; the relay keeps the conversation truthful when tests fail or the connection drops.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Use realtime only for the initial utterance and terse clarification; use mac-planner plus the cheaper terminal/computer-use tiers for implementation, tests, and iterative repair. Relay synthesizes the final evidence.
- **latency:** Acknowledge in under 2 seconds; implementation may take minutes. Speak only milestone or blocker updates, with a final result after tests and an artifact link.
- **cost:** Roughly $0.05–$0.40 per task depending on number of planner/test loops; terminal execution and browser reads dominate elapsed time, not speech.
- **security:** The task can modify source and create commits/PRs, so the owner must explicitly phrase the request as implementation, not merely diagnosis. Repository contents, issue text, and test output leave the Mac only as summarized relay context; secrets must remain local. Report exact commands, changed files, and test evidence instead of claiming success from a clean exit alone.
- **missing:** A durable multi-step task capsule with artifact references and resumable checkpoints; A Mac-side patch/test executor that can iterate on failures under one job; A browser bridge that can read the owner’s authenticated issue or PR and optionally post the result; A final evidence schema that relay-realtime can turn into a truthful spoken outcome

### ""Tell me what changed across my Mac files, authenticated web tabs, and project activity since the last time I asked, and explain which changes actually matter.""
- **useful because:** Today each surface can be queried, but the owner cannot ask one wearable question that produces a cross-surface, deduplicated delta with provenance. This turns the pendant into a trusted situational-awareness device instead of a launcher for isolated searches.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Use background/cheap models to normalize and diff collected records; use the realtime tier only to ask a missing-scope clarification and speak the ranked result. A judgement pass should classify impact and uncertainty.
- **latency:** A short scope acknowledgement under 2 seconds, collection in 10–30 seconds, and a spoken three-item summary. The owner can interrupt for the next item.
- **cost:** About $0.03–$0.15 per snapshot, dominated by local indexing and authenticated-page extraction; model spend is small if raw records are hashed and only changed excerpts are sent.
- **security:** Local filenames and authenticated page text are sensitive. Keep raw snapshots on the Mac/browser session, send only changed excerpts plus source identifiers, and expose a spoken 'why this was included' for every item. Never infer that absence means deletion when a source was unreachable.
- **missing:** A cross-surface snapshot/diff store keyed by owner-requested checkpoints; Mac and browser adapters that emit stable source IDs, timestamps, and reachability; A faculty-judgement ranking contract with explicit unknown/unreachable states; A compact spoken citation format and retention/deletion controls

### ""I can't see the screen well right now—describe the current Mac or browser screen, tell me what is actionable, and carry out the next thing I say without losing my place.""
- **useful because:** This makes the hive an accessibility surface rather than merely voice remote control. The pendant supplies continuous spoken orientation and interruption; mac-vision interprets visual layout; browser-extension preserves authenticated web context; mac-planner/action executes the owner’s follow-up while the relay maintains the referent ('the blue button', 'the second result').
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** Use gpt-4.1-mini or an equivalent low-cost vision loop for screenshots and element grounding; use the planner only for multi-step actions; realtime handles short descriptions, disambiguation, and interruption.
- **latency:** First orientation in under 3 seconds, action acknowledgement under 1 second, and each requested UI transition under 5 seconds. The owner can interrupt at any point and ask for a shorter description.
- **cost:** About $0.02–$0.20 per screen/action cycle, dominated by screenshot tokens and repeated visual grounding; cache unchanged regions and send diffs where possible.
- **security:** Screens may contain passwords, private messages, or financial data. Keep screenshots on the Mac when possible, redact password fields, expose the active app/domain before describing it, and never speak secrets aloud unless explicitly requested. Actions must be tied to the owner’s current referent and report the exact target.
- **missing:** A live mac-vision computer-use loop (currently disabled); Stable element identities across screenshots and browser DOM inspection; A relay-side referent/session state that survives spoken interruptions; An accessibility-oriented spoken layout contract rather than raw screenshot captions

### ""Let me start a conversation at my desk over USB, walk away, and have it continue over LTE without repeating myself or losing the reply.""
- **useful because:** The live pendant is testable over USB today but is worn and will eventually operate away from the Mac. Seamless migration removes the arbitrary boundary between desk testing and real wearable use: the relay keeps the voice turn, audio sequence, and downstream Mac job coherent while the pendant changes transport.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** Realtime relay remains the turn owner; transport and audio workers are deterministic. Use a cheaper background tier only to reconcile a partial transcript or summarize a job after a handoff.
- **latency:** USB-to-LTE handoff detection under 500 ms, no duplicate spoken sentence, and resume audio within 2 seconds where LTE is available. If handoff fails, preserve the turn and speak one concise retry state.
- **cost:** Low per invocation; mostly protocol/storage engineering. Model cost is limited to a rare transcript reconciliation, under roughly $0.01–$0.05.
- **security:** Bind both transports to the same authenticated pendant session and monotonic turn sequence; reject replayed audio or replies. Do not duplicate microphone chunks during overlap, and erase transient handoff buffers after acknowledgement.
- **missing:** A transport-independent pendant session identity and resumable audio sequence protocol; USB serial bridge support in the relay path alongside LTE WebSocket; A bounded overlap/reconciliation buffer for in-flight Opus frames and transcript state; Mac job continuation keyed to the same turn rather than a transport connection


## Changes it proposed to its own stack

### `context` — Introduce a durable, content-addressed 'task capsule' shared by relay, Mac planner/terminal, and browser harness. Each capsule records the owner’s original utterance, normalized goal, constraints, delegated surface, checkpoint state, artifact hashes/links, command and browser receipts, unresolved questions, and a monotonic revision. On reconnect, any surface can claim the next checkpoint; relay-realtime can answer 'where did we get to?' without replaying the entire transcript.
- **owner gets:** A task that starts on the worn pendant no longer vanishes when the owner walks away, the Mac sleeps, or a browser session expires. They can resume naturally and get a precise explanation of what happened, what remains, and what evidence exists.
- effort: Medium-high: schema and Durable Object/storage layer, adapters in planner/terminal/browser, conflict-safe checkpoint updates, and a spoken projection. Requires a migration for existing jobs rather than replacing them.  ·  risk: Stale or conflicting claims could cause duplicate actions; use leases, revision checks, idempotency keys, and append-only receipts. If storage is unavailable, preserve the current one-shot job behavior and say that resume is unavailable.
- cost: Small storage and request overhead; content-addressing avoids repeatedly sending transcripts and large artifacts. Model cost decreases because each turn receives a compact capsule delta instead of full context.  ·  latency: Adds one fast read/write per delegation, typically tens of milliseconds; avoids much larger context retransmission and reduces recovery latency.
- security: Capsules contain sensitive intent and artifact metadata. Encrypt or isolate per owner, redact secrets from receipts, enforce source-local raw data, and provide expiry/deletion. Cross-surface access must be scoped to the active owner session.
- depends on: A real asynchronous completion/event delivery path (POST /pipeline/events or its replacement); Stable job and receipt identifiers across POST /plan and POST /execute; Mac planner/terminal and browser adapters emitting idempotent receipts; A shared preference/session-memory projection


## What it asked for

_Nothing._
## Its own summary

Recorded four non-duplicate directions: voice-to-tested-patch completion, cross-surface meaningful-change diffs, durable resumable task capsules, accessibility-first visual UI narration/control, and seamless USB-to-LTE conversation migration. The haptic proposal was correctly rejected as already present in the backlog, so I did not rephrase it.

**Biggest unknown:** Whether the existing Mac/browser adapters already expose enough stable element IDs and receipt semantics to implement the accessibility and resumable-capsule designs without new harness work.

