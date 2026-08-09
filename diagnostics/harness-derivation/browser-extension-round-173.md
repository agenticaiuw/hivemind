# Harness derivation — browser-extension — round 173

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live Safari reachability** — Safari extension is online and currently exposes 9 tabs, including authenticated Gmail and X; POST /execute with actions can list tabs and read a page. The browser_enqueue wrapper only resolves/describes and does not invoke, so direct POST /execute is the working path for this agent.
  - evidence: POST /execute actions:[browser_read_page,{tabId:901464}] returned success with live Safari page provenance; the same response's prior log listed 9 tabs including Gmail tab 901464 and X tab 1163292. browser_enqueue_command returned invoked:false.

## Capabilities it proposed

### "“I’m looking at a purchase or subscription page—check every amount, renewal term, delivery date, and hidden add-on, compare it with the last time I saw this page, and give me a spoken pre-submit review. Do not submit anything.”"
- **useful because:** Authenticated checkout and renewal pages are exactly where silent fees and changed terms matter, and only the browser can see the owner’s logged-in cart. It turns an opaque page into a decision the owner can make from the pendant without risking an accidental purchase.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for page extraction and arithmetic; realtime only for the owner’s final spoken questions
- **latency:** 3–8 seconds to inspect and normalize the page; under 1 second for follow-up arithmetic
- **cost:** Usually one inexpensive extraction pass plus a small structured comparison; realtime tokens only if the owner asks follow-ups
- **security:** Cart contents, address fragments, and subscription terms leave the browser only as a redacted structured summary. Never persist full page text or payment fields. Never click the final purchase/subscribe/submit control; show the exact pending action and require the owner to do it in Safari.
- **missing:** A browser action that returns a structured, DOM-labeled extraction with sensitive-field redaction; A per-origin policy/configuration for which checkout fields may be spoken or retained; A comparison store for normalized prior offers with TTL and no raw page text

### "“Make sense of the tabs I have open: group them by project, remove duplicate or dead tabs only after showing me the list, and give me a 30-second spoken brief of what each project needs next.”"
- **useful because:** A real browser session accumulates research, inboxes, and stale pages that no single page summarizer can understand together. The extension supplies authenticated tabs and the Mac supplies durable project context; the pendant gives the owner a hands-free triage brief while preserving the exact tab list for review.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for tab clustering, titles/URLs, and concise summaries; realtime only for spoken clarification
- **latency:** 5–15 seconds for 10–30 tabs; incremental refresh under 3 seconds
- **cost:** Low: tab metadata and selective page extracts, with one compact synthesis; cost scales with pages actually opened, not tab count
- **security:** Do not send full content from every tab by default. Apply per-origin rules, redact account identifiers, and let the owner choose whether private tabs are included. Closing tabs is reversible only if a recovery manifest is saved; never close until the owner approves the explicit list.
- **missing:** A browser_list_tabs result exposed as a first-class structured input to planning; A bounded multi-tab extraction orchestrator with per-origin redaction and content budgets; A reversible tab cleanup action that stores a recovery manifest

### "“I left something half-done in Safari yesterday. Find the right private tab, tell me exactly where I stopped and what the next safe step is, then reopen it when I say ‘continue.’”"
- **useful because:** Browser sessions are ephemeral and the owner cannot remember which authenticated tab contains unfinished work. A small semantic handoff capsule lets the always-on relay and pendant recover the task without copying credentials or page dumps, while keeping the irreversible next step under the owner’s control.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model to create a compact handoff capsule from tab metadata, headings, visible form labels, and scroll position; realtime model only for the owner’s query and confirmation
- **latency:** Under 5 seconds to search the tab manifest; 2–5 seconds to reopen and verify the target page
- **cost:** Low per recovery: metadata plus a bounded visible-text extraction; storage is a few KB per capsule, not a page archive
- **security:** Never store cookies, input values, payment data, or full authenticated page text. Capsules contain origin, title, redacted landmarks, and a hash. Per-origin rules decide whether a capsule may exist at all. Reopening is allowed; typing, sending, purchasing, or submitting remains a separate explicit action.
- **missing:** A browser session manifest that records semantic landmarks and progress without field values; A relay query that searches those manifests across time and devices; An extension command to focus/reopen a tab and return a fresh verification snapshot

### "“Before I click this button in a logged-in site, tell me exactly what it will change—including the request, recipients, price, renewal, and side effects—and let me inspect a safe dry run without sending it.”"
- **useful because:** Today the browser agent can read or click, but it cannot reliably answer the crucial question before an unfamiliar authenticated button causes a real-world change. A transaction preflight would make the pendant a trustworthy second set of eyes for banking, work portals, purchases, and account settings while preserving the owner’s maximum-access policy.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** A local deterministic parser should identify form actions, targets, visible fields, confirmation text, and known side effects; use a cheaper background model to explain the structured result. Realtime is only for the owner’s spoken questions.
- **latency:** 2–5 seconds for DOM/form analysis; under 8 seconds if a sandboxed dry run is possible
- **cost:** Low for deterministic extraction, with a small model call for plain-language explanation; sandbox/network replay infrastructure dominates engineering cost, not API spend
- **security:** A dry run must never transmit real credentials, payment tokens, messages, or destructive requests. Use a browser-controlled interception layer that pauses the event and captures a redacted request preview; sandbox only with synthetic values or an origin-provided preview endpoint. Do not claim certainty when JavaScript or server-side effects cannot be modeled. The owner can still click through directly after seeing the preview.
- **missing:** An extension-side click interception and resumable pause protocol for high-impact DOM events; A structured redacted request/side-effect preview, including fetch/XHR and navigation intents, rather than page text alone; A per-origin capability declaration and uncertainty report for effects that cannot be simulated; A pendant/relay interaction that reads the preview in chunks and returns to the exact paused tab

### "“When a site asks to approve a sign-in in Safari, tell me the exact site, account, device, and location on the pendant; approve it only when I explicitly say ‘approve this login,’ otherwise leave it pending.”"
- **useful because:** The owner can be away from the Mac when an authenticated session needs a passkey or approval, but blindly approving a push is a phishing risk. Browser identity plus a spoken, origin-bound challenge on the worn device would make legitimate sign-in handoff possible without turning the pendant into an unconditional approval button.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** No expensive model is needed for the security decision: deterministic origin/account/device parsing and a signed challenge should drive the flow. Realtime only renders the challenge and collects an explicit spoken approval.
- **latency:** Under 2 seconds from challenge detection to pendant alert; approval result under 3 seconds
- **cost:** Negligible per challenge; engineering cost is secure challenge signing, origin binding, and platform integration
- **security:** Never approve from a generic push or voice phrase alone. The challenge must include the exact origin, account, user-agent/device, nonce, expiry, and a spoken confirmation phrase; approval is denied on mismatch, replay, or uncertain parsing. Do not expose one-time codes in logs or persist them. This requires the owner to opt in per origin and retain a hard physical cancel path.
- **missing:** Extension detection of WebAuthn/passkey and approval prompts with signed origin-bound challenge metadata; A relay-to-pendant challenge protocol with nonce, expiry, replay protection, and physical cancel; A browser callback that applies approval only to the paused matching tab/session; Per-origin opt-in configuration and an audit receipt that excludes secrets


## What it asked for

_Nothing._
## Its own summary

Produced three new browser-only cross-surface capabilities: (1) authenticated checkout/subscription pre-submit audit of fees, renewals, and changed terms without submitting; (2) multi-tab project clustering and spoken next-step brief with reversible cleanup; (3) authenticated unfinished-tab recovery using privacy-preserving semantic handoff capsules. I also verified Safari is genuinely online with 9 tabs and that direct POST /execute action arrays work, while the granted enqueue wrappers only return descriptions. The immediate implementation gaps are bounded structured DOM extraction/redaction, semantic tab/session manifests, and a reversible tab-focus/recovery command.

**Biggest unknown:** The owner has not supplied per-origin rules for which authenticated sites/categories may be read aloud or persisted; these proposals must ship with empty or conservative configuration rather than guessed site policies.

