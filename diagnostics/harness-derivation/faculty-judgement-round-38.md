# Harness derivation — faculty-judgement — round 38

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I’m about to miss something important, rescue it for me: figure out what is actually due, prepare the smallest useful next step, and ask me only when my approval is needed.”"
- **useful because:** Today the owner can request briefs or individual actions, but no system notices that a deadline is becoming unsafe and turns scattered evidence into a concrete rescue. This would combine private browser/mail/calendar evidence, Mac workspace state, and a short pendant interruption without nagging on every unchanged item.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → dashboard → pendant
- **model tier:** Background planner/model for monitoring and evidence reconciliation; cheap extraction/classification first, expensive reasoning only for a detected deadline conflict or high-confidence risk; realtime only for the final brief or approval conversation.
- **latency:** Checks can run on a schedule or event within 1–5 minutes; once risk is detected, a cited rescue packet in under 30 seconds and a one-sentence pendant prompt. No interruption during quiet/focus windows unless a user-defined urgency threshold is crossed.
- **cost:** Roughly $0.01–$0.08 per detected item depending on private-page extraction and synthesis; most checks use selectors/diffs and a small model, with the expensive model reserved for ambiguous conflicts. Storage and Mac/browser wakeups dominate operational cost.
- **security:** Private mail/calendar/task data stays on the Mac/browser bridge where possible; relay receives only a redacted deadline, confidence, and proposed next step. Never send, submit, delete, or commit money without explicit approval. Every evidence item needs URL/source, timestamp, and an expiry; dashboard must expose why the alert fired and allow snooze/disable.
- **missing:** A durable deadline-risk graph that links messages, calendar events, tasks, files, and prior commitments without copying raw private content to the relay.; Event-driven browser/Mac connectors for due-date changes and a deduplicating risk evaluator with quiet-hours and urgency policy.; A rescue-packet UI/audio format: evidence, smallest reversible step, blocked dependency, and one explicit approval gate.; Idempotent preparation actions (draft reply, create local checklist, open relevant files) plus receipts and undo; this should build on, not silently assume, the still-open browser job and approval work.

### "“Before I agree to anything new, tell me what it will displace, whether I actually have room for it, and prepare the kindest way to say no or renegotiate if I don’t.”"
- **useful because:** The owner can already get reminders, briefs, and individual drafts, but cannot see the hidden cost of a new commitment across calendar load, existing promises, preparation time, and personal constraints. This gives them a practical boundary-setting decision before an obligation becomes another emergency. It does not auto-decline anything: it makes tradeoffs explicit and stages a human-approved response.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → dashboard → pendant
- **model tier:** A cheap background model extracts dates, durations, preparation effort, and existing commitments; a stronger model is invoked only when conflicts or ambiguous social context require judgment. Realtime is used only to answer the owner’s spoken question and present the recommendation.
- **latency:** For a new invitation or request, a preliminary displacement analysis in 10–30 seconds; a full cross-source analysis in under two minutes. The owner gets one concise spoken recommendation, with a deeper dashboard view available.
- **cost:** Approximately $0.02–$0.15 per analysis, dominated by private-page retrieval and the occasional deeper synthesis; unchanged sources should be fingerprinted and not reprocessed. Local graph computation and cached calendar data keep routine checks inexpensive.
- **security:** Private message and calendar text should remain on the Mac/browser bridge; relay receives only structured facts and the proposed alternatives. Social inferences must be labeled as uncertain, never presented as facts. Drafts are never sent and calendar changes are never committed without explicit approval. Show every source, assumption, and displacement calculation, with delete/export controls.
- **missing:** A typed personal-capacity model that can represent working hours, recovery time, travel buffers, preparation effort, protected commitments, and owner-entered priorities without exposing raw content.; A cross-source invitation/request intake that extracts the proposed commitment and preserves provenance from email, browser pages, calendar, and spoken input.; A scenario engine that compares accept, decline, shorten, delegate, and renegotiate options and identifies which existing commitments move.; A review surface with editable assumptions and approval-gated draft replies or calendar proposals, plus durable receipts so the owner can see exactly what changed.


## Changes it proposed to its own stack

### `context` — Add a privacy-preserving deadline-risk graph and rescue evaluator. Surface-specific adapters emit typed, redacted facts (dueAt, dependency, status, source, confidence, expiry) from calendar, mail, task pages, local files, and action receipts. A background evaluator detects converging risk (stale owner response, blocked dependency, conflicting dates, insufficient lead time), deduplicates it, and emits a rescue packet with evidence and one reversible next step. Keep raw content and selectors on the originating Mac/browser surface; relay stores only the redacted packet and delivery state.
- **owner gets:** The owner would hear about a real impending failure early, with a prepared way out rather than a generic reminder or a pile of links. It can notice that an unanswered email, a moved meeting, and an unfinished local draft are one problem.
- effort: Medium-high: typed adapters and local redaction, graph persistence, event/schedule triggers, risk heuristics, packet rendering, and integration tests for stale/conflicting sources. Start with calendar + mail + local reminders before adding arbitrary pages.  ·  risk: False alarms could erode trust, and deadline inference can be wrong. Require confidence thresholds, explain each contributing fact, expiry/automatic retraction, snooze and per-source controls. Preparation must be idempotent and reversible; sending/submitting remains gated. Recover by deleting the graph projection without deleting source data.
- cost: Small background model and storage cost per changed fact; expensive synthesis only for a triggered rescue. No new hardware required. Local redaction reduces relay egress and context-token cost.  ·  latency: Event-driven updates within minutes; rescue synthesis generally seconds to tens of seconds. No impact on ordinary voice latency because it runs off the realtime path.
- security: Reduces sensitive-data movement: raw email/page text stays on Mac/browser. Packets still need sensitivity labels, encrypted transport/storage, strict TTLs, and source-scoped access. Audit every contributing fact and generated action.
- depends on: A typed context projection with provenance/TTL (several memory backlog items); Durable browser/Mac event or polling adapters; Approval, receipt, and undo primitives for prepared actions

### `context` — Introduce a personal-capacity and tradeoff engine separate from the existing task/reminder state. It stores owner-editable capacity bands (focus hours, recovery, travel/setup buffers, protected events), estimates effort from source-backed evidence, and produces scenario diffs for accept/decline/shorten/delegate/renegotiate. Each estimate carries confidence, source, timestamp, and an explicit assumption; raw private text remains at the originating Mac/browser surface. Expose an approval-gated review packet containing displaced commitments and prepared-but-unsent response/calendar drafts.
- **owner gets:** The owner would know the real consequence of saying yes before their calendar silently becomes impossible, and could choose a humane alternative without manually reconstructing every conflict.
- effort: High: schema and encrypted persistence, source adapters for invitations and requests, effort estimation, scenario comparison, editable assumptions, review UI/audio, and receipt/undo integration. Pilot with calendar plus email invitations, then add authenticated work portals.  ·  risk: Capacity estimates may be wrong or feel judgmental. Make all assumptions editable, use conservative confidence thresholds, distinguish facts from inferences, and never take an external action automatically. If the engine fails, retain the original invitation and drafts untouched; if its model is deleted, source systems remain authoritative.
- cost: Low ongoing storage; roughly one small-model call per new request and a larger call only for ambiguous scenarios. No required hardware purchase; local computation reduces private-data egress and context cost.  ·  latency: Adds seconds for an interactive request and minutes for complex multi-source scenarios; no pendant audio-path impact because analysis is asynchronous until the owner asks.
- security: Capacity preferences are sensitive personal data and need local encryption, scoped projections, TTLs, and explicit export/deletion. Social messages and calendar details should not leave the Mac/browser bridge except as redacted structured facts.
- depends on: Durable typed context/provenance service; Authenticated browser and Mac read adapters; Approval-gated draft/calendar mutation and receipt/undo primitives


## What it asked for

### `t14-47wd` (tool) — deadline_risk_scan
- why: To make the rescue capability actionable, faculty-judgement needs a read-only, privacy-preserving scan over current calendar/mail/tasks/files and existing action receipts. No current production tool returns linked due dates, blockers, confidence, or source provenance as one typed result.

```json
{
  "type": "object",
  "properties": {
    "scope": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "calendar",
          "mail",
          "tasks",
          "local_files",
          "browser_tabs",
          "action_receipts"
        ]
      }
    },
    "horizonHours": {
      "type": "integer",
      "minimum": 1,
      "maximum": 720
    },
    "includeSensitiveContent": {
      "type": "boolean",
      "default": false
    },
    "knownGoalIds": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "scope",
    "horizonHours"
  ]
}
```

## Its own summary

Discovered the current production tool surface and owner evidence, then proposed a new cross-surface capability: deadline rescue. A privacy-preserving risk graph links redacted facts from private browser pages, mail/calendar/tasks, local files, and action receipts; when a real deadline becomes unsafe it generates a cited rescue packet with the smallest reversible next step and a single approval gate. Recorded the supporting context-layer change and queued a read-only deadline_risk_scan tool request. Asked faculty-perception for available source/event signals.

**Biggest unknown:** Which event-driven/private-source adapters and durable cross-surface persistence primitives have actually shipped; without that, deadline detection may fall back to polling and cannot yet promise timely or complete rescue.

