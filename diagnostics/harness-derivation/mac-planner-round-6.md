# Harness derivation — mac-planner — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **local-agent-health** — The Mac local agent is reachable at 127.0.0.1:8000 and reports service AI Pendant Mac Local Agent version 0.5.0.
  - evidence: GET /health returned HTTP 200: {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0"}
- **local-agent-routes** — Only /health is confirmed public; root, /openapi.json, and /v1/bridge/work return 404 via GET.
  - evidence: GET probes returned HTTP 404 Cannot GET for each path.
- **remote-device-boundary** — Hardware inventory confirms pendant storage is remote microSD failure buffer; it is not local Mac storage. Relay has five tools including get_mac_status, mac_run_actions, browser_run_actions, web_search, and mac_delegate.
  - evidence: get_hardware_spec(stack) and get_hardware_spec(storage) responses explicitly state I run on MacBook and other devices are remote.

## What it asked for

### `p3-7rew` (permission) — probe:post:/plan
- why: Need to inspect the local agent's planning responses and supported action schemas without executing desktop side effects.
- risk it sees: Planning requests could potentially be interpreted as commands if the endpoint is misconfigured, though /plan is expected to be read-only.

### `c3-xmfd` (context) — Mac action authorization and confirmation policy
- why: The local agent is in FULL_CONTROL_MODE and /execute can perform arbitrary shell/AppleScript plus destructive file/app actions; I need the owner's policy for when to plan versus execute and what confirmation token/approval flow is required.
- would change: I would avoid executing high-impact actions without approval, route safe actions directly, and distinguish preview/dry-run from committed desktop changes.

## Its own summary

Confirmed local agent health (v0.5.0) and remote-device boundary. Only /health is publicly GET-accessible; root, /status, /capabilities, /openapi.json, /healthz, and /v1/bridge/work return 404. The known Mac action contract supports app/URL/path/file/keyboard/mouse/UI accessibility/browser/audio/reminder/note/search actions; FULL_CONTROL_MODE routes execution through computerControl.js. Requested permission to probe POST /plan and requested owner authorization/confirmation policy. Asked mac-vision, mac-terminal, and relay-realtime for their inventories and bridge/intent details.

**Biggest unknown:** The actual /plan response/action schema and the policy/approval mechanism for committing high-impact Mac actions remain unknown; peer reports about current apps, accessibility, shell, and relay intents are also pending.

