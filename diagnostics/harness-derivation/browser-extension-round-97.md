# Harness derivation — browser-extension — round 97

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-bridge health 2026-08-07 round 97** — GET /browser/status reports Safari extension offline and home-chrome offline; pendingCommands=9. Persisted browser sessions still reference three tabs (time.is, Selenium web form, httpbin form), but no live extension device is reporting a tab. GET /browser/inspections is empty.
  - evidence: Authenticated GET /browser/status, /browser/sessions, and /browser/inspections in this round.

## Capabilities it proposed

### "“Read this private webpage to me, but hide passwords, codes, account numbers, and other sensitive details. Give me the useful answer through the pendant, and let me ask for one specific redacted detail only when I need it.”"
- **useful because:** Today an authenticated page can be inspected or summarized, but sensitive text risks entering prompts, logs, receipts, or spoken output, while a blanket redaction would make the answer unusable. This gives the owner a practical privacy-preserving way to use logged-in Safari pages from the pendant: useful content is spoken immediately, secrets stay on the Mac, and narrowly requested disclosures remain local and deliberate.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → relay
- **model tier:** Use a cheaper background/local extraction model on the Mac to classify and summarize page regions; use the realtime tier only for the owner's live spoken request and short response. Never send redacted values to the cloud model.
- **latency:** Initial page capture and local redaction under 1 second for ordinary pages; spoken response within 2–3 seconds. A specific local-only reveal can take up to 1 second.
- **cost:** Near-zero incremental API cost for extraction because it runs locally; one short realtime turn for the spoken interaction. Dominant cost is existing audio relay/TTS, not page analysis.
- **security:** Passwords, OTPs, tokens, hidden inputs, payment data, and configured private selectors must be redacted before any page text leaves the Mac. Store sensitive spans only in an encrypted, short-lived Mac-local vault keyed to tab/session and inspection ID. A requested reveal must resolve locally and never be written to relay logs, cloud prompts, receipts, or durable memory. The owner should be able to disable all reveals.
- **missing:** A Mac-local DOM-aware redaction and encrypted evidence vault; A typed browser result format carrying opaque sensitive-span tokens and safe quoted evidence; A local-only reveal operation bound to the current tab/session and owner request; Pendant response plumbing that can play the safe summary and accept a follow-up request

### "“If I’m looking at a private page, let me tap the pendant to get one sensitive field read back privately, without putting that field into the cloud, browser history, or action logs.”"
- **useful because:** The owner sometimes needs a single order number, access code, or account detail from a logged-in page while away from the screen. Today the system either exposes page text broadly to software or cannot safely provide the detail at all. A short-lived pendant-bound disclosure gives useful access without turning the browser into a secret-export channel.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → relay
- **model tier:** No model should interpret or retain the secret. The Mac performs deterministic local DOM extraction and selector/pattern matching; realtime handles only the spoken request and a confirmation-free acknowledgment, never the value.
- **latency:** Tap-to-result under 1.5 seconds while Safari is connected; if the tab or bridge is unavailable, fail clearly without queuing the secret request.
- **cost:** Negligible API/model cost; local extraction and one short audio response dominate. Small encrypted local cache, automatically erased after one successful playback or 60 seconds.
- **security:** Require physical pendant presence plus a fresh session-bound nonce, but do not make this a general action-approval gate. Resolve only one field from the currently bound tab, never arbitrary page text; mask the value in all logs and receipts; do not allow replay, relay-side caching, or transcription. The pendant should indicate when a sensitive value is being spoken, and the owner can disable the feature.
- **missing:** Pendant firmware support for a short-lived secure-presence nonce and private-disclosure indicator; A Mac-local browser resolver that maps an owner phrase or configured selector to exactly one sensitive field without sending its value to any model; An end-to-end encrypted, memory-only result channel from Mac to pendant audio; Redaction-aware receipts that record only field type, tab/session, and outcome


## Changes it proposed to its own stack

### `browser-harness` — Add a lease-aware Safari bridge recovery protocol. Every queued browser command gets a device lease, created/expiry timestamps, an action class (read, reversible edit, irreversible), and a cancel token. When extension heartbeats disappear, stop dispatching new commands and move in-flight work to suspended; on reconnect, discard expired or superseded commands (especially type/click), resume only idempotent reads against a verified tab/session, and emit a typed recovery receipt with the exact dropped/resumed command IDs and reason. Add a janitor for the currently observed stale queue (9 pending commands), plus GET diagnostics for heartbeat age, queue age histogram, and last successful tab attachment. Wire recovery receipts into the Mac bridge/pending pendant alert so the owner hears 'Safari returned; 2 reads resumed, 1 stale form fill discarded' instead of waiting through repeated 45-second timeouts.
- **owner gets:** Safari sleep, browser restarts, or laptop network changes will no longer cause old private-page actions to run unexpectedly when the session returns, nor silently lose a requested read. The owner gets a concise explanation and a trustworthy continuation of safe work.
- effort: Medium: extend browserBridge queue state and persistence, add heartbeat transition handling and janitor, typed receipts, and Mac/relay event plumbing; no extension UI change required beyond existing heartbeat.  ·  risk: A false disconnect or tab replacement could suspend useful work or discard an edit. Preserve the command and evidence in a dead-letter journal, expose explicit retry from the owner, and require tab/session identity plus URL match before resuming. Never auto-resume clicks/types after a lease break.
- cost: Negligible API cost; local JSON/D1 journal growth bounded with 30-day retention. No new hardware cost.  ·  latency: Adds a fast heartbeat/lease check; reconnect recovery is immediate for reads, while currently blocked commands stop waiting instead of consuming repeated 45-second timeouts.
- security: Improves safety for authenticated sessions by preventing stale commands from executing after reconnect. Receipts should contain hashes/URLs and action metadata, not page secrets or form values.
- depends on: chg-14accc01's existing request IDs, idempotency IDs, tab/session affinity, and journal; chg-16bc5dee's planned durable browser job runner for persistence and result streaming; mac-terminal's proposed cross-surface browser circuit-breaker/diagnostics

### `browser-harness` — Add a local-first sensitive-content boundary for authenticated Safari results. Before browser text, snapshots, or form evidence leave the Mac, run DOM-aware redaction for password/OTP/token fields, hidden inputs, credit-card/account-number patterns, and owner-configured selectors; replace values with stable opaque tokens while retaining local-only encrypted evidence keyed by inspection ID. Send the planner only the minimum quoted regions plus URL/title/timestamp and a redaction manifest. If an action needs a redacted value, resolve the token locally in the browser bridge without exposing it to relay logs or the language model, and record only a hash in receipts.
- **owner gets:** The owner can safely ask about private logged-in pages and prepare forms without passwords, one-time codes, or full account numbers being copied into cloud prompts, journal files, or spoken responses. They get useful answers while reducing accidental secret exposure.
- effort: Medium-high: DOM extraction/redaction library in browserBridge, encrypted local evidence store and token resolver, configurable selectors, and tests against page text/snapshot/form paths.  ·  risk: Over-redaction can make a page summary incomplete; under-redaction can leak a novel secret format. Default to conservative pattern/field redaction, show '[redacted]' markers, allow an explicit local-only inspection mode, and never synthesize or speak redacted values. If the local vault is unavailable, fail closed for sensitive fields but still return nonsensitive text.
- cost: Small local CPU/storage overhead; no additional model/API calls. Encrypted evidence retention should be capped (for example 7 days or per-job deletion).  ·  latency: Typically tens of milliseconds for DOM scan and regex classification; large snapshots may add under 200 ms locally, preferable to sending entire pages for model-side filtering.
- security: Strongly reduces secret exfiltration through relay, logs, receipts, and TTS. Requires OS keychain or an equivalent Mac-local key for the evidence vault, strict token scoping by tab/session, and audit events that contain no raw values.
- depends on: chg-14accc01's typed browser results and provenance IDs; chg-e14fff33's provenance-aware browser workbench (use hashes/locators, never raw secrets); An authenticated Safari extension/bridge extraction hook that can inspect DOM fields before serialization


## What it asked for

_Nothing._
