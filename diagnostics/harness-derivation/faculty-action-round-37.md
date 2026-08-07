# Harness derivation — faculty-action — round 37

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution reachability** — At fresh probe, Mac agent fullControlMode=true but ready=false because Accessibility trusted=false and Screen Recording granted=false; browser extension home-chrome offline with 3 pending commands. Relay and Mac bridge are online. GUI/browser actions must be reported blocked, not attempted.
  - evidence: GET /ops/status and GET /browser/status at 2026-08-07T10:48Z

## Capabilities it proposed

### "“Make this happen everywhere it needs to, and tell me only when you can prove it worked.” For example: update a private web record, mirror the result into a Mac file or reminder, and leave me a receipt I can trust even if the browser or Mac briefly disconnects."
- **useful because:** Today judgement can choose a multi-step plan, but action cannot establish end-to-end success: a browser submission may succeed while the Mac mirror fails, or a disconnected surface may make an action look lost. This gives the owner one durable, evidence-backed completion state instead of optimistic acknowledgements or repeated manual checking.
- **path:** faculty-judgement emits a typed plan with step dependencies, allowed side effects, and a postcondition for each step → relay durable job runner owns retries, idempotency keys, deadlines, and a durable action ledger → browser extension performs authenticated private-page steps and returns URL/tab, extracted confirmation text, and before/after evidence → Mac agent performs local file/reminder/app updates and returns artifact hashes or API-level confirmation → faculty-perception independently re-reads each changed surface to verify the declared postconditions; it marks unknown rather than success when UI reachability is false → pendant displays a short success/partial/blocked status and lets the owner request retry or inspect the spoken receipt
- **model tier:** Use the cheaper background model for decomposition, retries, and evidence comparison; reserve realtime only for the owner's live request and concise status. Deterministic idempotency/postcondition checks should not consume model tokens.
- **latency:** A reversible two-surface job should acknowledge in under 1 second, finish in 5–30 seconds when both surfaces are online, and remain durable for hours when offline. Speak only the final verified/partial result; never claim success from dispatch alone.
- **cost:** Roughly $0.001–$0.02 per completed job depending on whether semantic extraction or conflict resolution needs a model; most steps are relay/database, browser bridge, and Mac-agent calls. Audio/status is negligible.
- **security:** Private page contents and local artifacts stay on their respective surfaces except for the minimum evidence projection (field names, hashes, and short confirmation snippets). Irreversible steps require the existing approval policy and a fresh consent lease; retries must be idempotent and never blindly resubmit. The receipt should expose exactly what changed, where, when, and what remains unverified.
- **missing:** A durable cross-surface action ledger with step state, idempotency key, dependency, deadline, and evidence references; A typed postcondition verifier that can ask browser and Mac surfaces to re-read state after mutation; A relay durable runner (the existing browser router/receipt work is not enough); A pendant status/receipt protocol and local indication for verified, partial, blocked, and retry states; A cross-surface consent lease enforced at execution time for irreversible steps; Fresh Accessibility/Screen Recording and browser-extension reachability before any GUI action can be considered executable

### "“Coordinate this change across my private browser account and my Mac, but if one side fails, leave the other side in a safe, recoverable state and tell me exactly what I need to approve next.” For example, update a logged-in order or appointment, then update my local calendar/reminder only after the private site confirms the change."
- **useful because:** The owner cannot safely perform coupled changes today: a browser mutation and a local Mac mutation are separate jobs, so a disconnect can leave contradictory state or cause a retry to duplicate the private action. This is a distinct transactional guarantee, not merely a receipt after independent actions.
- **path:** faculty-judgement declares a two-phase plan with a reversible preparation phase, a commit point, and compensation action → relay coordinates the transaction and persists a transaction record, fencing token, timeout, and commit decision → browser extension prepares and verifies the authenticated-site mutation without committing irreversible effects until the coordinator authorizes it → Mac agent prepares a local reminder/calendar/file change in a staging location and returns a deterministic artifact identifier → relay commits in a fixed order, then asks faculty-perception to verify both resulting states; if the second side fails, it invokes the declared compensation or leaves a clearly marked pending state → pendant announces the commit decision and exposes a single retry/abort control, never silently repeating a committed private mutation
- **model tier:** Use deterministic orchestration and local adapters for transaction mechanics; use a cheap background model only to translate unstructured site confirmations into typed facts. Realtime is needed only to explain a pause or request approval during the owner's conversation.
- **latency:** Preparation should complete in under 10 seconds when surfaces are reachable; commit and verification typically under 10 additional seconds. If a surface disappears, freeze safely within the configured timeout and retain the transaction for later resume rather than guessing.
- **cost:** About $0.002–$0.03 per transaction, dominated by occasional semantic confirmation extraction; storage and coordination are inexpensive. Compensation and verification add network calls but no continuous model usage.
- **security:** Private account data stays in the browser adapter; the relay receives only typed facts and transaction identifiers. A fresh consent lease is required at commit for irreversible actions. Fencing tokens prevent stale retries, and compensation must be explicitly declared and bounded—never invent a reverse action.
- **missing:** A transaction coordinator with prepare/commit/abort semantics across browser and Mac adapters; Staging APIs for local Mac changes and a browser-side prepare mode; Fencing tokens and durable commit decisions that survive relay or bridge restarts; Typed compensation definitions and a safe pending-state UI; Cross-surface approval enforcement at the commit boundary; Post-commit verification from an independent perception pass


## Changes it proposed to its own stack

### `relay` — Add an append-only Action Truth Ledger and verifier coordinator. Each planned step gets a stable job/step id, idempotency key, intended mutation, deadline, and machine-readable postcondition. The coordinator records dispatch, receipt, verification, retry, blocked, and unknown states separately; after every mutation it schedules a read-back through browser or Mac and stores minimal evidence references (surface, URL/path, timestamp, hash, short quote). A job is complete only when all required postconditions are verified; otherwise it remains partial/unknown and is safely resumable.
- **owner gets:** The owner stops hearing “done” when only a command was sent. They get a precise answer—verified, partially verified, blocked, or unknown—with enough evidence to continue safely after a disconnect, without duplicate submissions.
- effort: Medium/high: schema and durable storage, adapters for browser/Mac typed reads, verifier rules, retry/recovery semantics, receipt API, dashboard/pendant rendering, and integration tests using forced disconnects and duplicate delivery.  ·  risk: A verifier may miss a valid change or a site may expose stale cached state; use bounded re-read attempts, freshness timestamps, and explicit unknown status. Ledger growth needs retention and redaction. Recovery is replay from the last durable step, never blind whole-job replay.
- cost: Small D1/R2/storage and network overhead per step; occasional cheap background-model call only for unstructured confirmation text. No realtime-model requirement.  ·  latency: Adds one read-back round trip per mutation (typically 0.5–5 seconds); can verify independent steps in parallel while preserving dependencies.
- security: Evidence is minimized and redacted; private page text remains local where possible. Irreversible actions require a fresh consent lease checked by the coordinator, and ledger access must be authenticated/audited.
- depends on: durable relay job runner; typed browser/Mac action and read adapters; cross-surface consent lease; fresh reachability/permission probes; pendant receipt/status transport


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: transactional coordination of coupled private-browser and Mac changes using prepare/commit/abort, fencing tokens, declared compensation, independent verification, and pendant-visible approval/recovery. This addresses inconsistent cross-surface state rather than merely reporting individual action receipts.

**Biggest unknown:** The exact owner-approved policy for which browser and Mac mutations may be compensated automatically versus requiring manual recovery.

