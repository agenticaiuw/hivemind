# Harness derivation — browser-extension — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 9 tabs; active tab is authenticated x.com/home (tabId 1163292), default browser session is bound to it, and browser_read_page through POST /execute succeeds with provenance/evidence receipts.
  - evidence: GET /browser/status and POST /execute browser_read_page at 2026-08-08T03:12:02Z

## Capabilities it proposed

### "“What changed in my logged-in web accounts that I actually need to know about?”"
- **useful because:** This is the highest-value browser capability: the browser is the only node that can see authenticated pages, while the relay can stay awake and the pendant can deliver a short alert. On demand, it reads owner-configured origins, compares against the last local digest, joins changes with Mac Calendar/Mail context, and speaks only actionable deltas; it avoids pretending that public web search can see private accounts.
- **path:** pendant → relay-realtime → browser → mac-planner → dashboard
- **model tier:** background for page extraction and diffing; realtime only to turn the final prioritized result into a conversational answer
- **latency:** 10–20 seconds for 3–5 origins; under 2 seconds to speak an already-computed digest
- **cost:** ~$0.03–$0.15 per on-demand run, dominated by authenticated page extraction and summarization; unchanged pages should short-circuit before model use
- **security:** The owner must explicitly configure origins and per-origin extraction/redaction rules; default is empty. Keep raw page text in memory only, persist hashes and redacted evidence capsules, and never send passwords or form values to the relay. Ask before any browser mutation.
- **missing:** owner-supplied origin rules and categories; a durable per-origin digest store with retention controls; relay push from browser diff results into offline_alert_inbox

### "“Before I commit to this web form, check whether its dates, amount, and obligations conflict with my calendar and existing commitments, then tell me what I would be agreeing to—do not submit it.”"
- **useful because:** Authenticated forms often contain the consequential details that are invisible to calendar and mail APIs. The browser extracts the current draft, Mac reads existing commitments, and the relay produces a plain-language conflict report while preserving the form untouched. This turns the hive into a second pair of eyes at the exact moment the owner needs it.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background model for structured extraction and comparison; realtime only for the owner's follow-up questions
- **latency:** 15–30 seconds for a complex form; incremental follow-up under 3 seconds while the draft remains open
- **cost:** ~$0.05–$0.25 per review, dominated by form/page extraction and one synthesis pass
- **security:** Draft values are sensitive and must be processed ephemerally; per-origin rules decide which fields may be read, spoken, or persisted. Never click submit. Show the exact extracted commitments and confidence, with a visible browser receipt and a pendant summary.
- **missing:** form-schema extraction that labels dates, amounts, cancellation/renewal terms; a read-only calendar/mail comparison endpoint exposed to the browser workflow; a durable 'draft under review' session binding browser tab to pendant conversation

### "“Remember the paragraph I’m looking at in Safari and remind me next Tuesday why I saved it.”"
- **useful because:** A logged-in page can contain private research, tickets, or documents that public readers cannot access. The browser captures only the owner's selected/visible passage and URL, the relay links it to the pendant utterance, and Mac creates a reminder with a minimal, redacted citation. The owner gets durable recall without dumping an entire authenticated page into memory.
- **path:** browser → pendant → relay-realtime → mac-planner → dashboard
- **model tier:** realtime for resolving the short spoken request and identifying the selection; background for optional title/topic cleanup
- **latency:** 2–5 seconds to capture and confirm; reminder creation immediately after confirmation of the proposed text
- **cost:** ~$0.01–$0.05 per capture, mostly transcription and lightweight normalization
- **security:** Capture only explicit selection or viewport text, never hidden fields; redact secrets and configurable categories; persist URL, timestamp, and a short owner-approved excerpt rather than page HTML. Show the reminder payload before creation and provide undo.
- **missing:** extension support for selection/viewport capture as a first-class browser result; a private citation record linking URL, content hash, and reminder without storing raw page text; pendant conversation context that can refer back to the active Safari tab

### "“Check my logged-in accounts for inconsistent profile details—name, address, phone, and security contact—and tell me exactly which account is out of date. Don’t change anything.”"
- **useful because:** Profile drift across banks, utilities, insurers, travel sites, and work services causes failed verification, missed notices, and account recovery problems. Only the browser can inspect those authenticated settings pages; the Mac can provide the owner's canonical contact record; the relay can reconcile conflicts and the pendant can deliver a concise, private report. This is a read-only audit, not another form-filling workflow.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background model for schema normalization and conflict detection; realtime only for the owner's follow-up questions
- **latency:** 30–90 seconds for a configured set of origins; incremental account review under 10 seconds
- **cost:** ~$0.05–$0.30 per audit, dominated by authenticated page extraction; unchanged account schemas should be cached by content hash
- **security:** Profile and recovery details are highly sensitive. Require explicit per-origin field allowlists, keep raw values local and ephemeral, compare using keyed hashes where possible, speak only the conflicting field and site name, and never write settings. The dashboard must show exactly which origins were inspected and provide deletion of audit metadata.
- **missing:** a structured authenticated-settings extractor that understands labels and values without collecting hidden fields; local-only canonical contact data access from the Mac; pairwise comparison and redaction rules for identity/recovery fields; an owner-configured origin set

### "“Audit the third-party apps and devices that still have access to my logged-in accounts, tell me what is stale or unfamiliar, and prepare a revoke list without revoking anything.”"
- **useful because:** The browser can see authenticated security and connected-app pages that no local API can reach. A cross-account access inventory would expose forgotten OAuth grants, old sessions, and unknown devices before they become an incident. The owner gets a prioritized pendant summary and an explicit, reversible-looking but high-impact action list rather than silent revocations.
- **path:** browser → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** background model for normalizing provider-specific security pages and ranking stale access; realtime for answering questions about one entry
- **latency:** 45–120 seconds across several configured providers; a single-provider refresh under 15 seconds
- **cost:** ~$0.10–$0.40 per audit, mostly page extraction and normalization
- **security:** Security pages contain sensitive identifiers and session metadata. Store provider, app name, scope summary, last-seen age, and a redacted fingerprint—not tokens or full page text. Require an explicit configured origin list. Never revoke automatically; show the exact target and scope before any future action.
- **missing:** provider-agnostic connected-access schema; local redacted fingerprinting for app/device identity; stale-access ranking based on owner policy and last-seen data; a future revoke action that can be staged and individually undone where the provider supports it

### "“Show me what personal data each of my logged-in services has about me, where it is shared, and prepare a private deletion/export plan without sending any requests.”"
- **useful because:** A browser session is the only way to reach provider-specific privacy dashboards and account data controls behind existing logins. The hive could normalize those disparate disclosures into one local map, identify duplicate or unnecessary data, and prepare a sequenced plan while the pendant gives a short explanation. This gives the owner control over private data rather than merely automating ordinary browsing.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background model for extracting and normalizing privacy disclosures; realtime for explaining one provider or one category
- **latency:** 2–5 minutes for a first multi-origin inventory; subsequent refreshes 20–60 seconds using page fingerprints
- **cost:** ~$0.20–$1.00 per initial inventory, dominated by many provider pages and long disclosures; refreshes substantially cheaper
- **security:** Privacy dashboards may reveal sensitive data categories and recipients. Raw disclosures stay on the Mac in an encrypted, owner-deletable store; relay receives only category counts and redacted summaries. Never submit export/deletion requests automatically. Require explicit origin and retention policy configuration.
- **missing:** provider-specific privacy-dashboard extraction adapters; an encrypted local data inventory with field-level deletion; cross-provider category and recipient normalization; a staged request builder with evidence and expiry


## Changes it proposed to its own stack

### `browser-harness` — Add an owner-visible “active private page” handoff: the extension reports the focused tab, selection/viewport bounds, origin, and a short-lived opaque page token; the relay binds that token to the current pendant conversation. On Mac-agent restart, recover the existing tab by session ID without reopening or copying page contents, and expire the token when the tab changes or Safari closes.
- **owner gets:** The owner can say “this page” or press the pendant button while looking at a private page and be understood reliably, instead of repeating a URL or losing the context when the agent restarts. It makes browser access feel like part of the wearable rather than a separate automation console.
- effort: Medium: extension heartbeat/result schema, session binding, restart recovery, dashboard indicator, and tests for tab changes and expiry.  ·  risk: A stale token could attach the wrong page to a voice request; bind to tabId+URL+content hash and return an explicit mismatch rather than guessing. Recovery must never navigate or submit.
- cost: Negligible API cost; a few hundred bytes per heartbeat and a small local session record.  ·  latency: No noticeable foreground delay; active-tab handoff under 300 ms, recovery under 2 s.
- security: Improves security by using opaque, expiring references and keeping content local until an explicit read. Origin policy and redaction still apply.
- depends on: extension selection/active-tab metadata; browser session token storage; relay conversation context binding


## What it asked for

_Nothing._
