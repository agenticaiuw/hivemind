# Harness derivation — faculty-judgement — round 7

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep track of the promises and deadlines I make, and only remind me when one is at risk.”"
- **useful because:** People lose commitments across spoken conversations, email, calendar, and private web apps. This turns scattered intent into a closure loop: detect a commitment, identify its owner and due date, verify whether it was completed, and surface only genuinely at-risk items rather than generating another noisy task list.
- **path:** pendant captures an explicit spoken commitment or lets the owner say “track that” → relay stores a redacted commitment candidate and sends a cheap background job → Mac planner searches permitted Mail/Calendar/files and the browser bridge checks authenticated project or ticket pages for corroborating evidence → relay reconciles evidence, assigns confidence and a due-date window, then asks one short spoken clarification only when needed → pendant delivers a quiet reminder at an appropriate moment; Mac creates a note/reminder and a sourced review card, but never sends or submits anything
- **model tier:** Background/scheduled work uses a cheap extraction/classification model; gpt-5.6-luna reconciles cross-surface evidence and drafts the reminder; realtime is used only for the brief spoken clarification or delivery.
- **latency:** Capture acknowledgement under 1 second. Evidence gathering can take minutes or run nightly. An at-risk alert should arrive at least one useful working window before the inferred deadline, with quiet hours and a daily cap.
- **cost:** About $0.01–$0.08 per nightly owner-day depending on mailbox/page volume; most cost is authenticated-page extraction and cross-surface reconciliation, not speech.
- **security:** Commitments can expose sensitive relationships and work plans. Store minimum text plus source pointers, encrypt at rest, honor per-source allowlists and TTLs, and never infer a commitment from private audio without an explicit “track that” or an owner-configured opt-in. Alerts should quote only the minimum needed. Any outbound message, file deletion, purchase, or form submission still requires confirmation.
- **missing:** A durable commitment schema with confidence, source provenance, due-date uncertainty, status, and expiry; An opt-in pendant capture/confirmation gesture that is distinct from always-on transcription; Cross-surface evidence adapters for Mail, Calendar, files, and authenticated browser pages; A scheduler and quiet-hours/alert-budget policy; A review UI showing why an item is considered at risk and allowing dismiss, snooze, complete, or correct

### "“I’m going offline for a while—prepare what I need, and catch me up on only what changed when I’m back.”"
- **useful because:** A dropped link, flight, dead phone, or closed laptop currently fragments the agent’s work. This creates a deliberate continuity handoff: the owner gets a small offline packet before disconnecting, and a conflict-aware delta when the pendant reconnects instead of repeating stale briefings.
- **path:** pendant detects a spoken offline request or link-loss transition and confirms the handoff locally → relay freezes active jobs, records a signed checkpoint, and queues safe background work → Mac planner gathers explicitly permitted local files, calendar items, and browser page snapshots into an encrypted offline capsule → browser bridge captures only approved authenticated pages and marks each item with its capture time and freshness → on reconnect, relay compares the capsule against current Mac/browser evidence, asks the owner about conflicts, and speaks a short changed-since-handoff digest
- **model tier:** Cheap background model extracts and diffs documents/pages; gpt-5.6-luna handles conflict resolution and prioritization; realtime is only for the two short spoken interactions.
- **latency:** Handoff acknowledgement under 2 seconds; capsule preparation within 60 seconds for a normal work set. Reconnect digest under 10 seconds after the link is usable, with deeper reconciliation continuing in the background.
- **cost:** Roughly $0.02–$0.15 per handoff, dominated by document/page extraction and diffing; negligible cost when no handoff occurs.
- **security:** Offline capsules are high-value copies of private data. Use end-to-end encryption with device-bound keys, short expiry, explicit source allowlists, and a visible capsule manifest. Never cache passwords, browser cookies, raw microphone audio, or secrets. Require confirmation before syncing any changed content back or taking external actions.
- **missing:** A durable cross-surface checkpoint and job freeze/resume protocol; Encrypted pendant-readable handoff metadata and a Mac-local encrypted capsule store; Browser snapshot/export support that preserves freshness and provenance without exporting session credentials; A reconnect diff engine with conflict and stale-data handling; A local pendant state indicator and offline/reconnected event surfaced to relay

### "“Before I walk into this conversation, give me the context I need—and afterward, turn what I explicitly marked into a follow-up plan without sending anything.”"
- **useful because:** The owner’s important conversations span calendar invitations, email threads, private project pages, and spoken notes, but today those surfaces do not form a safe before/after loop. This capability gives a concise pre-conversation context packet, then converts only deliberately marked observations into sourced follow-up items, preserving continuity without secretly recording everyone.
- **path:** pendant receives an explicit “brief me for this conversation” request and offers a local mark gesture during or immediately after it → relay identifies the meeting/person and coordinates a bounded job → Mac planner gathers permitted calendar, Mail, local notes, and files relevant to that person or meeting → browser bridge reads approved authenticated project/customer pages and returns only cited excerpts → afterward, the pendant asks whether to finalize the marked items; relay reconciles them with the gathered context → Mac creates a reviewable follow-up workspace with owners, dates, evidence, and drafts, while the pendant speaks only the top two actions
- **model tier:** Use a cheap background model for retrieval, clustering, and citation extraction; use gpt-5.6-luna for identity/entity resolution, conflict handling, and concise plan synthesis; use realtime only for the short pre-brief and post-conversation confirmation.
- **latency:** Pre-brief in under 15 seconds, with a first three-bullet answer in under 5 seconds. Post-conversation extraction can finish within 60 seconds. No outbound action occurs without explicit approval.
- **cost:** Approximately $0.03–$0.20 per conversation, dominated by authenticated browser and mailbox retrieval; recurring cost is avoided by caching cited source fingerprints until they expire.
- **security:** This must not become covert meeting surveillance. Require an explicit pre-brief invocation and an unmistakable mark gesture/phrase; do not retain unmarked audio or third-party speech. Enforce source allowlists, redact sensitive excerpts, show provenance and retention, and require confirmation before sending mail, submitting forms, or sharing any generated content.
- **missing:** An identity-and-meeting resolver spanning calendar attendees, Mail, local files, and browser sessions; A pendant-local mark/unmark interaction that works offline and survives a dropped link; A bounded retrieval policy with source allowlists, freshness, and sensitive-field redaction; A durable conversation checkpoint tying pre-brief evidence to post-conversation marks; A Mac review workspace that shows each proposed follow-up, its source, confidence, and approval state


## Changes it proposed to its own stack

### `interaction` — Add a deliberate “track that” capture protocol: after a possible commitment is heard, the pendant gives a short local chime and asks for a one-word confirmation or correction (for example, “Friday”); only confirmed items enter the commitment ledger. A long press cancels, and the owner can say “show my tracked promises” to review or erase them.
- **owner gets:** The owner gets useful commitment tracking without having every private conversation treated as a task, and can correct dates before a false reminder causes stress or embarrassment.
- effort: Medium: pendant gesture/audio state, relay event, ledger integration, and a compact review surface on Mac.  ·  risk: False positives or missed confirmations could create silent gaps; mitigate with explicit confirmation, visible pending state, daily review option, and no destructive external action. If relay is unavailable, retain only a tiny pending marker and expire it locally.
- cost: Small per-event realtime cost for confirmation; otherwise negligible. No hardware cost if an existing button/long press is reused.  ·  latency: Adds roughly 1–2 seconds only when capturing a commitment; ordinary conversation remains unchanged.
- security: Reduces privacy exposure by making capture opt-in. Confirmation audio should be ephemeral and the ledger should retain a redacted summary plus provenance, not raw audio.
- depends on: commitment_ledger tool; durable event persistence and relay-to-pendant confirmation delivery; owner-configurable source allowlists and retention policy


## What it asked for

### `t3-j9ss` (tool) — commitment_ledger
- why: Commitment radar cannot safely infer, track, verify, and remind about commitments without a durable typed record with provenance and uncertainty. Existing generic notes/reminders lose source evidence and status transitions.

```json
{
  "operation": "string enum: upsert_candidate|list_at_risk|record_evidence|set_status|snooze|dismiss",
  "commitment": {
    "id": "optional string",
    "summary": "string",
    "owner": "optional string",
    "due_at": "optional RFC3339 timestamp",
    "due_window": "optional object with start/end RFC3339 timestamps",
    "confidence": "number 0..1",
    "sensitivity": "enum normal|sensitive|secret",
    "source_refs": "array of objects {surface,locator,captured_at,quote_hash}",
    "consent": "enum explicit_track|configured_opt_in"
  },
  "evidence": {
    "surface": "string",
    "locator": "string",
    "captured_at": "RFC3339 timestamp",
    "status": "enum open|done|blocked|unclear",
    "quote_hash": "string"
  },
  "idempotency_key": "string"
}
```

## Its own summary

This round added two owner-facing capabilities that are not ordinary reminders or briefs: a consent-gated commitment radar that detects at-risk promises across spoken intent, Mail/Calendar/files, and authenticated browser evidence; and an offline continuity handoff that prepares an encrypted capsule before disconnection and reports only meaningful deltas after reconnect. I also specified a pendant-level “track that” confirmation protocol and requested a typed commitment_ledger tool.

**Biggest unknown:** The implementation-critical primitives are still undefined: durable cross-surface checkpoint/freeze-resume semantics, event persistence, browser snapshot export without credentials, and the pendant’s exact local confirmation/audio behavior. I do not need another discovery request this round; I need those primitives and the pending orchestrator decisions before these can become safe implementations.

