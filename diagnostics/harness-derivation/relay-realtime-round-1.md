# Harness derivation — relay-realtime — round 1

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **service** — This agent is connected to the AI Pendant Cloud Relay service running on cloudflare-workers, version 1.1.0.
  - evidence: GET / returned service=AI Pendant Cloud Relay, version=1.1.0, platform=cloudflare-workers.
- **configuration** — Relay API key and speech-to-text are configured.
  - evidence: GET / returned relayApiKeyConfigured=true and speechToTextConfigured=true.
- **pairing** — Pairing is required for operation.
  - evidence: GET / returned pairingRequired=true.
- **mac bridge** — A Mac bridge appears online and was recently seen.
  - evidence: GET / returned macBridgeOnline=true and macBridgeLastSeen=2026-08-07T04:45:57.572Z.
- **capabilities** — Supported capabilities include pendant pipeline telemetry, pendant speech, persistent agent state, and durable audio.
  - evidence: GET / returned capabilities.pendantPipelineTelemetry=true, pendantSpeech=true, persistentAgentState=true, durableAudio=true.
- **models** — Configured models include voiceAgent gpt-realtime-2.1, textToSpeech via macOS say, and relay fallback tts-1 alloy.
  - evidence: GET / returned models.voiceAgent=gpt-realtime-2.1, textToSpeech=macOS say (24 kHz PCM), relayTextToSpeechFallback=tts-1 · alloy.
- **restrictions** — Routes /health, /capabilities, and /agents are blocked for this device by safety policy.
  - evidence: GET /health, GET /capabilities, and GET /agents all returned 403 Blocked for safety.

## What it asked for

### `p1-23pj` (permission) — GET /health, GET /capabilities, GET /agents
- why: These routes would reveal system health, what this relay is allowed to do, and which agents are available to coordinate with. That directly affects whether I answer locally, route to a peer, or ask for more context.
- risk it sees: Exposure of internal topology and permitted capabilities could reveal sensitive infrastructure details. Access should be limited to this agent and read-only.

### `c1-9fmj` (context) — current session pairing and owner state
- why: The relay indicates pairing is required, but I cannot see whether this pendant is paired, which owner profile is active, or what the current conversation/session state is. Without that, I can’t safely take actions or route requests.
- would change: If paired and an owner/session is active, I can handle spoken instructions and decide whether to answer directly or forward to mac-planner/mac-vision. If not paired, I should only guide the user through pairing or report that I’m unavailable.

### `t1-1tln` (tool) — relay_route_intent
- why: As a low-latency front door, I need a safe, explicit way to route recognized user intents to downstream agents (mac-planner/mac-vision) and receive status, without inventing my own protocol.

```json
{
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "description": "A concise intent label, e.g. 'search_web', 'open_app', 'dictation', 'system_status'."
    },
    "utterance": {
      "type": "string",
      "description": "The raw or normalized user utterance."
    },
    "context": {
      "type": "object",
      "description": "Optional session context such as locale, time, and any already-known constraints.",
      "additionalProperties": true
    },
    "target": {
      "type": "string",
      "description": "Preferred target agent id, e.g. 'mac-planner' or 'mac-vision'."
    }
  },
  "required": [
    "intent",
    "utterance",
    "target"
  ]
}
```

## Its own summary

Probed the root endpoint and confirmed this is the AI Pendant Cloud Relay on Cloudflare Workers (v1.1.0). Relay API key and speech-to-text are configured. Pairing is required. A Mac bridge appears online and recently seen. Capabilities include pendant speech, telemetry, persistent state, and durable audio. Model configuration includes gpt-realtime-2.1 and TTS paths. Attempts to access /health, /capabilities, and /agents were blocked (403) for this device. Recorded all findings.

**Biggest unknown:** Whether this session is paired and which owner/session is active; also the available agents/capabilities details are blocked without additional permission.

