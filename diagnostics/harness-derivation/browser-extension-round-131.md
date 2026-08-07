# Harness derivation — browser-extension — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Compare the details across my open logged-in tabs and tell me if anything conflicts—dates, amounts, names, or deadlines—and show me the exact evidence for each mismatch.”"
- **useful because:** The owner currently gets separate page summaries, but the dangerous mistakes are contradictions between systems (a calendar time differing from a reservation, an invoice total differing from a portal, or a changed deadline). This turns private browser access into cross-system error detection, with cited evidence rather than a vague alert.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background extraction/comparison model for open-tab normalization; reserve realtime for the owner's spoken follow-up and use the Mac only to assemble tab evidence.
- **latency:** 2–5 seconds for up to six open tabs; a spoken mismatch should arrive within one pendant turn. Most time is browser extraction, not model inference.
- **cost:** Roughly $0.01–$0.05 per comparison depending on page length; browser calls and DOM extraction dominate, with a small model doing field alignment.
- **security:** Private tab contents leave Safari and reach the relay/model. Send only selected fields and source snippets, retain them briefly, and never infer or transmit hidden form values. No mutation is needed, so no confirmation gate is required.
- **missing:** A multi-tab field normalization and contradiction detector with typed field provenance; A user-facing way to select which open tabs/accounts may be compared; A compact cited result delivered to the pendant

### "“Make a spoken, sourced explanation of the private page I’m looking at right now, focused on the part I point to, and let me ask follow-up questions without losing that exact page context.”"
- **useful because:** A logged-in page is often too dense to read while moving. The pendant becomes a private page-reading companion: the browser supplies the current DOM and visual/locator anchor, the Mac keeps the context, and the owner can ask successive questions by voice instead of repeatedly describing the page.
- **path:** browser-extension → relay-realtime → mac-planner → faculty-perception
- **model tier:** Use a small/medium extraction model for page cleanup and locator-scoped passages; use realtime only for the low-latency conversational explanation and follow-ups.
- **latency:** Initial answer in 3–6 seconds; follow-ups under 1.5 seconds when the page snapshot is already cached. Browser snapshot/extraction is the main latency.
- **cost:** About $0.005–$0.03 per initial page explanation and pennies for follow-ups; caching the normalized page avoids resending the full DOM each turn.
- **security:** Only the active tab and explicitly pointed region should be sent; redact passwords, tokens, and editable secret fields before relay. Do not click or type unless separately requested. Page URLs and snippets need short retention and deletion.
- **missing:** A reliable active-tab/pointed-region anchor from Safari (DOM locator plus optional screenshot coordinates); A page-context cache scoped to one conversation with freshness invalidation when the tab changes; Streaming TTS/audio return to the pendant for the sourced explanation

### "“Save an evidence packet for this logged-in page: the relevant excerpts, timestamp, URL, and screenshot, then draft a support or dispute message from it without sending anything.”"
- **useful because:** When an account, order, bill, or appointment is wrong, the owner needs a defensible record before the page changes. Safari can see authenticated evidence that the Mac or relay cannot; the Mac can package it locally and draft a precise message, while the pendant lets the owner trigger it hands-free.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-action
- **model tier:** Use a cheap extraction model to identify relevant fields and draft the message; realtime is only for clarifying what to include. No expensive computer-use loop is needed for read-and-package work.
- **latency:** 30–60 seconds for a complete packet including screenshot and local file; drafting can happen asynchronously while the owner continues using the Mac.
- **cost:** Approximately $0.01–$0.08 per packet, dominated by screenshot/page upload and draft generation; local storage is negligible.
- **security:** Evidence may contain names, addresses, order numbers, or financial data. Store encrypted locally with a short retention period, redact unrelated page regions, and require explicit user review before any external send. Never include cookies, credentials, or hidden inputs.
- **missing:** A browser evidence capture action that returns stable URL, timestamp, selected text, locator, and screenshot; A local encrypted evidence-bundle format with retention/deletion; A draft composer that links every claim to a captured excerpt and clearly marks the unsent message

### "“Audit the security pages of my logged-in accounts, correlate recent sign-ins, recovery settings, active sessions, and forwarding rules, and tell me what looks suspicious—with evidence and a remediation plan, but do not change anything.”"
- **useful because:** No existing summary or page-watch feature can reason about account compromise across providers. The owner needs one private, cross-account view of security drift and suspicious combinations, delivered to the pendant without exposing credentials or taking unilateral security actions.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Use a background model for structured security-field extraction and correlation; use realtime only to explain an anomaly or answer the owner's follow-up.
- **latency:** A full audit can take 1–3 minutes asynchronously; urgent anomalies should be summarized in one spoken response once extraction completes.
- **cost:** Roughly $0.05–$0.25 per audit, dominated by several authenticated page extractions and security-history text; much cheaper than a realtime model throughout.
- **security:** This handles exceptionally sensitive account data. Never transmit passwords, cookies, recovery codes, or full pages; redact unrelated messages and addresses; encrypt short-lived evidence; require explicit confirmation for any remediation such as sign-out, password reset, or forwarding-rule changes.
- **missing:** Provider-specific security-page adapters and a normalized security event schema; Cross-provider anomaly correlation rules with explainable confidence; A private, expiring security-audit report linked to source excerpts

### "“When I am on a private web app, make a temporary voice-controlled accessibility layer: read the controls and status aloud, let me say which labeled control to operate, and keep a visible transcript of what was done.”"
- **useful because:** Many authenticated sites are difficult to use from a small screen, keyboard, or voice. The browser can see semantic labels and the pendant can provide hands-free access, while the Mac keeps an auditable transcript. This is not merely page summarization: it makes unfamiliar private interfaces operable by voice.
- **path:** browser-extension → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** Use a low-cost model to map the accessibility tree into stable labels; use realtime for low-latency disambiguation and spoken interaction.
- **latency:** Control discovery under 2 seconds; each read-only query or reversible interaction under 1 second where the page is already cached.
- **cost:** About $0.005–$0.04 per interaction; most cost is repeated accessibility-tree extraction on highly dynamic pages.
- **security:** Voice commands could expose or alter private data. Mask sensitive values in spoken output, keep operations scoped to the selected tab, log exact targets, and stop before irreversible submissions unless the owner explicitly continues.
- **missing:** Stable accessibility-tree extraction and semantic element references in the Safari extension; A temporary tab-scoped voice-control session with disambiguation and expiry; A transcript/receipt view that distinguishes reads, reversible edits, and submits

### "“If I lose access to one of my logged-in devices, assemble an emergency recovery checklist from my private account pages, identify which recovery paths are still viable, and put the ordered steps on my Mac and in a short pendant briefing.”"
- **useful because:** Recovery information is scattered across provider security pages and is often discovered only after a lockout. The browser's authenticated sessions can inspect the actual current recovery routes; the Mac can store a local checklist, and the pendant can deliver the critical first steps even when the owner is away from the screen.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-judgement
- **model tier:** Use a background model to extract and rank recovery paths; use realtime only to answer a question about the generated checklist. No continuous expensive model is needed.
- **latency:** 5–10 minutes for a complete one-time inventory; later spoken retrieval should be under 2 seconds from the local checklist.
- **cost:** Approximately $0.05–$0.30 per inventory, depending on provider count; subsequent retrieval is nearly free.
- **security:** Recovery contacts, phone numbers, backup codes, and device identifiers are highly sensitive. Store encrypted locally, redact codes from model context and audio, never copy or expose secret values unnecessarily, and require explicit approval before changing recovery settings.
- **missing:** Provider-specific recovery-state extraction without reading secret codes; An encrypted local emergency packet with offline pendant-safe summaries; A dependency graph showing which recovery path depends on which device/account


## Changes it proposed to its own stack

### `integration` — Add a user-visible “compare these tabs” browser action: capture normalized, provenance-linked fields from 2–6 selected authenticated tabs, run contradiction checks (date, amount, identity, status, deadline), and return a compact mismatch card with source URL, DOM locator, excerpt, and screenshot crop. Keep the active comparison attached to the pendant conversation for follow-up questions.
- **owner gets:** It catches the real-world errors that separate summaries miss and lets the owner ask “which one is wrong?” while the exact private evidence is still available.
- effort: Medium-high: browser extraction and tab selection exist, but field normalization, provenance cards, mismatch scoring, and pendant follow-up state need implementation.  ·  risk: Dynamic pages can produce false mismatches or stale values. Show both source excerpts and freshness timestamps, allow dismiss/recheck, and never mutate either page.
- cost: Low per use (small extraction/comparison model, roughly $0.01–$0.05); screenshot crops and snippets are short-lived.  ·  latency: Approximately 2–5 seconds for six tabs; cached normalized fields make follow-ups near realtime.
- security: Authenticated excerpts leave Safari. Restrict to explicitly selected tabs, redact secrets/editable fields, short retention, and do not send cookies or full DOM.
- depends on: A browser action that accepts explicit tab IDs and returns typed extracted fields with locators; Conversation-scoped cache with freshness invalidation when any compared tab changes; A compact mismatch-card renderer and audio response path


## What it asked for

_Nothing._
