# Harness derivation — browser-extension — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser** — Safari extension is currently online with 9 tabs, including authenticated Gmail, OpenAI billing, and X sessions; POST /execute browser_list_tabs succeeds. Direct browser_navigate requires the URL under action.params.url rather than action.url; the latter fails validation.
  - evidence: POST /execute at 2026-08-08 01:25 returned tab list and a failed navigate receipt showing 'navigation command did not contain a valid URL' when url was top-level.

## Capabilities it proposed

### "Keep watch on the authenticated sites I configure, and when something materially changes, tell me on the pendant only what needs action—otherwise stay quiet."
- **useful because:** This is the highest-value browser-only capability: the browser can see logged-in pages that web search and the Mac's native APIs cannot, while the relay can watch overnight and the pendant can deliver a short alert without requiring the owner to open a screen. It converts dozens of noisy portal updates into an actionable interrupt.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Background/scheduled model for polling, extraction, deduplication, and priority ranking; realtime only when the owner asks follow-up questions by voice.
- **latency:** Polling can take minutes; a detected high-priority change should reach the pendant within 30 seconds. Interactive follow-up under 3 seconds after the browser read.
- **cost:** Low-to-moderate: scheduled extraction and diffing dominate; use a cheap model for unchanged/low-change pages and spend a larger call only on a confirmed material diff.
- **security:** Reads authenticated content and may expose it to the relay/model. Ship with empty per-origin rules and require the owner to configure origins plus may-speak/must-store categories. Persist hashes and minimal evidence, not page text; never submit forms or send messages automatically.
- **missing:** Durable scheduled browser poller that can target a named tab/session and recover after tab replacement; Per-origin extraction/redaction configuration UI, supplied by the owner rather than hardcoded; A relay-to-pendant alert delivery path using the accepted offline_alert_inbox skill; Semantic diff and deduplication state keyed by origin/page identity

### "After I complete an authenticated web task, turn the confirmation into a reminder automatically—include the date, amount or reference number, the exact follow-up deadline, and a link back to the page—and read me a one-sentence confirmation on the pendant."
- **useful because:** Important web transactions often end in a confirmation page that is easy to lose. The browser is the only node that can see the logged-in receipt; the Mac can create a native reminder; the relay can normalize dates and amounts; and the pendant can confirm hands-free. This is useful without letting the system submit anything.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Cheap background extraction/classification for the receipt; realtime only for the short spoken confirmation or owner questions.
- **latency:** Extract within 5 seconds after the owner leaves the confirmation page; reminder creation within 10 seconds; speech begins within 2 seconds after creation.
- **cost:** Low: one page extraction plus structured parsing per detected confirmation; Mac reminder action dominates neither latency nor token cost.
- **security:** Receipts can contain financial and identity data. Per-origin rules must explicitly choose which fields may be spoken or persisted; default to reference/deadline only, hash the page, and retain no raw receipt. Never infer success from an ordinary page; require a visible confirmation pattern and leave the browser unchanged.
- **missing:** A browser success-page detector or owner-triggered 'capture this confirmation' command; Structured receipt schema with origin-specific field allowlists and redaction; A route connecting browser evidence to POST /reminders or create_reminder; Duplicate suppression when the same confirmation remains open in a tab

### "I got interrupted—continue the authenticated web form where I left off, tell me what is already filled, ask me only for missing fields through the pendant, and leave it ready for my review without submitting."
- **useful because:** Forms are where browser access is uniquely valuable and interruptions are common. The extension can recover the exact session and field state, the Mac can supply known non-sensitive values when authorized, the relay can identify only missing information, and the pendant can conduct the short interview while the browser remains ready. No other node can safely resume a logged-in form.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Realtime for the brief missing-field interview; cheaper background model for field labeling, normalization, and checking the completed draft against the page.
- **latency:** Recover and inspect in under 8 seconds; each owner answer should update the page within 3 seconds; final review packet under 5 seconds. Stop before submit.
- **cost:** Moderate: repeated form snapshots and a few realtime turns; browser operations and model context dominate, so send field-level deltas rather than the whole page.
- **security:** Form fields may include financial, medical, employment, or identity data. Start with an empty per-origin policy and explicit field/category rules; redact secrets from relay logs and receipts; show the exact values and the final submit target on the pendant/Mac before stopping. Never submit, upload, or send without a separate owner action.
- **missing:** Robust DOM field inventory with labels, current values, requiredness, and sensitive-type detection; Encrypted short-lived draft state bound to browser session/tab, with field-level redaction; A pendant voice turn that can answer one missing field at a time and resolve ambiguity; A browser action to restore a draft after tab reload and a clear review/stop state

### "Gather the evidence for this issue from my logged-in web pages and my Mac files, build a private timeline with quoted source links and a list of contradictions, and leave a reviewable case file on my Mac without contacting anyone."
- **useful because:** The owner cannot get a trustworthy, cross-source case file from any single node today. The browser can access authenticated statements and receipts, the Mac can access local documents, the relay can reconcile dates and contradictions, and the pendant can let the owner steer the investigation hands-free. This is useful for billing disputes, insurance, travel claims, and support escalations while preserving the owner's control over any communication.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Background model for extraction, date normalization, deduplication, and contradiction detection; realtime only for the owner's spoken scope changes or review questions.
- **latency:** A 10–20 source case should be ready in 2–5 minutes; spoken follow-ups under 3 seconds. The owner reviews the generated file before sharing it.
- **cost:** Moderate: authenticated page reads and local-file extraction dominate context; use hashes and source excerpts rather than resending full documents on every turn.
- **security:** This may combine financial, legal, medical, or identity data. Data must remain local by default, with explicit per-origin and per-folder inclusion rules, field-level redaction, short-lived working files, and an audit manifest. Never send, upload, email, or submit the case file automatically.
- **missing:** A cross-surface evidence bundle format linking browser evidence capsules and Mac file excerpts; A local-only case-file writer with citations, redaction preview, and expiry/deletion controls; A contradiction/timeline analysis job that can request additional authenticated tabs without losing provenance; Pendant controls for narrowing scope, excluding a source, and marking a fact as owner-confirmed

### "Forget everything you learned from this browser task: remove its page captures, notes, cached excerpts, and relay context, and tell me what could not be deleted."
- **useful because:** Authenticated browser work can create sensitive traces across the extension, Mac agent, relay jobs, evidence capsules, and pendant alerts. Today there is no single owner-facing command that proves what was erased across all those surfaces. A cross-node forget operation gives the owner a tangible privacy control rather than requiring trust in scattered retention behavior.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Deterministic deletion and verification first; no expensive model call except to interpret an ambiguous spoken scope such as 'that task'.
- **latency:** A scoped deletion should complete and return a receipt within 10 seconds; any unavailable surface should be reported immediately rather than silently retried.
- **cost:** Very low model cost; storage enumeration, deletion, and verification dominate.
- **security:** Deletion itself must be scoped and reversible only through an explicit temporary quarantine, never by guessing. Require a clear task/session identifier in the UI or voice confirmation for broad scopes. Return a manifest of deleted, retained, and legally/system-required records; do not echo the sensitive content being deleted.
- **missing:** A shared provenance/session identifier across browser commands, Mac jobs, research briefings, captures, and pendant alerts; Deletion endpoints for browser evidence, relay context, cached model inputs, and offline alert payloads; A verifiable deletion receipt with retention exceptions and expiry timestamps; A pendant-visible privacy status and retry path when a node is offline

### "Reconcile the receipts in my logged-in merchant accounts against the financial files on my Mac, group duplicates and refunds, flag charges that do not match, and give me a private review list without disputing anything."
- **useful because:** The browser alone sees merchant-side order and refund details, while the Mac sees downloaded statements or exports; neither can reliably reconcile both sides. The relay can normalize merchants, dates, currencies, and order identifiers, and the pendant can report only the few anomalies worth reviewing. This provides practical financial oversight without authorizing a dispute or payment action.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Background model for entity matching and anomaly ranking, with deterministic arithmetic and duplicate detection around it; realtime only for owner questions about a flagged item.
- **latency:** A bounded month of records should process in 1–3 minutes; a spoken query about one anomaly should answer in under 4 seconds.
- **cost:** Moderate: page reads and local statement parsing dominate; cache normalized transaction rows and send only uncertain matches for model reasoning.
- **security:** Financial records and authenticated merchant pages are highly sensitive. Keep raw statements and page text on the Mac where possible, transmit redacted transaction fields only, store hashes and provenance, and make the review list private by default. Never contact merchants, initiate refunds, or open disputes.
- **missing:** A connector that extracts paginated order/refund records from configured authenticated origins; A local structured transaction vault with encryption, retention, and per-field redaction; Currency-aware matching with confidence, duplicate, refund, and partial-capture semantics; A review UI and pendant navigation for accepting, dismissing, or annotating anomalies


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-side, per-tab semantic observation mode: on an owner-configured origin, compute a local DOM/structured-field fingerprint and send only changed field paths, redacted values, title, and a short evidence capsule to the Mac agent. Include tab replacement recovery, login-expired detection, and an explicit pause/forget control. Do not transmit or persist full page text by default.
- **owner gets:** Authenticated pages can be watched continuously without shipping an entire private page to the relay, and the owner gets alerts only when a relevant field changes—even if the tab is backgrounded or the Mac briefly loses network.
- effort: Medium-high: Safari extension content-script and permission work, origin rule UI, local diffing, tab/session reconciliation, and integration with pageWatch/relay scheduling.  ·  risk: DOM layouts vary and local fingerprints can produce false positives or miss canvas-rendered content. Recover by showing the changed selector/evidence and allowing a one-shot full read; pause the observer on logout or rule removal. Never auto-act on a diff.
- cost: Small recurring compute in Safari; lower model/token cost because unchanged pages and raw text are not sent. No hardware cost.  ·  latency: Sub-second local change detection; alert path still depends on relay polling and model ranking, typically seconds.
- security: Improves privacy by keeping raw authenticated content local, but fingerprints and changed values remain sensitive; encrypt transport, bound data to the configured origin, expire capsules, and honor per-category may-speak/must-not-store rules.
- depends on: Owner-supplied per-origin rules (ship empty); Durable scheduler/pageWatch implementation; A relay-to-pendant path for offline_alert_inbox


## What it asked for

_Nothing._
