# Harness derivation — faculty-perception — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device inventory** — The live inventory currently exposes Safari on MacIntel online with 2 tabs, home-macbook-bridge online (last seen 2026-08-09T02:04:46.991Z), and cloudflare-contract-test mobile offline (last seen 2026-07-31T23:42:56.525Z). No pendant appears in the discovered device list.
  - evidence: discover(category=devices) returned exactly these three entries.

## Capabilities it proposed

### "Find any owner preference that is machine-inferred, contradicts a live measurement, and is poisoning your decisions; show me the conflict and let me correct it."
- **useful because:** A wrong pinned preference can silently affect every future turn. The known example is America/Chicago injected as a high-confidence machine preference while this Mac resolves to America/New_York. This capability would surface the exact source, live counter-evidence, affected routines, and a reversible correction instead of silently choosing.
- **path:** mac → relay → browser → dashboard → pendant
- **model tier:** Cheap background model for candidate ranking and affected-decision explanation; realtime only reads the concise conflict when the owner asks.
- **latency:** A nightly/background scan in seconds; an on-demand report under 3 seconds, with no device actuation until confirmed.
- **cost:** A few cents per scheduled scan at most; dominated by reading the memory projection and a handful of authoritative device/system values.
- **security:** Never reveal secret-valued facts in a broad report. Require explicit confirmation before editing pinned memory. Keep an audit record of old value, source origin, replacement, and affected routine IDs.
- **missing:** A read-only join between memory facts and authoritative Mac/relay measurements; A dry-run impact report for routines, quiet hours, and prior decisions that consumed the fact; A confirmation-and-rollback mutation that preserves provenance rather than overwriting history

### "Before you send, buy, delete, or submit anything, prove that the page and target still match what you showed me, then tell me exactly what changed if they do not."
- **useful because:** A logged-in browser can change after planning: prices, recipients, account, or form contents may be different when the click happens. This gives the owner a concrete before/after target proof and blocks a stale-plan action instead of treating a browser command receipt as success.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Use a cheap deterministic comparator for normalized target fields and hashes; use the judgement model only to explain a mismatch in plain language. Realtime speaks the final confirmation or refusal.
- **latency:** 150–500 ms for the pre-click comparison when the browser bridge is online; under 2 seconds including a spoken confirmation.
- **cost:** Near-zero model cost for matching; under $0.01 only when a mismatch needs explanation. Browser snapshots and hashes dominate latency, not tokens.
- **security:** Redact secrets and payment credentials before hashing or sending summaries to the relay. Never permit an action after an unresolvable mismatch. Confirmation must include the exact target and irreversible consequence, and every attempt needs an undo/receipt link where possible.
- **missing:** A browser-side normalized target capture with an opaque snapshot ID and content hash; A compare-and-expire gate between browser result and mac action execution; A relay event linking the owner's spoken confirmation to the specific target hash

### "For anything important, corroborate it with two independent surfaces and tell me when they disagree instead of picking the more convenient answer."
- **useful because:** A single source can be stale or structurally misleading: a Mac job can be completed while pendant playback is unknown, a browser can show a login wall, and relay registry absence does not prove pendant absence. Independent corroboration makes high-stakes spoken answers honest and gives the owner a useful reason for uncertainty.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic source-agreement rules first; a small background model classifies whether two observations are genuinely independent and writes the short explanation. Realtime is only for the spoken result.
- **latency:** Under 2 seconds interactively for cached sources; up to 10 seconds for a fresh browser or Mac corroboration query.
- **cost:** Typically under $0.02 per high-stakes check; browser rendering and fresh Mac probes dominate, while agreement itself is cheap.
- **security:** Do not treat duplicated relay/Mac projections as independent evidence. Keep source identity, capture times, and uncertainty visible. For destructive actions, disagreement must block execution and require explicit owner confirmation.
- **missing:** An independence map distinguishing primary observations from derived projections; A claim envelope containing source, capture time, freshness, and confidence for each observation; A policy that selects which claims require quorum and records disagreement without collapsing it

### "Which commitments are about to miss their deadline, and what is the last independently verified step for each?"
- **useful because:** The owner currently sees isolated routine, job, browser, and relay records. A deadline radar would connect them: distinguish planned from started, Mac-complete from owner-heard, and absent evidence from failure, then warn early enough to recover rather than after a deadline passes.
- **path:** mac → browser → relay → pendant → dashboard
- **model tier:** Cheap scheduled/background model over structured timestamps and receipts; realtime only speaks urgent exceptions.
- **latency:** Run every 5–15 minutes in the background; an on-demand answer under 2 seconds from cached state.
- **cost:** A few cents per day or less; structured receipt comparison dominates no model spend, with one small call only for grouping related steps.
- **security:** Do not infer completion from a Mac-side 'completed' status when playback is unknown. Keep deadlines and source records local where possible; require confirmation before sending recovery messages or changing schedules.
- **missing:** A normalized commitment/deadline record joining routine runs, Mac jobs, browser commands, relay announcements, and device events; A dependency graph that declares which evidence is sufficient for each commitment; A durable alert state with snooze, escalation, and explicit owner dismissal

### "Show me exactly what the system knew, from every surface, at the moment it made a decision—not what those surfaces say now."
- **useful because:** When an action is questioned later, the owner needs a faithful historical reconstruction: the browser content, Mac state, relay state, model inputs, and device availability as they existed then. Current logs and receipts cannot reliably answer this because they are fragmented, count-capped, or derived after the fact.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic snapshot assembly and hashes in the background; use a cheaper model only to narrate the reconstructed timeline. Realtime is unnecessary except for the owner’s spoken question.
- **latency:** Capture must add less than 100 ms to an action; reconstruction should return within 3 seconds for a recent action.
- **cost:** Low ongoing model cost; storage and hashing dominate. Keep compact metadata by default and retain sensitive bodies only under the owner’s explicit retention policy.
- **security:** Historical snapshots may contain page text, private messages, or secrets. Encrypt locally, redact before relay upload, support per-snapshot revocation, and require owner confirmation before exposing sensitive fields.
- **missing:** An immutable decision-context envelope created before planning; Cross-surface snapshot IDs and monotonic capture ordering; A retention and redaction policy for historical decision contexts; A replay reader that distinguishes observed state from later-derived status

### "Give me a short-lived, one-time approval token for this exact action, and make it impossible to reuse if the target, page, device, or deadline changes."
- **useful because:** Today a confirmation can be separated from the eventual browser or Mac execution, leaving ambiguity about what the owner actually approved. A one-use consent lease would bind approval to the exact target and context, expire automatically, and prevent queued or retried work from silently inheriting old consent.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic policy and signature checks; no expensive model is needed after the owner’s intent has been interpreted. Realtime is used only to collect the spoken approval and read the concise scope back.
- **latency:** Under 300 ms to mint and validate a lease; lease lifetime configurable from seconds to a few minutes.
- **cost:** Negligible model cost. The main cost is secure local key storage and a small append-only consent ledger.
- **security:** Never put the raw approval phrase or secrets in the relay. Bind the lease to a redacted action digest, target hash, device/session identity, expiry, and nonce; reject replays and fail closed on clock uncertainty. Destructive actions still require explicit confirmation.
- **missing:** A device- or Mac-held signing key with rotation and recovery; A target digest produced before approval and rechecked immediately before execution; A relay/Mac protocol that carries nonce, expiry, and one-time-consumption state; A visible owner-facing consent receipt and cancellation mechanism

### "If the connection drops halfway through, tell me whether the action happened, verify the real-world state, and resume only the unfinished part without duplicating anything."
- **useful because:** A lost link currently leaves the owner choosing between repeating an action and hoping it completed. This capability would reconcile Mac receipts, browser state, relay state, and (when present) device telemetry, then produce a resumable handoff with explicit duplicate-risk boundaries.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic state reconciliation first; use a cheap judgement model only when evidence is genuinely ambiguous. Realtime is only for the owner-facing decision or confirmation.
- **latency:** Detect interruption within 5 seconds; reconcile within 3 seconds after a surface returns; never auto-resume irreversible actions.
- **cost:** Low model cost; most work is bounded reads and state comparisons. Storage is a small resumable checkpoint per action.
- **security:** Fail closed when state cannot be verified. Bind checkpoints to target hashes and session identity, encrypt sensitive state, and require confirmation before any non-idempotent retry. Provide an explicit duplicate-risk explanation and undo path.
- **missing:** A cross-surface idempotency key understood by relay, Mac, and browser adapters; Checkpoint records containing completed side effects and verified post-state; A recovery coordinator that can distinguish unknown from not-started; A user-visible resume/abort decision with expiry


## What it asked for

_Nothing._
