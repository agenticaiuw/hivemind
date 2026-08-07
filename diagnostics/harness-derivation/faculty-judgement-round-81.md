# Harness derivation — faculty-judgement — round 81

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What should I do next?” — Give me three realistic choices for the next hour, ranked by what matters most, and if I choose one, set up the reversible pieces for me."
- **useful because:** A digest tells the owner what changed; it does not turn a scattered day into a decision. The pendant contributes the live interruption/voice context, the Mac contributes calendar, reminders, mail and local files, the browser contributes authenticated work pages, and the relay keeps assembling the slate after the owner walks away. This gives one mind a judgment layer: urgency, effort, deadlines, and what can actually be done now, with concise tradeoffs rather than a giant list.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** Background/cheap model builds a cited evidence slate and candidate plans; realtime is used only to speak the three choices and answer a follow-up. A deterministic policy layer enforces permissions, freshness, and confirmation before any external or destructive action.
- **latency:** Initial slate in 10–20 seconds (parallel reads); spoken answer under 2 seconds once the slate is cached. If a source is unavailable, say so and rank only verified evidence rather than guessing.
- **cost:** About $0.01–$0.05 per slate using a small background model, dominated by synthesizing private-source excerpts; realtime follow-ups under $0.01 each. Cache unchanged source fingerprints so routine use resends only deltas.
- **security:** Private mail, calendar and authenticated tabs leave their respective surfaces only as minimized, cited excerpts; never send page contents to public search. Do not infer sensitive health or emotional traits from voice. Creating a reminder is allowed by owner policy; sending mail, submitting forms, deleting files, purchases, or calendar changes require an explicit confirmation naming the exact mutation. Every recommendation records source, age, confidence, and why it was ranked; stale or contradictory evidence is surfaced.
- **missing:** A durable decision-slate object with evidence citations, freshness/contradiction state, and expiry; A shared cross-surface availability/attention snapshot from pendant, Mac, browser and relay; A plan-preview endpoint that turns the chosen option into reversible typed actions and a confirmation bundle; Reliable browser tab/window metadata and bridge reconnect (currently blocked by owner-side extension/TCC state)

### "“Before you use another device or service for this, show me what information will leave each surface, what will stay local, and let me approve a redacted version.”"
- **useful because:** Today the owner must trust invisible context movement between a wearable, relay, Mac, browser sessions, and models. They should be able to make a useful request without choosing between convenience and unknowable data exposure. This is a cross-surface privacy decision, not merely a permission toggle: the system presents the exact fields, destinations, retention, and purpose, then carries only the approved projection. It also makes private browser work and voice interaction understandable enough for daily use.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic data-flow classifier and redaction engine first; a cheap background model may explain the preview in plain language. Realtime is used only when the owner asks by voice and should never receive unapproved raw content.
- **latency:** A preview for an ordinary request should appear within 1–3 seconds from typed metadata and cached schemas; uncommon content classification may take 5–10 seconds. Approval must be explicit before dispatch, with a local timeout that cancels rather than defaults open.
- **cost:** Usually under $0.005 per request for deterministic field classification; $0.01 or less when a small model is needed to explain ambiguous text. Storage is limited to hashes and the owner's decision, not retained raw private content.
- **security:** The preview itself must not leak the sensitive content it is previewing: show labels and short masked samples by default. Secret facts, credentials, health data, and private messages require stronger masking and never flow to public search. Persist only policy decisions and provenance hashes with short TTLs. Approval must bind to an exact request, destination, fields, model tier, and retention; any material change invalidates it. This cannot prevent a compromised external service from mishandling approved data, so the preview must state the destination and deletion limits honestly.
- **missing:** A typed cross-surface data-flow manifest emitted before planning, including field sensitivity, destination, model, retention, and transformation; A deterministic local redaction/projection service that can produce approved subsets without sending the original payload to a model; An approval token bound cryptographically to the manifest hash and consumed exactly once by execution; An audit view showing what was actually transmitted versus what was approved, including failed or retried jobs


## Changes it proposed to its own stack

### `integration` — Add a durable Decision Slate coordinator between perception and action. On each request or scheduled wake, it fans out bounded reads to Mac/browser/relay, normalizes each item into {claim, source, observedAt, expiry, confidence, effort, deadline, reversibleAction}, rejects stale/contradictory claims, and emits exactly three ranked next-hour options. Persist the slate and its evidence hashes; when the owner picks one, compile only the reversible steps into POST /plan and require a human-readable confirmation packet before POST /execute. Expire the slate after 30 minutes or any source mutation, and expose a spoken 'why this?' and 'what changed?' view.
- **owner gets:** Instead of repeatedly hearing disconnected reminders and failed automation, the owner gets a short, trustworthy answer to “what should I do now?” that respects what is actually possible at this moment and can resume after interruption without silently repeating work.
- effort: Medium-high: typed schema, fan-out coordinator, ranking policy, persistence/expiry, and integration tests across relay, Mac, and browser. Can ship read-only ranking first, then action compilation.  ·  risk: A bad ranking could hide something important; always show the top omitted urgent item and source citations, cap to three options, and fall back to an evidence list when freshness or contradictions fail. Duplicate execution is prevented with slate/action idempotency keys and existing receipts/undo. Browser reliability remains degraded until the owner reconnects the bridge and fixes TCC; the slate must mark those options unavailable rather than pretending success.
- cost: Roughly $0.01–$0.05 per background slate; low storage for compact claims and hashes. No extra cost when nothing changed due to fingerprints.  ·  latency: Parallel reads 10–20 seconds on a cold slate; cached refresh under 2 seconds. Action execution remains the existing job latency.
- security: Private-source excerpts stay scoped to the coordinator and are minimized; sensitive claims carry stricter TTL and are excluded from spoken output unless requested. Confirmation is mandatory for sends, purchases, deletion, and calendar mutations.
- depends on: Typed source provenance/freshness projection (the repeated context-service backlog items); Durable job receipts and undo (existing receipt half); Browser bridge reconnect and truthful readiness reporting (owner action currently blocked)


## What it asked for

### `t22-gmuh` (tool) — decision_slate_compile
- why: The owner needs a trustworthy answer to “what should I do next?” that combines current private evidence across the pendant, Mac, authenticated browser and relay, ranks three feasible options, and compiles the selected option into a confirmation-ready reversible plan. Existing plan/execute and individual read/action tools do not provide durable cross-source evidence, contradiction handling, ranking, expiry, or idempotent selection.

```json
{
  "request": {
    "type": "string",
    "description": "Natural-language goal, usually 'what should I do next?' or a constraint such as 'I have 45 minutes'"
  },
  "horizonMinutes": {
    "type": "integer",
    "minimum": 15,
    "maximum": 1440,
    "default": 60
  },
  "maxOptions": {
    "type": "integer",
    "minimum": 2,
    "maximum": 3,
    "default": 3
  },
  "includeSources": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": [
        "pendant",
        "mac",
        "browser",
        "relay"
      ]
    },
    "default": [
      "pendant",
      "mac",
      "browser",
      "relay"
    ]
  },
  "mode": {
    "type": "string",
    "enum": [
      "read_only",
      "prepare_selected"
    ],
    "default": "read_only"
  },
  "selectedOptionId": {
    "type": "string",
    "description": "Required when mode=prepare_selected"
  },
  "confirmationToken": {
    "type": "string",
    "description": "Required for any irreversible action; reminders and notes may be prepared without it"
  }
}
```

