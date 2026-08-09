# Harness derivation — browser-extension — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep me informed when something important changes in one of my authenticated web accounts, without making me revisit every tab."
- **useful because:** The browser is the only node that can see existing logged-in sessions; the relay can compare and rank changes, and the pendant can deliver a short alert even when the Mac is not in front of the owner. This turns private web state into an actionable, low-noise feed rather than repeated manual inspection.
- **path:** browser-extension → mac-planner → relay-realtime → unified → dashboard
- **model tier:** Background model for scheduled page snapshots and diff classification; realtime only when the owner asks follow-up questions; cheap local hashing/diffing before sending page content.
- **latency:** Scheduled checks can complete within 1–5 minutes of the configured interval; an alert should reach the pendant within 10 seconds after a detected change.
- **cost:** Usually <$0.01 per changed page check when local DOM fingerprints avoid model calls; larger cost is incurred only for changed regions requiring semantic classification and speech synthesis.
- **security:** Authenticated page content leaves Safari only to the owner's local agent and relay. Ship with an empty per-origin configuration and explicit read/extract/redact/never-store rules; never persist full page text by default. Require confirmation before any click or submission, and display the source origin and timestamp in every alert.
- **missing:** A durable per-origin watch configuration UI/API built on existing browserSessions/pageWatch and redaction machinery; A scheduler that can enqueue browser snapshots for a registered Safari session; Semantic DOM-region diffing and deduplication; Relay delivery into the accepted offline_alert_inbox device skill

### "Save the useful part of this private web page for me, with its source, so I can ask about it later without reopening the site."
- **useful because:** A logged-in browser session often contains information unavailable to search or the relay, while the pendant is good at marking a moment hands-free. A deliberate capture creates a small, attributable memory instead of silently storing an entire page or losing the context when a tab closes.
- **path:** browser-extension → relay-realtime → mac-planner → unified → dashboard
- **model tier:** Use local extraction and redaction first; use a background model only to reduce the selected DOM/text to a short citation-preserving note. Realtime is reserved for the owner's spoken 'save this' interaction.
- **latency:** Capture acknowledgement within 3 seconds; searchable note within 30 seconds.
- **cost:** <$0.01 for a selected excerpt and metadata; model cost scales with excerpt length, with a hard truncation limit.
- **security:** Capture only an explicit selection or the visible semantic region, never the whole authenticated page by default. Apply existing redaction and per-origin rules; store origin, title, timestamp, selector/section label, and a short excerpt, with a never-store option. Do not speak secrets aloud unless the owner explicitly asks.
- **missing:** An extension command to return selected text and stable page metadata/URL; A provenance-aware note record that can be retrieved by voice; A user-configurable capture policy per origin and category, initially empty

### "Fill out this web form from my notes, show me exactly what will be submitted, and wait for my approval before sending it."
- **useful because:** This combines authenticated browser reach with local notes and the pendant's short spoken interaction: the owner gets the convenience of automation without losing visibility into the exact recipient, amounts, attachments, or wording. It is useful for applications, support forms, and routine data entry while preserving the explicit stop before irreversible submission.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → dashboard
- **model tier:** Background/local extraction for field mapping and deterministic note lookup; realtime model only for ambiguous fields or a spoken review request. No model should invent values; unresolved fields remain blank.
- **latency:** Draft in under 15 seconds for ordinary forms; review packet and spoken summary within 5 seconds after the draft is ready.
- **cost:** <$0.03 per ordinary form, dominated by semantic field mapping; near-zero when labels and note keys match deterministically.
- **security:** Read the form and local notes only after the owner invokes the task. Never submit automatically. Present a machine-readable field/value diff, origin, and attachment list on the Mac and a concise spoken checksum on the pendant; confirmation must be explicit and scoped to that exact draft. Respect per-origin read/redact rules and avoid persisting form values after completion.
- **missing:** A browser action that extracts form schema and current values without submitting; A draft transaction object with immutable field/value hash and expiration; A review surface that renders the diff and accepts one scoped approval; A submit action that can only consume the approved draft

### "What am I looking at in Safari right now, and what are the two most important things on this page?"
- **useful because:** The owner can ask hands-free while moving around, and the browser extension can inspect the actual authenticated tab rather than guessing from a URL. It makes the pendant a remote reader of private web context, including the currently selected tab and visible state, without requiring navigation or mutation.
- **path:** browser-extension → relay-realtime → mac-planner → mac-vision → unified
- **model tier:** Local DOM extraction and accessibility tree first; a small vision model only when the page is canvas/image-heavy; realtime model produces one short spoken sentence, with optional detail on request.
- **latency:** Under 4 seconds for text pages and under 8 seconds for visual pages.
- **cost:** A few cents only for visual pages; text pages should remain below $0.01 through local extraction and compact context.
- **security:** Return only the active tab's visible/semantic content and origin; do not enumerate or read background tabs unless asked. Redact according to the configured origin policy, never persist page text, and make the spoken answer explicitly identify the site so accidental cross-tab confusion is obvious.
- **missing:** Reliable active-tab targeting and browser_read_page result delivery from Safari; A compact context selector that limits extraction to visible content; A visual fallback for inaccessible/canvas pages; A voice command route that binds the request to a browser inspection job

### "Compare the private pages I already have open, tell me where they disagree, and give me one sourced conclusion without exposing the page contents elsewhere."
- **useful because:** Today the browser can inspect pages one at a time, but the owner cannot ask the system to reconcile several authenticated sources that are already open. This would turn private tabs into a trustworthy research instrument for decisions such as comparing account records, internal documentation, or conflicting status pages while preserving citations and locality.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → dashboard
- **model tier:** Local extraction and deterministic citation collection first; a background synthesis model handles comparison and contradiction detection; realtime is used only to answer the owner's follow-up question.
- **latency:** Produce a compact result in 15–30 seconds for up to five tabs; stream progress only if a page is slow or visually inaccessible.
- **cost:** Approximately $0.02–$0.10 per synthesis depending on extracted text and visual fallback; local deduplication should keep repeated pages cheap.
- **security:** Only inspect tabs explicitly selected by the owner, never all tabs by default. Keep raw page text local or ephemeral, attach origin/title/quoted evidence to every claim, apply per-origin redaction, and speak only the conclusion unless the owner asks for evidence. No external search or upload of private content.
- **missing:** Multi-tab selection and stable tab identifiers from the Safari extension; A local evidence bundle with per-claim source ranges and contradiction labels; A synthesis job that can operate on ephemeral authenticated content; A spoken citation format that identifies the source without reading sensitive excerpts aloud

### "Restore the private web work I was doing yesterday and put each page back at the right scroll position, search state, and draft context, without sending anything."
- **useful because:** A browser session today is fragile: a restart or accidental tab close loses the owner's working set and the mental context around it. A deliberate checkpoint would let the owner resume authenticated research or drafting from the pendant or Mac, including where they were reading, while keeping unsent work visibly unsent.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → dashboard
- **model tier:** Local session serialization for URLs, tab IDs, scroll anchors, and safe draft state; background model only labels a checkpoint and summarizes what was in progress. Realtime is unnecessary except for the spoken restore command.
- **latency:** Checkpoint in under 2 seconds; restore a normal workset within 10 seconds, with a progress report for slow origins.
- **cost:** Near-zero for serialization; under $0.01 if an optional short checkpoint summary is generated.
- **security:** Persist only explicit checkpoints, never a passive history of private tabs. Encrypt or keep checkpoint data on the owner's Mac, discard expired session tokens and page text, and restore drafts in preview mode. Do not replay clicks, submissions, or navigation with side effects.
- **missing:** A browser checkpoint format covering tab identity, URL, scroll/selection anchors, safe form draft state, and origin metadata; Extension support for restoring multiple tabs and page-local state; A local encrypted checkpoint store and expiry controls; A restore planner that distinguishes idempotent navigation from mutation

### "Find the one action I need to take on this private page, point me to it, and tell me what will happen before I click."
- **useful because:** The owner should not have to understand a dense authenticated dashboard to act safely. This capability combines page semantics, visual targeting, and spoken explanation: it identifies the relevant control, explains its consequence from nearby text, and leaves the click under the owner's control. It is more useful than merely reading the page because it converts private UI complexity into an actionable, reversible next step.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** Accessibility-tree and DOM analysis first; computer vision for unlabeled controls; realtime model gives the concise explanation and confidence level. No autonomous click unless separately requested.
- **latency:** Under 8 seconds for ordinary pages; under 15 seconds when visual grounding is required.
- **cost:** Usually <$0.03 per request, dominated by visual grounding on inaccessible interfaces.
- **security:** Inspect only the active page, identify origin and control text, and never infer a destructive consequence without showing the supporting nearby text. Do not click or submit. Avoid speaking secrets and redact values not needed to describe the action. Let the owner dismiss or request a screenshot/DOM evidence packet.
- **missing:** A grounded control locator that survives page reflow and can return a highlight rectangle; A consequence extractor that links controls to confirmation text, deadlines, and side effects; A browser overlay or screenshot annotation channel; Confidence and ambiguity reporting for pages with multiple plausible actions


## Changes it proposed to its own stack

### `new-surface` — Add a Safari toolbar command and pendant voice alias, “send this to my pendant,” that packages the active tab's visible title, origin, selected text, and a short extracted summary into a one-shot spoken delivery. It must expire after delivery and never become a persistent page archive unless separately requested.
- **owner gets:** The owner can turn a dense authenticated page into something usable while away from the Mac, with one deliberate gesture and no tab hunting or copy/paste.
- effort: Medium: Safari extension UI, selected-text extraction, relay job binding, compact summarization, and pendant audio delivery.  ·  risk: Selection may be empty or include sensitive text; show the origin and a preview before speech where practical, apply redaction rules, and drop the payload on timeout. Recovery is simply retrying from the still-open tab.
- cost: Low, typically one compact summarization call plus audio; no recurring cost when unused.  ·  latency: Aim for 3–6 seconds from toolbar click to spoken summary.
- security: Data crosses Safari to the local agent and relay only for this explicit action; no full-page persistence, origin policy required, and delivery payload should be deleted after playback.
- depends on: A functioning browser_read_page/selection extraction result path; Per-origin redaction and never-store configuration; Relay-to-pendant audio delivery using the existing pipeline/audio path


## What it asked for

_Nothing._
