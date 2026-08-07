# Harness derivation — faculty-judgement — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I on the hook for, and what should I decide next?” Give me one short, sourced list of commitments across my calendar, mail, notes, and logged-in work pages; merge duplicates, flag contradictory or stale evidence, rank by deadline and consequence, recommend the next reversible step, and let me approve any follow-up draft without sending it."
- **useful because:** Today the owner can get separate briefs and page watches, but not a trustworthy answer about obligations that span surfaces. This turns scattered promises and deadlines into an actionable decision queue while explicitly showing uncertainty instead of inventing certainty.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the cheaper background model for scheduled reconciliation and extraction; use realtime only for the owner's spoken clarification and final concise briefing. Mac reads local notes/calendar exports, browser reads already-authenticated private pages, relay deduplicates and persists evidence, pendant speaks the ranked result.
- **latency:** Scheduled runs finish in 2–5 minutes; an on-demand spoken answer should acknowledge immediately and return a 20–40 second brief within 15 seconds. Draft preparation may continue in background.
- **cost:** Roughly $0.02–$0.10 per scheduled run depending on page count; extraction and browser/session work dominate, not the final summary. Realtime cost is limited to the short interaction.
- **security:** Private mail, calendar, notes, and authenticated pages leave their respective devices only as least-privilege extracted fields and citations. Never send, submit, delete, or create an external commitment without confirmation. Secret values must be excluded from the obligation graph; every item shows source, timestamp, confidence, and stale/contradiction markers.
- **missing:** A durable commitment/obligation graph with deduplication, deadline normalization, provenance, confidence, and contradiction states; A cross-surface reconciliation job that can read local notes plus authenticated browser pages and persist evidence snapshots; A review queue and pendant action that lets the owner dismiss, snooze, clarify, or approve a reversible draft; A verified 24 kHz audio playback path for the resulting brief

### "“If I say yes to this, what does it displace, and can I realistically keep the promise?” Given a message, invitation, or request I am viewing, show me the hidden schedule, travel, workload, and dependency consequences; offer three honest responses (accept, decline, or propose a bounded alternative) and draft the chosen reply for my approval without sending it."
- **useful because:** The owner currently gets help after commitments exist, but not before agreeing to one. This prevents overcommitment by connecting the request in front of them to obligations, calendar constraints, active projects, and practical travel or preparation time. It preserves agency: the system recommends and drafts, but the owner decides and sends.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use a cheaper background model for extracting the request and calculating schedule/dependency implications; use realtime only when the owner asks the question aloud or wants a concise spoken recommendation. Browser and Mac agents gather evidence; relay performs the cross-surface comparison.
- **latency:** A spoken feasibility answer should arrive within 10–20 seconds after an immediate acknowledgement. Complex dependency analysis can continue in the background, with the pendant announcing that a fuller answer is ready.
- **cost:** Approximately $0.03–$0.15 per analysis, dominated by authenticated-page reads and dependency extraction. Reuse cached calendar/project state and only reread changed sources.
- **security:** The system may inspect sensitive messages, calendars, work pages, and local notes, but should pass only the minimum extracted facts to the planner. Never infer medical, financial, or employment consequences as certain. Drafts remain local and unsent; accepting, declining, or submitting requires explicit confirmation. Show each recommendation's evidence and uncertainty.
- **missing:** A request-context handoff that captures the active browser tab or selected message with URL, tab identity, and quoted source text; A constraint simulator that accounts for preparation, travel, deadlines, dependencies, and existing commitments rather than only calendar overlap; A private draft workspace showing the three alternatives and their evidence before any reply is sent; Cross-surface freshness and conflict checks so stale calendar or page data cannot produce confident advice


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Obligation Graph and reconciliation worker. Normalize commitments from calendar events, mail threads, local notes, reminders, and authenticated browser pages into entities with owner, counterparty, promised outcome, due window, evidence citations, confidence, and last-confirmed time. Link duplicates and represent conflicts explicitly; emit only material changes to the review queue. Keep drafts and proposed actions separate from commitments.
- **owner gets:** The owner gets an honest answer to “what am I on the hook for?” instead of multiple disconnected summaries, and stale or conflicting information is surfaced before it causes a missed promise.
- effort: Medium-high: schema and migrations, Mac-note/calendar adapters, authenticated browser extraction, deduplication heuristics, expiry/conflict logic, dashboard review UI, and relay scheduling.  ·  risk: False merges or inferred commitments could mislead the owner. Require source citations, confidence labels, conservative matching, expiry, and a one-tap ‘not my commitment’ correction. If a worker fails, retain the last snapshot and mark it stale rather than silently clearing items.
- cost: Small durable metadata storage; background model and browser extraction are the main API costs, bounded by changed-source polling and cached snapshots.  ·  latency: No impact on live voice; scheduled reconciliation is asynchronous. On-demand queries use indexed graph reads and should return in seconds.
- security: High sensitivity. Store normalized fields and hashes rather than raw mail/page bodies where possible; enforce per-source authorization and redact secrets from prompts and dashboard exports.
- depends on: Durable cross-surface job/event persistence; Authenticated browser session reattachment and typed extraction; Shared typed context projection with provenance and TTL; Verified audio queue/playback for spoken briefs

### `firmware` — Make the 24 kHz playback path a negotiated, measured audio contract rather than a codec setting: relay advertises sample rate/frame duration/codec version; pendant reports decode timing, buffer depth, underruns, and resampler health; firmware uses a bounded jitter buffer with sequence/timestamp validation, starts only after a short prefill, and falls back to a lower-rate frame profile when sustained decode or radio budget is exceeded. Add an end-to-end loopback/fixture test that verifies 24 kHz Opus decode → 31.25 kHz I2S output and records an auditable receipt.
- **owner gets:** Spoken briefings will sound continuous and intelligible instead of occasionally clipped, delayed, or silently failing; the pendant can tell the owner when quality degraded rather than pretending audio was delivered.
- effort: Medium: firmware buffer/telemetry and fallback state machine, relay negotiation, fixture audio vectors, acceptance thresholds, and dashboard diagnostics.  ·  risk: A fallback could change voice quality or hide a regression. Announce profile changes in telemetry, preserve the original error, cap buffering to prevent runaway latency, and fail closed to a clear audible/LED error when no safe profile is available.
- cost: Negligible API cost; modest firmware RAM/flash and test-fixture work. Existing simultaneous encode/decode load is about 87% of one core, so profiling and bounded buffering are essential.  ·  latency: Adds roughly 60–120 ms prefill/jitter buffering in the healthy case; avoids much larger stalls from underruns. Negotiated fallback may reduce quality but keeps speech available.
- security: Telemetry contains timing and device identifiers only; authenticate profile negotiation and reject untrusted codec parameters to prevent resource exhaustion.
- depends on: 24 kHz relay transcoding and pendant decoder integration; Durable audio receipts/diagnostics; End-to-end audio acceptance criteria

### `integration` — Build a pre-commitment constraint simulator that accepts a source request plus a candidate response and computes an evidence-backed impact envelope: preparation time, travel and recovery time, calendar collisions, dependent tasks, deadlines at risk, and who must be informed. Represent assumptions separately from facts, run best/likely/worst cases, and generate bounded alternatives such as shorter duration, async response, or a later date. Require a fresh-source check before presenting a recommendation and preserve the exact source excerpt used.
- **owner gets:** Before saying yes, the owner can see the real cost of a commitment and choose an honest alternative instead of discovering conflicts later or disappointing someone.
- effort: High: active-tab/message handoff, calendar and local-project adapters, authenticated browser reads, dependency extraction, temporal simulation, alternative drafting, evidence UI, and confirmation-safe reply integration.  ·  risk: The model could overestimate or underestimate effort, miss an obligation, or expose private context in a draft. Show fact/assumption boundaries, confidence and source timestamps; never claim feasibility as certainty; keep private reasons out of replies unless the owner explicitly includes them; fall back to “insufficient evidence” when freshness checks fail.
- cost: Moderate background-model and browser-read cost per analysis, reduced by cached source snapshots and changed-only refresh. No recurring realtime cost except the brief spoken interaction.  ·  latency: Adds seconds for fresh-source checks and dependency analysis; provide an immediate spoken acknowledgement and return the first bounded estimate within 20 seconds. Full alternatives may complete asynchronously.
- security: High sensitivity because the simulator correlates private schedule, work, and messages. Enforce purpose-limited retrieval, redact unrelated content, keep the impact graph private, and require explicit approval before any draft leaves the device.
- depends on: A source-aware active-tab or selected-message handoff; Freshness-aware cross-surface context projection; Durable evidence snapshots with provenance; A confirmation-gated draft/reply surface


## What it asked for

### `t12-h5kb` (tool) — obligation_graph_reconcile
- why: The owner needs one trustworthy, contradiction-aware answer about commitments spanning calendar, mail, local notes, reminders, and authenticated browser pages. Existing page-watch and brief tools cannot deduplicate obligations or preserve evidence/confidence across surfaces.

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
          "local_notes",
          "reminders",
          "authenticated_browser"
        ]
      }
    },
    "mode": {
      "type": "string",
      "enum": [
        "changed_only",
        "full_snapshot",
        "on_demand_question"
      ]
    },
    "since": {
      "type": "string",
      "format": "date-time"
    },
    "max_items": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50
    }
  },
  "required": [
    "scope",
    "mode"
  ]
}
```

