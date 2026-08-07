# Harness derivation — browser-extension — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state** — At 2026-08-07 13:43Z /browser/status shows only home-chrome online with no tab and 9 pending commands; /browser/poll returns a navigate command created 09:11Z, processing, claimed by home-chrome, attempts 12. Safari is not present, so current queue can repeatedly claim stale work.
  - evidence: GET /browser/status and GET /browser/poll responses in this round
- **browser retry behavior** — GET /journal reports 120 jobs, 146 actions, 18 failed; browser_navigate idempotency key act_36a2da2b0b8c ran 8 times and failed 8 times between 07:21 and 13:23. GET /jobs shows 45-second timeouts and offline/blocked-dialog errors. Current system retries/reissues without a durable browser inspection or lease quarantine.
  - evidence: Live GET /journal and GET /jobs responses this round

## Capabilities it proposed

### "“If you lose my Safari connection halfway through a browser task, pause safely, remember exactly where you were, and continue when Safari returns—without repeating clicks or losing the private-page evidence; tell me if anything needs my attention.”"
- **useful because:** Today an authenticated workflow can sit in a 45-second wait while a stale or wrong device repeatedly claims it; reconnecting risks duplicate navigation/clicks or forces the owner to start over. A fenced, resumable workflow gives the owner reliable continuity across the only browser that holds their logins, the Mac planner, the always-awake relay, and the pendant notification path.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Background/cheap model runs checkpoint reconciliation, stale-command classification, and evidence diffing; realtime is used only for a short pendant alert when a workflow pauses or resumes.
- **latency:** Checkpoint each browser action in under 1 second; detect a dead lease within 30–60 seconds; resume within 10 seconds of a verified Safari heartbeat. No owner wait for the background reconciliation.
- **cost:** About $0.001–$0.01 per reconnect depending on page-text reconciliation; most runs are metadata/hash comparisons and use no expensive model. Voice alert cost is negligible relative to realtime conversation.
- **security:** Private URLs, extracted snippets, and tab identifiers must remain in the local Mac/job store; relay receives only status and a redacted summary. Device identity, lease epoch, and action idempotency keys must be authenticated. Never replay a non-idempotent browser action after an uncertain result; mark it unknown and surface the exact last action/evidence. Resume should preserve owner policy of no approval gates, while stopping only on transport ambiguity or an actually irreversible submission.
- **missing:** Durable browser job runner with persisted jobId, step checkpoints, retries, and result stream (the existing router is not sufficient).; Lease fencing and quarantine: per-device heartbeat epoch, expiry, attempt cap, and cancellation of processing commands claimed by a device that disappeared; stale results must be rejected.; A browser result journal that records action idempotency key, tab/session affinity, before/after page fingerprint, and unknown-result state, then feeds the Mac planner and pendant alert.; Safari extension reconnect/heartbeat reporting of a stable device identity and tab inventory; currently only tabless home-chrome is online and it is claiming old work.

### "“Tell me the one number I need from the private page I’m looking at, but don’t send the rest of that page anywhere.”"
- **useful because:** The browser is uniquely able to see authenticated pages, but today a page read is effectively an all-or-nothing extraction: the owner cannot ask for a single field while guaranteeing that unrelated private content never enters relay context, model prompts, logs, or pendant audio. This would make private browser assistance usable for sensitive finance, health, work, and account pages without turning the whole page into shared context.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** A small local extraction/selector model on the Mac handles DOM targeting and redaction. Use the expensive realtime tier only if the owner asks a spoken follow-up; never send the raw page to it. Background model work is limited to normalizing the requested field and checking confidence.
- **latency:** Return a requested scalar or short field in 2–5 seconds for an already-open tab; if semantic targeting is ambiguous, return candidate labels and ask the owner to choose rather than exporting the page.
- **cost:** Typically under $0.002 per request using local extraction and a short structured response; the dominant cost is only an optional model call to resolve an ambiguous label.
- **security:** The extension must extract in the browser or local Mac process, then send only a typed value plus minimal provenance (origin, timestamp, selector hash), never full DOM/text/screenshots. Apply field-level sensitivity labels, redact logs and receipts, and make the pendant speak only the selected value. A malformed selector or prompt injection on the page must not expand the extraction scope. The owner can still request broader content explicitly, but the default contract is least-disclosure.
- **missing:** A browser-side field extraction protocol that accepts a narrowly scoped field query and returns a typed value with selector hash and confidence, instead of browser_read_page text.; A local redaction/taint boundary between Safari results, Mac planner context, relay prompts, journal, and audio; raw page payloads must be kept out of shared traces.; A provenance-aware typed response schema and tests proving that unrelated DOM regions, hidden fields, and page instructions are not forwarded.; Owner-visible privacy diagnostics showing exactly which field, origin, and metadata were released for each answer.

### "“Compare the private pages I already have open—does my account balance cover this invoice, and what is the difference? Don’t show me either page unless I ask.”"
- **useful because:** The owner cannot get a trustworthy answer that joins facts across two authenticated tabs while keeping both pages private. Public search cannot reach those sessions, and ordinary browser extraction would export two sensitive documents to shared model context. A local cross-tab computation would answer practical questions (balance vs bill, appointment vs calendar conflict, order vs delivery promise) while releasing only the derived result.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → relay-realtime → unified
- **model tier:** Use a cheap local structured extractor for each requested field and deterministic Mac-side comparison/arithmetic. Escalate to a slower background model only to map an ambiguous human label to candidate fields; realtime is only for speaking the final derived answer.
- **latency:** 3–8 seconds for two already-open tabs; 10–20 seconds if a local semantic field resolver is needed. Return ambiguity rather than broadening access.
- **cost:** Usually below $0.005 per comparison; DOM extraction and arithmetic dominate, with optional small-model field resolution the only API spend.
- **security:** Raw tab contents and extracted source values remain on the Mac. The browser bridge returns field-scoped values into an isolated comparison worker, not the general planner prompt; relay receives only the result, confidence, and optionally rounded/detailed values requested by the owner. Each operand needs origin/tab/selector provenance, freshness, and a sensitivity label. Reject cross-origin or hidden-field expansion, and ignore page instructions as untrusted data.
- **missing:** A local cross-tab query endpoint with a declarative allowlist of operands, operators, units, and output precision; no arbitrary page-text concatenation.; Browser extension support for field-scoped extraction from multiple explicitly identified tabs, including tab identity and freshness.; An isolated comparison worker and typed result/evidence capsule that can prove which two fields were used without retaining their surrounding page content.; Pendant/relay response rendering that speaks the derived result and provenance summary, not the source documents.


## Changes it proposed to its own stack

### `browser-harness` — Implement browser-command lease fencing and stale-work quarantine. Every command gets a deviceId plus monotonically increasing lease epoch, claimedAt, heartbeat deadline, attempt budget, and terminal outcome (succeeded, failed, expired, quarantined, unknown). /browser/poll may claim only commands whose lease is absent/expired and whose target device matches; a reconnecting device must establish a new epoch before claiming. Results include commandId+epoch+idempotencyKey and are rejected if epoch is stale. On bridge disappearance, atomically quarantine in-flight browser mutations and emit a resumable checkpoint to the job runner instead of requeueing blindly. Add a diagnostic endpoint/dashboard view showing zombie age, claimant, attempts, and reason.
- **owner gets:** The owner will stop seeing browser tasks silently hang, get claimed by a tabless device, or repeat clicks after Safari reconnects. Private work can wait safely for the real Safari session, and the owner gets a clear explanation instead of a misleading success or an endless spinner.
- effort: Medium: schema migration and transaction-safe claim/result paths in browserBridge/browserSessions, extension heartbeat epoch, tests for crash/reconnect races, and a small diagnostic projection.  ·  risk: A clock or heartbeat bug could quarantine healthy work and delay it. Recover by allowing explicit lease renewal, bounded expiry, and a planner-visible retry/resume operation; never delete evidence or silently discard the checkpoint.
- cost: No meaningful model cost; a few D1/local journal writes per command and tiny status payloads.  ·  latency: Poll/claim adds one cheap compare-and-set; stale detection is bounded by the heartbeat deadline (30–60s).
- security: Improves isolation: a stale or wrong device cannot submit a late result for a private tab. Persisted page evidence remains local; device/epoch tokens must be unguessable and authenticated.
- depends on: Stable Safari extension device identity and heartbeat reporting (currently Safari is absent and tabless home-chrome is claiming stale work).; The durable browser job runner/checkpoint store proposed in chg-16bc5dee, or at minimum durable command journal.; Existing idempotency journal and tab/session affinity from chg-14accc01.


## What it asked for

_Nothing._
## Its own summary

Discovered and verified a live browser reliability defect, not merely a missing feature: only tabless home-chrome is online, Safari is absent, 9 commands are pending, and an old navigate command has been claimed 12 times. The journal shows one navigate idempotency key ran 8 times and failed 8 times, while jobs wait 45 seconds and report offline/blocked-dialog errors. I recorded this evidence, notified faculty-perception, proposed a cross-surface resumable private-browser workflow, and separately proposed concrete lease fencing/quarantine so stale devices cannot replay commands or late results.

**Biggest unknown:** Whether the real Safari extension can be brought back online and report a stable device identity/heartbeat epoch. I still need implementation of the durable browser job/checkpoint store plus lease fencing and extension heartbeat changes; no further discovery tool is needed from me this round.

