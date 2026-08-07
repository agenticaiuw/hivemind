# Harness derivation — faculty-judgement — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I say yes to this, tell me what it will cause elsewhere in my life—and show me the safest alternatives."
- **useful because:** A form diff tells the owner what fields change, but not the commitments those changes create. This capability would inspect the authenticated browser page, Mac calendar/files, and existing relay jobs to surface collisions, deadlines, costs, follow-up work, and reversible alternatives before the owner commits. It is especially valuable when the owner is speaking through the pendant and cannot manually cross-check five surfaces.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Background planner (cheaper reasoning model) gathers evidence and computes impacts; realtime is used only to ask a concise clarification or read the final consequence brief aloud. Mac-vision/browser perform read-only inspection; faculty-action executes nothing until explicit approval.
- **latency:** Initial consequence scan in 20–60 seconds, with a short spoken result as soon as the highest-confidence conflicts are known; deeper evidence can continue in the background. Irreversible actions always wait for confirmation.
- **cost:** Roughly $0.03–$0.15 per scan depending on number of private pages and Mac documents; latency and token cost are dominated by evidence extraction and deduplication, not the spoken response.
- **security:** Private calendar, mail, browser pages, and local files leave their respective surfaces only as narrowly scoped evidence; redact secrets and unrelated content. Never infer approval from silence. Show source links/snippets, confidence, stale-data warnings, and require confirmation before sending, purchasing, deleting, or accepting anything.
- **missing:** A typed cross-surface impact graph linking a proposed mutation to calendar events, reminders, files, subscriptions, and pending jobs; Read-only browser/Mac evidence bundle with provenance and freshness; A consequence-ranking policy based on deadline, cost, social impact, and reversibility; Pendant-friendly approve/defer/inspect controls and a durable draft of the alternatives


## Changes it proposed to its own stack

### `context` — Add a typed consequence graph and mutation simulator. A proposed browser/Mac action becomes a candidate mutation with entity IDs, time interval, money estimate, audience, reversibility, and confidence. The service queries scoped calendar, reminders, files, browser sessions, and outstanding jobs, then returns ranked direct and second-order impacts with provenance and TTL. It must support an evidence cutoff so stale or missing surfaces are explicitly reported rather than silently treated as clear.
- **owner gets:** The owner gets an honest answer to 'what happens if I do this?' instead of discovering conflicts after accepting an appointment, submitting a form, or promising someone something. It reduces accidental commitments while preserving fast execution when no meaningful consequence exists.
- effort: Medium-high: schema and graph projection, adapters for Mac context graph and authenticated browser, impact rules, provenance UI, and tests for stale/offline surfaces. Start read-only and add mutation adapters later.  ·  risk: False positives could create alert fatigue; false negatives are more dangerous. Mitigate with confidence/rationale, severity thresholds, and 'unknown because unavailable' states. A graph bug must never authorize an action; it only informs the existing approval gate. Recover by disabling a faulty adapter or rule set.
- cost: Small persistent graph/index cost; approximately $0.01–$0.08 in background model calls per nontrivial scan, with caching by candidate hash. No new pendant storage required.  ·  latency: Adds roughly 10–40 seconds for a multi-surface scan; return a fast partial result and stream later evidence. Realtime speech remains low-latency because it reads a compact result.
- security: High sensitivity. Use per-source scopes, local filtering on the Mac/browser, field-level redaction, provenance, short TTLs, and no cross-task reuse without authorization. Never copy secrets or full page contents into the relay graph.
- depends on: A shared typed context service replacing hand-written fleetContext sections; Durable browser session/evidence provenance; Existing irreversible-action confirmation and receipt/undo mechanisms

### `hardware` — Replace the development pendant's single-button/LED interaction with a production interaction module: a low-power haptic actuator plus a capacitive thumb strip or two deliberate tactile controls, with a physical hold-to-confirm gesture. Keep the existing button as an emergency cancel. Expose distinct local events for hear-more, defer, approve, and cancel, with the firmware enforcing hold duration and LED/haptic acknowledgements offline.
- **owner gets:** The owner could review a consequence brief, defer it, or approve a prepared reversible step discreetly while walking or driving without speaking sensitive information aloud or fumbling for a phone. A clear local cancel also makes cross-surface automation feel interruptible rather than dangerous.
- effort: Medium hardware revision and firmware input layer; prototype with a small ERM/LRA motor and capacitive flex or sealed tactile switch, then validate accidental-activation rates, gloves, sweat, and pocket presses. Update relay event semantics and dashboard accessibility labels.  ·  risk: False touches or haptic confusion could trigger the wrong control. Require hold-to-confirm for approval, never allow a single tap to authorize an irreversible action, provide a long-press cancel, and fall back to the existing button/voice path if the new input self-tests poorly.
- cost: Approximately $3–$12 BOM increase for actuator, driver, and sealed input parts, plus a few mA only during feedback; negligible API cost. The current prototype has spare GPIO/I2C/SPI but the product enclosure and board need redesign.  ·  latency: Local acknowledgement under 100 ms; no network round trip for cancel/defer. This makes consequence previews and resumable work usable under LTE latency or a dropped link.
- security: Safer local cancellation and explicit approval semantics, but physical possession remains the trust boundary. Store no sensitive content in the device; emit signed, monotonic interaction events and reject replayed approvals.
- depends on: A typed candidate-action/impact result with explicit approve, defer, and cancel states; Firmware event protocol and relay idempotency for local input events; A production pendant PCB/enclosure rather than the current nRF9160 development kit


## What it asked for

### `t11-xyom` (tool) — cross_surface_impact_scan
- why: The proposed consequence-preview capability needs one read-only operation that gathers scoped, provenance-carrying evidence from authenticated browser tabs, Mac context, calendar/files/reminders, and active relay jobs. Without a single typed result, realtime cannot honestly answer what a proposed commitment will cause elsewhere.

```json
{
  "type": "object",
  "required": [
    "candidate"
  ],
  "properties": {
    "candidate": {
      "type": "object",
      "required": [
        "summary"
      ],
      "properties": {
        "summary": {
          "type": "string"
        },
        "sourceUrl": {
          "type": "string"
        },
        "proposedFields": {
          "type": "object"
        },
        "timeRange": {
          "type": "object"
        },
        "estimatedCost": {
          "type": "number"
        },
        "audience": {
          "type": "string"
        },
        "actionKind": {
          "type": "string",
          "enum": [
            "accept",
            "send",
            "purchase",
            "schedule",
            "delete",
            "edit",
            "other"
          ]
        }
      }
    },
    "scopes": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "browser",
          "calendar",
          "mail",
          "files",
          "reminders",
          "jobs"
        ]
      }
    },
    "maxSeconds": {
      "type": "integer",
      "minimum": 5,
      "maximum": 120
    },
    "freshnessSeconds": {
      "type": "integer",
      "minimum": 30,
      "maximum": 86400
    }
  }
}
```

## Its own summary

Proposed a new cross-surface capability: consequence preview before commitment—inspect the private browser page plus Mac calendar/files/reminders and relay jobs, rank direct and second-order impacts, and present safe alternatives without changing anything. Proposed the enabling typed mutation/consequence graph with provenance, TTLs, explicit unknowns, and no authorization power. Queued a precise read-only cross_surface_impact_scan tool request. Still need that tool, the typed context/impact graph, and owner-approved source scopes; no further permissions are needed this round.

**Biggest unknown:** Which concrete owner sources are authoritative for commitments (calendar vs reminders vs mail vs task files), and what severity/latency threshold should trigger a spoken interruption rather than a queued review item.

