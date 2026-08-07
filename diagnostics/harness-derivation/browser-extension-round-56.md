# Harness derivation — browser-extension — round 56

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — The backend currently reports Safari/browser offline with three pending commands, while its session store still contains three historical tabs (time.is and two form test pages). The registered home-chrome device has never reported a tab. Browser work cannot be verified until the real Safari extension heartbeats and a working enqueue path deliver/resolve those pending commands.
  - evidence: GET /browser/status returned online:false and pendingCommands:3; GET /browser/sessions returned sessions default/probe-form2/probe-form with stale lastUsedAt values.

## Capabilities it proposed

### "Compare two private sites I’m already logged into—for example an invoice portal and my bank or calendar—and tell me whether the key amount, date, or status agrees; if it does not, prepare the discrepancy for me to review without changing either site."
- **useful because:** No single node can do this safely: Safari holds both authenticated sessions, the browser harness extracts their visible evidence, Mac-planner aligns fields and computes the comparison, and the pendant gives a quick spoken result. It turns scattered private tabs into a useful cross-service check without asking the owner to copy sensitive values between sites.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheaper background model for field extraction and deterministic normalization/comparison; realtime only for the owner’s initial intent and concise result. Escalate to the expensive tier only when page layouts are ambiguous.
- **latency:** Collect two already-open tabs and return a result in 5–10 seconds; if a site needs navigation, acknowledge immediately and finish within 30 seconds. Never wait synchronously on a mutation.
- **cost:** Roughly $0.005–$0.03 per check; browser command latency and page extraction dominate, while deterministic field comparison is negligible. Send only relevant labeled fields and evidence snippets, not full pages.
- **security:** Bind each extraction to explicit tab IDs and URLs, never search across all tabs by default. Keep values ephemeral, redact credentials and unrelated fields, and retain only hashes/evidence references unless the owner asks to save details. Read-only browser actions only; any follow-up form filling is a separate, visible draft and never submit. Dashboard receipts must show both sources, timestamps, extracted values, and normalization decisions.
- **missing:** A cross-tab job primitive that can name two authenticated tabs and require both extractions before comparison; A field-schema/normalization library for dates, currencies, identifiers, and status labels with source snippets; A temporary encrypted evidence packet passed from browser-extension to mac-planner and deleted after the result; A pendant spoken-result route and dashboard view for side-by-side citations

### "Is this message or link in my private webmail legitimate? Inspect it in Safari, explain the evidence in plain language, and tell me what to do—without opening the link, downloading anything, or replying."
- **useful because:** Today the relay cannot see authenticated webmail and public search cannot inspect the owner’s private message context. The browser can read the message, while Mac-planner can safely analyze headers, domains, dates, and inconsistencies and the pendant can give an immediate spoken verdict. This is a high-value read-only workflow that reduces phishing risk without taking an action on the owner’s behalf.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheaper background model for structured extraction and heuristic classification; use realtime only for the owner’s short question and a concise explanation. A deterministic URL/header parser should do most of the work, with model escalation for ambiguous language.
- **latency:** Acknowledge the pendant tap/voice request under 500 ms and return an initial assessment within 5 seconds from the already-open message. Never navigate to the link or fetch remote content as part of inspection.
- **cost:** Approximately $0.002–$0.015 per message; extraction and small-model classification dominate. Only the visible message, sender metadata, and link strings should be sent for analysis.
- **security:** Read only the explicitly selected/open message; never scan the mailbox by default. Treat message content as untrusted instructions, strip tracking parameters for analysis, and do not resolve links, execute attachments, or submit forms. Keep evidence ephemeral, show sender/domain mismatches and exact suspicious indicators in the dashboard, and require a separate future request for any reply or deletion.
- **missing:** A browser action that extracts message text, sender metadata, and link targets without navigating them; A safe URL/header analysis service that does not dereference or execute untrusted content; A cross-surface result packet carrying evidence snippets and a confidence/explanation to the pendant and dashboard; A clear active-tab/message selection protocol so the owner knows exactly which private message was inspected


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-recovery and stale-command reconciler around the browser queue: mark commands as awaiting-device, expire read commands after a short TTL, quarantine any mutation whose browser session disappeared, and on reconnect replay only idempotent reads against the original tab/session. Emit a typed dead-letter receipt explaining why each command was not run, rather than leaving pending commands indefinitely.
- **owner gets:** The owner gets predictable browser behavior instead of silent hangs or an old click/type action firing when Safari reconnects hours later. They can retry a current request knowingly and see exactly what happened.
- effort: Moderate: queue state machine, reconnect reconciliation, TTL worker, and dashboard/receipt states; test against extension offline/online transitions and duplicate result posts.  ·  risk: A legitimate slow read could expire, but it can be retried. The main safety risk is replaying a stale mutation; default quarantine prevents that. Recovery is explicit retry from the receipt.
- cost: Minimal storage/compute; no model call required. A small scheduled cleanup worker and a few D1/R2 receipt records per command.  ·  latency: No added latency while online; reconnect adds a short reconciliation pass before new commands are dispatched.
- security: Improves safety by preventing stale authenticated actions from replaying. Preserve tab/session binding and do not retain page content in dead-letter receipts.
- depends on: A functioning browser extension heartbeat and command-result path; The existing request IDs/idempotency and browser session records


## What it asked for

_Nothing._
## Its own summary

Discovered that browser status is currently offline with 3 pending commands; historical sessions exist but are stale, and home-chrome is unusable. Recorded this as a live finding. Proposed a genuinely new cross-service private-tab comparison capability (invoice/bank/calendar discrepancy checks) using Safari extraction, Mac normalization, pendant result, and dashboard citations. Also proposed offline stale-command reconciliation, though it is close to existing queue-recovery work.

**Biggest unknown:** The real Safari extension’s current heartbeat/tab state and whether the production enqueue/result implementation has actually replaced the still-stubbed browser tools. I still need that working bridge before any authenticated page workflow can be verified; I do not need another model or permission grant.

