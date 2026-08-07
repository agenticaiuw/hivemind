# Harness derivation — browser-extension — round 21

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — Safari extension is currently offline with no tab and no pending commands; status exposes only stale fanout-probe-cleanup registration. There is no attach/list-tabs route, so recovery must happen through Mac-side watchdog or extension startup.
  - evidence: GET /browser/status returned online:false, tabId:null, tabCount:null, pendingCommands:0 at live probe.

## Capabilities it proposed

### "“Check whether the appointment or reservation in my logged-in website still matches my calendar, and tell me only if something conflicts or changed.”"
- **useful because:** Today the Mac can read local calendar data and the browser can reach a private website, but nothing reliably joins those two sources while preserving the website's session privacy. This would catch changed times, cancellations, locations, or missing confirmations without making the owner manually compare tabs.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use the background/cheaper model for scheduled or on-demand comparison after the browser extracts only the relevant event fields; use realtime only when the owner asks verbally and needs an immediate spoken answer. The Mac performs normalization and conflict detection; the relay coordinates and the pendant delivers the result.
- **latency:** Healthy bridge: 10–20 seconds for one or two authenticated page reads plus local calendar lookup. If Safari is asleep or offline, retain the request and notify the pendant when the bridge returns rather than spending 45 seconds timing out.
- **cost:** Roughly $0.01–$0.05 per comparison depending on page extraction and model use; browser interaction and model summarization dominate, while calendar lookup and field comparison are local and nearly free.
- **security:** Raw page content and calendar details should remain on the Mac wherever possible. Send the relay only normalized fields needed for the comparison and a short result, with source URL, timestamp, and freshness. Never alter either site or calendar automatically; adding or changing an event requires explicit owner instruction. Login redirects, CAPTCHA pages, stale cached pages, and ambiguous dates must be reported rather than treated as agreement.
- **missing:** A reliable Safari bridge lease and command path that can recover from sleep/restart; A local calendar read/normalization adapter exposed to the browser job runner; A field-level privacy filter and comparison schema for date, time zone, location, status, and participant; A durable cross-source comparison job with freshness timestamps and a pendant notification when a deferred check completes

### "“Save the important parts of this private webpage so I can ask about it later, but keep the original page and sensitive details on my Mac.”"
- **useful because:** The owner can currently read a logged-in page or create a normal note, but cannot make a durable, privacy-preserving handoff from Safari to the pendant. This would turn a fleeting authenticated page into a searchable local reference without copying an entire private webpage into the cloud or losing where each fact came from.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** The browser extracts only the owner-selected region; a cheaper background model produces a compact summary and fact index on the Mac. Realtime is used only when the owner immediately asks a follow-up through the pendant. Relay stores an opaque reference and notification, not page contents.
- **latency:** 5–15 seconds for extraction, local summarization, encryption, and an acknowledgement. Follow-up questions should answer in under 5 seconds when the Mac is reachable; otherwise the pendant should say the private reference is unavailable rather than upload it.
- **cost:** About $0.005–$0.03 per saved page when model summarization is used; the dominant cost is text extraction/summarization. Local encrypted storage and relay metadata are negligible.
- **security:** Require an explicit selection or spoken 'save this' tied to the active tab; never silently archive whole pages. Store original excerpt, URL, timestamp, and source hash in an encrypted Mac vault, with only a random reference and redacted title in the relay. Respect the owner's destructive-action policy for deletion, support immediate purge, and avoid retaining credentials, payment data, or hidden DOM fields. Dashboard should show exactly what was retained.
- **missing:** A local encrypted private-reference vault with per-item deletion and retention expiry; Browser extraction that returns the selected DOM region plus stable source metadata, excluding hidden fields; A relay protocol for opaque references and deferred pendant notifications; A local retrieval/summarization route that can answer against the vault without sending the original excerpt to the cloud


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge self-healing supervisor spanning Mac agent, Safari extension, relay, and pendant: maintain a signed device lease with heartbeat age and a tiny poll/result canary; when the lease expires, the Mac supervisor launches or foregrounds Safari and opens a neutral bootstrap URL, waits for the extension to re-register, then runs the canary before releasing queued browser jobs. If recovery fails, relay retains the job with bounded retry/backoff and the pendant receives one concise offline status rather than repeated timeouts. Purge stale extension registrations after a TTL and never copy cookies, page text, or session identifiers into the health telemetry.
- **owner gets:** Browser tasks would stop failing mysteriously after Safari sleeps, updates, or the extension restarts. The owner could ask from the pendant and trust that authenticated work resumes when the Mac is available, without manually opening a tab or debugging a dead bridge.
- effort: Medium: Safari extension startup/heartbeat changes, a Mac LaunchAgent or agent supervisor, relay lease state and retry queue, plus an observable health/repair event in the dashboard. Requires careful testing across sleep/wake and Safari relaunch.  ·  risk: Safari may open an unwanted tab or repeatedly relaunch during an actual user session; cap repairs, use a neutral local/start URL, and expose a disable switch. Never auto-submit browser actions: queued jobs resume only after canary success and preserve their existing irreversible-action stop. On failure, mark the job paused and provide a receipt.
- cost: Negligible API cost: health canary is local HTTP and relay state is a few D1/R2 bytes per lease/job. Small Mac CPU/network overhead only during stale-heartbeat recovery.  ·  latency: Adds roughly 1–3 seconds to a job after a healthy bridge; recovery after sleep/restart may take 5–15 seconds, but avoids the current 45-second command timeout.
- security: Improves availability without expanding page access. Telemetry should contain device ID, lease age, and canary outcome only; bootstrap must not navigate to arbitrary owner URLs. Existing Safari login/cookies remain entirely in Safari.
- depends on: A functioning extension poll/result implementation and a Mac-side process permitted to launch/foreground Safari; A durable browser job state/lease record in the relay; A neutral bootstrap URL and explicit stale-device TTL policy


## What it asked for

_Nothing._
