# Harness derivation — faculty-judgement — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you speak anything private, notice if someone else is talking nearby and keep the detail on-screen or queue it instead; tell me later what was withheld.”"
- **useful because:** The pendant is worn in public, but today pendantSpeech/audioBrief can speak arbitrary text and only one briefing path redacts. A configurable, fail-closed content-and-presence boundary prevents an embarrassing disclosure without pretending that timing-based focus is privacy. It uses the pendant microphone/USB audio path, Mac/browser context, relay arbitration, and an auditable explanation.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap local acoustic classifier for voice activity/bystander likelihood; deterministic policy evaluation for the first gate; expensive model only when the classifier is uncertain and the text is genuinely sensitive.
- **latency:** Under 100 ms for local acoustic state; under 300 ms for policy decision. Never wait on a cloud model before muting/queueing private speech.
- **cost:** About $0.001–$0.01 per uncertain utterance if a model call is needed; local VAD/classifier dominates engineering, not API spend.
- **security:** Raw microphone audio must stay on-device and be discarded immediately; transmit only a signed coarse state (owner-speaking/other-voice/unknown). Default unknown to no private speech. The owner must configure which classes may be spoken; dashboard gets the full reason, spoken relay gets only 'I held that back.' Require confirmation before any sensitive content is routed to a third-party TTS provider.
- **missing:** Firmware/bridge acoustic VAD and coarse bystander classifier with no retained PCM; A content gate in pendantSpeech.js and audioBrief.js, not just briefingTriage.redactForDelivery; Owner-editable destination policy mapping data class to speak/screen/queue; A dashboard review surface for held items and evidence

### "“Once a week, ask me to confirm or forget one old fact you still use, and show me exactly where it came from and what will stop working if I revoke it.”"
- **useful because:** The system currently carries preferences and derived facts indefinitely or across stores with no reliable revocation cascade. A tiny, paced memory-maintenance ritual gives the owner control over stale assumptions without making them audit hundreds of records, and makes memory feel trustworthy rather than uncanny.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Background/weekly cheap model ranks candidates by age, use count, disagreement, and sensitivity; deterministic code renders impact. Realtime is used only to answer the owner's short confirmation.
- **latency:** Candidate generation can run in under 2 minutes in the background; spoken prompt under 2 seconds. Never block an ordinary request on the ritual.
- **cost:** Roughly $0.01–$0.05 per weekly run; local storage scans and provenance joins dominate.
- **security:** Never speak the value of a secret; show redacted labels and require dashboard confirmation for sensitive facts. Revocation must emit tombstones to facts, context graph, browser provenance, and fleet memory, with a receipt listing stores that succeeded or failed. Until the cascade is complete, the fact must be excluded from prompts and external actions.
- **missing:** A durable cross-store fact-to-source link (at minimum capsuleId/source refs on memory facts); A scheduler and owner-facing queue for review candidates; A real global revocation cascade and failure receipt; A dashboard control that distinguishes forget, correct, and keep

### "“At the end of the day, tell me what the system changed, what it tried and failed to change, and what is still pending—grouped by outcome, not by which agent did it.”"
- **useful because:** Today relay jobs, Mac jobs, browser commands, action receipts, pipeline events, and routine runs have unrelated IDs and no owner-facing net-effect view. The owner should not need to know which body acted; they need one truthful ledger of completed, failed, cancelled, pending, and unapplied work, with undo links where available.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic joins and outcome classification first; a cheap background model writes the one-sentence digest. Realtime only answers follow-up questions.
- **latency:** Incremental collection under 3 seconds; digest under 10 seconds after the local bridge is reachable. If a surface is offline, explicitly mark its portion unknown rather than waiting indefinitely.
- **cost:** Usually under $0.01 per digest; storage/indexing and cross-surface correlation dominate.
- **security:** Do not include secret values or page bodies in the digest. Every line must carry job/action IDs and provenance, and 'not observed' must not become 'did not happen.' Mutation remains behind existing policy and physical approval; this is read-only.
- **missing:** A durable relay-job↔Mac-job↔browser-command correlation record rather than telemetry-only localJobId; Relay job leases/requeue so pending is distinguishable from orphaned; A normalized outcome schema consuming signed pendant delivery ACKs and pipeline events; An owner-facing dashboard and short spoken renderer

### "“If I take this meeting, accept this deadline, or let you do this task, show me the likely knock-on effects across my day before I commit.”"
- **useful because:** The current system can plan or execute, but it cannot answer the human question ‘what will this choice crowd out?’ A consequence simulator would combine calendar transitions, reminders, active project state, browser work, and pending jobs into a reversible forecast—not a second task planner and not an execution approval.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Cheap deterministic constraint propagation first; a background reasoning model explains only the top two conflicts and labels each inference. Realtime is reserved for the owner's follow-up question.
- **latency:** A preview in 3–8 seconds for local state; up to 15 seconds if authenticated browser context is needed. No mutation occurs during simulation.
- **cost:** About $0.02–$0.10 per nontrivial forecast; browser reads and model context dominate.
- **security:** The simulator must distinguish observed facts from guesses and never silently treat an unauthorised calendar as empty. External-site content stays on the Mac unless explicitly needed. Forecasts expire quickly and cannot be reused as approval for a later action.
- **missing:** A typed forecast graph with time intervals, capacity assumptions, and confidence; Reliable read adapters for calendar/reminders with an explicit unreadable state; A snapshot/version token spanning Mac, browser, and relay state; A dashboard visualization of displaced work and uncertainty

### "“Keep a private scorecard of when your forecasts were right or wrong, tell me when you are becoming overconfident, and let me correct the rule rather than repeating the mistake.”"
- **useful because:** The system currently emits urgency, deadline, permission, and source-confidence judgments, but has no outcome loop. The owner cannot tell whether a confident warning was useful, whether a missed deadline was predictable, or whether a stale heuristic should be retired. Calibration turns trust into a measured property.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic event/outcome matching and calibration statistics; a cheap background model clusters repeated error causes. Realtime only speaks a concise correction prompt when the owner asks.
- **latency:** Record each forecast in under 50 ms; nightly scoring under 30 seconds; no added latency to ordinary actions.
- **cost:** Usually below $0.01/day; local event matching and retention are the main costs.
- **security:** Store labels and scores, not private source text. Never infer that silence means success; outcomes need explicit evidence or remain unresolved. Owner corrections must be durable, reversible, and provenance-linked. Do not tune policy automatically for high-impact actions without review.
- **missing:** A forecast record with prediction, confidence, expiry, and expected observable outcome; Outcome adapters for calendar, reminders, browser watches, job receipts, and pendant delivery ACKs; A calibration dashboard with unresolved, correct, incorrect, and unscorable states; A policy-change proposal flow requiring owner confirmation


## Changes it proposed to its own stack

### `integration` — Build a cross-surface environment provenance feed: the Mac agent periodically snapshots installed-app versions, key workspace configuration hashes, browser-extension version/session identity, relay configuration version, and pendant firmware/audio build identifiers. The relay stores signed change records; the dashboard renders a human-readable ‘what changed since yesterday?’ explanation and the pendant can announce only a short warning when a change affects audio, privacy, or action reach. No file contents or credentials are collected.
- **owner gets:** When behavior changes unexpectedly, the owner can know whether the cause was a firmware flash, audio build, browser extension update, Mac permission drift, or relay deployment instead of debugging blindly. It is a practical explanation of system behavior, not infrastructure visible only to engineers.
- effort: Medium-high: typed snapshot schema, signed manifests on four surfaces, diff classification, retention, and dashboard rendering. Requires careful allowlisting of metadata paths.  ·  risk: Hashes can still reveal project names or update timing; redact paths and allow the owner to disable categories. A false attribution could mislead debugging, so every claim must link to the exact signed snapshot pair. If a surface is offline, show unknown rather than no change.
- cost: Negligible API cost; perhaps tens of KB per snapshot and modest local/relay storage. No new hardware.  ·  latency: No foreground impact if snapshots run on boot, reconnect, and a low-frequency background schedule. A reconnect diff should be available within seconds.
- security: Improves security incident visibility but creates a metadata history. Sign records, encrypt relay storage where available, omit content and secrets, and expose deletion/retention controls.
- depends on: A signed cross-surface identity/version manifest; A durable relay event table and retention policy; An owner-facing change-diff view; The existing pipeline/job receipt and provenance IDs being extended to firmware and deployment events


## What it asked for

_Nothing._
