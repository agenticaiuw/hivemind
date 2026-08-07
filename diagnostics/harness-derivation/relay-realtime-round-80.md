# Harness derivation — relay-realtime — round 80

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say “clip that and send it to my Mac,” take the last few seconds of what I said, package it with context, and hand it to the Mac as a task."
- **useful because:** The owner often talks while away from the Mac. A quick voice clip-to-task flow turns fleeting thoughts into actionable items without requiring them to repeat themselves later.
- **path:** pendant → relay → mac-planner → storage
- **model tier:** Realtime only captures and confirms; a cheaper planner on the Mac turns the clip into actions.
- **latency:** Under a second to confirm capture, then async processing on the Mac.
- **cost:** Low relay cost for capture metadata; Mac planning cost dominates when transcribing and interpreting.
- **security:** Voice content is sensitive. Store only what’s needed, encrypt at rest, and expire clips quickly. Confirm before sending if the clip includes personal data like passwords.
- **missing:** An implemented intent routing tool (relay_route_intent) or equivalent plan submission from relay; A small, durable clip buffer tied to a session on relay or storage; A clear schema for clip metadata (timestamp, locale, partial transcript, confidence); Mac-side handler that can accept a clip package and choose reminder/email/file actions

### "“What’s on my Mac right now, and is anything waiting for me?”"
- **useful because:** The owner can get a trustworthy, spoken snapshot while wearing the pendant and away from the desk: the current Mac display, active browser tab, and salient pending notifications are reconciled into one answer with source labels and uncertainty. This is not merely remote Mac control—the pendant, relay, Mac screen observer, and authenticated browser session jointly provide situational awareness without changing anything.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Use relay-realtime only to interpret the short spoken request and produce the immediate spoken answer; use mac-vision's low-cost vision loop for a screenshot/OCR/UI summary, browser-extension for the active authenticated tab's structured title/URL/text, and mac-planner only to reconcile the reports. No expensive model is needed for extraction.
- **latency:** A spoken acknowledgement in under 500 ms; first answer in 3–5 seconds, with partial status if one surface is offline. Cache the last successful observation with an explicit age rather than pretending it is current.
- **cost:** Roughly $0.01–$0.05 per request depending on screenshot/OCR and planner reconciliation; dominant costs are the vision call and transmitting the screenshot, not the relay utterance.
- **security:** The response can expose private screen and authenticated-page contents over the voice channel, so send only a task-relevant redacted summary by default and never read secrets, tokens, or full message bodies aloud. Keep raw screenshots/tab extracts ephemeral, encrypted, and attributable to timestamp/source; require an explicit spoken confirmation before any future action branch, while this read-only mode needs none.
- **missing:** A Mac-side read-only screen observer with timestamped screenshots, OCR/accessibility tree, active-window metadata, and notification triage (mac-vision is currently disabled).; A browser-extension endpoint that returns the active tab's structured metadata and bounded text to the relay, correlated to the same observation id.; A relay-side observation/fusion record with freshness, provenance, redaction, offline fallback, and a typed spoken-summary response.; A dashboard view showing exactly which Mac/browser observations contributed to each spoken claim.


## Changes it proposed to its own stack

### `relay` — Publish a relay capability inventory endpoint (e.g. GET /v1/relay/capabilities) and status endpoint (e.g. GET /v1/relay/status) so the relay agent can discover its own routes and whether intent routing and server-browser features are implemented.
- **owner gets:** More reliable voice assistant behavior. The relay stops guessing what exists, which reduces misroutes, repeated proposals, and “I can’t see my own surface” bugs that waste time when the owner is speaking.
- effort: Medium. Add route definitions, connect to internal router metadata, and include version/feature flags for unimplemented schemas.  ·  risk: Low. The main risk is exposing internal details; mitigate by returning a minimal, non-sensitive list and gating anything sensitive behind existing auth.
- cost: Small development cost; negligible per-call cost.  ·  latency: Minimal. Inventory calls are rare; voice routing stays fast.
- security: Positive if done right: fewer accidental calls to missing features; ensure the endpoint reveals only what’s necessary.

### `integration` — Implement relay_route_intent as a real router: accept a structured intent, map it to mac_delegate or browser_run_actions, return a job reference, and feed status updates to relay_job_status. Include feature flags so the relay can degrade gracefully.
- **owner gets:** The owner gets consistent behavior: saying “open my calendar” or “check that tab” always routes to the right place, even if some surfaces are offline, without the assistant improvising a protocol.
- effort: Medium to high. Needs backend implementation, mapping logic, job tracking, and tests across Mac online/offline states.  ·  risk: Medium. Bad routing could trigger unintended actions; reduce risk with conservative mappings and clear logging/receipts (no new gates).
- cost: Moderate development cost; runtime cost dominated by downstream planning/execution.  ·  latency: Small added overhead at the relay; most time remains in Mac planning and execution.
- security: Positive if it reduces ad-hoc tool use; ensure intent payloads are validated and logged safely.

### `integration` — Add a read-only, time-bounded 'situation snapshot' protocol spanning pendant audio, relay, Mac observer, and browser extension. On one request, mint an observationId; concurrently collect a Mac screenshot plus active-window/accessibility metadata and the active browser tab's bounded structured extract; redact secrets locally; reconcile only claims supported by timestamped sources; return a spoken summary with age/source markers. Persist only the compact claim set and hashes, not raw screen/page data, and expose a dashboard drill-down for the owner.
- **owner gets:** While away from the desk, the owner can ask what is happening on the Mac and receive a current, evidence-backed answer rather than blindly opening apps or hearing a stale guess.
- effort: Medium-high: a Mac observer and browser-extension response contract, relay fan-out/fusion/redaction, and dashboard provenance UI; staged rollout can ship Mac metadata before vision.  ·  risk: Screen capture or browser extraction could leak private content, and disagreeing snapshots could produce a false synthesis. Recover by defaulting to 'I could not verify', including source ages, minimizing/omitting sensitive fields, and retaining a correlation id for audit. If either surface is offline, report that explicitly rather than substituting old data without labeling it.
- cost: One vision/OCR request plus a small reconciliation request per query; raw screenshot transfer and vision inference dominate. Compact claim storage is negligible; no new hardware cost.  ·  latency: Parallel collection keeps the target at roughly 3–5 seconds; a slow/offline surface should yield a partial response by deadline rather than blocking the pendant.
- security: Adds a sensitive observation channel. Requires local redaction of credentials/OTP/payment fields, encrypted in-transit transport, short TTL for raw artifacts, and dashboard access scoped to the owner; read-only means no mutation risk.
- depends on: A Mac-side read-only screenshot/accessibility observer (mac-vision is currently disabled); An authenticated active-tab extract endpoint in the browser extension; A relay observationId/freshness/provenance schema and spoken-summary path


## What it asked for

_Nothing._
