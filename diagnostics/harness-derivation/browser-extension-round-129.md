# Harness derivation — browser-extension — round 129

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live Safari access** — Safari bridge is online with 3 tabs; Gmail tab is authenticated and visible to browser_list_tabs, but browser_read_page and browser_snapshot both fail with 'Extension does not have access to this frame.'
  - evidence: POST /execute actions browser_list_tabs and browser_read_page at 2026-08-07T18:02:47–18:02:51Z

## Capabilities it proposed

### "“Read this private webpage to me, but keep my data on the Mac: explain the active Safari page aloud through the pendant, cite the exact headings/fields you used, and let me ask follow-ups without reopening or sending anything.”"
- **useful because:** The browser is the only node that can see authenticated pages, while the pendant is the only node the owner can query hands-free. A local extraction/citation capsule would make private pages genuinely conversational without leaking full page contents to the relay or taking actions.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Realtime for the short spoken explanation and follow-ups; a cheaper background model creates the local page digest and citation anchors.
- **latency:** First answer under 5 seconds after the active tab is captured; follow-ups under 2 seconds from the cached capsule.
- **cost:** About $0.01–$0.04 per page session; most cost is one small realtime response, not repeated full-page context.
- **security:** Authenticated DOM stays on the Mac; send only the selected digest and bounded citation snippets to the relay. Never include passwords, tokens, hidden inputs, or compose/send controls. No mutation is offered.
- **missing:** A Safari content-script fallback for pages where the extension currently reports “does not have access to this frame” (observed on Gmail); A local citation-capsule format with field redaction and short-lived retention; Pendant playback/control for navigating cached citations

### "“Audit the security and privacy settings of the accounts I already have open in Safari, compare them with my stated preferences, and give me a prioritized report with exact evidence—do not change any setting.”"
- **useful because:** No other node can inspect logged-in account security pages. This turns the browser’s private reach into a periodic, read-only safety check rather than another inbox summary, catching weak recovery options, unexpected sessions, or exposed profile data.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for multi-page extraction and comparison; realtime only to answer the owner’s follow-up questions.
- **latency:** 3–10 minutes for a full audit; a concise spoken result when complete, with progress available if the owner walks away.
- **cost:** Roughly $0.05–$0.20 per audit depending on page count; browser extraction and report synthesis dominate, not voice.
- **security:** Treat all discovered account/security data as highly sensitive. Keep raw pages on the Mac, transmit only redacted findings and source URLs/labels, encrypt stored reports, and never click a setting or revoke a session. The report must explicitly distinguish observed evidence from inference.
- **missing:** A browser audit recipe library for common account-security pages and semantic selectors; Local secret/PII redaction before relay submission; A durable report artifact with evidence snippets and expiry

### "“If you cannot read the private page I asked about, diagnose the browser failure, recover using a safe alternate view (reader, print, or accessibility tree), and either answer from verified text or tell me exactly what is blocked—never guess.”"
- **useful because:** Today Safari exposes Gmail tabs but the bridge fails with “does not have access to this frame,” so the system can see a tab exists yet cannot use it. An explicit recovery behavior prevents confident nonsense and makes the one unique browser capability dependable across real sites.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Cheap classifier for failure diagnosis and recovery choice; realtime model only when a verified page excerpt needs spoken explanation.
- **latency:** Try two safe recovery paths within 15 seconds, then give a plain-language blocker and recovery suggestion.
- **cost:** Under $0.02 per failed read; most work is local browser actions and accessibility/print extraction.
- **security:** Recovery must remain read-only, preserve the existing login, and never upload screenshots or DOM to third-party services. Do not bypass CAPTCHAs, paywalls, or permission prompts; report those as blockers.
- **missing:** Safari extension permission/frame-access diagnostics and a content-script or accessibility-tree fallback; A print/reader-view extraction action with tab affinity; Typed failure reasons surfaced to the voice agent

### "“Save the receipt, confirmation, or warranty page I’m viewing in Safari into my private evidence locker, then let me retrieve it later by saying ‘find the warranty for my headphones’ and hear the relevant date, amount, and link from the pendant.”"
- **useful because:** Important proof is trapped in authenticated webpages and disappears into browser history. This would turn a one-time private page into a durable, searchable record available hands-free, without requiring the owner to forward email or manually copy details.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background extraction model for structured fields and deduplication; realtime only for the owner’s short retrieval query.
- **latency:** Capture in under 8 seconds; later retrieval in under 3 seconds, with an explicit ‘not found’ rather than guessing.
- **cost:** About $0.01–$0.05 per capture and pennies per retrieval; encrypted local storage dominates implementation, not inference.
- **security:** Receipts can expose addresses, order numbers, and payment fragments. Encrypt the evidence store on the Mac, redact payment secrets, preserve source URL and capture time, and require a local pendant presence or Mac unlock for retrieval. Never transmit the full page to the relay.
- **missing:** An encrypted, schema-versioned local evidence vault with retention and deletion controls; Browser extraction recipes that classify receipts, warranties, tickets, and confirmations; A pendant query/index protocol that works when the Mac is temporarily offline

### "“Compare the personal details shown in the private sites I have open—name, address, phone, and subscription status—and tell me where they disagree, with the exact source for each value. Do not edit anything.”"
- **useful because:** People’s accounts drift silently after moves, new phone numbers, or billing changes. Only the authenticated browser can inspect these private values, while the Mac can normalize them and the pendant can deliver a concise discrepancy list without exposing full pages.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for field extraction, normalization, and contradiction detection; realtime for the final short spoken report.
- **latency:** Under 60 seconds for up to six open sites; no page mutation.
- **cost:** Approximately $0.03–$0.12 per comparison, depending on page count and OCR/accessibility fallback use.
- **security:** This is highly sensitive identity data. Keep raw values on the Mac, hash or redact them in relay context, show only masked values by default, and allow the owner to delete the comparison artifact. Never infer a value from a page that was not successfully read.
- **missing:** A schema for normalized identity fields with confidence and provenance; Cross-tab extraction orchestration that handles different site layouts; Local redaction/masking and deletion-aware comparison storage

### "“Before I enter a password, payment detail, or one-time code into the page I’m viewing, inspect the real destination and surrounding page context, tell me who will receive it and why it looks trustworthy or suspicious, and keep the fields untouched.”"
- **useful because:** The browser can see login state and page context that the relay cannot. A spoken, page-grounded preflight would catch lookalike domains, unexpected redirects, and risky payment forms at the moment of greatest consequence, without pretending to be an absolute security guarantee.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Fast local rules and reputation checks first; realtime model only to explain ambiguous evidence in one short spoken response.
- **latency:** Under 2 seconds for known domains; under 8 seconds when redirect and certificate metadata need inspection.
- **cost:** Usually below $0.01 per check; uncommon ambiguous pages may require a small model call.
- **security:** Never capture or transmit the secret field values. Inspect only origin, redirect chain, form action, visible labels, and browser security metadata. Clearly label uncertainty and do not block or auto-submit on the owner’s behalf.
- **missing:** Extension access to form-action and redirect/security metadata without reading field values; A local domain/reputation cache with expiration; A pendant interaction that can warn while leaving the current page and focus unchanged


## Changes it proposed to its own stack

### `browser-harness` — Add a verified read-only fallback chain for Safari: when browser_snapshot/read_page returns frame-access failure, collect the tab’s accessibility tree or print/reader representation through the extension, tag the result with tabId/URL/timestamp, and return a typed blocker if all fallbacks fail. Add a self-test page and expose the extension’s host-permission/frame-access diagnosis in the receipt.
- **owner gets:** Private pages stop being a silent dead end. The owner gets either grounded text from the logged-in tab or an honest explanation of why it cannot be read, instead of an empty or hallucinated answer.
- effort: Medium: Safari extension content-script/permissions work plus bridge result typing and tests across Gmail and a normal page.  ·  risk: A broader host permission could increase exposure; keep extraction read-only and scoped to the requested tab, with no raw DOM persistence. If the fallback misbehaves, disable it per-origin and retain the existing failure path.
- cost: Negligible API cost; modest engineering cost. Accessibility/print extraction is local.  ·  latency: Adds up to two local fallback attempts, typically 1–5 seconds; successful ordinary pages remain unchanged.
- security: Requires explicit host permissions and stronger redaction boundaries, but avoids sending raw authenticated DOM off-device.
- depends on: Safari extension host/frame permission diagnostics; Typed browser failure results in browserBridge.js; Local redaction before relay context


## What it asked for

_Nothing._
