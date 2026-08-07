# Harness derivation — browser-extension — round 124

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What’s the latest on this page?”"
- **useful because:** With Safari on a logged-in page, the system would identify the page's account/order/project/thread, search the owner's private Gmail and other open authenticated tabs for matching references, reconcile dates and status, and speak a sourced answer through the pendant. This is a high-value cross-surface action no Mac-only agent can perform reliably because the browser alone holds the private session and the pendant supplies the hands-free query/output.
- **path:** pendant → browser → mac-bridge → relay-realtime
- **model tier:** Use relay-realtime only to interpret the short voice request and present the answer; use a cheaper background planner for entity extraction, Gmail/page retrieval, deduplication, and citation assembly.
- **latency:** Initial answer within 8–15 seconds; parallel browser reads dominate. If a login or disambiguation is needed, say exactly which tab/account is missing and pause.
- **cost:** About $0.01–$0.04 per invocation depending on private-page text and reconciliation length; browser actions and Mac relay are the dominant non-model work.
- **security:** Only access the currently selected Safari tab and explicitly named related private sources; never expose full email bodies in logs. Return URL/title/snippet citations and redact unrelated recipients, tokens, and financial identifiers. No sending or mutation is involved.
- **missing:** An entity-linking recipe that derives stable identifiers from the active page without uploading whole-page text; A Gmail authenticated search action exposed through the browser harness; A compact citation capsule that the pendant can render as spoken references

### "“Read this page to me, but skip anything private unless I ask for it.”"
- **useful because:** The owner can consume a logged-in page while walking without accidentally hearing account numbers, message bodies, addresses, or one-time codes aloud. The browser extracts structure and sensitivity labels; the relay produces a concise spoken rendering; the pendant's local button can reveal the next redacted item on demand. This makes authenticated browser access safe in public spaces, rather than merely possible.
- **path:** browser → relay-realtime → pendant → mac-bridge
- **model tier:** A slower inexpensive model classifies DOM regions and creates the redacted outline; relay-realtime only handles the live request and short playback control.
- **latency:** Start speaking within 3 seconds for the page outline; reveal a requested field within 2 seconds. Large pages should stream section by section.
- **cost:** Roughly $0.005–$0.02 per page read; DOM extraction and local sensitivity rules dominate, with model cost only for ambiguous regions.
- **security:** Sensitive text should be redacted before it reaches the relay/model whenever deterministic selectors, input types, or patterns identify it. Never persist raw page text or audio. Requiring a physical pendant button press for each redacted-field reveal prevents a nearby voice from causing disclosure.
- **missing:** DOM-level sensitivity metadata and deterministic redaction before model/relay transfer; A pendant-local reveal-next/redact toggle that works while attached by USB and later offline; Streaming section audio with per-section sensitivity state and an audit receipt

### "“What has changed across my private web accounts since last month, and what pattern should I care about?”"
- **useful because:** Today the browser can read a page or emit isolated watch reports, but the owner cannot ask a longitudinal question spanning many authenticated sites and receive a trustworthy, evidence-linked answer. This capability would build a time-indexed semantic history of the owner's selected private pages—prices, statuses, deadlines, policy text, and account events—then explain trends, recurring failures, and unusual changes without making the owner revisit every site.
- **path:** browser → mac-bridge → relay-realtime → pendant
- **model tier:** Use a cheaper background model to normalize watch snapshots, cluster equivalent entities, and calculate trends; invoke relay-realtime only when the owner asks for the spoken explanation or follow-up.
- **latency:** Precompute incrementally after each watch run; answer a one-month query in under 5 seconds from the local history. If evidence is incomplete, identify the exact missing interval rather than hallucinating continuity.
- **cost:** Approximately $0.01–$0.05 per month of monitored history during background normalization, plus under $0.01 for a spoken query. Storage and extraction dominate; raw page text should not be repeatedly sent to a model.
- **security:** Keep raw authenticated snapshots encrypted on the Mac and store only normalized fields, sensitivity labels, hashes, and source pointers in the relay. Each spoken claim must carry a source URL/date and confidence. The owner must explicitly select which watches participate; do not silently correlate unrelated accounts or infer sensitive health/financial traits.
- **missing:** A durable time-series store for semantic browser observations with retention and deletion controls; Cross-watch entity resolution and trend/anomaly analysis that preserves source-level citations; A query route that turns a natural-language historical question into bounded private-watch retrieval, with spoken and Mac-readable evidence views

### "“Make me a private archive of my data from these logged-in sites, organized so I can actually use it.”"
- **useful because:** The owner cannot currently turn several authenticated web accounts into one local, searchable, encrypted archive without manually navigating exports, downloading files, and reconciling formats. The browser could operate each site's existing export/download flow, the Mac could normalize and index the resulting data, and the pendant could report progress or warn when a site requires a human step. This is useful for migration, backup, privacy review, and leaving a service.
- **path:** browser → mac-bridge → mac-terminal → relay-realtime → pendant
- **model tier:** Use a background model for schema mapping, deduplication, and archive organization; use realtime only for progress questions and spoken exception handling.
- **latency:** Minutes to hours depending on site export jobs; the owner should be able to leave and later ask the pendant for progress. Never claim completion until checksums and per-site manifests verify it.
- **cost:** About $0.05–$0.50 per archive depending on file volume and schema reconciliation; local disk and hashing dominate, with model calls only for ambiguous field mapping.
- **security:** Archive remains encrypted on the owner's Mac; no raw export is sent to the relay or model. Downloads must be isolated per site, malware-scanned, checksum-recorded, and auto-expired from staging. The system must stop before any destructive account-closure step and report exactly which exports were obtained.
- **missing:** A browser download/export workflow that can detect site-specific asynchronous export jobs and resume them; An encrypted local archive writer with per-source manifests, checksums, retention, and deletion verification; A schema-mapping/indexing pipeline that supports heterogeneous private exports without uploading their contents

### "“Are any of my logged-in accounts showing signs of compromise, and what should I do first?”"
- **useful because:** Today isolated browser reads cannot correlate a new-login alert in one account, a password-reset email in another, and unfamiliar sessions or forwarding rules across several private services. This capability would inspect only owner-selected security pages and matching inbox evidence, correlate events by time/device/IP, rank the likely incident, and give a short containment plan—spoken through the pendant and cited on the Mac—without changing settings automatically.
- **path:** browser → mac-bridge → relay-realtime → pendant
- **model tier:** Use a background model for event normalization and correlation; use realtime for the owner's immediate question and concise incident narration. Deterministic rules should handle known security-alert patterns.
- **latency:** Initial triage in 10–20 seconds for already-open tabs; deeper account-by-account inspection can continue as a background job with progress updates.
- **cost:** Approximately $0.02–$0.10 per triage across several accounts, dominated by authenticated page retrieval and classification; retain only normalized security events, not whole messages.
- **security:** This capability itself handles extremely sensitive data. Restrict it to explicitly enrolled accounts and security-related folders/pages, redact tokens and full IP/device identifiers in speech, encrypt local evidence, and require a physical pendant acknowledgement before opening a reset or recovery page. It may draft a containment checklist but must not change passwords, revoke sessions, or contact support without a separate owner request.
- **missing:** A security-scope browser extractor for login history, recovery settings, forwarding rules, and alert messages across heterogeneous sites; Cross-account event correlation with device/time normalization and false-positive explanations; A local encrypted incident record plus pendant escalation/acknowledgement flow


## Changes it proposed to its own stack

### `integration` — Add an authenticated-browser-to-pendant escalation path for genuinely high-salience watch changes. A page-watch report would carry a semantic urgency score and evidence capsule; the relay would queue a short spoken alert, while the pendant gives one distinctive vibration. A physical button acknowledges it, suppresses duplicate reports, and can request the cited page excerpt. Quiet hours, per-watch escalation, and a daily cap prevent notification storms; ordinary changes remain in the Mac review queue.
- **owner gets:** A critical delivery delay, appointment cancellation, or account security change reaches the owner even when Safari is in the background and the Mac screen is closed. They do not have to remember to open a dashboard, yet low-value page churn stays silent.
- effort: Medium-high: urgency policy, relay queue integration, pendant acknowledgement event, and watch-report-to-evidence linking.  ·  risk: False urgency or repeated alerts could erode trust. Recover by defaulting to digest-only, honoring a per-watch disable command, deduplicating by normalized evidence hash, and exposing an alert history. No browser mutation occurs.
- cost: Negligible model cost for deterministic rules; approximately $0.001–$0.01 for ambiguous urgency classification. One short audio alert uses trivial bandwidth/storage.  ·  latency: Under 5 seconds from completed watch inspection to pendant alert when relay is online; queue for later playback if offline.
- security: Alert speech must use the same redaction policy as page reads and avoid raw account identifiers. Store only report IDs, urgency, and hashed evidence; require the physical button for expanded excerpts.
- depends on: A working browser watch report with stable evidence capsules (existing /watches and /browser/inspections, but currently no urgency-to-device bridge); A pendant event/acknowledgement route and local vibration/audio control; Relay audio queue with quiet-hours and deduplication semantics


## What it asked for

_Nothing._
## Its own summary

Safari is now genuinely usable: the extension is online with three tabs, including the owner's logged-in Gmail inbox (tab 901464), and POST /execute browser_list_tabs returned typed receipts. I recorded three non-duplicate directions: active-page-to-private-context answering (“What’s the latest on this page?”), redacted spoken reading of authenticated pages, and urgent authenticated-watch escalation to pendant vibration/audio with physical acknowledgement. I also told mac-planner that the Gmail tab is live. What remains is not browser reachability: it is the missing bridge between browser evidence and safe cross-surface behavior.

**Biggest unknown:** No owner-specific authenticated workflow or sensitivity policy has been supplied, so I still need a concrete target account/page and rules for what may be spoken aloud, what stays on the Mac, and which watch changes merit a pendant interrupt. Technically still missing are DOM redaction before model transfer, active-page entity-to-Gmail search, and a pendant acknowledgement/event route.

