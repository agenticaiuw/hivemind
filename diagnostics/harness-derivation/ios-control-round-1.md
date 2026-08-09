# Harness derivation — ios-control — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac Local Agent v0.5.0 is reachable at localhost:8000; authenticated routes use bearer token and /health is public. It exposes 223 routes and full-control planner/computer-use support.
  - evidence: GET /health returned service/version; GET /capabilities returned routeCount=223 and auth contract.
- **live-mac-state** — Mac automation is currently live and verifiable: Accessibility, Screen Recording, synthesized input, and computer-use loop are ready; Safari browser bridge is online with 2 tabs and 0 pending commands.
  - evidence: GET /ops/snapshot and GET /observe at 2026-08-09T01:50Z reported permissions.ready=true, inputReachability=verified, browser.online=true.
- **reachable-devices** — Discovered reachable devices are Safari on MacIntel (2 tabs), home-macbook-bridge (online), and cloudflare-contract-test (offline). No physical pendant or iPhone device appears in the devices discovery list, although iPhone Mirroring is a running Mac application.
  - evidence: discover(devices) returned exactly those three items; GET /observe listed iPhone Mirroring among running apps.
- **relay-audio** — Relay is configured/reachable and supports pendant speech, durable audio, and persistent state, but current pipeline delivery evidence proves only relay acceptance, not pendant playback; no pendant telemetry is present.
  - evidence: GET /ops/snapshot relay payload reported reachable/D1 and pairingRequired; GET /pipeline showed delivery state held_by_relay, awaitsDevice=true, provesPlayback=false/heard=unknown.
- **owner-context** — Owner permits browser reading/clicking without asking, allows reminders/notes, requires confirmation before destructive actions (sending mail, deleting files, buying), prefers one short spoken sentence, and wants end-to-end 24 kHz pendant audio. Remembered timezone America/Chicago is explicitly sampled/not stated and conflicts with live machine timezone America/New_York.
  - evidence: discover(owner) returned remembered policy and goal; GET /machine-context reported timezone America/New_York.
- **ios-capability-discovery** — The shipped production tools surfaced are get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate, read_web_page, and relay_job_status; no dedicated ios tool was surfaced in tools discovery. Exact ios_* action schema remains unknown.
  - evidence: discover(tools) returned 7 items and none were ios-specific; route listing was Mac-agent routes only.

## What it asked for

### `c1-ckl5` (context) — meaning of independent iOS node
- why: I can reach only the Mac-local agent; iPhone Mirroring capture/events are physically Mac-local, while no iPhone device is registered in discovery. I need the intended boundary for calling this facet an independent node.
- would change: If independence means separate relay-addressable identity, I will propose a relay job/receipt channel while keeping capture and input execution on Mac. If it means a deployable iOS service, I will identify required pairing, transport, and permissions instead of pretending the current facet is independent.

### `t1-17sj` (tool) — ios_mirroring_inspect
- why: Future owner requests include reading/controlling the real iPhone, but tools discovery exposes no iOS-specific tool and the generic Mac action schema does not document ios_* operations. A read-only inspect capability is needed to safely determine mirroring/window state before any frontmost-only interaction.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "status",
        "capture",
        "ocr",
        "home"
      ]
    },
    "windowId": {
      "type": "string",
      "description": "Optional iPhone Mirroring window identifier when known"
    },
    "includeVision": {
      "type": "boolean",
      "description": "For capture, whether to return a vision/OCR representation"
    }
  },
  "required": [
    "operation"
  ]
}
```

### `t2-ksiv` (tool) — propose_capability
- why: The user explicitly requires recording a new owner-facing capability, but propose_capability/propose_change are not present in the currently exposed tool manifest. I need the recorder itself, not a replacement text response.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string"
    },
    "owner_can_have": {
      "type": "string"
    },
    "today_gap": {
      "type": "string"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "novelty_boundary": {
      "type": "string"
    }
  },
  "required": [
    "title",
    "owner_can_have",
    "today_gap",
    "required_changes",
    "novelty_boundary"
  ]
}
```

## Its own summary

Environment established. I run as ios-control, a facet of mac-planner on the owner's MacBook—not a physically independent iPhone or relay process. Mac Agent v0.5.0 is live at localhost:8000 with bearer-authenticated routes, full-control/computer-use enabled, Accessibility + Screen Recording + synthesized input verified, and Safari bridge online (2 tabs, 0 pending). The relay is reachable/D1-backed and supports durable audio, but no pendant is registered/telemetry is present; current audio evidence proves relay acceptance only, not playback. Device discovery exposes Safari, the Mac bridge, and an offline contract-test mobile device; iPhone Mirroring is merely a running Mac app, with no iPhone identity or ios_* schema surfaced. Owner policy: browser read/click is allowed, reminders/notes can be created, destructive actions require confirmation, spoken replies should be short; the stated 24-kHz pendant audio goal remains relevant. I recorded these findings, notified mac-planner, requested context defining 'independent node,' and requested a read-only ios_mirroring_inspect capability. Practical meaning: independence can only be a relay-addressable identity/job/receipt boundary while capture and event posting stay Mac-local; it improves routing and observability, not physical autonomy.

**Biggest unknown:** The exact ios_* action registry and the intended relay contract for an 'independent' iOS node are not discoverable from the surfaced tools/routes. Until supplied, I cannot safely perform or claim iPhone reads/taps/typing/swipes; I also cannot infer iPhone presence from the Mirroring app process alone.

