# Harness derivation — faculty-action — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you send, delete, book, or edit anything, make sure the world is still the world I approved: if the page, file, or app changed since you reviewed it, stop and tell me exactly what drifted instead of acting."
- **useful because:** Prevents the most dangerous class of automation error: a correct decision applied to a stale page, renamed file, changed price, or moved calendar slot. The pendant can give a concise 'stale—needs review' outcome while the Mac/browser retain private details.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-perception → mac-planner → mac-vision → browser-extension → faculty-action
- **model tier:** Cheap background planner computes a normalized precondition digest; realtime model is used only to explain a mismatch or ask for renewed approval.
- **latency:** 150–400 ms for preflight hashes; up to 2 s for a fresh browser/app observation. If drift is detected, fail closed immediately rather than spending model latency retrying.
- **cost:** Usually under $0.01 per guarded action; dominated by one small perception/planning call, not the hash or receipt work.
- **security:** Never send page secrets or form contents to the pendant. Store only typed locators, sensitivity labels, and salted digests. A mismatch must not be silently refreshed into approval; require a new human decision for destructive or external actions. Needs a policy-defined treatment for volatile fields such as clocks and stock counts.
- **missing:** A first-class precondition_digest and expected_revision field in the operation envelope; faculty-perception support for producing a fresh typed digest from app_state/file_state/browser_field evidence; faculty-action enforcement that refuses execution on digest mismatch before invoking Mac/browser; A canonical volatility policy and owner-selected approval rules for each action class

### "If you started something on my pendant and the Mac, browser, or link disappeared halfway through, keep the exact operation alive, tell me what is pending, and continue only after checking that it is still safe—not by blindly replaying it."
- **useful because:** A dropped connection should produce a recoverable, truthful handoff rather than a duplicate email, double purchase, or abandoned half-finished workflow. It lets the owner walk away and return later while preserving the distinction between not started, partially applied, verified, and unknown.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → faculty-perception → faculty-action → faculty-judgement
- **model tier:** Background state machine and cheap deterministic retry logic; use the realtime tier only when the owner asks for a spoken status or must resolve an ambiguity.
- **latency:** Persist the checkpoint before every side effect (<100 ms target). On reconnection, re-observe within 2 s and resume only after preconditions pass; otherwise surface a pending/unknown haptic outcome.
- **cost:** Pennies or less per recovery; storage and receipts dominate, with model use only for ambiguous state reconciliation.
- **security:** Exactly-once is impossible across arbitrary external systems, so never claim it. Each step needs an idempotency key, a durable checkpoint, a postcondition verifier, and an explicit unknown state. Do not replay a step that might have committed externally; require owner approval for non-idempotent continuation. Encrypt sensitive payload references and keep secrets on the Mac/browser.
- **missing:** A durable saga/checkpoint record linking operation_id, step_id, attempt_id, idempotency key, and last known state; A relay wake/reconnect trigger that pushes pending status to the pendant without exposing payloads; Action executor semantics for resume versus compensate versus stop; Verifier-driven recovery policy that distinguishes not_started, applied, verified, and unknown; A bounded retention and expiry policy for abandoned operations

### "Run a no-flash bench check of my connected pendant and audio bridge before I leave: prove the buttons, link, 24 kHz audio path, storage failure path, and outcome signaling work, and give me one signed pass/fail receipt with the failing component named."
- **useful because:** The hardware is physically on the Mac now, but today there is no owner-facing way to know whether it is safe to wear. A deterministic preflight catches a dead serial link, broken bridge, audio regressions, or missing failure buffering before the device matters in the field.
- **path:** mac-terminal → mac-planner → relay → faculty-action → faculty-perception → pendant → relay-realtime
- **model tier:** No expensive model for measurements: use deterministic test scripts and a small background summarizer; realtime only reads the final result aloud if requested.
- **latency:** 30–90 s for the full suite; individual checks should stream progress and fail fast on connection or power faults.
- **cost:** Effectively zero API cost; dominated by local test execution and optional fixture playback. No Mac microphone capture is needed.
- **security:** Read-only by default: no flashing, no firmware mutation, no filesystem cleanup, and no upload of raw audio. Use synthetic fixtures and hashes/metrics only. Require explicit approval before any test that writes a diagnostic file or changes device configuration.
- **missing:** A resolved mac-terminal operation for enumerating the two USB serial devices and collecting bounded serial diagnostics with exit status; A test protocol understood by both nRF9160 and ESP32 firmware for button/LED/link/storage self-tests; A deterministic bridge loopback command that reports Opus framing, packet loss, and round-trip timing; A signed, persisted acceptance receipt joining all component evidence without claiming LTE registration; A safe owner-visible command surface that clearly labels USB as bench-only

### "Before anything leaves my Mac or browser, show me exactly what personal data would cross the boundary, remove what I did not authorize, and let me set a rule like 'never send addresses or private notes to this site.'"
- **useful because:** The owner gets a genuine data-egress firewall rather than a vague promise that an action is safe. It protects against an agent putting the right text into the wrong recipient, leaking hidden page context, or forwarding a private note while still allowing useful automation.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action → relay
- **model tier:** A small background classifier and deterministic policy engine handle field classification and redaction; realtime is reserved for explaining a blocked transfer in conversation.
- **latency:** Under 500 ms for known schemas and local files; up to 2 s for an unfamiliar document, with fail-closed behavior if classification is uncertain.
- **cost:** Typically below $0.02 per outbound operation; classification of novel text dominates, while known-field policy checks are local.
- **security:** Raw secrets and sensitive text must stay on the Mac/browser wherever possible. The pendant receives only categories, counts, destination, and a short owner-authored summary. Policies must be immutable for the duration of an operation, logged with a digest, and never weakened by a model's explanation.
- **missing:** A typed outbound-payload manifest describing source, destination, field category, and redaction action; A local classifier/redactor that can inspect browser fields, messages, files, and clipboard without uploading raw content; A durable owner policy store with deny-by-default rules and per-destination exceptions; Executor support for submitting the redacted payload rather than the original and proving which digest was sent

### "When I ask you to find something across my Mac, browser, and pendant history, return a time-bounded answer with a map of where each fact came from, what was not searched, and a one-touch way to erase the temporary search trail."
- **useful because:** Today a confident answer can silently mix stale Mac files, browser sessions, and device notes without telling the owner which source supported which sentence. Provenance-aware personal search would make the system useful for real recall while preserving the owner's ability to clean up the investigation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → relay
- **model tier:** Use a cheaper background retrieval and ranking model; realtime only summarizes the already-provenanced result aloud.
- **latency:** Initial answer within 5 s for local indexes and 10 s for browser/session searches; stream source completion and stop at the owner's requested time window.
- **cost:** $0.01–$0.05 depending on the number of sources; indexing and local hashing dominate recurring cost rather than generation.
- **security:** Search should be scoped explicitly by time, source, and sensitivity. Never merge secret browser fields into a spoken answer. Store source hashes and redacted snippets by default, make temporary indexes expire automatically, and require a deliberate owner gesture to retain a result as memory.
- **missing:** A federated query contract for Mac files, browser state, relay records, and pendant outbox items; Stable source IDs and freshness/version metadata that survive a multi-source query; A provenance graph linking each returned claim to evidence and explicitly recording omitted/unavailable sources; A temporary-index lifecycle with owner-visible deletion and proof of deletion

### "Let me hand a live task from my voice to the Mac without repeating myself: keep the exact goal, constraints, and private context on the relay, show the Mac only the minimum it needs, and let me take it back to the pendant at any point."
- **useful because:** This makes the hive feel like one assistant instead of separate agents. The owner can start while walking, let the Mac do a long browser or file workflow, interrupt it from the pendant, and resume with the same intent—without copying a transcript or exposing every private conversation to every surface.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → mac-vision → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime handles the initial spoken intent and interruption only; a cheaper background model compiles a least-privilege task capsule and summarizes progress.
- **latency:** A handoff acknowledgement in under 1 s; Mac receives a task capsule within 3 s. Taking control back should cancel new side effects within one checkpoint interval.
- **cost:** $0.01–$0.04 per handoff, dominated by capsule compilation and progress summarization; raw audio need not leave the relay after transcription.
- **security:** The relay must issue capability-scoped capsules, not full transcripts or credentials. Each capsule has destination, allowed actions, expiry, revocation, and sensitivity labels. Revocation must reach browser and Mac before another side effect, and the pendant must show when the task is running elsewhere.
- **missing:** A capability-scoped task capsule format with revocation and expiry; Relay routing for bidirectional control and progress events between pendant and Mac job; Mac/browser executor support for accepting, pausing, and returning a capsule without losing state; A privacy-preserving context compiler that separates required constraints from conversational history; Pendant UI semantics for running, paused, revoked, and returned states using the existing tactile outcome channel


## What it asked for

_Nothing._
## Its own summary

Round 204 produced three new owner-facing capabilities: (1) fail-closed precondition-drift protection before any consequential Mac/browser action, (2) checkpointed interruption recovery that re-observes and never blindly replays an uncertain step, and (3) a no-flash connected pendant/ESP32 bench acceptance run producing one signed pass/fail receipt. I discovered the live device table: Mac bridge online, Safari online, but the pendant is still not relay-registered. The proposals explicitly identify the missing connective contracts rather than pretending existing routes already provide them.

**Biggest unknown:** I still need a resolved, read-only mac-terminal diagnostic operation with typed enum values for serial enumeration and bounded device test results (including exit status), plus a firmware-side diagnostic protocol for the nRF9160 and ESP32. Without those, the bench acceptance capability can be designed but cannot honestly prove button, storage, or bridge state. For production recovery, the other key missing piece is a durable operation saga/checkpoint envelope with explicit unknown-state semantics.

