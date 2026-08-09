# Harness derivation — unified — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I rely on the pendant, tell me whether a conversation is safe and usable right now.”"
- **useful because:** The owner gets one honest go/no-go answer instead of interpreting separate health, privacy, relay, and audio counters. It should fail closed when privacy is latched, the relay is unhealthy, or the last measured link/codec run violates the shipped thresholds.
- **path:** pendant → relay → mac-planner
- **model tier:** deterministic checks first; background gpt-5.6-luna only to explain an already-computed verdict
- **latency:** under 3 seconds for the snapshot; no model call on the healthy path
- **cost:** near-zero API cost; dominated by a few authenticated health and receipt reads
- **security:** Return only redacted health and audio metrics. Never start capture or transmit owner audio. Require a local privacy-convergence check and report its state rather than guessing.
- **missing:** typed conversation-readiness endpoint that joins privacy_convergence_check, incident diagnostics, latest audio validation, and relay/mac health; a stable freshness window for the measurements; owner-facing verdict vocabulary (READY, LIMITED, DO_NOT_SPEAK)

### "“Stress-test the audio link now, without sending my voice, and tell me whether 24 kHz will survive this connection.”"
- **useful because:** The owner can distinguish a healthy codec from a bad live link before an important conversation. A synthetic, bidirectional test can exercise the exact loss/jitter envelope and return measured packet continuity, clipping, resampler, and bridge-buffer results plus a safe profile recommendation.
- **path:** relay → pendant → mac-planner
- **model tier:** deterministic audio validator and fault injector; background gpt-5.6-luna summarizes results only when requested
- **latency:** 15–45 seconds for a short synthetic run; never run on the realtime voice path
- **cost:** low API cost; dominated by test duration and artifact storage if the owner asks to retain them
- **security:** Use generated fixtures only—no microphone capture, speech, or owner audio leaves the device. Make injection explicit and never silently alter the production profile. Redact raw artifacts by default.
- **missing:** a safe orchestration route that binds one fault-injection run to one pipeline validation run; a generated-fixture pipeline ID accepted by audio_pipeline_validate; a policy for whether tests may interrupt an active conversation

### "“Prove this task can survive my Mac going to sleep, then leave it in a safe checkpoint.”"
- **useful because:** Before a long or consequential task, the owner gets a dry-run crash rehearsal: durable context, handoff package, replay classification, and the exact point another node would resume. This exposes jobs that only look durable because state is in model context, without performing the task twice.
- **path:** mac-planner → relay → browser
- **model tier:** deterministic workbench/ledger inspection and fault simulation; background gpt-5.6-luna explains the checkpoint report
- **latency:** under 10 seconds for a dry run; never interrupt an active task unless the owner explicitly asks for a live sleep simulation
- **cost:** low; local filesystem and relay receipt reads dominate, with optional one background explanation
- **security:** Dry-run must not click, send, write, or close anything. Bind the rehearsal to one job/intent, redact browser content and withheld parameters, and require confirmation before deliberately suspending a live job.
- **missing:** a read-only checkpoint/rehearsal endpoint joining workbench context, action ledger, relay job, and browser lease; a deterministic crash-point simulator that does not mutate production state; a signed handoff receipt stating completed, durable, replayable, and blocked steps

### "“Audit my next week of routines and tell me exactly when and where each one will fire—without changing anything.”"
- **useful because:** The owner travels, while routines intentionally fire in the Mac's America/New_York zone. This read-only audit makes that surprising policy visible, flags ambiguous ‘morning/evening’ language and stale leases, and prevents a routine from silently shifting to the pendant's unknown timezone.
- **path:** mac-planner → relay → pendant
- **model tier:** deterministic timezone/lease expansion; background gpt-5.6-luna only turns conflicts into plain language
- **latency:** under 3 seconds for a seven-day audit
- **cost:** negligible; schedule expansion and routine reads
- **security:** Read-only by default. Show the resolved zone and source for every firing time; never infer a pendant timezone from zoneless device digits. Mutations require a separate explicit request.
- **missing:** typed routine-audit endpoint with a seven-day expansion and resolved-zone field; lease/conflict diagnostics joining Mac scheduler and relay routine claims; owner-visible distinction between Mac execution zone and current physical location

### "“Give me the live, evidence-backed answer—not your memory—and tell me if the Mac, browser, and relay disagree.”"
- **useful because:** The owner gets a deliberate reality check for claims such as whether a purchase went through, whether a document changed, or whether a job completed. The system distinguishes observed evidence from inference, reports freshness and source disagreement, and refuses to collapse conflicting surfaces into a confident sentence.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** deterministic multi-surface evidence collection and freshness checks; gpt-5.6-luna synthesizes only the collected evidence and must preserve uncertainty
- **latency:** 5–15 seconds depending on browser and Mac reads; no background polling unless explicitly requested
- **cost:** low-to-moderate per invocation; dominated by browser/Mac round trips, with a small synthesis call only when sources disagree
- **security:** Query only explicitly bound tabs, apps, files, or jobs; redact page content and credentials; never treat model memory as evidence. Any action triggered by the result remains a separate confirmed request.
- **missing:** a typed evidence-quorum request with explicit source bindings and freshness limits; a common observation envelope carrying source, timestamp, object identity, and confidence; conflict-preserving synthesis rules and an owner-facing stale/unknown state

### "“Use this logged-in page to finish the task, but prove afterward that its contents were not retained outside the approved result.”"
- **useful because:** The owner can delegate browser work without making page contents, credentials, or sensitive fields permanent system memory. The browser supplies only the minimum result, the relay/Mac keep a signed retention receipt, and any attempted spill into logs, context, or evidence is surfaced as a failure rather than silently accepted.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** deterministic data-boundary enforcement and receipt checks; planner model may perform the task but cannot redefine the retention contract
- **latency:** normal task latency plus under 2 seconds for post-task verification
- **cost:** low-to-moderate; dominated by browser task execution and redacted receipt storage
- **security:** Credentials and page contents must remain in the bound browser session. Results need explicit field allowlisting, log redaction, encrypted short-lived buffers, and physical approval for exporting anything beyond the allowlist. A failed deletion must be reported as failed, never as success.
- **missing:** per-job data-boundary contract with allowed fields, retention TTL, and destinations; browser-side redaction/export primitive and Mac/relay log scrubber; cryptographically linked retention/deletion receipt visible to the owner; enforcement that model context and action evidence cannot retain disallowed values

### "“When the browser reaches an ambiguity, ask me one concise question on the pendant, show the exact choices, and continue only with my selected choice.”"
- **useful because:** Long browser tasks currently either guess, stall, or require the owner to return to the Mac. This creates a safe conversational interrupt: the browser session is held at a recorded checkpoint, the pendant speaks a bounded choice set, and the selected option is bound to the exact page state before continuation.
- **path:** browser → relay → pendant → mac-planner
- **model tier:** browser agent detects ambiguity and emits a structured question; realtime voice handles the owner's short selection; deterministic planner validates page identity and resumes
- **latency:** question delivery under 2 seconds; resume under 5 seconds after the answer
- **cost:** low per interruption; one short realtime exchange plus browser round trips
- **security:** Never turn a free-form answer into an irreversible action without confirmation. Bind question nonce to tab/session, URL pattern, DOM state hash, expiry, and allowed choices; cancel on page drift or timeout. Do not speak or retain page secrets.
- **missing:** structured browser ambiguity event with an opaque nonce and finite choices; durable suspended-command lease and page-state binding; pendant delivery/answer route and resume validator; owner policy distinguishing clarification from approval


## What it asked for

_Nothing._
