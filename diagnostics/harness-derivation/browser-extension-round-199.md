# Harness derivation — browser-extension — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch the authenticated pages I explicitly add, and tell me only when a meaningful change happens—summarize what changed, cite the old and new claim, and put the short alert on my pendant if the Mac is away."
- **useful because:** This is the single most useful browser-specific capability: it turns existing logins into a quiet personal monitoring service without pretending public search can see them. The browser holds the session, the relay compares claims, and the pendant reaches the owner when no screen is open.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background change detection uses a cheap model; realtime is used only to compress a confirmed change into a spoken alert.
- **latency:** Polling or scheduled checks can take 1–5 minutes; a confirmed urgent change should reach the pendant within 15 seconds.
- **cost:** Roughly $0.01–$0.05 per changed page per day; most checks should be DOM/hash comparison with no model call. Storage and delivery dominate less than model summarization.
- **security:** Ship with an empty per-origin configuration. The owner explicitly adds origins and chooses read/extract/redact/never-store and may-speak/must-not-speak rules. Persist only short claims and provenance, never page text, HTML, or screenshots; require no confirmation for reading but stop before any mutation.
- **missing:** owner-configurable origin rules UI and API; scheduled browser session runner with per-origin selectors or semantic anchors; claim-level old/new diffing and urgency ranking; relay-to-pendant alert delivery for browser findings

### "When I say 'what am I looking at?' or 'is this important?', read the active Safari page behind my login, answer from the live page in three spoken sentences, and let me ask a follow-up that stays grounded to that exact tab until I say stop."
- **useful because:** The owner can currently get either generic web search or a raw page read, but not a low-friction conversation about the private page already in front of him. Binding follow-ups to tab ID and a short-lived evidence capsule prevents answers drifting to a similarly named public page.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime for the short answer and follow-up; no background model unless the page is long, where a cheaper extraction pass produces claims first.
- **latency:** First answer under 5 seconds; follow-ups under 3 seconds while the tab remains open.
- **cost:** About $0.005–$0.03 per question depending on page length; page extraction and repeated context are the main costs, so send claim capsules rather than full text.
- **security:** Read-only browser action set; never click or type for this intent. Keep the page body out of memory, retain only capped claims with URL, host, content hash, and 24-hour expiry, and apply the owner's empty-until-configured origin policy.
- **missing:** intent route that resolves active tab and creates a grounded conversation handle; tab-bound evidence context with expiry and invalidation on navigation; pendant phrase/button trigger and follow-up correlation

### "Let me collect two or more pages from my open Safari tabs, ask one question about them, and receive a short comparison with links and the exact claims supporting it—then save the comparison as a note without saving the page contents."
- **useful because:** This makes the browser genuinely collaborative with the planner: authenticated pages can be compared even when no other node can access them, while the owner gets a decision-ready answer instead of tab-by-tab summaries. A provenance-backed note makes the result inspectable and expires the sensitive source claims.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap extraction and deduplication first; a capable non-realtime model synthesizes only the selected claims. Realtime reads the final short answer aloud.
- **latency:** Selecting and reading 2–5 tabs in 10 seconds; synthesis in 10–20 seconds; spoken result immediately after.
- **cost:** Approximately $0.03–$0.15 per comparison, dominated by synthesis over multiple claim sets; no cost for unchanged cached evidence.
- **security:** Selection is explicit by tab ID, and all actions are read-only until the owner separately asks to save a note. Store only the comparison and provenance, not source page text; redact secrets before model submission and expire browser claims after 24 hours.
- **missing:** multi-tab selection/collection command in the extension; claim-level citation format that survives navigation; note writer that stores synthesis plus provenance without source bodies; pendant gesture or spoken command to add the current tab to a temporary basket

### "Start this authenticated web task and keep working until it is finished or genuinely needs me—for example, gather the required information, complete the safe steps, and if the site presents 2FA, CAPTCHA, or a human-only decision, alert my pendant with exactly what I need to do; after I intervene, resume at the same step without losing the work."
- **useful because:** Today browser automation is a sequence of isolated commands. The owner cannot delegate a long, login-bound workflow that survives the moments only a human can handle. This would make the browser a persistent coworker: it can work while the owner is away, stop precisely at a human boundary, and continue rather than restarting or guessing.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheaper background planner for navigation and form-state tracking; use realtime only to explain a blocker or deliver the short pendant prompt. A stronger model is reserved for recovering when the site changes layout.
- **latency:** Ordinary safe steps can take minutes without conversation. A human-blocker alert should arrive within 10 seconds, and resumption should begin within 5 seconds of the owner completing the intervention.
- **cost:** Approximately $0.05–$0.50 per workflow, dominated by browser observations and recovery planning; most actions should use deterministic selectors and cached page structure rather than a model call.
- **security:** The owner has maximum-access policy, so this is not a blanket confirmation gate. The system must still stop at genuine human-only challenges and never ask the model to infer or store passwords, one-time codes, CAPTCHA answers, or private page bodies. Persist only an encrypted workflow checkpoint: origin, tab/session identity, action state, redacted field labels, and provenance. The owner should be able to cancel or inspect the checkpoint from the dashboard.
- **missing:** durable browser workflow/checkpoint state that survives tab and extension restarts; human-blocker detection for 2FA/CAPTCHA and a pendant alert/resume protocol; DOM/state diff recovery when a site changes between steps; an explicit action manifest showing completed, pending, and skipped steps; relay scheduling and retry ownership for long-running browser jobs

### "Let me mark a region of any logged-in page as private—by saying 'never send the right column' or drawing over it—and then ask the AI about the rest of the page. It should answer from the unmarked content while proving that the private region never left Safari."
- **useful because:** The owner could finally use the browser agent on mixed pages such as invoices, medical portals, or account dashboards without choosing between no help and exposing an entire screen. This is a user-visible privacy control, not an invented site sensitivity list.
- **path:** browser-extension → relay-realtime → pendant → dashboard
- **model tier:** A local deterministic redaction pass handles DOM regions and screenshots; a cheaper model summarizes only the surviving claims. Realtime speaks the answer.
- **latency:** Marking a region should be immediate; a page answer in under 5 seconds.
- **cost:** About $0.005–$0.03 per question; local redaction reduces prompt tokens and therefore dominates the savings.
- **security:** The extension must enforce redaction before serialization, not ask the model to redact after upload. Store only the redaction rule and a page hash, never the excluded text. Clearly show when a page cannot be safely segmented and refuse that read rather than claiming proof.
- **missing:** extension-side region selection and DOM/screenshot redaction; a verifiable redaction receipt showing excluded nodes and hashes; relay support for claim sets with hard exclusion boundaries; pendant command to create and clear a temporary page privacy rule

### "Audit the security and privacy settings inside my logged-in accounts, compare them with my stated preferences and local device state, and give me one prioritized fix at a time—preparing each safe change in the browser but leaving the final high-impact change visible for me to inspect."
- **useful because:** No public search can inspect the owner's real account settings, and a generic Mac security check cannot see web-only sessions, recovery methods, sharing permissions, or active subscriptions. The browser, Mac, relay, and pendant together could turn a scattered security chore into a finite prioritized queue.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** Background extraction and deterministic policy checks handle most settings; a stronger model only resolves ambiguous labels across sites. Realtime reads one fix and its reason aloud.
- **latency:** An audit may run for several minutes in the background; each finding should be available within 30 seconds of its page being read.
- **cost:** Roughly $0.10–$1 per audited account depending on page count; browser observations dominate, while repeated unchanged settings should be cached by content hash.
- **security:** Ship with no assumed security taxonomy: the owner supplies preferences and categories. Never persist secrets, recovery codes, or page bodies. Read-only audit is automatic; any prepared mutation must show its exact target, old value, and new value in the dashboard and remain undoable where the site permits.
- **missing:** owner-authored preference schema for security categories; cross-origin account inventory and duplicate-setting normalization; site-specific security-setting extractors; diff/undo records for prepared browser mutations; a dashboard and pendant queue that presents one finding at a time


## Changes it proposed to its own stack

### `browser-harness` — Add a tab-scoped 'evidence lease' to browser sessions: every browser_read_page or snapshot returns a short-lived lease keyed by tabId, URL, navigation content hash, and extracted claim IDs. Any follow-up answer must present that lease; navigation automatically invalidates it and forces a fresh read. The extension should expose the active tab and lease state to the relay, without transmitting page bodies unless a read action explicitly requests them.
- **owner gets:** When the owner asks a follow-up about a private page, the answer will stay about the page he actually saw instead of silently drifting after a tab refresh or navigation. It makes spoken answers trustworthy and lets him say 'that number' without repeating the URL.
- effort: Medium: browser session schema, navigation invalidation, relay context binding, and a small extension heartbeat field; 1–2 weeks.  ·  risk: A stale or lost lease should fail closed to a fresh read, not answer from old claims. Recovery is automatic on the next read; no page data needs to be retained.
- cost: Negligible storage; reduces model cost by reusing capped claims while preventing expensive wrong-context follow-ups.  ·  latency: Adds tens of milliseconds for lease validation; navigation-triggered refresh costs one browser read.
- security: Improves isolation: claims cannot be reused across origins or tabs, and the lease carries provenance without page text. It is not an origin permission system; keep the owner's explicit origin configuration separate.
- depends on: browser sessions already expose tabId and URL; browser result provenance/content hash remains available; an active-tab resolver or explicit tab binding in the relay


## What it asked for

_Nothing._
## Its own summary

Discovery advanced: Safari is online with two real tabs (authenticated DoorDash order and YouTube subscriptions), and POST /execute successfully performed browser_list_tabs plus a read-only DoorDash page read with provenance/content hash. I recorded three capabilities: (1) owner-configured authenticated-page change monitoring delivered to the pendant (the highest-value browser capability), (2) tab-bound spoken Q&A with grounded follow-ups, and (3) a multi-tab comparison basket that saves only the synthesis and provenance. I also recorded a tab-scoped evidence lease change to prevent follow-ups drifting after navigation, and told mac-planner the concrete gaps.

**Biggest unknown:** The owner has not supplied the first origins or content categories for browser automation. Engineering still needs an explicit origin configuration, a scheduler/semantic diff runner, tab-bound conversation leases, and multi-tab claim collection. I will not invent sites or sensitivity rules; the defaults should remain empty and read-only.

