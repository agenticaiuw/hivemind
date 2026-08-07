# Harness derivation — browser-extension — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live authenticated Safari state** — Safari is online with 3 tabs; Gmail inbox is open and readable at tab 901464, while two example.com tabs show Failed to open page. Gmail currently exposes 14,986 inbox items and visible GitHub Actions failures for buckymatch.
  - evidence: POST /execute browser_list_tabs and browser_read_page at 2026-08-07T17:36Z

## Capabilities it proposed

### "When a GitHub failure or security alert arrives in my private Gmail, investigate it end to end: open the linked authenticated page, inspect the run or alert, check the matching local repository on my Mac, and give me a spoken diagnosis with a ready-to-run repair plan and draft reply—never send or merge anything."
- **useful because:** The browser can see private Gmail/GitHub context while the Mac can inspect the actual checkout; together they turn noisy alert mail into an actionable, evidence-backed incident packet instead of merely summarizing an inbox. The pendant makes the result available while away from the desk.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant
- **model tier:** background for polling/classification and log summarization; realtime only when the owner asks follow-up questions by voice
- **latency:** Detect within 5 minutes; 30–90 seconds for the first incident packet, dominated by authenticated page loads and local test/log inspection
- **cost:** About $0.01–$0.08 per incident using a cheap classifier plus one background synthesis; realtime follow-up is separate
- **security:** Private Gmail/GitHub text and selected local logs leave the Mac only to the relay/model; redact tokens, cookies, and secrets. Read and draft only; do not send mail, merge, deploy, or edit code without an explicit later request.
- **missing:** Gmail/GitHub alert classifier and deduplication keyed by workflow run or alert ID; link-following from an email into authenticated GitHub with bounded extraction; local-repository matching and diagnostic adapter on Mac; incident packet store and pendant audio notification

### "If a private account sends me a suspicious-login or security notice, build a live containment checklist: verify the alert against the logged-in account security page, list active sessions and recent changes, compare them with my Mac and calendar activity, and leave reversible cleanup actions ready for me to review."
- **useful because:** A security email alone is ambiguous. Browser access verifies the source and account state, while the Mac supplies device context and the pendant can interrupt the owner immediately with a concise risk level. This catches compromised accounts without blindly clicking links or revoking the wrong session.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background classifier and evidence extraction; realtime voice only for the urgent alert and owner questions
- **latency:** Alert within 2 minutes; 20–60 seconds to assemble the checklist, mostly browser navigation and security-page loading
- **cost:** Roughly $0.02–$0.10 per alert; model cost is minor compared with authenticated page fetches and optional local correlation
- **security:** Treat email links as untrusted until origin and account identity are verified; never expose passwords, recovery codes, cookies, or full mail bodies. Revoking sessions, changing passwords, or contacting support is prepared but not executed until the owner explicitly asks.
- **missing:** security-notice detector with sender/link validation; cross-surface device-activity comparison; account-security-page extraction recipes for each provider; persistent incident timeline and owner-facing severity interrupt

### "Find a suspicious or duplicate charge from my private email, verify it against the logged-in bank or merchant account, assemble the supporting receipts and correspondence into a dated evidence packet on my Mac, and prefill the dispute form—then tell me the deadline and exactly what would be submitted, but do not submit it."
- **useful because:** This is a high-stakes task where no single surface has the whole truth: Gmail has receipts and merchant mail, Safari has the transaction/dispute workflow, and the Mac can preserve a local evidence packet while the pendant gives a timely deadline alert. It saves hours and reduces the chance of missing a dispute window.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** background extraction and document organization; realtime only to explain the proposed dispute or answer questions
- **latency:** 2–5 minutes for a single charge, dominated by bank/merchant page loads and receipt downloads; immediate spoken alert only for a deadline under 72 hours
- **cost:** About $0.03–$0.15 per packet, mostly document extraction and one synthesis call; storage is small local PDFs/text
- **security:** Bank pages, transaction details, and receipts are extremely sensitive; keep raw evidence on the Mac, send only minimized fields and hashes to the model, and never expose credentials or full account numbers. Prefilling is reversible; submission and any merchant contact must stop for review.
- **missing:** transaction/receipt entity linker across Gmail and authenticated merchant pages; local encrypted evidence-bundle writer with retention and deletion controls; provider-specific dispute-form extraction and field mapping; deadline monitor that can alert through the pendant

### "When I say “clean up my online footprint,” find the accounts and services I actually use from my private inbox and browser sessions, show me what personal data each service retains and the available privacy/deletion controls, prepare the requests and an expiry-tracked follow-up list, and leave every request unsent for my review."
- **useful because:** No current node can inventory a person's authenticated services, understand each provider's privacy UI, and maintain the resulting deletion-request deadlines as one coherent job. This gives the owner control over forgotten accounts and stale personal data without requiring them to remember every service or manually revisit each privacy page.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** Use a cheaper background model for inventory, page extraction, and deadline tracking; reserve realtime for the owner's spoken questions about a specific service.
- **latency:** An initial inventory may take 10–20 minutes because each service needs authenticated navigation; per-service preparation should take under 90 seconds. Deadline alerts should be delivered at the configured cadence.
- **cost:** Approximately $0.10–$0.60 for an initial inventory depending on the number of services and policy pages, then pennies per follow-up; local encrypted metadata is the larger practical cost, not inference.
- **security:** This touches highly sensitive identity and privacy data. Keep raw page captures and account identifiers on the Mac, send minimized policy excerpts for reasoning, verify the origin before following links, never expose cookies/passwords/recovery codes, and never submit a deletion request automatically. The owner must see the exact destination, scope, and text of each request.
- **missing:** A provider-neutral authenticated account inventory and identity-resolution layer; Privacy-policy/control-page extraction recipes with origin verification; A local encrypted registry of prepared requests, proof of submission state, and follow-up deadlines; A browser workbench that renders side-by-side evidence and unsent request text; Pendant reminders for unresolved deletion requests

### "Before I open a link from an email or message, inspect it in an isolated browser tab, follow redirects without signing in, compare the final domains and page identity with the sender's claims, check public reputation signals, and tell me whether it looks legitimate or like a credential trap."
- **useful because:** The owner gets a practical warning at the moment of risk. The browser can inspect the real destination and redirect chain, while the relay can explain the evidence and the pendant can make the warning audible without requiring the owner to paste a suspicious URL into a separate service.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Cheap background classifier for redirects and reputation; realtime only for a spoken verdict or follow-up.
- **latency:** 5–15 seconds for a URL with a short redirect chain; longer pages can be summarized asynchronously.
- **cost:** Usually under $0.02 per check; public reputation lookups and page fetches dominate rather than model tokens.
- **security:** Never send credentials or cookies to the destination during inspection; isolate the tab, block downloads and form submission, redact URL query tokens before external reputation checks, and treat the verdict as advice rather than proof.
- **missing:** An isolated, no-cookie browser inspection mode with redirect-chain capture; A safe URL handoff from Gmail/message context that preserves sender and message evidence; Reputation lookup and domain-identity comparison service; A pendant interrupt for high-confidence credential-phishing warnings

### "Prepare a private digital-estate map: discover my important online accounts and subscriptions from authenticated browser sessions and local records, record what each account is for, renewal or cancellation dates, recovery dependencies, and my chosen instructions, then leave an encrypted, printable handoff packet and tell me what is still missing."
- **useful because:** Today the owner's digital life is scattered across browser sessions, email, local files, and recurring charges. A single encrypted handoff packet would let a trusted person understand what exists and what to do in an emergency without granting this system authority to transfer assets or delete accounts.
- **path:** browser-extension → mac-terminal → mac-planner → dashboard → relay-realtime → pendant
- **model tier:** Background model for inventory, deduplication, and packet drafting; realtime only when the owner reviews or corrects an account entry.
- **latency:** Initial collection 15–30 minutes with incremental saves; updates after that should complete in under 2 minutes per changed account.
- **cost:** About $0.10–$0.50 for initial classification and drafting, with encrypted local storage and optional PDF generation dominating operational cost.
- **security:** This is exceptionally sensitive. Keep the packet encrypted and local, never collect or display passwords/recovery codes by default, separate account metadata from secret material, require a local unlock to export or print, and maintain an audit trail of every read and edit.
- **missing:** Account/subscription entity resolution across private mail, browser tabs, and local files; A local encrypted packet format with trusted-contact and per-field visibility controls; Recovery-dependency graph and renewal/cancellation date extraction; A review UI that flags uncertain or stale entries without exposing secrets; A safe owner-triggered export/print path


## Changes it proposed to its own stack

### `browser-harness` — Add an authenticated evidence-graph worker that turns a Gmail message into a bounded cross-surface case: preserve message/thread ID and link origins, open only same-origin authenticated links, extract selected fields with DOM/source citations, hand a normalized case to Mac diagnostics, and join returned local evidence into one immutable incident or dispute packet. It must support pause/resume, deduplication, and an explicit draft-not-submitted state rather than a generic page summary.
- **owner gets:** The owner gets one answer that connects the email, private web page, and local machine instead of three disconnected snippets—and can hear the conclusion without reopening every tab.
- effort: Medium-high: browser-side case state, extraction recipes, Mac handoff schema, evidence joiner, and dashboard/pendant rendering; prototype with Gmail/GitHub first.  ·  risk: A bad link or extraction could associate the wrong account or incident. Enforce origin/account checks, cite every field, retain raw data locally, and allow case discard/rebuild; no outbound submission is part of the worker.
- cost: Low ongoing API cost (cheap extraction plus one synthesis); local evidence storage grows per case and needs retention controls.  ·  latency: Adds 10–30 seconds for correlation and local handoff, but removes repeated manual page visits.
- security: High sensitivity: minimize model payloads, hash and encrypt local artifacts, redact tokens/account numbers, and never treat email text as instructions.
- depends on: A durable browser case/checkpoint store beyond one-shot /execute; A typed Mac evidence-return endpoint for bounded repo/device diagnostics; Provider-specific Gmail/GitHub extraction recipes; Pendant notification/audio queue for case severity and deadline


## What it asked for

_Nothing._
## Its own summary

Discovered and used the now-live Safari bridge: 3 tabs are online, including authenticated Gmail, and read the current inbox showing multiple buckymatch GitHub Actions failures. Proposed three new owner-facing cross-surface capabilities: end-to-end private GitHub incident diagnosis, suspicious-login containment checklist, and charge-dispute evidence packet; also proposed the missing browser evidence-graph worker that connects Gmail, authenticated pages, Mac diagnostics, and pendant alerts. Told mac-planner about the live finding.

**Biggest unknown:** The orchestrator still has not supplied the owner's preferred authenticated workflows or sensitivity preferences. The implementation now mainly needs the connective case/evidence state, provider-specific extraction recipes, minimized/encrypted local artifact handling, and a typed Mac handoff—not another browser navigation primitive.

