# Harness derivation — browser-extension — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Capability discovery reports Safari on MacIntel online with 1 tab, unlike the earlier tabCount=0 state; browser command wrappers still fail resolution, so this is observable device presence but not yet usable page content.
  - evidence: discover(devices) returned Safari on MacIntel — browser · Safari · 1 tab(s) · online; browser_read_or_navigate(browser_snapshot) returned unresolved ambiguity and browser_enqueue_command_implemented(browser_list_tabs) returned unresolved.

## Capabilities it proposed

### "“Before I submit this, check the page I'm on against my calendar and local files, flag conflicts, and prepare exactly what would be sent—but do not submit.”"
- **useful because:** This turns the browser's authenticated form/cart into a second pair of eyes: it can catch a double-booked appointment, stale attachment, wrong date, or mismatched account before an irreversible click. No single node can see the logged-in page and the Mac's local context together.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background/standard model for extraction and comparison; realtime only for the owner's spoken follow-up.
- **latency:** 10–20 seconds for page extraction plus local context; then immediate spoken summary. Submission remains staged and reviewable.
- **cost:** Roughly $0.01–$0.05 per check; browser extraction and context packaging dominate, not speech.
- **security:** The page's claims leave Safari only as short-lived, host-keyed findings under existing 24-hour/200-character browser retention. Local files are read only when explicitly named by the task. Show the exact staged payload and destination; never submit without a separate owner command.
- **missing:** A cross-surface compare-and-stage orchestrator joining browser form previews with calendar/files; A reliable active-page extraction command and field-level provenance in the preview; Owner-supplied per-origin configuration, initially empty

### "“Is this service really broken, or is it just my browser? Check the authenticated status page, test the Mac's network path, and tell me what evidence agrees or conflicts.”"
- **useful because:** When an account dashboard says outage, lockout, or payment failure, the owner needs diagnosis rather than a screenshot. Safari can see the logged-in truth; the Mac can independently test DNS/HTTP/connectivity; the relay can reconcile them and speak a confidence-labeled answer through the pendant.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap background model for evidence normalization and contradiction detection; realtime only if the owner asks follow-up questions.
- **latency:** Under 30 seconds, with partial results spoken as they arrive if one surface is slow.
- **cost:** About $0.01–$0.03 per diagnosis; network probes and browser reads are the dominant work, with tiny synthesis cost.
- **security:** Never expose credentials or retain page bodies. Persist only short claims with URL/host provenance and a 24-hour TTL. Network tests must be read-only and limited to the host the owner named. Report disagreement explicitly rather than asserting the service is down.
- **missing:** A named-host diagnostic workflow that joins browser evidence with allowlisted Mac network probes; A browser page-to-host binding so a status page cannot silently cause probes to an unrelated domain; Pendant alert formatting for 'browser says X / network says Y' uncertainty

### "“I’m looking at this page—tell me the important parts, and if I ask a follow-up, answer from the page I’m actually on.”"
- **useful because:** This is the browser tier's defining superpower: a spoken assistant that can see an authenticated page the relay and Mac planner cannot access, while the pendant remains hands-free. It would make dense bills, portals, policies, and dashboards usable without copying text or exposing a login to another service.
- **path:** browser → pendant → relay → mac-bridge
- **model tier:** Use a cheap extraction/summarization model for the page; reserve realtime for the short conversational answer. Do not send full HTML on every turn—cache a page fingerprint and only resend the relevant section or changed DOM.
- **latency:** Initial page capture 5–12 seconds; follow-ups 2–5 seconds when the page fingerprint is unchanged.
- **cost:** Approximately $0.01–$0.04 per page plus follow-ups; DOM extraction and context transfer dominate. Caching cuts repeated-turn cost substantially.
- **security:** Authenticated page content is sensitive. Keep raw text in memory only, persist only bounded claims with existing browser provenance/24-hour TTL, redact secrets and payment fields before speech, and tell the owner which origin supplied each answer. The owner must explicitly invoke page reading; never poll arbitrary tabs continuously.
- **missing:** A functioning browser active-tab/read-current-page command (the current wrappers cannot resolve reliably); A page-context cache keyed by tab/origin/fingerprint with section-level retrieval; Pendant intent routing for 'this page' and a spoken citation such as title, origin, and last-read time; An explicit empty per-origin policy configuration that the owner can populate later

### "“Before I act on this logged-in page, tell me which account and identity it is actually operating as, and warn me if that differs from the person, organization, or account I meant.”"
- **useful because:** A browser can be authenticated and still be authenticated as the wrong customer, workspace, tenant, or billing identity. This catches the dangerous class of errors that ordinary form previews miss: editing a client’s record instead of mine, paying from the wrong account, or uploading into the wrong organization. Safari supplies the authenticated identity cues, the Mac supplies the owner’s intended identity from the current task/calendar/file context, and the relay turns disagreement into a short pendant warning.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap background extraction and entity matching; realtime only to answer a spoken clarification. Use deterministic string/domain matching first and invoke a model only for ambiguous identity labels.
- **latency:** 3–8 seconds before any staged action; a warning must arrive before the action preview is presented.
- **cost:** About $0.005–$0.02 per check; DOM extraction and identity normalization dominate, with model calls only for ambiguity.
- **security:** Identity cues are sensitive and must not be retained as page text. Store only a bounded result (matched/mismatched/unknown, normalized account label, origin, timestamp) under existing browser provenance and short TTL. Never infer or announce a personal identity from weak cues; say unknown. The check is advisory and must not silently block the owner's maximum-access policy.
- **missing:** An authenticated-identity extractor that recognizes tenant/workspace/account cues without retaining page bodies; A task-scoped intended-identity record assembled from the owner’s spoken goal and Mac context; A pre-action hook that sends the mismatch or unknown warning to the pendant before execution; Owner-configurable rules for which identity labels may be spoken aloud

### "“Reconcile this transaction across the logged-in site and my Mac: did it actually go through, is it duplicated, and what evidence proves the answer?”"
- **useful because:** A confirmation page, a pending bank entry, and a receipt email can disagree for hours. The browser is the only body with the authenticated transaction state; the Mac can inspect local receipts or exports; the relay can correlate IDs and dates and tell the owner whether to wait, retry, or contact support. This prevents duplicate payments without requiring the system to move money.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background model for receipt/transaction entity matching, with deterministic exact-ID and amount checks first; realtime only for follow-up questions.
- **latency:** 15–30 seconds for the first reconciliation; under 5 seconds for follow-ups while evidence fingerprints are unchanged.
- **cost:** Approximately $0.02–$0.06 per reconciliation; document extraction and cross-source matching dominate.
- **security:** Financial values and account identifiers must remain ephemeral except for a short redacted evidence capsule. Speak masked account labels and last-four digits only, never full numbers. Persist claims with host, URL, timestamp, and TTL—not page text or screenshots. No retry, refund, or support message is sent automatically.
- **missing:** A transaction evidence normalizer spanning browser DOM, local mail/files, and optional calendar context; A contradiction-aware correlation engine that distinguishes pending, settled, reversed, and duplicated states; A pendant response format that cites sources and confidence without speaking secrets; Explicit owner rules for which financial categories may be spoken or persisted

### "“When this site asks for consent, explain what it will actually share or authorize, compare it with my privacy rules, and stage the safest choice without clicking accept.”"
- **useful because:** Consent dialogs hide scope behind vague labels and are especially hard to inspect hands-free. Safari can inspect the authenticated origin and its permission/consent details; the Mac can compare them with an explicit owner policy; the pendant can give a plain-language warning and leave a reversible choice staged. This is a browser-only protection neither the relay nor the Mac can provide without seeing the live session.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap structured extraction plus a rules engine for known permission scopes; background model only to translate unfamiliar legal text. Realtime is reserved for the owner’s clarification.
- **latency:** 5–15 seconds after the owner asks; no click occurs until the owner explicitly chooses the staged option.
- **cost:** About $0.01–$0.04 per dialog; DOM extraction and legal-text compression dominate.
- **security:** Do not persist the full consent text or identifiers. Keep a bounded summary, origin, scope, and policy decision with provenance and short TTL. Treat unknown scopes as unknown rather than safe. This is advisory and transparent, not a hidden blocker: the owner can choose any option after hearing the tradeoff.
- **missing:** A consent/permission-dialog detector that extracts concrete scopes, recipients, duration, and data categories; An owner-editable privacy policy schema with empty initial configuration and per-origin overrides; A staged browser choice object that can be reviewed and then clicked explicitly; Pendant speech templates for scope, consequence, and uncertainty


## What it asked for

_Nothing._
## Its own summary

Discovered Safari is now online with one tab, but every granted browser wrapper I tried still fails live resolution (snapshot is ambiguous; list-tabs is unresolved). I recorded three capabilities: (1) pre-submit authenticated-form checking against Mac calendar/files, (2) browser-vs-network outage diagnosis with explicit disagreement, and (3) hands-free 'what matters on the page I’m looking at?'—the most useful browser capability and the one that makes the pendant/browser pairing uniquely valuable.

**Biggest unknown:** I still need one reliably resolved read-current-page/active-tab command (using the inventory's exact browser_snapshot/browser_read_page action spelling), plus the implementation of the page-context cache and pendant intent routing. Separately, the owner still needs to supply the empty-by-default per-origin read/extract/redact/never-store policy and speech/retention preferences; I will not invent sites or sensitivity categories.

