# Harness derivation — mac-vision — round 4

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

- **mac-vision environment and capabilities** — The mac-vision agent runs on the owner's MacBook Air (hostname: MacBook-Air-6.local) and has full accessibility permissions. The computerUse loop is currently disabled, and vision upload is not consented. The system has screen recording and automation permissions granted for many apps including Terminal, Safari, and AI Pendant Agent. The agent knows about the attached AI Pendant device, its hardware specs, and relay/cloud setup, but cannot control the computerUse loop yet.
  - evidence: /ops/status and hardware spec probe responses showing fullControlMode true, loopEnabled false, visionUploadConsented false, accessibility and screen recording permissions granted, and detailed pendant and network hardware specs.

## What it asked for

### `c2-q8vo` (context) — active applications and UI state on MacBook
- why: To understand which apps and UI elements are currently accessible and visible to the mac-vision agent in order to plan subsequent screen actions safely and effectively.
- would change: This information would allow me to decide which UI components to interact with, ensure I do not interfere with critical workflows, and determine if I can enable computerUse loop safely.

### `t2-v86g` (tool) — computer_vision.screenshot
- why: To analyze the current screen state and determine if enabling the computerUse loop is safe and feasible, and to decide next UI actions.

```json
{
  "resolution": {
    "type": "string",
    "enum": [
      "full_hd",
      "retina_5k",
      "quad_hd"
    ]
  }
}
```

