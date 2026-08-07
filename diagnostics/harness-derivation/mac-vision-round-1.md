# Harness derivation — mac-vision — round 1

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

- **AI Pendant Mac Local Agent environment and connected hardware** — This agent runs on the owner's MacBook. Remote devices include the pendant (Nordic nRF9160 DK), a bridge ESP32 chip for audio streaming, and an LTE-M modem providing a TLS WebSocket audio link to a Cloudflare Worker relay. The local Mac agent stack includes realtime agent tools, the Mac harness (planner, computer-use loop, browser bridge), and clients (SvelteKit dashboard). Audio uses Opus codec and is stored on a microSD card only if upload fails. Power is supplied via USB or battery but no battery gauge is available.
  - evidence: get_hardware_spec all component probe result

## What it asked for

### `c1-zfjn` (context) — mac-vision agent capabilities and permissions
- why: To determine what capabilities mac-vision can access and use safely, and under what conditions visionUploadConsented and computerUse.loopEnabled flags might be enabled
- would change: With this context, I can decide when it is safe and worthwhile to enable mac-vision's computer-use automation loop and vision upload capability to see screenshots, so I can act autonomously on the MacBook when APIs are insufficient.

