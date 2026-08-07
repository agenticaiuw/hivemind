# Harness derivation — relay-realtime — round 79

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “resume my work,” tell me the last unfinished thing I was doing across the pendant, Mac, and authenticated browser, then offer the single next action; if I say “do it,” carry it out and report what changed."
- **useful because:** The owner is often away from the Mac and loses the thread between spoken ideas, local apps, and logged-in web tabs. Today no component correlates the last voice intent with Mac action receipts and browser state into one trustworthy continuation. This would make the wearable a genuine handoff point rather than a command microphone.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to recognize the short resume request and speak the answer. A cheaper background summarizer should build a compact handoff capsule from recent receipts, Mac status, and browser tab evidence; mac-planner performs the selected next action.
- **latency:** A cached capsule should produce a spoken answer in under 1 second; rebuilding after a new Mac/browser event may take 5–15 seconds and need not block the owner. Execution remains the existing short-action latency.
- **cost:** About $0.01–$0.05 per capsule refresh depending on model/context; near-zero for cached reads. The dominant cost is summarizing changed activity, not the voice turn.
- **security:** Browser evidence can contain private authenticated page text and should be reduced to titles, URLs, citations, and task-relevant snippets before relay storage. Never expose page contents in an unsolicited spoken response. “Do it” must be an explicit second utterance; all actions need an immutable receipt and undo where available.
- **missing:** A durable cross-surface handoff-capsule store keyed to the owner and updated from Mac action receipts plus browser-session/page evidence; A relay-readable endpoint that returns the capsule with timestamps, confidence, and provenance rather than raw transcripts; A small background refresh trigger on receipt/browser-heartbeat changes (or a Worker alarm); no scheduler exists today; A resume intent handler that can map the selected capsule item to mac-planner or browser-extension without inventing a protocol


## Changes it proposed to its own stack

### `relay` — Add an idempotent command transaction journal spanning the pendant uplink, relay, and Mac/browser executors. Every recognized utterance that could cause an action receives a durable command UUID before dispatch; the relay persists states (heard, dispatched, accepted, completed, failed, unknown) and reconciles unknown states against job receipts after LTE reconnect. A repeated utterance or retry replays status instead of dispatching a duplicate action, while the pendant LED/button can request the latest state without another full voice turn.
- **owner gets:** In weak LTE or a dropped Mac connection, the owner can currently be left unsure whether “send it,” “create that reminder,” or a browser change happened. This gives a clear spoken answer—done, not started, or needs retry—and prevents accidental duplicate actions when they repeat themselves.
- effort: Medium: a small durable command ledger and idempotency key propagation through relay planning/execution, plus reconciliation adapters for existing Mac job receipts and browser command results; firmware needs only a status request/LED pattern if available.  ·  risk: A stale or incorrectly reconciled state could falsely say an action completed. Preserve the raw receipt and expose “unknown” rather than guessing; allow explicit retry and retain undo links. Recovery is ledger replay/reconciliation, not a second blind dispatch.
- cost: Negligible storage and request overhead; no extra model call for retries. A short status summarization may use the realtime model only when the owner asks.  ·  latency: Adds one durable write before dispatch, typically tens of milliseconds; first spoken acknowledgement can be immediate, with completion delivered asynchronously.
- security: Command UUIDs must be unguessable and scoped to the owner/session; ledger contents may include sensitive utterances and action results, so encrypt at rest and redact spoken logs. Do not make the UUID itself an authorization bypass.
- depends on: A durable relay-side store (Durable Object or equivalent); Mac planner/executor and browser command handlers accepting and returning the idempotency UUID; A reconnect/status path from pendant firmware; the current one-button/one-LED device can expose coarse state but needs a defined blink vocabulary

### `interaction` — Give the pendant a physical, always-available cancel gesture: a long press (for example 1.5 seconds) sends an authenticated CANCEL for the currently active relay/Mac/browser command, and the relay immediately stops dispatching further steps, asks downstream executors to cancel, then speaks a concise partial-completion report when the owner releases the button. The gesture must be distinct from the normal press-to-talk path and work even when no speech is recognized.
- **owner gets:** The owner is often away from the Mac and may notice mid-action that a command is wrong, too broad, or affecting the wrong tab. Today stopping requires another successful voice turn—and possibly waiting for the network—so a worn physical control is the fastest way to regain control without adding approval gates to ordinary work.
- effort: Medium: firmware gesture and LED feedback, relay active-command registry plus cancellation propagation, and cooperative cancellation in Mac planner/action runner and browser command queue. For non-cancellable OS operations, mark the command as cancellation-requested and report honestly.  ·  risk: Cancellation can race with completion, so the system must never claim rollback; return a receipt showing steps completed before the cancel. A false long press could interrupt useful work, so require a deliberate hold and a distinct vibration/LED acknowledgement if hardware permits.
- cost: Tiny relay storage/request overhead and no model cost; firmware change only. No new recurring API spend.  ·  latency: Relay should acknowledge the cancel within one LTE round trip (target under 500 ms when connected); downstream stop is best effort and reported as such.
- security: Only the paired pendant/session may cancel its own active command; use a nonce-bound authenticated event, rate-limit repeats, and avoid putting command text in the physical event payload.
- depends on: A relay active-command registry with cancellation state; POST /execute and browser command queue support for cancellation or cancellation-requested receipts; Pendant firmware support for long-press event and a defined LED state


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct gaps: (1) a cross-surface interrupted-work handoff capsule for “resume my work,” (2) an idempotent command transaction journal that resolves LTE/dispatch ambiguity without duplicate actions, and (3) a physical pendant long-press cancel that can interrupt active Mac/browser work. The first is connective work and was flagged as close to an existing backlog item; the latter two are newly recorded changes.

**Biggest unknown:** Whether the existing Mac/browser executors can accept cancellation and idempotency identifiers without races; implementing those requires a durable relay command registry plus explicit downstream protocol support.

