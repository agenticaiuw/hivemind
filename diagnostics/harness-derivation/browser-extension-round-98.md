# Harness derivation — browser-extension — round 98

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser continuity state** — Safari extension is currently offline with 9 pending browser commands, while three durable sessions remain persisted with stale tab IDs (default last used 06:26 UTC; probe-form sessions from 05:39–05:40). Browser inspections store is empty.
  - evidence: GET /browser/status returned online:false and pendingCommands:9; GET /browser/sessions returned default/probe-form/probe-form2; GET /browser/inspections returned inspections:[]

## Capabilities it proposed

### "Fill this logged-in form using my saved private details, but never reveal the sensitive values to the AI; tell me what fields will be completed and stop before submitting."
- **useful because:** Today an assistant can either expose sensitive values to model context or leave the owner to type them manually. This would let the owner use the browser’s existing authenticated autofill context while retaining a spoken, reviewable summary of which fields are populated and exactly where the irreversible boundary is.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the realtime tier only for the owner’s live request and concise spoken preview; use a cheaper background/local planner to map the form schema and validate field labels. The browser extension performs the secret-bearing field writes locally; the model receives field names, types, redacted hashes, and validation outcomes—not values.
- **latency:** Under 3 seconds for schema discovery and a field checklist; sensitive field filling should complete within 5 seconds, with the owner able to review or correct the checklist before any submit action.
- **cost:** One small local/background planning call plus the existing browser command round trips; roughly $0.01–$0.05 per form depending on schema complexity. Dominant cost is page extraction/planning, not secret handling.
- **security:** Passwords, payment numbers, government IDs, and other secret values must never be serialized into model prompts, relay audio, receipts, screenshots, or general logs. The extension needs a local-only autofill primitive that accepts a field classification and uses Safari’s credential/payment store or an owner-approved local vault. Require explicit owner confirmation immediately before submit, and record only redacted field metadata. A malicious page could mislabel fields, so show origin, field labels, and destination domain in the pendant/Mac preview.
- **missing:** A browser-extension local secret-field fill primitive with classification and redacted success/failure results; DOM-origin and destination-domain binding for each fill command; A review UI/audio protocol that summarizes populated field names without values; A submit-boundary checkpoint that is separate from reversible typing; A local secret-vault/autofill integration on Safari with no value export


## Changes it proposed to its own stack

### `browser-harness` — Add a privacy-preserving browser-to-fleet handoff envelope. After an authenticated Safari extraction, the browser harness emits only the requested fields (not raw DOM, cookies, or screenshots), each with tab/session id, URL, timestamp, locator/snippet hash, confidence, and an expiry. Sign it with a one-shot capability token scoped to the exact downstream operation (for example, create a reminder or draft text on the Mac); the Mac/relay can redeem it once, then it is invalidated. On extension reconnect, reconcile pending commands against these envelopes and mark stale tab-bound commands expired rather than replaying them.
- **owner gets:** The owner can ask the pendant about a private logged-in page and have the Mac follow up without silently copying an entire sensitive page into model context or accidentally replaying an old browser action after Safari was offline. Results remain evidence-backed and narrowly scoped while still enabling genuinely cross-device workflows.
- effort: Medium: extend browserBridge/browserSessions result schema and durable queue, add field-selection/redaction and token store, add Mac-side redemption plus reconnect reconciliation, and expose receipt events in the existing jobs/inspections dashboard.  ·  risk: A bad selector or overly broad field request could omit context or disclose more than intended; token loss could leave a job incomplete. Default to explicit requested-field manifests, short TTLs, hash-only provenance, and retry as a fresh read after expiry. Never replay a mutation from a stale envelope; existing receipt/undo remains available for reversible Mac actions.
- cost: Negligible API cost beyond the extraction/planner call already required; small D1/R2 metadata growth (roughly 1–3 KB per handoff, with TTL cleanup).  ·  latency: Adds about 10–30 ms for signing/storage and one local redemption round trip; no extra model call.
- security: Improves isolation: raw authenticated page content stays in the browser boundary, downstream receives least-privilege fields and an expiring one-use token. Still requires careful redaction of snippets and strict audit logging of redemption.
- depends on: chg-14accc01 reliable browser command queue and typed results; chg-e14fff33 provenance-aware browser workbench; existing POST /execute browser_* dispatch and POST /browser/result/:commandId; existing jobs/receipts and browser inspections storage

### `dashboard-ux` — Add a browser readiness/diagnostics surface that reports per registered device heartbeat age, tab availability, oldest pending-command age, poll/result round-trip latency, last extension error, and route-method compatibility (for example, distinguish a documented POST inspection route from an unsupported GET). Provide a cheap read-only canary and make /execute fail fast with a typed reason when no device/tab can service a command, instead of waiting for the 45-second browser result timeout.
- **owner gets:** When the owner asks about a private website, the pendant can immediately say whether Safari is reachable and whether a page is open, rather than appearing to ignore them or hanging for nearly a minute. It also prevents stale queued work from being mistaken for completed browser actions.
- effort: Small to medium: augment browser status/inspections diagnostics, add a non-mutating extension canary, classify queue failures, and surface the result in existing jobs/receipts and dashboard views.  ·  risk: A canary could reveal page metadata or create noise if implemented as navigation; keep it extension heartbeat-only and never inspect page contents. Diagnostics may expose URLs, so redact or hash URLs outside the owner dashboard and apply short retention.
- cost: No model/API cost; a few heartbeat and queue metadata writes, under 1 KB per device per event.  ·  latency: Reduces failed-task latency from up to 45 seconds to roughly 100 ms; healthy tasks gain only a small status lookup.
- security: Read-only health data should be scoped to the owner; URL/title details are sensitive and must not enter general model context. No new action authority.
- depends on: existing GET /browser/status and GET /browser/inspections; existing browserBridge 45-second waitForBrowserResult behavior; existing jobs/receipts and dashboard event storage

### `browser-harness` — Introduce a value-blind form protocol: the planner sends a signed manifest of expected field roles and origin (for example, shipping_address.city or payment.card_number), while Safari-side code resolves approved local autofill providers and performs the writes without returning values. Results contain only role, DOM locator hash, redacted validation state, and before/after presence bits. Reject manifests whose origin, frame, or field role changes after navigation; keep the final submit as a separate command that is never included in the fill batch.
- **owner gets:** They can complete tedious authenticated forms using information already stored on their Mac/browser without the AI learning or repeating secrets. The owner gets a clear spoken checklist and can still inspect and approve the final submission.
- effort: Medium: extension protocol and Safari autofill bridge, origin/frame binding, manifest signing, redacted result types, and a separate submit checkpoint in the existing command/receipt path.  ·  risk: Autofill could target a deceptive or changed field. Bind every command to the exact origin, frame tree, field-role hash, and short-lived tab session; fail closed on mismatch and require a fresh read. Recovery is an owner-visible incomplete-fill receipt, never an automatic retry against changed DOM.
- cost: No additional model call during filling; modest local metadata storage, under 2 KB per form. Safari credential/payment APIs may require platform entitlement work rather than API spend.  ·  latency: One schema/manifest planning round, then local field writes in tens to hundreds of milliseconds; avoids round-tripping each secret field through the model.
- security: Sensitive values remain inside Safari/local vault boundaries and are excluded from prompts, relay payloads, screenshots, logs, and receipts. This is stronger than merely redacting extracted text because the model never receives the value at all.
- depends on: Safari extension implementation access to local autofill/credential APIs; signed browser command envelopes with tab/origin binding; typed redacted browser result schema; separate irreversible-submit command and owner review surface


## What it asked for

_Nothing._
## Its own summary

Discovered live browser state: Safari is offline, 9 commands are pending, and three persisted sessions reference stale tabs; inspections are empty. I recorded this finding and proposed two new improvements: (1) least-privilege, field-level browser→Mac handoff envelopes with provenance and one-shot expiring capability tokens, plus stale-command reconciliation; (2) browser readiness diagnostics and a fast-fail canary exposing heartbeat/tab/queue health instead of a 45-second timeout. I also notified mac-planner so its deferred-job scheduler can align with browser reconnect behavior.

**Biggest unknown:** The granted browser enqueue tools are still schemas/stubs, so I cannot perform a real authenticated-page read or validate reconnect behavior. The owner’s first private browser workflow and sensitivity preferences also remain unavailable; until those arrive, proposed field manifests and redaction defaults cannot be tuned to a real account.

