# Harness derivation — browser-extension — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser** — Safari extension is online with 9 tabs, including a logged-in Gmail inbox (14,986 messages) and active X home; POST /execute with browser_list_tabs returns tab IDs and receipts.
  - evidence: POST /execute body {"actions":[{"type":"browser_list_tabs"}]} returned HTTP 200, tabCount 9, Gmail and X tabs, extension provenance commandId browser_187a6bae-f548-4ef2-9308-26ac3c3becad.

## Capabilities it proposed

### "If a website needs me to sign in, approve a passkey, or solve a challenge, pause the task, tell me on the pendant which site needs me, and continue automatically once I'm back in."
- **useful because:** Authenticated automation currently fails opaquely at the exact moment a human credential or device approval is needed. This makes the browser a cooperative agent: it never asks the model to handle secrets, and the owner can resolve the interruption on the already-open Safari session without losing the task's context.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap classifier in the browser harness to detect login, passkey, MFA, CAPTCHA, and consent interstitials; use the planner tier to preserve and resume the task. Realtime is only for the brief spoken alert and owner reply.
- **latency:** Detect within 1 second of the blocking page; pendant alert within 3 seconds. Resume within 5 seconds of a successful browser heartbeat/navigation after the challenge.
- **cost:** Low: classifier and state machine dominate; about $0.001-$0.01 per interruption, with no model call for routine detection.
- **security:** The system must not capture or transmit passwords, OTPs, passkeys, or CAPTCHA contents. Store only origin, coarse blocker type, task ID, and an expiring continuation token. The owner sees the exact domain on the pendant and the Mac keeps focus on that tab. A challenge timeout cancels the task and discards continuation state.
- **missing:** Extension-side blocker detection based on accessibility tree and navigation patterns; An expiring paused-browser-job state with safe resume conditions and a heartbeat/event callback; A relay-to-pendant alert payload for site and blocker type, building on offline_alert_inbox; A browser resume action that revalidates origin and semantic target before continuing

### "Save this exact section of the page for me, with its link and why it matters, so I can ask about it later from the pendant—even if the tab is closed."
- **useful because:** A useful browser assistant should preserve the small piece the owner meant, not an entire page or a vague URL. This connects Safari's authenticated view to the wearable's memory: the owner can mark a passage while reading a private dashboard or article and retrieve a concise, source-linked cue later without reopening the session.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a cheap extraction/summarization model in the background to normalize the selected DOM fragment and generate a one-sentence why-it-matters note. Realtime is only needed when the owner later asks for the bookmark; no expensive call at capture time if they provide a spoken reason.
- **latency:** Capture acknowledgement under 500 ms; summarize/store within 5 seconds. Pendant retrieval should begin within 2 seconds and offer the source URL before reading private text aloud.
- **cost:** A few cents per bookmark only when summarization is requested; storage is small and bounded by a per-bookmark text limit.
- **security:** The owner must explicitly invoke capture. Preserve origin, URL, title, selected text/DOM, timestamp, and optional reason under the configured per-origin retention rules; default to encrypted local storage and a short retention period. Never capture password fields, hidden DOM, or whole-page HTML. Speaking the bookmark should require the normal wearable interaction and redact categories marked not-to-speak.
- **missing:** An extension action to capture the current selection or semantic section with a stable locator and tab provenance; A relay bookmark record with encrypted, per-origin retention and deletion controls, connected to existing capture/bookmark storage; A pendant retrieval/list interaction that distinguishes browser bookmarks from offline_moment_bookmark entries; A later browser re-open or source-validation action that reports when the page has changed

### "Before I click a button on a logged-in site, tell me if it will send my information to a different company or open a suspicious domain."
- **useful because:** The extension is the only node that can inspect the real authenticated page and its form targets, redirects, and embedded origins. A compact spoken warning on the pendant can catch phishing, accidental third-party uploads, and deceptive OAuth handoffs at the moment of action—before the owner has disclosed anything.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic origin/form-action comparison and a cheap reputation/rules lookup first; invoke the planner tier only for an ambiguous human-readable explanation. Realtime speaks a one-sentence warning when a risky click is attempted.
- **latency:** Inspection under 150 ms for known origins; under 2 seconds when a reputation lookup is needed. Do not delay ordinary same-origin clicks.
- **cost:** Near-zero for local checks; occasional lookup/model explanation under $0.005 per warning.
- **security:** Never transmit form values or page text to reputation services. Compare registrable domains locally, disclose the exact destination origin, and distinguish expected identity providers from unknown third parties. The feature warns and logs a receipt but does not silently block, matching the owner's maximum-access policy; a high-risk alert should still require the owner's explicit decision before continuing.
- **missing:** Extension-side pre-action inspection of form action, link destination, redirect chain, and iframe origins; A local/public suffix and configured trusted-identity-provider matcher with per-origin owner overrides; A low-latency relay event carrying destination metadata to the pendant without sensitive fields; A browser receipt that records the warned destination and the owner's subsequent choice

### "Turn this complicated web page into a spoken menu of the few things I can actually do, let me choose one from the pendant, and then carry it out in Safari."
- **useful because:** Today the owner can ask for a page read or a specific browser action, but cannot reliably operate an unfamiliar, dense authenticated interface hands-free. The extension can see the page's accessibility structure, the planner can reduce it to an actionable menu, and the pendant can provide a low-bandwidth physical choice without exposing the whole page or requiring a phone screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a fast local accessibility-tree parser and a cheaper planner model to rank and label actions; use realtime only to speak the short menu and interpret a selection. Use the expensive tier only when the page has ambiguous controls or the owner asks a follow-up question.
- **latency:** Generate the first 3-5 item menu within 3 seconds, announce it within 1 second, and execute a selected reversible action within 4 seconds. Rebuild the menu after every navigation or mutation.
- **cost:** Typically $0.005-$0.03 per page menu depending on ambiguity; extension extraction and relay traffic dominate less than model usage.
- **security:** Send the model a filtered accessibility tree, not raw HTML, password fields, hidden elements, or arbitrary page text. Keep origin and tab provenance on every menu item, expire menus after navigation, and require an explicit second button press for actions that send, purchase, delete, or otherwise commit. The owner’s existing maximum-access policy still allows the action; this is an interaction affordance and audit trail, not a blanket block.
- **missing:** A browser extension command that returns a filtered accessibility tree with stable role/name/locator IDs and marks sensitive controls; A planner operation that converts that tree into a bounded, ranked action menu and preserves the locator IDs; A pendant menu protocol for speaking item numbers and receiving a selection over the relay; A browser executor that revalidates the selected locator against the current tree before acting and emits a concise result receipt

### "Check this notice in my logged-in account against the organization's public site, and tell me whether the deadline, amount, or instructions differ before I act on it."
- **useful because:** A private portal message can be outdated, mistaken, or a phishing-like instruction even when the owner is already logged in. No single node can do this well: Safari supplies the authenticated notice, the relay can retrieve public authoritative material, and the planner can produce a field-level discrepancy report for the pendant.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper extraction model for the notice and public-page normalization; use realtime only to answer the owner's spoken request and read a short discrepancy summary. Escalate to the expensive tier only when the two sources use materially different terminology.
- **latency:** Return a preliminary comparison in 10 seconds and a spoken summary in 2 seconds after completion. Never navigate away from the authenticated tab or take action automatically.
- **cost:** About $0.01-$0.06 per comparison, dominated by two-page extraction and normalization; public retrieval can use the existing cheaper search tier.
- **security:** Transmit only the selected notice fields and the public URL/query, not the whole authenticated page or account identifiers. Keep private excerpts ephemeral and origin-scoped. Clearly label the public source and its retrieval time; if no authoritative match is found, say so rather than calling it fraudulent.
- **missing:** A browser selection/extraction action that lets the owner nominate one notice and its relevant fields; A relay workflow that fetches and provenance-checks the organization's public source without leaking private account data; A structured comparison schema for dates, amounts, URLs, phone numbers, and instructions with confidence and source citations; A pendant response format that reads discrepancies and lets the owner save or dismiss the finding

### "When a website rejects something I entered, tell me which fields are wrong in plain language, suggest corrected values from the surrounding page, and let me fix only those fields from the pendant."
- **useful because:** Browser automation today can type, but a failed validation leaves the owner staring at an opaque red form and forces a second attempt. The extension can read the page's accessible validation messages, the planner can explain them without repeating secrets, and the pendant can drive a targeted correction while preserving the rest of the form.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic extraction for aria-invalid fields and nearby error text; use a cheaper planner model to translate and propose corrections. Realtime speaks only the affected field and accepts a short correction. Use the expensive tier only for genuinely ambiguous validation.
- **latency:** Detect errors within 500 ms after navigation or submit response; explain within 3 seconds; apply a selected correction within 2 seconds.
- **cost:** Usually under $0.01 per correction; most work is local DOM parsing and one short planner call.
- **security:** Never echo password, payment, OTP, or hidden-field values. Suggestions must be marked as suggestions and never silently overwrite existing values. Keep a field-level diff and origin/tab binding, expire it on navigation, and expose the exact proposed correction before typing it.
- **missing:** Extension extraction of accessible validation state, field labels, constraints, and nearby help text; A planner schema for field-specific suggestions that distinguishes deterministic fixes from guesses; A pendant interaction for selecting a named field and dictating or confirming a correction; A browser patch action that updates only the bound field and returns an updated validation receipt


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-side semantic interaction journal for each command: before and after every browser action, capture only the target element's accessible role/name, origin, tab ID, and a normalized value hash, then return a compact evidence capsule. For navigation and form workflows, require the next action to re-resolve the element by role/label and reject stale tab or changed-origin references; do not store page text or screenshots by default.
- **owner gets:** When a logged-in page changes underneath the agent, it will stop touching the wrong button and explain precisely what changed. The owner gets dependable automation across Gmail, billing portals, and unfamiliar sites instead of silent mis-clicks, while sensitive page contents stay out of long-term records.
- effort: Medium: extension content-script instrumentation plus local-agent capsule schema and browser action integration; 1-2 weeks including Safari compatibility testing.  ·  risk: Some sites expose poor accessibility labels and actions may fail where they previously worked; recovery is a fresh page snapshot and an explicit locator fallback. Hashes can still reveal equality relationships, so keep capsules short-lived and origin-scoped.
- cost: Negligible API cost; tens of KB per workflow at most, with a bounded TTL. No new hardware cost.  ·  latency: Adds roughly 50-150 ms per browser action for semantic resolution and receipt generation.
- security: Improves provenance and stale-page safety; by design avoids persisting page text, typed secrets, or screenshots. Origin and field hashes remain sensitive metadata and must be encrypted/TTL-limited.
- depends on: POST /execute; GET /browser/poll; POST /browser/result/:commandId; GET /browser/sessions; POST /jobs/:jobId/receipts


## What it asked for

_Nothing._
## Its own summary

Fresh browser work is now grounded in a live Safari extension: 9 tabs are open, including logged-in Gmail and X, verified through POST /execute browser_list_tabs with a receipt. I recorded four non-identical proposals: semantic interaction journals to prevent stale-page misclicks; pause/resume around login/MFA challenges without touching secrets; source-linked selection bookmarks retrievable from the pendant; and pre-click cross-origin/data-destination warnings. The most important missing connective pieces are extension-side semantic/DOM inspection, expiring browser continuation state, a privacy-scoped browser bookmark record, and a low-latency relay event path to the pendant. I also confirmed the previously requested form-approval workflow collides with an existing backlog item and did not restate it.

**Biggest unknown:** The owner's actual first authenticated sites and categories that must never be spoken or persisted remain intentionally unspecified. I still need the owner to provide 3–5 target origins plus per-origin read/extract/redact/never-store rules; without that, browser automation should stay generic and conservative rather than inventing site policy.

