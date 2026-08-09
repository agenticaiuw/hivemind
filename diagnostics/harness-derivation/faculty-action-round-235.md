# Harness derivation — faculty-action — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the operation that was interrupted, but only if the world is still in the state you expected.”"
- **useful because:** A dropped link, app restart, or browser reload currently leaves the action facet with an ambiguous half-run. This capability turns that ambiguity into a safe, useful recovery: perception re-checks every unfinished step, action resumes only from a verified boundary, and the owner gets one plain-language explanation instead of a duplicate submission or silent abandonment. It is the single most useful action capability because it makes long tasks trustworthy rather than merely executable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for journal reconciliation and cheap local checks; realtime only when the owner asks what is happening
- **latency:** Under 2 seconds for a resume decision when cached postconditions are available; up to 10 seconds for fresh browser/Mac verification
- **cost:** Usually <$0.01 per recovery; dominated by one small judgement call, not by the Mac/browser checks
- **security:** Never replay a mutation from an executor receipt alone. Each unfinished step needs a fresh faculty-perception verification with locator and provenance; private/secret evidence stays as hashes or minimal snippets. If a step is not provably complete, stop and require the existing physical transaction approval before retrying. The relay must expire recovery leases and deduplicate operation/step IDs.
- **missing:** A recovery coordinator that consumes executor receipts and verifier results and computes a resumable boundary; An additive operation_id/attempt_id correlation field on verify_operation_step and action receipts; A durable, user-readable recovery explanation in the dashboard and a compact outcome event for the pendant

### "“Tell me exactly what changed on my Mac and in my open browser since I last left, and let me undo only the changes I choose.”"
- **useful because:** The owner can ask the pendant for a trustworthy return-to-work briefing instead of reconstructing tabs, files, drafts, and app state from memory. It is more than presence: it correlates a baseline with current state, separates the agent's mutations from outside changes, and offers targeted undo without rolling back unrelated work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for state hashing/diffing; realtime only to summarize the selected diff in conversation
- **latency:** 3 seconds for a normal diff; 10 seconds if browser snapshots or file manifests must be refreshed
- **cost:** <$0.01 for hash-based diffs; LLM cost only for summarization and selected undo planning
- **security:** Baselines must be content-addressed and encrypted; default evidence is names, metadata, and hashes, never file contents or form secrets. Browser fields marked private/secret are represented only by redacted change markers. Undo is per mutation, requires an action receipt and fresh postcondition verification, and must fail closed when an outside edit makes reversal unsafe.
- **missing:** A durable per-owner baseline/checkpoint store with explicit checkpoint creation and expiry; A provenance-aware diff service that joins Mac action ledger entries, browser command results, and fresh observations; A selective undo planner that can present candidate reversals without treating all changes as agent-owned

### "“Repeat your last answer.” (turn the pendant wheel one click toward me)"
- **useful because:** A missed answer is not a failed download: every byte may have arrived while the owner was distracted. A physical, low-attention replay control lets the owner recover without saying the wake word again or forcing the realtime model to guess which answer they mean. It is especially valuable in noise, while walking, or when the link has just recovered.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** No new model call when the artifact is still cached; otherwise background retrieval, with realtime only for a short spoken confirmation
- **latency:** Start playback within 300 ms for a cached response; within 3 seconds after a cellular retry
- **cost:** Near-zero for cached replay; one small retrieval/metadata call when the artifact is absent
- **security:** The wheel must address an opaque response ID, never arbitrary history. Replay only audio artifacts delivered to this owner and within a bounded expiry; require a deliberate two-click or press-and-hold for private/secret responses. Persist only response ID, cursor, codec/rate, expiry, checksum, replay count, and interruption status—not transcript or audio by default. Deduplicate replay requests and never treat replay as a new instruction.
- **missing:** A rotary encoder input and debounce/gesture firmware integration (the owner has requested this product direction; current bench buttons are already assigned); A compact INBOX manifest field identifying the last replayable audio artifact and its expiry; A relay verb that fetches/resumes a specific delivered artifact without invoking the model or re-executing its underlying action


## Changes it proposed to its own stack

### `integration` — Add a mandatory operation_id, step_id, and attempt_id correlation contract across POST /execute receipts, GET /jobs/:jobId/receipts, browser command results, and verify_operation_step. The relay stores an append-only step state machine (started, executor-reported, independently-verified, unknown, compensated) and rejects a retry unless the prior attempt is explicitly terminal or its postconditions have been freshly checked. Every receipt must include the exact action class, reversibility, timestamps, and the verifier evidence reference; correlation IDs must be opaque and non-secret.
- **owner gets:** When the Mac, browser, or link fails halfway through a task, the owner gets one truthful answer—finished, safely resumable, or needs attention—instead of duplicate emails, double purchases, or an action that silently stopped. It makes the system able to continue long work without asking the owner to remember which step already happened.
- effort: Medium: shared schema and relay state machine, adapters in Mac/browser executors, and a small migration for existing receipts. Then adversarial tests for timeout-after-submit, browser reload, duplicate delivery, and verifier disagreement.  ·  risk: A schema mismatch could strand existing jobs; preserve a legacy adapter and default old receipts to unknown, never complete. A compromised executor could claim completion, so only faculty-perception verification can transition a step to verified. Expire abandoned attempts and provide operator-visible recovery rather than automatic mutation.
- cost: Negligible storage and API overhead (a few hundred bytes per step); one extra read-only verifier call on uncertain steps. No new model call for ordinary successful actions.  ·  latency: No meaningful added latency on successful actions; uncertain recovery adds roughly 1–10 seconds for fresh Mac/browser verification.
- security: Improves replay resistance and auditability. IDs reveal no content; evidence references are sensitivity-labeled and default to hashes. Never place form secrets, page contents, or private file data in receipts.
- depends on: The already-granted verify_operation_step contract; A documented executor receipt schema for POST /execute and browser results; A relay-owned durable operation journal and idempotency index


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities. The strongest is resumable execution: after a dropped link or restart, faculty-action must resume only at a boundary independently re-verified by faculty-perception, never from executor receipts alone. I also recorded a private “what changed since I left?” diff with selective, provenance-checked undo, and owner-controlled replay of the last delivered audio through the future rotary input. The recorder flagged the latter two as close to existing backlog ideas, so they should be treated as narrow amendments rather than broad new primitives.

**Biggest unknown:** I still need the exact receipt schema and operation/attempt correlation used by POST /execute and GET /jobs/:jobId/receipts, plus confirmation of whether any durable checkpoint/baseline store already exists. For replay, I need the planned rotary encoder event format and the relay’s canonical audio-artifact identifier. Without those, I can specify safe behavior but cannot implement a trustworthy continuation or replay path.

