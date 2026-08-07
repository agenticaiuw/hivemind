# Harness derivation — browser-extension — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every weekday morning, check my logged-in work dashboard, calendar, and inbox, then give me a short audio briefing with only what needs my attention."
- **useful because:** It turns scattered authenticated web information into a hands-free prioritized briefing without making the owner open multiple sites. It uses the browser tier for information unavailable to public search.
- **path:** dashboard routine setup → relay scheduler/job store → Mac Safari browser bridge (navigate/read/extract) → cheap summarizer → R2 audio generation → pendant playback notification
- **model tier:** Browser extraction and rule-based field selection first; a small background model summarizes and prioritizes. Realtime is used only if the owner asks a follow-up by voice.
- **latency:** Run before the requested delivery time; 1–3 minutes is acceptable. Audio should be ready at the scheduled time, not block a live conversation.
- **cost:** Low per run: browser actions dominate wall time, while extraction plus a small summary should be a few thousand tokens; avoid sending full page HTML or old history to the model. Audio costs one short synthesis per briefing.
- **security:** Authenticated page contents leave Safari for the local agent/relay and may include sensitive mail or meetings. Store only extracted actionable fields, encrypt job/audio data, and let the owner choose domains and retention. Never send, delete, accept invites, or alter calendar entries automatically; those require explicit confirmation.
- **missing:** A durable scheduled-job runner with per-site extraction recipes; A browser result sanitizer that keeps only requested fields; A small-model summarization/audio pipeline and pendant notification/playback

### "Open this website, fill out the form with the information we discussed, and show me exactly what is ready before you submit it."
- **useful because:** The browser can perform tedious navigation and drafting while preserving the owner's control over irreversible submissions. This is especially useful for support tickets, expense claims, travel forms, and appointment requests behind logins.
- **path:** pendant voice request → relay planner → Mac Safari browser bridge (navigate/click/type/select/read) → dashboard diff/preview → pendant or iOS confirmation
- **model tier:** Use the planner model to map the request to fields, then deterministic browser actions and a cheap verifier to detect missing/changed values. Realtime only handles conversational clarification.
- **latency:** Draft in under 30–60 seconds for a normal form; pause immediately when a submit/send/purchase action is reached.
- **cost:** Moderate one-time browser interaction cost; minimize tokens by extracting labels/values and a screenshot only near the final review rather than repeatedly transmitting whole pages.
- **security:** A malicious page could alter labels or exfiltrate typed secrets; restrict navigation to the requested origin, redact passwords/one-time codes, and show destination, all field values, attachments, and total cost. Require explicit, fresh confirmation immediately before submit/send/purchase, with an expiry if the page changes.
- **missing:** Origin allowlist and action-risk gate in browser bridge; Structured form-field extraction plus final-page change detection; A review UI that lets the owner approve or edit the exact pending action

### "Watch this logged-in page and tell me when the status changes, but don't click anything or send anything."
- **useful because:** It can monitor order status, application queues, ticket updates, or operational dashboards that are not exposed through public APIs, saving repeated manual checks.
- **path:** dashboard watch setup → relay scheduler → Mac Safari browser bridge with browser_wait_for/read → deduplicated event store → pendant audio alert and dashboard history
- **model tier:** Prefer DOM selectors and hashes/rules; use a cheap model only to classify a changed snippet. No realtime model unless the owner asks what the change means.
- **latency:** Poll at a user-selected interval (for example 15 minutes to 6 hours); alert within one interval. Do not keep a live browser loop when not needed.
- **cost:** Low if snapshots are diffed locally and only changed text is summarized; browser polling and wakeups dominate. Retain compact before/after snippets, not full pages.
- **security:** Persistent login access and page contents are sensitive. Limit each watch to a declared URL/origin and selector, encrypt state, allow immediate pause/revoke, and prevent all click/type/navigation beyond the watch scope. Alerts may reveal sensitive data aloud, so require a private-mode setting or terse notification.
- **missing:** Persistent watch scheduler with backoff and expiration; Selector/hash diffing and notification deduplication; Per-watch privacy settings and revocation controls


## Changes it proposed to its own stack

### `browser-harness` — Add a typed browser-job protocol with origin allowlists, tab bootstrap via navigate, structured extract selectors, per-action risk labels, screenshot/text evidence, cancellation, and an atomic 'pending irreversible action' state. Return compact structured results instead of full page HTML.
- **owner gets:** Browser tasks become dependable and auditable: the owner can see exactly what was read or drafted, sensitive data is less likely to be copied into model context, and a stalled job can be stopped without leaving half-finished actions.
- effort: Medium: extend local-agent browser bridge, extension result schema, and dashboard review component; add integration tests for no-tab bootstrap and tab/page changes.  ·  risk: Schema mismatch could break existing browser actions; support old action translation and fall back to current text results. A false risk classification must fail closed before irreversible actions.
- cost: Small engineering cost; lower ongoing token cost by sending extracted fields/diffs rather than HTML. No hardware cost.  ·  latency: Slightly faster for extraction; evidence capture adds at most a few seconds near review.
- security: Improves security through origin scoping, redaction, cancellation, and explicit confirmation. The extension still has access to existing logins, so maintain visible activity and revocation.
- depends on: A durable browser command/result correlation ID; Dashboard review surface shared by web, menubar, and iOS

### `memory` — Store browser task definitions as versioned, user-owned recipes (origin, allowed paths, selectors, extracted fields, cadence, privacy/retention, and confirmation policy), while storing only compact redacted results and hashes by default. Prune raw page evidence after review or a short configurable TTL.
- **owner gets:** Recurring tasks keep working without repeatedly explaining them, while old email, financial, and health-page contents do not silently accumulate in the assistant's memory or inflate every prompt.
- effort: Medium: add recipe/result entity types and retention sweeps in D1/R2, plus dashboard controls for inspect/export/delete.  ·  risk: A site redesign can make a recipe wrong; detect selector failures and pause rather than guessing. Incorrect pruning could remove useful evidence, so preserve owner-pinned reports and audit metadata.
- cost: Lower token and storage cost over time; scheduled cleanup adds negligible compute. Audio retention should be swept rather than retaining indefinitely.  ·  latency: Faster recurring runs because recipes avoid planner exploration; first run remains slower.
- security: Materially reduces sensitive-data exposure and gives the owner deletion/export controls. Recipe credentials should never be stored; rely on Safari sessions.
- depends on: Typed browser-job protocol; Working scheduled-job runner and retention sweeper

### `dashboard-ux` — Add a unified Jobs inbox across web, menubar, and iOS showing running/blocked/completed browser and Mac jobs, compact evidence, sensitive-field redactions, and a single prominent 'Approve this exact action' review step. Include pause/revoke, schedule, retention, and per-origin permissions.
- **owner gets:** The owner can understand what the assistant did while away, approve risky actions confidently, and recover from failures without replaying the whole conversation or hunting through logs.
- effort: Medium: shared SvelteKit components plus job/evidence APIs and notification deep links.  ·  risk: Overly dense evidence can overwhelm; default to a concise summary with expandable details. A stale approval could be dangerous, so bind approval to a page/content hash and expire it on change.
- cost: Negligible API cost; fewer repeated voice turns and less model context should reduce cost.  ·  latency: No impact on background execution; faster human approval because all relevant details are in one place.
- security: Makes authorization visible and auditable, but must avoid exposing secrets in notifications or shared screens; redact by default and require device unlock for sensitive evidence.
- depends on: Typed browser-job protocol; Durable job state and content-hash approval tokens


## What it asked for

### `t13-twz9` (tool) — browser_command_enqueue_live
- why: The browser extension is the only tier that can read the owner's existing authenticated Safari pages, but every granted enqueue wrapper still returns an implementation error. A working command path is required for any actual browser task, testing, or useful page extraction.

```json
{
  "type": "object",
  "properties": {
    "deviceId": {
      "type": "string",
      "description": "Optional Safari extension device id; empty targets live Safari"
    },
    "command": {
      "type": "string",
      "enum": [
        "list_tabs",
        "get_active_tab",
        "navigate",
        "extract_page",
        "click",
        "type",
        "key"
      ]
    },
    "url": {
      "type": "string"
    },
    "selector": {
      "type": "string"
    },
    "text": {
      "type": "string"
    },
    "key": {
      "type": "string"
    }
  },
  "required": [
    "command"
  ]
}
```

## Its own summary

I grounded proposals in the actual stack and browser constraints. High-value browser capabilities are: scheduled authenticated-page briefings delivered as short audio; draft-and-review form completion that stops before submit/send/purchase; and selector/hash-based watches for logged-in status changes. I proposed a typed, origin-scoped browser-job protocol with compact extraction, evidence, cancellation, and fail-closed irreversible-action handling; recipe-based privacy-preserving memory; and a unified cross-surface Jobs review inbox. The key operational blocker remains that every granted browser enqueue wrapper is still an unimplemented stub, so I requested a live correlated enqueue tool and informed mac-planner.

**Biggest unknown:** Whether the orchestrator will implement the browser command enqueue path. Without it, I cannot perform or validate any real authenticated Safari workflow, despite the extension being online and navigate being able to bootstrap a tab.

