# Harness derivation — browser-extension — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 9 tabs, including authenticated Gmail and X; POST /execute browser_list_tabs and browser_read_page both completed successfully. The read_page action addressed the active X tab despite a tabId field, so tab targeting needs explicit validation before sensitive reads.
  - evidence: POST /execute 2026-08-08 returned 9 tabs (Gmail tab 901464, active X tab 1163292); browser_read_page result provenance tabId=1163292 and redaction secret=0 sensitive=0.

## Capabilities it proposed

### "Watch this logged-in page for me and, when something materially changes, tell me exactly what changed and carry out the harmless next step on my Mac."
- **useful because:** This is the browser's unique reach turned into an end-to-end outcome: authenticated pages are monitored while the relay sleeps, noise is semantically filtered, the pendant gives an offline alert, and the Mac can resolve the routine consequence. It avoids making the owner repeatedly reopen a portal.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Background/cheap model for scheduled page snapshots and semantic diffs; realtime only for the owner's spoken follow-up; local Mac planner for the reversible next step.
- **latency:** Snapshot polling can be minutes behind; alert generation under 10 seconds after a detected change; spoken follow-up under 2 seconds once the owner responds.
- **cost:** Low background cost: one small extraction/diff call per poll plus one realtime turn only on escalation. Browser traffic and page text dominate, so send hashes/structured fields after initial extraction rather than full pages.
- **security:** Authenticated page text must remain origin-scoped and be redacted before relay persistence or speech. Ship empty per-origin rules and require the owner to configure allowed origins, speakable categories, and never-store fields. Never submit/send/purchase automatically; show the proposed Mac action and require the owner's existing explicit go-ahead for genuinely irreversible work.
- **missing:** A production page-watch scheduler that stores per-origin rules and semantic field hashes; Reliable browser action tab targeting (the current read_page result fell back to the active tab); Relay-to-pendant alert delivery over the currently attached USB path and a first-run watch setup UI; An escalation contract that turns a detected diff into a typed reversible Mac action

### "I'm looking at something in Safari—let me ask the pendant questions about the exact page or selection without sending the page to the cloud or losing my place."
- **useful because:** The owner can turn any authenticated, dense page into a hands-free conversation: 'what is the cancellation deadline?', 'compare these two rows', or 'what should I do next?' The browser supplies private visibility, the Mac performs local extraction, and the pendant supplies the lowest-friction interface while the owner is away from the keyboard.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Local Mac extraction/vision first for DOM text, selection, and screenshots; use the cheaper relay model for short question answering over the extracted slice; realtime tier only for turn-taking and spoken output.
- **latency:** Under 1.5 seconds for DOM selection questions; under 4 seconds for a screenshot/vision question; never upload the full authenticated page by default.
- **cost:** Usually one small local extraction and a short model turn; screenshot questions add one vision call. Cost is bounded by the selected region, with a hard byte/token cap and a 'page not selection' explicit owner command.
- **security:** The extension must identify the exact tab and selection, not silently use the active tab (current live behavior did that). Do not persist page text; attach an ephemeral capsule with origin, selection bounds, and content hash, redact secrets locally, and expose origin/category policy before speech. Questions are read-only and do not trigger clicks or form submission.
- **missing:** A pendant-to-browser 'current page' correlation protocol carrying tabId, selection, and expiry; A local extraction endpoint that returns selected DOM text/accessibility tree or a cropped screenshot; Explicit tabId enforcement and failure when the requested tab is unavailable; A low-latency relay event that asks a question against the ephemeral browser capsule

### "Save exactly what I'm looking at in Safari for later, including the useful passage and why I cared, then reopen it from my pendant tomorrow—even if the Mac has been restarted."
- **useful because:** Authenticated research and work pages disappear into tabs today. This turns a spoken interruption into a durable, searchable handoff: Safari contributes the private page/selection, the relay stores only a bounded encrypted capsule, the Mac restores the URL and scroll/selection when possible, and the pendant recalls it hands-free.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** Cheap local extraction and embedding for the selected passage; background model for a one-line reason/title; realtime only when the owner asks to recall or reopen it.
- **latency:** Capture under 2 seconds; spoken recall under 3 seconds; restoration may take 5 seconds including browser navigation and session recovery.
- **cost:** Small one-time extraction/embedding per bookmark; no recurring model cost. Storage and authenticated page fetches dominate, with a strict passage-length cap.
- **security:** Persist origin, URL, selection, and user-supplied reason separately from content, with per-origin never-store rules and expiry. Never store cookies or full page text; encrypted capsule should be deleted on request. Reopening is reversible navigation, but any page action after restore remains read-only until separately requested.
- **missing:** A first-class browser bookmark capsule schema with origin policy, expiry, selection locator, and content hash; A relay-backed capture index that the pendant can query while offline alerts remain local; Browser restoration that can reopen a tab and best-effort scroll to a DOM anchor; A voice intent connecting 'save this' to the active Safari tab rather than an untrusted current-tab fallback

### "When I say “verify this,” inspect the authenticated page I am viewing, compare the key facts against the authoritative source and its last-known snapshot, and tell me whether the claim is current, changed, or unverified—with a dated evidence card I can reopen."
- **useful because:** This gives the owner a trustworthy answer for invoices, account notices, travel rules, and other private pages instead of a confident paraphrase of stale content. The browser is the only node with the login; the relay can explain the result through the pendant; the Mac can retain a small, auditable evidence card rather than a whole page.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Local extraction and deterministic field comparison first; cheap background model for normalization; realtime only to explain the verdict aloud.
- **latency:** Under 5 seconds for one page and one known source; up to 15 seconds for a multi-source comparison.
- **cost:** One small extraction/comparison call per verification, dominated by authenticated page capture; retain hashes and selected facts, not full page bodies.
- **security:** Never invent authority or treat search results as proof. Store origin, timestamp, content hashes, extracted claims, and source URLs with redaction and expiry; never speak configured-secret categories. The evidence card must visibly distinguish 'unchanged,' 'changed,' and 'could not verify.'
- **missing:** A browser evidence-card primitive with signed timestamps and content hashes; A local comparison/extraction worker able to address multiple explicit tabs or URLs; Owner-configured authoritative sources and categories, initially empty; Pendant speech for a structured verdict plus a way to reopen the evidence card

### "If a private website logs me out, changes its security challenge, or silently stops showing fresh data, tell me on the pendant what broke and guide me through restoring the session—without ever reading the site's content aloud."
- **useful because:** Authenticated automation currently fails opaquely. The owner should know whether a task failed because the site changed, the session expired, or the Mac/browser is offline, and be able to recover deliberately instead of trusting an old cached answer.
- **path:** browser-extension → relay-realtime → mac-planner → mac-vision
- **model tier:** Deterministic browser/session health checks and cheap classification; realtime only for the short spoken diagnosis and guided recovery.
- **latency:** Detect on the next scheduled check; diagnosis under 3 seconds; recovery remains interactive and may take as long as the site requires.
- **cost:** Very low: status/DOM checks, no full-page model call unless the owner asks for help. Costs are dominated by occasional screenshot guidance during recovery.
- **security:** Inspect only login/session indicators and freshness metadata until the owner explicitly asks for content. Never transmit passwords, one-time codes, cookies, or challenge answers to the relay; let Safari render the recovery UI and keep sensitive fields local.
- **missing:** A session-health classifier that distinguishes expiry, challenge, consent wall, site outage, and stale DOM; Browser extension events for navigation/login/freshness failures; A pendant alert payload that says what recovery is needed without leaking site content; A Mac-vision recovery mode that highlights but does not submit security fields

### "Let me ask, “what did I miss in my open tabs?” and get a private, deduplicated briefing of only unread or materially changed items across my logged-in tabs, with each item linked back to its exact tab and location."
- **useful because:** The owner can leave a research or work session and recover the important deltas without manually reopening nine tabs or having the assistant scan public substitutes. This is a cross-tab private briefing, not a generic news summary: it preserves provenance and makes the browser's authenticated context useful through the day.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** Local DOM/accessibility extraction and deterministic unread/change detection; background small model for clustering and priority ranking; realtime only to speak the compact briefing.
- **latency:** On-demand briefing in under 10 seconds for up to 20 tabs; incremental indexing in the background.
- **cost:** One cheap clustering call over bounded snippets; local extraction and tab navigation dominate. Never send full pages when unread markers and selected fields suffice.
- **security:** Respect per-origin read/extract/redact/never-store configuration, ship empty for unknown origins, and speak only categories explicitly allowed. Keep provenance (origin, tab, locator, timestamp) alongside each claim; never click messages or mark items read unless separately requested.
- **missing:** A multi-tab extraction/indexing job with bounded snippets and unread markers; A semantic deduplicator that preserves source provenance and confidence; Stable locators for returning to the exact message/section in a tab; A browser-to-pendant briefing event with item-by-item navigation


## Changes it proposed to its own stack

### `browser-harness` — Make every browser read/inspect/click/type action require and enforce an explicit tabId (or an explicit session id resolved to a tab); if the requested tab is missing, return an error instead of falling back to the active tab. Include the resolved tabId and origin in the receipt and browser evidence capsule.
- **owner gets:** The assistant will stop answering from the wrong page or touching the wrong account. This matters most when Gmail, X, and multiple failed/example tabs are open together, and it makes private authenticated browser help trustworthy enough to use hands-free.
- effort: Moderate: thread tabId through action validation, extension command payload, result provenance, and session recovery; add tests with nine simultaneous tabs and a changed active tab.  ·  risk: Some existing callers omit tabId and will fail rather than silently work; migrate them to the default session explicitly and show a clear 'which tab?' response. Recovery is straightforward because no page is mutated on a missing-target error.
- cost: Negligible API cost; small implementation/test effort and a few bytes per command receipt.  ·  latency: No meaningful latency change; one validation step may save a costly wrong-page model turn.
- security: Strong positive: prevents cross-origin/account confusion and accidental actions on a different authenticated tab. Does not add a permission gate or reduce the owner's maximum access.
- depends on: Define default browser session semantics for voice requests; Expose tabId/sessionId in pendant-to-browser correlation events


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely usable now: it is online with 9 tabs, including authenticated Gmail and X. I verified POST /execute browser_list_tabs and browser_read_page live. I recorded three owner-facing capabilities: authenticated change-to-action escalation, pendant questions about the exact private page/selection, and interruption-safe authenticated research capsules; plus a concrete browser-harness change to reject implicit active-tab fallback. The strongest immediate value is private page Q&A and later resumption, because no other node can see those logged-in pages. I still need explicit tab/session correlation from the pendant voice path, a local selected-DOM/screenshot extraction primitive, persistent page-watch/capsule policy with per-origin rules, and—critically—tabId enforcement: my live read request carrying tabId=901464 returned the active X tab (1163292), proving the current fallback is unsafe.

**Biggest unknown:** Whether the relay voice event currently carries enough browser identity (tabId, origin, selection/locator, expiry) to bind a spoken request to the page the owner means. Until that contract exists, authenticated browser actions must remain explicit and should never infer the active tab.

