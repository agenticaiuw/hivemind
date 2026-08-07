# Harness derivation — mac-planner — round 42

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner readiness** — Live Mac agent is not ready for accessibility/UI automation: Accessibility trusted=false and Screen Recording missing; browser extension home-chrome is offline with 2 pending commands, while relay and Mac bridge are online. mac_readonly_inspect is granted but currently has no implementation.
  - evidence: GET http://127.0.0.1:8000/ops/status returned HTTP 200 with ready:false, accessibility.trusted:false, screenRecording.granted:false, browser.online:false, pendingCommands:2, relay.macBridgeOnline:true; all three mac_readonly_inspect calls returned 'tool was granted a schema but has no implementation yet'.

## Capabilities it proposed

### "“Start this now; if anything can't run, keep the rest moving and tell me exactly what finished, what's waiting, and what I need to fix.”"
- **useful because:** Today a single spoken goal can stall on one offline browser tab or missing Mac permission, leaving the owner unsure whether anything happened. This capability turns the hive's partial reach into a dependable handoff: the relay coordinates, the Mac performs local work, the browser contributes authenticated data when its lease is live, and the pendant reports a concise completion or recovery brief.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the initial spoken clarification and short status utterances; use a cheaper background model to partition the goal, reconcile receipts, and generate the completion/recovery brief.
- **latency:** Acknowledge in under 1 second, begin runnable Mac work within 2 seconds, report blocked/queued partitions within 3 seconds, and continue retries in the background until a bounded deadline or reconnect.
- **cost:** Low-to-moderate per request: one short realtime turn plus a small background planning/summarization call; most cost is authenticated browser extraction or any generated audio, not coordination.
- **security:** Authenticated tab content remains in the browser-to-relay path only when needed and is redacted from generic status. Local file/app effects remain on the Mac. The owner has chosen maximum access, so no approval gate is introduced; high-impact effects must still be plainly named in receipts and never be reported as completed until a typed success is observed.
- **missing:** A shared cross-surface job/DAG schema with stable dependency and action IDs; Browser progress events and resumable polling instead of the current blocking wait; A Mac readiness/permission adapter and implementation of the granted read-only inspection tool; Relay continuation worker with bounded retry, lease epochs, and typed partial-completion receipts

### "“Use my private tabs and local files to answer this, but keep the raw contents on my Mac—send only the minimum redacted evidence needed, and show me what left the device.”"
- **useful because:** The owner can currently ask the hive to combine authenticated browser data, Mac files, and relay reasoning, but cannot reliably control or audit the privacy boundary. This would make private cross-surface assistance practical for sensitive work: the Mac/browser can inspect locally, the server can reason over minimized evidence, and the pendant can report the exact disclosure rather than forcing an all-or-nothing choice.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a local Mac-side model or deterministic redaction for classification, entity masking, and evidence selection; use the cheaper background model for synthesis over the redacted evidence. Reserve realtime only for the owner's spoken request and disclosure summary.
- **latency:** Local collection and redaction under 2 seconds for ordinary pages/files; synthesis and spoken summary within 5 seconds. Large documents should stream bounded evidence chunks rather than upload whole sources.
- **cost:** Low-to-moderate: local processing dominates latency, while server cost is limited to selected snippets and a compact synthesis call. No generated audio is needed except the brief spoken disclosure report.
- **security:** Raw page text, credentials, tokens, cookies, and unselected files must remain on the Mac/browser. Redaction must fail closed for uncertain secrets and preserve source hashes so evidence can be audited without retaining contents. The dashboard should show destination, fields/categories disclosed, source, timestamp, and retention; the owner can still choose maximum access explicitly, but the default must be minimized disclosure.
- **missing:** A Mac/browser-local evidence broker that can read selected tabs/files and redact before relay upload; A structured disclosure manifest and source-hash receipt shared by browser, Mac, relay, and dashboard; Secret/PII detection with configurable local-only rules and bounded evidence extraction; Relay APIs that accept evidence manifests and reject raw content outside an explicit owner-selected mode


## Changes it proposed to its own stack

### `integration` — Add a capability-aware execution handshake and partitioner before every multi-surface job. At dispatch, snapshot relay/Mac/browser leases and permissions, then split the plan into executable-now, retryable-when-online, and impossible-with-current-permissions steps. Execute the first partition immediately; persist the latter two with dependency edges and stable action IDs. Emit one typed progress stream and a final receipt that distinguishes completed, skipped-by-dependency, queued-for-retry, and never-attempted—without treating a missing browser or Accessibility permission as a 45-second timeout or silently leaving pending commands.
- **owner gets:** A spoken request can make useful progress even when Safari or Mac automation is unavailable, and the owner gets an honest answer immediately: what happened, what is waiting, and what would make it continue. It prevents duplicate clicks after reconnect and avoids the current confusing state where browser work waits 45 seconds while the pendant has no meaningful update.
- effort: Medium: readiness adapters for relay, Mac /ops/status, and browser lease; a DAG partitioner and durable continuation records; progress/receipt schema in relay and dashboard; reconnect worker and pendant status utterances.  ·  risk: A stale lease could misclassify a step as runnable; require a short lease epoch and recheck immediately before each side effect. If the Mac crashes, stable action IDs and existing receipts allow resume; if a dependency fails, mark descendants blocked rather than running them.
- cost: Low API cost: mostly local status checks and durable metadata; occasional background text summarization for the final receipt, using a cheaper model rather than realtime.  ·  latency: Adds roughly 100–300 ms preflight, but removes 45-second browser timeout waits and gives immediate partial results.
- security: Status and permission metadata stay local/relay-private; browser page contents are not copied during handshake. Continue honoring owner maximum-access policy—this is observability and scheduling, not an approval gate.
- depends on: Browser command progress/resumable polling (extends chg-14accc01); Mac action receipts (chg-5fc73ce3, already implemented); A durable relay continuation/job store

### `context` — Introduce a privacy-boundary evidence protocol: browser and Mac agents produce typed local evidence atoms (claim, source class, timestamp, confidence, sensitivity, source hash, expiry) and a disclosure manifest before anything reaches the relay. A local redaction/selection stage sends only approved atoms; the relay refuses unmanifested raw page/file payloads. Store the manifest and hashes, not raw sensitive content, so the dashboard and pendant can provide an auditable 'what left the Mac' receipt and later detect stale evidence.
- **owner gets:** The owner gets useful answers from private tabs and files without having to trust an invisible upload decision. They can understand exactly which facts were shared, use the answer later with freshness labels, and keep credentials and unrelated private material local.
- effort: High: define the evidence atom and manifest schemas, add local extraction/redaction in both browser bridge and Mac agent, enforce relay validation, add retention/expiry handling, and build a compact dashboard and spoken receipt.  ·  risk: Over-redaction can make answers incomplete; expose missing-evidence reasons and allow an explicit per-request broader disclosure mode. Under-redaction is the critical failure, so secret detection must fail closed and raw-payload rejection must be enforced server-side. Hash-only receipts can still leak equality patterns, so salt hashes per job.
- cost: Moderate engineering cost; low ongoing API cost because payloads are smaller. Local models or deterministic rules add CPU use but avoid repeated server processing of irrelevant content.  ·  latency: Adds roughly 0.5–2 seconds for local extraction/redaction; reduces relay transfer and synthesis time for large pages.
- security: Substantially improves data minimization and auditability. It introduces a new local policy engine that must be protected from prompt injection in page content and must never treat webpage instructions as disclosure authorization.
- depends on: A browser bridge that can return structured page regions rather than only raw extraction; Mac-local file/context readers with sensitivity classification; Relay request validation and durable manifest storage; Dashboard and pendant receipt rendering


## What it asked for

_Nothing._
