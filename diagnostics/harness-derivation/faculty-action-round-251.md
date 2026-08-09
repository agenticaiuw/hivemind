# Harness derivation — faculty-action — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness round 251** — Mac agent is fully ready: Accessibility and Screen Recording trusted for AI Pendant Agent, input reachability verified, Safari browser bridge online with one device last seen within ~0.2s, relay reachable, and no pending browser commands. The physical pendant is still absent from the live device table; only home-macbook-bridge and offline mobile are listed.
  - evidence: GET /observe, GET /browser/status, and GET /ops/status at 2026-08-09T02:08Z

## Capabilities it proposed

### "“Make this multi-step change across my Mac and browser, but before anything irreversible, tell me exactly what will change; only continue if I approve the concrete diff, and prove afterward that every step landed.”"
- **useful because:** Today planning, execution, and verification are separate surfaces. This gives the owner one safe operation: a spoken, redacted change-set; a physical approval boundary; ordered execution; independent postcondition checks; and a truthful verified/unknown result instead of claiming success from executor receipts.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for planning and diff generation; realtime only for the short spoken summary and approval exchange
- **latency:** 2–5 seconds to produce the change-set, under 1 second for pendant approval acknowledgement, then stepwise execution with progress; no silent timeout-based commit
- **cost:** Usually 1 planning call plus cheap verification calls per step; roughly 2–8x a normal single action depending on step count. Dominant costs are model planning and fresh browser/Mac evidence, not haptics.
- **security:** The pendant receives only a redacted human summary, operation digest, risk, and expiry—not form secrets or page contents. Approval binds to the exact digest. Each step must be independently verified; a failed or unknown step pauses later destructive steps. Requires explicit policy for whether compensating undo may run automatically.
- **missing:** A first-class change-set/diff object with stable step IDs and digest; A commit coordinator that can pause, resume, and compensate after partial completion; Per-step executor receipt correlation in verify_operation_step; A spoken/redacted diff renderer suitable for the pendant

### "“At the time I specified, check that the real-world preconditions are still true, then do the action across my Mac/browser; if anything changed, don't guess—tell me on the pendant and leave a resumable approval waiting.”"
- **useful because:** A scheduled intent is dangerous when it fires against stale assumptions. This makes routines conditional on fresh observed Mac/browser state, with a deliberate stop on drift and a resumable operation rather than a blind retry. It is especially useful for prices, appointment windows, recipient/account selection, and browser sessions that change overnight.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** background model for routine compilation and condition normalization; cheap deterministic checks first; realtime only if the owner is needed to resolve drift
- **latency:** At fire time, 1–3 seconds for freshness checks; action starts only after all required predicates pass. If blocked, notify within one haptic/audio event and keep the operation pending until expiry.
- **cost:** Low when predicates are structured (mostly route calls); one model call only when a natural-language predicate must be interpreted or drift explained. Roughly <$0.02 for a normal firing, higher for ambiguous pages.
- **security:** Never treat a stale heartbeat or executor receipt as a predicate. Each predicate declares sensitivity and freshness. Do not include private page contents in pendant notifications. Expire pending operations and require physical approval for external side effects; never silently substitute a different account, recipient, or browser tab.
- **missing:** A persisted predicate schema with freshness limits and safe failure semantics; A routine firing coordinator that snapshots evidence before execution; A way to bind a pending operation to the exact browser session/tab and resume only if its identity remains valid; A dashboard view of blocked predicates and expiry

### "“If something I asked you to do partially failed or became unverifiable, stop all retries, gather the minimum fresh evidence, and give me one safe recovery choice on the pendant—resume, undo what definitely happened, or abandon.”"
- **useful because:** Partial completion is the dangerous state: a message may be sent while a calendar update failed, or a browser submit may be unknown. This turns an opaque failed job into a bounded recovery decision and prevents duplicate submissions. The owner gets a concise explanation and a single safe next gesture rather than a second attempt made on assumptions.
- **path:** relay → faculty-perception → faculty-action → mac-planner → browser → pendant → dashboard
- **model tier:** cheap deterministic state machine for receipts, digests, idempotency, and expiry; background model only to summarize evidence in human language
- **latency:** Detect and freeze within seconds of a failed/unknown step; evidence collection under 5 seconds; no automatic retry of external side effects. The owner can choose a recovery path later while the lease remains valid.
- **cost:** Low: mostly receipt and verifier calls, with a small summary call only for ambiguous cases. About <$0.01 for deterministic failures and <$0.05 when fresh browser/Mac evidence and explanation are needed.
- **security:** Recovery choices are bound to the original operation and step digests. 'Undo' is allowed only when a verified compensating action exists; otherwise expose unknown and do not claim reversal. Never replay a non-idempotent browser submit. Pendant payload contains no secrets or page content; expire and cryptographically bind queued choices.
- **missing:** A durable partial-operation state machine with per-step idempotency keys; A recovery planner that advertises only verified compensations; A fresh-evidence bundle format shared by faculty-perception and faculty-action; A way to freeze/cancel downstream queued steps atomically

### "“When I’m on a phone call, keep a private running record of decisions and commitments, and afterward turn only the confirmed action items into reminders or calendar drafts.”"
- **useful because:** The pendant is present for the conversation while the Mac can control iPhone Mirroring and create structured Mac records. Today call audio, spoken decisions, and follow-up actions remain disconnected. This would prevent forgotten commitments without silently sending messages or scheduling anything.
- **path:** pendant → relay → mac-planner → ios → dashboard
- **model tier:** realtime for low-latency private call transcription and brief action-item extraction; background model after the call for cleanup and deduplication
- **latency:** Under 500 ms for rolling local status; no audible interruption to the call. A post-call draft should appear within 30 seconds of hang-up.
- **cost:** Realtime audio/transcription dominates: roughly one realtime session plus a small post-call extraction call. Cost scales with call duration; drafts themselves are cheap.
- **security:** Call audio and transcript are highly sensitive. Default to ephemeral processing, encrypt any retained notes, show a recording/transcription indicator, and require explicit owner confirmation before creating reminders, calendar entries, or messages. Never transmit call audio to a third party without a visible policy choice.
- **missing:** An explicit iPhone call-audio capture/control bridge compatible with iPhone Mirroring; A pendant mode that can receive or locally buffer call markers without interrupting the call; Speaker-attribution and confidence metadata for action-item extraction; A post-call confirmation UI that distinguishes quoted commitments from inferred tasks

### "“Before I share this file or paste this text anywhere, find sensitive details, show me exactly what would leave my devices, and let me approve a redacted version or cancel.”"
- **useful because:** The current action surfaces can type or upload, but they do not give the owner a reliable data-boundary review. This capability makes sharing understandable at the moment it matters, across Finder, Mail, Messages, and logged-in browser sessions.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for local classification and redaction suggestions; realtime only for a short spoken summary and physical approval exchange
- **latency:** 1–5 seconds for ordinary text/files; larger files can be scanned asynchronously but must remain staged until review. No upload or paste before approval.
- **cost:** Mostly local hashing/classification; one model call for ambiguous content. Typical cost under $0.05, dominated by document parsing for large files.
- **security:** The scanner must run locally whenever possible and must never send raw secrets to the relay or model unnecessarily. The digest must bind source, destination, exact redaction, and expiry. A redaction failure must block sharing rather than fall back to the original. Approval must not expose the sensitive content on the pendant.
- **missing:** Local content classification and deterministic redaction engine for common secrets and personal identifiers; A destination-aware preview format for browser fields, mail, messages, and uploads; A hard gate in every paste/upload/send executor path; A safe way to speak a useful summary without reading secrets aloud

### "“Create the final document from these sources, keep a private provenance map of what came from where, and when a source changes later, tell me exactly which claims or sections are now stale instead of silently rewriting it.”"
- **useful because:** A Mac agent can manipulate files and a browser can access sources, but today the owner cannot tell which parts of a deliverable depend on which source or whether an old fact silently survived. This creates an auditable, updateable artifact rather than a one-shot generated file.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for extraction, citation mapping, and change impact analysis; realtime only for short owner queries or approval of an external publication
- **latency:** Initial small document in under a minute; large projects can run asynchronously. Source-change alerts should arrive after a bounded scan, not block normal Mac use.
- **cost:** Parsing and hashing can be local; model cost scales with source and document size. A later incremental scan should process only changed sources and affected sections.
- **security:** Source permissions and private documents must remain local or within an explicit allowlist. Provenance must store hashes and locators rather than unnecessary copies. Never publish an updated artifact automatically; external sharing requires a fresh review and approval.
- **missing:** A provenance graph linking output spans to source hashes, URLs, files, and retrieval timestamps; Incremental source watcher/snapshot support for browser pages and local files; A document renderer that can expose stale claims and citation evidence without leaking private sources; A versioned output store with reversible updates


## Changes it proposed to its own stack

### `relay` — Add a durable operation coordinator that treats every cross-surface request as an append-only step graph: each step has an idempotency key, executor receipt, independent verification receipt, compensation (if any), expiry, and state {planned, approved, running, verified, unknown, cancelled}. Freeze downstream steps on unknown; expose a recovery choice instead of retrying. Correlate verify_operation_step with operation_id plus executor attempt_id, and persist the digest so a later approval cannot be replayed against a changed plan.
- **owner gets:** When a task half-completes, the owner gets an honest answer and a safe way forward instead of duplicate messages, double purchases, or a false success. It also makes the pendant's outcome beacon meaningful because each status corresponds to a real durable state.
- effort: Medium-high: coordinator schema, migration from existing job/receipt records, atomic transitions, and adapters for Mac/browser executors.  ·  risk: Migration bugs could strand existing jobs or mark an action unknown unnecessarily. Roll out read-only shadow state first, reconcile against existing receipts, and preserve the current cancel/undo paths as fallback.
- cost: Negligible storage and relay compute; a few additional verifier calls per step. No new hardware cost.  ·  latency: Adds roughly one persistence and one verification round per step; deliberate but bounded. It prevents costly and dangerous blind retries.
- security: Improves replay resistance and auditability. Must encrypt sensitive evidence references, keep secrets out of operation digests, and enforce expiry/monotonic state transitions.
- depends on: verify_operation_step must accept an executor attempt_id/action correlation field; A canonical idempotency-key scheme for browser and Mac action adapters; Owner policy for which compensations may run without a new physical approval


## What it asked for

_Nothing._
