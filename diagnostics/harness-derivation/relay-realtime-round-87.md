# Harness derivation — relay-realtime — round 87

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say something like “handle that later” or “queue this for when I’m back at my desk,” track it and help me resume it when the Mac is available."
- **useful because:** The owner is often away from the Mac. They need a way to capture intent in the moment, then reliably resume it later without losing context or re-explaining.
- **path:** pendant → relay → mac-bridge → unified
- **model tier:** Realtime for capture/clarification; cheaper planner on Mac for execution when available.
- **latency:** Capture must be instant (sub-second spoken confirmation). Execution can wait until the Mac is online.
- **cost:** Low per capture (short transcript + a small record). Main cost is later planning/execution on the Mac.
- **security:** Stores summarized intent and minimal context. Must avoid leaking sensitive content; provide a quick spoken summary and allow the owner to cancel. No hidden execution without a clear record.
- **missing:** A durable queue or job store that survives relay restarts; A scheduler/availability watcher to trigger resume when the Mac is online; A status/readback UI or voice summary for queued intents; Implementation for relay_route_intent (currently schema-only)

### "When you answer me using my Mac or an authenticated browser tab, tell me briefly what you checked, when it was last observed, and let me ask “why?” to hear the exact supporting snippets or actions—without exposing secrets in the spoken summary."
- **useful because:** Today the owner cannot distinguish a fresh observation from model guesswork or understand why a cross-device answer was produced. Provenance and an on-demand drill-down make the wearable trustworthy while keeping routine voice replies short.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay extracts the provenance request and speaks the concise result; mac-planner and browser-extension return typed observations and source metadata; use a cheaper background model to normalize and redact provenance records, not the realtime tier.
- **latency:** Initial answer should remain under 2 seconds beyond the downstream read. A “why?” drill-down may take up to 4 seconds if it must re-fetch a source; cached provenance should be immediate.
- **cost:** Usually one additional small metadata payload and no extra model call; roughly <$0.001 per interaction beyond existing reads. Drill-down may add one short realtime turn, dominated by existing downstream/API costs.
- **security:** Source snippets can contain private mail, work data, or authenticated-page content. Store only short-lived encrypted provenance references and redacted excerpts, never credentials; require an explicit spoken “why” before reading sensitive detail aloud, and make the dashboard show/delete retained records.
- **missing:** A common typed observation/provenance envelope shared by Mac and browser actions (source, observed_at, operation, redacted evidence, confidence).; Relay-side short-lived provenance cache keyed to the voice run and a spoken follow-up resolver for “why?/where did that come from?”.; Mac and browser adapters that emit source metadata and stable citations for each returned result.; Dashboard controls to inspect retention, redact, and delete provenance records.

### "Before carrying out a spoken request that touches both my Mac and an authenticated browser, tell me in one sentence if the live state differs from what you asked for—such as a changed tab, account, selected file, or draft—and then proceed using the current state unless I stop you."
- **useful because:** A wearable command is often issued without seeing the screen. Today the Mac and browser tiers can act, but the owner has no compact, cross-surface indication that the target changed between intent and execution. This prevents silent actions on the wrong document or account without imposing confirmation gates.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use faculty-perception for deterministic live-state snapshots and faculty-judgement for comparing them with the utterance; the realtime relay only verbalizes the resulting difference. Use a cheaper model for post-action summaries; reserve realtime for the immediate warning.
- **latency:** Add no more than 1 second before the first spoken response for a simple request, and proceed concurrently with state reads where safe. For complex actions, return a warning within 3 seconds while the planner continues preparing the action.
- **cost:** One compact perception/compare call per multi-surface action, typically <$0.005; most cost is screenshot or authenticated-page extraction, not speech.
- **security:** State snapshots may contain private screen and authenticated web data. Send only structured fingerprints and the minimum differing labels to the relay; encrypt transient snapshots, avoid persisting screenshots, and make spoken warnings redact account names unless the owner asks for detail. This is informational, not a confirmation gate.
- **missing:** A shared intent-vs-live-state diff schema spanning Mac UI, files, and browser tab/session identity.; A pre-action snapshot hook in mac-planner and browser-extension, with mac-vision/faculty-perception adapters.; A relay event that can speak a non-blocking discrepancy while the existing action job continues.; Tests proving no discrepancy report can mutate state or accidentally select a different authenticated account.


## Changes it proposed to its own stack

### `integration` — Implement an intent router bridge so relay_route_intent becomes real: relay emits a structured intent + utterance, unified/faculty-perception resolves context, faculty-judgement chooses target (Mac planner vs browser vs server browser), faculty-action dispatches using existing tools. Include receipts/status so the relay can summarize progress without inventing protocol.
- **owner gets:** Voice commands become dependable. The owner can speak naturally and the system routes tasks to the right place, even when the Mac is asleep, without brittle, hand-written routing logic.
- effort: High: requires wiring across relay, unified faculties, and dispatch paths plus telemetry/receipts.  ·  risk: Medium: misrouting could cause wrong actions. Mitigate with conservative defaults, clear spoken confirmations, and receipts/undo where available.
- cost: Moderate: adds planning calls; uses cheaper tiers for non-urgent work.  ·  latency: Low for capture; routing/dispatch can be async when appropriate.
- security: Must log minimal data, avoid leaking sensitive utterances, and keep permissions scoped. Needs audit trail for dispatched actions.
- depends on: Implementation of relay_route_intent (schema exists, no implementation); Reliable status/receipt access for dispatched tasks

### `relay` — Add a first-class Provenance Ledger between relay voice runs and every downstream result. Each dispatched Mac/browser operation receives a voiceRunId and operationId; adapters return a typed envelope containing source surface, observedAt, query/action, redacted evidence references, and confidence. The relay stores only encrypted, short-lived envelopes, attaches a compact citation to the spoken result, and resolves a follow-up “why?” against that exact ledger entry rather than rerunning an ambiguous request. Expire entries automatically and expose deletion/audit controls in the dashboard.
- **owner gets:** The owner can trust a concise answer while away from the Mac, then immediately learn what was actually checked and how fresh it was—without repeating a risky or stale action and without hearing private page contents by default.
- effort: Medium: define the envelope and correlation IDs, instrument mac-planner/browser adapters and relay job receipts, implement short-lived encrypted storage plus a follow-up resolver, and add dashboard inspection/deletion. No model retraining required.  ·  risk: A downstream adapter may omit or mislabel evidence, so the relay must say “source unavailable” rather than invent provenance. Correlation bugs could attach the wrong citation; enforce unique operation IDs and test concurrent voice runs. If the ledger is unavailable, preserve current replies without claiming citations.
- cost: Small storage and serialization overhead; typically no extra model call. Optional redaction can use a cheap background model, with a deterministic field-level scrubber as fallback.  ·  latency: Under 50 ms for ledger write/read on the normal path; a drill-down that fetches a live source may add 1–4 seconds, while cached citations remain immediate.
- security: Improves auditability but introduces sensitive metadata. Encrypt at rest and in transit, keep retention short (for example 24 hours), redact excerpts, isolate tenant/session keys, and provide immediate owner deletion. Never speak raw authenticated content unless explicitly requested.
- depends on: A shared typed result/provenance envelope in the Mac planner and browser extension; Stable voiceRunId/operationId propagation through /plan, /execute, jobs, and receipts; Short-lived encrypted relay storage and a spoken follow-up intent resolver; Dashboard controls for provenance retention and deletion

### `hardware` — Add a tiny coin vibration motor with a low-side driver and a dedicated firmware GPIO to the pendant, plus a sealed tactile isolation mount. Define three local patterns (acknowledged, attention/result-ready, failure) and accept relay push events carrying only a pattern and expiry—not message text or private data. Keep the existing one-button/one-LED behavior unchanged and make vibration optional when battery is low.
- **owner gets:** The owner can know from a pocket or noisy environment that a Mac/browser job finished or failed without staring at the pendant or keeping audio on. A private haptic signal is especially useful when the owner is away from the Mac and cannot safely hear spoken details.
- effort: Medium hardware revision and firmware integration: motor, driver, enclosure/assembly changes, battery characterization, push-event handling, and pattern tests. Requires a relay-to-pendant event channel and a small device capability advertisement.  ·  risk: Vibration can annoy or wake the owner, drain the battery, or be mistaken for another alert. Provide an off/quiet mode, rate limits, maximum pulse duration, and LED fallback; if the motor or driver fails, voice and LED remain functional. Do not use haptic signals to imply an action succeeded unless the receipt is authoritative.
- cost: Approximately $0.50–$2 in components and assembly at volume, plus roughly 10–30 mA while vibrating; negligible idle draw with a proper load switch. No per-call API cost.  ·  latency: A push event can signal completion within the existing relay delivery latency; local onset should be under 100 ms after receipt.
- security: Positive for privacy because status can be signaled without speaking content. The event channel still needs device authentication, replay protection, and expiry; patterns must never encode secrets or arbitrary data.
- depends on: A reliable authenticated relay-to-pendant push channel with reconnect/retry semantics; Pendant firmware capability advertisement and battery-aware event handling; Job receipts that distinguish queued, running, succeeded, failed, and undone states; Owner-configurable quiet hours and haptic enable/disable state


## What it asked for

_Nothing._
## Its own summary

Recorded three proposals: (1) a cross-surface provenance ledger with spoken “why?” drill-down, (2) non-blocking intent-vs-live-state discrepancy reporting before Mac/browser actions, and (3) a private haptic completion/failure channel for the pendant. The required changes are typed correlation/envelopes and short-lived encrypted retention, perception hooks and diff events across Mac/browser, and a future pendant vibration hardware/firmware revision plus authenticated push delivery. No further discovery was performed this round.

**Biggest unknown:** Whether the existing relay-to-pendant production path can deliver authenticated low-latency push events; the available inventory still does not expose that relay surface.

