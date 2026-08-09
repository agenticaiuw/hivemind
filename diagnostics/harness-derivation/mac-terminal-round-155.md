# Harness derivation — mac-terminal — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser and routing health** — Safari extension and Mac bridge are online with 9 tabs, but heartbeat capabilities is empty; browser failures include repeated inaccessible-frame errors. /routing reports zero requests and zero samples despite /journal showing 120 jobs, 174 actions, and 54 failed actions.
  - evidence: GET /ops/status, GET /browser/status, GET /jobs/local_ed75c632-747c-4739-9340-7ec1117fa6d3, GET /routing, GET /journal

## Capabilities it proposed

### "When I press the pendant and ask “what am I looking at?”, read the active Safari tab I’m actually viewing, summarize only the useful content aloud, and if the page is inaccessible tell me exactly why instead of retrying blindly."
- **useful because:** This is the system's most valuable everyday loop: the pendant supplies hands-free intent, Safari supplies authenticated state the cloud cannot access, and the Mac/relay turn it into a short answer. The live Mac already has a 9-tab authenticated Safari session and browser_read_page succeeds when pinned to the active tabId; this removes the need to dictate URLs or expose page contents to a third-party login.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime only for the spoken turn and intent extraction; deterministic browser_list_tabs plus browser_read_page first, then a cheap background summarizer for long text. Escalate to vision only when DOM extraction reports an inaccessible frame or the owner explicitly asks what is visually shown.
- **latency:** 3 seconds for tab discovery and extraction, 2 more seconds for spoken summary; vision fallback up to 8 seconds with an explicit “I’m looking at the screen” status.
- **cost:** Usually one deterministic tool sequence plus 300–800 summary tokens; realtime audio dominates. Vision fallback is the expensive path and should be rare.
- **security:** Authenticated page text leaves the Mac for summarization through the existing relay/model path; redact passwords, payment fields, tokens, and hidden inputs before upload. Never read a non-active tab unless the owner names it. If extraction fails, report the concrete browser error and do not invent content.
- **missing:** A browser intent that resolves active tabId then performs one bounded read, rather than URL-based reads; A sanitizer that removes secret-like fields before relay summarization; A spoken error taxonomy for extension injection/frame access failures

### "Every weekday morning, inspect the authenticated tabs I have already left open, group only items that need my attention today, and read me a five-item maximum digest with the tab name and a direct next action."
- **useful because:** The owner has real authenticated work state in Safari that briefing.js cannot reach. The live extension exposes nine tabs, including Gmail and the active OpenAI billing page, but the current system repeatedly launches invalid example URLs and spends 54 failed actions on inaccessible frames. A bounded open-tab digest turns browser sessions into useful morning triage without asking the owner to log in again.
- **path:** relay-realtime → browser-extension → mac-planner → relay-realtime
- **model tier:** Scheduled/background tier: deterministic tab enumeration and per-origin allowlist first, then a cheap summarizer with strict five-item output. Realtime is used only to read the finished digest on the pendant.
- **latency:** Run in under 30 seconds in the background; speech starts within 1 second when the owner asks for the digest. Skip any tab that exceeds a 4-second extraction budget.
- **cost:** Nine tab metadata reads are deterministic; summarize at most 6,000 sanitized tokens, normally a few cents or less on a background model. Realtime speech is the dominant interactive cost.
- **security:** This intentionally processes authenticated content. Keep origin/tab allowlists local, redact credentials, payment data, and message bodies unless the owner has enabled that origin, and retain only extracted action items with source tab and timestamp. Require explicit per-origin enrollment; never navigate or mutate pages.
- **missing:** A durable per-origin enrollment and redaction policy for scheduled browser reads; A scheduler job that snapshots only already-open tabs and records freshness; Frame-access recovery that marks a tab unavailable instead of generating repeated retries

### "Let me say “I need to finish this before I leave” on the pendant, then have the system watch the active Mac project and authenticated browser tabs, detect the smallest concrete next step, and remind me only when that step is actually unblocked—silently deferring reminders while I am speaking or presenting."
- **useful because:** This turns the hive into an executor of intent rather than another inbox. The pendant captures the commitment at the moment it matters; the Mac knows the foreground project and app state; the browser holds the authenticated dependency; and the relay can wait until the dependency changes. The owner gets one timely nudge instead of repeated generic reminders.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Use realtime only to capture the commitment. Use a background model to derive one next step and a deterministic watcher to test its precondition; use realtime again only when delivering the short reminder.
- **latency:** Capture immediately; derive the step within 10 seconds. Re-evaluate on browser heartbeat, project change, or scheduled checkpoints, with no more than one spoken interruption per hour.
- **cost:** One short realtime turn plus infrequent background extraction; most checks are deterministic metadata comparisons and cost essentially nothing.
- **security:** The watcher sees project names and authenticated-tab metadata, not unrestricted page contents by default. Store the commitment, precondition, and evidence timestamp encrypted locally; require explicit confirmation before any mutation such as sending, purchasing, or deleting.
- **missing:** A durable commitment object with a single next-step precondition and expiry; Cross-surface change events for foreground project, active tab, and browser authentication state; An interruption arbiter shared by relay audio and Mac notifications

### "When I say “I’m going into a meeting,” have the pendant and Mac create a temporary focus contract: suppress noncritical voice and browser notifications, capture urgent items into a private queue, and give me one prioritized spoken handoff when I say “I’m back.”"
- **useful because:** The owner should not have to manually coordinate pendant audio, Mac notifications, and authenticated browser work before every meeting. The wearable provides reliable start/end intent, the Mac can observe and suppress local interruptions, and the browser can classify which open-session changes are urgent. The return handoff is more useful than a stream of interruptions during the meeting.
- **path:** relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime for the two short boundary utterances; deterministic suppression and event capture during the contract; background ranking of queued items; realtime for the final spoken handoff.
- **latency:** Focus starts within 500 ms and ends within 1 second. Queueing is local and immediate; handoff generation under 5 seconds.
- **cost:** Near-zero during the meeting aside from event storage; one small background ranking call at return and a short realtime response.
- **security:** The contract must never suppress safety-critical system alerts. Keep queued browser snippets local until handoff, redact message bodies and credentials, and expire all meeting data automatically after a configurable retention period.
- **missing:** A cross-surface focus contract API with begin/end/expiry and criticality rules; Mac notification suppression and restoration with a crash-safe prior-state snapshot; Browser event buffering that records only changed titles, senders, and urgency signals

### "If the relay or internet drops while I am wearing the pendant, let me keep asking short commands and get spoken answers from my Mac over the live USB pendant and audio bridge, then reconcile the conversation with the relay when it returns without repeating actions."
- **useful because:** The hardware is physically present and testable today even though LTE registration is not. A cloud outage should not turn a wearable command device into a dead button: the pendant, Mac, and ESP32 bridge can provide a local control-and-speech path, while the relay later merges only the unanswered conversational turns. This is a genuinely different failure mode from merely showing an offline LED.
- **path:** relay-realtime → mac-planner → mac-vision → unified
- **model tier:** A small local Mac model or deterministic command recognizer for short commands; no realtime cloud model while disconnected. Use the expensive realtime tier only to reconcile ambiguous turns after connectivity returns.
- **latency:** Button-to-local acknowledgement under 300 ms; simple command result under 2 seconds; reconciliation after reconnect is asynchronous and must not block local control.
- **cost:** No cloud API cost during outage; local CPU and audio conversion dominate. A small reconciliation call is made only for turns that were not fully answered locally.
- **security:** Local mode must visibly state that cloud context and authenticated browser sessions are unavailable. Keep a bounded encrypted turn journal, attach idempotency keys to every attempted mutation, and reconcile as facts—not as permission to repeat side effects.
- **missing:** A USB serial protocol carrying pendant turn IDs and command/result envelopes; A local Mac speech/intent fallback with a strict supported-command set; A durable exactly-once reconciliation protocol between local journal and relay jobs; ESP32 bridge audio routing that can switch between cloud and local playback


## Changes it proposed to its own stack

### `browser-harness` — Add an extension capability handshake and bounded failure classifier. On heartbeat, have the Safari extension report injectable-frame support, active tabId, granted origins, and extension version; on browser_read_page, resolve tabId before urlContains, canonicalize URLs with an explicit scheme, and classify failures as invalid URL, no host permission, inaccessible frame, stale tab, or extraction timeout. Cache one failure per (tabId, origin, error class) for 10 minutes so planners stop issuing identical retries; return a recovery hint such as activate-tab, request-origin-permission, or use-screen-capture.
- **owner gets:** The owner gets a truthful answer instead of a loop of identical failures. Today the extension reports online but capabilities=[]; the logs show repeated “Extension does not have access to this frame” failures and a navigation to example.com rejected as an invalid URL. A single diagnostic lets the pendant say “Safari can’t read this frame; activate the tab or grant this site” and move on.
- effort: Medium: extension heartbeat schema, browserBridge normalization, typed error mapping, and planner retry suppression; add integration tests for the nine currently open tabs and iframe-denied pages.  ·  risk: A stale cached error could suppress a newly fixed permission. Include extension-version, tab-generation, and 10-minute expiry in the key; an explicit owner request bypasses suppression. URL canonicalization must not alter authenticated paths.
- cost: Negligible runtime cost; avoids dozens of failed browser actions and their planner/context-token costs.  ·  latency: Heartbeat payload grows slightly; successful reads become faster by eliminating repeated failed attempts. Permission recovery may add one round trip.
- security: Reports origin permissions and frame capability metadata to the local agent only; never report page contents in the heartbeat. Keep origin grants scoped and redact URLs containing query secrets.
- depends on: Safari extension heartbeat support; browser_read_page accepting stable tabId as the primary locator; A typed browser error contract shared by browserBridge and planner

### `model-routing` — Join every execute/plan job to its routing receipt and persist the selected tier, model, prompt/completion token estimates, latency, and escalation reason in the durable job record and /journal response. Populate routingStats from the actual planner and deterministic paths, not only the streaming API. Add a compact GET /routing/recent?limit=20 view keyed by jobId and action type.
- **owner gets:** The owner can finally see whether the system is spending expensive model calls or merely running deterministic actions. Right now /routing reports totalRequests=0 and no samples while /journal reports 120 stored jobs, 174 actions, 54 failures, and every job unattributed. That makes it impossible to notice a costly retry loop or choose a cheaper path.
- effort: Medium: pass jobId through planner/orchestrator into routing receipts, persist bounded scalar telemetry, and add a read-only route/dashboard panel.  ·  risk: Telemetry can become a privacy leak or inflate the job store. Store model/tier and token counts, not prompts or page contents; cap recent records and redact command strings. If persistence fails, execution must continue and mark telemetry unavailable.
- cost: Small disk writes; likely saves API cost by exposing accidental escalations and repeated failed browser calls.  ·  latency: Sub-millisecond in-memory accounting plus one bounded atomic write per completed job; no extra model call.
- security: Improves auditability without exposing secrets. Treat model names and token counts as local-only authenticated data.
- depends on: A stable jobId passed into routing instrumentation; A bounded durable telemetry schema; No change to FULL_CONTROL execution policy


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: commitment-aware next-step nudging across Mac/browser/pendant, a temporary meeting focus contract with deferred urgent handoff, and a local USB conversational fallback that continues through relay outages with exactly-once reconciliation. The missing pieces are durable commitment/precondition state, cross-surface interruption and notification control, USB turn envelopes, local command fallback, and reconciliation semantics.

**Biggest unknown:** Whether the existing USB-connected nRF9160 and ESP32 firmware expose enough stable audio/control framing to implement local fallback without a firmware protocol change.

