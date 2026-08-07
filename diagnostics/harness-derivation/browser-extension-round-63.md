# Harness derivation — browser-extension — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — At round 63, /browser/status reports only the home-chrome registration online with no tab (tabId null, tabCount null) and 5 pending commands; /browser/sessions contains three persisted sessions pointing at stale Safari tabs, last used around 06:26.
  - evidence: GET /browser/status and GET /browser/sessions responses in this round

## Capabilities it proposed

### "“Use the right account for this website, and tell me if Safari is signed into a different one before you do anything consequential.”"
- **useful because:** People routinely keep personal, work, and family accounts open in the same browser. Today the system can read and fill an authenticated page, but it cannot reliably establish which identity a tab represents or prevent a task from silently landing in the wrong account. This would make delegated browser work trustworthy without requiring the owner to remember which tab is which.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background classifier/ruleset to extract account-identity evidence from page chrome and session metadata; use the realtime tier only to explain an ambiguity in the owner's voice conversation. The browser extension supplies page evidence, the Mac planner correlates tabs and task entities, and the relay stores a compact account-alias registry.
- **latency:** Identity checks should add less than 2 seconds to a normal browser task; an ambiguous identity can be reported immediately and resolved conversationally before the task continues.
- **cost:** Usually near-zero model cost for DOM labels, URL/domain, and cached aliases; roughly $0.001–$0.01 only when an ambiguous page needs model interpretation. Storage and extraction dominate operational cost, not inference.
- **security:** Account labels are sensitive metadata. Keep only owner-defined aliases and redacted evidence hashes, never passwords, cookies, or full page bodies. The system must report uncertainty rather than infer an identity from an email address alone. For a high-impact action, surface the selected account and evidence in the existing review/receipt record; do not silently switch accounts.
- **missing:** An extension/page extractor that recognizes login identity indicators (account menu, avatar label, organization/workspace) and returns locator plus evidence hash; A durable per-domain account-alias registry with expiry and an explicit 'unknown' state; A cross-tab identity consistency check integrated into browser job planning and receipts; A pendant-friendly account-selection/status card in the dashboard


## Changes it proposed to its own stack

### `browser-harness` — Add a durable cross-surface transaction ledger for browser jobs. Persist each planned step with a stable idempotency key, input hash, target device/session/tab, precondition snapshot hash, status (pending/running/completed/uncertain), result receipt, and resume cursor. On restart or extension reconnect, resume only from the first incomplete step; completed steps are skipped after receipt/hash verification, while uncertain browser mutations are quarantined for re-read rather than replayed. Rebind stale tabs only after URL/title/session validation, and expose a recovery endpoint/UI showing the next safe step and why.
- **owner gets:** If Wi-Fi, Safari, or the Mac drops halfway through a logged-in task, the owner can say “continue” without duplicate form fills, repeated purchases, or losing the work already done. They get an honest recovery state instead of an apparently finished job or a dangerous replay.
- effort: Medium-high: SQLite/D1-backed ledger schema, atomic step transitions, recovery worker, session/tab revalidation, and job status/receipt UI; roughly 1–2 weeks including crash/reconnect tests.  ·  risk: A crash between the real browser mutation and recording its receipt can leave a step uncertain; never replay uncertain mutations automatically—perform a read-only verification or mark it for owner review. Ledger corruption recovers from append-only events and the existing job receipt/undo records.
- cost: Negligible storage (about 1–4 KB per step plus bounded receipts); background retries use cheap model/rules, with expensive reasoning only for ambiguous recovery. No new per-action API call when healthy.  ·  latency: Healthy jobs add under 10 ms per step for ledger writes; reconnect recovery may add one browser read per uncertain step.
- security: Ledger contains URLs, hashes, and potentially sensitive result metadata; encrypt at rest, redact field values by default, apply short retention, and never persist page bodies or credentials. Device/session binding prevents accidentally continuing in the wrong logged-in account.
- depends on: Durable browser job runner (chg-16bc5dee); Reliable browser command queue with request IDs and tab/session affinity (chg-14accc01); Existing action receipts/undo storage (chg-5fc73ce3)

### `browser-harness` — Implement an account-identity attestation layer between browser extraction and job execution. For each browser session, periodically extract only identity-bearing UI metadata (domain, workspace/organization label, masked account name, locator, timestamp), normalize it into a durable alias with confidence and expiry, and attach the attestation ID to every planned browser step and receipt. Before any consequential navigation/fill/click, compare the task's intended account alias with the current tab attestation; if absent or changed, pause the job as 'identity unknown' and send the pendant a concise account-choice prompt. Never infer identity from a URL alone, and never auto-switch accounts.
- **owner gets:** The owner can delegate work across personal and work accounts without accidentally editing the wrong tenant, inbox, or subscription. They get an actionable warning tied to the exact tab and account evidence instead of discovering the mistake after submission.
- effort: Medium: extension extractor and evidence-hash protocol, alias store with TTL, planner precondition hook, pendant prompt payload, and receipt/dashboard display; about 1–2 weeks.  ·  risk: Some sites hide identity labels or render them dynamically, producing false 'unknown' states; recovery is a read-only re-extraction or explicit owner selection. A compromised page could spoof text, so treat attestation as evidence with confidence—not cryptographic proof—and never store secrets.
- cost: Small bounded metadata storage (hundreds of bytes per session/attestation); mostly deterministic extraction, with occasional cheap model fallback for unfamiliar layouts.  ·  latency: One lightweight extraction at session start and before consequential steps, typically under 500 ms; ambiguity adds a human-response delay only when needed.
- security: Improves cross-account safety while minimizing exposure: store masked labels and hashes, encrypt the alias registry, apply short TTLs, and make account identity visible in action receipts. It does not grant new browser permissions.
- depends on: Authenticated browser sessions and browser_* execution through POST /execute; A new durable account-alias/attestation store; A planner precondition hook that can pause and resume a job; A pendant/dashboard message type for account selection


## What it asked for

_Nothing._
## Its own summary

Discovered a concrete gap beyond the existing durable-runner proposals: jobs still need a crash-safe cross-surface transaction ledger with per-step idempotency, receipts, precondition hashes, and a resume cursor. I proposed it for the browser harness and informed mac-planner. Live state is degraded: only the tabless home-chrome registration is online, five browser commands are pending, and the persisted Safari sessions are stale. I still need a functioning command enqueue implementation plus a reliable Safari heartbeat/tab reattachment path before authenticated browser work can be exercised; I did not re-request the already-denied tool/context grants.

**Biggest unknown:** Whether the five pending commands are stale/replayable or belong to a disconnected Safari session, and why Safari stopped reporting while its sessions remain persisted.

