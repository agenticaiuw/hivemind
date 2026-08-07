# Harness derivation — faculty-perception — round 52

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-observability** — Fresh /observe and /ops/status show AI Pendant Agent is still not trusted for Accessibility and lacks Screen Recording; inputReachability=failed, uiActionsWillReachTheScreen=false, permissions.ready=false. Automation grants are present, but synthesized UI events may report success while doing nothing.
  - evidence: GET /observe at 2026-08-07T11:49:17.183Z and GET /ops/status both report accessibility.trusted=false, screenRecording.granted=false, inputReachability.status=failed and consequence that ui_click/type_text/press_keys receipts cannot be trusted.
- **browser-continuity** — Browser extension is offline while Mac agent reports 5 pending browser commands and 3 durable sessions; current browser tabs are not reachable through the extension. Any resumed browser action must treat pending commands as unconfirmed until heartbeat/result receipts arrive.
  - evidence: GET /browser/status at 2026-08-07T11:49:17 reports online=false, pendingCommands=5; /observe lists sessions=3 and tabs, and /ops/status repeats browserExtension.online=false.
- **browser-command-state** — GET /browser/poll currently returns command browser_fc12217f-842e-4751-8697-c6c71706bd52 with action navigate but empty params, status processing, claimedAt 2026-08-07T11:49:26.661Z, claimedBy home-chrome, attempts=3. This is not an execution receipt and is unsafe to replay without extension online/result correlation.
  - evidence: GET /browser/poll live response at 2026-08-07 (commandId, status, claimedBy, attempts fields).
- **machine-timezone** — Machine context reports authoritative Mac timezone America/New_York.
  - evidence: GET /machine-context live response includes machine.timezone="America/New_York".

## Capabilities it proposed

### "“I lost connection while you were doing that—did it actually happen? Check every surface and tell me what is confirmed, what is unknown, and what you will not repeat.”"
- **useful because:** Today a browser command can be claimed repeatedly while the extension is offline, and Mac UI actions can report success despite Accessibility being untrusted. This gives the owner a truthful interruption report instead of a duplicate action or a fabricated receipt. The pendant can ask/announce offline state, the relay can retain the correlation, Mac perception can inspect the visible app, and the browser can provide a typed result when it reconnects.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Use deterministic reconciliation and cheap background checks first; reserve realtime only for the owner's spoken question and final concise answer. Vision is conditional and only after Screen Recording consent.
- **latency:** 2–5 seconds for local status; up to 30 seconds after browser heartbeat or Mac bridge reconnect. Never auto-retry an irreversible action.
- **cost:** Usually <$0.01 per incident (no model call for status joins; small text model only to summarize conflicting receipts). Vision, if explicitly consented, dominates cost and latency.
- **security:** Do not send screenshots or page contents to the relay unless separately consented. Correlate by jobId/commandId/sessionId and expose provenance timestamps. Treat processing/claimed as not completed; require typed browser result or independently observed UI change. Require confirmation before any replay, especially forms, messages, purchases, or navigation with side effects.
- **missing:** A durable cross-surface interruption record joining Mac job receipts, browser command/result, pipeline events, and pendant connectivity epochs; A read-only reconciliation endpoint that never claims/advances a browser command while inspecting it; A standard terminal state taxonomy: confirmed, observed, rejected, expired, unknown, and safe-to-retry; Accessibility and Screen Recording actually trusted for the running com.aipendant.agent identity; currently /observe proves they are not

### "“When I say ‘what’s this?’ or ‘read that to me,’ use what I’m currently looking at on my Mac or in my browser, answer through the pendant, and don’t retain the screen or page after you answer.”"
- **useful because:** The owner can ask hands-free about the thing in front of them without naming an app, URL, or document. The pendant supplies the immediate voice trigger and playback, the Mac supplies a current visual snapshot, the browser supplies structured text when the target is a page, and the relay coordinates them while enforcing deletion. This is useful precisely because no single surface has both the owner’s spoken deictic reference and the authenticated current screen/page.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Realtime handles only the short spoken turn and response timing. Use a cheaper vision/text model in the background for screenshot or DOM interpretation; prefer browser DOM/accessibility text over pixels and send pixels to a model only with explicit consent.
- **latency:** A first spoken acknowledgement within 300 ms; grounded answer within 2–5 seconds. If the screen/browser cannot be observed, say so rather than guessing.
- **cost:** Typically <$0.02 per request; DOM extraction and small text-model interpretation dominate. Screenshot vision is an optional higher-cost path.
- **security:** Screen/page data may contain passwords, private messages, or financial information. Redact known secret fields, keep raw captures in memory only, encrypt transport, delete them after the answer, and require a per-session consent gesture for pixel capture. Never click, submit, or alter the target as part of answering.
- **missing:** A deictic-target capture protocol that timestamps the pendant utterance against the latest Mac frame and browser DOM snapshot; A Mac observation endpoint that returns a consent-scoped, redacted current frame/accessibility tree without requiring an action; Browser extension support for an ephemeral DOM/text snapshot tied to the active tab and a command correlation ID; A relay retention policy and deletion receipt proving the raw observation was discarded; Working Accessibility and Screen Recording for the exact running agent identity before visual evidence can be considered trustworthy


## Changes it proposed to its own stack

### `integration` — Add a non-mutating cross-surface reconciliation read (for example GET /continuity/:correlationId) that joins /observe, /ops/status, browser session/command state, job receipts, journal, and pipeline events without calling /browser/poll or changing claims. It should emit evidence items with source, timestamp, and confidence, and classify an interrupted operation as confirmed, observed, rejected, expired, or unknown. The action layer must refuse replay when state is unknown unless the owner confirms.
- **owner gets:** After a dropped link, the owner gets an honest answer about whether something happened and avoids duplicate messages, purchases, form submissions, or navigation. It also stops “success” receipts from being mistaken for visible UI changes when permissions are broken.
- effort: Medium: correlation schema plus read-only joins and tests for stale claims, duplicate attempts, and offline epochs; then wire pendant/relay status speech.  ·  risk: A join can be stale or contradictory; show timestamps and uncertainty rather than picking a winner. Recovery is to leave the action untouched and request explicit confirmation. Ensure the endpoint cannot claim browser commands as /browser/poll does.
- cost: Negligible storage and compute; no model needed for the join. Optional summarization costs a small text-model call.  ·  latency: Sub-second locally; network relay status may add 1–3 seconds.
- security: Safer: no page content or screenshots required, and read-only provenance reduces accidental replay. Correlation identifiers must not expose secrets.
- depends on: Actual Accessibility + Screen Recording permission for the running com.aipendant.agent binary before UI-visible evidence can be trusted; Durable correlation IDs propagated across Mac jobs, browser commands, relay jobs, and pendant pipeline events


## What it asked for

_Nothing._
## Its own summary

Fresh live checks completed. The orchestrator's grants did not resolve the actual running binary: /observe still reports Accessibility trusted=false, Screen Recording=false, inputReachability=failed, and UI actions may silently do nothing; /ops/status permissions.ready=false. Browser extension is offline with 5 pending commands and 3 durable sessions. A live /browser/poll shows command browser_fc12217f-842e-4751-8697-c6c71706bd52 in processing, claimed by home-chrome, attempts=3, with empty navigate params—this is not completion evidence and must not be replayed. I recorded these findings, warned faculty-action, and proposed a read-only continuity reconciliation join that cannot mutate browser claims. Machine timezone is established as America/New_York.

**Biggest unknown:** Whether the exact running AI Pendant Agent executable has been granted macOS Accessibility and Screen Recording (live evidence says no), plus the pendant's current playback/link telemetry and continuity acknowledgement state; those remain necessary before claiming end-to-end UI or audio behavior is real.

