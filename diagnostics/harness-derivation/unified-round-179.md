# Harness derivation — unified — round 179

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""When I ask you to do something across my Mac or browser, don't just say it ran—tell me only when the intended result is evidenced and I have actually heard the confirmation.""
- **useful because:** It closes the dangerous gap between an accepted job, a browser command, and a spoken claim of success. The owner gets one trustworthy completion statement, or a precise pending/failure statement, instead of false confidence after a timeout or partial execution.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for correlating receipts and evidence; realtime only to phrase the final short spoken result
- **latency:** Up to 2 seconds after the final evidence arrives; otherwise hold the result and notify at the next natural turn, never repeatedly poll in the conversation path.
- **cost:** Low: one background correlation per completed job, dominated by no more than a few receipt/evidence reads; realtime cost only for the final sentence.
- **security:** Query only the explicitly bound tab/app and redact page contents. Never treat command acceptance as success. Require confirmation before reporting irreversible actions; expose failure and stale evidence rather than guessing.
- **missing:** A production joiner that correlates relay job, Mac receipt, browser result, and audio_delivery_ack_queue event into one terminal state; A delivery-aware spoken-result queue on the relay

### ""Use my logged-in browser, but never send the whole page to the relay—pull only the fields needed for this request, and ask me on the pendant before exposing anything sensitive.""
- **useful because:** The browser is the only node with private sessions, so least-data access lets the owner use those sessions without turning every page into model context or relay storage. It makes browser automation feel like a trustworthy assistant rather than a remote screen dump.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** background planner to derive a minimal field selector; realtime only for the owner's explicit confirmation and short result
- **latency:** 1–3 seconds for ordinary structured pages; up to 5 seconds when a confirmation is required. On unsupported pages, refuse rather than fall back to raw capture.
- **cost:** Low-to-moderate: one planning call for a selector and one small structured payload; substantially cheaper than transmitting screenshots/full DOM and safer by construction.
- **security:** Selectors are bound to an exact tab/session and expire. Redact credentials, tokens, hidden fields, and unrelated DOM by default. Sensitive classes (financial, health, messages, account changes) require the physical transaction approval latch; retain only hashes and receipts, not page bodies.
- **missing:** A browser-extension extraction primitive that returns allowlisted structured fields without raw DOM/screenshots; A sensitivity classifier and selector digest enforced by the relay; A policy binding the physical transaction approval latch to data disclosure, not only external actions

### ""Stop whatever action you are currently carrying out for me—on the Mac, in the browser, or in the relay—and tell me exactly what was stopped and what may already have happened.""
- **useful because:** A single, immediate abort is the most important control once this system can act in several places. Today cancellation is fragmented and may leave browser commands, Mac jobs, or relay work running; the owner needs one spoken stop command with a bounded blast radius and an honest partial-effects report.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic control path; no expensive model call for matching an explicit stop command, background model only to summarize partial effects afterward
- **latency:** Issue cancellation within 250 ms locally and within 1 second to relay/Mac/browser when links are healthy. If a surface is offline, mark it unreachable and keep the cancellation intent until its lease expires; never claim stopped.
- **cost:** Very low: authenticated control frames and receipt reads; optional background summarization only on multi-step jobs.
- **security:** Bind the stop to the active session/job set, not an unrestricted kill switch. Preserve immutable receipts, distinguish cancellation-before-dispatch from cancellation-after-side-effect, and never undo or delete data automatically. A local privacy latch remains the separate control for microphone/playback.
- **missing:** A correlated cancellation coordinator spanning relay jobs, Mac jobs, and browser command leases; An idempotent stop-intent envelope with expiry and per-surface acknowledgements; A pendant-to-relay control frame that can carry stop intent over USB fallback and LTE when available

### ""For this request, give yourself a hard budget—time, money, number of messages, and data you may disclose—and stop with a receipt when any limit is reached.""
- **useful because:** The owner can delegate an outcome without granting an unbounded agent. A single request becomes an enforceable contract across the pendant, relay, Mac, and browser: the agent cannot quietly spend more time, send more messages, or expose more data than authorized.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy enforcement and counters; background model only to decompose the request into budgeted steps
- **latency:** Budget checks before every dispatch, under 50 ms locally; report immediately when a limit is exhausted.
- **cost:** Low ongoing overhead for signed counters and receipts; one background planning call per delegated request. It can reduce model and browser costs by preventing runaway retries.
- **security:** Budgets must be immutable after execution begins unless the owner deliberately renews them. Track attempted and completed effects separately, include recipient and data-disclosure counts, and fail closed when a surface cannot report usage. Never infer monetary authorization from a vague phrase.
- **missing:** A signed delegation-contract object propagated from pendant to relay, Mac, and browser; Per-surface pre-dispatch budget enforcement and atomic consumption receipts; Owner-facing renewal/expiration flow that works over USB when LTE is unavailable


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) evidence-gated completion that speaks success only after Mac/browser execution evidence and actual audio-delivery confirmation, (2) least-data browser delegation with field/region-bound disclosure and physical approval for sensitive data, and (3) one explicit stop command that cancels active relay/Mac/browser work and reports partial effects. The third is the highest-leverage safety control; the first is the most useful everyday trust feature. The live Mac bridge and Safari extension are online; the pendant is physically testable over USB but is still not LTE-registered.

**Biggest unknown:** The relay-side joiner/control plane does not yet exist: it must correlate job, browser, Mac, and audio receipts; enforce data-bound selectors; and carry an idempotent cross-surface stop intent. I still need those implementation capabilities, not more owner context. Accessibility/Screen Recording remains an owner-manual grant and is not a blocker for the structured browser/AppleScript paths.

