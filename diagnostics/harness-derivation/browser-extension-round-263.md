# Harness derivation — browser-extension — round 263

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at a logged-in website in Safari. Ask it whatever I ask you, and tell me the answer with exactly where you found it.”"
- **useful because:** This would make the pendant a voice doorway into the owner’s private web sessions rather than a public-search toy: invoices, dashboards, account history, and pages behind login become queryable while the owner is walking. The answer includes the page title, URL, timestamp, and a short quoted claim so the owner can audit it, while the page itself is not retained.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Use the realtime tier only to capture the owner’s spoken question and deliver the short answer; use the cheaper mac-planner/browser worker for navigation, extraction, claim checking, and citation formatting.
- **latency:** Under 8 seconds for the current tab; up to 20 seconds for a navigation/search across the authenticated origin. If the page needs login, CAPTCHA, or a visual choice, stop and speak the checkpoint instead of guessing.
- **cost:** Usually one cheap browser extraction plus one short realtime turn, roughly $0.01–$0.05 depending on answer length; navigation and page text dominate latency, not model tokens.
- **security:** The browser may expose private data to the model and the pendant speaker may be audible to others. Default to the current tab, read-only action allowlists, redaction of detected secrets, and claims-only short-lived browser memory (24-hour TTL, 200-character cap) with URL/evidence provenance. Ship an empty per-origin configuration for the owner to fill; never silently invent an allowlist. Ask before navigating away from the current origin or reading forms/private fields.
- **missing:** A relay intent that binds one spoken question to a browser job and returns a compact cited answer; A browser extraction mode that returns claim-level snippets and provenance rather than a page blob; A pendant response format for “I found X at URL Y at time Z” plus an audible privacy warning

### "“What am I looking at?” or “What does the red number in this page mean?” while I’m on a Safari tab."
- **useful because:** The pendant becomes a hands-free ‘ask about this’ button for the owner’s actual browser context. It combines DOM text, accessibility labels, the current scroll/selection, and a screenshot when the answer is visual, so the owner can understand a chart, error banner, video, or dense logged-in dashboard without describing the page or reading a URL aloud. This is useful precisely because the browser session and its login are unreachable to the relay alone.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** Use the realtime model for the short spoken question and answer; use mac-vision only when DOM extraction cannot resolve the referenced region, and a cheaper planner for page text/selection retrieval. Keep the visual crop small and task-scoped.
- **latency:** 2–4 seconds for text/selection answers and 6–10 seconds for a visual crop. If the reference is ambiguous, ask one spoken clarification (“the red number near the chart or the banner?”) rather than dumping the page.
- **cost:** $0.01–$0.08 per query; screenshot token usage and visual fallback dominate, while most pages are answerable from accessibility/DOM text alone.
- **security:** The screenshot may contain private data and nearby unrelated content. Capture only the viewport or element bounding box requested, redact secrets, do not persist the image or page body, and include the live URL/title in the spoken answer. An empty owner-supplied per-origin configuration should control whether visual capture is allowed; default to current-tab read-only and no navigation.
- **missing:** A pendant event that carries a transient reference such as current selection, focused element, scroll position, and question audio; A browser_snapshot/extract operation that returns element bounds plus accessible text and can crop one referenced region; Cross-surface reference resolution so “this”, “the red number”, and “the button below it” are grounded in the same live tab

### "“Put this Safari task on hold; when I’m back, restore the exact page, tab, scroll position, and draft so I can continue from my pendant.”"
- **useful because:** Long browser tasks currently disappear into an open tab. A spoken hold/resume makes the Mac and browser an external working memory: the owner can leave the desk, let the Mac sleep or switch tasks, then resume the same authenticated page at the same section without re-finding it. It should restore drafts and focus, but never silently re-submit a form or replay a click.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** Use mac-planner/browser code for session capture and restoration; realtime is only for the short hold/resume dialogue and status. No expensive vision unless the saved locator no longer exists.
- **latency:** Capture in under 2 seconds; restore in under 8 seconds. If the origin, login, or DOM has changed, return a spoken “needs review” checkpoint with the last known title and section instead of guessing.
- **cost:** Usually under $0.02, mostly a cheap session operation and one short realtime response; visual fallback on changed layouts is the cost outlier.
- **security:** Persist only a host-keyed session descriptor (URL, title, locator, scroll/focus metadata, and an opaque draft reference), never page text, screenshots, cookies, or passwords. Expire it after 24 hours by default and expose a spoken “forget this task” command. Restoration must be read-only until the owner explicitly asks to continue a mutation.
- **missing:** A durable browser-task bookmark with tab/session identity, scroll anchor, focused control, and draft hash; A restore operation that can reopen the authenticated tab and verify page identity before applying scroll/focus; A pendant-visible task list with short names and expiry, backed by browser provenance rather than stored page content

### "“What did I see or agree to on that private website last week? Find the original page in my Safari history, verify it is still the same information, and tell me what changed.”"
- **useful because:** Today the assistant can answer from the page currently open, but it cannot reconstruct a private web decision after the tab is gone. This would let the owner recover a forgotten appointment, policy, order, or account detail from authenticated Safari history, then distinguish the original observation from the page’s current state. It turns the browser into a trustworthy time-aware memory without pretending that stale web facts are current.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Use the cheaper browser/mac-planner tier to search Safari history and revisit candidate pages; use realtime only for the owner’s spoken query and a compact comparison. Use a stronger model only when several pages conflict or the page structure changed substantially.
- **latency:** Return likely candidates in 5 seconds and a verified comparison in 15–30 seconds. If history is unavailable, the login expired, or multiple pages match, speak the uncertainty and ask for one disambiguating detail.
- **cost:** Approximately $0.03–$0.15 per lookup; authenticated navigation, repeated extraction, and conflict resolution dominate cost.
- **security:** History URLs and private page contents are highly sensitive. Keep raw history and page bodies on the Mac, send only task-scoped claims and bounded evidence to the relay, redact query-string secrets, and never put page text in durable memory. Store only a short-lived claim with original URL, observed time, current verification time, and content hashes. The owner must be able to erase the entire evidence chain.
- **missing:** A local Safari-history search and page-revisit action that does not require exporting the browsing history to the relay; A temporal evidence model linking an old observation to a fresh read and classifying unchanged, changed, unavailable, or contradicted; A spoken answer format that clearly separates “you saw then” from “the site says now,” with an erase-evidence command

### "“Take the ticket, boarding pass, or QR code I’m viewing in Safari and put the right version on my iPhone, then tell me what was added.”"
- **useful because:** A private browser session often contains the artifact the owner needs away from the Mac: a boarding pass, event ticket, pickup QR, or appointment barcode. Today the browser can read it and the phone can be controlled, but no single capability identifies the usable artifact, transfers it safely, verifies the phone’s resulting screen, and tells the pendant which version is ready. This would bridge the browser’s login reach to the phone’s physical usefulness.
- **path:** pendant → browser → mac-bridge → iOS → relay
- **model tier:** Use mac-planner/browser extraction to identify the artifact and mac-vision for QR/barcode geometry; use the iOS-control facet for Wallet/share/import flow; realtime only confirms the target and reports success.
- **latency:** 10–20 seconds for a straightforward image or pass; up to 45 seconds where iOS presents an import sheet. Stop at ambiguous identity, duplicate passes, or an external share destination.
- **cost:** Roughly $0.05–$0.20, dominated by one visual extraction and iPhone verification; ordinary DOM image extraction is cheaper.
- **security:** Passes can contain names, booking codes, and scannable credentials. Transfer only the selected artifact, never the whole page; keep the QR image transient; verify the destination app and pass title on iPhone; do not upload it to third-party conversion services. Require confirmation before adding to Wallet or sharing externally, and provide a spoken cancellation path.
- **missing:** Artifact detection that distinguishes a scannable pass from unrelated page QR codes and binds it to title/date/owner identity; A local browser-to-iPhone transfer channel for an image or structured pass payload; iOS verification that reads back the resulting pass title, issuer, date, and barcode presence before declaring success

### "“I’m about to share my screen. Hide anything private in Safari, leave only the page I named, and tell me what you closed or changed.”"
- **useful because:** Screen sharing accidents expose exactly the authenticated browser state that makes this system valuable. A pendant command could inventory open tabs, classify visible titles/URLs/forms, close or navigate away from sensitive tabs, and leave a named presentation tab active. The owner gets an audible checklist before sharing instead of relying on memory under pressure.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** Use the cheap browser planner for tab inventory and deterministic tab operations; use mac-vision only for a page whose title does not reveal sensitive content; realtime speaks the checklist and accepts corrections.
- **latency:** Inventory in 2 seconds and complete a hide plan in under 8 seconds. If a tab cannot be classified confidently, quarantine it rather than leave it visible and report the tab title to the owner.
- **cost:** Usually below $0.03, since it is tab metadata and deterministic navigation; visual inspection is the exceptional cost.
- **security:** The classifier itself sees private titles and URLs, so keep analysis local and do not persist the inventory. Closing tabs can lose unsaved drafts: save a reversible tab snapshot first, and prefer moving sensitive tabs to a hidden window or blank page when possible. Never claim the screen is safe without checking the active window and display.
- **missing:** A multi-tab browser inventory and active-window verification action; A reversible quarantine operation that hides tabs without destroying unsaved state; A local sensitivity classifier with an explicit owner override for ambiguous tabs


## What it asked for

_Nothing._
