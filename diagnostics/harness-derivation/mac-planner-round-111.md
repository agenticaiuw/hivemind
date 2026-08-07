# Harness derivation — mac-planner — round 111

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Capture this as a decision packet, work it out while I’m away, and leave me something I can resume.”"
- **useful because:** The pendant is the only surface present when the owner thinks of a goal, the Mac can read local Calendar/Mail and leave files, Safari holds private sessions, and the relay can coordinate after the owner walks away. This produces a durable, sourced decision with drafts and explicit next step—not merely a spoken answer or an unattended watcher.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to capture/confirm the goal and announce completion; use a cheaper background planner for evidence collection, reconciliation, and drafting. Use a small local model for extraction/normalization where possible.
- **latency:** Acknowledge the pendant request in under 2 seconds; initial packet in 30–90 seconds; long browser/Mac work continues asynchronously. On resume, speak one sentence plus a pointer to the full bundle.
- **cost:** Roughly one realtime turn for capture and one short completion turn; background cost dominated by authenticated-page extraction and synthesis (typically 2–6 slower-model calls), with no model cost while waiting.
- **security:** Private Calendar/Mail and logged-in tabs leave the Mac only as extracted, cited snippets; retain source URL/tab, timestamp, and evidence hash, not whole pages. Default all email/form changes to drafts. Require the owner’s existing confirmation before sending, deleting, purchasing, or other destructive actions. Packet must expire and support deletion.
- **missing:** A durable cross-surface packet/job object with checkpointed state, evidence citations, and a resume token that survives relay/Mac restart; A worker/result stream joining mac job receipts and browser command results into that packet; A pendant-resume command and short audio notification tied to packet completion; A Mac workbench writer that atomically creates a folder containing brief, evidence, drafts, and next actions

### "“For the next ten minutes, let the Mac use only the shipping total and delivery date from this logged-in page; do not share anything else.”"
- **useful because:** Today, private browser access is effectively session/page scoped, while Mac automation and the relay have no owner-visible, field-level boundary. This would let the owner safely combine a logged-in browser fact with a local action without exposing the whole page, account, or unrelated tabs. The pendant is the natural place to grant and revoke the temporary scope.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime handles the spoken grant and revocation only. A cheaper background model may map the requested fields to page evidence and validate the result; deterministic policy code enforces the field allowlist and expiry.
- **latency:** Speak back the granted scope in under 2 seconds; extraction and delivery within 5 seconds; revocation takes effect on the next relay request and must be acknowledged immediately.
- **cost:** One short realtime turn plus a small extraction/validation call when semantic field mapping is needed; policy checks and token revocation are negligible.
- **security:** Issue an unguessable, single-purpose capability token bound to tab/session, field paths or an approved semantic extraction, recipient surface, operation, and expiry. Return only redacted values with provenance; never forward DOM, cookies, screenshots, or page text outside the allowlist. Revoke on pendant gesture, timeout, tab navigation, logout, or source change. Any send/delete/purchase still requires the owner’s existing confirmation.
- **missing:** A field-level browser extraction contract that can return typed values rather than whole-page text; Relay-enforced capability tokens with expiry, audience, revocation, and audit receipts; Mac actions that accept only the scoped typed values and cannot silently reacquire the browser page; A pendant UI/gesture for reviewing and revoking active data grants


## Changes it proposed to its own stack

### `integration` — Add a resumable decision-packet coordinator above the existing Mac jobs and browser sessions. It should create packetId/resume token, persist a state machine (captured → collecting → synthesized → review-ready), append immutable evidence references and action receipts, checkpoint after every surface, and expose GET status plus a compact completion event. On restart it resumes only unfinished steps; on privacy expiry it tombstones source material while retaining a redacted receipt.
- **owner gets:** If the owner leaves Wi‑Fi, closes the lid, or is interrupted, they can return to the same answer instead of repeating the request or guessing what changed. Every recommendation has a source and the exact draft/action state is visible on the Mac.
- effort: Medium-high: coordinator, durable store, adapters for browser and Mac job receipts, resume protocol, and a small workspace renderer.  ·  risk: A stale packet could act on changed information. Every packet needs freshness timestamps, invalidation on source/session loss, and a visible 're-check required' state. Recovery is replay from the last checkpoint; no mutation is auto-replayed.
- cost: Negligible storage; background synthesis costs a few slower-model calls per packet. Reconciliation after restart may repeat only the failed step.  ·  latency: Immediate acknowledgement stays realtime; first useful packet usually 30–90 seconds, with no blocking of the pendant conversation.
- security: Sensitive extracts remain local or encrypted; relay stores hashes and minimum snippets. Resume tokens must be unguessable and revocable; destructive actions remain drafts until owner confirmation.
- depends on: Durable browser job runner (chg-16bc5dee is still missing persistence/retry/result stream); A packet-aware relay event/result route; Atomic Mac workspace bundle writer; Existing Mac job receipts and browser session affinity


## What it asked for

_Nothing._
## Its own summary

Discovered the owner’s current state and backlog, avoiding repeated watch/meeting-brief proposals. I proposed a new cross-surface capability: an interruptible, resumable decision packet started from the pendant, coordinated by relay, grounded in private Mac/browser evidence, synthesized in the background, and left as a cited Mac review bundle with drafts—not sent actions. I also proposed the integration state machine and checkpointed evidence/receipt design, and informed faculty-judgement and relay-realtime.

**Biggest unknown:** The key implementation gap is still durability: the browser router/session layer exists, but the durable browser job runner with retry, persistence, and planner-visible result stream is explicitly unfinished. The packet coordinator, pendant resume event, and atomic Mac workbench writer also do not yet exist. I did not re-request denied permissions or already-pending tools.

