# Harness derivation — unified — round 37

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep track of the promises and follow-ups I make out loud. If I said I’d send, buy, schedule, or check something, watch the relevant logged-in pages and my Mac for evidence, then remind me only when it is still unresolved—and let me mark it done by voice.”"
- **useful because:** A wearable hears commitments at the moment they happen, while the browser and Mac can verify whether they were actually completed. This closes the gap between a reminder list and reality, without flooding the owner with every note or unchanged page.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Background extraction/classification uses a cheaper model; realtime is used only for the brief spoken confirmation and an on-demand status question. Browser/Mac evidence matching runs asynchronously.
- **latency:** Acknowledge capture on the pendant in under 1 second; create a tracked promise within 30 seconds; evidence checks run on their configured cadence (default hourly during waking hours), with urgent matches pushed within 2 minutes.
- **cost:** Roughly $0.01–$0.05 per captured commitment depending on transcript length and evidence checks; the dominant cost is authenticated page extraction, not the short classification call. Most checks should be skipped using change fingerprints.
- **security:** Commitments and evidence may include private mail, calendar, purchases, or work pages. Store only a redacted commitment plus provenance and short-lived hashes by default; never read unrelated tabs, send messages, buy, or submit forms automatically. Voice “mark done” is reversible; any resulting external action requires the existing confirmation policy.
- **missing:** A durable promise entity with lifecycle (open, snoozed, done, cancelled), confidence, due-window, and provenance linking an utterance to browser/Mac evidence; A cross-surface evidence matcher that can inspect only explicitly bound tabs/apps and distinguish completion from a merely similar page; A quiet-hours/escalation policy and pendant voice commands for snooze, status, and mark-done; A compact owner-facing promise queue and audit trail in the dashboard

### "“Protect my attention across every surface. Combine what my pendant hears, what is on my calendar, what my browser discovers, and what my Mac is doing; interrupt me only when something exceeds my urgency rules, otherwise batch it into the next natural moment.”"
- **useful because:** Today each surface can notify independently, causing duplicate or badly timed interruptions. A single attention policy would let the owner stay focused while still escalating genuinely urgent personal or work events, with the pendant as the final low-friction channel.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background classifier to normalize events and deduplicate them. Use the realtime model only when the owner asks why something was escalated or changes the policy conversationally.
- **latency:** Local suppression and deduplication under 2 seconds; urgent escalation within 10 seconds of a qualifying event; ordinary items delivered at the next configured digest window.
- **cost:** About $0.01–$0.03 per event batch; most cost is event normalization and authenticated browser reads. Deduplication and policy evaluation should be deterministic and avoid model calls when metadata is sufficient.
- **security:** The policy engine necessarily sees sensitive calendar, browser, and conversation metadata. Keep raw content on its originating surface where possible, transmit typed severity/category summaries, encrypt policy state, and expose an explanation and audit trail for every interruption. Never infer medical, relationship, or employment urgency without an explicit owner rule.
- **missing:** A shared event envelope with source, sensitivity, urgency, expiry, correlation key, and freshness; A single owner attention policy with focus modes, escalation contacts/channels, quiet hours, and duplicate suppression; A relay-side arbiter that can delay, merge, or escalate events while preserving source provenance; Pendant-local acknowledgement and snooze semantics that work through a temporary link outage; A dashboard showing suppressed, batched, and escalated events so the owner can tune the policy


## Changes it proposed to its own stack

### `context` — Add a cross-surface commitment/evidence ledger: each captured promise gets a compact typed record (utterance time, normalized intent, due window, sensitivity, allowed surfaces, confidence, and expiry). Browser and Mac workers append signed evidence observations with URL/app provenance, timestamp, semantic fingerprint, and match confidence; a relay reducer advances the lifecycle idempotently and emits one receipt or escalation. Keep raw audio and page text out of the ledger unless explicitly pinned.
- **owner gets:** The owner can ask “what am I still supposed to do?” and get an honest answer grounded in what actually happened, rather than a stale reminder list. If a Mac or browser disconnects, the commitment remains intact and resumes without duplicate reminders.
- effort: Medium-high: schema and reducer, authenticated provenance envelopes, extraction/matching worker, scheduler integration, dashboard queue, and pendant commands; build on existing job receipts and browser session affinity rather than replacing them.  ·  risk: False matches could mark a promise complete or expose sensitive context. Require high confidence or explicit voice confirmation for completion, show source evidence, retain an undo transition, and expire unmatched observations. If the ledger is unavailable, keep a local encrypted capture and replay idempotently when relay returns.
- cost: Small durable storage and queue overhead; approximately one cheap classification call per commitment and incremental extraction only when a bound page changes. No realtime-model cost for background checks.  ·  latency: Voice capture acknowledgement stays sub-second; lifecycle updates are eventual (seconds to minutes) and should not block conversation. Dashboard status can be stale with an explicit freshness timestamp.
- security: Least-privilege per commitment (specific tab/app bindings), redacted fields and short retention, encrypted transport/storage, and no automatic external side effects. Provenance lets the owner inspect exactly why an item was considered done.
- depends on: A durable browser job runner with tab/session affinity and typed results; A typed context projection with sensitivity and TTL; An offline pendant capture spool and delivery receipt; A durable scheduler/queue with idempotency keys

### `interaction` — Create a fleet-wide attention arbiter with a typed event bus. Every surface publishes minimal event envelopes; the arbiter correlates duplicates, evaluates the owner’s focus policy, and chooses suppress, batch, pendant nudge, Mac notification, or urgent escalation. Persist the decision, reason, expiry, and source references so suppressed events can be audited later.
- **owner gets:** The owner gets fewer interruptions without losing important information, and can ask “what did you hold back?” instead of wondering whether something was missed. A single policy follows them between the pendant, Mac, and browser.
- effort: High: define event schema and privacy projection, implement deterministic policy evaluation and correlation, add relay persistence and delivery acknowledgements, integrate browser/Mac publishers, and add pendant snooze/ack behavior.  ·  risk: A bad policy or classifier could suppress something important, while duplicate delivery could create notification fatigue. Default to escalation for unknown high-impact events, show reason codes, retain an undo/replay path, and provide a prominent temporary “interrupt everything” mode.
- cost: Low storage and queue cost; batching reduces model and notification calls. A cheap classifier is needed only for ambiguous severity or semantic correlation.  ·  latency: Adds milliseconds to seconds for normal routing; urgent events should bypass digest queues and reach the pendant within roughly 10 seconds.
- security: Event payloads should be minimized and encrypted; per-surface permissions must prevent the browser from exposing page contents to unrelated policy decisions. Audit records should contain hashes and categories rather than raw private text.
- depends on: A typed cross-surface event envelope and privacy projection; Durable relay scheduling and delivery receipts; Pendant-local snooze/acknowledgement behavior; Owner-configurable focus and escalation policy


## What it asked for

### `t8-7lhy` (tool) — commitment_evidence_query
- why: The proposed promise tracker cannot safely decide whether an uttered commitment was completed using generic browser/Mac actions alone. It needs one least-privilege, provenance-preserving query that searches only explicitly bound tabs/apps and returns evidence candidates without mutating anything.

```json
{
  "type": "object",
  "required": [
    "commitmentId",
    "bindings"
  ],
  "properties": {
    "commitmentId": {
      "type": "string"
    },
    "bindings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "surface",
          "target"
        ],
        "properties": {
          "surface": {
            "type": "string",
            "enum": [
              "browser",
              "mac"
            ]
          },
          "target": {
            "type": "string",
            "description": "Specific tab/session URL pattern or app/path binding"
          }
        }
      }
    },
    "query": {
      "type": "string"
    },
    "since": {
      "type": "string",
      "format": "date-time"
    },
    "maxResults": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10
    }
  }
}
```

