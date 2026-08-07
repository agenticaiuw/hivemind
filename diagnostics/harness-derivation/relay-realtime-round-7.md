# Harness derivation — relay-realtime — round 7

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **relay service and bridge status** — Cloud relay is healthy (version 1.1.0) and the Mac bridge is online; relay API key and speech-to-text are configured.
  - evidence: GET /health returned service AI Pendant Cloud Relay v1.1.0 with macBridgeOnline=true, relayApiKeyConfigured=true, speechToTextConfigured=true.
- **devices currently online** — Home MacBook Bridge device is online; a separate mobile test device is offline.
  - evidence: GET /v1/devices/status returned devices list with home-macbook-bridge online=true and cloudflare-contract-test online=false.
- **latest voice pipeline state** — Latest voice pipeline job is completed; no active run indicated by this endpoint.
  - evidence: GET /v1/ops/voice-runs/latest returned status completed for pipelineId job_f57a9331-2c6a-4cab-81b0-3c44b6d3cf6a.
- **agent tool inventory (from stack spec)** — Stack spec says realtime agent has exactly five tools today: get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate.
  - evidence: get_hardware_spec(component='stack') returned agent_tools_today listing those five tool names.

## What it asked for

### `c5-kzfn` (context) — Relay intent contract and supported intents/context fields
- why: I can route user requests via relay_route_intent, but I do not have a definitive list of supported intent labels, required context fields, or validation rules. Without this, I risk misrouting or sending malformed requests to mac-planner/mac-vision.
- would change: With a contract, I will normalize utterances into allowed intent labels, populate required context fields, and choose between mac-planner and mac-vision safely. Without it, I must treat routing as best-effort and prefer asking clarifying questions.

## Its own summary

Relay is healthy and configured; Mac bridge is online. I can see device status and latest voice run status. Stack spec says the realtime agent has five tools today and web tasks may be able to run server-side in the future. I informed mac-planner of bridge status and asked for their intent/context expectations.

**Biggest unknown:** I still lack a concrete relay intent routing contract: the allowed intent labels, required context fields, and validation rules for relay_route_intent and downstream agents.

