# Harness derivation — faculty-action — round 22

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant button offline to bookmark a moment, bring it back later, figure out what it relates to, and leave me a ready-to-review follow-up on my Mac."
- **useful because:** The pendant already records offline moments, and the relay already surfaces held alerts, but today a bookmark is only an isolated event. This would turn a fleeting thought captured without connectivity into a grounded, actionable thread without requiring the owner to remember it later. It is inherently multi-node: pendant capture, relay durability, Mac/private-app context, browser session evidence when available, and faculty judgement/action for a safe follow-up.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic pendant/relay code for capture, deduplication, ordering, and delivery. Use a cheap background text model on the Mac for clustering/transcription summarization; use faculty-perception for evidence gathering and faculty-judgement for intent classification. Reserve realtime only for the eventual short spoken receipt or a focused clarification.
- **latency:** Capture must be immediate and offline. On reconnect, durable delivery and an initial receipt should complete within 2 seconds; enrichment may run in the background for up to 2 minutes. If private browser evidence is unavailable, leave the item pending rather than guessing or acting.
- **cost:** About $0.01–$0.05 per reconciled bookmark, dominated by background model/context extraction; near-zero relay/storage cost. Realtime cost is avoided unless the owner asks a follow-up question.
- **security:** Bookmark audio/transcript and matched private context may contain sensitive data. Encrypt the pendant spool and relay payload, minimize context to candidate snippets, retain provenance and expiry, and keep browser content on the Mac. Never send email, submit a form, or alter a calendar item automatically; create a reviewable draft/reminder with before/after evidence. Require explicit confirmation for any irreversible action.
- **missing:** A durable bookmark envelope with monotonic device sequence, capture timestamp, link state, audio/transcript hash, and idempotency key across pendant→relay→Mac; A reconnect reconciler that acknowledges each envelope exactly once and reports late/duplicate/out-of-order delivery back to the pendant; A Mac enrichment worker that searches permitted local apps and authenticated browser tabs, records evidence versions/provenance, and expires stale matches; A decision-window/action-manifest bridge so judgement can request one clarification and action can create a review item or reversible reminder; A dashboard queue showing bookmark, transcript, matched evidence, confidence, expiry, and approve/edit/dismiss controls; current browser is offline and Mac readiness is false

### "Remember this for the next place I arrive: when my pendant detects that I have reached a chosen place, give me the relevant note or open the exact Mac/browser workbench I need there—without me having to remember to ask."
- **useful because:** A wearable can capture intent at the moment it occurs, while the Mac and browser can prepare the private, concrete material needed later. The owner gets a just-in-time handoff instead of a generic reminder that arrives too early or too late. This requires the pendant's physical continuity, an always-awake relay, the Mac's local files/apps, and authenticated browser sessions together; no single node can provide it safely.
- **path:** pendant → relay → iOS → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic geofence/proximity events, encrypted queueing, and scheduled delivery for the control plane. Use a background economical model to turn the captured note into a compact context card and choose the relevant workbench. Use faculty-perception to verify current place/session evidence and faculty-judgement to resolve ambiguity. Use realtime only for the short spoken handoff when the pendant is worn.
- **latency:** Capture is immediate and offline. Place arrival should trigger a local acknowledgement in under 1 second; the prepared card/workbench should be ready within 10 seconds online. If location confidence or browser freshness is inadequate, defer and ask one concise question rather than guessing.
- **cost:** Roughly $0.01–$0.04 per handoff, mostly background context matching; deterministic relay and local Mac work are negligible. Realtime speech is only a few cents when used.
- **security:** Location and private account data are highly sensitive. Keep raw location on the paired iOS/pendant path, send only a place pseudonym and intent ID to the relay, and keep authenticated page contents on the Mac. Require per-place opt-in, visible active-place state, expiration, revocation, and an audit trail. Opening a prepared workbench is reversible; sending, purchasing, deleting, or submitting anything still requires explicit confirmation.
- **missing:** A product pendant with BLE/UWB or another reliable proximity/location signal and encrypted offline intent records; the current prototype has one button/LED and no location sensor; A paired iOS companion that resolves places locally, manages consent, and forwards signed arrival/absence events; Relay support for delayed, ordered intent envelopes keyed to place policies and expiry, including deduplication across reconnects; Mac/browser workbench generation that can stage private evidence without mutating accounts and can revalidate sessions at arrival time; A dashboard policy editor and audit view for place triggers, quiet hours, retention, and revoke/delete controls


## Changes it proposed to its own stack

### `integration` — Add a cross-surface operation-state reconciler that derives terminal job status from append-only pipeline events and relay acknowledgements, rather than trusting the current `processing` field. It should validate event ordering, mark runs completed/failed/expired, detect orphaned uploads and stale pending browser commands, and emit one signed owner-facing receipt with the evidence IDs. A reconnecting pendant must receive only the receipt delta it has not acknowledged, keyed by pipelineId plus event sequence.
- **owner gets:** The live pipeline currently contains runs that have `done` events but remain `processing`; the owner cannot reliably tell whether an offline alert, spoken response, or Mac action actually finished. This prevents safe follow-up and can cause duplicate work. Correct terminal receipts make 'what happened?' trustworthy across dropped links.
- effort: Medium: define event-schema/state reducer, migration for existing pipeline records, relay/Mac reconciliation endpoint, pendant ACK cursor, and dashboard diagnostics; add crash/reconnect and duplicate-delivery tests.  ·  risk: A reducer could prematurely close a job when events arrive late. Use a bounded settling window, explicit `expired/unknown` instead of success, and retain the raw event log for replay. On migration, preserve all records and label old runs `legacy-uncertain` rather than rewriting history.
- cost: Small background compute and D1/local JSON writes; roughly <$0.001 per operation. No new model call required.  ·  latency: Receipts become available within one event cycle (target <500 ms online); a 5–10 second settling window applies only when the link is unstable.
- security: Receipts should contain metadata and provenance IDs, not raw private page/audio contents. Sign relay acknowledgements and scope each receipt to the paired pendant/Mac identity.
- depends on: A shared typed event envelope with sequence numbers and idempotency keys; Relay persistence and pendant acknowledgement cursor; Action/browser runners emitting explicit per-step terminal evidence


## What it asked for

_Nothing._
## Its own summary

Round 22 produced two new, non-duplicate action-layer proposals. (1) An offline pendant bookmark should become a durable, deduplicated cross-node follow-up: relay stores it, Mac/private browser evidence enriches it, judgement opens a decision window, and action leaves a cited review item rather than silently sending anything. (2) A pipeline operation-state reconciler should derive terminal status from event history; live evidence currently shows runs with done events still labeled processing, making completion receipts unreliable and risking duplicate work.

**Biggest unknown:** Whether the existing relay/pipeline schemas already expose a monotonic event sequence and pendant acknowledgement cursor; without those, exactly-once bookmark reconciliation and trustworthy terminal receipts cannot be implemented. Immediate operational blockers remain browser extension offline (2 pending commands), Mac Accessibility and Screen Recording unavailable (agent ready=false), and no verified per-step terminal/idempotency evidence from runners.

