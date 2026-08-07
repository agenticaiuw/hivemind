# Harness derivation — mac-vision — round 13

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Turn on mac-vision's accessibility-mode UI interaction loop to automate GUI tasks without taking over the screen or keyboard focus."
- **useful because:** This allows safe, non-intrusive automation and assistance with Mac GUI tasks using only accessibility APIs, respecting user control and multi-app workflows.
- **path:** mac-bridge → macbook
- **model tier:** background
- **latency:** seconds
- **cost:** low, mostly CPU on Mac side
- **security:** Requires explicit user opt-in and ongoing consent. Limited to accessibility API calls with no screen drawing or keystroke stealing allowed.
- **missing:** UI hierarchy snapshots from mac-planner to power the accessibility interaction model; Improved state and error handling for partial action states

### "Show me a history of recent actions taken by mac-vision in automation loops with human-readable explanations and option to undo."
- **useful because:** Provides transparent audit trail and accidental action recovery for better trust and control over autonomous UI interactions on the Mac.
- **path:** macbook → dashboard → pendant
- **model tier:** background
- **latency:** seconds
- **cost:** low storage and compute; mostly UI rendering cost.
- **security:** Secure handling of undo requires integration with the loop's action classification to only undo safe and reversible actions.
- **missing:** Unified action logging and undo framework across agents


## Changes it proposed to its own stack

### `integration` — Integrate mac-vision with the Cloudflare Worker relay to allow partial offloading of UI state classification and action suggestion to a cloud tier. This enables more powerful multimodal fusion with voice commands and history synthesis.
- **owner gets:** The owner's Mac GUI automation benefits from cloud-assisted intelligence without compromising privacy, improving responsiveness and context-awareness.
- effort: Medium  ·  risk: Data privacy requires end-to-end encryption and trust boundary clearly signed by the owner to avoid data leakage.
- cost: Moderate cloud compute and bandwidth costs, reduced Mac CPU load.  ·  latency: Minimal additional latency as cloud assists asynchronously with local prioritization.
- security: Requires careful design of authentication and data flow controls to avoid replay or man-in-the-middle attacks.
- depends on: mac-vision accessibility interaction mode; cloudflare relay enhancements

### `hardware` — Add a dedicated low-power vision coprocessor or embedded GPU to the pendant hardware for on-device image analysis to recognize Mac screen contents and UI elements, enabling offline partial vision-based UI control without Mac involvement.
- **owner gets:** Allows mac-vision features to run even if MacBook is asleep or disconnected, enhancing availability and responsiveness for common tasks without network latency or privacy risk.
- effort: High: requires hardware design, firmware development, and driver integration.  ·  risk: Increased power consumption, cost, and potential hardware debugging complexity.
- cost: Significant increase in device BOM cost and power draw.  ·  latency: Improves local responsiveness, reduces cloud dependency.
- security: Sensitive UI image data never leaves the pendant, improving privacy.


## What it asked for

### `c3-9yck` (context) — ui_hierarchy_snapshot
- why: To power mac-vision's no-pixels automation on the Mac without turning on screenshot-and-pixel control mode.
- would change: I will base next actions on accessible UI structure, safer and less intrusive than pixel-based actions.

