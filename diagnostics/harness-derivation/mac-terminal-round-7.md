# Harness derivation — mac-terminal — round 7

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local-agent HTTP service** — GET /health returns service AI Pendant Mac Local Agent version 0.5.0. GET /jobs is exposed and returns completed job records including command text, action results, browser page metadata, and an account email visible in snapshot; this is sensitive observability data and should be access-controlled/redacted in migration.
  - evidence: probe_http GET /health => {ok:true,service:'AI Pendant Mac Local Agent',version:'0.5.0'}; GET /jobs => 200 with job local_... and browser snapshot containing Google Account: Evan Liu (evan20050827@gmail.com).
- **Job API behavior** — GET /jobs accepts limit=1 but still returned a very large full browser snapshot; individual /jobs/:id, /metrics, OpenAPI and Swagger discovery endpoints are absent (404). The list endpoint is therefore both an observability source and a potential data-leak surface.
  - evidence: probe_http GET /jobs?limit=1 => 200 with full action/browser element payload; GET /jobs/local_... => 404; GET /metrics, /openapi.json, /swagger.json => 404.

## What it asked for

### `t9-2kln` (tool) — mac_readonly_diagnostics_impl
- why: The granted safe_mac_command and mac_readonly_diagnostics interfaces are present but return 'no implementation yet', so I cannot verify cwd inheritance, timeout behavior, host OS, storage, battery, or network state needed to assess argv migration compatibility. I need a read-only diagnostic path only; no mutation or arbitrary shell.

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "enum": [
        "pwd",
        "sw_vers",
        "system_profiler SPSoftwareDataType",
        "df -h",
        "pmset -g batt",
        "scutil --nwi",
        "ps -axo pid,ppid,comm,args",
        "whoami"
      ]
    },
    "timeout": {
      "type": "integer",
      "minimum": 1,
      "maximum": 30
    }
  },
  "required": [
    "command"
  ]
}
```

### `c8-exdn` (context) — Mac shell compatibility workflow inventory
- why: The migration needs to preserve existing behavior while replacing arbitrary command strings with argv capability classes. I know four examples (pmset -g batt, scutil --nwi, system_profiler SPAirPortDataType, osascript volume), but not whether other commands, pipelines, cwd assumptions, or long-running jobs are relied upon.
- would change: If given the actual command corpus and cwd/timeout patterns, I can classify which workflows fit fixed argv capabilities, which require explicit compatibility-shell mode, and which need streaming/cancellation or recovery semantics.

