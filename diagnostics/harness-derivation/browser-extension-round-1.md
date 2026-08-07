# Harness derivation — browser-extension — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Browser bridge status** — GET /browser/status reports online=true with one registered device: Safari on MacIntel, Safari 26.5.2, extension v1.2.0, tabCount 0, no active tab, pendingCommands 0. The stub home-chrome is not returned by this live status response.
  - evidence: GET /browser/status -> 200 {online:true, devices:[{browserName:'Safari', extensionVersion:'1.2.0', tabCount:0, online:true}], pendingCommands:0}
- **Local agent service** — Root health endpoint identifies service as AI Pendant Mac Local Agent version 0.5.0.
  - evidence: GET /health -> 200 {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0'}
- **Registered browser devices** — Trailing-slash GET /browser/status/ returns two online registrations: real Safari extension with no tabs, and home-chrome stub with null tabCount and no browser metadata. No pending commands.
  - evidence: GET /browser/status/ -> 200 devices=[Safari on MacIntel tabCount:0 online:true, home-chrome tabCount:null online:true], pendingCommands:0

## What it asked for

### `c1-o3q8` (context) — Browser command enqueue API
- why: The bridge exposes GET /browser/poll and POST /browser/result/:commandId, but reconnaissance has not revealed how an agent enqueues commands for the extension or the command JSON schema.
- would change: I can use the browser safely and concretely (read tabs, navigate, extract page content) only after knowing the enqueue endpoint and supported command types; otherwise I can only report status.

### `t1-500f` (tool) — browser_enqueue_command
- why: The only exposed browser interaction currently available to this agent is status/poll observation; useful work requires submitting a command to the extension queue so Safari can navigate, inspect tabs, click, type, or extract page content.

```json
{
  "type": "object",
  "properties": {
    "deviceId": {
      "type": "string",
      "description": "Optional extensionId/device identifier; omit to target the live real Safari device."
    },
    "command": {
      "type": "string",
      "enum": [
        "list_tabs",
        "get_active_tab",
        "navigate",
        "extract_page",
        "click",
        "type",
        "key"
      ],
      "description": "Browser operation."
    },
    "url": {
      "type": "string",
      "description": "Required for navigate."
    },
    "selector": {
      "type": "string",
      "description": "Required for click/type."
    },
    "text": {
      "type": "string",
      "description": "Required for type."
    },
    "key": {
      "type": "string",
      "description": "Required for key."
    }
  },
  "required": [
    "command"
  ]
}
```

## Its own summary

Reconnaissance complete: the local backend identifies as AI Pendant Mac Local Agent v0.5.0 (/health). Browser status is available at /browser/status/; it reports two online registrations: real Safari on MacIntel (Safari 26.5.2, extension v1.2.0, 0 tabs/no active tab) and a home-chrome stub (null tabCount, no metadata). /browser/poll and /browser/poll/ return 204 with no queued commands; pendingCommands is 0. I recorded and relayed these facts to mac-planner and all agents. I requested orchestrator context for the command enqueue API/schema and requested a browser_enqueue_command capability.

**Biggest unknown:** How commands are enqueued and the exact supported command/result JSON schema; without that I cannot read or operate logged-in pages.

