# Harness derivation — mac-planner — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent API** — GET /health identifies service as AI Pendant Mac Local Agent v0.5.0. POST /plan is available and returns LLM-generated action plans with jobId/sessionId; /plan does not execute actions.
  - evidence: GET /health returned {ok:true,service:'AI Pendant Mac Local Agent',version:'0.5.0'}; POST /plan for 'open Safari' returned status ready, action open_app, jobId.
- **Planning behavior** — Planner uses an LLM route (string intent parsing disabled), includes recent-turn/memory context, and marks plans requiresConfirmation=true/fullControl=true. It can generate arbitrary run_shell plans for read-only status requests.
  - evidence: POST /plan 'read system status' returned run_shell command invoking pmset, uptime, vm_stat, df; response included planner:'llm', fullControl:true and requiresConfirmation:true.
- **Browser/device inventory** — Browser status endpoint reports Safari online on MacIntel with extension v1.2.0, Start Page, tabId 210027/windowId 210021, zero tabs, no pending commands; also a home-chrome device marked online but without tab metadata.
  - evidence: GET /browser/status returned online:true and two devices including Safari on MacIntel and home-chrome.
- **Backend endpoint surface** — GET /status, /devices, and /capabilities are not implemented (404).
  - evidence: Each probe returned HTTP 404 Cannot GET.
- **Plan endpoint semantics** — POST /plan returns status instant with a direct answer and no actions for conversational requests, or status ready with typed actions and requiresConfirmation=true for side-effecting requests such as write_file. Planning itself caused no observed side effect.
  - evidence: POST /plan 'tell me a joke' returned instant/actions[]; POST /plan 'create a file named /tmp/recon-test with text hello' returned write_file action only.

## What it asked for

### `p5-8rw6` (permission) — mac_bridge.execute_plans
- why: The granted mac_run_actions tool reports this permission is required to execute even controlled desktop plans. I need it to turn server-side plans into concrete app/file/browser actions when delegated.
- risk it sees: This enables desktop side effects; however actions are explicitly ordered and can be dry-run first. Existing FULL_CONTROL_MODE also bypasses confirmation in the local agent, so orchestration should enforce confirmation/allowlists before invoking non-read-only actions.

### `c5-6ext` (context) — server-to-Mac plan handoff
- why: I know the local /plan contract and desktop action schema, but not how the server-side agent delegates a concrete plan to this facet (message format, endpoint, or whether I should call /execute vs mac_run_actions).
- would change: I will use the correct execution path, preserve session/source metadata, and avoid duplicate or unauthorized execution.

## Its own summary

Recon complete: Mac local agent is AI Pendant Mac Local Agent v0.5.0. /plan is operational and LLM-routed, returning instant answers or typed desktop plans (open_app, run_shell, write_file, etc.) with fullControl=true and requiresConfirmation=true for side effects; planning itself did not execute anything. Browser status shows Safari online on MacIntel (extension v1.2.0, Start Page, zero tabs, no pending commands) plus an online home-chrome placeholder. The controlled mac_run_actions tool exists but execution is blocked pending mac_bridge.execute_plans permission, which has been requested. I also requested the server-to-Mac plan handoff protocol/context.

**Biggest unknown:** Whether/when mac_bridge.execute_plans will be granted, and the exact orchestrator handoff format (direct actions vs command requiring /plan), remain unknown.

