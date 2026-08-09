# Harness derivation — browser-extension — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every morning, check the authenticated sites I explicitly configure, tell me only what changed and requires action, and leave everything else alone."
- **useful because:** This is the single most valuable browser-only capability: it turns existing Safari logins into a quiet personal operations desk without asking the owner to open each site. It can cover work portals, bills, bookings, and account notices while refusing to invent an origin list; the owner supplies an inspectable empty-to-start configuration.
- **path:** browser → relay → pendant → mac-planner → dashboard
- **model tier:** Background model for scheduled page comparison and extraction; realtime only when the owner asks a follow-up by voice. Use the Mac for deterministic diffing and the relay for concise prioritization.
- **latency:** Nightly or morning sweep may take 1–3 minutes across configured origins; a spoken answer should be under 10 seconds, with a pendant alert for urgent findings.
- **cost:** Roughly $0.02–$0.15 per sweep depending on page count and extracted text; browser navigation and Mac diffing dominate wall time, not model tokens.
- **security:** Ship with an empty per-origin policy. The owner must add origins and categories; never persist page bodies or credentials. Store only short-lived claims with host/URL provenance, and do not read aloud categories marked private. Stop before sending, submitting, paying, or deleting; present the prepared action instead.
- **missing:** Scheduled browser job runner that can target the configured Safari session; Per-origin read/extract/redact/never-store configuration UI, initially empty; Page-change normalization and semantic diffing across login redirects and dynamic content; Relay-to-pendant alert delivery for urgent findings

### "When I say 'what am I looking at?', use the element or text currently focused in Safari—not the whole page—and explain it through my pendant, with a link back to the exact place."
- **useful because:** Whole-page extraction is noisy and dangerous on authenticated pages. Focus-scoped context lets the owner ask about a selected paragraph, table row, error, or form field hands-free while preserving page boundaries and reducing sensitive data exposure.
- **path:** browser → relay → pendant → mac-planner
- **model tier:** Realtime model only for the short spoken explanation; the extension and Mac should deterministically capture selection, focused element, nearby labels, URL, and a bounded DOM ancestor before sending context.
- **latency:** 2–5 seconds from button/voice request to first spoken sentence; capture should complete in under 300 ms.
- **cost:** About $0.005–$0.03 per question; DOM capture is local and the model summary dominates.
- **security:** Transmit only the focused/selected region with a strict character and ancestor-depth bound; redact password fields, hidden DOM, tokens, and cross-origin frames. Do not persist page text. The returned deep link or selector may be ephemeral and should be clearly labeled.
- **missing:** A real browser_read_focus_context extension command that reports selection, focused control, nearby labels, and stable tab/frame metadata; Relay intent routing for deictic requests ('this', 'that field', 'what am I looking at?'); A safe page-anchor representation that can reopen the same place without replaying a mutation

### "Warn me immediately if an authenticated page looks like a phishing or account-takeover situation—wrong domain, suspicious login prompt, new recovery details, or an unexpected payment—then tell me exactly why."
- **useful because:** A browser session is the one place this system can see login and security state before the owner acts. Combining URL/DOM evidence from Safari with local history and a short pendant alert could catch a convincing lookalike or account compromise that email triage misses.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic extension checks and Mac-side domain/history rules first; a cheap background model classifies ambiguous page text. Realtime is reserved for the owner's follow-up question.
- **latency:** Under 1 second for URL/form heuristics and under 8 seconds for a semantic warning; never wait for a model before showing a local high-confidence warning.
- **cost:** Near-zero for deterministic checks; $0.01–$0.05 for an ambiguous security-page classification. URL and small DOM metadata dominate data handling, not tokens.
- **security:** Never transmit passwords, typed secrets, cookies, or full page bodies. Keep a local, inspectable domain/recovery-change history. Alerts must explain evidence and confidence, not claim certainty; do not block navigation or typing under the owner's maximum-access policy.
- **missing:** Extension hook for navigation and focused password/recovery forms before submission; Local domain reputation and per-origin baseline store; Security-specific alert schema with evidence snippets redacted before pendant speech; Mac/relay correlation with recent account-change findings

### "If Safari crashes or I switch Macs, let me say 'resume my browser task' and reopen the right authenticated page at the right step, without saving passwords or page contents."
- **useful because:** Today browser work disappears with a closed tab or a dropped Mac link. A bounded task checkpoint would make long, authenticated workflows—claims, applications, research, bookings—survive interruption while keeping the session itself in Safari and keeping secrets out of the relay.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic checkpoint extraction for URL, origin, tab title, visible task label, form field names, and an opaque page anchor. Use a cheap background model only to name the task and detect when the anchor is stale; realtime only handles the owner's resume request.
- **latency:** Checkpoint under 1 second when a tab changes; resume in 5–15 seconds including Safari navigation and anchor reacquisition.
- **cost:** Under $0.02 per checkpoint/resume; most work is extension and Mac state management.
- **security:** Persist no cookies, credentials, page body, or typed values. Encrypt the checkpoint locally and expire it quickly. On resume, verify origin and show the owner the page title/task label; if the anchor moved, reopen the page but do not guess a click or submit.
- **missing:** Extension event/checkpoint API for tab close, navigation, and form-progress metadata; Mac-local encrypted checkpoint store with expiry and stale-anchor detection; A resume route that targets the existing Safari session rather than creating a second browser profile; Dashboard controls to inspect and delete checkpoints

### "When a private website shows me something important—an incorrect charge, cancellation, delivery promise, or account status—let me say 'witness this' and get a tamper-evident, time-stamped evidence packet I can later use in a dispute, without storing my credentials or the whole page."
- **useful because:** Authenticated web evidence is currently ephemeral: a tab can change, a session can expire, and screenshots are hard to search or explain. A selective, provenance-backed witness packet would let the owner prove what the site displayed at a specific time and quickly retrieve the exact claim during a support call or appeal.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Browser and Mac deterministically capture the selected claim, URL/origin, timestamp, and a cryptographic digest of the surrounding DOM or screenshot. A background model can produce a short human-readable claim and redact obvious secrets; realtime is only for the owner's spoken request or later question.
- **latency:** Capture and local sealing under 2 seconds; spoken confirmation under 5 seconds. Retrieval during a dispute under 10 seconds.
- **cost:** Usually under $0.03 per witness; local hashing and encrypted storage dominate, with a small model call only when a concise claim or redaction decision is needed.
- **security:** Never save cookies, passwords, hidden inputs, or an unbounded page body. Keep the raw evidence encrypted on the Mac with explicit expiry; store only a short claim, digest, URL, and provenance in the relay. Clearly distinguish a cryptographic record of what was captured from proof that the website itself was truthful. The owner must be able to inspect, export, and delete a packet.
- **missing:** A browser 'witness selection' command that captures the focused region plus bounded surrounding context; Mac-local encrypted evidence vault with content-addressed hashes and export to a human-readable PDF/JSON packet; Relay APIs for witness receipt, expiry, retrieval, and provenance verification; Pendant feedback indicating that a witness was sealed and its short reference code

### "Before I change anything on a logged-in site, show me the consequences—fees, dates, lost benefits, affected subscriptions, and what can be undone—using the site's own current terms, but do not perform the change."
- **useful because:** Many costly web actions hide consequences behind several authenticated screens. The owner should be able to ask from the pendant and receive a decision-grade preview assembled from the live site and local calendar/subscription context, rather than discovering the fee after clicking.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Browser automation should follow a read-only exploration plan; the Mac computes dates and compares local commitments; a background model extracts and explains terms. Realtime only answers the final spoken question.
- **latency:** 10–30 seconds for a multi-screen preview; never perform a mutation while exploring.
- **cost:** About $0.03–$0.20 per preview, dominated by authenticated page navigation and model extraction across several screens.
- **security:** Use an explicit read-only action set and refuse mutation commands within the exploration job, while honoring the owner's maximum-access policy for ordinary actions. Keep page text transient; persist only cited claims, URLs, and expiry. Flag uncertainty when terms are dynamic or the site requires an irreversible confirmation step.
- **missing:** Read-only browser exploration with a bounded multi-page plan and mutation-proof receipts; A consequence schema for money, dates, entitlements, dependencies, and reversibility; Mac-side joins to Calendar, reminders, and known subscriptions with clear source labels; A pendant response format that separates site facts, local conflicts, and uncertainty

### "Collect the account details I explicitly request from my logged-in services, compare them across sites, and tell me where they disagree—such as address, renewal date, payment status, or cancellation state—without leaving copies of the exports behind."
- **useful because:** Important personal data is fragmented across authenticated portals and often silently contradicts itself. The browser can reach those private sources, while the Mac can normalize and compare them locally; the owner gets a single discrepancy list instead of manually checking every account.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Background model for schema mapping and contradiction explanation; deterministic Mac code performs normalization, date/currency comparison, and deletion of temporary exports. Realtime is only for follow-up questions.
- **latency:** One-off collection in 1–5 minutes depending on services; concise spoken discrepancy report in under 10 seconds after results arrive.
- **cost:** Roughly $0.05–$0.40 per collection, dominated by several authenticated navigations and export parsing; recurring checks should use a cheaper scheduled tier.
- **security:** The owner explicitly chooses services and fields. Downloads remain encrypted and local, are deleted after normalization, and never enter relay memory. Persist only minimal discrepancy claims with source, timestamp, and short TTL. Never infer that matching data proves identity or correctness; expose each source and stale state.
- **missing:** A browser workflow for authenticated data export/download with per-origin field selection; Mac-local ephemeral parser and canonical schema for dates, currency, addresses, and status values; A contradiction engine that preserves source-level evidence without retaining raw exports; Owner-facing controls for field selection, retention, and immediate purge


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct browser capabilities: (1) scheduled, owner-configured authenticated-site triage (the browser-layer version of the previously denied portal idea), (2) phishing/account-takeover warnings based on Safari security state plus Mac/relay correlation, and (3) encrypted, expiring resume checkpoints for interrupted authenticated tasks. I also explored focused-page context, but the recorder identified that as an existing backlog cluster, so it should not be treated as new work. The live device inventory now reports Safari online with one tab; my direct /execute navigation probe failed because the action payload's URL shape was rejected, so I did not pretend to inspect page contents.

**Biggest unknown:** The productive next step is not another model feature: I still need the extension-side event/checkpoint and security hooks, a working documented POST /execute browser action schema (the current probe rejected a valid-looking URL), and the owner's explicit per-origin configuration. The config must start empty; I still must not invent which authenticated sites or categories he wants monitored.

