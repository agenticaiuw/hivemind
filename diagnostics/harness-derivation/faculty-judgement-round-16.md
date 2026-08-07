# Harness derivation — faculty-judgement — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner task reachability** — The owner has repeatedly asked for Gmail, GitHub, calendar, and browser page access, and those requests were recorded as failed; a truthful availability/preflight layer is therefore more urgent than another task planner.
  - evidence: Owner projection lists read gmail, read github, read calendar, and browser page access under asked_for_and_did_not_get with got=failed.

## Capabilities it proposed

### "“Do this wherever you can, and if something is blocked, tell me exactly what I need to reconnect.”"
- **useful because:** The owner's real failures are not intent failures but silent reachability failures (mail, GitHub, calendar, browser access). A single request should be routed across pendant, relay, Mac, and authenticated browser, preflight each required session, use the strongest available path, and return a truthful partial-completion receipt instead of retrying or pretending.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-5.6-luna for planning and reconciliation; gpt-4.1-mini for deterministic UI extraction; gpt-realtime-2.1 only for the short spoken status and a confirmation gate.
- **latency:** Preflight under 2 seconds for cached session health; complete reversible reads in under 15 seconds; speak immediately if blocked, then continue asynchronously and post a receipt.
- **cost:** About $0.01–$0.06 per request, dominated by planner/reconciliation; health probes and receipts should be local/cheap, with no realtime call except the spoken interaction.
- **security:** Do not export page contents to the relay when Mac/browser can inspect locally. Never infer authentication from stale cache. Report which surface saw what, redact secrets, and require confirmation for sends, purchases, deletion, or external submission.
- **missing:** A typed cross-surface reachability/preflight contract (session, permission, freshness, and action scope); A router that can downgrade to read-only or draft-only paths and return per-step blockers; A user-facing reconnect action on pendant/dashboard that names the exact missing grant or browser session; Durable partial-completion receipts linked to the original request

### "“Stop everything you’re doing for me right now.”"
- **useful because:** A wearable assistant can start work on a Mac, browser, and relay and then outlive the conversation. The owner needs a reliable physical, voice, and dashboard kill switch that cancels queued and in-flight work, prevents a browser submission race, and tells them what was successfully stopped and what could not be interrupted.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No expensive model for cancellation; deterministic signed control messages and local abort handlers. Use gpt-4.1-mini only to summarize the resulting stop receipt if needed.
- **latency:** Physical button-to-stop acknowledgment under 500 ms locally; relay fan-out under 2 seconds; final per-job receipt under 10 seconds.
- **cost:** Under $0.005 per invocation; mostly durable event writes and cancellation fan-out, no model required.
- **security:** The stop command must be authenticated, replay-protected, and work offline on the pendant by silencing audio and refusing new execution until acknowledged. Cancellation must win races against send/submit operations; preserve an immutable audit receipt and never claim cancellation after an irreversible action has already completed.
- **missing:** A signed cross-surface cancellation protocol with job generations and idempotent abort semantics; Abort hooks in Mac, browser, and relay workers, including a pre-submit browser barrier; A pendant firmware kill/hold gesture and local execution lock; A concise cancellation receipt and post-stop re-enable flow

### "“Without asking, make it obvious whether you heard me, are working, are blocked, or are finished—and tell me what you need if blocked.”"
- **useful because:** Today a silent wearable and asynchronous Mac/browser work leave the owner guessing whether a request was heard, lost, still running, or failed. The owner should have a truthful, glanceable/haptic execution state that follows one request across every surface, survives a dropped conversation, and turns a blocker into a concrete next step rather than a dead end.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event/state aggregation for the state machine; gpt-4.1-mini only to compress a blocker into one spoken sentence; gpt-realtime-2.1 only when a live conversation is active.
- **latency:** Local heard acknowledgment under 300 ms; state transitions under 1 second; blocker explanation within 3 seconds; final receipt may arrive asynchronously.
- **cost:** Under $0.01 per request, primarily durable event storage and notification delivery; no model needed for normal transitions.
- **security:** Expose only coarse state and a redacted blocker on the pendant; never display private page content or secrets. Sign state transitions with request ID, surface, timestamp, and terminal outcome so a stale 'done' cannot mask a later failure. Quiet hours must suppress haptics but not erase the receipt.
- **missing:** A durable cross-surface execution state machine with monotonic request generations and terminal outcomes; Pendant firmware support for distinct acknowledgement/progress/blocked/done haptic patterns and an offline queued state; A shared event stream consumed by relay, Mac, browser, and dashboard; A concise blocker taxonomy mapped to actionable reconnect or approval instructions


## Changes it proposed to its own stack

### `hardware` — Add a deliberate three-position hardware control (OBSERVE / PREPARE / ACT) with a tactile detent and unmistakable haptic/LED indication, plus a signed mode beacon that every relay, Mac, and browser action handler must check immediately before execution. OBSERVE permits sensing and reading only; PREPARE permits drafts/forms but no external mutation; ACT permits previously approved reversible actions and still requires confirmation for destructive or external sends.
- **owner gets:** The owner can change the assistant's authority without finding a screen or remembering a setting—especially while walking, distracted, or handing the pendant to someone. The physical position makes “what can this thing do right now?” legible and prevents a stale voice instruction or queued job from acting later under the wrong level of trust.
- effort: High: revise enclosure and PCB input, firmware state machine, signed mode propagation, and action middleware on relay/Mac/browser; add end-to-end race tests and a boot-safe default.  ·  risk: A stuck or misread switch could unexpectedly restrict work or, worse, grant authority. Use fail-closed boot and disconnect defaults, debounce plus redundant ADC/GPIO read, visible/haptic acknowledgement, and require a fresh mode token at every irreversible boundary. Recovery is moving to OBSERVE and reconnecting.
- cost: Prototype hardware roughly $3–$10 BOM (sealed 3-position switch, haptic motor/driver, indicator); under 20 mW active incremental draw. No meaningful per-request API cost.  ·  latency: Under 100 ms local acknowledgement; mode-token validation adds under 10 ms per action.
- security: Substantially reduces confused-deputy and stale-queue risk, but creates a high-value control surface; authenticate mode tokens, prevent remote mode changes, and log every transition without logging private audio/content.
- depends on: A cross-surface signed command/job protocol; Action middleware with an irreversible-action barrier; A firmware update and enclosure redesign path


## What it asked for

### `t6-raqo` (tool) — cross_surface_preflight
- why: To fulfill the proposed truthful routing behavior, I need one cheap authoritative call that reports which surfaces can currently read, draft, or execute for a given job, rather than repeatedly invoking unavailable tools or claiming success.

```json
{
  "type": "object",
  "properties": {
    "intent": {
      "type": "string"
    },
    "required_scopes": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "read",
          "draft",
          "mutate",
          "destructive"
        ]
      }
    },
    "targets": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "pendant",
          "relay",
          "mac",
          "browser"
        ]
      }
    }
  },
  "required": [
    "intent"
  ]
}
```

## Its own summary

This round produced three new, non-overlapping pieces: (1) truthful cross-surface reachability preflight and fallback for the owner's repeatedly failed Gmail/GitHub/calendar/browser requests, (2) a universal pendant/Mac/browser/relay kill switch with race-safe cancellation receipts, and (3) a future pendant hardware authority dial OBSERVE/PREPARE/ACT enforced by signed mode tokens at every action boundary. I also recorded the observed failure pattern and queued a precise cross_surface_preflight tool request. To build these, I still need the orchestrator to decide on that tool, plus the signed job/cancellation protocol, action barriers, and (for the authority dial) a product hardware/enclosure path; I am not repeating the several context/permission requests already pending.

**Biggest unknown:** Whether the existing cross-surface job/event persistence and browser/Mac action layers expose cancellable job IDs and a final pre-submit barrier; without those, the kill switch can stop queued work but cannot honestly guarantee in-flight cancellation.

