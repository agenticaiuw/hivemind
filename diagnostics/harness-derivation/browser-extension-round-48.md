# Harness derivation — browser-extension — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Compare the options in my logged-in accounts and the public alternatives, tell me which is best for my situation, and prepare the next steps without committing anything.”"
- **useful because:** Only the browser extension can read the owner's authenticated prices, eligibility, account status, and saved details; the relay can add public alternatives while the Mac can normalize a comparison and produce a practical recommendation. This turns scattered private tabs into a sourced decision, while stopping short of purchase, submission, or sending.
- **path:** pendant → browser → relay → mac-planner → dashboard-ux
- **model tier:** Background/cheap model for extraction, normalization, and first-pass comparison; expensive realtime tier only for the owner's follow-up conversation or ambiguity resolution.
- **latency:** Start immediately with a spoken acknowledgment under 2 seconds; return a concise comparison in 1–3 minutes, with longer authenticated pages processed asynchronously and a completion receipt on the pendant.
- **cost:** Roughly $0.03–$0.15 per invocation, dominated by page extraction and one synthesis pass; public pages should use the cheaper relay browser lane and authenticated pages should not consume relay browser minutes.
- **security:** Private page text, account identifiers, and possibly pricing/eligibility data leave Safari only to the owner's relay/Mac path; redact secrets and payment data before synthesis, retain cited snippets briefly, and make the final recommendation auditable. Never auto-purchase, submit, send, or change account settings; show the exact proposed action and destination for owner approval.
- **missing:** A durable multi-tab comparison job that can capture several authenticated Safari tabs plus public pages, preserve tab/session affinity, and resume after Mac sleep or an extension reconnect; A normalized evidence schema for offers, constraints, dates, eligibility, exclusions, and total cost with source URL, timestamp, and snippet citations; A drift detector that marks an option stale when its page changes between extraction and any later review; A dashboard artifact and pendant completion receipt that present side-by-side results and a prepared-but-uncommitted next action

### "“Keep working on this private web task even if it needs me to log in or complete 2FA; tell me exactly when I need to take over, then resume where you left off.”"
- **useful because:** Today an authenticated browser task effectively dies at an expired session, login wall, or passkey/2FA prompt. This would let the owner hand off the tedious parts while retaining control of credentials and strong authentication: the agent prepares everything, wakes the owner only for the secret step, then continues without losing the task state.
- **path:** pendant → browser → relay → mac-planner → dashboard-ux
- **model tier:** Cheap background model for state tracking and form/page reconciliation; realtime tier only for the brief spoken handoff and any ambiguity about what the owner sees.
- **latency:** Detect an auth interruption within 2 seconds, notify the pendant promptly, and resume within 5 seconds after the extension reports the authenticated page; long waits for the owner must not hold an HTTP request open.
- **cost:** About $0.02–$0.10 per task, mostly page reconciliation after the session resumes; no need to spend public-browser minutes because this is an owner-private Safari workflow.
- **security:** The agent must never request, record, OCR, or transmit passwords, passkeys, recovery codes, or one-time codes. Safari remains the credential boundary. Persist only an opaque task state and redacted field metadata; bind resumption to the same browser profile/tab and invalidate the state if the origin, account, or task intent changes. External submission remains a distinct owner-triggered operation.
- **missing:** An extension/local-agent auth-interruption detector that classifies login, 2FA, passkey, CAPTCHA, consent, and ordinary page errors without reading secret fields; A durable, encrypted task checkpoint containing the intended origin, tab identity, completed step IDs, and redacted before/after metadata, surviving Mac sleep, extension reconnect, and relay restart; A pendant-to-Safari handoff signal with a clear local prompt and completion acknowledgement, plus a resumable browser result stream instead of a single blocking wait; A reconciliation pass that verifies the resumed account and page state before continuing, and reports exactly what was skipped or changed


## Changes it proposed to its own stack

### `browser-harness` — Add a browser 'context capsule' protocol: Safari keeps a short-lived, per-tab capsule containing the active URL/title, selection or focused field, viewport text around it, and a DOM accessibility path. A pendant utterance such as “what does this mean?” or “handle this” references the capsule by tab/session nonce; the relay forwards only the requested region to the Mac planner, which can ask the extension for a fresh read if the page drifted. Capsules expire, are encrypted at rest, and never include passwords or full-page content by default.
- **owner gets:** The owner can point at something in a private webpage and ask about it naturally without copying links, describing which tab, or exposing the entire account page. It makes the pendant genuinely useful for authenticated web pages while minimizing unnecessary private data transfer.
- effort: Medium: Safari content-script/extension changes, a nonce-bound capsule endpoint in the local agent, planner prompt wiring, and a small UI indicator for the active referenced tab.  ·  risk: Dynamic pages may produce a stale or ambiguous anchor; return an explicit stale/ambiguous result and ask the owner to identify the tab rather than silently acting elsewhere. Recover by refreshing the capsule. Avoid storing page text beyond the short TTL.
- cost: Negligible API increase for focused-region extraction; typically one small model call instead of a full-page read. Local storage and bandwidth are minimal.  ·  latency: A cached capsule answers in under a second for local metadata; fresh extraction adds roughly 1–3 seconds, with no 45-second blocking wait if the command queue is asynchronous.
- security: Improves privacy by defaulting to selected/focused content and binding every request to a tab nonce; still requires strict redaction of password inputs, cookies, tokens, and hidden DOM fields.
- depends on: A resumable browser command/result stream rather than the current single 45-second blocking wait; Typed tab/session affinity and idempotent browser actions (already partially present); Voice/planner support for resolving a capsule nonce and reporting stale anchors


## What it asked for

_Nothing._
## Its own summary

This round produced two new browser-first capabilities beyond the existing watch/draft backlog: (1) cross-account/private-vs-public option comparison with sourced normalization and an uncommitted next-step artifact, and (2) a nonce-bound Safari page context capsule so a pendant utterance can refer naturally to the focused/selected content without copying or exposing an entire logged-in page. I notified mac-planner.

**Biggest unknown:** The durable implementation is still missing: browser jobs do not yet persist/resume across restart or Mac sleep, and the command path still relies on a single blocking wait rather than progress/resumable polling. The capsule additionally needs Safari extension support and a normalized evidence schema.

