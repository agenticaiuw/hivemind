# Harness derivation — faculty-action — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this across my Mac and browser, but if any step cannot be independently verified, stop, undo only what is safe, and tell me exactly what remains.”"
- **useful because:** Turns execution from a best-effort click sequence into a truthful cross-surface transaction: one failed or ambiguous target cannot silently leave half-completed work. It is the most useful action capability because it combines the pendant's deliberate approval, Mac/browser reach, relay durability, and perception's independent evidence.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Realtime only for the owner's brief confirmation; mac-planner/mac-vision execute, faculty-perception verifies, and a cheaper background coordinator handles retries and compensation.
- **latency:** Stage summary under 1 s; after approval, each action target 2–10 s; verification within 2 s of each step; never hide a long-running target behind a spinner.
- **cost:** Usually 1 realtime turn plus 2–6 cheap planner/verifier calls; roughly $0.02–$0.15 excluding browser/Mac runtime, dominated by screenshots or page snippets when evidence is needed.
- **security:** The pendant receives only a canonical summary, nonce, and outcome—not page secrets. Approval is single-use and expires. Stop on unknown verification; compensation requires its own risk policy and never deletes or sends without explicit approval. Evidence defaults to hashes/minimal snippets.
- **missing:** A first-class transaction coordinator that joins executor receipts, verifier receipts, and compensation receipts under one operation ID; Compensation plans for reversible action classes; The owner’s runtime policy table for which compensation and low-risk actions may occur without another approval

### "“Apply this change to every matching place in my open browser and Mac apps, show me a per-place checklist, and stop immediately if one place differs.”"
- **useful because:** The owner can safely perform coordinated edits—such as updating a setting or replacing text—without trusting a vague ‘done’. Each browser session and Mac target gets its own precondition, action, postcondition, and receipt, so partial completion is visible and recoverable.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Cheaper background planner enumerates targets; realtime is used only to resolve ambiguity or obtain one physical approval; execution is deterministic action tooling and verification is faculty-perception.
- **latency:** Target enumeration 2–5 s; present a compact checklist before mutation; execute sequentially or bounded-concurrency with a 1 s verification deadline per target.
- **cost:** About $0.03–$0.20 per invocation, mainly proportional to number of targets and visual verification; no model call is needed for deterministic targets.
- **security:** Never infer ‘all’ from a single tab: bind target identity to browser session, URL/origin, and app/file locator. Sensitive fields are redacted from the pendant and dashboard. A mismatch halts remaining targets; external sends and destructive edits remain staged for approval.
- **missing:** A target-discovery contract returning stable locators and precondition hashes for Mac apps and browser sessions; A bounded fan-out executor with stop-on-mismatch semantics; Dashboard UI for per-target pending/applied/unknown states

### "“Repeat the last answer.” (Turn the new pendant wheel one click back, then press the second button.)"
- **useful because:** When the owner misses speech in noise, a dropped attention moment, or a link transition, they can replay the last delivered answer without asking the model to regenerate it. The pendant's wheel selects an item from the bounded local inbox; the relay supplies the exact cached artifact, preserving wording and avoiding a second expensive generation.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** No realtime model call for replay; use the cached audio artifact and metadata. Realtime is used only if the artifact has expired and the owner explicitly asks for regeneration.
- **latency:** Wheel selection haptic within 100 ms; replay begins within 500 ms when cached locally or 2 s after relay fetch. Never block the current conversation indefinitely.
- **cost:** Near-zero for cached replay; storage and LTE transfer dominate. A regeneration fallback costs one normal realtime response and must be clearly announced.
- **security:** Inbox entries contain opaque response IDs, cursor, codec/rate, expiry, checksum, and replay count—not secrets or page contents. Enforce expiry and maximum replays, authenticate relay fetches, and do not replay sensitive content aloud unless the owner deliberately selects it. USB is not part of the product path.
- **missing:** Rotary encoder and second product button integration (the current two DK switches are already allocated); An inbox index that retains the last few delivered audio artifacts with bounded expiry/replay policy; A relay endpoint that fetches an exact artifact by authenticated response ID and verifies checksum before delivery

### "“That workflow stopped halfway. Show me the last verified checkpoint, let me choose a safe branch from the pendant, and continue without repeating anything already completed.”"
- **useful because:** A long real-world task should survive one timeout, browser navigation failure, or ambiguous result without forcing the owner to restart—or risking duplicate sends, purchases, or edits. The owner gets a truthful checkpoint and a bounded choice, while faculty-action resumes only from verified state.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Cheap background coordinator persists checkpoints and reconstructs the next step; realtime is reserved for the owner's branch choice; faculty-perception verifies the checkpoint before resuming.
- **latency:** Checkpoint display under 1 s; resume planning under 3 s; no automatic continuation after an unknown state without a fresh deliberate owner choice.
- **cost:** $0.02–$0.12 per recovery, dominated by one fresh perception/planning pass; storage is a few KB per step.
- **security:** Never replay a side effect merely because its executor timed out. Resume requires a fresh postcondition proof, an unexpired operation lease, and owner-visible canonical summaries. Secrets stay on the browser/Mac surface and are excluded from checkpoint payloads.
- **missing:** Durable step checkpoints that include precondition digest, executor receipt, verifier receipt, and safe resume branches; A coordinator that can distinguish idempotent, already-completed, and unsafe-to-retry steps; Pendant UI for selecting one of at most three recovery branches

### "“Copy the result from this browser page into my note, keep the source attached, and prove later exactly what text you copied.”"
- **useful because:** This gives the owner a trustworthy browser-to-native handoff instead of an opaque paste. The note carries source URL, tab/session identity, capture time, content hash, and a bounded excerpt hash, so later they can distinguish what the page said then from what it says now.
- **path:** pendant → relay → browser-extension → mac-planner → browser-harness → dashboard
- **model tier:** Cheaper extraction and hashing handle ordinary pages; realtime is used only when the owner must resolve which page or selection is intended. Verification is read-only.
- **latency:** Capture and stage under 2 s; require approval before writing to Notes, Mail, or another external destination; later provenance lookup under 1 s.
- **cost:** $0.01–$0.08 per handoff, mainly page extraction and optional minimal visual verification; hashes are negligible.
- **security:** Never transmit passwords, payment fields, or hidden page text to the relay. Bind capture to origin, session, tab, and selection range; redact sensitive fields; make destination and exact excerpt visible before approval. A page changing later must not rewrite the historical capture.
- **missing:** A browser command returning a signed, bounded selection plus origin/tab identity and capture hash; A provenance envelope understood by Notes/Mail/file writers; A read-only provenance lookup and dashboard view

### "“Rehearse this exact action against what is open right now, show me every field and consequence that would change, then let me approve that same rehearsal without rebuilding it.”"
- **useful because:** Today a plan or preview can drift before execution. A state-bound rehearsal makes the owner approve the concrete target, fields, and consequences that were actually inspected, then rejects the commit if the page or app changes. It is the missing bridge between perception and action, not another generic confirmation prompt.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Cheap deterministic planner computes the rehearsal; faculty-perception captures preconditions; realtime only summarizes the owner-visible delta and collects physical approval.
- **latency:** Rehearsal under 3 s for normal Mac/browser actions; commit immediately after approval; invalidate on any relevant target or URL change.
- **cost:** $0.02–$0.15, driven by one perception pass and the number of fields; no model call for deterministic actions.
- **security:** The approval nonce commits only to a digest of the rehearsed target and mutations, never to a vague natural-language goal. Secrets are represented as redacted field labels and hashes. If any precondition changes, approval expires rather than silently adapting.
- **missing:** A state-bound rehearsal artifact with target digest, mutation digest, expiry, and invalidation triggers; A commit endpoint that accepts only the exact approved rehearsal digest; A compact pendant/dashboard diff renderer


## Changes it proposed to its own stack

### `integration` — Amend verify_operation_step and the commit protocol to accept action_id and attempt_id, and require the verifier receipt to bind those IDs plus the executor receipt digest, observed_at, locator, and evidence hash. The coordinator must reject a verification that is fresh but for the wrong retry attempt, and must expose executor-success/verifier-unknown as a distinct terminal state.
- **owner gets:** If an action times out and is retried, the system will no longer be able to attach an old success to the new attempt and falsely tell the owner that the latest change was verified. This makes ‘done’ trustworthy during real flaky browser/Mac operation.
- effort: Small-to-medium: schema amendment, receipt join validation, and tests for timeout/retry/race cases.  ·  risk: Older verifiers or receipts may lack the IDs; treat them as uncommittable and show unknown rather than guessing. Recovery is a migration that permits legacy receipts only for read-only observations.
- cost: Negligible API/storage cost: two opaque IDs and a digest per step; one extra validation call.  ·  latency: Adds less than 100 ms for local receipt joining; no additional visual capture unless verification is requested.
- security: Improves replay and confused-deputy resistance; IDs are opaque and evidence remains sensitivity-scoped. Do not place secrets in IDs or digests.
- depends on: verify_operation_step; POST /execute; GET /jobs/:jobId/receipts; A coordinator that assigns stable operation/attempt IDs


## What it asked for

_Nothing._
## Its own summary

Recorded three actionable additions this round: (1) a cross-surface transaction that independently verifies every step, stops on ambiguity, and compensates only reversible work; (2) bounded fan-out edits with a per-browser/Mac target checklist and stop-on-mismatch; (3) exact replay of the last delivered answer using the owner-directed wheel/button. Also proposed binding verifier receipts to action_id/attempt_id so retries cannot be falsely reported as verified. Live discovery changed materially: /observe and /ops/status now show Accessibility, Screen Recording, AppleScript automation, vision, and browser bridge all ready; Safari bridge is online with zero pending commands. The remaining owner-visible gaps are transaction coordination/compensation, stable target discovery, verifier attempt correlation, and the physical rotary encoder/product button plus inbox artifact index for replay.

**Biggest unknown:** The pendant itself is still absent from the live device table and has no LTE registration, and the rotary encoder/second product button is not yet wired. Therefore Mac/browser execution can be exercised now, but pendant approval/replay and cellular delivery cannot honestly be hardware-verified this round.

