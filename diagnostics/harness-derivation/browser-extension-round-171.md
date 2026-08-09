# Harness derivation — browser-extension — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser reachability** — Safari extension is online with 9 tabs, including authenticated Gmail and X; POST /execute browser_list_tabs succeeds and returns tab IDs plus receipts. The previously assumed tabCount=0 is stale.
  - evidence: POST /execute {actions:[{type:'browser_list_tabs'}]} returned 9 tabs at 2026-08-08T02:45:45Z, including mail.google.com and x.com/home.

## Capabilities it proposed

### "Read the authenticated conversation I'm looking at, draft a concise reply in my voice, type it into the site's compose box, and let me review it on the pendant before anything is sent."
- **useful because:** This turns the browser's unique access to logged-in conversations into a safe, tangible workflow: the owner can handle email/support/social replies from the pendant while retaining the final send decision. No other node can both see the private thread and place a draft in the real site's editor.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Use a cheap background model for thread extraction and draft variants; use realtime only for the owner's spoken edits/approval. The browser and Mac perform deterministic extraction and typing.
- **latency:** Extract 3–8 seconds, draft 2–5 seconds, type immediately; the pendant review should start within 1 second after the draft is ready.
- **cost:** ~$0.01–$0.06 per thread depending on length; token volume for quoted thread text dominates, so send a bounded, redacted excerpt and cache the extraction.
- **security:** Private thread text and the proposed reply leave Safari for model processing. Never persist raw thread text by default; keep origin/session/tab and a hash plus the typed draft receipt. Require an explicit pendant action for typing into the compose box and always stop before send, payment, or other irreversible submission. Implement per-origin read/extract/redact/never-store rules as empty owner-supplied configuration rather than assuming sites.
- **missing:** A browser action contract that accepts tabId plus a bounded extraction/compose target and returns DOM evidence in one command; A relay-to-pendant review card/audio protocol carrying draft text, origin, and an approve-edit-reject state; An explicit owner-supplied per-origin privacy configuration persisted by the browser session layer; A deterministic 'type draft but never submit' executor with recovery if the page changed

### "When I say “watch this page,” remember the authenticated Safari tab and tell me only when a meaningful value changes—like a delivery status, appointment slot, account balance, or policy deadline—with the old and new values and a link back to the exact tab."
- **useful because:** A normal web search cannot see the owner's logged-in state, and a generic notification cannot explain what changed. This makes the browser a private sensor and the pendant a low-friction interrupt channel: the owner gets a useful delta instead of repeated page dumps, and can resume the exact authenticated page on the Mac.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Use deterministic DOM selectors and normalized-value comparison first; run a small background model only when the page structure changes or a human-readable diff is needed. Realtime is reserved for speaking an urgent delta, not polling or diffing.
- **latency:** Poll on an owner-selected cadence (5 minutes to daily); detection under 10 seconds after the page changes, spoken alert under 2 seconds once the relay sees it.
- **cost:** Near-zero for selector/value polling; ~$0.001–$0.02 only for structural-diff interpretation. Bandwidth and authenticated page snapshots dominate, so retain only hashes and extracted fields.
- **security:** The watcher can expose private balances, orders, or schedules. Store origin, tab/session identity, selector, normalized old/new values, and a redacted audit receipt—not full page HTML. The owner must configure per-origin extraction and categories; never infer a universal sensitivity taxonomy. Pause when Safari logs out or the tab identity changes, and send alerts through the already-accepted offline inbox without speaking disallowed categories.
- **missing:** A durable browser watch definition with selector/semantic-anchor, cadence, and category policy; A page-watch worker that survives extension restarts and detects logout/tab replacement; A semantic diff engine that can recover when a site's DOM changes without retaining raw pages; A pendant alert payload that includes a safe spoken summary plus a tap-to-resume tab token

### "I have too many Safari tabs. From the pendant, say “triage my tabs,” then give me the three that need attention, explain why from their live authenticated contents, and let me archive, reopen, or leave each one without losing the session."
- **useful because:** This is immediately useful today with the owner's real Safari session: it turns nine unrelated tabs into an actionable queue without sending him through each page. Gmail, logged-in services, and private dashboards are precisely where public search and the relay have no reach; the Mac can safely clean up only after the owner hears the proposed list.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Use browser title/URL and bounded page extraction, then a cheap ranking model for urgency and duplicates. Use realtime only to speak the three-item result and accept a short spoken choice; deterministic Mac/browser actions handle archive/reopen.
- **latency:** 5–12 seconds for a nine-tab triage; each owner choice should execute in under 2 seconds.
- **cost:** ~$0.01–$0.04 per triage; extracted text is the main cost. Keep only compact per-tab summaries and hashes, not raw page text.
- **security:** This reads every selected authenticated tab, so selection and privacy policy must be explicit. Ship with an empty per-origin rule set and let the owner choose included origins/categories. Do not speak or persist secrets, message bodies, or financial identifiers by default; provide per-tab exclusion and a local-only mode. Closing/archive actions need an undo receipt.
- **missing:** A multi-tab browser extraction action with per-tab limits and exclusions; A tab triage ranking schema that records reasons and citations rather than opaque scores; A browser session operation for park/archive/reopen with stable tab recovery tokens; A spoken carousel UI that maps one pendant choice to one tab and exposes undo

### "Gather the facts from the authenticated pages I name—such as an order page, a support thread, and the policy page—make a short evidence-backed brief with links and quoted snippets, and read me the answer on the pendant without saving the page contents."
- **useful because:** When the answer is split across private sites, the owner currently has to copy sensitive text between tabs and explain the context. This creates a temporary, citation-preserving bridge from Safari sessions to the pendant: useful for disputes, returns, benefits, travel, and account decisions while keeping the source pages in the browser and the derived answer ephemeral.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** A background model assembles and cross-checks the bounded extracts; use realtime only for the final spoken answer or follow-up. Deterministic URL/origin checks and quote offsets provide evidence, while the model is not trusted to invent citations.
- **latency:** 15–30 seconds for three pages; a follow-up question against the retained in-memory capsule under 3 seconds.
- **cost:** ~$0.03–$0.15 per brief depending on page length; extraction and quote verification dominate. Delete the capsule after the session or on pendant command.
- **security:** This intentionally combines sensitive contexts, so the owner must explicitly name tabs/origins each time or configure an allowlist. Never store raw HTML or page text, never send content to third-party search, redact credentials/identifiers before model input, and speak only the requested facts. Show source origin and a short quote aloud so the owner can detect a bad extraction.
- **missing:** A one-shot browser capsule API that extracts only selected tab regions and returns stable quote anchors; Cross-page provenance objects that survive model summarization but expire automatically; An ephemeral relay memory scope with explicit delete/TTL and no journal persistence; A pendant interaction for naming tabs or selecting the next cited source

### "Use the verification code that just arrived in my authenticated mail to fill the waiting sign-in page in Safari, but never speak it, save it, or use it anywhere else."
- **useful because:** Two-factor flows are where the browser, mail session, and the owner’s attention currently break apart. This would let the owner complete a login while keeping the one-time secret inside the browser bridge, eliminating transcription errors without exposing the code to speech, durable memory, or a model.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Use deterministic DOM extraction for a narrowly scoped, recently received one-time-code pattern; no generative model should see or retain the code. Realtime only handles the owner’s explicit request and success/failure narration.
- **latency:** Under 5 seconds from explicit request to filling the waiting field; expire the operation after 60 seconds or navigation.
- **cost:** Negligible API cost; the dominant cost is secure implementation and testing of origin binding, not inference.
- **security:** This is credential-adjacent and must bind the code to the exact waiting origin, field, and one active login attempt. Require explicit owner invocation each time, never log the value, never put it in a receipt, refuse ambiguous pages or multiple candidate codes, and erase all buffers immediately after fill. Do not press submit.
- **missing:** A privileged ephemeral browser action for origin-bound OTP extraction and fill; Extension-side secure zeroization and redacted result receipts; A challenge/intent handshake proving the code’s destination tab before reading mail; A relay policy that prevents OTP values entering model context, journals, analytics, or pendant audio

### "Audit the security settings on the authenticated sites I select—recent sessions, recovery methods, two-factor status, and unexpected account changes—and tell me what is abnormal, with a direct path to fix each issue."
- **useful because:** The owner cannot get a trustworthy, cross-site security picture from public search or isolated app APIs. The browser can inspect the real logged-in security pages, while the pendant can surface a short urgent warning before an account compromise becomes a loss.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Use deterministic extractors for known security fields and a low-cost background model only to normalize labels across sites; use realtime for urgent narration. Never let a model autonomously change security settings.
- **latency:** 30–60 seconds for a selected set of sites; urgent anomaly audio within 2 seconds of a completed audit.
- **cost:** ~$0.01–$0.08 per site depending on page complexity; extraction and cross-site normalization dominate.
- **security:** Security pages are exceptionally sensitive. The owner must explicitly select origins, and the system must retain only normalized posture facts and redacted receipts. Never collect passwords, recovery codes, full session identifiers, or private messages. Any remediation must stop at a prepared page or draft change and show the exact intended setting.
- **missing:** Origin-specific security-page adapters with strict field allowlists; A posture schema for recovery methods, MFA state, sessions, and change history; Anomaly correlation engine that distinguishes a new device from a known travel/device change; A safe remediation navigator that preserves the current authenticated session but never commits a setting

### "Compare the account details on the authenticated pages I choose—name, address, renewal date, plan, or booking—and tell me where they disagree, with the smallest safe set of edits to make them consistent."
- **useful because:** Important errors often live between sites: an old address, mismatched passenger name, or renewal date that silently differs from the receipt. The owner can ask this from the pendant instead of manually copying private values across tabs; the system identifies the contradiction but does not silently edit accounts.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Use deterministic field extraction and normalization for dates, names, currency, and addresses; use a cheap model only for site-specific labels. Realtime speaks discrepancies and proposed edits, while browser actions remain review-only.
- **latency:** 10–25 seconds for three selected pages; a spoken discrepancy report within 2 seconds after comparison.
- **cost:** ~$0.01–$0.05 per comparison; page extraction and normalization dominate, with no need for expensive realtime inference.
- **security:** Cross-account correlation is sensitive. Require explicit per-origin selection on every run or an owner-configured allowlist, redact values in logs, show only the minimum differing fragments, and retain no raw page contents. Never change a field without a separate owner instruction and a visible before/after preview.
- **missing:** A typed cross-page field extraction contract with confidence and source anchors; Normalization for names, addresses, dates, currencies, and plan identifiers; An ephemeral comparison capsule that deletes source values after producing the diff; A browser edit-preview action that can populate—but not submit—each correction


## What it asked for

_Nothing._
