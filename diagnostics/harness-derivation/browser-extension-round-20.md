# Harness derivation — browser-extension — round 20

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge health** — Safari browser bridge is currently offline with no registered devices and 2 pending commands; a browser_navigate execution failed after the 45-second wait. This is a live reliability gap, not merely lack of a tab.
  - evidence: GET /browser/status returned {"online":false,"devices":[],"pendingCommands":2}; POST /execute browser_navigate returned failed with message extension offline and durationMs 45127.

## Capabilities it proposed

### "From my pendant, check the private page I mentioned and tell me what changed since the last time I looked; save the evidence to my Mac if it matters."
- **useful because:** Only the browser can access the owner's logged-in page, while only the pendant is available hands-free. This turns a spoken question into a sourced private-page answer and preserves the relevant evidence without forcing the owner back to Safari.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use the realtime tier only to clarify the page identity and speak the short answer; use a cheaper background model to normalize the page and compare it with the stored baseline. Browser performs authenticated navigation/extraction, Mac stores the evidence packet, and the relay routes the result to the pendant.
- **latency:** Target 5–10 seconds when Safari is online; immediately say 'checking' on the pendant. If the bridge is offline, report that state and queue the read rather than hanging.
- **cost:** Roughly $0.01–$0.05 per check depending on extracted page size and comparison model; browser/Mac work dominates reliability, not token cost. Storage is a few KB per evidence packet, with configurable retention.
- **security:** Page content remains on the Mac/browser path; send the relay only the minimum spoken summary and an opaque evidence ID by default. Encrypt stored snippets, redact secrets and payment fields, bind the request to the existing Safari session, and never submit forms. Require confirmation before sharing a private snippet aloud in a public mode or forwarding it elsewhere.
- **missing:** A durable per-page baseline/evidence store with semantic diff and retention controls; A pendant-to-browser request correlation path that can identify 'the page I mentioned' without replaying sensitive page contents to the relay; Working Safari extension heartbeat/recovery; currently GET /browser/status is online:false with two pending commands; A Mac bridge endpoint to save and retrieve encrypted evidence packets and expose a short spoken result


## Changes it proposed to its own stack

### `browser-harness` — Add a bridge self-healing supervisor with an explicit offline spool. When Safari stops heartbeating, mark the device unavailable, cancel/park pending browser jobs without 45-second request hangs, and have the Mac harness attempt a reversible recovery sequence (wake/open Safari, verify the AI Pendant extension is enabled, then wait for a heartbeat). Persist queued jobs with TTL, tab/session affinity, and the original intent; on reconnection resume only idempotent reads/watches, while surfacing any form-fill job as 'paused—review before continuing'. Emit a compact pendant notification and a Mac log receipt for offline, recovery-attempted, resumed, or expired states.
- **owner gets:** The owner stops losing minutes to silent browser failures and does not have to remember which private-page task vanished when Safari slept or the extension was disabled. Long-running private watches can recover overnight, while unfinished forms remain safely paused rather than being replayed blindly.
- effort: Medium: bridge health state machine, persistent spool, Mac-side Safari/extension recovery adapter, and integration tests for sleep/offline/reconnect and duplicate command IDs.  ·  risk: Opening or focusing Safari may be surprising; make that recovery policy configurable and log it. A network/session change can invalidate a page, so resumed reads must revalidate URL/title and discard stale tab affinity. Never auto-resume submit/send/purchase actions. If recovery fails, expire by TTL and report the exact parked job.
- cost: Negligible API cost; one small D1/SQLite record per queued job and occasional heartbeat/recovery metadata. No page content needs to leave the Mac during health handling.  ·  latency: Failed commands return immediately with a parked/offline state instead of waiting 45 seconds. Normal online commands add no meaningful latency; reconnect adds only the Safari wake/heartbeat interval.
- security: Keep session cookies and page contents in Safari; persist only intent, metadata, and hashes. Recovery must not broaden permissions or transmit credentials. Audit every resume/cancel transition.
- depends on: chg-14accc01 reliable browser command queue; A Mac-side Safari automation path that can wake/open Safari and inspect extension health; A durable per-device heartbeat and job state store


## What it asked for

_Nothing._
