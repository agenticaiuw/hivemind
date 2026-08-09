# Harness derivation — faculty-perception — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS input and screen observability is live** — The running AI Pendant Agent reports Accessibility trusted=true, Screen Recording granted=true, no required permissions missing, and ready=true; Safari browser extension is online with 2 tabs and pendingCommands=0.
  - evidence: read_continuity_snapshot include relay,pipeline invoked GET /ops/snapshot HTTP 200; body status.permissions and status.browser at 2026-08-08T04:52:56Z

## Capabilities it proposed

### "“Did that actually happen, or are your surfaces disagreeing?” Give me one short answer that separates requested, accepted, executed, delivered, heard, and unknown—and names the exact contradiction when sources disagree."
- **useful because:** This is the single most useful missing perception: today a completed Mac job or relay-delivered announcement can be mistaken for something the owner received. It turns silent false confidence into an explicit, actionable uncertainty report.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Cheap background classifier for event normalization; realtime only when the owner asks. No expensive model is needed for state comparison.
- **latency:** Under 1 second from cached snapshot; under 4 seconds if it must fetch relay and pipeline state.
- **cost:** <$0.01 per query; dominated by one model call only when contradictory free text needs summarization.
- **security:** Do not expose page bodies or secrets in the report; pass IDs, timestamps, hashes, statuses, and redacted snippets only. Require confirmation before treating an ambiguous event as proof of action.
- **missing:** A shared causal correlation ID carried from voice turn through relay job, Mac job, browser command, and audio artifact; A device-originated playback event (the existing device_playback reader has no writer); A perception reducer that compares snapshots instead of trusting completed status

### "“What private material did you send or retain outside this Mac?” Show a provenance-and-retention receipt for each relay/browser operation: source, destination surface, content class, hash/capsule, retention policy, and whether deletion is actually enforced."
- **useful because:** Relay browser reads currently mint no ID or hash, and page text can enter announcements that are filtered by TTL but never deleted; the owner cannot discover this exposure today. This gives a concrete privacy answer rather than a vague trust claim.
- **path:** browser-extension → relay-realtime → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Background deterministic reducer plus a small model only to classify redacted content sensitivity. Use realtime only for an immediate spoken warning.
- **latency:** Receipt generated asynchronously within 2 seconds of an operation; spoken warning within one turn when high-sensitivity content crosses the relay.
- **cost:** <$0.005 per operation for hashing/classification; storage and one browser/relay metadata write dominate, not model tokens.
- **security:** Hash and classify after local redaction; never replicate raw page text merely to make the receipt. Treat URL/query and login-wall indicators as sensitive. Require confirmation before sending sensitive content to relay or storing it in announcements.
- **missing:** Relay read contract returning stable request ID and content hash; Transport from relay to the Mac evidenceCapsules store; the Mac schema already exists; Enforced announcement/audio deletion and a durable outbound data-flow ledger

### "“When did that happen for me?” Normalize every event and scheduled action into the owner's declared timezone, show the machine timezone separately, and mark pendant timestamps as unknown instead of guessing."
- **useful because:** The owner says America/Chicago while this Mac resolves America/New_York, and the pendant has no captured zone. Without this, a morning brief, routine, or device event can be confidently reported an hour off or assigned a fictitious instant.
- **path:** pendant → relay-realtime → mac-planner → unified → faculty-perception
- **model tier:** No model: deterministic timezone conversion and uncertainty propagation; use realtime only to phrase the final answer.
- **latency:** Under 200 ms from stored events; under 2 seconds if joining relay and Mac traces.
- **cost:** Negligible API cost; dominated by a small durable timezone-preference record and event annotations.
- **security:** Timezone is personal location metadata. Keep it local, distinguish owner preference from inferred machine zone, and never infer physical location from timezone.
- **missing:** An explicit owner-timezone preference distinct from the Mac's America/New_York zone; A timestamp contract requiring offset/zone or an explicit zoneless/unknown marker on relay and pendant events; Cross-surface event join keys so converted times refer to the same operation

### "“Before you act, tell me what you can actually see right now.” Return a compact, read-only attestation of the focused Mac window, visible browser tab, permissions, and relay/pendant freshness, with a screenshot/content hash and an explicit stale/unknown flag."
- **useful because:** Now that the exact agent has Accessibility and Screen Recording and the browser bridge is online, the system can finally distinguish current screen reality from cached DOM, old pipeline records, or a relay claim. It gives the owner a trustworthy pre-action checkpoint and makes later disagreement diagnosable.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Deterministic snapshot and hashing first; a small vision model only to describe visible UI when requested. Realtime is unnecessary unless spoken immediately.
- **latency:** 500 ms for status plus browser metadata; under 3 seconds when a screenshot and vision description are requested.
- **cost:** <$0.01 per requested attestation; screenshot upload/vision dominates, and hashes/status-only are effectively free.
- **security:** Screenshots can contain mail, financial pages, and secrets. Keep raw images on the Mac, return hashes and redacted regions by default, and require explicit confirmation before relaying pixels or acting on a sensitive surface.
- **missing:** A single Mac route that atomically captures focused-window metadata, screenshot hash, browser tab identity, and permission state; A cross-surface snapshot schema with monotonic capture time and correlation ID; Owner policy for which apps/domains may be described or uploaded

### "“Put these events in the order they really happened, even if the clocks disagree.” Build a causal timeline across my pendant, Mac, relay, and browser, using sequence numbers and link transitions; mark any ordering that is inferred rather than observed."
- **useful because:** Today timestamps come from different clocks: relay UTC, Mac local time, browser event time, and pendant zoneless monotonic time. A believable but wrong chronology makes incident recovery and “what did you do?” answers unreliable. The owner gets an honest order with uncertainty instead of a falsely precise timestamp list.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Deterministic event-graph reducer; use a cheap model only to phrase conflicts. Realtime is not needed for the computation.
- **latency:** Under 2 seconds for a recent incident; under 10 seconds for a multi-day bounded reconstruction.
- **cost:** Under $0.01 per reconstruction; storage of compact event edges dominates, not inference.
- **security:** The graph must contain metadata and hashes by default, not raw audio, page text, or secrets. Preserve uncertainty rather than fabricating edges. Permit the owner to delete local event details without breaking aggregate counters.
- **missing:** A monotonic sequence/correlation envelope emitted by every surface; A relay-to-Mac clock-offset sample and explicit pendant monotonic epoch/session identity; A causal-graph store and query that preserves observed versus inferred edges

### "“Before you send or store this, show me every surface that will see it and the private fields that will cross each boundary.” Simulate the complete route through pendant, relay, Mac, browser, and durable stores, then block or ask for confirmation when the route exposes sensitive material."
- **useful because:** The owner currently cannot predict that a browser read may enter relay announcements, or distinguish local evidence storage from cloud retention. A preflight data-flow preview prevents accidental disclosure instead of merely reporting it afterward.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic taint/data-flow analysis with local redaction; a small classifier labels sensitivity. Realtime only speaks the confirmation prompt.
- **latency:** Under 500 ms for known route templates; under 3 seconds when content classification is needed.
- **cost:** Under $0.01 per preflight; classification and optional local screenshot OCR dominate.
- **security:** Raw sensitive content must remain local during simulation. Treat URLs, login state, mail, financial data, and audio as sensitive by default. A route marked unknown must fail closed for external transmission, but local reversible actions may proceed.
- **missing:** A route manifest declaring every read, write, retention, and external boundary; A taint label attached to evidence capsules, browser results, audio, and announcements; A judgement/action gate that consumes the simulation and requires explicit confirmation

### "“If the connection dies right now, what exactly will survive and what will be lost?” Give me a pre-action failure rehearsal for the intended task: offline pendant behavior, Mac/browser queues, relay expiry, resumability, and whether retry could duplicate an action."
- **useful because:** The system spans a wearable, browser sessions, a Mac, and a relay, but no owner-facing answer predicts the consequence of a dropped link. This lets the owner choose a safe route before sending a message, changing a file, or starting a long research task—not after partial execution.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-perception → faculty-judgement
- **model tier:** Deterministic policy simulator over live reachability, queue state, retention, and action reversibility; use realtime only to explain the result briefly.
- **latency:** Under 1 second for a rehearsal of a known action plan; under 5 seconds for a multi-surface workflow.
- **cost:** Negligible model cost; the expensive part is maintaining accurate per-step durability and retry contracts.
- **security:** Never execute the rehearsal. Do not reveal queued secrets or command bodies; show classifications and destinations. Any step without an idempotency key or undo path must be labeled duplicate-risk and require confirmation.
- **missing:** A declarative durability/retry contract for every action and artifact; Per-step idempotency keys and explicit duplicate/undo semantics across Mac, browser, relay, and pendant; A failure-injection-free simulator that evaluates plans without touching external systems


## What it asked for

### `c13-szld` (context) — owner timezone authority
- why: The owner memory says America/Chicago, while the Mac's authoritative resolved timezone is America/New_York and the pendant has no zone. Time conversion cannot be truthful without knowing whether Chicago is the owner's intended personal timezone or stale memory.
- would change: I will label event times as conflicting/unknown instead of silently converting them, and will use the confirmed preference for schedule and continuity reports.

