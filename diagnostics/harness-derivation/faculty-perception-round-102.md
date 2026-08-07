# Harness derivation — faculty-perception — round 102

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observe-2026-08-07T14:37Z** — The live Mac agent reports foreground Claude, 16 running apps, Accessibility untrusted and Screen Recording false for AI Pendant Agent; inputReachability is failed, so synthesized UI actions may report success without reaching the screen. Browser extension home-chrome is offline with 10 pending commands and three durable tabs (UTC time.is plus two test forms).
  - evidence: GET /observe at 2026-08-07T14:37:12.320Z; GET /ops/status at same period.
- **relay-mac-bridge-2026-08-07T14:37Z** — Relay is reachable and mac bridge is online; no pendant is registered in the live device discovery (devices list contains only home-macbook-bridge online, home-chrome offline, cloudflare-contract-test offline).
  - evidence: discover devices at current round; GET /ops/status relay payload macBridgeOnline=true and last seen 2026-08-07T14:37:06Z.

## Capabilities it proposed

### "“Is that still true?” Give me a trustworthy answer by comparing what my pendant, Mac, browser, and relay each last observed, showing any disagreement and how old each observation is."
- **useful because:** Today the system can silently mix fresh observations with stale cached state and cannot tell the owner when surfaces disagree. This would make uncertainty visible before the owner relies on an answer, especially after a dropped connection or browser sleep.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model to normalize and compare observations; reserve realtime only when the owner asks verbally and wants an immediate spoken verdict.
- **latency:** Under 2 seconds for a spoken verdict when all surfaces are online; under 10 seconds when reconnecting and reconciling delayed observations.
- **cost:** Low per invocation: mostly local structured comparisons and short metadata; roughly one inexpensive text-model call only when observations need semantic reconciliation. Storage and relay writes dominate rather than inference.
- **security:** The ledger could expose location, private-page presence, audio-derived facts, and device identifiers. Keep raw audio/page content local, send only signed claims and hashes to the relay, encrypt the ledger, apply per-source retention, and require confirmation before sharing a private observation across surfaces.
- **missing:** A cross-surface observation ledger with immutable timestamps, source identity, freshness/expiry, confidence, and contradiction links; Device-signed observation envelopes and replay protection for pendant, Mac bridge, and browser extension; A pendant implementation that can buffer observations offline and later upload them with capture time and delivery acknowledgment; A reconciliation service that distinguishes a true contradiction from observations made at different times or scopes; A dashboard/spoken response format that cites sources and says explicitly when no source is authoritative


## Changes it proposed to its own stack

### `integration` — Add a perception-trust envelope to every Mac/browser action receipt. Before execution, snapshot /observe and /ops/status; attach accessibility/inputReachability, screenRecording, browser-online, tab/session, and bridge/pendant presence. If UI reachability is failed or browser is offline, receipts must be labeled not-verified (and browser commands remain queued), never success. On reconnect, run a fresh observation and reconcile queued commands by request ID, reporting stale/duplicate/confirmed outcomes.
- **owner gets:** The owner will stop being told that a click or typed action succeeded when the agent could not reach the screen, and will know exactly which queued browser work is still pending after Chrome reconnects.
- effort: Moderate: shared receipt schema plus pre/post observation hooks in Mac and browser bridges; migration for existing jobs.  ·  risk: Some previously reported successes will become 'not verified' and require retry or manual review; recover by preserving current receipts and adding explicit reconciliation rather than rewriting history.
- cost: Negligible API cost; one small local status read per action batch and a few hundred bytes of receipt metadata.  ·  latency: Adds roughly 50–200 ms for local probes; no model call.
- security: Stores permission/device health metadata with receipts; redact paths and avoid page content. This improves safety by preventing false claims.
- depends on: Existing GET /observe and GET /ops/status routes; Existing action receipt/job records; Browser command request IDs and durable session state


## What it asked for

_Nothing._
