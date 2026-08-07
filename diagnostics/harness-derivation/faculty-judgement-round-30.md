# Harness derivation — faculty-judgement — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take care of this, even if I leave or one of my devices goes offline—when I come back, show me exactly what is finished, what changed underneath us, and the one decision I still need to make.”"
- **useful because:** Today a multi-step task can partially succeed across the Mac, private browser, pendant, and relay, then leave the owner guessing whether to retry, undo, or continue. This gives them a trustworthy handoff: work survives interruption, stale state is detected before resuming, and partial side effects are explained rather than silently repeated.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** A cheap background model classifies steps, computes semantic diffs, and writes the handoff; the realtime tier is used only if the owner asks a follow-up question through the pendant.
- **latency:** Immediate acknowledgement on the pendant (<2 seconds); background reconciliation within 1–3 minutes after a device returns; no blocking voice turn while long work runs.
- **cost:** Roughly $0.01–$0.05 per interrupted job, dominated by page/state re-reading and the final synthesis; substantially cheaper than replaying the whole conversation in realtime.
- **security:** Private browser data and Mac state remain on their respective nodes where possible; the relay stores only encrypted task checkpoints, hashes, and minimal status. Resuming any irreversible step requires explicit approval, and the owner must be able to discard the recovery capsule.
- **missing:** A cross-surface saga/checkpoint protocol with idempotent steps, semantic preconditions, and compensation records; A durable encrypted recovery capsule shared by relay, Mac, browser bridge, and pendant; A semantic stale-state diff and revalidation service; A dashboard/pendant handoff view that distinguishes done, safely undoable, blocked, and approval-needed

### "“While I’m unavailable, protect my time: triage incoming requests, identify what conflicts with my real commitments, and negotiate a reasonable alternative only within rules I’ve approved. Tell me what you accepted, declined, or left for me.”"
- **useful because:** The owner currently has to personally reconcile messages, calendar constraints, deadlines, and travel context, then conduct the same scheduling negotiation repeatedly. This would provide bounded representation rather than merely a briefing or a draft: it can resolve routine requests while preserving the owner’s judgment for exceptions.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → pendant → dashboard-ux
- **model tier:** A cheaper background model performs extraction, conflict analysis, and policy matching. The realtime model is used only when the pendant presents an exception and the owner discusses it live.
- **latency:** Routine requests should be triaged within 5 minutes; policy-compliant negotiations within 15 minutes. The owner gets a short pendant summary on return, with no realtime model held open while waiting for replies.
- **cost:** Approximately $0.02–$0.10 per request, dominated by authenticated mailbox/calendar reads and any message-generation calls; substantially less than a continuous voice session.
- **security:** This can affect reputation and commitments. It must use an explicit per-domain policy (people, meeting types, maximum delay, working hours, travel buffer, and forbidden topics), never infer permission from silence, and require approval for new commitments, sensitive content, money, legal/medical matters, or anything outside policy. Keep an immutable evidence trail and make every sent message undoable where the service permits.
- **missing:** A versioned owner policy language and approval UI for bounded representation; Authenticated email, calendar, travel, and task connectors with shared identity and provenance; A constraint solver that understands buffers, time zones, dependencies, and uncertainty rather than simple calendar overlap; A send gate that proves a proposed response is within policy before transmission; A pendant exception interaction for approve, reject, or defer without opening the Mac


## Changes it proposed to its own stack

### `integration` — Build a cross-surface saga coordinator: compile a goal into typed steps with preconditions, idempotency keys, evidence checkpoints, and explicit compensation/rollback metadata; persist an encrypted recovery capsule at every checkpoint. When a node reconnects, re-read only the affected state, produce a semantic before/after diff, mark completed steps as verified rather than replaying them, and route the owner one bounded decision if continuation could create an irreversible effect.
- **owner gets:** If a task is interrupted halfway—such as gathering private details, filling a form, and preparing a Mac file—the owner can return to an accurate explanation and continue safely instead of duplicating work or wondering what already happened.
- effort: High: shared schema and durable storage in relay, adapters in Mac and browser agents, pendant status/approval UX, crash/reconnect testing, and compensation handlers for common actions.  ·  risk: A bad compensation could itself change data, and semantic diffs can miss a subtle change. Default to no automatic compensation for external side effects; require evidence and confirmation, keep immutable receipts, and offer a manual recovery path. If the relay is unavailable, retain a bounded local capsule and reconcile later.
- cost: Moderate storage and state-read costs; approximately $0.01–$0.05 per interrupted/reconnected job, mostly model-assisted diffing. No new hardware required.  ·  latency: Adds a few seconds for checkpoint writes and 1–3 minutes for post-reconnect reconciliation, while the pendant acknowledgement remains immediate.
- security: Capsules contain sensitive task metadata and possibly encrypted snippets; use per-owner encryption, least-privilege surface projections, short retention, deletion controls, and never copy raw authenticated page content to the relay unless required.
- depends on: Durable job/event persistence primitives; Per-surface typed action receipts and idempotency; Cross-surface preflight and recovery routing; Owner approval gate for irreversible actions

### `context` — Create a policy-bound representation layer: a versioned, human-readable rule set compiled into machine-checkable constraints for scheduling and communication. Before any external response, the system must show which rule authorized it, which calendar/mail facts supported it, what uncertainty remained, and whether the action creates a new commitment. If no rule matches, it must route an exception to the pendant rather than improvise.
- **owner gets:** The owner could safely let the system handle routine coordination without wondering whether it made a promise, disclosed something private, or traded away time they needed. They would control the boundaries once and receive only genuinely novel decisions.
- effort: High: policy schema and editor, provenance-aware connectors, constraint evaluation, pre-send enforcement, exception UX on pendant, and adversarial testing against ambiguous messages and timezone conflicts.  ·  risk: Overly strict rules could leave routine requests unresolved; overly broad rules could cause unwanted commitments. Start in shadow mode, report hypothetical decisions, require explicit activation per policy category, and retain a one-tap disable switch.
- cost: Low per-request inference overhead; engineering and connector work dominate. Approx. $0.02–$0.10 per handled request for reads, constraint evaluation, and response generation.  ·  latency: Adds seconds for policy evaluation and evidence assembly, but avoids waiting for the owner on routine cases; exceptions reach the pendant promptly.
- security: High sensitivity because the system can speak for the owner. Enforce least-privilege account tokens, redact policy-sensitive data from relay logs, encrypt evidence, expire drafts and receipts, and require explicit confirmation for policy changes.
- depends on: Authenticated mail/calendar/task/travel connectors; A durable provenance and action-receipt store; Pendant approve/reject/defer interaction; A secure policy editor and versioned policy compiler


## What it asked for

_Nothing._
