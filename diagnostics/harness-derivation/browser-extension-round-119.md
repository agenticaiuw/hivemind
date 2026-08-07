# Harness derivation — browser-extension — round 119

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-session-routing** — The Safari extension is online with Gmail tab 901464. browser_list_tabs without a tab target reported a stale default session tab (320512, time.is), and browser_snapshot then failed as protected-page. Supplying params.tabId=901464 made both browser_read_page and browser_snapshot succeed. browser_navigate to example.com successfully bootstrapped tab 901786 and updated the default session.
  - evidence: GET /browser/status; POST /execute browser_list_tabs, browser_snapshot, browser_read_page with tabId 901464, and browser_navigate https://example.com at 2026-08-07T15:05Z

## Capabilities it proposed

### "When I say “triage this alert,” inspect the alert in my logged-in Safari tab, follow its private links, check the corresponding local project or logs on my Mac, and give me a sourced spoken diagnosis plus a prepared (never sent) reply or next-step checklist."
- **useful because:** Today the browser can see private inbox/issue details while the Mac can inspect local repositories and logs, but neither alone can connect the two. This turns a vague alert into an actionable diagnosis without sending anything or losing the evidence trail.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → unified
- **model tier:** Use the realtime tier only to capture the short spoken intent and deliver the result; use the cheaper background planner for browser extraction, local log correlation, deduplication, and draft generation.
- **latency:** Acknowledge immediately; return an initial diagnosis in 15–30 seconds, with longer local-log searches continuing as a background job and a spoken completion notice.
- **cost:** Usually 1–2 background model calls plus one short realtime turn; browser and local-shell calls dominate latency, not tokens. Roughly $0.02–$0.10 per triage depending on log volume.
- **security:** Private page text and selected local logs leave their respective devices only to the relay/model; redact secrets and limit correlation to the linked repository/paths. Never submit, send, merge, or change files without a separate owner instruction; show the exact prepared text and cited source snippets.
- **missing:** A cross-surface correlation job that carries a browser URL/message identifier and a Mac repository/log query as typed inputs; A durable evidence bundle joining browser tabId/URL snippets with shell command output and draft provenance; A completion push from background jobs to the pendant/relay

### "When I say “save this for my walk,” preserve the exact private Safari page or selected passage I’m viewing, its linked evidence, and my spoken note in a private handoff capsule; then let me ask the pendant about that capsule later even when the Mac is closed or Safari has navigated away."
- **useful because:** The owner currently loses the useful context of a logged-in page as soon as the tab changes or the Mac sleeps. This would make the browser a secure source of private context and the pendant a genuinely useful continuation surface, without requiring the owner to keep a tab open or repeat the task.
- **path:** browser-extension → relay-realtime → mac-planner → unified
- **model tier:** Use the realtime tier only for the short save/query conversation. A cheaper background worker should extract the selected passage, fetch only explicitly linked evidence while the session is available, generate a compact searchable index, and expire it automatically.
- **latency:** Acknowledge the save immediately and finish capture in under 5 seconds; pendant questions should begin speaking within 1 second from the cached capsule, with deeper linked evidence arriving asynchronously.
- **cost:** About $0.01–$0.05 per save/query pair; storage and browser extraction dominate operational cost, while the model is used only for compression and follow-up answers.
- **security:** This contains authenticated private page text and possibly tokens or personal data. Encrypt capsules at rest and in transit, bind them to the owner/device, exclude passwords and form fields by DOM policy, show the source URL and capture time before answering, and enforce a short TTL plus one-tap deletion. No follow-up navigation, submission, or message sending should occur from a capsule without a new explicit request.
- **missing:** A browser command that captures the user-selected DOM range plus surrounding semantic context and cited links, rather than only whole-page text; An end-to-end encrypted, TTL-bound capsule store that the relay can query without exposing raw page content to unrelated jobs; Pendant-side capsule identifiers and offline cache/query protocol, with sync conflict handling when the Mac reconnects; A provenance-preserving answer contract that cites the captured URL, range, timestamp, and whether evidence was live or cached


## Changes it proposed to its own stack

### `browser-harness` — Add an active-tab reconciliation layer before every browser action: compare the durable default session target against the extension's latest /browser/status and browser_list_tabs result; discard stale/protected/local-file targets, select an explicit live http(s) tabId, and inject that tabId into read/snapshot/click/type actions. For browser_navigate, retry once only after refreshing tab inventory, and record whether it bootstrapped a new tab or targeted an existing one. Expose failure classes (stale_session, protected_page, no_tab, extension_timeout, site_denied) instead of one generic browser_navigate failure.
- **owner gets:** Safari actions stop failing mysteriously after the bridge or a previous navigation leaves the default session pointing at the wrong tab. The owner gets a truthful result and their logged-in page is preserved rather than an automation loop poking the extension page or retrying blindly.
- effort: Medium: browser bridge/session resolver, typed error mapping, tests for stale tab, protected page, no-tab bootstrap, and timeout.  ·  risk: A wrong tab could be selected if inventory races with a navigation; mitigate with URL/origin revalidation immediately before mutation and retain explicit tabId in receipts. Recovery is a fresh list_tabs plus one controlled retry; never repeat irreversible actions automatically.
- cost: Negligible API cost; one lightweight extension/status or list-tabs round before actions, plus occasional retry latency.  ·  latency: ~0.4–1.0s for reconciliation on reads; navigation failures gain one bounded retry, while successful navigations remain unchanged.
- security: Improves security by preventing commands from landing on protected extension pages or an unintended stale tab; URL/origin and tabId become mandatory receipt fields.
- depends on: chg-14accc01 request IDs and tab/session affinity; live browser_list_tabs action and /browser/status heartbeat; typed action receipts from chg-5fc73ce3


## What it asked for

_Nothing._
## Its own summary

Discovered and verified the browser path is usable: Safari is online, Gmail tab 901464 is readable when an explicit tabId is supplied, while the default session can be stale and point at a protected time.is tab. Navigation bootstraps a new tab successfully. Reported the root cause to mac-terminal, recorded the finding, and proposed an active-tab reconciliation/error-classification fix plus a cross-surface private-alert triage capability.

**Biggest unknown:** The durable browser job runner and a production implementation of the granted enqueue wrappers still need to be shipped; I cannot verify their code path from this harness.

