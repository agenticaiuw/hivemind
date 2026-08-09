# Harness derivation — faculty-action — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you send or change anything, show me exactly what will happen, let me approve the preview on the pendant, then do it and prove the result.”"
- **useful because:** The owner gets a trustworthy two-phase action: a human-readable preview before side effects, a deliberate physical approval, and an independently checked outcome. It prevents the dangerous gap where a Mac receipt says an action ran but the intended browser/file/message postcondition was never established.
- **path:** faculty-judgement → relay-realtime → pendant → mac-planner → browser-extension → faculty-perception
- **model tier:** Use the realtime tier only to explain the preview and collect the owner's decision; use the cheaper background planner for multi-step planning and faculty-perception for verification.
- **latency:** Preview in under 2 seconds; physical approval can wait up to 60 seconds; execute and verify within 10 seconds for normal Mac/browser actions.
- **cost:** About one realtime turn plus one small background planning/verification call; roughly $0.01–$0.08 depending on model and screenshot evidence, dominated by planner context.
- **security:** Secrets and page contents stay on Mac/browser; the pendant receives only a redacted summary, risk class, digest, and opaque transaction ID. Never execute without a fresh approval, reject expired/digest-mismatched previews, and mark verification unknown rather than claiming success.
- **missing:** A preview envelope renderer on the pendant that can present more than a status code (rotary encoder and second button would make selection practical); A relay orchestrator that chains prepare → physical approval → execute → verify without treating executor receipts as proof; A narrow redaction/summarization contract for previews

### "“If I press the safety button on the pendant, stop every pending computer action and tell me which ones were actually stopped.”"
- **useful because:** A real emergency stop is the one action the owner should never have to explain twice. It provides a physical, offline-tolerant kill path for queued Mac/browser work, cancels before dispatch where possible, and reports per-job cancelled, already-running, or unknown instead of pretending cancellation rewound an external side effect.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** No expensive model is needed for the stop itself: firmware emits a signed event, relay cancels queues, Mac/browser agents enforce cancellation checkpoints, and the background verifier reconciles final states. Realtime is used only to narrate the result if the owner asks.
- **latency:** Pendant acknowledgement under 150 ms locally; relay propagation under 1 second when connected; reconciliation within 5 seconds. Offline press must persist and apply on reconnect.
- **cost:** Near-zero model cost for the stop path; one inexpensive reconciliation call for jobs that were in flight.
- **security:** The stop event must be authenticated, monotonic, replay-resistant, and never interpreted as approval. Cancellation is best-effort: an already-submitted email or web mutation cannot be undone; each job must surface cancelled-before-dispatch, stopped, completed, or unknown. Do not transmit page contents to the pendant.
- **missing:** Firmware mapping for a dedicated second button or rotary-button safety gesture; A relay-wide cancellation fanout and cancellation checkpoint contract in Mac/browser executors; A durable stop epoch that prevents stale queued work from executing after reconnect

### "“Make this browser action work even when the tab changes: bind it to the exact session and target, execute only if the session is still fresh, and prove the field or URL afterward.”"
- **useful because:** Browser automation currently has the highest risk of acting on the wrong tab or stale login. Exact session binding plus freshness gating makes cross-surface action dependable: the browser holds the owner's private session, the Mac plans, the relay coordinates, and perception verifies the actual resulting field or URL.
- **path:** browser-extension → mac-planner → faculty-judgement → faculty-action → faculty-perception → relay-realtime
- **model tier:** Use a cheap planner for selector/session matching; reserve realtime for ambiguity or owner-facing clarification. Use read-only faculty-perception for postconditions and provenance.
- **latency:** Session/status check under 500 ms; action under 5 seconds; verification within 2 seconds after the browser result.
- **cost:** Typically one low-cost planning call and one verification call; screenshots/snippets, if requested, dominate token cost.
- **security:** Session IDs and opaque target handles cross the relay, never cookies, tokens, or page secrets. Refuse stale/unbound sessions and mismatched target digests. Evidence defaults to hash-only or minimal snippet, with secret fields excluded.
- **missing:** A first-class command envelope carrying session ID, target digest, freshness deadline, and postcondition; Browser executor support for atomic check-before-act and result correlation; A policy for when a stale session asks the owner versus safe retry

### "“After you submit this, keep watching for the real confirmation and tell me on the pendant when it actually arrives—or tell me it never did.”"
- **useful because:** Today an action receipt only says that a click or request completed. The owner cannot hand off the long tail: waiting for an email, status change, approval, delivery, or payment confirmation while the Mac may sleep and the browser session may change. This capability turns an action into a truthful outcome contract, with explicit expiry and escalation instead of false success.
- **path:** faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime → pendant → faculty-perception
- **model tier:** Use a cheap background watcher and event matching model; reserve realtime only for ambiguity or the owner's spoken follow-up. The relay holds the watch while the Mac sleeps, and faculty-perception checks fresh browser/Mail state before emitting a result.
- **latency:** Initial watch registration under 2 seconds; poll or event checks on a configurable schedule (typically 1–5 minutes); haptic alert within 10 seconds of a detected confirmation. Expired watches report plainly without further model work.
- **cost:** Low ongoing cost: scheduled lightweight checks dominate, with a small model call only when new text must be matched to the expected confirmation. Roughly $0.01–$0.10 per watched workflow, plus relay execution.
- **security:** The watch stores only an opaque job ID, expected evidence type, expiry, and redacted matching rule. Mail/page contents stay on the Mac/browser; the pendant receives a short status and outcome code. Never infer confirmation from a receipt, and never send reminders or follow-up messages without a separate approval.
- **missing:** A durable outcome-watch object with expiry, polling schedule, deduplication cursor, and expected evidence contract; Mac/browser watchers that can inspect Mail or a bound browser session without losing provenance when tabs change; Relay scheduling and wake delivery to the pendant, including haptic states for confirmed, still waiting, expired, and ambiguous; A distinction between immediate executor completion and externally verified outcome in the action ledger


## Changes it proposed to its own stack

### `hardware` — Add a low-profile rotary encoder with integrated push switch to the jewellery pendant, wired as a debounced GPIO/SPI input alongside the existing two DK buttons; reserve the push switch for selecting a pending action and the wheel for browsing redacted action summaries. Pair it with the already-owned DRV2605L and motor once i2c2 is enabled, using tactile patterns rather than a visible multicolour LED.
- **owner gets:** The owner can safely choose among multiple pending actions without memorizing long-press meanings or looking at a screen. A small wheel and tactile confirmation make the pendant feel like jewellery while giving it the missing selection axis needed for previews, cancellation, repeat, and approval.
- effort: Moderate hardware revision and firmware work: encoder PCB/enclosure integration, GPIO interrupt and debounce, menu state machine, and i2c2/DRV2605L integration. Bench test over USB before any product transport assumptions.  ·  risk: Accidental wheel rotation could select an action, so selection must never execute; only a distinct push/hold gesture can approve, and cancellation remains the safe default. Mechanical bounce and cramped enclosure wiring are recoverable with debounce and a fallback to existing sw0/sw1. Do not flash or alter the live device without explicit approval.
- cost: Roughly $3–$15 for an encoder and small PCB/mechanical changes; negligible additional power except brief haptic pulses, with a few KB of firmware RAM/flash.  ·  latency: Selection feedback should be local under 100 ms; no model or relay round trip is required until the owner confirms.
- security: Improves security by separating browse/select from approve. The pendant should carry only opaque IDs and redacted labels, never page contents or secrets; signed approval envelopes remain mandatory.
- depends on: A physical enclosure/PCB revision that can accommodate the encoder; Firmware i2c2 enablement and DRV2605L driver integration; The preview/cancel/approval envelopes proposed above; Owner approval of the specific mechanical component and gesture map


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-surface capabilities: (1) redacted preview → deliberate pendant approval → Mac/browser execution → independently verified outcome (the single most useful missing behavior); (2) a physical pendant emergency stop with durable stop epochs and truthful per-job cancellation states; (3) browser actions bound to an exact fresh session/target digest with postcondition proof. Also recorded a hardware change: add a rotary encoder/push switch and integrate the already-owned DRV2605L so the owner can browse and select pending actions tactfully. Live checks show the Mac bridge and Safari extension online, Accessibility/Screen Recording now granted for AI Pendant Agent, and no pending browser commands.

**Biggest unknown:** The granted verify_operation_step and audio_path_probe schemas still do not resolve to live implementations, so I cannot honestly verify a postcondition or remeasure the audio path this round. The device registry still has no connected pendant. What I still need is implementation of the preview/approval/cancellation envelopes and verifier, an owner-approved encoder/mechanical design, and a real pendant connection for hardware verification; no further permission request is useful right now.

