# Harness derivation — browser-extension — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What’s broken in my projects right now?”"
- **useful because:** The browser can see private GitHub/CI pages while the Mac can inspect local repositories. Together they can distinguish a real production failure from stale email noise, deduplicate repeated alerts, and give me a short spoken incident list with links and the exact next diagnostic command—something neither browser nor Mac can establish alone.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use the realtime tier only to interpret the spoken request and deliver the final short answer; use a cheaper background planner for parallel tab extraction, alert clustering, and local read-only diagnostics.
- **latency:** 30–60 seconds for the first incident digest; stream the first confirmed issue to the pendant while remaining projects finish.
- **cost:** Roughly one low-latency turn plus 2–4 cheap extraction/diagnostic calls; browser and shell calls dominate time, not tokens.
- **security:** Private GitHub/CI page text and local diagnostic output leave the browser/Mac only to the relay for synthesis. Read-only by default; never rerun, merge, deploy, or edit without a separate request.
- **missing:** A cross-surface incident correlator that joins authenticated browser alerts to local repository/CI evidence; A read-only allowlisted repository diagnostic bundle exposed to mac-terminal; A compact spoken-result route that retains source links and confidence per incident

### "“Read me the page I’m looking at, and let me get back to this exact spot later.”"
- **useful because:** A private Safari page is the only source this system can access behind the owner’s existing login, but today its meaning is stranded in a tab. The extension should extract the visible section, relay a concise spoken summary to the pendant, and preserve a return capsule (URL, tab, heading, and text anchor) so a later pendant request reopens the same place on the Mac.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime handles the short spoken summary; a cheaper background model creates the normalized anchor and redacts unnecessary page text.
- **latency:** Under 8 seconds to speak the first summary; reopening the saved spot should take under 15 seconds when Safari is online.
- **cost:** One short realtime response plus inexpensive extraction/embedding; page text size is the dominant variable, so cap the capsule to the selected region rather than the whole page.
- **security:** The capsule contains private page text and a login-bound URL. Encrypt at rest, set a short TTL, expose delete from the pendant, and never include cookies or page-wide content. Reopening is reversible navigation; do not submit forms.
- **missing:** A durable cross-surface page capsule store with TTL and owner-visible deletion; Browser extraction that returns stable heading/DOM text anchors and can navigate back to them; A pendant phrase/button binding for listing and reopening recent private-page capsules

### "“Make sure my important Safari tabs are still usable.”"
- **useful because:** A tab can exist yet be a failed page, a login expiry, a blank frame, or an extension-inaccessible document—as live evidence shows with three tabs online but the active example.com tab titled “Failed to open page.” A session-health pass would check the owner’s named tabs, reopen broken URLs without losing session affinity, and tell me exactly which ones need me to sign in.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background checker for navigation/readability tests and classification; realtime only speaks exceptions that need the owner’s attention.
- **latency:** Run on demand in 20 seconds or less for 3–6 tabs; emit each failure as soon as it is verified.
- **cost:** Mostly browser round trips; low model cost if results are reduced to status codes and short failure reasons.
- **security:** Never enter credentials or bypass MFA. Keep page contents out of health telemetry; report only URL domain, title, access state, and failure reason. Reopening a tab is reversible but must not close the owner’s existing tab.
- **missing:** A browser session-health action that tests extension frame access separately from tab existence; A non-destructive tab recovery operation that opens a replacement while preserving the named session; A small status-to-pendant alert mapper with suppression until state changes

### "“Before you act on this private webpage, tell me if anything on it is trying to manipulate you or smuggle in instructions.”"
- **useful because:** Authenticated pages can contain hostile or accidental instructions aimed at an agent rather than the owner. The owner should get a clear separation between page facts and untrusted page directives before the system clicks, types, or carries anything across surfaces.
- **path:** browser-extension → faculty-perception → faculty-judgement → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper background classifier for page-level injection screening and extraction; use realtime only to explain a detected risk in plain speech and answer the owner’s follow-up.
- **latency:** Under 5 seconds for an initial risk banner or spoken warning; deeper cross-page comparison can continue in the background.
- **cost:** Low-to-moderate model cost, dominated by sending only suspicious snippets and structural metadata rather than whole private pages.
- **security:** Page content remains untrusted data and must never gain tool authority. Preserve the original URL and suspicious snippet for audit, redact secrets, and never silently continue an action after a high-confidence injection finding.
- **missing:** A browser trust-boundary representation that labels extracted text as untrusted page data; A cross-surface action planner rule that prevents page text from becoming an executable instruction; A concise pendant warning format with a link back to the exact suspicious region

### "“Explain the chart or dashboard I’m looking at, even if the page has no readable text.”"
- **useful because:** Many logged-in dashboards render their important information into canvas, SVG, or inaccessible visual widgets. The browser can reach the page, while mac-vision can interpret a screenshot and the pendant can deliver a compact spoken explanation; today no path combines those three forms of access.
- **path:** browser-extension → mac-vision → faculty-perception → relay-realtime → pendant
- **model tier:** Use a vision-capable background model for chart extraction and trend calculations; reserve realtime for the owner’s spoken question and the short answer.
- **latency:** 10 seconds for a first chart description and 30 seconds for a cited trend comparison across two dashboards.
- **cost:** Vision inference and screenshot transfer dominate; crop to the chart region and cache a low-resolution, short-lived image rather than sending the entire tab.
- **security:** Screenshots may contain private names, balances, or tokens. Crop and redact before relay, encrypt temporary artifacts, expire them quickly, and require explicit follow-up before clicking any visual control.
- **missing:** A browser screenshot/crop result with the tab URL and bounding-region metadata; A mac-vision chart interpreter that returns values, axes, uncertainty, and source coordinates; A spoken answer format that states when a value was estimated from pixels rather than read from the DOM

### "“Find every subscription I’m paying for on sites I’m already logged into, show me the renewal dates and cancellation path, and keep a review list—do not cancel anything.”"
- **useful because:** Recurring services are fragmented across private account pages and often hide renewal terms behind dashboards. The browser is uniquely able to inspect those authenticated pages; the Mac can normalize dates and totals; the pendant can give a useful spoken summary without taking a destructive action.
- **path:** browser-extension → mac-planner → mac-terminal → faculty-judgement → relay-realtime → pendant
- **model tier:** Use a cheaper background model for account-page extraction, merchant/entity deduplication, and date normalization; realtime only answers clarifying questions and reads the prioritized list.
- **latency:** A first account-by-account result in 1–2 minutes, with incremental results as each site is inspected; no need to keep the low-latency model engaged.
- **cost:** Browser navigation and page extraction dominate. Keep model cost bounded by sending only renewal, price, merchant, and cancellation-policy snippets, not full account pages.
- **security:** This exposes financial and account information. Store only merchant, amount, cadence, renewal date, source URL, and evidence snippet with a short TTL; never enter credentials, cancel, or change billing. Warn about sites where cancellation requires a destructive click.
- **missing:** A user-started authenticated account inventory workflow with explicit domain scope and per-site session affinity; A normalized subscription record with evidence, confidence, currency, cadence, and renewal-date provenance; A non-mutating review queue and pendant summary for follow-up cancellation instructions


## What it asked for

_Nothing._
## Its own summary

Three new owner-facing capabilities recorded: (1) spoken cross-surface project-incident triage joining private GitHub/CI tabs with read-only local repo diagnostics; (2) a private-page spoken summary plus a short-lived return capsule that reopens the exact Safari location from the pendant; (3) Safari session-health checks that distinguish an existing tab from a readable, authenticated page and recover broken tabs non-destructively. Live Safari is online with three tabs, but current usability is not trustworthy: the active tab is a failed example.com page, and a Gmail read returned an extension-frame access failure despite an earlier successful read. I told mac-planner this evidence.

**Biggest unknown:** Whether the extension can reliably access ordinary authenticated pages after a fresh browser command (the live failure may be per-frame/tab, not global). The remaining product work is connective: incident correlation, page-capsule persistence/TTL, and session-health classification/recovery; no new browser enqueue tool is needed for a first prototype because POST /execute is currently usable.

