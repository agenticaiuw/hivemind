# Harness derivation — faculty-judgement — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Only interrupt me when it is worth interrupting me; otherwise queue it and give me one coherent update later.”"
- **useful because:** Today each scheduled job, browser watch, and Mac event can independently compete for attention. This would combine urgency, deadline, confidence, current focus, and whether the pendant is being worn into one decision: speak now, vibrate later, queue silently, or suppress as duplicate. The owner gets fewer pointless interruptions without missing genuinely time-sensitive items.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Background model classifies and deduplicates events; a cheap policy evaluator scores urgency and interruption cost. Realtime is used only when an approved event actually needs a spoken exchange. Pendant firmware supplies local wear/button/audio state; Mac supplies Focus/meeting/idle signals; browser supplies authenticated-page urgency; relay is the durable arbiter and queue.
- **latency:** Urgent safety/deadline events: under 2 seconds from event receipt to decision. Ordinary events: batch within 5 minutes or at the next owner-selected quiet-window boundary. Spoken delivery starts only when the pendant is available and the policy permits it.
- **cost:** Approximately $0.001–$0.01 per event batch, dominated by background classification and optional speech generation; policy scoring and deduplication should be local/worker-side with no model call for obvious cases.
- **security:** Private calendar/mail/browser titles and device presence signals leave the relevant surfaces only to the relay; retain normalized urgency and hashes rather than raw content. Never infer emergency authority from a low-confidence event. Require confirmation before any action, and let the owner inspect, mute, reprioritize, or delete queue items.
- **missing:** A shared event envelope with source, urgency evidence, deadline, confidence, sensitivity, deduplication key, and expiry; A durable cross-surface attention queue with quiet windows and coalescing; Pendant push/vibration and local availability signal; Mac Focus/meeting/idle signal adapter; A policy endpoint that returns speak-now, defer-until, queue, suppress, and an explanation

### "“If I haven’t dealt with this by Friday, make sure the right person knows—but don’t send anything unless the conditions are actually met.”"
- **useful because:** The owner can make conditional commitments without relying on memory. The system would watch for concrete completion evidence across the Mac and authenticated browser, remind the owner privately first, and—only under an explicitly configured rule—prepare or send a narrowly scoped escalation to a chosen person. This closes the loop between intention, evidence, and consequence rather than merely creating another reminder.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A background model extracts the commitment, recipient, evidence criteria, and fallback wording. Deterministic policy evaluates deadlines and evidence. Realtime is used only for the pendant's brief confirmation or final approval conversation; no expensive model is needed for routine checks.
- **latency:** Commitment capture under 5 seconds. Evidence checks run hourly or at configured checkpoints. A missed-deadline decision should reach the pendant within 30 seconds; external delivery waits for explicit approval unless the owner has separately enabled that exact escalation rule.
- **cost:** Roughly $0.005–$0.03 per commitment per week, dominated by occasional cross-surface summarization; most evidence checks are deterministic hashes, timestamps, and typed state reads.
- **security:** Recipients, deadlines, and private evidence are sensitive. Store encrypted commitment definitions, minimize copied content, and show the exact evidence and proposed message before any send. Destructive or reputational actions always require confirmation unless the owner has granted a specific, revocable rule for that recipient and message class. Every escalation needs an audit trail and cancellation window.
- **missing:** A typed commitment definition with completion predicates and fallback conditions; Cross-surface evidence adapters that can prove or disprove those predicates; A durable deadline monitor with timezone and clock-skew handling; A recipient-specific escalation policy and revocation mechanism; A review surface showing evidence, proposed message, and cancellation/approval controls


## Changes it proposed to its own stack

### `interaction` — Add an attention arbitration layer above schedules, browser watches, relay jobs, and Mac notifications. Normalize every candidate interruption into an event envelope (deadline, consequence, confidence, sensitivity, source, dedupe key, expiry), maintain a durable queue, and compute a single owner-facing decision with reason and reconsideration time. Feed local pendant wear/audio/button state and Mac Focus/meeting/idle state into the scorer; coalesce related items into one brief rather than emitting separate alerts.
- **owner gets:** The pendant becomes considerate instead of merely loud: it can wait while the owner is speaking or in a meeting, combine five low-value updates into one useful sentence, and still surface the one thing that truly cannot wait.
- effort: Medium-large: event schema and queue, relay arbiter, Mac signal adapter, browser/job integrations, pendant push/availability path, dashboard controls, and end-to-end interruption tests.  ·  risk: A bad score could delay something important or create alert fatigue. Mitigate with conservative defaults, expiry/deadline fail-open rules, visible explanations, per-source mute controls, and a one-button 'tell me everything queued' recovery path. If relay is unavailable, local pendant only handles explicit emergency/high-priority pushes.
- cost: Low ongoing API cost if normalized events are scored by deterministic policy; occasional background model calls for ambiguous urgency and deduplication. Storage is small metadata plus owner-approved summaries.  ·  latency: Adds milliseconds for deterministic events and up to a few seconds for ambiguous classification; urgent events bypass batching.
- security: Centralizes sensitive urgency metadata, so encrypt queue contents, minimize raw page/mail text, enforce source-specific retention, and audit every speak/defer/suppress decision.
- depends on: Durable cross-surface job/event persistence; Typed action postconditions and event provenance; Pendant server-push/availability signal; Mac Focus/meeting/idle adapter; Owner-configurable quiet windows and escalation policy

### `hardware` — Add a low-power secure element to the pendant, provisioned as the owner's revocable presence and approval key. It should sign button-confirmed approvals and short-lived presence assertions, with replay protection and a hardware-backed counter; private message content and long-lived credentials must remain off-device.
- **owner gets:** The owner could approve a consequential handoff with a physical gesture they trust, even when the Mac is locked or the browser session is elsewhere, without exposing account passwords or making the pendant a copy of their identity.
- effort: Medium: select and integrate a secure element, provision/revoke keys, add pendant signing firmware, relay verification, recovery ceremony, and dashboard controls for revocation and audit.  ·  risk: Loss or theft of the pendant could enable unauthorized approvals if presence is treated as sufficient. Require button interaction plus a short validity window, support immediate remote revocation, rate-limit signatures, and provide a recovery path using the Mac. Firmware rollback and counter desynchronization need tested recovery.
- cost: Approximately $1–$3 in added component cost at volume, negligible idle power and a few milliseconds per signature; no recurring model/API cost.  ·  latency: Adds roughly tens of milliseconds to a physical approval and negligible time to ordinary conversation.
- security: Improves resistance to remote prompt injection and stolen browser sessions, but creates a high-value key. Use per-device keys, encrypted provisioning, signed firmware, rotation, revocation, and never use it to silently authorize arbitrary actions.
- depends on: Typed commitment and escalation policies; Relay-side signature verification and audit logging; Pendant firmware update and secure provisioning process; A clear owner recovery and revocation flow


## What it asked for

### `t18-8ylu` (tool) — attention_arbitrate
- why: A single durable arbiter is needed to decide whether cross-surface events should interrupt, defer, coalesce, or suppress. Without a typed decision endpoint, each scheduled job and surface will continue notifying independently and the proposed capability cannot be implemented safely.

```json
{
  "type": "object",
  "required": [
    "events",
    "owner_state"
  ],
  "properties": {
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "event_id",
          "source",
          "summary",
          "urgency",
          "confidence",
          "sensitivity",
          "dedupe_key",
          "expires_at"
        ],
        "properties": {
          "event_id": {
            "type": "string"
          },
          "source": {
            "type": "string"
          },
          "summary": {
            "type": "string"
          },
          "urgency": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
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
          "dedupe_key": {
            "type": "string"
          },
          "deadline": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "expires_at": {
            "type": "string",
            "format": "date-time"
          },
          "evidence_ref": {
            "type": [
              "string",
              "null"
            ]
          }
        }
      }
    },
    "owner_state": {
      "type": "object",
      "required": [
        "pendant_available",
        "quiet_window"
      ],
      "properties": {
        "pendant_available": {
          "type": "boolean"
        },
        "wearing": {
          "type": [
            "boolean",
            "null"
          ]
        },
        "speaking": {
          "type": [
            "boolean",
            "null"
          ]
        },
        "focus_mode": {
          "type": [
            "string",
            "null"
          ]
        },
        "in_meeting": {
          "type": [
            "boolean",
            "null"
          ]
        },
        "quiet_window": {
          "type": "boolean"
        },
        "last_interrupt_at": {
          "type": [
            "string",
            "null"
          ],
          "format": "date-time"
        }
      }
    },
    "policy": {
      "type": "object",
      "properties": {
        "max_batch_size": {
          "type": "integer",
          "minimum": 1
        },
        "urgent_threshold": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "default_quiet_until": {
          "type": [
            "string",
            "null"
          ],
          "format": "date-time"
        }
      }
    }
  },
  "example_call": {
    "events": [
      {
        "event_id": "mail-123",
        "source": "browser:gmail",
        "summary": "Two-factor code expires in 8 minutes",
        "urgency": 0.95,
        "confidence": 0.88,
        "sensitivity": "private",
        "dedupe_key": "gmail:2fa",
        "deadline": "2026-08-07T12:00:00Z",
        "expires_at": "2026-08-07T12:05:00Z",
        "evidence_ref": "tab-4#msg-22"
      }
    ],
    "owner_state": {
      "pendant_available": true,
      "wearing": true,
      "speaking": false,
      "focus_mode": "Work",
      "in_meeting": false,
      "quiet_window": false,
      "last_interrupt_at": null
    }
  },
  "expected_output": "A signed, explainable decision per event: decision (speak_now|vibrate|defer|queue|coalesce|suppress), deliver_after, expires_at, rationale_codes, grouped_event_ids, policy_version, and an audit record with idempotency key. It must fail closed for normal sensitive content but fail open for explicit deadlines above the urgent threshold."
}
```

### `s6-uud6` (skill) — offline_attention_latch
- does: When the relay link drops or the owner is speaking, the pendant locally retains a small set of signed attention decisions already received (urgent, deferred, or queued), signals only the approved haptic/LED urgency pattern, and lets the owner press once to acknowledge or twice to request a compact replay when connectivity returns. It never invents urgency or exposes message text offline.
- must be on-device because: The decision may arrive just before a link drop and the pendant must avoid duplicate alerts or losing an urgent deadline while offline. Local acknowledgement and suppression need to survive radio gaps and button events.
- trigger: Server push of an approved attention decision; link-loss/reconnect event; single or double button press.
- storage: Small ring buffer in pendant flash/NVS: up to 16 envelopes, event IDs, expiry, acknowledgement bits, and replay count; roughly 4–8 KB. No raw mail, page, calendar, or speech content.
- RAM budget: About 8–16 KB working RAM including queue decode and debounce; bounded static allocation, no model or large text buffers, comfortably within the 211,608 B application RAM budget.

