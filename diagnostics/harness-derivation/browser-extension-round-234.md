# Harness derivation — browser-extension — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser device state** — Safari on MacIntel is online with 3 tabs; home-macbook-bridge is online. Browser action resolver still ambiguously maps list-tabs to browser_list_sessions, so granted wrappers cannot execute list/read reliably.
  - evidence: discover(devices) at round 234; browser_read_or_navigate(browser_list_tabs) returned resolver ambiguity between action:browser_list_tabs and action:browser_list_sessions.

## Capabilities it proposed

### "“From the page I’m looking at, tell me the three things that need my attention, and put the rest in a brief queue I can hear later.”"
- **useful because:** This is the highest-value browser-only workflow: the owner can speak from the pendant while the browser reads an already-authenticated page, separates actionable items from bulk, and delivers the result through the pendant without exposing the page body to the relay or requiring him to pick up the Mac.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime only for the short spoken request and final answer; a cheaper background model performs page extraction, deduplication, and priority ranking.
- **latency:** 10–20 seconds for the first three items; queue construction may continue for up to 60 seconds and be announced as ready.
- **cost:** Usually <$0.03 per invocation; browser extraction and compact claim-ranking dominate, not speech.
- **security:** Read-only browser actions; no form submission. Send only bounded extracted claims and host/URL provenance to the relay; never HTML, screenshots, or page text. Use existing 24-hour browser-fact TTL and 200-character value cap. The owner must later provide any origin/category policy; ship empty configuration rather than inventing one.
- **missing:** An intent that targets the current authenticated tab and returns ranked claims plus a deferred audio queue; A browser action bundle that can read the current tab through the live extension (the current tool resolver is ambiguous for browser_list_tabs); A compact pendant queue protocol for multiple result items, beyond the accepted offline_alert_inbox

### "“Compare the two open pages I’m looking at on price, renewal date, cancellation terms, and anything that could surprise me; read me the differences and save only the short comparison.”"
- **useful because:** The browser is uniquely able to see both authenticated tabs, while the pendant makes a private comparison usable away from the screen. This turns scattered account pages into a decision the owner can hear, with explicit evidence and bounded retention rather than retaining either page.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Background model extracts a fixed schema from each tab and computes differences; realtime model speaks the short comparison and answers one follow-up.
- **latency:** 20 seconds for two tabs and a concise spoken result; up to 45 seconds if one page needs a wait/reload.
- **cost:** <$0.04 per comparison; two authenticated DOM reads and schema extraction dominate.
- **security:** Read-only allow-set: list tabs, read/snapshot, wait only. Do not click or type. Store only the requested comparison claims, each with tab URL provenance, 24-hour browser TTL, and the existing 200-character cap; never store HTML, screenshots, or raw page text. Empty per-origin/category policy remains explicit until the owner supplies it.
- **missing:** A reliable browser_list_tabs/read action resolution (the current granted wrapper is ambiguous between browser_list_tabs and browser_list_sessions); A multi-tab execution primitive that binds each extracted claim to its source tab; A user-visible delete/expire control for the saved comparison packet

### "“Before I do anything on this site, tell me which account and organization I’m signed into, whether the session looks normal, and whether there are any pending security warnings.”"
- **useful because:** Wrong-account actions and silently expired or challenged sessions are costly. The browser can inspect authenticated identity markers and security notices that the relay and pendant cannot reach; the pendant can give a private preflight before the owner edits, shares, or pays.
- **path:** pendant → browser → relay → mac-bridge
- **model tier:** Small background classifier for account/session/security-marker extraction; realtime model only for a terse spoken preflight.
- **latency:** 3–8 seconds for the current tab, with no action beyond read and snapshot.
- **cost:** <$0.01 per preflight; one DOM read and compact classification dominate.
- **security:** Read-only, no clicks or typing. Speak only the account/org name and security status, not page content or secrets. Persist nothing by default; if a finding is saved, use existing host provenance, 24-hour TTL, and short-value cap. Ship with empty per-origin rules rather than assuming which identity categories are safe to speak.
- **missing:** A browser security/identity extractor that recognizes account markers without site-specific hardcoded origins; A stable current-tab read operation; the granted browser wrapper currently fails resolution for list/read enum values; A pendant response type for 'session warning' distinct from ordinary informational alerts

### "“Check the authenticated accounts I have open and tell me whether my name, address, subscription status, and payment identity disagree anywhere. Don’t change anything.”"
- **useful because:** A single page can look correct while different services hold stale or contradictory personal data. No other node can inspect the owner’s logged-in accounts together. A private, read-only cross-account audit would surface errors before they cause failed renewals, misdirected notices, or identity confusion.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Background model extracts a fixed set of identity and billing fields and computes contradictions; realtime model speaks only the short discrepancy report.
- **latency:** 30–90 seconds for up to five currently authenticated tabs; partial results should arrive as each origin completes.
- **cost:** $0.05–$0.15 per audit, dominated by several authenticated page reads and structured comparison.
- **security:** Read-only browser allow-set; no clicks, typing, or account changes. Raw page content must stay on the Mac. Send only field-level discrepancy claims with host provenance, redacted values, and short TTL; never persist full addresses, payment numbers, HTML, or screenshots. The owner must explicitly configure which origins and categories participate; ship with no origins enabled.
- **missing:** A cross-origin audit job with an owner-supplied origin/category configuration; A structured extractor for identity, address, subscription, and payment markers that does not rely on hardcoded sites; A pendant report format that says which origins disagree without speaking sensitive values aloud

### "“Run my private account incident check: compare today’s authenticated security and activity pages with the last baseline, tell me what changed, and prepare a containment checklist without touching the accounts.”"
- **useful because:** The owner currently has no way to ask the wearable to investigate a possible account compromise across logged-in services. Browser access can reach security pages and recent activity; the relay can correlate changes over time; the pendant can deliver an urgent, concise warning while the Mac remains untouched.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Background model performs baseline comparison and groups changes into likely-benign versus suspicious; realtime model speaks only urgent findings and the next safe checklist item.
- **latency:** Under two minutes for a configured set of origins; urgent anomalies should be spoken as soon as one origin completes.
- **cost:** $0.05–$0.20 per check, depending on origin count and page depth.
- **security:** Strictly read-only: no password changes, sign-outs, recovery actions, or clicks. Store hashes and minimal change claims rather than activity-page text, with short browser TTL and revocable provenance. Never speak secrets, recovery codes, full IP addresses, or device identifiers. Configuration must be owner-provided and empty by default.
- **missing:** A durable, encrypted baseline store for per-origin security claims and comparison timestamps; A security-change classifier that distinguishes routine login activity from high-risk changes; A pendant alert escalation path for a suspected compromise, including a compact checklist and acknowledgement state

### "“Is this account notification legitimate? Compare the message I have open with the official account’s security page, explain any mismatch, and give me a safe next step without opening links or replying.”"
- **useful because:** The owner can receive a convincing account alert but has no private, hands-free way to validate it against the service he is actually logged into. The browser can inspect both authenticated evidence sources while the pendant gives a calm answer without clicking a potentially malicious link.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Background model performs domain, timestamp, event, and account-identity comparison; realtime model gives a short confidence-qualified explanation and safe next step.
- **latency:** 15–30 seconds for the open message and official security page; no network action beyond read-only navigation to a known official origin.
- **cost:** $0.03–$0.08 per verification, dominated by two page reads and evidence comparison.
- **security:** Never click message links, download attachments, type credentials, or send replies. Treat the message as hostile input. Navigate only to an owner-configured official origin, preserve URL and claim provenance, and retain no message body. Do not claim certainty when evidence conflicts; speak the mismatch and recommend manual escalation.
- **missing:** A hostile-content isolation mode that prevents message-derived URLs from becoming navigation targets; An official-origin binding supplied by the owner rather than inferred from the message; A confidence and mismatch report designed for spoken delivery, with evidence links shown on the dashboard


## What it asked for

_Nothing._
