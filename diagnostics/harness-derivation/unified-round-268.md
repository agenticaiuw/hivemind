# Harness derivation — unified — round 268

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device reachability** — Safari and the home Mac bridge are online; nRF9160 pendant is currently offline in the device registry, so pendant approval/notification behavior cannot be live-tested this round.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, and nrf9160-pendant offline (last seen 2026-08-09T02:56:31.366Z).

## Capabilities it proposed

### "“Before you send this, check the actual draft, recipients, attachments, and privacy risks, then let me approve it on the pendant.”"
- **useful because:** It prevents the most costly class of mistakes—sending the wrong private page, recipient, or attachment—while using the browser’s authenticated view and the pendant’s physical approval as a genuine cross-surface safety boundary.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Realtime for the short spoken explanation and confirmation-word readback; deterministic extraction/classification and background model for attachment and sensitive-data checks.
- **latency:** 3–8 seconds for inspection and risk summary; submission only after explicit pendant approval.
- **cost:** Roughly $0.01–$0.05 per review depending on attachment OCR/content length; browser inspection and deterministic checks dominate latency, not token cost.
- **security:** Only inspect the explicitly bound tab/session and user-selected draft; redact secrets and unrelated tabs before relay storage. Never transmit credentials or full private page contents to the relay. Submission, sending, or payment-like actions require physical_transaction_approval_latch approval and an expiring plan digest.
- **missing:** A typed outbound-message preflight schema that binds tab, recipient set, attachment hashes, and draft fingerprint; A production caller from browser inspection into the staged approval handoff; A durable relay implementation for the existing approval-handoff contract and a receipt that distinguishes inspected from actually submitted

### "“Show me exactly what would change across my Mac and logged-in browser before you do it, then apply that same plan only if I approve the preview.”"
- **useful because:** A single preview can expose effects that are invisible from either node alone: files the Mac would modify, the authenticated page state that would change, and downstream notifications. It turns risky multi-surface work into a reviewable diff rather than a spoken promise.
- **path:** mac-bridge → browser → relay → pendant
- **model tier:** Deterministic planners and filesystem/page fingerprints for the preview; a cheaper background model may summarize the diff. Realtime is used only to explain the result and collect the owner’s approval.
- **latency:** 5–15 seconds for a bounded preview; apply in the background with progress and a final receipt. Preview must never mutate state.
- **cost:** $0.01–$0.04 per preview; screenshot/DOM extraction and hashing dominate, while model summarization is optional.
- **security:** Bind the preview to exact paths, tab/session IDs, page fingerprints, and attachment hashes with a short expiry. Redact credentials and unrelated tabs. Revalidate every fingerprint immediately before applying; if anything moved, refuse rather than guessing. Require the physical transaction approval latch for irreversible or external effects.
- **missing:** A dry-run executor that produces typed before/after file and page diffs rather than prose; A shared cross-surface plan digest and revalidation endpoint; A dashboard/pendant presentation that can show a compact diff and tie approval to the exact digest

### "“Keep watch while I work: if this browser page or the matching Mac file changes underneath me, stop before I overwrite anything and tell me what conflicted.”"
- **useful because:** Authenticated web editors and local files can diverge while the owner is talking or walking away. This prevents silent stale overwrites by combining tab fingerprints, local file hashes, and the pendant’s immediate warning/approval path.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Deterministic hashes, version checks, and conflict classification; use the background model only to summarize non-sensitive diffs. No realtime model is needed unless the owner asks a spoken question.
- **latency:** Sub-second checks before each mutation and under 3 seconds to notify the owner; no polling faster than the editor’s practical cadence.
- **cost:** Near-zero model cost; browser heartbeats and local hashes are the main resource use. A model summary is under $0.01 per conflict.
- **security:** Bind each watch to one tab/session and one explicit local path; never scan unrelated files or send raw document contents to the relay. Store only hashes and bounded diff metadata. If a conflict is detected, freeze the staged action and require a fresh physical approval after re-previewing.
- **missing:** A cross-surface watch record with local-path and browser-tab bindings; A pre-mutation compare-and-swap guard for browser and Mac action executors; A compact pendant conflict alert and a re-preview flow that preserves the owner’s draft

### "“Let my trusted helper finish this one task, without giving them my browser session or credentials, and tell me exactly what they did.”"
- **useful because:** Today the system can act through the owner’s private browser but has no safe delegation boundary. A scoped handoff would let another person or model complete one bounded job without exposing the owner’s logged-in session, while the pendant remains the owner’s final consent device.
- **path:** relay → browser → mac-bridge → pendant
- **model tier:** Deterministic capability-token issuance, scope enforcement, expiry, and receipts; background model may translate the helper’s natural-language request into allowed steps, but cannot expand scope.
- **latency:** Under 2 seconds to issue or revoke a delegation; normal task latency thereafter.
- **cost:** Below $0.02 per delegated task excluding the actual model work. Token validation and receipts dominate neither cost nor latency.
- **security:** Use a one-task, one-session, one-origin capability token with expiry, nonce, allowed action types, and byte/page limits. Never export cookies, passwords, or raw unrelated page data. Require physical pendant approval to issue, narrow, or extend delegation; immediate revocation must work while the helper is active.
- **missing:** A relay-issued scoped delegation token and verifier in both browser and Mac executors; A helper-facing surface that cannot call arbitrary /execute or browser routes; A pendant approval payload and owner-visible live audit stream for delegated steps

### "“At 7 tonight, show me what will actually happen across my Mac, browser, and pendant before any routine runs, including anything that will need my approval.”"
- **useful because:** Routines today are schedules, not an understandable future execution. A time-travel preview would resolve the Mac timezone, enumerate current browser/session availability, predict queued alerts and approvals, and expose failures before the owner is surprised by them.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Deterministic schedule expansion, dependency checks, and action-risk classification; background model only summarizes the resulting execution graph.
- **latency:** Under 5 seconds for a bounded 24-hour preview; no action is dispatched by the preview.
- **cost:** Usually under $0.01; schedule expansion and health reads are local/relay work, with optional short model summarization.
- **security:** Preview must be read-only and must not fetch private page contents beyond the bound session metadata. Label America/New_York as the Mac execution zone, distinguish unknown pendant location, and mark every prediction with freshness and confidence. Approval requirements must be predictions, never silently satisfied.
- **missing:** A pure routine simulator that expands schedules into cross-surface action graphs without executing; A dependency/freshness snapshot for browser, Mac bridge, relay, and pendant availability; A durable preview identifier that can be revalidated at firing time and displayed on the pendant

### "“If you say you finished something but the real page or file does not match, find the discrepancy, stop retrying blindly, and tell me whether it was partial, rolled back, or never happened.”"
- **useful because:** A receipt is not proof of world state. Browser tabs can navigate, Mac apps can fail after dispatch, and a relay can lose the result. The owner needs a post-action truth check that separates completed, partially applied, externally changed, and unknown states before any retry can duplicate an effect.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Deterministic receipt correlation, idempotency checks, and read-only world reconciliation; use a background model only to phrase the discrepancy and suggest safe next steps.
- **latency:** Start within 2 seconds of a contradictory receipt; produce a bounded diagnosis within 10 seconds. Never auto-retry an unrepeatable action.
- **cost:** Under $0.02 for ordinary jobs; hashing, page fingerprints, and receipt joins dominate, with model use optional.
- **security:** Read only the paths, tabs, and external objects named by the action receipt. Preserve the original audit trail, redact private contents, and treat unknown state as a stop condition. Require fresh physical approval before any compensating action.
- **missing:** A postcondition contract on every Mac/browser action with typed observable evidence; A reconciliation engine that joins job receipts, browser results, and current world fingerprints; A user-facing partial/unknown state and compensation workflow that cannot masquerade as success


## What it asked for

_Nothing._
## Its own summary

This round I recorded three new cross-surface capabilities: (1) outbound-message preflight that inspects the exact authenticated draft, recipients, and attachments and requires physical pendant approval before sending; (2) a dry-run world diff spanning Mac files and browser state, with digest-bound approval and revalidation; and (3) conflict protection that detects browser/local-file changes before a stale overwrite. The extracted-fact erase proposal was correctly rejected as a duplicate of the existing owner-visible memory review/forget capability. I also confirmed Safari and the Mac bridge are online, while the nRF9160 pendant is offline, so pendant approval cannot be hardware-tested now.

**Biggest unknown:** The implementation boundary is now clear: I still need a typed cross-surface plan/diff contract, production wiring for the existing prepare/approve routes, and a relay-backed approval/delivery loop. I do not need another discovery round to propose these; the remaining blocker is implementation access and the pendant coming back online. The preview proposal is close to an existing backlog item, so it should be merged with that rather than kept as a second feature.

