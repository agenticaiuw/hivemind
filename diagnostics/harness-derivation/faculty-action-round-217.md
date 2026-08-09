# Harness derivation — faculty-action — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do this for me, but don't tell me it's done until the Mac/browser state proves every step succeeded—and if anything is uncertain, stop and tell me exactly where.""
- **useful because:** This would be the system's single most useful action primitive: it turns a spoken goal into a staged, physically approved operation with independent postcondition checks, rather than confusing an executor receipt with truth. It can safely span the relay, pendant, Mac apps, and a browser session.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime only for clarifying the goal and presenting the approval summary; use the cheaper local planner for decomposition and execution, and deterministic verification wherever possible.
- **latency:** Under 2 seconds to present a concise approval summary; execute steps as fast as the target app allows; verification adds roughly 0.5–2 seconds per step. Never claim completion while a verifier is pending.
- **cost:** Usually one realtime turn plus local planner calls; roughly $0.01–$0.05 per operation depending on ambiguity. Browser screenshots and long reasoning dominate cost, so prefer structured state and hashes.
- **security:** The pendant receives only an opaque transaction summary/hash, nonce, expiry, and outcome—not page contents, passwords, or message bodies. Require the existing physical transaction approval latch for risky actions. A failed or stale verifier yields UNKNOWN, never success; preserve receipts and offer undo where available.
- **missing:** A coordinator that binds each plan step to an action receipt and a verify_operation_step call, with explicit COMMITTED/UNKNOWN/ROLLED_BACK states; A compact owner-facing approval summary for multi-step plans; Per-step compensation policy for partial execution

### ""Start this task now and finish it even if the Mac sleeps or the link drops; when I come back, tell me which steps really happened and resume only the missing ones.""
- **useful because:** Long-running computer tasks currently risk becoming an ambiguous half-finished job. A checkpointed operation lets the owner delegate genuinely useful work—research, file organization, browser workflows, or a multi-app setup—without re-running an already completed irreversible step after a disconnect.
- **path:** relay-realtime → faculty-action → faculty-perception → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** Use a cheap background/local planner for decomposition and checkpoint handling; use realtime only for the initial confirmation and exception conversation. Verification should be deterministic or local, with the expensive model invoked only for ambiguous recovery.
- **latency:** Immediate acknowledgement and haptic pending state; checkpoint writes under 200 ms per step. Resume on reconnect within 10 seconds, but pause rather than guess when state diverges.
- **cost:** Low ongoing inference cost: one planning call plus event-driven recovery, approximately $0.005–$0.03 per task. Storage and browser inspection, not tokens, dominate long jobs.
- **security:** Each step gets an idempotency key, precondition snapshot, receipt, and verified postcondition. On reconnect, compare fresh state before retrying. Expired approval leases and changed browser sessions force a new physical approval. Do not persist secrets in the relay journal; retain only hashes/minimal snippets.
- **missing:** Durable per-step checkpoints and idempotency keys in the job journal; A resume coordinator that compares fresh state before retry; A clear owner-visible distinction between completed, skipped, retried, and unknown steps

### ""That worked—remember the exact safe sequence and do it every weekday at 8, but ask me again if the website, recipient, or amount changes.""
- **useful because:** The owner can turn a successful, verified action into a guarded routine without manually rebuilding it. The system captures the proven sequence, then re-plans only when live state differs, making recurring browser/Mac work useful without silently reusing stale targets.
- **path:** relay-realtime → faculty-action → faculty-judgement → faculty-perception → mac-planner → browser-extension → relay-realtime
- **model tier:** Use a cheap background/scheduled model to instantiate the routine and compare live state; use realtime only to explain the captured recipe and request approval when a material field changes.
- **latency:** Routine firing should be quiet and under 10 seconds when all preconditions match. If a target, amount, recipient, or browser session differs, pause immediately and ask rather than improvising.
- **cost:** Low: deterministic routine execution costs cents or less per run; model calls occur only on changed state or ambiguity. Browser inspection is the main variable cost.
- **security:** Never template secrets or page contents; store selectors, field roles, and hashes where possible. Require physical approval for each high-risk run or when any protected field changes. A changed recipient/amount/site origin is a hard stop, not a fuzzy match.
- **missing:** A verified-operation-to-routine compiler that stores typed preconditions and permitted mutations rather than a screen recording; Routine-run diffing that identifies exactly which material fields changed; A per-routine approval policy and safe disable/expiry mechanism

### ""Prepare all of this across my Mac and browser, but make no external change until I approve one atomic commit—and if the commit cannot be completed everywhere, leave every surface in its original state.""
- **useful because:** The owner cannot safely coordinate a multi-surface change today: a calendar edit may succeed while a browser form or draft fails. This provides true transaction semantics across surfaces, not merely a plan, an approval gesture, or a later verification report.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → mac-vision
- **model tier:** Use a background/local planner to construct staged changes; use realtime only to explain the final diff and collect approval. Deterministic commit and compensation should not spend the expensive model tier.
- **latency:** Preview within 5 seconds; one physical approval; commit each surface with a bounded timeout. If atomicity cannot be guaranteed, refuse to claim atomic execution and retain staged drafts only.
- **cost:** Approximately $0.01–$0.05 for planning and diff explanation; browser inspection and generated previews dominate cost.
- **security:** External side effects remain staged until approval. The pendant receives only a transaction summary/hash. Each participant must expose prepare/commit/abort; irreversible actions such as sending a message cannot be rolled back and must be isolated as the final explicitly labeled step.
- **missing:** A cross-surface prepare/commit/abort protocol; Staging adapters for Mac apps and browser forms; A transaction coordinator with compensation and an explicit non-atomic refusal path

### ""Show me exactly what would change before you do it: files, calendar entries, browser fields, and messages—then let me approve that concrete diff from the pendant.""
- **useful because:** Today an owner can approve a high-level intent without seeing a complete, structured account of every mutation. A cross-surface diff gives them a meaningful decision surface before execution, especially for bulk edits or browser workflows where a prose summary can omit hidden changes.
- **path:** relay-realtime → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic adapters to generate file/calendar/form/message diffs; use a cheaper model to summarize only when fields are ambiguous. Realtime presents the short spoken summary, while the pendant displays a hash and haptic choice rather than sensitive content.
- **latency:** Generate a preview in under 5 seconds for ordinary tasks; approval remains pending until all intended mutations have a preview. Any preview invalidated by state change must be regenerated.
- **cost:** Low to moderate, roughly $0.005–$0.03 per preview; screenshot/OCR fallback is the dominant cost and should be avoided when structured state is available.
- **security:** Redact secrets and private bodies from the pendant and relay. Bind approval to a canonical diff hash, target identities, and expiry. If the actual mutation differs from the approved diff, abort rather than silently widening scope.
- **missing:** Canonical diff schemas for each mutation class; Preview adapters for browser and Mac surfaces; Approval binding to a complete diff hash, not just an intent summary


## Changes it proposed to its own stack

### `integration` — Add a compensating-action saga to faculty-action: after each mutating step, persist its receipt, verifier provenance, and a typed compensation (undo endpoint, reverse browser command, or owner-confirmed manual recovery). If a later step fails, automatically compensate only steps whose postconditions and reversibility are known; otherwise freeze the operation as UNKNOWN, send the owner a concise haptic/status outcome, and expose the exact recovery point. Bind compensation to the same transaction nonce and refuse replay after expiry.
- **owner gets:** A multi-step request will no longer leave the owner wondering whether half of it happened or silently undo something that cannot safely be undone. For example, a failed calendar-plus-message workflow can reverse the calendar change when verified, while stopping before touching a sent message.
- effort: Medium-high: typed compensation metadata in the planner/action ledger, saga state transitions, verifier integration, and recovery UI/voice wording.  ·  risk: An incorrect compensation could be worse than the original action. Default unknown/non-reversible, require explicit owner approval for compensation that can affect external communication or deletion, and make every transition auditable and idempotent.
- cost: Small storage increase per step (receipt, hashes, compensation type); negligible inference cost except when recovery needs ambiguity resolution.  ·  latency: Adds one verification and possibly a compensation call after failures; successful single-step actions are unchanged.
- security: Reduces damage from partial execution, but compensation itself is a privileged mutation. Keep secrets off the pendant, reuse the existing physical approval latch for high-risk recovery, and expire transaction nonces.
- depends on: verify_operation_step being callable for each step; An action-ledger schema that records reversibility and compensation; Existing POST /jobs/:jobId/undo and browser command receipts

### `browser-harness` — Introduce scoped, expiring capability tokens for browser actions. Before execution, faculty-judgement issues a token bound to the operation ID, origin, tab/session, allowed action types, field locators, and canonical payload hash. The browser extension rejects navigation, origin changes, new fields, or payload mutations outside that token and returns a machine-readable refusal. Rotate the token after every approval or browser session change.
- **owner gets:** A malicious page redirect, stale tab, or planner mistake cannot quietly turn "fill this form" into "submit a different form". The owner gets a hard stop and a precise explanation instead of discovering an unintended browser action afterward.
- effort: High: token issuance and validation in relay/browser bridge, origin and session binding, structured locator matching, and refusal receipts.  ·  risk: Overly narrow locators could block legitimate workflows; overly broad locators recreate the danger. Start in observe/deny mode, record near misses, then enable enforcement per action class. Never fall back to unscoped execution.
- cost: Small token and validation overhead; occasional extra browser inspection. No meaningful model cost.  ·  latency: Adds tens of milliseconds per browser command plus occasional re-inspection after navigation.
- security: Strongly reduces confused-deputy, stale-session, and prompt-injection risks. Tokens contain no secrets; payload hashes may still reveal metadata and should be scoped and expired.
- depends on: Structured browser command/result envelopes; Stable browser session and origin identity; Owner-configurable action-risk policy; A browser-side refusal receipt consumed by faculty-action


## What it asked for

_Nothing._
