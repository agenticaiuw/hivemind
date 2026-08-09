# Harness derivation — faculty-perception — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observability and permissions** — At 2026-08-08T23:55Z, GET /ops/status and GET /ops/snapshot report the exact AI Pendant Agent identity healthy and ready: Accessibility and Screen Recording are granted, automation grants are present, browser extension is online on Safari with 2 tabs, relay is reachable with D1, and Mac bridge is online. No pendant is listed in the live device inventory.
  - evidence: GET /ops/status HTTP 200 and read_continuity_snapshot(include=relay,pipeline) HTTP 200; discover(devices) lists only home-macbook-bridge online and cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you tell me something you saw or before another part of you acts on it, show me which parts are directly observed, which are inferred, and which could already be stale."
- **useful because:** The system currently has grounded/asserted claim fields in browser provenance but does not enforce them at the boundary where judgement and speech consume context. This capability would prevent a stale tab title, relay 'delivered' state, or Mac-completed job from being silently upgraded into a fact about what the owner saw or heard. It is useful because it turns perception into a trust contract the other faculties can rely on.
- **path:** faculty-perception → faculty-judgement → faculty-action → browser-extension → relay-realtime → mac-planner
- **model tier:** Cheap background classifier for provenance joins and freshness; realtime model only verbalizes the resulting trust labels
- **latency:** Under 300 ms for cached records; under 2 seconds when it must inspect the current browser or Mac state
- **cost:** Very low: mostly deterministic joins, hashes, and age checks; occasional small model call for ambiguity classification
- **security:** Do not retain raw page text or screenshots merely to explain provenance. Return capsule IDs, source host/path, capture time, hash, sensitivity class, and a short redacted claim. Sensitive claims require confirmation before being spoken or acted on.
- **missing:** A mounted browserProvenance route and consumer; the module exists but is currently unmounted; A relay-to-Mac provenance bridge that returns stable read IDs and content hashes for cloud browser reads; A single claim-envelope contract accepted by judgement and action, with states observed, grounded, inferred, stale, and unknown; Freshness rules by source type, including the explicit rule that socket bytes and Mac completion are not playback

### "Can I rely on you right now, and exactly which parts of you are reachable, stale, or only pretending to be complete?"
- **useful because:** The current status export reports many components but can still hide semantic gaps: the Mac bridge can be online while no pendant exists, a browser can heartbeat while a command is pending, and a relay can accept audio without proving playback. This capability gives the owner a reachability contract rather than a green dashboard: per-surface liveness, freshness age, last verified operation, and the strongest claim that surface can support.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic probes and policy rules first; a small background model turns the matrix into plain language only when needed
- **latency:** 1-3 seconds for active read-only probes; cached answers under 200 ms
- **cost:** Near-zero model cost when rendered from structured probes; network and browser heartbeat probes dominate
- **security:** Probe only read-only health endpoints and do not include tab content, credentials, or audio. Surface stale timestamps and missing devices rather than guessing. Require confirmation before any probe that opens or changes a session.
- **missing:** A typed reachability contract separating transport, authentication, observation, and actuation for each surface; An active pendant-registration/heartbeat source; today no nRF9160 is registered and the converse path does not update the registry; A browser command round-trip probe with a nonce and expiry, distinct from extension heartbeat; A semantic health policy that marks relay socket-delivered audio as not-heard until the accepted playback lifecycle telemetry exists

### "What is actually visible to me right now, and do the browser, screen, and accessibility views agree?"
- **useful because:** Now that the exact AI Pendant Agent has Accessibility and Screen Recording, perception can cross-check three independent views instead of trusting one stale channel. A screenshot can catch overlays and modal dialogs the DOM misses; accessibility can reveal focus and labels; the browser bridge can provide URL/session identity. Reporting disagreements prevents actions against the wrong tab or hidden dialog.
- **path:** faculty-perception → mac-vision → browser-extension → mac-planner → faculty-action
- **model tier:** Realtime vision only for the current screenshot when the owner asks; deterministic browser/accessibility joins and a cheap vision model for routine disagreement detection
- **latency:** 1-2 seconds for a current-state answer; under 500 ms for browser-only cached state
- **cost:** Moderate only when a screenshot is required; image tokens dominate, while DOM/accessibility metadata is cheap
- **security:** Screenshots may contain passwords, financial data, or private messages. Redact known sensitive regions before sending to a model, keep raw screenshots local with short TTL, and require confirmation before exposing or acting on sensitive content.
- **missing:** A perception endpoint that atomically captures screenshot, focused app, accessibility tree summary, and browser snapshot with one capture ID; A local redaction pass for screen images and accessibility values before model upload; A disagreement schema (same tab, same focus, same visible title, overlay present) with freshness timestamps; A policy that blocks action when the three views disagree on target identity

### "Is this browser session, Mac session, and relay conversation definitely the same task and the same me, or could one of them be stale or crossed?"
- **useful because:** The system has separate browser, Mac, and relay identities, but no owner-visible binding that proves they refer to the same live task. A stale browser tab or reused relay context could otherwise feed observations into the wrong action. This capability would expose a task-binding verdict before sensitive context is joined or an action is taken.
- **path:** faculty-perception → browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Deterministic cryptographic/session checks; no model call unless the owner asks for a plain-language explanation
- **latency:** Under 250 ms with cached session state; under 2 seconds when a fresh browser challenge is required
- **cost:** Negligible API cost; dominated by one browser challenge-response and local signature verification
- **security:** Never expose raw session identifiers, cookies, or extension nonces in speech. Bind only pseudonymous task IDs and expiry windows. If binding fails, refuse cross-surface joins rather than guessing.
- **missing:** A relay-issued task nonce propagated into Mac and browser commands; A browser extension challenge-response proving the active tab/session owns that nonce; A Mac-side attestation tying the action ledger and browser result to the same task nonce; An owner-visible 'bound / stale / crossed' verdict consumed by judgement and action

### "Before you say this aloud, did any part of the answer come from a secret, private screen, or sensitive page—and can you safely summarize it without leaking the value?"
- **useful because:** Current redaction and provenance structures protect stored evidence, but nothing is a final speech-time gate across browser text, screenshots, Mac state, and relay-generated summaries. This would stop a private tab title, password fragment, message, or financial value from being spoken merely because it entered context upstream.
- **path:** faculty-perception → relay-realtime → browser-extension → mac-vision → mac-planner → unified
- **model tier:** Deterministic sensitivity classifier and redaction first; a small model only for safe paraphrase when the owner has authorized spoken summaries
- **latency:** Under 150 ms for known-sensitive fields; under 1 second for a novel combined answer
- **cost:** Low: local classification and masking dominate; model cost only for paraphrasing redacted content
- **security:** Raw sensitive values stay on the Mac and are never sent to the relay or realtime model. Default to omission, not euphemistic guessing. Require explicit owner policy for categories such as messages, passwords, health, finance, and intimate content.
- **missing:** A speech-boundary interceptor that sees the final grounded claims before TTS or realtime output; One sensitivity taxonomy shared by evidence capsules, screenshots, browser claims, and Mac automation results; Local redaction/paraphrase routines that preserve meaning without transmitting the secret; A durable owner policy for which categories may be spoken, summarized, or always omitted

### "Has my system become less safe since the last time I trusted it—did permissions, browser sessions, relay credentials, or automation scope change?"
- **useful because:** A current green status is not evidence that the trust boundary stayed stable. The owner needs a security-drift report that notices permission changes, new browser identities, relay credential rotation, scope changes, and unexpected automation surfaces, then distinguishes owner-approved changes from unexplained ones.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic baseline comparison and policy evaluation; use a cheap background model only to explain a flagged diff
- **latency:** Under 1 second from a cached baseline; 2-4 seconds when refreshing all surfaces
- **cost:** Very low: structured metadata and hashes only; no page bodies or screenshots required
- **security:** The baseline itself is sensitive. Store only salted fingerprints, permission classes, device/session pseudonyms, and timestamps. Never expose bearer tokens or raw credential material. A newly broadened permission should be reported but not automatically revoked.
- **missing:** A signed, owner-approved security baseline spanning Mac TCC permissions, browser extension identities, relay device credentials, and action scopes; Change events for permission grants/revocations and relay credential/scope updates; A durable approval record distinguishing owner-approved changes from unexplained drift; A policy engine that blocks sensitive actions when the baseline is stale or unexplained drift is present


## What it asked for

_Nothing._
## Its own summary

Recorded three new, non-duplicate capabilities: cryptographic cross-surface task binding; a speech-time privacy/sensitivity gate; and security-posture drift detection against an owner-approved baseline. Each names the owner-visible benefit and the missing protocol or policy changes required.

**Biggest unknown:** Whether the existing relay, browser, and Mac identity/session stores can be extended with a shared task nonce and signed baseline without exposing credentials or requiring a new owner-facing identity system.

