# Harness derivation — mac-terminal — round 268

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant sound wideband, and keep the conversation intelligible while I walk away from the Mac.”"
- **useful because:** The owner explicitly wants the 24 kHz superwideband path end to end. Today the physical chips are attached over USB but the pendant is not LTE-registered, so this should be testable now and later survive a Mac-to-LTE handoff. It makes the wearable feel like one continuous conversation instead of two unrelated transports.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for turn-taking and transport negotiation; background diagnostics use a cheaper model or no model.
- **latency:** First audio under 250 ms on USB and under 700 ms on LTE-M; codec/route switch must be click-free within 1 second.
- **cost:** Negligible model cost for negotiation; roughly 1–2 KB/s telemetry and ordinary realtime audio bandwidth. Engineering cost is chiefly codec plumbing and bench testing.
- **security:** Audio remains in the existing authenticated relay path. The bridge must never silently downgrade to recording or claim a route is live; expose route, codec, sample rate, packet loss, and last acknowledged sequence in the dashboard and pendant truth beacon.
- **missing:** A real host-side USB serial reader/framing implementation (the granted schema is unresolved in the live inventory); A negotiated 24 kHz codec/profile shared by nRF9160, ESP32 bridge, and relay audio endpoints; A route-handoff protocol that keeps turn ID and replay cursor while switching USB↔LTE; Bench acceptance tests using both physically attached chips, including loss, unplug, and reconnect

### "“Tell me only what failed overnight, what it affected, and let me retry the safe ones from the pendant.”"
- **useful because:** Scheduled research, briefs, browser work, and Mac jobs can complete or fail while the owner is away. Today failures are scattered across job records and routine status, so the owner either misses them or has to remember which job to inspect. A concise spoken digest with exact scope and a one-button retry turns unattended automation into something trustworthy.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** Background/cheap model clusters and summarizes completed job receipts; realtime model is used only when the owner asks a follow-up or dictates a retry.
- **latency:** Generate the digest within 30 seconds of the owner's morning request, or proactively after the daily routines settle. Retry acknowledgement under 1 second; report completion asynchronously.
- **cost:** Low: one small summarization call over bounded failure metadata, not raw page/audio content. Most requests are zero-model aggregation. Storage is a few KB per day.
- **security:** Never include secrets, page bodies, or shell environment in the spoken digest. Browser failures should expose host/title and a safe reason, not session data. Retry must preserve the original job's action list and idempotency key; destructive or ambiguous mutations remain excluded and are reported as requiring Mac/browser confirmation.
- **missing:** A cross-surface failure event schema carrying job, routine, browser command, and action receipt IDs; A durable exactly-once retry endpoint that can resume safe failed steps without replaying completed side effects; Relay aggregation that can read Mac-agent job/journal data and routine outcomes while preserving source provenance; Pendant UX for selecting or declining one named retry with truthful completion feedback

### "“Keep working on this until it is actually finished; only wake me if you hit a decision I must make.”"
- **useful because:** The owner can delegate a one-off multi-step objective, but today the system treats planning, browser interaction, Mac execution, and waiting as separate jobs. A durable supervision contract would let the owner walk away: the relay keeps the objective alive, the browser preserves its authenticated session, the Mac performs work, and the pendant interrupts only for a genuinely blocking decision. This is not a scheduled routine or a status brief; it is a bounded, resumable task with an explicit stopping condition.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model for polling, progress classification, and retry decisions; use realtime only when the pendant asks the owner a blocking question. Escalate to the planner only when the task state changes or the next action is ambiguous.
- **latency:** A progress check every 15–60 seconds depending on the task; speak an interruption within 3 seconds of detecting a blocking decision; resume within 10 seconds after the owner answers.
- **cost:** Low-to-moderate background usage: mostly deterministic state checks and receipt comparisons, with one small model call per meaningful state transition. Browser and Mac execution costs dominate, not conversation tokens.
- **security:** The contract must declare allowed surfaces, maximum duration, and forbidden side effects before it starts. Authenticated browser sessions and local files never leave their owning surface. The pendant should receive only a concise decision capsule, not page contents or shell output. Expiry, laptop sleep, browser logout, and relay loss must end in an honest paused state rather than fabricated completion.
- **missing:** A durable objective record with goal, stopping condition, allowed action classes, deadline, current step, and owner-decision checkpoints; A cross-surface state machine that correlates browser command IDs, Mac job IDs, receipts, and relay events and survives process restart; A wait/resume protocol for browser and Mac work, including an explicit blocked-on-owner state and idempotent continuation token; A single dashboard and pendant representation of progress, pause reason, expiry, and final evidence; A policy-independent confirmation handoff: the owner’s spoken answer must be attached to the exact pending decision, not interpreted as a new unrelated command

### "“Before I rely on it tomorrow, test my automations end to end and repair anything that is broken without touching my real data.”"
- **useful because:** The owner has multiple routines and several physical/software nodes, but today a routine can remain nominally enabled while its browser session, Mac bridge, relay route, or audio path is unhealthy. A synthetic end-to-end rehearsal would exercise the real handoffs with disposable data, detect stale credentials, dead routes, and incompatible payloads, and produce a spoken pass/fail report before the owner depends on the system.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** Deterministic probes and disposable canary jobs first; a background model classifies failures and proposes the smallest repair. Realtime is unnecessary unless the owner asks a follow-up.
- **latency:** A nightly or owner-triggered rehearsal completes within 5 minutes; individual probes have hard deadlines and fail fast. The pendant receives one concise result and can read the failing component on demand.
- **cost:** Low recurring cost if canaries use local fixtures and test accounts; occasional background classification on failure. Engineering cost is in fixtures, isolation, and end-to-end contracts.
- **security:** Canaries must never send mail, buy, delete, alter production files, or submit authenticated forms. Browser tests use a dedicated test origin/session or dry-run endpoints; Mac tests use a disposable workspace. Store only hashes, route health, and failure evidence, not credentials or page contents. Repairs must be limited to reversible configuration/session renewal and be explicitly labeled.
- **missing:** A first-class disposable canary environment for browser commands, Mac actions, pipeline audio/events, and relay jobs; A routine health contract with expected inputs, outputs, latency, and evidence rather than only lastStatus; Safe repair adapters for stale browser sessions, stopped local agents, mismatched audio profiles, and interrupted jobs; A dependency graph that identifies which owner-facing routines are affected by each failed node; A dashboard and pendant result format that distinguishes tested, untested, degraded, and repaired

### "“Prove that answer and show me exactly what you changed.”"
- **useful because:** Today evidence is fragmented: browser provenance can explain page-derived claims, while Mac jobs and audio pipelines have separate receipts, and the pendant only hears the final answer. The owner needs one cross-surface explanation that can distinguish observed fact, inferred conclusion, and side effect, then point to the exact page, file, job receipt, or audio sequence without dumping private contents into the conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic evidence traversal builds the chain; a cheap background model compresses it into one spoken sentence. Use realtime only for follow-up questions such as “which file?” or “undo that.”
- **latency:** A spoken summary within 2 seconds for recent work; full evidence view within 5 seconds. Traversal must work after relay or Mac restart.
- **cost:** Near-zero for traversal and hashing; small summarization cost only when the owner asks for a natural-language explanation. Storage is bounded identifiers, timestamps, hashes, and source pointers.
- **security:** The pendant receives redacted summaries and opaque evidence IDs by default. Raw page text, shell output, credentials, and private files remain on their source surface. Evidence must be append-only and distinguish 'observed' from 'model inferred'; never claim proof when the source is missing or stale.
- **missing:** A common evidence graph linking browser provenance, Mac action receipts, pipeline sequence IDs, routine runs, and relay messages; Immutable claim records with source freshness, redaction policy, and an explicit observed/inferred/changed classification; A spoken evidence protocol that can page from a one-sentence answer to a source-specific dashboard view; Retention and revocation rules so an owner can remove sensitive evidence without leaving dangling claims presented as proof


## Changes it proposed to its own stack

### `mac-harness` — Add a durable, no-gate execution capsule for every run_shell action: preserve the pre-rewrite action and the actually dispatched action, resolved cwd, selected non-secret environment keys (with secret names and values redacted), pid/process-group, start/finish monotonic timestamps, exit code/signal, stdout/stderr byte counts plus content digests, and the jobId↔ledgerId mapping. On failure, record a machine-readable recovery class (timeout, signal, nonzero exit, output overflow, missing executable) and generate a replay command that is opt-in but does not require reconstructing the original context by hand. Make shell execution use a killable process group so cancel and timeout terminate descendants, then reconcile processing jobs at boot into interrupted/failed rather than leaving them immortal.
- **owner gets:** When the Mac says a task failed, the owner can know exactly what happened and resume it instead of hearing a vague “Failed” and repeating a potentially destructive command. It also makes the agent honest about commands that were silently rewritten and about whether cancellation actually stopped work.
- effort: Medium-high: instrument computerControl.js and executor receipts, pass jobId into orchestrator ledger metadata, add process-group spawn/termination, boot reconciliation, and a small job-detail/replay view. No model work is required.  ·  risk: Capturing environment or output can leak tokens and personal data; redact by key and cap/ hash large streams, with an explicit sensitive-output marker. Killing a process group may terminate child work the owner expected; only use it for the job's own process group and record the signal. Recovery replays must be visibly labeled as replays and never happen automatically.
- cost: No recurring API cost. Small local JSON/digest overhead; bounded capsule storage can replace redundant full output after retention.  ·  latency: Near-zero dispatch overhead for timestamps and exit status; process-group setup adds milliseconds. Job detail becomes faster because it no longer needs a rerun.
- security: Improves auditability without reducing the owner's deliberately unrestricted FULL_CONTROL_MODE. Secret environment values never enter durable records; command text still needs sensitivity classification because shell strings can contain inline secrets.
- depends on: Fix orchestrator ledger closure and pass planMeta.jobId rather than null; Replace exec with a process-group-capable spawn/execFile path while retaining arbitrary shell capability; Define bounded stdout/stderr retention and redaction rules; Boot-time reconciliation of pendant-jobs.json and interrupted ledgers

### `model-routing` — Add a deterministic intent tier for the owner's already-repeated, low-ambiguity Mac requests: Downloads inventory/count, battery/Wi‑Fi, routine status, and job lookup. Compile each into a bounded action plan or GET route, and escalate only when the request adds interpretation (for example, “which files matter?”). Record the estimated tokens and latency saved per bypass so routing improves from evidence rather than guesswork.
- **owner gets:** A simple request should be answered in seconds and should not consume a full planner turn. The owner has issued the Downloads-count request repeatedly; the live routing record shows one such request consumed 5,210 estimated tokens and 2,079 ms in the planner tier.
- effort: Medium: add intent matchers, deterministic handlers, regression tests for false positives, and a routing receipt that explains why escalation occurred.  ·  risk: A matcher could misread an ambiguous command or hide a needed action. Keep the tier read-only, require exact slots for paths/counts, and escalate on any mutation, ambiguity, or missing parameter. It must return the same job/receipt shape as planner execution.
- cost: Material reduction in planner calls for recurring status/inventory questions; effectively zero model cost for deterministic hits. Small local CPU cost.  ·  latency: Likely sub-200 ms for local reads instead of roughly 2 seconds observed for the planner request.
- security: No new access; deterministic handlers should use existing authenticated Mac routes and preserve the same output redaction.
- depends on: Define exact deterministic intents and slot grammar; Use existing GET /machine-context, GET /jobs/:jobId, GET /routines, and run_shell only for the explicitly bounded Downloads inventory; Add routing metrics by intent and escalation reason


## What it asked for

_Nothing._
## Its own summary

Produced four non-duplicate proposals. The highest-value one is the end-to-end 24 kHz superwideband conversation with USB-now/LTE-later handoff, preserving turn IDs and truthful transport state. I also proposed truthful, replayable shell execution capsules with process-group cancellation and crash reconciliation; a cross-surface overnight failure digest with safe retry from the pendant; and deterministic routing for repeated Mac status/Downloads requests. The routing probe measured the concrete waste: a simple Downloads request used 5,210 estimated planner tokens and 2,079 ms.

**Biggest unknown:** The newly granted USB serial diagnostic schema still does not resolve against the live inventory, so I could not read either physically connected chip. The actual missing piece is an implemented, bounded host serial/framing reader (or a bench command path with truthful exit/port diagnostics). Device discovery currently reports the nRF9160 pendant offline and the Mac bridge online; wearable LTE continuity remains unverified.

