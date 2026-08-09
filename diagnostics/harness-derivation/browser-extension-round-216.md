# Harness derivation — browser-extension — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me only what changed on my signed-in accounts that needs me today, and put the urgent ones on my pendant.”"
- **useful because:** This is the system's highest-value browser-only job: Safari can see authenticated dashboards that the relay, Mac APIs, and public search cannot. It turns noisy portal changes into a small exception queue, with the always-near pendant delivering urgent items even when the owner is away from the screen. The browser supplies evidence, the relay ranks and deduplicates it, and the Mac can prepare reversible follow-up without pretending it sent anything.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background/scheduled extraction and diffing on a cheap model; use the expensive realtime tier only when the owner asks a spoken follow-up. Browser returns short claims and evidence capsules, never page bodies.
- **latency:** Initial per-origin scan under 60 seconds; unchanged origins cost no speech. Urgent alert delivery under 10 seconds after a detected change; spoken follow-up under 2 seconds once the owner asks.
- **cost:** Low per scan: browser command latency and a small extraction/diff prompt dominate; roughly 1 cheap invocation per changed page, near-zero when hashes/selectors are unchanged. Realtime cost occurs only for an alert or question.
- **security:** Ship with an empty, inspectable per-origin rule set; the owner later chooses origins and read/extract/redact/never-store and may-speak/must-not-speak categories. Persist only host-keyed claims under the existing 24-hour, 200-character browser-fact limits with provenance; never HTML, screenshots, or page text. Never submit forms or send messages automatically; show a proposed action for the owner to invoke.
- **missing:** A scheduler that invokes browser page-watch jobs against owner-supplied origins; Robust per-origin change selectors and authenticated-session expiry handling; A cross-surface exception queue that deduplicates browser findings and emits offline_alert_inbox payloads; Owner configuration UI for the currently-empty origin and speech/retention policy

### "“Before I act on this account page, verify it against my local records and tell me exactly what does not match.”"
- **useful because:** A signed-in page alone can be misleading or stale. This creates an evidence join no single node can perform: Safari reads the private page, the Mac checks local Calendar/Mail/files or a downloaded statement, and the relay explains the disagreement over voice. It is useful for invoices, delivery dates, subscription renewals, and account changes without persisting the underlying sensitive documents.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Cheap extraction and deterministic field matching first; invoke the expensive realtime model only to explain ambiguous conflicts or answer a spoken clarification.
- **latency:** 30 seconds for a normal two-source comparison; up to 90 seconds when a local search and authenticated navigation are required.
- **cost:** One small browser extraction plus one local search per request; model cost is dominated by conflict explanation, not retrieval. No recurring cost unless the owner asks.
- **security:** Require the owner to initiate each comparison and identify the enrolled origin/category; send only selected fields and hashes between surfaces. Do not save page text or local attachments. Keep provenance links and short claims under existing browser retention. If a mismatch would lead to a payment, cancellation, or message, stop at a preview and state the exact proposed mutation.
- **missing:** A structured cross-surface comparison contract (field, source, observed value, timestamp, confidence); A browser extraction mode that returns labeled fields rather than prose; A Mac search adapter that can return redacted matching fields from local records; A voice response format that distinguishes stale data from a true conflict

### "“I’m looking at this page—give me the important numbers and remind me what I need to do next.”"
- **useful because:** The owner should not have to copy a private page into chat. Safari can capture the active tab and focused/selected region, the relay can summarize it, and the pendant can speak a concise answer while the Mac remains available for a reversible next step. This is especially valuable for dense authenticated portals and forms where public web search is useless.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a small extraction model for headings, labels, dates, and amounts; use realtime only for the owner's follow-up question or a spoken summary.
- **latency:** Active-tab capture in 2 seconds and first spoken bullets within 4 seconds; never wait on a full-page crawl when a focused region is available.
- **cost:** One browser snapshot/read and a short extraction prompt per request. The main cost is sending selected DOM text; cap it aggressively and avoid screenshot tokens unless structure is unavailable.
- **security:** The extension must explicitly mark whether the payload is active-tab metadata, selected text, or a screenshot. Default to selected/focused text, redact secrets and account identifiers, discard raw content after synthesis, and store no browser fact unless the owner asks. Do not click or submit as part of summarization.
- **missing:** A reliable active-tab/focused-selection command (the current bridge has no separate active-tab route); A payload-size-limited browser snapshot with DOM labels and origin metadata; A relay-to-pendant spoken-summary message type that expires after playback; A clear owner-visible indicator showing which tab/region was sent

### "“Save my place in this private web process, and later tell me exactly where I left off and what evidence I still need—without saving the page itself.”"
- **useful because:** Today a multi-step authenticated task disappears into a browser tab: the owner can lose a partially completed claim, application, return, or support case and cannot recover the state from the pendant. A continuity capsule would preserve only a structured checkpoint—origin, workflow label, completed fields, unresolved fields, timestamps, and provenance pointers—so the owner can resume days later or ask by voice what remains. This is different from page summarization or change alerts: it preserves the owner's progress through a process, not the site's content.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Use deterministic DOM/form-state extraction and a cheap model to normalize labels; use the realtime tier only when the owner asks a spoken resume question or the workflow state is ambiguous.
- **latency:** Checkpoint capture under 3 seconds after an explicit “save my place”; resume answer under 2 seconds from the local capsule, with browser revalidation only when requested.
- **cost:** Small extraction call per explicit checkpoint and occasional revalidation; storage and API costs are negligible compared with repeated full-page scraping. No scheduled model spend unless the owner enables revalidation.
- **security:** Never store HTML, screenshots, typed secrets, password fields, payment values, or page text. Store only a short structured state with host, workflow identifier, field labels/statuses, timestamps, and provenance URL hashes. Capsules must be encrypted locally, expire by default, and be deleted on request. Reopening a workflow may navigate but must not submit or send anything.
- **missing:** A browser action that emits a normalized form/workflow checkpoint while excluding sensitive input values; An encrypted, user-visible continuity-capsule store on the Mac with expiry and deletion; A revalidation operation that compares the saved checkpoint to the current authenticated page without mutating it; Pendant commands for listing, resuming, and deleting saved private workflow checkpoints; A schema for distinguishing owner-entered progress from facts merely displayed by the site

### "“Audit the sharing, recovery, and active-session settings on my signed-in accounts, and tell me which ones are unexpectedly exposed.”"
- **useful because:** The owner cannot get a reliable inventory of private account security state from public search or local Mac APIs. Safari can inspect the settings behind existing logins, the Mac can compare dates and known-device records, and the relay can reduce the result to concrete anomalies. The system should report findings and prepare a fix plan, not silently change security settings.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → pendant
- **model tier:** Deterministic extraction and rule checks for sessions, recovery methods, sharing scopes, and dates; use a cheaper model to cluster equivalent settings. Realtime is reserved for explaining an anomaly by voice.
- **latency:** A user-triggered audit in 2–5 minutes across enrolled origins; urgent high-risk findings reach the pendant within 10 seconds of discovery.
- **cost:** One small extraction request per settings page and a compact rules evaluation. Cost scales with enrolled origins, but unchanged settings can be skipped using field fingerprints.
- **security:** This is exceptionally sensitive. Require explicit enrollment per origin and category, do not speak secrets or full email/phone identifiers, persist only redacted findings with short TTL and provenance, and never alter settings automatically. A proposed remediation must show the exact setting and target value before navigation or save.
- **missing:** Origin-specific security-settings extractors and a common schema for sessions, sharing, recovery, and devices; A local known-device/recovery inventory that the Mac can provide without uploading raw contacts; Risk rules with owner-overridable severity and false-positive handling; A pendant alert payload that says “security finding available” without revealing its content aloud

### "“Why is this private bill or statement different from the last one? Show me the exact changed line items and the likely cause.”"
- **useful because:** A current-page summary cannot answer a longitudinal question. The browser can revisit the authenticated statement, the Mac can retain only a redacted structured ledger of prior line items, and the relay can explain the delta over voice. This gives the owner an auditable answer for billing disputes without retaining full statements or screenshots.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → pendant
- **model tier:** Use deterministic field extraction, amount/date arithmetic, and line-item matching first; use a cheap model to label likely causes; reserve realtime for the owner's follow-up or an ambiguous explanation.
- **latency:** Under 45 seconds for a pair of statements already enrolled; under 2 minutes if the browser must locate the prior statement. Spoken result within 3 seconds after the comparison completes.
- **cost:** Two bounded browser extractions and one compact diff prompt per request. The dominant cost is navigating authenticated pages; raw statement content is discarded after normalization.
- **security:** Store only normalized line-item hashes, redacted labels, amounts where explicitly allowed, and provenance with a short expiry; never retain PDFs, HTML, account numbers, or screenshots. Make the comparison owner-initiated and disclose which periods and origin were used. Any dispute message or payment action remains a preview only.
- **missing:** A versioned structured statement extractor resilient to changing portal layouts; A redacted line-item ledger with explicit per-origin retention and deletion controls; A browser locator for prior statements that can read but not download or submit; A diff/explanation format that separates observed changes from inferred causes


## Changes it proposed to its own stack

### `browser-harness` — Add a read-only browser_context action that asks the Safari extension for the active tab's tabId, origin/title, focused element metadata, selected text, and a bounded DOM snapshot in one response. Include a per-request content budget, explicit source kind (selection/focus/page), and a disposable context ID that later browser_read_page or browser_click calls must reference.
- **owner gets:** The owner can say “this page” and get an answer about the exact private page or form field in front of him, instead of the agent guessing among tabs or requiring him to paste sensitive text. It also makes read-only browser work fast and auditable.
- effort: Medium: extension content-script capture plus one local-agent bridge action, schema validation, and Safari permission testing. Add redaction and truncation tests for passwords, payment fields, and large pages.  ·  risk: Focused fields may contain secrets or the wrong tab may be captured. Default to selected text/labels, omit input values marked password/payment, show origin and source kind before synthesis, cap payloads, and discard the context after the request. Recovery is simply a new capture; no page mutation occurs.
- cost: Negligible runtime/API cost beyond one small extraction request; engineering effort is the cost. No hardware change.  ·  latency: Removes a round trip between list-tabs, choose-tab, and read-page; target under 500 ms for metadata and under 2 seconds for a bounded snapshot.
- security: Improves security by making the capture scope explicit and bounded, but introduces a new sensitive-data boundary. Enforce origin in the returned context and apply existing redaction before relay transmission.
- depends on: A working browser_* dispatch through POST /execute; Safari extension support for active-tab and selection capture; Empty owner-supplied origin policy remaining the authority for whether context may leave the Mac; A relay prompt contract that treats context IDs as disposable evidence, not memory


## What it asked for

_Nothing._
