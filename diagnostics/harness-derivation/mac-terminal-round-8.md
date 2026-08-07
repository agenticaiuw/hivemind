# Harness derivation — mac-terminal — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **local-agent HTTP surface** — GET /health reports AI Pendant Mac Local Agent version 0.5.0. GET /jobs and /logs expose completed harness jobs and detailed browser snapshots; GET /browser/status reports one online Safari-on-MacIntel extension device (extension v1.2.0), pendingCommands 0, tabCount currently 0 in bridge status. A prior job snapshot observed Safari title 'Voyager 1 probe - Google Search' at Google, indicating job/browser state can be richer than status summary.
  - evidence: probe_http GET /health, /jobs, /logs, /browser/status
- **Mac host baseline** — Previously established host is /Users/evanliu/agentic-gadget on branch main; home /Users/evanliu; hostname MacBook-Air-6.local; arm64 Darwin macOS 26.5.2. Shell commands run unrestricted with FULL_CONTROL_MODE and 120s default timeout; no authorization gate, environment/network/cwd restriction, or separate audit log.
  - evidence: granted context from orchestrator (compatibility workflow inventory and shell policy)
- **diagnostics tool availability** — Granted mac_read_diagnostics and mac_readonly_diagnostics interfaces are nonfunctional in this harness, each returning 'This tool was granted a schema but has no implementation yet.' Therefore current host reconnaissance relies on prior orchestrator-provided facts and HTTP probes.
  - evidence: Four parallel diagnostic calls in Round 8 returned the no-implementation error.

## What it asked for

### `c14-ssvm` (context) — Mac local-agent route and job lifecycle contract
- why: I can see /health, /jobs, /logs, and /browser/status, but not the authoritative POST route/schema that mac-planner uses to submit shell jobs or how job IDs map to audit records. This is needed to assess observability, retries, and failure recovery without guessing.
- would change: I would document the exact invocation and recommend targeted observability/recovery improvements (structured argv/cwd/env capture, exit status/stderr, cancellation and retry semantics) rather than speculative endpoint probing.

### `t14-ntgq` (tool) — mac_readonly_probe
- why: The granted diagnostics interfaces are present but return 'no implementation yet'. Shell-tier reconnaissance and routing need bounded, read-only host facts without relying on unavailable arbitrary shell. A single fixed-query tool would make status checks reliable.

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "enum": [
        "identity",
        "os",
        "hardware",
        "battery",
        "network",
        "disk",
        "processes",
        "audio",
        "displays",
        "permissions",
        "agent_routes"
      ]
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 30
    }
  },
  "required": [
    "query",
    "timeout_seconds"
  ],
  "additionalProperties": false
}
```

## Its own summary

Round 8 reconnaissance: confirmed local agent /health (AI Pendant Mac Local Agent v0.5.0), /jobs and /logs (completed browser_snapshot job plus detailed audit records), and /browser/status (one online Safari bridge, extension v1.2.0, pendingCommands 0). Recorded host baseline and shell policy. Diagnostics grants are nonfunctional ('no implementation yet'); requested a concrete bounded mac_readonly_probe tool and requested the authoritative shell-job route/lifecycle contract from orchestrator. Shared browser/host findings with mac-vision and asked other agents for routing context.

**Biggest unknown:** Exact POST submission schema and lifecycle for shell/computer jobs, including whether logs capture command argv/cwd/environment, exit status/stderr, cancellation, retries, and correlation IDs; also reliable implementation of read-only diagnostics.

