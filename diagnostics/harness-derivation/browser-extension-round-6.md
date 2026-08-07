# Harness derivation — browser-extension — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the relevant pages in my open browser tabs, compare the options, and give me a short brief with links and any deadlines.”"
- **useful because:** Turns scattered authenticated tabs into an actionable summary without making the owner copy/paste sensitive content. Useful for travel, bills, purchases, research, and work portals.
- **path:** pendant (voice request and spoken completion) → Safari extension (read only the explicitly selected tab(s), extract title/URL/content) → Mac agent (sanitize, deduplicate, and persist a small result) → dashboard/iOS (show brief, citations, and source tabs)
- **model tier:** Use a cheap background model for extraction, comparison, and summarization; reserve realtime only for the initial conversational handoff and playback. Never let page text become instructions to the agent.
- **latency:** A 10–30 second asynchronous job is acceptable; stream a quick acknowledgement, then deliver text/audio when complete.
- **cost:** Roughly $0.01–$0.08 per brief depending on page length; dominant cost is input tokens from extracted pages, so cap pages and summarize each before cross-page comparison. No audio generation unless the owner asks to hear it.
- **security:** Read-only by default, allowlist the tab IDs/URLs supplied by the owner, strip credentials and hidden form fields, and treat all page content as untrusted data. Do not click, type, submit, download, or expose full page contents in logs. Require confirmation before opening a new domain or accessing a non-selected tab.
- **missing:** A reliable selected-tab/tab-list command and tab IDs from the Safari extension; Per-job page-size limits and redaction before data reaches the model; Citation-preserving background-job storage and delivery

### "“Every weekday morning, check my authenticated work portal for new high-priority items and tell me only what needs my attention.”"
- **useful because:** A quiet, recurring triage routine removes repetitive checking while keeping the owner in control of consequential actions.
- **path:** relay scheduler/job store (run at the owner's chosen local time) → Safari extension on the Mac (read only the named portal and known page region) → background model (classify against owner-defined rules and produce a concise digest) → pendant/iOS/dashboard (deliver a short notification and optional audio brief)
- **model tier:** Cheap background model for extraction/classification; realtime model only if the owner starts a follow-up voice conversation. Use deterministic selectors and hashes to avoid sending unchanged pages to a model.
- **latency:** Complete within 2 minutes of the scheduled time; stale or unavailable browser should yield a clear 'not checked' notice, never a guessed result.
- **cost:** About $0.001–$0.03 per run when unchanged content is hashed locally; larger runs cost more from page text. Audio is optional and should be generated only for nonempty digests.
- **security:** Explicitly authorize each domain and page region, store only extracted task metadata, and never auto-send messages, approve expenses, or click links. Require confirmation for any action beyond reading. Notify if login/session state changes or a new domain appears.
- **missing:** Persistent scheduler with timezone/DST handling; Extension-side domain/page-region allowlists and content hashing; A clear consent UI showing exactly what recurring jobs can read and retain

### "“Research this topic across the public web, check the sources, and send me a cited answer later.”"
- **useful because:** Lets the owner delegate multi-page research while they continue their day, with a compact answer and traceable sources rather than an unverified conversational guess.
- **path:** relay job scheduler and Cloudflare Browser Run (navigate/search public pages, no owner cookies) → cheap background model (extract claims, cross-check dates, summarize) → dashboard/iOS (show citations, timestamps, confidence and source excerpts) → pendant (announce completion and optionally play a generated audio brief)
- **model tier:** Background model for all browsing/extraction and synthesis; realtime only for clarifying scope or discussing the result. Use a small model for per-page extraction and a stronger slower model only for final synthesis when sources conflict.
- **latency:** 30 seconds to 5 minutes depending on source count; acknowledge immediately and deliver asynchronously. Stop after a configurable source/time budget.
- **cost:** Approximately $0.03–$0.30 per run, dominated by Browser Run calls and page tokens; cache URL snapshots and reuse unchanged source hashes. Audio adds a separate per-minute generation cost and is opt-in.
- **security:** Use an isolated server browser with no cookies or local network access; treat pages as hostile prompt injection. Cite every material claim, preserve retrieved timestamps, and never install, download, purchase, or submit forms. Ask confirmation before using any private/authenticated source.
- **missing:** Cloudflare Browser Run adapter exposed as a queued background tool; Prompt-injection-resistant extraction sandbox and source cache; Job progress, cancellation, and citation UI

### "“Fill out this web form from the information I give you, stop before submission, and show me exactly what will be sent.”"
- **useful because:** Saves repetitive browser typing while keeping the owner as the final authority over messages, purchases, applications, and other consequential submissions.
- **path:** pendant (collect fields and read back sensitive ones privately) → Safari extension (fill only the explicitly selected form, never submit) → Mac agent (validate field mapping and produce a diff/preview) → dashboard/iOS (review every field, origin, attachments, and final submit button)
- **model tier:** Use deterministic field mapping plus a cheap model for label matching; realtime only for spoken clarification. No model should infer missing sensitive values; ask the owner.
- **latency:** 1–10 seconds to fill and render a review; pause indefinitely for owner confirmation.
- **cost:** Usually <$0.01, dominated by small field-extraction input; screenshots should be avoided where DOM labels suffice. No audio cost unless readback is requested.
- **security:** Never auto-submit, upload, or alter payment/identity fields without a separate explicit confirmation bound to the exact origin, form hash, and field values. Mask secrets in logs and UI unless owner chooses reveal; block cross-origin frames and suspicious page instructions. Recover by clearing the form and showing the untouched state.
- **missing:** Structured form-field extraction and safe fill command; Cryptographic/visible preview binding confirmation to exact form state; Sensitive-field policy and redaction in extension results


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class browser session API: list tabs with stable tab IDs, select a tab explicitly, bootstrap navigation only after confirmation, capture a bounded DOM/text snapshot with URL/title, and return structured redaction metadata. Add extension heartbeats with tab inventory and clear stale-session errors.
- **owner gets:** The assistant can reliably act on the page the owner means instead of failing when Safari has no reported tab or risking the wrong authenticated page. It also makes browser jobs auditable and resumable.
- effort: Medium: extension polling/result protocol, Mac bridge methods, schema/versioning, and dashboard consent UI; test Safari tab lifecycle, sleep, reload, and multiple profiles.  ·  risk: A stale tab ID could target a different page after navigation. Bind IDs to window/tab plus URL origin and invalidate on navigation; show a confirmation preview and fall back to read-only failure. Recover by requiring re-selection.
- cost: Small per-job metadata overhead; reduces model cost by returning bounded extracted text and hashes rather than screenshots/full DOM. No meaningful hardware cost.  ·  latency: One heartbeat/list operation adds <1 s; bounded extraction is faster than screenshot-based computer use. Session startup may still take up to the existing 45 s timeout, which should become configurable.
- security: Strongly positive if origin, tab selection, redaction, and audit records are enforced. Never return cookies, passwords, hidden inputs, or page instructions as executable commands.
- depends on: Extension protocol support for tab inventory and stable IDs; Mac bridge schema for read-only browser jobs; Owner-facing consent and audit display

### `memory` — Create a browser-job memory tier separate from conversational context: retain only normalized facts, source URLs, retrieval timestamps, consent scope, and a short owner-approved summary; expire raw page text/screenshots quickly and never inject whole prior pages into every prompt.
- **owner gets:** Follow-up questions remain coherent and cited without repeatedly exposing private browsing content or making every voice turn slower and more expensive.
- effort: Medium: schema, retention worker, per-job access control, and prompt assembly changes across relay and Mac agent.  ·  risk: Over-aggressive pruning can lose evidence or make a summary stale. Keep source links and hashes, mark expired facts, and re-fetch on request; provide deletion controls.
- cost: Lower recurring token cost and storage versus replaying raw pages; modest D1/R2 metadata cost.  ·  latency: Faster follow-ups from compact facts; re-fetch adds latency only when evidence is expired.
- security: Positive: minimizes private data retention and prompt injection replay. Enforce tenant/job scope and never treat stored page text as instructions.
- depends on: Browser job IDs and source metadata; Retention/sweep worker (currently audio sweep is disabled); Centralized context assembly rather than hand-written per-surface sections


## What it asked for

### `c7-jgzz` (context) — owner's highest-value browser workflows
- why: I can design safer, more useful automations if I know whether the owner primarily wants research, work-portal triage, shopping/travel, or form filling.
- would change: I would prioritize the matching capability, consent UX, and retention policy instead of building broad browser access with unnecessary exposure.

## Its own summary

Proposed four concrete browser capabilities: read-only authenticated multi-tab briefs, recurring portal triage, isolated public-web research with citations, and form filling that always stops for exact review. Proposed a browser-harness session API with stable tab IDs, bounded/redacted extraction, origin binding, and explicit consent; and a compact browser-job memory tier to reduce token cost and private-data retention. I still need the owner's top workflow preference and implementation of tab inventory/selection, scheduler, and the isolated Browser Run adapter.

**Biggest unknown:** Safari currently reports zero tabs and has no reliable tab-list/selection API, so authenticated workflows cannot safely target an owner-selected page yet.

