# Harness derivation — browser-extension — round 107

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension** — Safari is currently offline with tabCount 0 and 10 pending commands; browser sessions remain stale records for time.is and test forms, so no authenticated page read is currently trustworthy.
  - evidence: GET /browser/status returned online:false, only home-chrome offline, pendingCommands:10; GET /browser/sessions returned stale lastUsedAt entries from 2026-08-07 06:26.

## Capabilities it proposed

### "Tell me on the pendant when one of my watched private websites has logged me out, hit a CAPTCHA, or needs a consent step, and give me a link to fix it; don’t silently treat the watch as unchanged."
- **useful because:** Authenticated browser automation currently fails ambiguously when Safari is offline, a tab disappears, or a login expires. A liveness/reauthentication capability distinguishes “nothing changed” from “we could not inspect the page,” preventing missed work and giving the owner a timely, actionable recovery path through the one device that can restore the session.
- **path:** browser-extension → relay-realtime → mac-planner → unified
- **model tier:** Use deterministic browser/session checks first (HTTP/status, tab identity, login markers, CAPTCHA/consent heuristics). Use a cheaper background model only to classify ambiguous page states and generate a one-line explanation; realtime is reserved for the pendant alert.
- **latency:** Evaluate on each scheduled watch run and on extension heartbeat; alert within one run (normally under 1 minute after detection). Recovery link should be available immediately, while re-check waits for the next heartbeat.
- **cost:** Near-zero for status, URL, and DOM marker checks; roughly $0.001–$0.01 only for ambiguous page-state classification. Storage is a small per-watch state record and event history.
- **security:** Login pages and CAPTCHA text are sensitive. Store only state class, site hostname, timestamp, and a short redacted diagnostic—not credentials or screenshots by default. Never attempt to bypass CAPTCHA or MFA; direct the owner to the existing Safari tab. Alerts must not read private page contents aloud unless requested.
- **missing:** A typed browser health result distinguishing offline, missing tab, session expired, CAPTCHA/MFA, consent interstitial, and successful inspection; Per-watch liveness state with last-good timestamp and explicit unknown/error status, rather than treating failed reads as no-change; A reconnect/reauth alert route to the pendant and a safe resume operation after the owner restores the session; Tests covering Safari extension disappearance and stale queued commands

### "When I say “stamp this page,” create a tamper-evident receipt of the exact authenticated webpage state I’m seeing—selected text, URL, timestamp, and a screenshot or DOM hash—so I can later prove what the site showed me without exposing my login or storing the whole page in the cloud."
- **useful because:** The owner cannot today establish a trustworthy record of what a private portal, price, appointment, policy, or account page displayed at a particular moment. A signed, user-triggered browser receipt would support disputes and personal records while preserving the distinction between evidence captured from Safari and later AI summaries.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** No expensive model is needed for capture or verification. Use deterministic local hashing/signing on the Mac and a cheap background model only if the owner requests a human-readable label or summary; realtime handles the short pendant command and receipt ID.
- **latency:** Capture and sign in under 2 seconds; spoken confirmation within 3 seconds. Verification should be local and near-instant, with relay timestamp lookup only when the owner wants an externally anchored timestamp.
- **cost:** Low per invocation: hashes and signatures are local; storage is proportional to optional screenshots. A small relay/database cost covers timestamp anchors and receipt metadata. Model cost is optional and near zero by default.
- **security:** Never capture cookies, password fields, hidden form values, or unrelated tabs. Encrypt the optional screenshot locally; default to selected text plus URL/title and a cryptographic DOM/screenshot hash. Keep private content out of relay logs; expose only receipt ID, hash, timestamp, and user-chosen redacted excerpt. Sharing a receipt must be an explicit separate owner action.
- **missing:** A browser capture command that returns active-tab selection, URL/title, sanitized visible DOM or screenshot, and excludes credential fields; A Mac-held device signing key and receipt format with canonicalization rules so the same page state verifies consistently; A relay timestamp-anchor endpoint and immutable receipt lookup/export; A pendant command/result flow for receipt creation, later verification, deletion, and optional redacted sharing; Verification tooling that reports changed, authentic, incomplete, or unverifiable rather than a misleading boolean


## Changes it proposed to its own stack

### `browser-harness` — Add a BrowserObservation health envelope and per-watch state machine. Every poll/result cycle must emit one of inspected, no_tab, extension_offline, stale_session, auth_interstitial, captcha_or_mfa, or command_expired with observedAt, lastGoodAt, deviceId, tabId, and sessionId. A failed observation must never update the semantic page baseline as if unchanged. Coalesce repeated failures, create one resumable recovery event, and reconcile pending commands by lease/epoch when Safari returns.
- **owner gets:** The owner will know whether a quiet private page is truly unchanged or simply unreachable, and will receive one clear recovery prompt instead of repeated or false completions after reconnect.
- effort: Medium: browserBridge/browserSessions state changes, route schema, watch scheduler integration, and extension reconnect tests.  ·  risk: Existing consumers may assume a boolean success/no-change result; version the envelope and preserve legacy fields. On crash, replay only leased-but-unacknowledged observations and deduplicate by commandId/epoch.
- cost: Negligible compute/storage; no model call for deterministic states. A small event record per watch and bounded coalescing window.  ·  latency: Adds a few milliseconds to command bookkeeping; alerts wait for the next heartbeat or watch interval.
- security: Persist only host/state/timestamps and IDs by default; do not retain CAPTCHA screenshots or page text. Recovery URLs should target the existing tab and never include credentials.
- depends on: A durable page-watch scheduler (chg-e767dfc0 or equivalent); A reconnect-safe command lease/idempotency layer (chg-14accc01 / current mac-planner envelope); Pendant notification delivery through pipeline events


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: “stamp this page,” producing a tamper-evident, device-signed receipt of an authenticated Safari page state with optional encrypted local evidence, relay timestamp anchoring, and pendant verification. It requires sanitized browser capture, Mac signing, immutable receipt lookup, and explicit sharing controls.

**Biggest unknown:** Whether the owner values evidentiary page receipts enough to justify device-key provisioning and encrypted local screenshot storage.

