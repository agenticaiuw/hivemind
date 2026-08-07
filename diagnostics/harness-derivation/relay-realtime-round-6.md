# Harness derivation — relay-realtime — round 6

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **device status visibility** — I can query /v1/devices/status and saw a mac_bridge device online (Home MacBook Bridge) and a mobile test device offline.
  - evidence: GET /v1/devices/status returned devices: home-macbook-bridge online=true; cloudflare-contract-test online=false.
- **voice pipeline state** — I can query the latest voice run and history, and the latest pipeline status was completed.
  - evidence: GET /v1/ops/voice-runs/latest returned latest.status=completed; history shows prior voice_command entries with replies and plan_ready/completed states.

## What it asked for

### `c4-c1a4` (context) — live_voice_ingestion_and_routing_contract
- why: As the low-latency front door, I need to know how recognized speech reaches me (ASR event format, partial vs final transcripts, timestamps, locale) and when I should answer directly versus route via relay_route_intent.
- would change: With this contract, I can avoid guessing. I will parse the provided transcript format, decide to respond locally for simple Q&A, or call relay_route_intent with the required fields and preferred target, and then report status back to the user.

## Its own summary

Probed available status endpoints. Confirmed I can read device status, latest voice run status, voice history, and memory. Found a Home MacBook Bridge device online. Recorded findings. Sent a message to mac-planner asking what intents it supports and what context it needs for routing. Requested orchestrator context for the live voice ingestion/routing contract so I don't invent protocol details.

**Biggest unknown:** I still lack the explicit contract for incoming ASR/transcript events and routing decisions (when to answer locally vs route, required fields, and context). I also don't yet know mac-planner's supported intents and readiness; that answer will arrive in a later round.

