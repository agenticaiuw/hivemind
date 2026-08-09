# Harness derivation — unified — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask “is everything okay?”, give me one short spoken answer that distinguishes pendant audio health, relay reachability, Mac/browser availability, and any unfinished work, then tell me the single safest next step."
- **useful because:** The owner currently has to ask several surfaces separately and cannot tell whether silence is a codec failure, a dead bridge, or a queued action. A correlated verdict turns an opaque wearable into something trustworthy in one sentence.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic health aggregation first; background model only to compress evidence into owner language, never realtime for diagnosis.
- **latency:** Under 2 seconds for the normal snapshot; under 5 seconds if a fresh audio validation is required.
- **cost:** Near-zero for route snapshots; roughly $0.001–$0.01 only when a background model summarizes nontrivial evidence.
- **security:** Expose status and redacted error classes only; never read browser page contents or secret-bearing job parameters. Any repair or action must be separately confirmed.
- **missing:** A typed cross-surface health verdict route that joins pendant/audio, relay, Mac, and browser state; A small policy mapping symptoms to one safe next step; A spoken response formatter with a strict one-sentence budget

### "After a Mac, browser, or relay interruption, ask me only about the steps that cannot be safely replayed, automatically continue idempotent work, and tell me exactly what was skipped or blocked."
- **useful because:** Interrupted work is currently either forgotten or risks being performed twice. This gives the owner continuity without duplicate messages, purchases, edits, or browser submissions, while preserving a clear human decision point for unsafe steps.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic ledger/replay engine; background model only for explaining the resulting plan. No realtime model needed unless the owner asks while speaking.
- **latency:** Resume plan in under 1 second after startup; spoken explanation under 3 seconds.
- **cost:** No meaningful model cost for classification; <$0.005 for optional explanation.
- **security:** Gate on replaySafety, not reversibility: only idempotent/additive steps may auto-run. Require the existing physical transaction approval latch for irreversible/off-machine actions; never replay withheld secrets.
- **missing:** Close ordinary orchestrator ledgers so successful plans are not misclassified as interrupted; A relay job lease_until and expiry/requeue sweep; A startup caller that invokes planResume and executes only approved runnable steps; A continuation path for pending approval on the owner's next conversation

### "Run a bounded bench diagnostic on the connected pendant and audio bridge, correlate both UART logs with relay/audio events, and hand me a redacted bug report with the first failing layer and the exact next test."
- **useful because:** The hardware is physically connected and testable now, but a dual-UART capture is just text and the owner cannot tell modem, bridge, codec, or relay failure apart. This turns today's bench setup into actionable evidence without pretending USB is a product transport.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic capture bounds, timestamp/sequence correlation, and threshold checks; background model only writes the concise bug report.
- **latency:** Capture 30–120 seconds as requested; report within 10 seconds after capture ends.
- **cost:** No realtime model cost; <$0.01 for optional report synthesis.
- **security:** Bench-only explicit trigger; never capture microphone PCM by default, only diagnostic lines and counters. Redact tokens, identifiers, and room content. Require confirmation before uploading logs off the Mac.
- **missing:** A structured Mac bench-UART reader for both known USB ports with bounded duration and exit receipts; A common timestamp/sequence schema between nRF9160, ESP32 bridge, relay pipeline, and audio delivery receipts; A correlator that classifies first-failure layer and preserves raw logs locally with retention/erase controls; A dashboard/downloadable report with redaction preview

### "Before I approve a risky request, let me ask “show me what this would change” and receive a reversible simulation across the real Mac files, logged-in browser session, and relay state—including conflicts, side effects, and an undo boundary—without touching anything."
- **useful because:** The owner can preview isolated forms or tidy plans, but cannot see the combined consequences of a multi-surface action before approval. A true cross-surface simulation makes high-impact automation understandable instead of asking for blind trust.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic snapshot/diff engine and capability-specific simulators; background model only explains the diff in plain language.
- **latency:** Simple simulations under 3 seconds; complex browser workflows under 10 seconds, always clearly marked as simulation.
- **cost:** Usually no model cost; <$0.02 for optional explanation of a large diff.
- **security:** Simulation must use isolated browser transactions or read-only snapshots, never submit forms or send data. Redact secrets and page contents by default. Snapshot retention must be bounded and deletable.
- **missing:** A cross-surface simulation contract with declared read set, predicted writes, and confidence; Browser transaction recording or site-specific dry-run adapters; Mac filesystem/app shadow state for writes outside existing preview modules; A diff viewer and spoken summary that distinguishes guaranteed effects from predictions

### "Before anything leaves my Mac or logged-in browser, show me a compact privacy receipt saying what data will leave, who receives it, why it is needed, and what will be retained; let me allow, redact, or cancel that specific transfer."
- **useful because:** Approval currently answers whether an action is allowed, not whether its data exposure is understood. The owner needs a content-level boundary for emails, uploads, browser forms, research services, and relay storage.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic taint/provenance and destination policy engine; a background model may suggest redactions but cannot silently apply them.
- **latency:** Receipt in under 1 second for known fields; under 3 seconds when classifying document content.
- **cost:** Low deterministic cost; <$0.01 for optional sensitive-content classification.
- **security:** Perform classification locally whenever possible. Never transmit raw content merely to classify it. Require explicit confirmation for new destinations or sensitive categories; retain only the signed receipt, not a copy of the payload.
- **missing:** Payload provenance and sensitivity labels across Mac actions, browser commands, and relay jobs; A transfer-intercept hook before send/upload/form-submit actions; Owner-editable destination and data-category policy; Pendant/dashboard receipt rendering with redact-and-retry support

### "Let me declare a bounded mission—goal, allowed apps/sites, time limit, data limit, and stop conditions—and have the pendant tell me when the mission is complete, blocked, or needs a decision, instead of improvising beyond what I asked."
- **useful because:** Today an action can span several nodes, but the owner has no single contract for scope, budget, or stopping. A mission envelope makes long-running automation predictable and lets the wearable remain the final attention channel.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic mission policy, budget accounting, and stop-condition enforcement; planner model only decomposes the goal into steps.
- **latency:** Mission creation under 2 seconds; progress events batched to avoid interrupting conversation; completion/blocked notification within one event cycle.
- **cost:** Background planning typically <$0.03; deterministic progress and enforcement are negligible.
- **security:** Allowlist surfaces and destinations, cap action count/runtime/data volume, fail closed on policy ambiguity, and require physical approval for actions outside the declared envelope. Do not expose browser secrets in mission summaries.
- **missing:** A durable mission envelope and budget ledger spanning relay jobs, Mac jobs, and browser sessions; Step-level scope checks before execution; Stop-condition/event evaluation and owner-visible progress receipts; A pendant notification policy that defers nonurgent mission updates until a natural conversation boundary


## What it asked for

_Nothing._
