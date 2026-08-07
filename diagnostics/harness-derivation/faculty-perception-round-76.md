# Harness derivation — faculty-perception — round 76

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS computer-use reachability** — At 2026-08-07T13:02Z, AI Pendant Agent cannot reach screen/input: accessibility trusted=false, screenRecording=false, inputReachability failed, and observe explicitly warns ui_click/ui_menu/type_text/press_keys can report success while doing nothing. computer-use loopEnabled=false and visionUploadConsented=false.
  - evidence: GET /ops/status and GET /observe HTTP 200 live responses.
- **live fleet status** — At 2026-08-07T13:02Z, home-macbook-bridge is online; no pendant is registered. home-chrome browser extension is offline with 7 pending commands and 3 durable browser sessions.
  - evidence: discover(devices) plus GET /ops/status and GET /observe.
- **audio pipeline history** — Pipeline history contains a 24 kHz mono PCM TTS result (75,734 bytes, 1,578 ms) uploaded to relay and awaiting pendant, but this is historical; no pendant is currently connected.
  - evidence: GET /pipeline live response and device table.

## Capabilities it proposed

### "“What can you actually see and control right now?”"
- **useful because:** The owner gets an honest, concise fleet-status answer before asking for work: which device is present, whether the Mac can really control its UI, whether private browser sessions are reachable, and whether a reply can reach the pendant. It prevents the current dangerous mismatch where a UI receipt says success but input is not reaching the screen.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception
- **model tier:** Cheap background/state synthesis; use realtime only to speak the already-computed status.
- **latency:** Under 1 second from cached snapshots; refresh only stale surfaces in parallel.
- **cost:** Near-zero model cost when rendered from typed state; a small synthesis call only when there are conflicting or nuanced states. Dominant cost is none/low-latency relay transport.
- **security:** Do not include URLs, page text, account names, or screenshots by default. Report capability states and timestamps only; require confirmation before exposing sensitive browser/session details.
- **missing:** A unified, typed fleet-observation snapshot with freshness and provenance; A perception-backed action-trust barrier for UI receipts; Pendant presence/registration event surfaced in the same snapshot


## Changes it proposed to its own stack

### `context` — Add a perception-backed action-trust barrier: before any UI action is accepted as completed, query the latest /observe reachability snapshot and attach a tri-state result (verified-reachable, unreachable, unknown) to the action receipt. If unreachable, force the receipt to 'not evidenced' and prevent downstream agents from treating the action as success; preserve the intended action for retry after reachability changes. Also invalidate snapshots after a short TTL or foreground-app/permission change.
- **owner gets:** The owner will stop being told that a click or typed message happened when the agent demonstrably could not affect the screen. Failed computer-use attempts become safe to retry instead of silently losing work.
- effort: Moderate: action-receipt schema, preflight hook in mac action runner, 2–5 second observation cache, and downstream planner/judgement handling for not-evidenced receipts.  ·  risk: A transient probe failure could conservatively defer a harmless action; recover by retrying after a fresh observation. It must not claim verification from a stale screenshot or receipt alone.
- cost: Negligible API cost; one local observation/read per UI batch, no model call.  ·  latency: ~50–200 ms local preflight when cache is stale; no added latency for non-UI actions.
- security: Improves safety by preventing false claims. Observation remains local; no screenshots or page contents leave the Mac unless separately consented.
- depends on: GET /observe reachability fields; existing action receipts and undo/job journal; owner enabling Accessibility and Screen Recording if pixel/UI control is desired

### `context` — Build a cross-surface contradiction detector that continuously compares time-stamped observations, rather than trusting any one subsystem: pendant-delivery claims against registered-device presence, browser-command results against extension heartbeat, and UI-action receipts against inputReachability. When mutually incompatible facts appear, emit a durable 'reality conflict' record with both sources, timestamps, and an expiry; mark dependent jobs unresolved until a fresh observation resolves it. Do not auto-retry or silently choose a winner.
- **owner gets:** The owner gets an honest answer when the system disagrees with itself, instead of a polished but false completion message—for example, audio reported as waiting for a pendant that is not connected, or a browser action whose result is stale after the extension went offline.
- effort: Moderate-to-high: typed observation envelopes, pairwise contradiction rules, durable conflict records, and planner/briefing rendering. No new model is required for the initial rule set.  ·  risk: Over-reporting during brief reconnects could make the system feel hesitant; mitigate with source-specific grace windows and explicit expiry. Never erase either observation, and allow a fresh probe to close a conflict.
- cost: Negligible storage and local computation; no routine model cost. Occasional cheap summarization only when presenting several conflicts to the owner.  ·  latency: Asynchronous (<100 ms local evaluation); conflict status may lag a heartbeat by one polling interval.
- security: Safer by default: exposes only capability-state metadata and timestamps, not page contents or audio. Conflict records must inherit the stricter retention policy of their sources.
- depends on: A typed observation envelope with source, timestamp, confidence, and freshness; GET /observe, GET /ops/status, GET /browser/status, GET /pipeline, and device-registration events; Downstream jobs understanding an explicit unresolved/reality-conflict state


## What it asked for

_Nothing._
## Its own summary

Fresh perception pass complete. At 2026-08-07 13:02Z, the Mac bridge is online, but the agent cannot truthfully perform pixel/UI control: Accessibility and Screen Recording are false, inputReachability failed, and computer-use is disabled/unconsented. Browser extension is offline with 7 pending commands; no pendant is registered. I recorded these facts, notified mac-vision and faculty-judgement, and proposed a perception-backed action-trust barrier so UI receipts cannot be mistaken for real effects. I also recorded that historical 24 kHz audio exists but is not evidence of a live pendant.

**Biggest unknown:** Whether the owner will manually grant Accessibility + Screen Recording to the exact AI Pendant Agent binary, bring the browser extension online, and physically connect/register a pendant. Until then, only AppleScript/automation-backed Mac work and relay-side state inspection are honestly reachable; UI actions and pendant delivery are not.

