# Harness derivation — faculty-judgement — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Only interrupt me when it truly matters; otherwise collect it and bring it to me at the next good moment.”"
- **useful because:** The owner gets one attention policy across the pendant, Mac, browser, and always-on relay instead of being interrupted by every notification or missing important changes. The system can recognize that a calendar conflict, urgent account message, or expiring form matters, check whether the owner is speaking/driving/in a meeting, and either speak now, vibrate once, or queue a concise evidence-backed bundle for the next safe opening.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background classifier/rules engine for notification normalization and urgency; use gpt-5.6-luna only to reconcile ambiguous cross-source importance; use realtime solely for the final low-latency spoken interruption.
- **latency:** Urgent events should reach the decision gate in under 10 seconds; a queued bundle can be assembled in the background. The owner should hear at most one short sentence immediately, with detail deferred until asked.
- **cost:** About $0.001–$0.01 per event batch, dominated by occasional Luna reconciliation; routine rules, calendar focus checks, and deduplication should be local/worker-side. Realtime cost is only incurred for an approved spoken interruption.
- **security:** Private notification metadata and snippets cross the relay only when the owner has enabled a source. Default to titles and severity, redact message bodies, retain queued items briefly, and require confirmation before any resulting send, submit, delete, or purchase. Dashboard must show why an interruption was promoted and provide mute/undo.
- **missing:** A shared event envelope with source, urgency evidence, expiry, sensitivity, and deduplication key across relay/Mac/browser/pendant; A cross-surface attention policy evaluator that can read Mac focus/frontmost state and pendant conversation state; A durable short-lived attention queue with 'next safe opening' delivery and auditable promotion reasons; Per-source adapters for calendar/mail/browser watches and a dashboard policy editor; A pendant haptic/LED vocabulary for queued-versus-urgent states without forcing audio

### "“When I make an important decision, remember what I decided, why, what evidence I used, and when I should revisit it—then let me ask you about it months later.”"
- **useful because:** Today the owner can complete a task, but the reasoning disappears across a voice turn, private browser tabs, Mac files, and calendar events. A private decision record would preserve the decision rather than merely the transcript: assumptions, alternatives considered, evidence links or local file references, confidence, affected people, and a review date. Later the pendant could answer “why did I choose this?” or “what changed since then?” with sources and clearly marked uncertainty.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background extractor to detect candidate decisions and collect structured fields; use gpt-5.6-luna only to resolve ambiguity and produce a compact rationale; use the realtime model only for the owner's immediate spoken query. No model should silently infer a consequential decision from casual speech without a reviewable draft.
- **latency:** Draft a candidate record within 30 seconds after a cross-surface job completes; confirmation or correction should take one short voice turn. Historical retrieval should answer in under 3 seconds, with deeper evidence loading deferred until requested.
- **cost:** Roughly $0.01–$0.05 per decision, dominated by one Luna extraction/reconciliation call and optional embedding/indexing; routine storage and retrieval are inexpensive. Do not process every utterance—trigger only on explicit cues or consequential completed actions.
- **security:** Decision records may contain highly sensitive health, financial, relationship, or work information. Keep raw evidence on its originating Mac/browser surface, store only minimized summaries and opaque references in the relay, encrypt records, support per-record expiration/export/deletion, and require explicit owner confirmation for sensitive records. Never expose a private rationale to another person or take a new action solely because an old decision exists.
- **missing:** A first-class decision-record schema with rationale, alternatives, assumptions, evidence references, confidence, participants, sensitivity, and review/expiry dates; A cross-surface collector that can join one pendant conversation with the resulting Mac/browser actions without storing raw private content centrally; An owner-facing review flow for confirm, edit, forget, and mark-as-no-longer-valid, usable by voice and dashboard; A provenance-preserving retrieval/index that distinguishes remembered facts from reconstructed explanations; A scheduled revisit evaluator that can compare current evidence with the decision's original assumptions without changing anything automatically


## Changes it proposed to its own stack

### `integration` — Add an attention-event bus and policy evaluator shared by relay, Mac bridge, browser extension, and pendant. Every candidate event is normalized into {eventId, source, subject, evidenceRef, urgency, sensitivity, expiresAt, requiredAction, dedupeKey}; the evaluator combines it with current conversation state, Mac focus/frontmost app, calendar occupancy, and owner quiet hours. It emits exactly one disposition—speak_now, haptic_only, queue_until_open, or suppress—plus a human-readable reason. Deliveries and acknowledgements are idempotent and expire automatically.
- **owner gets:** Important things reach the owner without turning the pendant into a noisy notification speaker, and the owner can trust a short interruption because the system can explain why it broke through.
- effort: Medium-high: event schema and D1/R2-free short-lived queue, adapters in relay/Mac/browser, pendant haptic command, policy tests, and dashboard controls. Start with calendar plus browser-watch events, then add mail and reminders.  ·  risk: A bad urgency rule could either wake the owner unnecessarily or hide something important. Recover with conservative defaults, visible queue history, per-source mute, one-tap 'always promote/demote', TTLs, and a hard emergency bypass only for explicitly configured sources.
- cost: Negligible storage/compute for rules and queue; roughly $0.001–$0.01 for ambiguous batches that invoke Luna. No continuous realtime model cost.  ·  latency: Adds one local/worker policy hop (target under 200 ms); event ingestion remains background. Spoken delivery waits only for the existing relay turn when promoted.
- security: Use opaque event IDs and minimum necessary metadata in the relay; keep full private content on the Mac/browser where possible, encrypt queued payloads, and audit every cross-surface disclosure.
- depends on: A typed cross-surface event envelope and provenance fields; Current harness-ledger persistence primitives; The already-requested local interruption gate, with this evaluator acting above it; A small pendant command for haptic-only/queued state

### `memory` — Create a private, provenance-preserving decision ledger separate from ordinary memory. The relay issues a decision transaction ID at the start of an explicitly marked decision session; pendant transcript segments, Mac job results, browser page evidence, and resulting calendar/file changes attach to that ID. A background compiler writes a compact record of decision, alternatives, assumptions, evidence references, confidence, sensitivity, and review date, then asks the owner to confirm or edit it. Retrieval must return the record plus source timestamps and distinguish direct evidence from model reconstruction.
- **owner gets:** The owner can recover the reasoning behind an important choice instead of redoing research or trusting an unexplained old memory. When circumstances change, they get a review prompt grounded in the original assumptions rather than an intrusive or irreversible action.
- effort: High: transaction propagation through relay/Mac/browser jobs, local evidence references, encrypted ledger storage, extraction and review UX, expiration/deletion semantics, and tests for source attribution. Build explicit voice-started sessions first; do not attempt passive life-logging.  ·  risk: Incorrectly attributed evidence could create false confidence, and a sensitive rationale could be retained too long. Mitigate with explicit-session opt-in, draft-before-save, visible provenance, conservative confidence, per-record TTL, immediate forget, and no autonomous action from a record.
- cost: Small persistent storage cost; approximately $0.01–$0.05 per confirmed decision for background extraction/reconciliation, with no realtime call unless the owner asks about it.  ·  latency: No impact on live conversation beyond issuing a transaction ID. Draft appears within tens of seconds after the work; retrieval targets under 3 seconds for the summary.
- security: Raw transcripts and page contents remain local where possible; central records contain minimized text and opaque evidence pointers, encrypted at rest and scoped to the owner. Sensitive records require explicit confirmation and support cryptographic deletion of references.
- depends on: A cross-surface job/event correlation primitive; Durable, typed memory with provenance and sensitivity/TTL; Mac and browser adapters that return stable evidence references; Voice and dashboard review controls


## What it asked for

### `t7-wopx` (tool) — attention_event_submit
- why: Implement the proposed cross-surface attention arbitration without forcing each surface to invent its own notification logic. Relay, Mac, and browser adapters need a common write path for candidate events and a typed disposition result.

```json
{
  "type": "object",
  "properties": {
    "source": {
      "type": "string",
      "enum": [
        "pendant",
        "relay",
        "mac",
        "browser",
        "schedule"
      ]
    },
    "subject": {
      "type": "string",
      "description": "Minimal human-readable subject; never include full private body unless explicitly allowed."
    },
    "evidence_ref": {
      "type": "string",
      "description": "Opaque pointer to source evidence retained on its originating surface."
    },
    "urgency": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100
    },
    "sensitivity": {
      "type": "string",
      "enum": [
        "public",
        "normal",
        "private",
        "secret"
      ]
    },
    "required_action": {
      "type": "string",
      "enum": [
        "inform",
        "review",
        "reply",
        "submit",
        "none"
      ]
    },
    "dedupe_key": {
      "type": "string"
    },
    "expires_at": {
      "type": "string",
      "description": "ISO-8601 expiry; event must not be delivered after this time."
    },
    "owner_policy_hint": {
      "type": "string",
      "description": "Optional source-specific hint, not an override."
    }
  },
  "required": [
    "source",
    "subject",
    "urgency",
    "sensitivity",
    "required_action",
    "dedupe_key"
  ]
}
```

## Its own summary

Round 17 produced a new cross-surface capability: a single attention policy that decides speak-now, haptic-only, queue-until-open, or suppress using pendant conversation state, Mac focus/calendar state, browser/account urgency, and relay persistence. I recorded the corresponding integration change (typed, provenance-bearing attention-event bus) and requested an `attention_event_submit` tool. I also asked relay and Mac agents to coordinate delivery and state adapters.

**Biggest unknown:** The actual notification/focus signal inventory and current cross-surface persistence primitives are still unavailable to me, so I cannot yet specify the adapter routes or prove which urgency sources can be safely connected. I still need the requested attention-event tool and those pending orchestrator grants before refining this into an implementation plan.

