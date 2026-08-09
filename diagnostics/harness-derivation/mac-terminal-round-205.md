# Harness derivation — mac-terminal — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish this job end to end. If a step fails, diagnose it, repair what you can, and only wake me when you need a decision.”"
- **useful because:** This would make the hive feel like one dependable assistant instead of a collection of one-shot tools: the pendant starts the request, the relay remains responsible while the Mac or browser works, and failures become repair attempts rather than silent dead ends. It is the single most useful missing behavior for everyday delegation.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to capture the short command and speak the final result; use a cheaper background planner for step diagnosis, retries, and repair. The relay is the durable coordinator, not the voice model.
- **latency:** Acknowledge on the pendant in under 1 second; run repairs asynchronously. Speak a decision request within 10 seconds of an irrecoverable failure, otherwise remain quiet until completion.
- **cost:** Roughly 1 background planning call per failure (usually $0.01–$0.05), plus negligible relay/storage cost; browser/Mac execution dominates wall time, not tokens.
- **security:** A repair may mutate files, browser state, or external services. Keep the existing maximum-access policy, but expose a concise repair plan and exact affected surface in the pendant/dashboard message; never claim success until a postcondition is observed. Secrets stay on the Mac/browser/relay boundary and are not sent to the model unless required.
- **missing:** A durable cross-surface workflow state machine with explicit postconditions; Failure diagnosis that can read shell exit status and preserve stdout/stderr without flattening it; A repair-attempt budget and resumable step cursor shared by Mac and browser jobs; A single completion event consumed by relay, dashboard, and pendant

### "“Run a bench check on both chips and tell me, in plain language, whether the pendant and audio bridge are healthy, what each emitted, and what I should fix next.”"
- **useful because:** The hardware is physically present today but USB truth is otherwise trapped in ad-hoc shell scripts. A bounded bench report would turn a failed flash, silent UART, framing error, or healthy boot into an answer the owner can act on, without pretending the cable is a wearable transport.
- **path:** mac-terminal → mac-planner → relay → dashboard
- **model tier:** Use a deterministic parser for port discovery, bounded capture, timestamps, and known boot/health frames; use a cheap background model only to explain unknown lines. No realtime model is needed.
- **latency:** Start capture within 2 seconds and return a first report in 10 seconds; allow up to 60 seconds for boot/reconnect evidence.
- **cost:** Near-zero API cost for deterministic parsing; at most $0.01 for explanation of novel diagnostic lines. The cost is local disk space for capped timestamped logs.
- **security:** Read-only USB access and local logs only. Never upload raw UART logs by default because they may contain tokens or owner data; send only classified counters/errors to the relay. Require explicit cleanup/retention policy for captured logs.
- **missing:** A real host serial reader/port-list implementation (the granted schema is unresolved in the live inventory); Framing parsers and health-counter definitions for nRF9160 and ESP32; A typed bounded capture action with exit code, port, baud, and byte-count receipts; A dashboard report that links each conclusion to a timestamped log span

### "“Did that actually work? Check the Mac and the browser, show me the evidence, and say exactly what is still unverified.”"
- **useful because:** The owner currently has to trust a terse success string even when a command was rewritten, a browser click only queued work, or a job/ledger cannot be joined. This capability answers outcome questions from observed postconditions and provenance rather than from the planner's intention, and it explicitly preserves uncertainty.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic evidence collection and correlation first; a low-cost model converts the evidence into a short explanation. Reserve realtime for the spoken answer, not investigation.
- **latency:** Speak an initial status in 2 seconds from existing receipts; fetch missing Mac/browser evidence within 15 seconds and revise the answer once.
- **cost:** Usually under $0.01 per verification using structured receipts; screenshots or novel-page interpretation can add $0.02–$0.10. Storage is capped evidence metadata, not page bodies or raw shell environments.
- **security:** Evidence may include sensitive paths, URLs, and visible browser content. Keep raw artifacts local, redact environment variables and credentials, and send the relay only claims, hashes, timestamps, and source references. Do not report success when only dispatch was observed.
- **missing:** A postcondition/evidence schema shared by shell actions and browser commands; Correlation between job IDs, action receipts, ledgers, and browser command IDs; A read-only verifier that can compare before/after state and trace browser claims to provenance; Pendant/dashboard rendering for verified, failed, and unknown states

### "“Put what you hear from me on the pendant into a live, editable workspace on my Mac, show the browser evidence beside it, and keep the spoken conversation and the final document synchronized until I say ‘done’.”"
- **useful because:** Today the pendant conversation, Mac actions, and browser evidence are separate interactions; the owner cannot glance at one authoritative working artifact, correct a misunderstanding without restarting, and leave with a durable result. This would make the wearable useful for hands-free capture while the Mac provides precision and the browser supplies authenticated evidence.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime handles turn-taking and low-latency transcription/acknowledgement. A cheaper background model maintains the structured draft, reconciles edits, and summarizes browser evidence; deterministic code owns versioning and synchronization.
- **latency:** Audio acknowledgement under 500 ms; draft updates under 2 seconds; browser evidence may arrive asynchronously, with visible pending markers rather than blocking the conversation.
- **cost:** Approximately $0.02–$0.10 per sustained session depending on audio duration and evidence interpretation; most cost is realtime audio, while synchronization and version storage are negligible.
- **security:** The workspace may contain private speech, authenticated browser data, and potentially sensitive documents. Keep raw audio and page bodies on their originating surfaces, send the relay only structured deltas and references, show the owner exactly which browser claims entered the draft, and require explicit 'done/send/submit' before any external publication.
- **missing:** A shared versioned workspace object with append-only deltas from pendant speech, Mac edits, and browser evidence; A low-latency event channel from relay to the Mac dashboard and back, with reconnect and conflict resolution; Browser evidence adapters that attach source URL/provenance to individual draft claims rather than only to a completed job; A Mac editor view with speech-safe live updates and an explicit finalization boundary


## What it asked for

_Nothing._
## Its own summary

Round 205 produced three distinct owner-facing capabilities: (1) self-healing cross-surface delegation that diagnoses and repairs Mac/browser failures before waking the owner, (2) a bounded dual-chip USB bench health report for the now-physically-connected nRF9160 and ESP32, and (3) evidence-backed outcome verification that correlates Mac receipts and browser provenance and says what remains unknown. The live USB diagnostic grant still does not resolve: the inventory has no serial capability, so no port was read. I informed mac-planner.

**Biggest unknown:** Whether the existing browser provenance routes are live and whether any agent has already implemented a shared postcondition/evidence schema; the proposal recorder accepted the capabilities but flagged those pieces as not observed.

