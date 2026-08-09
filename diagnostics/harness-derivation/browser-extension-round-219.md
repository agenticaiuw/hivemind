# Harness derivation — browser-extension — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“While I’m wearing the pendant, check the authenticated pages I already have open, tell me the one thing that needs my attention, and prepare the next action without sending or submitting anything.”"
- **useful because:** This is the browser node’s uniquely valuable job: it can see private logged-in pages while the relay hears the owner and the Mac can act. It turns a vague spoken request into a bounded triage: read the live sessions, extract only actionable claims, then prepare (but do not commit) a reminder, draft, or navigation for the owner to inspect.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime handles the short spoken request and final answer; a cheaper background planner performs page extraction/ranking and produces a structured action preview.
- **latency:** 10–20 seconds for one to three already-open tabs; if a page is slow, return partial results and a durable job status rather than holding the voice turn.
- **cost:** Usually one cheap extraction/planning call plus a short realtime response; browser and Mac execution dominate latency, not token cost. Avoid sending page bodies to the model—send capped claims and provenance.
- **security:** Authenticated page content leaves Safari only as the minimum extracted claims. Persist findings, not HTML, screenshots, or page text, using the existing 24-hour browser TTL and provenance. Configuration must ship empty and let the owner define per-origin read/extract/redact/never-store and per-category speak/store rules. Stop before any send, purchase, or form submit and show the exact proposed mutation.
- **missing:** A first-class browser triage orchestration job that enumerates the live Safari session, applies an explicit read-only action allow-set, ranks extracted claims by urgency, and emits a Mac action preview; A pendant-facing result card/voice protocol for “one thing + prepared next action”; Owner-supplied per-origin and category policy configuration (initially empty)

### "“I’m looking at this page—when I press the pendant button, explain the relevant section and answer my follow-up questions without losing my place.”"
- **useful because:** The owner can ask about a private dashboard, bill, policy, or form while keeping Safari open and hands off the keyboard. The browser supplies the authenticated DOM and focused/visible context; the pendant supplies low-friction questions; the relay answers grounded in that exact page rather than guessing from a URL or public search.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** Realtime for the spoken question and concise grounded answer; a low-cost extractor first reduces the page to visible text, headings, selected values, and URL, then realtime sees only that context.
- **latency:** Under 5 seconds for capture plus answer on a normal page; preserve a short-lived page-context ID so follow-ups do not re-upload the entire page.
- **cost:** One small extraction and one short realtime turn per question. Context-ID reuse materially reduces token cost; never send screenshots unless DOM extraction fails and the owner explicitly enables visual fallback.
- **security:** Only the current tab and visible/focused region are captured, with sensitive fields redacted by origin policy. Do not persist page contents; retain only a short-lived context ID and any explicitly requested claim under existing browser provenance/TTL rules. The button must not click, type, or submit.
- **missing:** A working browser_read_page/browser_snapshot command path that returns focused selection and visible region, not merely a URL; A context lease keyed to tab and page revision, with invalidation on navigation or login change; Pendant-to-browser question correlation and a spoken “context expired” fallback

### "“Before I submit this checkout, application, or message, read the final page aloud, calculate the real commitment, and leave it ready for me—but do not press Submit.”"
- **useful because:** Irreversible browser actions are where a private-session browser is most valuable and most dangerous. The owner gets a last-mile audit of recipients, amounts, dates, attachments, and changed fields while Safari remains authenticated; the Mac can independently compute totals or compare dates, and the pendant makes the stopping point audible without pretending to be a security gate.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Cheap deterministic extraction and field diff first; realtime only summarizes the final commitment and answers questions. Use vision only when a form is canvas-rendered or the DOM is incomplete.
- **latency:** 3–8 seconds after the owner says “check this”; never wait indefinitely on a dynamic page. Return a field-by-field preview and a stable review token.
- **cost:** Low: one browser extraction, optional local calculation, and a short spoken summary. Screenshots/vision are the expensive fallback and should be opt-in per origin.
- **security:** The browser action allow-set is read-only for this workflow: inspect, extract, and compare, never click submit/send/purchase. Redact secrets and payment credentials; do not persist page text. Show exact target, amount, recipient, and changed fields. The owner may then use normal Safari controls themselves; this workflow does not add a confirmation gate to the system.
- **missing:** A final-form extractor that normalizes labels, values, recipients, totals, dates, attachments, and disabled/enabled submit controls across sites; A page-revision-bound review token and diff against the last extracted state; A structured handoff from browser fields to Mac local calculators/calendar without exposing unrelated page content

### "“Copy the relevant details from this logged-in page into the other logged-in site, translate the fields correctly, and leave the second form ready for review without submitting it.”"
- **useful because:** This is a genuinely browser-exclusive capability: the owner’s authenticated data may exist in two separate services that no public API or Mac-only agent can access. It could transfer an address from an account portal into a shipping form, claim details into an insurer form, or an itinerary into a travel site while preserving the owner’s existing sessions. The owner gets the labor-saving part without surrendering control of the irreversible submit.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** A cheaper structured mapper performs field matching, normalization, and validation; realtime is used only for spoken clarification of ambiguous fields. Vision is a fallback for unusual rendered forms.
- **latency:** 15–30 seconds for two already-open authenticated tabs. Return a field-by-field transfer report and stop with the destination form staged.
- **cost:** One extraction call, one mapping/validation call, and browser fill actions. Token cost stays bounded by sending only selected source fields and destination labels, never complete page bodies.
- **security:** Cross-origin transfer must be explicit per invocation and limited to fields the owner names or approves. Never copy passwords, MFA codes, payment CVVs, session tokens, or hidden fields. Preserve a reversible field ledger showing source label/value, destination label/value, transformations, and omissions. Do not submit or send. Persist no page text; retain only a short-lived provenance record if the owner asks.
- **missing:** A cross-origin transfer planner that can hold two authenticated browser session handles simultaneously; Schema-aware field matching with normalization, ambiguity reporting, and explicit exclusion of credential/payment fields; A browser fill transaction with per-field undo and a destination-page revision check before each write; A pendant-readable transfer summary and a way to correct one field by voice before staging the rest

### "“Compare these two logged-in services and tell me whether they agree—show me exactly where they differ and which page supports each fact.”"
- **useful because:** People routinely have conflicting private records: a travel booking versus an airline account, an invoice versus a payment portal, or an appointment portal versus a calendar. Today the system can inspect a page or act on the Mac, but cannot perform a provenance-preserving cross-origin reconciliation. This would return a small evidence-backed discrepancy report instead of a vague summary or an unsafe correction.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap deterministic extraction and normalization first; a slower background model resolves semantic equivalence and contradictions. Realtime only speaks the conclusion and lets the owner ask about one discrepancy.
- **latency:** 20–60 seconds for two or three authenticated pages; stream each source as it arrives and clearly mark unresolved conflicts.
- **cost:** One extraction pass per source and one comparison pass. Keep only compact claims, URLs, timestamps, and field-level evidence; page HTML and screenshots are not sent or stored.
- **security:** Read-only browser actions. The owner chooses the tabs/origins for each comparison; no silent crawling of other sessions. Claims inherit the existing short browser TTL and provenance. Never infer that one source is authoritative without saying so, and never modify either service automatically.
- **missing:** A multi-source comparison job that can bind named source tabs and maintain independent provenance for every claim; A normalization/contradiction engine for dates, amounts, names, statuses, and time zones; A compact evidence capsule that the pendant can identify by source and field without speaking sensitive page text aloud

### "“On this private settings page, explain what each available change would affect in my other accounts and devices, then stage only the changes I choose without applying them.”"
- **useful because:** Settings pages hide consequential dependencies: changing a forwarding rule, recovery method, privacy switch, subscription tier, or device permission can affect several services. A browser node can see the actual authenticated options and current values; the Mac can model local consequences; the pendant can make the impact understandable while the owner is away from the keyboard. This is an impact analysis and staged configuration workflow, not merely reading a page or filling a form.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Deterministic extraction identifies controls and current values; a background model builds a dependency/impact explanation from the page and local machine context. Realtime presents only the selected change and its consequences.
- **latency:** 10–30 seconds for one settings page plus known local dependencies; complex changes should return an asynchronous impact report with a review token.
- **cost:** One extraction and one impact-analysis call, with optional local inspection. Keep model context to control labels, current values, linked domains, and documented effects rather than full page content.
- **security:** Read-only by default. Never infer or alter security settings silently. Any staged mutation must include an exact before/after diff, affected origins/devices, rollback instructions, and a page revision check. Secrets and recovery codes are excluded. Nothing is applied by this workflow.
- **missing:** A settings-control semantic extractor that distinguishes informational controls, reversible changes, and security-critical changes; A dependency graph connecting browser-origin settings to Mac accounts, local apps, and other registered surfaces; A reversible staged-change format that can be reviewed by voice and applied later as a separate owner-directed action


## What it asked for

_Nothing._
