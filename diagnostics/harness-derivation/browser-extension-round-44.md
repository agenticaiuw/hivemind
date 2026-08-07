# Harness derivation — browser-extension — round 44

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — As of live ops status, Mac agent and relay are online, but browser extension is offline; Safari is not registered, only never-seen home-chrome exists with zero tabs, and 3 commands are pending. Safari automation permission is granted, but browser work cannot run until the extension heartbeats.
  - evidence: GET /ops/status HTTP 200: browser.online=false, devices=[home-chrome tabCount 0], pendingCommands=3; automation.Safari granted.

## Capabilities it proposed

### "When you reach a passkey, two-factor prompt, CAPTCHA, or other human verification while handling something in my logged-in browser, tell me exactly what to do on the pendant, let me complete that step, then resume the same task in the same tab without losing the draft or context."
- **useful because:** Many of the owner's private accounts cannot be used end-to-end by automation today because authentication challenges interrupt the browser session. This would let the owner supply only the human-bound proof while the browser, Mac, relay, and pendant preserve and continue the useful work instead of abandoning it or asking the owner to start over.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a background/cheap model to maintain the task state and identify the challenge type; use realtime only for the short, low-latency pendant interaction and spoken instructions. Never send credentials, passkeys, or one-time codes to the model.
- **latency:** Challenge detection should pause within 1–2 seconds; the pendant instruction should respond conversationally within 500 ms; after the owner completes the challenge, resume in under 3 seconds and verify the tab/session before continuing.
- **cost:** Usually below $0.01 per challenge, dominated by a few realtime spoken turns; routine state tracking and page classification should use the cheaper tier. No external CAPTCHA-solving or credential-processing API.
- **security:** The system must not read, store, transcribe, or relay OTPs, passkeys, biometric data, or CAPTCHA answers. Detect challenge surfaces locally where possible, show the originating domain and requested action, require the owner to perform the proof directly in Safari, and cryptographically bind the resume token to the same device, tab, URL origin, and short expiry. Any changed destination or irreversible action must be surfaced before continuing.
- **missing:** Browser challenge detection with an explicit paused-task state; A secure browser-to-pendant resume handshake bound to tab/device/origin and expiry; Extension UI or protocol for reporting challenge kind without extracting secrets; Relay task state that survives the browser extension disconnecting briefly; A clear owner-facing review step when authentication changes the page or transaction


## Changes it proposed to its own stack

### `browser-harness` — Add browser-device lease and queue recovery: each command records target extension/device, tab affinity, idempotency class, enqueue/expiry timestamps, and attempt count; reject or cancel commands whose device lease is offline, purge/mark the three currently pending orphan commands, retry only idempotent reads after a reconnect, and return a typed 'browser unavailable / waiting for Safari' status instead of holding a 45-second request open. On extension heartbeat, perform a handshake that reports tabs and claims only commands for that device; never silently replay clicks/types/submits.
- **owner gets:** When Safari sleeps, closes, or loses its extension connection, the owner gets an immediate honest status rather than a timeout or an old click replayed into a new tab. When it reconnects, safe page reads resume automatically while form edits remain explicitly pending, so private browser tasks survive ordinary laptop sleep without risking duplicate actions.
- effort: Medium: browserBridge queue schema/state machine, heartbeat lease and reconnect handshake in the extension, stale-command migration, typed API receipts, and tests for sleep/reconnect/tab replacement.  ·  risk: A reconnect could still target the wrong tab if affinity is weak; require extension-reported tabId plus URL/title fingerprint and invalidate on mismatch. Reads may be repeated, so label timestamps/attempts. Mutations are never auto-retried and are recoverable from the pending review queue.
- cost: Negligible API cost; small D1/SQLite queue metadata and heartbeat traffic. No new hardware.  ·  latency: Offline requests return in milliseconds instead of waiting 45s; reconnect adds one heartbeat round trip before safe reads resume.
- security: Improves safety by binding commands to a leased device/tab and preventing stale mutation replay. Keep URLs, extracted content, and drafts encrypted/retained only under existing browser-session policy.
- depends on: A working Safari extension heartbeat/result path and stable device identity; Durable browser job runner (chg-16bc5dee); Typed browser receipts/tab affinity (chg-14accc01)

### `browser-harness` — Add a local field-aware privacy firewall between Safari and every model/surface: classify DOM fields and accessibility values as credentials, authentication factors, payment data, personal identifiers, or ordinary task content; redact secret values before page text, screenshots, logs, receipts, and relay payloads leave the Mac; expose only typed facts such as 'payment method ending 42' or 'verification required'. Permit an owner-selected, short-lived reveal of one non-secret field to one task, with automatic erasure.
- **owner gets:** The owner could finally ask the system to work inside sensitive logged-in sites without turning every page read into a copy of passwords, full card numbers, recovery codes, or private identifiers in model context and activity logs. Tasks that need billing or identity facts would still work through safe summaries rather than requiring the owner to avoid browser automation entirely.
- effort: High: local DOM/accessibility classifier, screenshot redaction before upload, field metadata propagated through browser results and receipts, redacted logging, task-scoped reveal tokens, and adversarial tests across common login/payment forms.  ·  risk: A classifier can miss an unusual secret field or over-redact useful content. Default to conservative redaction, allow local-only extraction for uncertain fields, show a redaction report, and make the task fail visibly rather than transmitting uncertain values. Never permit model-side unredaction.
- cost: Moderate local CPU and storage overhead; roughly one small classification pass per page or screenshot. No third-party API is required, and redaction should reduce token and vision-upload costs.  ·  latency: Adds approximately 100–500 ms for a page extraction and up to a second for screenshot redaction, but avoids round trips and should reduce downstream model context.
- security: Meaningfully reduces secret exfiltration to relay/model/logs. The classifier and redaction code become a high-value security boundary and need local tests, versioned policies, audit receipts, and strict origin/task scoping.
- depends on: Browser extraction and screenshot result typing; A local-only secret/PII classifier and redaction library; Relay and activity-log support for redacted payloads and retention metadata; Owner-visible indication of what was withheld


## What it asked for

_Nothing._
