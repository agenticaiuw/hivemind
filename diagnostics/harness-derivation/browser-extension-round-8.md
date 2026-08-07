# Harness derivation — browser-extension — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser execution** — The browser enqueue implementation is still absent in this round; browser commands cannot be sent even though Safari extension protocol and navigate bootstrap are specified. Safari currently has zero tabs, so no authenticated page can be read until enqueue is implemented or owner opens a tab.
  - evidence: browser_enqueue_command_implemented returned error: tool granted schema but has no implementation; prior live state says tabCount=0 and browser_read_page reports no matching tab.

## Capabilities it proposed

### "Research this topic across my logged-in websites, compare the results, and send me a concise audio brief later."
- **useful because:** Authenticated browser access can reach private dashboards, subscriptions, and accounts unavailable to public search; asynchronous delivery avoids making the owner wait.
- **path:** pendant voice request → relay job queue → Mac browser bridge for authenticated pages → dashboard job/result and audio playback
- **model tier:** Use cheap background model for page extraction, deduplication, and comparison; use realtime only to clarify the request or summarize interactively. Browser navigation/extraction should be deterministic actions, not expensive model turns.
- **latency:** Acknowledge in under 1 second; finish in 1–5 minutes depending on sites; deliver when complete.
- **cost:** Typically a few planner/extraction calls plus one short synthesis, substantially cheaper than keeping realtime audio open; dominant costs are model tokens and generated audio, not browser commands.
- **security:** Private page contents leave the browser bridge for processing and may contain account data. Default read-only, show source URLs, isolate sites per task, and require confirmation before submitting forms, sending messages, buying, or changing settings.
- **missing:** A durable multi-page browser job runner with per-site tab/session isolation; Result schema containing URL, title, extracted claims, timestamps, and permission scope; Background audio synthesis and notification when a job completes

### "Watch this logged-in page or price/availability page and tell me only when the specified condition changes."
- **useful because:** Turns browser access into useful passive monitoring for bills, appointments, deliveries, inventory, and work dashboards without repeatedly asking the owner.
- **path:** dashboard routine editor → relay scheduler → Mac Safari browser bridge → pendant notification/audio
- **model tier:** Scheduled fetch and DOM/diff logic on a cheap background tier; use realtime only for conversational setup or ambiguous condition interpretation.
- **latency:** Polling cadence configurable from 5 minutes to daily; alert within one polling interval.
- **cost:** Low if DOM snapshots are hashed and only changed sections are sent to the model; audio only on alerts. Cost is dominated by polling frequency and pages requiring visual/model interpretation.
- **security:** Persist only encrypted cookies/session references on the Mac; never copy credentials into the relay. Require explicit opt-in per URL, redact unrelated page regions, pause on logout/CAPTCHA, and require confirmation for any action beyond reading.
- **missing:** Scheduled browser polling with change fingerprints; Encrypted local credential/session handling and routine pause controls; Diff-aware alert and notification pipeline

### "Fill out this online form using the details we discussed, stop before the final submit, and show me exactly what will be sent."
- **useful because:** Removes repetitive data entry while preserving owner control over consequential submissions; browser can use existing authenticated sessions and visually verify the final payload.
- **path:** pendant voice request → Mac Safari browser bridge → dashboard preview with highlighted fields → pendant or iOS confirmation → browser submit only after confirmation
- **model tier:** Cheap structured extraction and form filling; stronger model only for ambiguous fields or mapping natural language to sensitive fields. Realtime handles confirmation dialogue.
- **latency:** Draft in 10–30 seconds; confirmation and final submit happen only after owner responds.
- **cost:** Low-to-moderate tokens; screenshot/evidence capture dominates browser-side work, and audio is limited to the preview/confirmation.
- **security:** Wrong recipient, amount, date, or disclosure is the primary risk. Never auto-submit; display all changed fields and destination domain, redact stored secrets, require a fresh confirmation bound to the exact payload, and log what was submitted.
- **missing:** Field-level form semantic extraction and safe value mapping; Human-readable before/after preview with sensitive-field controls; Confirmation token bound to page URL and form hash


## Changes it proposed to its own stack

### `browser-harness` — Add a durable browser-task runner: bootstrap a tab via navigate, maintain task-scoped tab IDs, execute read/click/type/wait sequences with timeouts, capture URL/title/DOM text and screenshots, and return structured evidence plus an audit log. Separate read-only tasks from mutating actions and gate the latter on explicit confirmation.
- **owner gets:** Browser work becomes reliable enough to finish research and routine tasks later instead of timing out or losing track of which page was used.
- effort: Medium: extension command protocol, Mac bridge worker, retry/state machine, and dashboard audit view.  ·  risk: Sites with popups, CAPTCHAs, or changed layouts may cause wrong targeting; fail closed, require selectors/evidence checks, and let the owner resume manually from the recorded tab.
- cost: Small ongoing storage/token overhead; fewer repeated planner calls should reduce total cost.  ·  latency: Adds seconds for retries and evidence capture, but enables asynchronous completion rather than blocking voice.
- security: Increases retained metadata about private pages; encrypt task artifacts, redact secrets, and enforce confirmation for submit/purchase/send actions.
- depends on: A result schema shared with mac-planner; Per-task browser tab/session isolation; Notification/audio job completion

### `model-routing` — Introduce a browser-specific low-cost pipeline: deterministic command planner for navigation/extraction, small model for selector repair and page summarization, and realtime model only for owner-facing dialogue. Pass compact evidence bundles rather than full page HTML into subsequent turns.
- **owner gets:** Authenticated web tasks finish faster and cost less while still handling ordinary site layout changes; conversations remain responsive.
- effort: Medium: classifier, selector-repair fallback, evidence compactor, and per-task model policy.  ·  risk: A cheap model may misunderstand a page or click the wrong control; enforce read-only defaults, confidence thresholds, evidence assertions, and escalation to the stronger model before any mutation.
- cost: Lower token usage per task; occasional escalation adds cost only on hard pages.  ·  latency: Usually lower; selector repair may add one retry.
- security: Compact evidence reduces exposure of unrelated private content; still needs redaction and task-scoped retention.
- depends on: Structured browser evidence schema; Action risk scoring exposed to browser runner; Durable task state

### `dashboard-ux` — Add a Browser Jobs view shared by web, menubar, and iOS: active/queued/completed jobs, per-site permission scope, source evidence, extracted result, pending confirmation cards, pause/cancel, and retention controls. Make every mutation previewable with destination, fields, and exact confirmation status.
- **owner gets:** The owner can see what the browser is doing, recover from a stuck login, and approve consequential actions without guessing whether a task succeeded.
- effort: Medium: Svelte views plus Worker job/event endpoints and shared result types.  ·  risk: A dashboard bug could hide pending actions; default to fail-closed and expose the raw audit event when rendering fails.
- cost: Small storage/UI cost; evidence retention should be capped to control D1/R2 growth.  ·  latency: No meaningful impact on live interaction; event streaming makes progress visible.
- security: Dashboard itself exposes private browsing activity; require local auth, redact page text by default, and enforce per-task retention/deletion.
- depends on: Durable browser-task runner; Structured evidence and audit schema; Shared confirmation service


## What it asked for

### `t7-f8pe` (tool) — browser_command_enqueue
- why: The granted browser enqueue tool is currently unimplemented, so I cannot bootstrap Safari or execute even read-only navigation despite the extension protocol existing. A working enqueue endpoint is required for authenticated browser usefulness.

```json
{
  "type": "object",
  "properties": {
    "deviceId": {
      "type": "string",
      "description": "Optional registered browser device; empty targets live Safari"
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

I proposed three owner-facing browser capabilities: asynchronous authenticated research with audio delivery, change monitoring of logged-in pages, and safe form filling that previews exact fields before submission. I proposed a durable browser-task runner, browser-specific cheap-model routing, and a shared Browser Jobs dashboard with evidence, permissions, audit, pause/cancel, and confirmation. I also informed mac-planner of the structured handoff schema and safety gates. The immediate blocker remains concrete: the granted browser enqueue tool has no implementation, Safari currently reports zero tabs, and I cannot execute or bootstrap any browser action. I requested an implemented enqueue tool and recorded this finding.

**Biggest unknown:** The exact cross-surface job/evidence/confirmation schema and whether browser session state can be safely retained or transferred to a server-side browser; without the enqueue implementation I cannot validate any authenticated workflow end to end.

