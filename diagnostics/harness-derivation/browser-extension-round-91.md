# Harness derivation — browser-extension — round 91

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge liveness** — Live browser status currently reports online=false for home-chrome, no tab, and 9 pending commands; cached default/probe sessions point to stale Safari tabs last used ~7 hours ago. Browser inspections are empty.
  - evidence: GET /browser/status 200: online false, home-chrome tabId null, pendingCommands 9. GET /browser/sessions 200: default tab 320512 lastUsedAt 06:26 UTC plus probe tabs. GET /browser/inspections 200: inspections []

## Capabilities it proposed

### "When I walk away from my Mac, freeze all browser work that can see my private accounts, close or blur sensitive tabs if I choose, and resume the paused read-only work when I return with the pendant. Tell me exactly what was paused, discarded, or resumed."
- **useful because:** The owner can leave the desk without trusting a stale authenticated browser session or an unattended queued command. This uses the pendant's physical presence as a practical privacy boundary while preserving useful work instead of simply losing it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model handles the short spoken pause/resume interaction; a cheaper background worker classifies queued browser steps, expires unsafe work, and produces the audit summary.
- **latency:** Pause must reach the Mac/browser within 2 seconds of a pendant departure event; resume status within 5 seconds of return. No model call is needed for the hot-path freeze.
- **cost:** Negligible per event for the hot path; roughly $0.001–$0.01 for an optional background summary, dominated by model summarization rather than transport.
- **security:** Presence state and browser-action metadata leave the pendant for the relay/Mac; page contents remain on the Mac unless already extracted for the job. A departure must cancel queued submit/send/purchase actions, revoke browser command leases, and optionally close or replace sensitive tabs. Resume must never replay expired or irreversible steps. The owner should explicitly configure whether tabs are merely frozen, blurred, or closed.
- **missing:** Pendant-to-relay presence/absence events with signed, debounced epochs; A browser command lease that can be revoked atomically across /execute, the local queue, and extension polling; A sensitive-tab policy and reversible freeze/restore mechanism in Safari; A cross-surface audit event and dashboard showing paused, expired, and resumed steps; A return-presence handshake that revalidates the Mac, browser device, tab identity, and session freshness


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge liveness and recovery coordinator: maintain per-device heartbeat state, mark cached sessions stale when the extension goes offline, retain queued commands with TTL and idempotency, and automatically resume only read-only jobs when Safari reconnects; emit a concise event containing device, session, queued count, and skipped actions.
- **owner gets:** When Safari sleeps or the extension drops, private-page work will not silently disappear or report stale results. The owner gets one clear status and queued read-only checks resume after reconnect, while irreversible work remains visibly paused.
- effort: Moderate: bridge state machine, queue persistence, reconnect drain, and result correlation; exercise offline/online and duplicate poll cases.  ·  risk: A reconnect could run an outdated read; mitigate with TTL, URL/session revalidation, and cancellation on changed tab identity. Never auto-resume submit/send/purchase actions.
- cost: Negligible API cost; small local JSON/D1 state increase.  ·  latency: No impact while online; reconnect adds one heartbeat/drain interval.
- security: Keeps authenticated content on the owner Mac; logs metadata only (device/session/action class), not page text. Requires explicit stale-session expiry.
- depends on: chg-16bc5dee; chg-14accc01


## What it asked for

_Nothing._
