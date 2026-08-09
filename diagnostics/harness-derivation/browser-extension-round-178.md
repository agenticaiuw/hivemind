# Harness derivation — browser-extension — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at, and what do I need to do next?” while I have a page open in Safari."
- **useful because:** This is the single most valuable browser-only capability: the pendant can answer about the authenticated page already in front of the owner, even when the cloud cannot log in. It reads the current tab, correlates it with the owner's local calendar/files when relevant, and speaks a short answer with the exact page section it used. Page text is ephemeral by default and is not added to memory.
- **path:** pendant → browser → mac-bridge → relay-realtime
- **model tier:** Use the realtime tier only for the final short spoken answer; use the cheaper Mac planner for DOM extraction, section finding, and local-context lookup, with no model call for obvious headings/links.
- **latency:** 2–5 seconds after the button/voice request; browser extraction dominates, with a 10-second fallback that returns the page title and detected headings.
- **cost:** Usually one small planner call plus one short realtime response; roughly $0.01–$0.04 depending on page size. DOM pruning and heading extraction keep context cost bounded.
- **security:** The browser is the only component that sees authenticated content. Send only the selected page section and URL/title to the planner, redact passwords/payment fields, never persist raw DOM, and expose an inspectable per-origin rule shipped empty until the owner configures it. Do not click or submit as part of this read operation.
- **missing:** A reliable POST /execute browser action path callable by the planner (currently the route is not introspectable via GET); Current-tab targeting and DOM section extraction with field-type redaction; A transient browser-result envelope carrying source anchors to the spoken response

### "“Fill this web form from the details in my local files, check every field, and show me exactly what would be submitted—do not submit it.”"
- **useful because:** Authenticated forms are where browser access saves real time and errors are costly. The browser can fill fields behind the owner's login, the Mac can source structured values from local files, and a verifier can detect missing/invalid fields and produce a human-readable before/after diff. The owner gets a ready-to-send form without losing control of the irreversible final action.
- **path:** browser → mac-bridge → relay-realtime → pendant
- **model tier:** Cheaper background planner extracts candidate values and maps labels to fields; realtime is used only to speak the concise diff or answer a correction. Deterministic browser validation handles required fields and formats.
- **latency:** 10–20 seconds for a normal form, with progress updates on the pendant; never wait indefinitely on a single page script.
- **cost:** One planner call over redacted local values and field labels, about $0.01–$0.05; browser actions and deterministic validation dominate latency rather than token cost.
- **security:** Never copy passwords, CVV, or hidden tokens into model context. Keep values in the local agent, redact sensitive categories using existing origin/redaction policy, and retain only a short field-name/status receipt. Stop before submit and speak the exact destination and changed fields; owner may then issue an explicit separate submit command.
- **missing:** A browser action result schema that returns field labels, values masked by category, native validation errors, and a stable form fingerprint; Local field-value extraction with origin/category redaction; A cross-surface draft receipt that the pendant can replay after the browser tab changes

### "“Compare the two open authenticated tabs and tell me which information is newer or contradictory.”"
- **useful because:** Owners routinely have a portal, confirmation email, and document open at once. No public search can see those sessions. The browser extension can extract the relevant sections from both tabs, the Mac can normalize dates and identifiers, and the relay can explain the contradiction through the pendant instead of forcing visual tab switching.
- **path:** browser → mac-bridge → relay-realtime → pendant
- **model tier:** Use deterministic extraction for dates, amounts, identifiers, and headings; use a cheaper planner to align sections and detect conflicts; reserve realtime for the final spoken decision and one follow-up question.
- **latency:** 5–12 seconds for two ordinary pages; return partial results if one tab is slow or has expired, explicitly naming the unavailable tab.
- **cost:** About $0.01–$0.04 per comparison after DOM pruning; the main cost is two browser extractions, not the final speech.
- **security:** Keep raw page bodies local to the Mac agent where possible; send only aligned snippets and metadata to the model. Mask account numbers and payment data, apply per-origin redaction rules, and do not write either page into durable memory unless the owner explicitly asks to save an evidence packet.
- **missing:** A browser action that addresses two specific tab/session IDs in one request and returns bounded excerpts; Deterministic date/amount/identifier normalization and contradiction scoring; A spoken answer format that names each tab and quotes a short source anchor without leaking secrets

### "“Use my logged-in Safari, but keep the page contents on my Mac; tell me only the answer I asked for.”"
- **useful because:** The owner can access private portals without making their authenticated page text part of a cloud prompt. A local Mac-side extractor would answer targeted questions, returning only a minimal fact and provenance to the relay and pendant. This makes browser access trustworthy enough for everyday use, not merely technically possible.
- **path:** browser → mac-bridge → relay-realtime → pendant
- **model tier:** Run DOM selection, OCR, and sensitive-field detection locally with a small model or deterministic rules. Use the realtime tier only on the already-redacted answer and never on the page body.
- **latency:** 3–8 seconds for a targeted question; if local extraction cannot isolate an answer, say so rather than uploading the whole page.
- **cost:** Usually below $0.01 in API cost because only a short redacted answer reaches the realtime model; local CPU is the dominant cost.
- **security:** Raw DOM, screenshots, cookies, and form values stay on the Mac. The local extractor needs an explicit per-origin allowlist supplied by the owner, field-level redaction, short-lived buffers, and an audit receipt showing what left the device. No page text is persisted by default.
- **missing:** A Mac-local extraction/redaction worker that can answer against DOM and screenshot data without cloud transfer; A result contract distinguishing local-only evidence from text permitted to leave the Mac; Per-origin configuration UI that starts empty and is explicitly populated by the owner

### "“I lost the page I was working on—restore the exact authenticated browser state from five minutes ago.”"
- **useful because:** A normal browser back button cannot reliably restore a portal's form state, scroll position, selected filters, or the correct tab after a redirect or accidental close. A local state journal would let the owner recover work without logging in again or reconstructing a multi-step workflow.
- **path:** browser → mac-bridge → pendant
- **model tier:** No expensive model is needed for capture or restore. Use a cheap classifier only to decide which controls are safe to serialize; the pendant speaks a short recovery result.
- **latency:** Under 3 seconds to list recoverable checkpoints and under 8 seconds to restore one.
- **cost:** Near-zero API cost; bounded local storage and browser extension CPU dominate.
- **security:** Never store cookies, tokens, passwords, payment fields, or raw page bodies. Store encrypted, expiring UI state keyed to origin and tab, with sensitive controls represented only as masked presence. Restoration must be same-origin and visibly report what was restored.
- **missing:** An encrypted, expiring browser-state journal for URL, scroll, tab identity, filters, and non-sensitive form state; Extension commands for checkpoint capture and same-origin restoration; A pendant-visible recovery receipt and automatic cleanup after logout or session expiry

### "“Turn this complicated logged-in page into a voice menu, and take me to the right control when I name it.”"
- **useful because:** Many authenticated portals are visually dense and unusable while walking or when the owner cannot look at the screen. The extension can build a temporary semantic menu from headings, labels, tables, and actionable controls; the pendant can read the menu and the browser can focus or navigate to the selected control without requiring visual hunting.
- **path:** browser → pendant → relay-realtime → mac-bridge
- **model tier:** Use local accessibility-tree parsing and deterministic label matching first. Use the cheaper planner only for ambiguous natural-language labels; realtime handles only the short spoken interaction.
- **latency:** Initial menu in 2–6 seconds; focus or scroll action under 2 seconds after the spoken choice.
- **cost:** Usually under $0.02 per interaction; most work is local accessibility-tree parsing and speech transport.
- **security:** Read only the accessibility subtree needed for the current menu. Mask values in financial, health, and credential fields, never submit or activate destructive controls through menu generation, and expire the menu when the tab navigates.
- **missing:** An accessibility-tree extraction command with semantic roles, labels, and action IDs; A temporary voice-menu registry mapping spoken choices to tab-scoped focus/scroll actions; A browser-to-pendant low-latency interaction loop with stale-menu detection


## Changes it proposed to its own stack

### `browser-harness` — Add an atomic browser evidence transaction: accept a list of tab/session IDs plus extraction selectors or semantic targets, execute read-only snapshots in parallel, normalize title/URL/timestamps, redact sensitive fields locally, and return bounded excerpts with stable element anchors and a transaction ID. Keep the raw DOM in the extension/local agent only, expire it after 10 minutes, and expose a receipt that later actions can reference without resending page text.
- **owner gets:** The pendant can reliably answer “compare these tabs,” “what changed since yesterday,” or “show me the exact field you filled” without silently reading the wrong tab or forcing the owner to repeat context. It also makes authenticated browser work feel dependable rather than like a fragile sequence of clicks.
- effort: Medium: extend browserBridge.js command payload/result schema, add parallel tab dispatch and local redaction, and add a bounded receipt store; test Safari tab churn and session expiry.  ·  risk: A tab can navigate during extraction or an anchor can become stale. Return per-tab freshness and partial failure rather than guessing; expire transaction data and allow cancellation. Recovery is a new read transaction, never a blind mutation.
- cost: Negligible API cost beyond the existing planner call; local memory/disk bounded to a few MB with 10-minute expiry.  ·  latency: Parallel extraction reduces two-tab comparisons from sequential latency to roughly the slower tab plus one planner pass.
- security: Improves security by keeping raw authenticated DOM local and making redaction/expiry explicit; still requires conservative per-origin rules supplied by the owner.
- depends on: A working POST /execute browser action dispatch with explicit tab/session targeting; Use existing local-agent/httpPolicy.js, originFanOut.js, browserSessions.js, and redaction.js rather than new policy constants; A receipt route or equivalent ephemeral transaction lookup


## What it asked for

_Nothing._
