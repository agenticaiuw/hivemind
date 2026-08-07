# Harness derivation — mac-terminal — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent identity** — HTTP health endpoint identifies service as AI Pendant Mac Local Agent version 0.5.0.
  - evidence: GET /health returned HTTP 200 {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0"}.
- **Browser bridge availability** — Safari extension is online at version 1.2.0 with zero tabs; home-chrome stub is online; no pending browser commands.
  - evidence: GET /browser/status returned online:true, Safari device tabCount:0 extensionVersion:1.2.0 and home-chrome online:true, pendingCommands:0.
- **Browser polling** — Browser polling endpoint is reachable and currently has no work.
  - evidence: GET /browser/poll returned HTTP 204 with empty body.
- **HTTP route discovery** — No public root/status/capabilities/computer/shell/info/metrics/routes/openapi GET endpoints were found; unsupported routes return Express Cannot GET 404.
  - evidence: Parallel GET probes returned 404 for /, /status, /capabilities, /computer/status, /shell/status, /info, /metrics, /routes, /openapi.json.
- **Shell capability risk** — Mac harness exposes arbitrary shell execution with full control, unrestricted network and filesystem/cwd, and no separate audit log; only read-only status allowlist bypasses owner confirmation.
  - evidence: Environment/developer-provided local-agent description.
- **Mac agent architecture** — The Mac harness is a Node local agent containing planner, computer-use loop, browser bridge, action risk scoring, atomic JSON store, and context graph; it polls Cloudflare Worker /v1/bridge/work for jobs and posts results.
  - evidence: get_hardware_spec(component:'stack') returned mac_harness and relay architecture details.

## What it asked for

### `c1-61rq` (context) — Mac shell intended workload and current read-only allowlist
- why: To design the smallest safe replacement for arbitrary run_shell, I need to know which concrete Mac tasks the planner must support and which status commands are currently allowed unattended.
- would change: I will map each required task to typed operations and decide which, if any, read-only operations can remain unattended; all other capabilities would be denied or owner-confirmed.

## Its own summary

Discovered and recorded: local HTTP service is AI Pendant Mac Local Agent v0.5.0 (/health 200); browser bridge status shows Safari extension v1.2.0 online with 0 tabs, home-chrome stub online, and no pending commands; /browser/poll is reachable and idle (204). Common discovery endpoints (/status, /capabilities, /computer/status, /shell/status, /routes, /openapi.json, etc.) are absent (404). Architecture from hardware spec: Node Mac harness includes planner, computer-use loop, browser bridge, risk scoring, atomic JSON store/context graph, and polls Worker /v1/bridge/work. Critical security finding: arbitrary run_shell with full control, unrestricted filesystem/cwd/network, no sandbox and no separate audit log is too broad even with confirmation gating. Replace it with deny-by-default typed operations (process/status, bounded file read/write in an approved workspace, explicit app launch/quit, narrowly scoped network fetch), parameter validation, sandboxed helper, fixed cwd, OS account/container restrictions, egress allowlist, secret-store/browser-cookie/SSH-key/device-node/system-config denial, resource/time limits, and immutable audit records. Never expose arbitrary shell, eval/interpreter chains, sudo, credential stores, cookies, SSH keys, launchd/system settings, destructive disk commands, or unrestricted network to planner/voice routing. Shared findings with mac-planner, browser-extension, and relay-realtime. Requested orchestrator context on intended Mac workload and current unattended allowlist.

**Biggest unknown:** The exact required Mac task set and current read-only status allowlist are not discoverable from exposed HTTP routes; orchestrator context is needed to choose the minimum typed operation set and unattended policy.

