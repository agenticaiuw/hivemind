# Harness derivation — mac-planner — round 12

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I say ‘prepare my workday’, check my calendar and inbox, make a concise brief, and put it in a note on my Mac; don't send anything.”"
- **useful because:** Turns a vague spoken request into a finished desktop artifact without making the owner wait while reading multiple apps. It is read-only and leaves a durable note they can review.
- **path:** pendant voice request → relay job queue → Mac bridge reads Calendar/Mail and writes a dated Markdown note → dashboard shows source links and completion status
- **model tier:** Realtime model only interprets the short command and confirms scope. A cheap background model extracts and summarizes the fetched data; deterministic Mac actions do the reads/writing.
- **latency:** Acknowledge in under 1 second; complete asynchronously in 10–30 seconds; play a short audio completion notification and expose the note path.
- **cost:** Low: one short realtime turn plus background summarization of bounded snippets. Dominant cost is inbox/calendar text volume; cap to today's events and the newest unread messages, with truncation and local extraction where possible.
- **security:** Reading private mail/calendar requires an explicit one-time account scope and visible source list. Never send, delete, archive, or modify events in this routine. Note content may contain sensitive data; keep it local by default and require confirmation before cloud storage or sharing.
- **missing:** A typed, read-only Mac connector for calendar/mail with bounded fields; A durable async job/result schema and completion notification; A local-note destination policy and source citation format

### "“Find the best flight options for next Thursday, compare total price and duration, and leave me a shortlist; do not book.”"
- **useful because:** Delegates tedious authenticated or public web research and produces a reviewable shortlist without risking a purchase. It can run while the owner does other work.
- **path:** pendant request → relay/background browser agent searches travel sites → dashboard displays structured options, timestamps, and evidence → Mac bridge optionally saves a local comparison file
- **model tier:** Cheap background model drives search and extracts normalized fields; realtime is used only for the initial acknowledgement and final spoken summary. Use a stronger model only when pages disagree or require reasoning.
- **latency:** Initial acknowledgement under 1 second; research 1–3 minutes asynchronously; completion audio under 20 seconds and a dashboard result with direct links.
- **cost:** Moderate and controllable: browser page/tool calls dominate, not model tokens. Limit providers, cache repeated searches, and stop after enough diverse valid options. Avoid sending whole pages to the model; extract price, itinerary, baggage, and timestamp fields.
- **security:** No booking or payment action is allowed in this mode. Authenticated pages and passenger details must remain in the browser session; redact passport/payment data from evidence. Any transition to checkout, account change, or message send requires a fresh explicit confirmation token.
- **missing:** Cloudflare Browser Run integration with tab/session isolation; Structured browser evidence and extraction schema; A policy engine that hard-blocks booking/payment mutations

### "“Clean up my Downloads: group files by type into folders and show me what will be moved before doing it.”"
- **useful because:** Reduces desktop clutter while preserving owner control. A dry-run inventory makes bulk file operations understandable and reversible before any mutation.
- **path:** pendant voice request → Mac bridge inventories Downloads and proposes a move plan → dashboard shows file counts, paths, and conflicts → Mac bridge executes approved atomic moves and reports failures
- **model tier:** Deterministic local planner handles classification and conflict detection; cheap model only labels ambiguous extensions. Realtime handles the short approval dialogue, not the inventory.
- **latency:** Inventory preview in 2–5 seconds for a normal Downloads folder; execution under 10 seconds; spoken confirmation only after the preview is ready.
- **cost:** Very low model cost; local filesystem enumeration dominates. Keep file names/contents on-device and send only counts and proposed categories to the relay.
- **security:** Never delete or overwrite by default. Exclude application bundles, hidden files, cloud-sync folders, and recently modified files unless explicitly included. Require confirmation for the exact move manifest; provide an undo journal and detect external changes before execution.
- **missing:** Dry-run/commit transaction support in the Mac bridge; Atomic move journal with undo; UI for manifest review and conflict policy

### "“Every weekday at 5 pm, summarize the notes I created today into three next actions and put them in my task app; never send messages.”"
- **useful because:** Creates a reliable end-of-day closeout without requiring a live conversation, turning scattered notes into actionable tasks and reducing forgotten commitments.
- **path:** dashboard routine editor sets schedule and note scope → relay scheduler launches a background job → Mac bridge reads today's local notes and creates tasks → pendant plays a brief completion summary
- **model tier:** Cheap background model extracts actions; deterministic integration creates tasks. Realtime is unnecessary except optional audio playback; use a small notification/audio path instead.
- **latency:** Starts at 5 pm, completes within 1–2 minutes, with a dashboard notification and optional short audio.
- **cost:** Low if note text is locally prefiltered and capped; background summarization dominates. Skip execution when no notes exist.
- **security:** Task creation changes external state, so the routine should default to draft/preview until explicitly enabled. Scope to a configured local notes folder, redact secrets, and never infer recipients or send messages. Each run needs an audit record and duplicate suppression.
- **missing:** User-facing recurring routine scheduler/editor; Local notes reader and task-app connector; Draft-vs-commit policy and idempotent task creation


## Changes it proposed to its own stack

### `mac-harness` — Put a typed capability broker in front of the existing FULL_CONTROL computer loop. Accept structured argv/files/app/UI operations with per-capability scopes, dry-run, idempotency keys, result evidence, and confirmation tokens for irreversible or external actions; keep arbitrary shell/AppleScript behind an explicit owner setting and an audit log.
- **owner gets:** The Mac can remain powerful, but a malformed or over-broad plan cannot silently send mail, delete files, spend money, or exfiltrate data. Routine reversible actions stay fast while dangerous actions become understandable and recoverable.
- effort: Medium-high: broker schema, executor adapters, policy tests, migration of existing plan action types, audit/undo journal, and UI confirmation flow.  ·  risk: Some existing automations may fail when untyped; recover with a compatibility mode that logs and requires confirmation, plus per-command allowlists. A bad policy could block useful work, so provide clear escalation rather than silent failure.
- cost: Small implementation/storage cost; negligible API cost. Local policy evaluation adds milliseconds.  ·  latency: <100 ms for local policy; confirmation adds human delay only when risk warrants it.
- security: Large improvement: current FULL_CONTROL bypasses actionRisk entirely, so this closes the main unattended-action gap and limits shell/metacharacter injection.
- depends on: A durable confirmation-token service shared by relay, dashboard, and Mac agent; Typed action/result schema; Owner-visible audit and undo records

### `memory` — Replace per-surface prompt hand-written fleetContext with a compact, typed context API: stable owner preferences and permissions, task-local facts, and expiring summaries are fetched by need. Add token budgets, provenance, retention/forget controls, and automatic pruning of stale sessions.
- **owner gets:** The assistant remembers useful preferences without repeatedly replaying long histories or exposing unrelated private data to every task. Responses become cheaper, faster, and less likely to confuse old context with current instructions.
- effort: Medium: schema/versioning, retrieval filters, summarizer, migration from fleetContext, dashboard controls, and deletion tests.  ·  risk: Over-aggressive pruning can lose important preferences; retain pinned facts and show provenance, with owner-editable memory and restore from versioned records.
- cost: Lower recurring token cost by shrinking every-turn context; modest D1 operations and background summarization cost.  ·  latency: Usually lower due to smaller prompts; one bounded retrieval query per task.
- security: Improves least-privilege context sharing and makes retention explicit. Sensitive entities need field-level redaction and access scopes.
- depends on: A typed task/job schema; Memory provenance and retention metadata; Dashboard memory controls

### `model-routing` — Introduce an asynchronous job router with cheap background models for extraction, summarization, monitoring, and retries; reserve realtime for short voice turns and final notifications, and use a stronger model only on ambiguity or failed structured validation.
- **owner gets:** Long tasks finish in the background without tying up a conversation or making the owner pay realtime rates. The owner receives concise, useful results when ready rather than waiting through tool calls.
- effort: Medium: queue priorities, cancellation, retries, bounded input extraction, model fallback, and result notification/audio generation.  ·  risk: Cheap models can miss nuance; enforce JSON schemas, confidence thresholds, citations, and escalation to a stronger model. Ensure duplicate jobs are idempotent.
- cost: Meaningful reduction in token and audio spend; background model and browser/tool calls become the dominant costs.  ·  latency: Initial response stays sub-second; completion varies by task, with progress and cancellation available.
- security: Background jobs need scoped credentials, expiry, and cancellation. Do not persist raw private inputs beyond the job retention policy.
- depends on: Durable D1 job state and idempotency; Completion notification/audio path; Structured evidence schemas


## What it asked for

### `t6-3vx5` (tool) — mac_read_sources
- why: Workday briefs and other useful desktop routines need bounded, read-only access to Calendar and Mail without scraping UI or granting arbitrary shell control.

```json
{
  "type": "object",
  "properties": {
    "sources": {
      "type": "array",
      "items": {
        "enum": [
          "calendar_today",
          "calendar_range",
          "mail_unread",
          "mail_recent"
        ]
      }
    },
    "start": {
      "type": "string",
      "description": "ISO timestamp, required for calendar_range"
    },
    "end": {
      "type": "string",
      "description": "ISO timestamp, required for calendar_range"
    },
    "mail_limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50
    },
    "account_scope": {
      "type": "string",
      "description": "Pre-authorized account identifier"
    },
    "include_body": {
      "type": "boolean",
      "description": "Default false; return snippets only"
    },
    "redact": {
      "type": "boolean",
      "description": "Default true"
    }
  },
  "required": [
    "sources",
    "account_scope"
  ]
}
```

## Its own summary

Grounded in the actual stack, I proposed four owner-facing capabilities: async workday brief, safe flight research, dry-run Downloads cleanup, and recurring end-of-day action extraction. I also proposed three stack changes: a typed Mac capability broker replacing the unsafe FULL_CONTROL bypass, scoped/pruned memory, and cheap async model routing. I asked for a bounded read-only Calendar/Mail tool and synced relay/browser/terminal peers on job, evidence, and confirmation contracts.

**Biggest unknown:** The critical missing implementation is the end-to-end durable job/confirmation path: exact D1 job schema and callbacks, dashboard routine editor, local Calendar/Mail/task connectors, and whether the owner wants compatibility mode for existing arbitrary shell/AppleScript workflows. Current FULL_CONTROL remains the highest practical risk until the typed broker is deployed.

