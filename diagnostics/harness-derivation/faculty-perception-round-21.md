# Harness derivation — faculty-perception — round 21

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observability** — At 2026-08-07T09:54:30Z, Mac foreground app is Claude (com.anthropic.claudefordesktop), 13 user apps running. Accessibility is not trusted for AI Pendant Agent, synthesized input is rejected, Screen Recording is not granted, and /observe explicitly says UI actions may report success while doing nothing; machine ready=false.
  - evidence: GET /observe returned foregroundApp Claude, accessibility.trusted=false, eventsPost=false, screenRecording=false, uiActionsWillReachTheScreen=false; GET /ops/status corroborates ready=false.
- **fleet-connectivity** — At 2026-08-07T09:54Z, Mac bridge and cloud relay are reachable/online, but browser extension home-chrome is offline with 2 pending commands. Three durable browser sessions exist on the Mac, including default at https://time.is/UTC and two Selenium/httpbin probe tabs.
  - evidence: GET /ops/status and GET /browser/status; GET /observe browser.tabs.
- **pendant-offline-events** — Pipeline telemetry contains pendant-origin offline-store events: at 07:22 held alerts surfaced (2 alerts, last_alert_id=a3), at 07:16 one held alert surfaced (last_alert_id=a1), and at 07:12 a moment bookmark was held while link was down. These records show offline events are being forwarded after reconnection.
  - evidence: GET /pipeline response events with source nrf9160, meta.storage=microSD, origin=pendant-offline-store.

## Capabilities it proposed

### "“When my pendant reconnects, catch me up on anything that happened while I was offline—what was captured, what arrived late, what actually ran on the Mac or browser, and what is still waiting—without repeating or rerunning anything.”"
- **useful because:** The current system demonstrably holds pendant alerts/bookmarks on microSD and forwards late voice responses, while the browser can be offline with queued commands and the Mac can be reachable but incapable of trusted UI input. A reconnect digest would prevent duplicate actions and make offline behavior understandable in one short spoken update.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay/background model to reconcile typed event receipts; use realtime only to speak the short digest when the pendant reconnects.
- **latency:** First digest within 3 seconds of link restoration; incremental updates can arrive later. No action is rerun as part of reconciliation.
- **cost:** Usually <$0.01 per reconnect; dominated by one small reconciliation/summary call, with event hashing and deduplication local/relay-side.
- **security:** Digest may reveal private browser/account activity over the pendant speaker. Keep source snippets off the relay digest, include only owner-approved event titles and statuses, and require explicit confirmation before surfacing sensitive account names or taking a retry action.
- **missing:** A durable exactly-once event ledger spanning pendant offline-store IDs, relay jobs, Mac jobs, and browser command IDs; A reconciliation endpoint that labels each item captured/received/queued/applied/failed/unknown with source timestamp and freshness; Pendant reconnect trigger and spoken-summary acknowledgement state; A rule preventing automatic retries during reconciliation, especially when Mac Accessibility or browser extension reachability is false

### "“For anything I said to the pendant, let me ask ‘what happened to that?’ and get a single evidence-backed timeline—from audio capture through relay, planning, Mac/browser execution, and spoken reply—clearly separating completed, queued, failed, and unknown.”"
- **useful because:** Today the pieces expose different partial truths: pendant offline records, relay jobs, Mac pipeline events, and browser pending commands. The owner cannot reliably distinguish ‘the system heard me,’ ‘it planned it,’ ‘it actually changed something,’ and ‘the reply was only waiting to be played.’ A causality trace would answer that question without guessing or rerunning work.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap background reconciliation model—or deterministic event joining first—to construct the trace; use realtime only when the owner asks verbally through the pendant.
- **latency:** Deterministic lookup and merge under 500 ms for recent events; up to 3 seconds if semantic labels are needed. Never wait by silently retrying an action.
- **cost:** Usually <$0.005 per query; event joins and status classification should be local/relay-side, with model cost only for ambiguous labels.
- **security:** The trace can expose private page titles, commands, and message content. Store identifiers and status by default, redact payloads, enforce per-owner authorization, and require confirmation before revealing sensitive source text or offering a retry.
- **missing:** A shared correlation ID propagated from pendant capture through relay, Mac/browser jobs, TTS delivery, and pendant playback; A normalized event vocabulary with terminal states and explicit unknown/late/duplicate markers; Immutable, privacy-redacted receipts retained long enough to answer historical queries; A query path available to the pendant that can return a compact trace while offline or after reconnect


## Changes it proposed to its own stack

### `mac-harness` — Make the Mac action harness consume the read-only /observe trust fields before executing UI steps. When accessibility.trusted=false, eventsPost=false, screenRecording=false, or inputReachability.status is failed, every UI-dependent step must return a typed `untrusted_precondition` result with the exact failed observation and must not emit a success receipt; non-UI actions (filesystem, approved AppleScript targets) remain separately classified. Stamp the observation timestamp and a short-lived state epoch onto each action receipt so a permission change or browser disconnect invalidates prior plans.
- **owner gets:** The owner will no longer be told that a click or typed command succeeded when the Mac visibly did nothing. They get an honest explanation—such as Accessibility being granted to the wrong binary—and can still use safe non-UI actions instead of losing time debugging phantom success.
- effort: Moderate: central preflight in the Mac action dispatcher, typed receipt schema, tests for stale epochs and mixed UI/non-UI plans, plus relay propagation.  ·  risk: Some existing clients may treat current optimistic success as completion; version receipts and provide a migration adapter. Recovery is a fresh observation after permissions are fixed, then re-plan only the failed UI steps.
- cost: Negligible API cost; one small local preflight and receipt payload per action.  ·  latency: Adds roughly 10–50 ms for local observation/preflight; avoids expensive failed computer-use loops.
- security: Improves safety by preventing untrusted UI execution and by exposing only permission-state metadata, not screen contents.
- depends on: A stable typed /observe response and action receipt schema; Planner/judgement support for `untrusted_precondition` and state epochs; A permission repair path or owner-facing instructions for the AI Pendant Agent binary

### `interaction` — Add a cross-surface completion vocabulary and pendant indication: every owner-originated request is assigned one of four states—heard, queued, applied, or needs-owner—and the relay pushes only state transitions. The pendant gives a short distinct acknowledgment for heard/queued and a separate completion cue for applied; the spoken answer includes the same state token. Mac and browser adapters must translate their native receipts into this vocabulary, while an explicit unknown state is used when permissions or reachability prevent verification.
- **owner gets:** The owner gets immediate, honest feedback even when away from the Mac: they can tell whether the pendant merely heard them, whether work is waiting, or whether a real external change was verified. This removes the dangerous ambiguity between a successful voice response and a completed action.
- effort: Moderate protocol and firmware/UI work: state transition schema, relay fan-out, Mac/browser receipt adapters, reconnect-safe deduplication, and short local tones/LED patterns.  ·  risk: A lost completion event could leave the pendant at queued; recover by replaying the latest durable state on reconnect and allowing the owner to ask for the causality trace. Never promote queued or unverified to applied.
- cost: Negligible API cost; small relay storage and one compact push per transition. Firmware uses existing notification hardware rather than new sensors.  ·  latency: Heard/queued cue can be immediate; applied cue depends on the responsible surface and should not add execution latency.
- security: Cues reveal only state, not private content. Spoken details remain subject to owner authentication and redaction rules.
- depends on: A shared correlation ID and normalized event vocabulary; Durable relay state-transition replay; Mac/browser adapters that stop emitting optimistic success; Pendant firmware support for distinct notification patterns


## What it asked for

_Nothing._
