# Harness derivation — mac-planner — round 7

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent health** — Local agent is AI Pendant Mac Local Agent version 0.5.0 and /health returns ok.
  - evidence: GET http://127.0.0.1:8000/health returned HTTP 200 with {ok:true,service:'AI Pendant Mac Local Agent',version:'0.5.0'}.
- **Mac planner behavior** — POST /plan accepts free-form commands and returns status ready, typed action plans, jobId, and fullControl=true; plans are marked requiresConfirmation=true even though the granted context says actual FULL_CONTROL_MODE execution bypasses confirmation.
  - evidence: POST /plan for 'list files in home directory' returned list_directory path /Users/evanliu, jobId, requiresConfirmation:true, fullControl:true. POST /plan for system status returned run_shell plan.
- **Mac identity** — The planner resolved the local home directory as /Users/evanliu.
  - evidence: POST /plan 'list files in home directory' returned params.path '/Users/evanliu'.
- **Discoverable read-only Mac plans** — Planner can produce list_directory for /Applications, browser_list_tabs(limit), run_shell via osascript to list running/foreground apps, and run_applescript plus ui_snapshot(maxElements) for accessibility inspection.
  - evidence: Four POST /plan probes returned these exact action types and parameters.
- **Browser integration planning** — The local planner recognizes browser_list_tabs as a typed action with limit parameter; this is distinct from the browser-extension report that Safari extension is online but has zero tabs and enqueue implementation errors.
  - evidence: POST /plan 'check Safari tabs and browser status' returned browser_list_tabs {limit:50}; browser-extension peer reported tabCount=0/tabId=null.

## What it asked for

### `t5-prur` (tool) — mac_readonly_inspect
- why: I need to report actual Mac environment state (running apps, foreground app, accessibility permission/UI snapshot, browser tabs, and directory listings) without using the side-effect-capable executor or arbitrary shell. The existing mac_run_actions tool cannot perform these typed read-only inspections.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "running_apps",
        "foreground_app",
        "accessibility_enabled",
        "ui_snapshot",
        "browser_tabs",
        "list_directory"
      ]
    },
    "path": {
      "type": "string",
      "description": "Required only for list_directory; must be an approved absolute path such as /Applications or /Users/evanliu."
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 200
    },
    "max_elements": {
      "type": "integer",
      "minimum": 1,
      "maximum": 500
    }
  },
  "required": [
    "operation"
  ],
  "additionalProperties": false
}
```

## Its own summary

Reconnaissance established the Mac local agent identity and planner contract: localhost:8000 health is AI Pendant Mac Local Agent v0.5.0; /plan accepts free-form commands and emits typed plans (list_directory, run_shell, run_applescript, ui_snapshot, browser_list_tabs), resolves the home directory as /Users/evanliu, and reports fullControl=true. I also confirmed the planner can generate read-only inspection plans for apps, accessibility, and browser tabs, but did not execute them. I informed mac-vision and relay-realtime of these findings and requested a narrowly scoped read-only inspection tool to obtain actual state without arbitrary shell or side effects.

**Biggest unknown:** Actual current running/foreground apps, accessibility permission and UI snapshot, installed applications, and browser tabs remain unknown because the available reconnaissance interface only plans actions and the side-effect-capable executor does not expose typed read-only inspection.

