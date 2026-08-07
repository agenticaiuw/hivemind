# Harness derivation — faculty-perception — round 19

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-control** — At 2026-08-07T09:49:25Z, Mac foreground app is Claude; AI Pendant Agent Accessibility is not trusted, synthesized events are rejected, input reachability failed, and ui_actions will report success while doing nothing. Screen recording is also false.
  - evidence: GET /observe returned accessibility.trusted=false, eventsPost=false, inputReachability.status=failed, consequence warning, screenRecording=false.
- **browser-connectivity** — At 2026-08-07T09:49:25Z, home Chrome extension is offline with no active tab, while the Mac bridge is online; browser command queue has 2 pending commands.
  - evidence: GET /browser/status returned online=false, home-chrome offline, tabId=null, pendingCommands=2.
- **audio-pipeline** — The latest observed completed spoken response rendered as 24 kHz mono PCM, 164650 bytes, 3430 ms, with zero clipped samples; a later pendant offline store event surfaced 2 held alerts.
  - evidence: GET /pipeline returned tts done metadata sampleRate=24000, pcmBytes=164650, clippedSamples=0, and nrf9160 alert_delivered detail held alerts surfaced.
- **pendant-storage-policy** — Pendant has one button/LED and a single full-duplex I2S peripheral; microSD over SPI/exFAT is intended only as a failure buffer when upload fails, not routine storage. Therefore a perception snapshot should be compact metadata and only persist offline when upload is unavailable.
  - evidence: get_hardware_spec(io) and get_hardware_spec(storage) returned prototype hardware and explicit audio-storage policy.

## Capabilities it proposed

### "Before you do anything, tell me what you can actually see and control right now—my Mac app, screen, browser tabs, and any notes I made on the pendant—and clearly mark anything you cannot verify."
- **useful because:** Today the system can mistake a nominally successful UI action for a real one, or infer browser state from a stale/offline extension. This gives the owner an honest, sourced perception boundary before decisions or actions, combining live Mac observation, browser heartbeat/session state, relay job state, and offline pendant bookmarks/alerts.
- **path:** pendant: owner asks verbally and receives a concise spoken capability report; local bookmarks/held alerts are included with timestamps and link state → relay-realtime: transcribes the request and coordinates a read-only perception job → mac-planner: queries Mac /observe and /browser/status, returning foreground app, accessibility/input reachability, screen-recording state, browser connectivity, and pending queue → browser-extension: if online, returns current tab metadata and session freshness; if offline, explicitly reports unavailable rather than guessing → dashboard: renders each fact with source timestamp, confidence, and a red 'not verified' label; no action surface is invoked
- **model tier:** Realtime only for the short spoken acknowledgment; use a cheaper background model to normalize and explain the read-only telemetry. No vision model is needed unless screen capture permission is present.
- **latency:** Initial spoken boundary in 1–2 seconds from relay/Mac telemetry; browser heartbeat may take up to 5 seconds. Stale pendant events must retain their capture time and never be presented as current.
- **cost:** Low: one short realtime turn plus a small background normalization call; dominated by realtime audio, not telemetry. No screenshots or page contents leave the Mac unless separately requested.
- **security:** Read-only metadata can reveal the foreground app, open-tab URLs, and offline notes. Redact URL query strings and sensitive note text by default. Never claim control from a nominal action receipt when accessibility/inputReachability is false. Require explicit confirmation before any follow-up action.
- **missing:** A typed perception snapshot contract shared by relay, Mac, browser, and pendant, with source timestamps, TTL, and confidence; A pendant-side read API for bookmarks/held alerts (currently only surfaced indirectly in pipeline events); Browser extension heartbeat/session freshness exposed to the relay without relying on stale cached status; Mac UI hierarchy/screen capture only after Accessibility and Screen Recording are granted to the actual AI Pendant Agent binary

### "If your devices disagree about what happened, tell me plainly which versions conflict, what evidence each one has, and ask me only the smallest question needed to resolve it—before anyone acts."
- **useful because:** A wearable may record an offline bookmark, the relay may receive it late, the Mac may report a job as complete, and the browser may still be offline or unchanged. Today those partial truths can be silently merged into a confident but false story. The owner needs contradiction detection, not merely more logs or another briefing.
- **path:** pendant: attaches a monotonic capture id and link state to each spoken request, bookmark, alert, and playback acknowledgement; it can announce a short conflict alert even after reconnect → relay-realtime: correlates delayed pendant events, relay receipts, and Mac/browser reports into one incident without treating arrival order as event order → mac-planner: supplies job lifecycle and observation claims with event-time, execution-time, and receipt-time separately; it must expose when a UI receipt is unverified → browser-extension: supplies tab/session evidence and command acknowledgements, including offline gaps and tab identity → unified: runs independent claim comparison and emits a contradiction record with evidence pointers, confidence, and the minimum clarification question; faculty-judgement decides whether the conflict blocks action → dashboard: presents a side-by-side claim diff and resolution history, while the pendant speaks only the concise conflict and question
- **model tier:** Use a cheap background model or deterministic schema comparison for timestamps, IDs, status, and field conflicts. Reserve realtime for the spoken conflict notification and the owner's answer; no expensive model is needed for routine agreement.
- **latency:** Detect conflicts within 1–3 seconds after each new receipt or reconnect. Offline events may be reconciled later, but must remain visibly late and never overwrite a newer event without an explicit resolution.
- **cost:** Low ongoing cost: mostly structured comparison and D1 event storage; occasional background normalization dominates. Realtime cost occurs only when a conflict needs to be spoken or clarified.
- **security:** Evidence may contain private URLs, app names, audio metadata, or message text. Store hashes and minimal excerpts by default, redact secrets, restrict evidence to the owner, and require confirmation before resolving a contradiction by taking an external action. Never silently discard either claim.
- **missing:** A durable event envelope with globally unique event ID, origin, capture time, observed time, receipt time, and causal links across pendant, relay, Mac, and browser; A contradiction ledger and deterministic field-level comparator with retention and owner-visible resolution states; Mac and browser adapters that distinguish attempted, accepted, executed, and verified outcomes instead of one success boolean; A reconnect reconciliation protocol that is idempotent and preserves late/offline events; A unified clarification response path from the pendant back to the blocked incident


## Changes it proposed to its own stack

### `integration` — Introduce a cross-surface event-envelope and contradiction ledger. Every pendant, relay, Mac, and browser record carries origin, event ID, capture time, observed time, receipt time, causal predecessor, evidence hash, and verification state. A deterministic comparator creates an unresolved conflict when two claims about the same request disagree; reconciliation is append-only, idempotent, and cannot erase the late/offline claim. Expose a minimal conflict feed to unified and the dashboard, with a pendant-sized alert payload.
- **owner gets:** They stop receiving a smooth but false account of whether something was heard, delivered, executed, or verified. When the system disagrees, they get the exact disagreement and one focused question instead of having to reconstruct it from logs.
- effort: Medium-high: shared schema and migrations, adapters for four producers, comparator, reconnect reconciliation, dashboard diff, and a small relay-to-pendant alert path. Requires test fixtures for offline, duplicate, delayed, and contradictory events.  ·  risk: More visible uncertainty and additional records may initially feel noisy; clock skew can create false conflicts. Mitigate with monotonic per-device sequence numbers, server receipt ordering only as a fallback, confidence thresholds, and an owner-configurable quiet policy. Recovery is append-only replay and ledger rebuild.
- cost: Low runtime/API cost for structured comparisons and hashes; modest D1/R2 metadata growth. Audio and page content should not be copied into the ledger unless explicitly needed.  ·  latency: Sub-second local comparison and roughly 1–3 seconds after cross-surface receipt; reconnect reconciliation can continue in background.
- security: Evidence hashes and redacted excerpts reduce exposure, but event metadata still reveals activity timing and app/site identity. Encrypt sensitive evidence, enforce owner-only access, and apply short retention to raw excerpts.
- depends on: Typed producer adapters for pendant, relay, Mac, and browser; A durable idempotency/event-ID scheme; Verified-vs-attempted outcome states from Mac and browser; A clarification/acknowledgement route to the pendant


## What it asked for

### `t2-bi37` (tool) — get_perception_snapshot
- why: The owner needs a single read-only, provenance-bearing answer about what each surface can currently observe/control. Existing tools expose Mac status and browser actions separately, and stale/offline state can otherwise be mistaken for live truth.

```json
{
  "type": "object",
  "properties": {
    "include_pendant": {
      "type": "boolean"
    },
    "include_browser": {
      "type": "boolean"
    },
    "include_mac_ui": {
      "type": "boolean"
    },
    "max_age_seconds": {
      "type": "integer",
      "minimum": 0
    }
  },
  "additionalProperties": false
}
```

