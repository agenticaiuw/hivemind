# Harness derivation — mac-planner — round 106

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask you to check or do something in my browser, keep it queued if the browser bridge is asleep, wake the right browser when possible, and tell me on the pendant when it is ready or why it cannot proceed—then continue automatically without me repeating myself."
- **useful because:** Today a voice request can silently become a failed browser job because the extension is offline or blocked. This turns the wearable, always-on relay, Mac executor, and browser session into one durable handoff: the owner gets a clear status and does not need to remember or reissue work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background/state-machine logic for health checks, queueing, retries, and notifications; realtime model only for the initial spoken request and concise exception explanation.
- **latency:** Acknowledge on pendant in under 1 second; retry on browser heartbeat for up to 10 minutes with exponential backoff; once online, begin within 2 seconds. Never busy-loop or hold the realtime model open.
- **cost:** Near-zero model cost for normal operation; a few short TTS/status messages per failure or recovery dominate, plus negligible D1/local queue storage.
- **security:** Browser commands may touch authenticated sessions, so preserve existing per-session affinity and evidence capsules; never auto-submit forms or send messages as part of recovery. Opening a browser is low impact, but navigation and mutations must retain existing receipts and owner policy. Status should disclose only site/task labels, not page contents, until execution succeeds.
- **missing:** A durable browser-intent queue with idempotency keys and retry policy shared by relay and Mac agent; A Mac-side health action that can launch the configured browser and surface an actionable notification when the extension is not polling (extension enablement itself may still require the owner); A relay-to-pendant completion/failure event contract tied to the original voice request; A watchdog that distinguishes offline extension, blocked dialog, expired session, and owner-required permission rather than reporting one timeout

### "Replay the last failed thing I asked for in a safe sandbox, compare it with the original pendant, relay, Mac, and browser trace, and tell me exactly which device or step diverged."
- **useful because:** Today a failed voice request leaves separate job receipts, pipeline records, and browser errors, but the owner must manually correlate them and try again. This would turn an intermittent multi-device failure into a reproducible diagnosis rather than another blind retry.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic trace correlation, request-id matching, and sandbox replay first; use a cheap background model only to render the final three-sentence explanation. Realtime is unnecessary.
- **latency:** Immediate spoken acknowledgement; collect the original trace in under 2 seconds and produce a diagnosis within 30 seconds. If replay needs an unavailable browser, report the exact blocked boundary rather than waiting indefinitely.
- **cost:** Usually near-zero model cost; bounded trace storage and one optional short summary call. Replay may consume ordinary Mac/browser execution time but should not invoke paid external actions.
- **security:** Sandbox replay must prevent sends, purchases, deletes, form submissions, and other irreversible effects; authenticated pages should be inspected only in the original paired session and with redacted evidence. Store hashes and bounded excerpts by default, not raw page bodies or audio.
- **missing:** A durable cross-surface correlation ID propagated from pendant audio/pipeline events through relay intent, Mac job, browser command, and every receipt; A replay mode that clones or stubs high-impact actions and marks the boundary where execution was intentionally suppressed; A trace joiner that orders events by monotonic timestamp across device clocks and distinguishes timeout, permission, offline, and application errors; A compact pendant/dashboard result schema carrying first-divergence step, evidence references, and a resumable next action


## Changes it proposed to its own stack

### `model-routing` — Add a live reachability-aware planner preflight that queries /ops/status and /browser/status before selecting an execution path. For each browser intent, classify it as public-read (may fall back to Mac Safari/Chrome AppleScript or direct web retrieval), authenticated-session (queue until the extension is online), or browser mutation (queue and preserve session affinity). Return the chosen path and blocker reason in the plan and receipt, rather than attempting a 45-second browser timeout.
- **owner gets:** A spoken request will fail quickly and intelligibly instead of hanging, and public information can still be delivered when the browser extension is asleep. Authenticated work will wait safely rather than being rerun or accidentally performed in the wrong session.
- effort: Medium: planner preflight, intent classification, bounded fallback executor, and receipt fields; no new model tier required.  ·  risk: Misclassification could send a public read through the wrong browser or queue work unnecessarily. Default uncertain cases to queue/no action; retain the original command and idempotency key so recovery is deterministic.
- cost: Negligible API cost; one or two local status reads per browser request. No extra model call for deterministic classification.  ·  latency: Adds tens of milliseconds for status checks; avoids 45-second dead waits when the bridge is offline.
- security: Improves security by forbidding authenticated fallback outside the paired browser session and making session affinity explicit. Public-page fallback still needs URL allowlisting and evidence capture.
- depends on: Browser bridge must expose a stable online/heartbeat state and session identity (already represented by /browser/status and /browser/sessions).; Planner must attach an idempotency key to queued browser intents.; For authenticated recovery, durable queue and pendant status events are still needed.


## What it asked for

_Nothing._
## Its own summary

Established the live Mac boundary and proposed a new model-routing change: preflight /ops/status and /browser/status, use safe public-page fallback, queue authenticated work, and avoid 45-second browser timeouts. Cross-surface status was sent to faculty-judgement and faculty-action. The owner’s requested self-filing pendant bug reports are already represented in the backlog, so I did not duplicate them.

**Biggest unknown:** Whether the owner will enable the AI Pendant Browser Bridge and macOS Accessibility/Screen Recording; without those, authenticated browser control and vision-based Mac actions remain unavailable. The newly granted mac_readonly_inspect tool is still schema-only, so direct inspection requires a real implementation.

