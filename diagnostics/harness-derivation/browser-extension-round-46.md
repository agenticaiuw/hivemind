# Harness derivation — browser-extension — round 46

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser transport** — As of this round the live browser service is still offline: Safari is not registered, home-chrome has no tab, and 3 commands are pending. The Mac bridge itself is online, so the failure is specifically extension heartbeat/enqueue/result transport rather than total Mac reachability.
  - evidence: GET /browser/status returned online:false, devices:[home-chrome tabId:null tabCount:null], pendingCommands:3; GET /ops/status reported macBridgeOnline:true.

## Capabilities it proposed

### "“Save this private page for later, remember where I stopped, and when I say ‘continue that’ from the pendant, reopen it and tell me what changed since then.”"
- **useful because:** The owner can turn a fleeting authenticated browser session into a durable, voice-addressable thread without copying URLs or sensitive page contents into chat. It combines private Safari access, the always-awake relay, Mac execution, and the pendant as a low-friction resume control; no single node can provide this continuity.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use the realtime model only for the short voice intent and spoken confirmation; use a cheaper background model to normalize the page fingerprint, summarize differences, and maintain the resume record.
- **latency:** Acknowledge the pendant command in under 2 seconds; reopen and produce the delta in 5–15 seconds, depending on Safari and page load. If the Mac is offline, relay queues the resume job and reports that state.
- **cost:** Roughly $0.01–$0.05 per resume depending on extracted page size; realtime audio tokens dominate the immediate interaction, while background summarization is the larger variable cost for long pages.
- **security:** Private page text must remain scoped to the owner and should be retained as a short-lived encrypted fingerprint plus a small cited excerpt, not a full page archive. The resume record needs URL, tab affinity, scroll/selection locator, timestamp, and sensitivity label. Reopening is reversible; never submit forms or send messages as part of resume. Require explicit confirmation only if a later voice request tries to mutate the page.
- **missing:** A working browser command enqueue implementation and a live Safari heartbeat (current browser status is offline with 3 pending commands); A durable browser resume-record schema with locator fallback (URL, tab/session id, semantic anchor, scroll position, baseline fingerprint); A relay job type that can survive Mac/browser disconnection and deliver a concise spoken completion receipt; Dashboard controls to inspect, expire, or delete saved private-page resume records

### "“Explain this logged-in page, but keep anything private that isn’t relevant on my Mac.”"
- **useful because:** Today authenticated browser assistance either cannot run because transport is offline or risks sending an entire private page to a cloud model. This gives the owner useful answers from private pages while minimizing disclosure: the browser captures the page, the Mac performs local relevance filtering and redaction, and the relay receives only the question and approved excerpts with local citations. The pendant provides the natural spoken request and receives the answer.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Use a small local Mac extraction/redaction model or deterministic DOM/PII filters first; use the expensive realtime model only to interpret the short spoken request and speak the final answer. Use a cheaper background model for long-page synthesis when needed.
- **latency:** A short page should answer in 3–8 seconds; large pages may take 15 seconds. The pendant should immediately say that local filtering is in progress rather than waiting silently.
- **cost:** About $0.005–$0.03 per request; local extraction is effectively free, and cloud cost is dominated by the small, relevance-filtered excerpt rather than the full page.
- **security:** Sensitive text must be filtered before leaving the Mac, with a visible audit showing what excerpts were shared and why. Redaction must cover credentials, payment details, health data, and unrelated account content, while preserving source locators locally for citations. The owner must be able to choose local-only mode, inspect/delete the temporary page cache, and disable cloud synthesis. Never infer that a redaction is perfect; if relevance classification is uncertain, return a local-only answer or ask the owner.
- **missing:** A functioning Safari extension heartbeat and browser command transport; A Mac-local page extraction and PII/relevance filtering service with deterministic redaction fallbacks; A privacy manifest and per-request disclosure receipt linking each model input to local DOM locators; A local-only answer path for cases where the owner forbids cloud transmission; Dashboard controls for reviewing and deleting temporary captured-page data


## Changes it proposed to its own stack

### `browser-harness` — Implement a real browser command transport and recovery protocol: extension heartbeat must register Safari as online with tab metadata; enqueue must atomically persist commandId/deviceId/tab affinity and expose pending/expired states; the extension must acknowledge receipt separately from result, retry results idempotently, and clear or quarantine the three currently stranded pending commands after an operator-visible TTL. Add a browser_resume primitive that reattaches by tabId when possible and falls back to URL plus semantic anchor, returning a typed failure instead of hanging for 45 seconds.
- **owner gets:** The owner gets dependable access to logged-in Safari pages and can resume private work instead of silently losing commands or waiting through unexplained timeouts. It is the prerequisite for voice-driven continuation and every authenticated browser workflow.
- effort: Medium: extension heartbeat/ack changes, local-agent queue state machine and tests for retries, tab reattachment, TTL cleanup, and one end-to-end Safari test.  ·  risk: A retry could duplicate a click or type action. Restrict automatic retries to navigation/read/wait and make mutation commands carry an idempotency key; quarantine ambiguous mutation results for dashboard review. Recover by replaying only explicitly safe commands and exposing receipts.
- cost: Negligible API cost; small local JSON/D1 storage increase for command state and short receipts.  ·  latency: Removes the current 45-second timeout failure mode; normal reads add less than 200 ms for acknowledgement, while reconnect fallback may add page-load time.
- security: Preserve tab/session affinity and never log page bodies or typed secrets. Encrypt or redact resume metadata and make TTL deletion observable.
- depends on: A functioning Safari extension heartbeat and command enqueue endpoint (currently browser offline; provided enqueue wrappers still return implementation errors); Durable browser session/resume records

### `mac-harness` — Add a local privacy gateway between browser extraction and any model call. It should parse the captured DOM into semantic blocks, classify relevance to the owner’s spoken question, redact high-risk fields and unrelated blocks locally, assign stable local citation IDs, and emit a disclosure receipt containing hashes/locators rather than raw page text. Support an enforced local-only mode and a fail-closed behavior when classification confidence is low.
- **owner gets:** They can ask questions about authenticated pages without routinely exporting their whole logged-in account or unrelated personal data to the relay. Answers remain traceable to the exact private page regions used, and the owner can see or delete the temporary capture.
- effort: Medium-to-large: DOM normalization, sensitive-field classifiers, local model or rules, receipt storage, browser integration, and adversarial tests for hidden fields, rendered text, and accidental credential leakage.  ·  risk: Over-redaction can make answers incomplete; under-redaction can expose sensitive information. Recover by retaining the original only in an encrypted short-lived Mac cache, showing uncertainty, allowing local-only fallback, and never silently retrying with the unredacted page.
- cost: Small local CPU/storage cost; optional local model increases disk/RAM use. Cloud API cost decreases because only selected excerpts are sent.  ·  latency: Adds roughly 0.5–3 seconds locally, but reduces upload and cloud synthesis time for long pages.
- security: Strongly improves data minimization, but the gateway itself becomes a sensitive local component and must use strict TTL deletion, encryption at rest, no raw-content logs, and explicit audit receipts.
- depends on: A functioning browser extension heartbeat and command transport; A typed browser extraction result containing DOM regions and locators; Relay support for citation-bearing, redacted excerpts and local-only responses


## What it asked for

_Nothing._
