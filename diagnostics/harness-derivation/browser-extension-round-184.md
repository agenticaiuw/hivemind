# Harness derivation — browser-extension — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the private pages I already have open, compare their claims, and give me a contradiction report with a source link for every claim—without changing any tab.”"
- **useful because:** Public search cannot reach the owner's logged-in pages, while a single-page read cannot reconcile several private sources. This turns Safari's existing authenticated tabs into a private research desk: the owner gets disagreements, stale timestamps, and missing evidence instead of a blended hallucinated summary.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Local extraction and date/number normalization first; a slower background synthesis model compares claims; realtime only speaks the final short report when requested.
- **latency:** 10–30 seconds for 2–6 tabs; return partial results if one tab disappears.
- **cost:** <$0.03 per synthesis, dominated by one compact comparison call; DOM extraction and deduplication run locally.
- **security:** Do not save page bodies. Keep source URL/title/selected claim spans only in an expiring in-memory job; redact credentials, messages, payment, and health fields according to owner-supplied per-origin rules. Never navigate, click, or type during a read-only comparison.
- **missing:** A multi-tab read batch that pins a snapshot time and reports unavailable tabs explicitly; Claim-level normalization for dates, amounts, and qualifiers, with source offsets; A contradiction-result format that the pendant can summarize and the Mac can open to the exact source tab

### "“I’m handing someone my Mac—lock down my browser now, close or blank every private tab, cancel queued browser work, and tell me what was erased.”"
- **useful because:** The browser is the one surface holding sessions that nobody else can reach, so a physical pendant panic action should protect it faster than opening Safari menus. This gives the owner an immediate, comprehensible privacy response when travelling, lending the laptop, or suspecting shoulder-surfing.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** No expensive model for the lock operation; deterministic extension/Mac actions. Use realtime only to speak the receipt and any tabs that could not be closed.
- **latency:** Under 2 seconds for the extension to revoke/close tabs and under 5 seconds for Mac-agent cleanup; operate locally even if the relay is unavailable.
- **cost:** Near-zero API cost; one optional short speech generation.
- **security:** The panic action must not depend on LTE or model inference. It should revoke browser command leases, stop pending extraction, clear only relay-held transient page material, and optionally close tabs; it must never delete browser history, saved passwords, or owner files unless separately configured. Persist only an audit receipt (counts, origins optionally hashed). Requires an explicit owner-configured set of origins/actions, shipped conservative and empty until chosen.
- **missing:** A signed low-latency panic event from the pendant/USB bridge to the Mac agent; Safari extension command to revoke all pending commands and close or navigate private tabs; A relay endpoint to cancel transient browser jobs and emit a deletion receipt; An owner-configurable panic policy with dry-run testing

### "“Read this long private page to me in chunks; when I interrupt from the pendant, tell me exactly where I stopped and let me resume on the same section tomorrow.”"
- **useful because:** This combines the browser's authenticated access with the pendant's only always-near interaction: the owner can consume a private document while walking, interrupt naturally, and resume without searching the page again. It is more useful than a generic page summary because the spoken stream has a durable semantic position.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background model to segment and index the page; realtime handles only the current spoken chunk and interruption. Store a tiny pointer, not page text.
- **latency:** First chunk in 2–5 seconds; interruption acknowledged in under 500 ms locally; resume lookup under 3 seconds.
- **cost:** <$0.02 per long page, dominated by one segmentation/summarization call; repeated resumes reuse the compact index.
- **security:** Never persist raw authenticated page content or send it to the pendant flash. Persist only origin, title hash, document fingerprint, section/paragraph anchor, and owner-created label under explicit per-origin retention rules. If the page changes, report stale anchor rather than guessing.
- **missing:** A browser extraction/segmentation result with stable semantic anchors, not just truncated text; A cross-surface playback cursor keyed by document fingerprint and owner label; A durable pointer store with expiry and deletion, plus a resume command from the pendant; Integration with the already accepted playback interruption primitive

### "“Tell me which of my configured private sites can no longer complete a read because I’m signed out, and give me a one-tap way to reopen each login page—never enter credentials.”"
- **useful because:** Authenticated automation silently failing is worse than no automation: the owner may believe a work or bill check happened. A periodic, privacy-bounded login-state probe lets the relay and pendant report only capability health, while Safari remains the sole place for credentials and the owner completes login themselves.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic origin-specific probes and a cheap classifier for login-wall versus normal error; no realtime model unless the owner asks for explanation.
- **latency:** Probe configured origins in parallel within 10 seconds; alert only on state transitions, not every poll.
- **cost:** Near-zero API cost; browser requests and local DOM checks dominate.
- **security:** Configuration must be owner-supplied and empty by default. Never extract usernames, cookies, tokens, or page bodies; return only origin, state (healthy/login-wall/error), timestamp, and a redacted reason. Reopening a login page is reversible; typing credentials is explicitly out of scope.
- **missing:** An origin health-check definition with a login-wall detector and allowed landing URL; A state-transition store with quiet hours and stale/unknown distinction; A pendant alert mapping for login failures and a Safari action to reopen the origin

### "“Teach the pendant one private website by showing it the three fields I care about, then let it extract only those fields in future—show me the rule before you save it.”"
- **useful because:** Today authenticated browser automation requires engineering selectors or an invented site list. The owner should be able to create a precise, privacy-minimized site skill interactively: select the relevant page regions, name their meaning, preview several runs, and keep only the approved fields. This makes private workflows buildable by the owner rather than by guessing their sites or retaining whole pages.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap local model for DOM/accessibility clustering and selector generation; use realtime only to conduct the short teaching conversation. Validation should be deterministic across sample page states.
- **latency:** Teaching session under two minutes; preview under five seconds per run; future extraction under ten seconds.
- **cost:** <$0.02 for initial semantic labeling and negligible cost for later deterministic extraction; DOM snapshots and rule testing dominate.
- **security:** The extension must keep credentials and unselected fields out of every snapshot. Store an inspectable rule (origin, landmark, field label, extraction transform, retention/speech policy), not page text. The owner must explicitly approve each field and may delete the rule and all derived values. Configuration ships empty by default.
- **missing:** An interactive extension command that returns owner-selected DOM/accessibility regions with stable landmarks; A rule compiler that produces and tests resilient extraction recipes against multiple page states; A per-field policy editor and versioned approval record exposed through the Mac/pendant; A test-run harness that reports selector drift without reading unrelated fields


## What it asked for

_Nothing._
## Its own summary

Browser access is live now: POST /execute successfully navigated Safari from no tab to example.com and returned a real tab/command receipt; a subsequent browser_read_page reached the owner's existing ChatGPT session. I recorded four new owner-facing capabilities: private multi-tab contradiction reports, a pendant-triggered browser privacy panic/cleanup, resumable spoken reading of authenticated pages, and login-state health alerts that never touch credentials. The first form-audit idea collided with an existing safety-net capability and was correctly not recorded.

**Biggest unknown:** I still need the owner’s explicit browser configuration: the first 3–5 origins to automate, which content categories may be spoken, and which may never be persisted. I also need the implementation work for structured multi-tab extraction, signed pendant panic delivery, semantic playback cursors, and origin-specific login-wall probes; the existing routes are primitives, not these capabilities.

