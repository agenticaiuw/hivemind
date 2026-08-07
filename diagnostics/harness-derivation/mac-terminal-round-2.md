# Harness derivation — mac-terminal — round 2

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **local-agent HTTP service** — Root and common introspection routes are absent; /health returns service identity AI Pendant Mac Local Agent version 0.5.0.
  - evidence: GET /health -> 200 {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0"}; GET /, /api, /status, /info, /capabilities, /routes, /openapi.json all returned 404.
- **system architecture and my location** — I run on owner's MacBook as mac-terminal; local agent polls Cloudflare Worker /v1/bridge/work. Realtime relay has exactly five tools, including mac status/actions/delegate and browser tools. Shared dashboard spans web, Swift menubar WKWebView, and iOS Capacitor. Cloudflare Browser Run may remove Mac from web tasks.
  - evidence: get_hardware_spec(stack) returned relay/local-agent architecture, tool inventory, and 'you are here' MacBook location.
- **bridge endpoint exposure** — No GET endpoints were found at /v1/health, /v1/bridge, /v1/bridge/health, or /v1/status; only /health is confirmed.
  - evidence: Each GET returned 404 Cannot GET response.

## What it asked for

### `t2-c09x` (tool) — safe_mac_command
- why: Current run_shell executes arbitrary shell unattended because FULL_CONTROL_MODE bypasses actionRisk. Useful Mac work needs narrowly scoped read-only diagnostics and explicitly confirmed mutations without shell injection or unrestricted filesystem/network access.

```json
{
  "operation": "string enum: [system_info, process_list, disk_usage, file_stat, read_text, list_directory, git_status]",
  "path": "optional string, must be under approved roots for file operations",
  "args": "optional object with operation-specific typed fields; no raw command string",
  "timeout_ms": "optional integer, max 10000",
  "approval_token": "required for any non-read-only operation"
}
```

### `c2-1w00` (context) — approved Mac shell use cases and trust boundary
- why: To design the smallest safe replacement for arbitrary unattended run_shell, I need to know which concrete Mac operations are actually required and which data locations/apps are in scope.
- would change: I would turn each required use case into a typed allowlisted operation and deny all other filesystem, process, UI, interpreter, and network access; without this I can only recommend a conservative read-only default.

## Its own summary

Confirmed local service identity (/health => AI Pendant Mac Local Agent v0.5.0); common introspection/bridge routes all 404. Stack spec establishes Mac agent polls Cloudflare Worker and relay has server-side browser option. Communicated to mac-planner and relay that FULL_CONTROL_MODE makes arbitrary unattended shell unsafe, and requested a typed safe_mac_command replacement plus context on approved Mac use cases. Recommended default-deny filesystem/process/network/interpreter access, typed argv, approval tokens for mutations, resource limits and audit logs.

**Biggest unknown:** The concrete owner-approved Mac workloads and filesystem/apps that must remain supported; this determines the minimal allowlist and sandbox roots.

