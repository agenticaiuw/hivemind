# Harness derivation — browser-extension — round 141

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser** — Safari extension is live with 9 tabs, including authenticated Gmail inbox and OpenAI API billing overview; active tab is OpenAI billing. Browser actions execute successfully through POST /execute with browser_* action types.
  - evidence: POST /execute {actions:[{type:'browser_list_tabs'}]} returned 200, 9 tabs, extension commandId browser_86aa9ef8-076f-44a7-a029-d4818b966fd7.

## Capabilities it proposed

### "Is anything in my logged-in web accounts showing signs of a billing or security problem? Compare the evidence across the pages already open, explain why it matters, and leave me a ready-to-review incident packet without changing or sending anything."
- **useful because:** A single suspicious notice is often ambiguous; correlating an authenticated billing page, inbox notices, and security/account tabs can distinguish a real compromise or charge from noise. Safari can see the private evidence, the Mac can preserve a review packet, and the pendant can interrupt the owner only for a high-confidence issue.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for multi-tab extraction and correlation; realtime only to deliver a short alert or answer follow-up questions
- **latency:** 30–90 seconds for the first investigation; under 3 seconds for a spoken alert once the packet exists
- **cost:** Usually 1–3 background model calls plus browser bridge latency; dominated by authenticated page extraction, not audio
- **security:** Page content, account names, and financial/security details leave Safari for local processing and possibly the relay. Ship an explicit per-origin and per-category policy (empty until owner configures it), redact secrets before model calls, retain only hashes/snippets and URLs by default, and never send or submit remediation. The owner should confirm before any password, dispute, or support action.
- **missing:** A cross-tab security/billing correlation job with typed evidence categories and confidence scoring; Local extension-side secret/credential redaction before extracted DOM leaves Safari; An encrypted, expiring incident-packet store and pendant alert linkage; Owner-supplied per-origin and per-category read/speak/persist configuration

### "Which of my open private tabs are safe to close? Check for unsaved drafts, pending forms, active sessions, and duplicate or failed pages, then give me a spoken list and close only the ones I explicitly name."
- **useful because:** A crowded Safari window hides real risk: a draft or checkout can be lost among duplicate error tabs, while closing every tab destroys useful authenticated context. The extension can inspect tab state that the Mac and relay cannot see, and the pendant makes the decision hands-free.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for tab triage and state classification; realtime for the short spoken inventory and follow-up close commands
- **latency:** 10–30 seconds for 9–20 tabs; under 2 seconds to close a named tab and return a receipt
- **cost:** One cheap classification call over compact tab/page metadata, with extra reads only for ambiguous tabs; browser latency dominates
- **security:** Reading private tabs may expose drafts and account details to local processing/relay. Default to metadata and targeted state signals, redact content, store no page text, and let the owner configure origins/categories that may be inspected. Closing is reversible only if a tab can be restored; never close unsaved forms or drafts automatically.
- **missing:** Browser tab triage classifier with unsaved-state and pending-transaction signals; A close-tab action with restore metadata and receipt; Compact spoken inventory and named-tab command routing from the pendant; Owner-configurable per-origin inspection rules

### "Before you inspect my open Safari tabs, tell me exactly what each tab would expose, what will be redacted, what may be spoken through the pendant, and how long any evidence will remain; let me change those rules for this task only."
- **useful because:** Private browser automation is otherwise a trust fall. An owner-facing exposure preview makes the boundary tangible per tab and per request, especially when Gmail, billing, and social accounts are open together, without requiring the owner to understand extension internals.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** cheap local policy evaluation for the exposure map; realtime only to answer the owner's spoken policy edits and confirm the resulting summary
- **latency:** 1–3 seconds to render a 9-tab exposure map; immediate updates after a rule edit
- **cost:** No model call for standard origins and rules; at most one small classification call for unknown page categories
- **security:** The preview itself must not quote page contents or reveal hidden account data. Policies ship empty/conservative, are explicit and inspectable, and task-scoped overrides expire automatically. The system should record policy decisions and redaction counts, not raw text; edits affect the current task only unless the owner saves them.
- **missing:** A browser exposure-map endpoint that combines tab metadata, origin rules, redaction policy, speech policy, and retention TTL; Extension-side preflight that evaluates a planned read before dispatch; Task-scoped policy overrides carried through relay, Mac, and pendant speech; A compact pendant-friendly policy summary and expiration cue

### "While I’m away from my Mac, keep a private, local timeline of meaningful changes in the authenticated tabs I currently have open—new inbox items, billing totals, account warnings, or a draft becoming submitted—and tell me exactly what changed when I return, even if the tab has since been closed."
- **useful because:** Today a page watcher can report a later state, but it cannot explain the sequence of changes across the owner’s currently open private work or recover a change that disappeared when a tab closed. A local event timeline gives the owner an answer to “what happened while I was gone?” without continuously shipping page contents to the relay.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** local extension heuristics and compact hashes continuously; background model only when the owner requests a summary; realtime for a short return-home spoken digest
- **latency:** Under 1 second per tab mutation check locally; 5–20 seconds to summarize a day’s timeline; immediate pendant alert only for owner-configured urgent categories
- **cost:** Near-zero API cost during watching; storage and local CPU dominate, with one background call per requested digest
- **security:** Raw DOM and drafts must stay in Safari or encrypted Mac storage; store redacted field-level diffs, hashes, origin, and timestamps with strict TTL. Never infer that a draft was sent from disappearance alone—label uncertainty. The owner must explicitly choose tabs/origins and categories, and alerts must obey speak/retain rules.
- **missing:** An extension-local mutation/event journal that survives tab closure and records redacted semantic diffs; A bounded encrypted timeline store with TTL and compaction; A return-time summarizer and pendant alert channel for event batches; Explicit owner configuration for watched tabs, categories, speech, and persistence

### "Make a tamper-evident record of what this logged-in page showed me at this moment, including the exact visible fields and account identity, so I can later prove what I saw without preserving my whole browsing session."
- **useful because:** For a disputed charge, cancellation, support case, or changing dashboard, a normal screenshot is weak evidence: it lacks trustworthy time, origin, and proof that the record was not edited later. The browser can capture the authenticated view while the Mac signs and stores a minimal evidence bundle; the pendant can read its receipt ID without exposing the page aloud.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background/local deterministic capture and hashing; realtime only if the owner asks for a spoken receipt or explanation
- **latency:** 1–5 seconds to create a bundle; under 2 seconds to retrieve metadata later
- **cost:** No model call for capture; storage and optional OCR are the dominant costs
- **security:** Evidence may contain private financial or account data. Encrypt it locally, retain only owner-selected regions, redact secrets before any relay transfer, include origin/session/account attestation and clock source, and expose deletion/expiry. A cryptographic signature proves bundle integrity, not that the website itself was truthful; state that limitation.
- **missing:** Extension capture of selected DOM regions plus screenshot/accessible text with stable locators; Mac-side encrypted evidence vault with hash chain, trusted timestamp, and exportable verification manifest; Account-identity and origin attestation in the signed bundle; A pendant-friendly receipt lookup and local deletion control

### "Before I submit this private web form, simulate the submission in a disposable browser sandbox: show every field and network-side effect it would trigger, identify hidden or changed values, and tell me whether the real submission is safe without contacting the real service."
- **useful because:** A form preview shows visible text but cannot reveal JavaScript-added fields, redirects, analytics payloads, or side effects triggered before the final click. A sandbox would let the owner understand a high-impact authenticated action without risking a purchase, message, deletion, or account change.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background deterministic browser replay/network diff; realtime only to summarize the risk and answer follow-up questions
- **latency:** 10–60 seconds depending on form complexity; no real-world side effect until the owner separately proceeds
- **cost:** Higher local CPU and temporary browser storage; one optional background model call to explain the diff, with no need to send page contents by default
- **security:** Sandbox isolation must be real: block external network writes, payment APIs, emails, uploads, and service workers; use synthetic tokens and scrub credentials. Some sites cannot be faithfully simulated, so label unknown behavior rather than claim safety. The owner must still explicitly initiate the actual submission afterward.
- **missing:** An extension-controlled disposable tab/context with network interception and synthetic credential/token substitution; A side-effect classifier that distinguishes reads, writes, redirects, uploads, and third-party calls; A DOM/network before-after diff rendered as a reviewable artifact and spoken summary; A clean handoff from sandbox state to the real tab without replaying unsafe actions


## Changes it proposed to its own stack

### `browser-harness` — Add a local, extension-side semantic privacy firewall that classifies DOM nodes and extracted text before any browser result is posted: credentials, payment numbers, session tokens, personal identifiers, and owner-configured categories are replaced with stable placeholders while non-sensitive text, labels, and provenance remain. Return a reversible redaction manifest so the model can say what was withheld. Apply the same filter to page reads, snapshots, form previews, and screenshots via OCR; never infer permissions from the classifier—just make the transformation observable and configurable per origin.
- **owner gets:** The owner can finally ask the system to inspect logged-in pages without silently shipping passwords, tokens, or card data to the model. He gets useful answers with clear '[withheld]' evidence instead of choosing between total access and total refusal.
- effort: Medium-high: extension DOM walker and screenshot OCR/redaction, shared policy schema, result-envelope changes, tests against Gmail/billing/forms, and a local policy editor.  ·  risk: False negatives could leak sensitive text; false positives make answers less useful. Fail closed for unknown credential-like fields, expose redaction counts and placeholders, and allow the owner to inspect/adjust per-origin rules. Recovery is disable-per-origin or fall back to local-only extraction.
- cost: Small ongoing CPU cost in Safari and modest storage for policy/manifests; no meaningful API increase, and potentially lower model-token cost from removing boilerplate/secrets.  ·  latency: Typically 50–300 ms per page result; screenshot OCR can add 1–3 seconds.
- security: Strongly improves least-data transfer, but the classifier and policy code become security-critical; keep raw DOM in the extension process only and never log it.
- depends on: A versioned per-origin/per-category policy configuration that ships empty and is explicitly filled by the owner; Browser result envelopes carrying redaction manifests and provenance; A local-only OCR/redaction implementation for screenshots

### `browser-harness` — Add an account-identity attestation to every authenticated browser result and action plan. The extension should derive only visible, non-secret identity markers (origin, profile/avatar label, masked email or account switcher state) from the current tab, bind them to tabId/sessionId, and detect when navigation or an account switch changes that identity. Surface an explicit 'account changed/unknown' event to the Mac planner and pendant, and include the attestation in receipts and drafts so a multi-tab task cannot silently mix identities.
- **owner gets:** The system stops confusing two accounts on the same site—personal versus work Gmail, the wrong billing organization, or a stale tab—before it gives an answer or prepares a change. The owner gets a plain-language account label attached to every private-web result, not an opaque tab number.
- effort: Medium: extension adapters for generic profile/account UI, typed attestation in browser result envelopes, change detection on navigation, and planner/receipt display. Start with generic visible-label heuristics and add site adapters only when the owner configures an origin.  ·  risk: Some sites hide identity or render it dynamically, producing unknown rather than a false positive; labels can be spoofed by page content. Treat unknown as an observable uncertainty (not a hard execution gate), show the source locator, and let the owner correct the label. Recovery is refresh/reinspect the tab.
- cost: Negligible API cost; 1–2 KB metadata per browser result and small extension DOM work.  ·  latency: Under 100 ms for visible account markers; dynamic sites may require one extra read.
- security: Improves auditability without sending credentials. Mask identifiers by default and never expose cookies, tokens, or full account numbers.
- depends on: Typed browser result/provenance envelopes; A per-origin configuration surface for identity selectors and masking; Receipt UI that displays tab, origin, and identity attestation


## What it asked for

_Nothing._
## Its own summary

Safari is no longer an empty harness: the real extension is online with 9 tabs, including authenticated Gmail and OpenAI billing, and POST /execute browser actions work. This round recorded a cross-account billing/security incident investigator, account-identity attestations bound to each tab/session, a browser tab safety/closure triage, and an owner-facing per-tab exposure preview. The privacy-firewall variant was recorded but flagged as close to the previous egress-filter idea, so it should not be repeated. I also informed mac-vision that Safari control is through POST /execute and the extension bridge.

**Biggest unknown:** The owner has not supplied the per-origin and per-category policy that determines what authenticated content may be read, spoken, persisted, or retained. The next useful step is to expose that as an empty, task-scoped configuration and ask the owner to fill the first few origins—not to guess them.

