# Harness derivation — browser-extension — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 9 tabs, including authenticated Gmail and X; browser_list_tabs succeeds through POST /execute. Earlier tabCount=0 is no longer current.
  - evidence: POST /execute {actions:[{type:'browser_list_tabs'}]} returned 200 at 2026-08-08T03:00:22Z with Gmail tab 901464, X tab 1163292 active, and 9 total tabs.

## Capabilities it proposed

### "“Find the matching information across my logged-in tabs—like the invoice in Gmail and the contract in my document system—and tell me what conflicts, without sending or changing anything.”"
- **useful because:** Public search cannot reach the owner’s private mail and documents, and no single browser tab contains the answer. The extension can read several already-authenticated tabs, the Mac can align names, dates, amounts, and clauses locally, and the pendant can deliver the result hands-free. This is the highest-value thing this browser node could uniquely enable: private cross-application fact checking before money or commitments move.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Background model for extraction and comparison; realtime model only for clarifying which entities or discrepancy the owner wants spoken.
- **latency:** 20–60 seconds for a multi-tab comparison; a short spoken result under 5 seconds once ready.
- **cost:** $0.03–$0.20 per comparison depending on extracted text and number of tabs; browser extraction and local normalization dominate, with a compact final synthesis.
- **security:** Never upload raw private pages by default. Extract only requested fields in the Mac agent, redact account numbers and unrelated content, retain an ephemeral evidence map with origin/tab/time, and delete it after delivery. Read-only browser actions only unless the owner separately asks for a mutation.
- **missing:** A multi-tab browser extraction action that returns bounded regions from selected tab IDs; Local schema/normalizer for entities, amounts, dates, and document clauses; A cross-tab evidence graph with source citations and contradiction scoring; An owner-supplied per-origin read/redact/never-store policy

### "“Lock down my browser right now.”"
- **useful because:** A pendant is physically present when the owner notices someone else approaching; the Mac may be unattended and Safari may hold mail, social, and financial sessions. One spoken command or dedicated hardware event can immediately hide/lock the Mac and close or quarantine selected authenticated tabs, something the cloud relay alone cannot do.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime intent classification only; deterministic Mac/browser actions perform the lockdown and report completion.
- **latency:** Under 3 seconds to mute/stop browser exposure and lock the Mac; status confirmation within 5 seconds.
- **cost:** Near-zero API cost after intent recognition; the work is local OS and extension control.
- **security:** This is deliberately a high-impact but owner-requested emergency action. Make the trigger explicit (a spoken phrase or dedicated long press), avoid deleting data, preserve unsaved drafts where possible, and report exactly which tabs/apps were closed, hidden, or left open. Do not transmit page contents.
- **missing:** A pendant emergency-intent event distinct from ordinary conversational audio; An idempotent local lockdown action that locks the display and records recoverable tab state; Browser extension support for hiding/quarantining selected origins and restoring them after unlock; A hardware/voice fallback when the Mac-to-relay link is unavailable

### "“Before I submit this form, check every field against the source message or document and give me a spoken mismatch report; then leave the form filled but do not submit it.”"
- **useful because:** Authenticated forms are where a small transcription error becomes a real financial, legal, or operational mistake. The browser can inspect the private form and source tabs, the Mac can normalize fields and detect discrepancies, and the pendant can read a concise report while the extension fills only after the owner hears it. This is a useful read-and-prepare workflow rather than a generic browser macro.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model extracts and matches fields; realtime model turns discrepancies into a short spoken checklist.
- **latency:** 10–30 seconds for ordinary forms; leave a field-by-field evidence report in the Mac UI while speaking only exceptions.
- **cost:** $0.02–$0.12 per form, dominated by extraction and comparison; filling is local and essentially free.
- **security:** Keep raw values local and ephemeral, redact secrets and full account numbers from speech, show origin/source for every mismatch, and never submit or send. The owner can explicitly choose which fields may be filled.
- **missing:** Structured form-field extraction and source-field selectors across tabs; A comparison engine with field-specific normalization (dates, currencies, names, addresses); A fill-draft browser action with per-field provenance and undo; Per-origin rules for fields that must never be spoken or persisted

### "“Finish signing me in: if the site asks for a one-time code, find the matching code in my authenticated mail, verify it belongs to this exact login attempt, and enter it without reading the code aloud.”"
- **useful because:** Today the browser can see the login page and mail may be open, but no node safely joins the two authenticated contexts. This would remove a frequent interruption while preserving the code as an ephemeral secret: the pendant starts the request, Safari supplies the challenge context, the Mac matches the newest message, and the relay coordinates the handoff.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime model only interprets the owner’s request; deterministic local extraction and origin/challenge matching perform the sensitive operation. No model should be given the raw OTP.
- **latency:** 5–15 seconds after the code email arrives; abort clearly if there are multiple plausible codes or the challenge has expired.
- **cost:** Under $0.01 per attempt; browser and local matching dominate, with no need to send the OTP to a model.
- **security:** This grants access to authenticated accounts and must be tightly bound to the active browser origin, tab, challenge nonce where available, and a short expiry. Never speak, persist, log, or upload the code. Do not guess between messages; return ambiguity. The owner must explicitly invoke this per login attempt.
- **missing:** A browser action that exposes the active login origin and challenge state without page-wide extraction; A local Gmail/mail connector or browser extraction limited to newly arrived OTP-shaped messages; Origin- and challenge-bound ephemeral secret passing between the mail tab and login tab; A pendant intent and abort event for sensitive sign-in completion

### "“After you do something on the web, tell me exactly what changed and prove it happened.”"
- **useful because:** A browser command can report that a click succeeded while the site silently rejects it, redirects, or applies a different value. The extension can capture a minimal before/after semantic witness, the Mac can compare it locally, and the pendant can speak a trustworthy result instead of a generic success message.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic extraction and diffing first; a cheap background model labels the change; realtime is used only to answer follow-up questions.
- **latency:** Add 2–6 seconds after an action for postcondition checking; speak a one-sentence result immediately and retain detailed evidence locally.
- **cost:** $0.005–$0.03 per witnessed action; local DOM diffing dominates and model use is optional for structured pages.
- **security:** Capture only the changed fields, destination, timestamp, and a short redacted witness—not full screenshots or page contents. Never claim success when the postcondition is absent or ambiguous. Sensitive values must be masked in speech and receipts.
- **missing:** A browser postcondition action that re-reads the affected region after mutation; Semantic before/after diffs for navigation, form fields, and confirmation banners; A compact owner-facing receipt that links action, target, and observed result; Per-origin rules for evidence retention and redaction

### "“If the website changes halfway through my task, stop following the old plan, explain what changed, and continue only from a newly verified step.”"
- **useful because:** Today browser automation can execute selectors or clicks, but a changed authenticated site can turn a stale instruction into the wrong action. A semantic checkpoint loop would let the owner delegate long web tasks while the browser revalidates each page, the Mac replans from observed state, and the pendant reports a meaningful interruption rather than silently failing.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background planner for checkpoint comparison and recovery; realtime only for owner clarification when the new page offers multiple valid paths.
- **latency:** Under 3 seconds per checkpoint on stable pages; pause and speak within 5 seconds when a meaningful change is detected.
- **cost:** $0.02–$0.15 per multi-step task, driven by page snapshots and replanning; stable steps should use deterministic matching without model calls.
- **security:** Use read-only revalidation before every mutation, bind checkpoints to origin and page semantics rather than fragile coordinates, and retain only hashes plus the minimum changed text. Never silently substitute a new destination or recipient.
- **missing:** Semantic page-state fingerprints and checkpoint storage; A browser wait/revalidate action that can detect changed forms, destinations, and confirmation states; Planner support for branching recovery from observed state; A spoken interruption/resume protocol on the pendant


## Changes it proposed to its own stack

### `browser-harness` — Add a single read-only browser action, browser_extract_bundle, that accepts explicit tab IDs and bounded selectors, returning normalized visible text, form labels/values, origin/title, and stable element anchors with per-field provenance. Enforce a byte/time budget and return no page data outside requested regions. Add browser_fill_draft using those anchors, with a reversible before/after receipt and an explicit never-submit guarantee.
- **owner gets:** The owner could ask the pendant to compare private information across Gmail, documents, and a form, hear only the discrepancies, and have the corrected draft prepared without manually shuttling between tabs or risking an accidental submission.
- effort: Medium: extension content-script extraction and anchor validation, local-agent action schemas, receipts, and tests across Safari pages and frames.  ·  risk: DOM changes can invalidate anchors or expose more text than intended; fail closed on stale/ambiguous anchors, return a clear partial result, and keep the original form untouched. Recover by discarding the draft and re-reading the page.
- cost: Negligible runtime API cost; modest implementation and test cost. Extraction is local; only compact selected fields need model processing.  ·  latency: Adds roughly 1–3 seconds per tab for extraction and validation; avoids repeated full-page reads and should reduce total task latency.
- security: Improves least-data handling by bounding selectors and emitting provenance, but introduces a powerful field reader/filler. Require explicit owner configuration per origin and never include secrets in logs, receipts, or spoken output.
- depends on: An owner-supplied per-origin read/redact/never-store configuration; A deterministic field normalization/comparison library; The existing POST /execute browser action path and result receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities the owner cannot have today: origin-bound automatic OTP handoff from authenticated mail, semantic proof of browser action postconditions, and checkpointed recovery when a website changes mid-task. Each requires new browser extraction/state primitives and cross-surface coordination rather than merely exposing existing actions.

**Biggest unknown:** Which authenticated mail provider and login flows the owner wants supported first; the design intentionally leaves origins and secret-handling policy configurable.

