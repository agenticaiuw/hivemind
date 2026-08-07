# Harness derivation — faculty-judgement — round 80

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner-brief reliability** — The owner has repeatedly requested Gmail/GitHub/Calendar reads and received failures; the current scheduled daily brief reports completed but there is no established shared source-health contract proving whether each source was actually reached.
  - evidence: discover:owner shows repeated failed read gmail/read github/read calendar requests; scheduled daily brief exists; proposed source_health_snapshot request identifies missing typed reachability/freshness evidence.

## Capabilities it proposed

### "“Give me my morning brief, but never pretend an account was checked if it wasn’t; use whichever connection works and tell me exactly what is still unknown.”"
- **useful because:** The owner has repeatedly asked to read Gmail, GitHub, and Calendar and received failures. Today a failed connector can silently become an apparently empty brief. This capability makes absence of evidence visible: it tries the logged-in browser and Mac paths, labels every item with source and freshness, retries later when a surface is offline, and speaks one short actionable brief rather than false reassurance.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to extract and normalize each source and compare with the prior snapshot; use realtime only to answer the owner or resolve an ambiguity. Deterministic reachability/freshness checks should run before any model call.
- **latency:** Initial spoken response under 4 seconds with partial results; background retries and reconciliation may take up to 10 minutes. Never block the brief on a dead provider.
- **cost:** Roughly $0.01–$0.05 per daily run depending on source volume; most cost is normalization and change summarization, not transport. Realtime follow-up is only incurred when the owner asks about an item.
- **security:** Reads private mail/calendar/GitHub only through existing authenticated Mac/browser sessions. Store normalized hashes and source timestamps rather than message bodies; redact secrets and never send or submit anything. Tell the owner which provider was unreachable and require confirmation before any follow-up action.
- **missing:** A shared source-health contract (reachable, authenticated, stale, empty, or unknown) across browser and Mac adapters; A durable per-source baseline/freshness store and retry schedule in the relay; A spoken brief renderer that must include an explicit unknowns section; Stable provenance links/locators for private browser and AppleScript reads

### "“When I correct how you handle something, turn that correction into a rule I can review, test on recent examples, and apply everywhere.”"
- **useful because:** Today the owner must repeat the same preferences to each surface: how short a brief should be, which notifications matter, what counts as urgent, and which actions require confirmation. A correction made during a voice interaction should become a visible, reversible personal policy—not an opaque model habit—then govern the relay, Mac, browser, and scheduled routines consistently.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Use the realtime model only to identify a candidate rule from the owner's correction. Use a cheaper background model to normalize it, find conflicts, and replay it against sampled historical decisions. Deterministic policy evaluation should enforce the approved rule.
- **latency:** Acknowledge the candidate rule in under 3 seconds; do not activate it until the owner approves. Rule simulation may run in the background for under 2 minutes. Enforcement must add under 100 ms to an action decision.
- **cost:** About $0.01–$0.08 per proposed rule, dominated by replaying historical examples; negligible cost for deterministic enforcement. Keep only compact rules and hashes, not full private source content.
- **security:** A mistaken inferred preference could suppress an important alert or permit an unsafe action. Every inferred rule must show examples, scope, expiry, confidence, conflicts, and an explicit approve/reject control; destructive-action confirmation policy can never be weakened by learned rules. Sensitive source data stays on its originating Mac/browser surface where possible.
- **missing:** A versioned personal-policy registry with scope, priority, expiry, provenance, and rollback; A correction-to-rule compiler that produces a human-readable candidate rather than silently learning; A deterministic evaluator shared by relay, Mac, browser, and scheduled routines; A replay/simulation service that shows the owner how the candidate would have changed prior outcomes; A pendant-friendly rule review flow with approve, reject, pause, and undo states

### "“Look at the commitments I am about to make and warn me when they exceed the time or energy I have, then draft a kind way to decline or renegotiate—without sending anything.”"
- **useful because:** A calendar can be technically free while a person is overloaded by travel, preparation, recovery, or unresolved work. The owner should get help before saying yes, not a retrospective list of missed commitments. The system would combine private calendar and mail context with the owner's stated energy constraints, identify the actual tradeoff, and prepare a reversible boundary-setting response for review.
- **path:** relay-realtime → faculty-perception → faculty-judgement → browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-action
- **model tier:** Use a background model for weekly load estimation and candidate tradeoffs; use realtime only when the owner is deciding in conversation. Deterministic calendar duration, overlap, travel buffers, and response deadlines should be computed without an expensive model.
- **latency:** For a spoken “should I take this?” answer, return a first estimate in 5 seconds and refine asynchronously. A weekly scan can complete overnight; never interrupt solely on a low-confidence inference.
- **cost:** Approximately $0.02–$0.10 per weekly scan, primarily from summarizing relevant private threads and estimating preparation burden. Per-decision realtime usage is occasional.
- **security:** This infers sensitive health, work, and relationship patterns. Keep raw mail and calendar on the Mac/browser; send the relay only derived load factors and the minimum snippets needed for a draft. Never contact someone or accept/decline an invitation without explicit confirmation. Let the owner inspect and delete every inferred constraint.
- **missing:** A private commitment model that includes preparation, travel, recovery, and unresolved follow-up—not just calendar duration; An owner-editable energy and boundary profile with uncertainty and expiration; A cross-surface scan that correlates calendar invitations, mail threads, and browser task pages; A draft-only renegotiation composer with evidence for why the commitment is flagged; A quiet, owner-controlled threshold for when this may interrupt


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's single-button/single-LED interaction with a production pendant interaction module: a low-power coin haptic actuator with a dedicated driver, a capacitive or force-sensitive confirmation surface, and a fuel-gauge IC exposed to firmware. Keep the physical button as an emergency stop. Define three haptic patterns (queued, needs-confirmation, completed) and expose battery/charging state to the relay.
- **owner gets:** The owner can approve or stop a cross-surface action privately in a pocket, know whether a delayed brief is waiting without opening a phone, and avoid discovering that the pendant died. This enables genuinely hands-free, silent operation in meetings and public places rather than forcing spoken confirmation.
- effort: Medium hardware revision and firmware abstraction; validate enclosure acoustics, false touches, haptic patterns, and battery calibration across a week of wear. Add relay event types and end-to-end tests for stop/confirm/reconnect.  ·  risk: Haptic noise or accidental touch could disturb the owner or approve the wrong thing; default the new surface to notification-only, require a deliberate press-and-hold for approval, and retain the current button as stop. If the driver fails, fall back to LED/audio and continue action receipts. Fuel-gauge readings can be wrong until calibrated.
- cost: Approximately $3–$8 BOM increase in volume ($10–$20 in prototype parts), plus under 5 mA peak during haptic pulses and tens of µA quiescent for the gauge. No per-invocation API cost.  ·  latency: Local confirmation/stop is sub-100 ms and works during a dropped link; battery telemetry adds negligible relay latency.
- security: A physical confirmation channel reduces accidental remote approvals, but it must never approve destructive actions from a single tap. Store no biometric or touch waveform; emit only explicit button/gesture events.
- depends on: Cross-surface commit coordinator with typed confirmation states; Universal stop latch and reconnect receipt queue; Firmware event protocol for haptic/gesture/battery telemetry


## What it asked for

### `t21-35y1` (tool) — source_health_snapshot
- why: The daily brief must distinguish empty results from failed or stale authenticated providers before any model summarizes them; current per-surface action tools return results but do not provide a common health/freshness verdict.

```json
{
  "sources": "array of {id: string, kind: 'mail'|'calendar'|'github'|'browser_page'|'filesystem', max_age_seconds?: number}",
  "attempt_budget": "integer, default 2",
  "include_evidence": "boolean, default true"
}
```

