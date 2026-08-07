# Harness derivation — mac-vision — round 51

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the Mac vision loop to assist with GUI operations requiring pixel-level understanding, but only after obtaining all necessary permissions and owner consent."
- **useful because:** It would allow seamless visual UI navigation and advanced task automation that APIs and accessibility alone cannot achieve, increasing the range and power of Mac automation for the owner.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** realtime
- **latency:** 200ms per step; batch to 25 steps per loop
- **cost:** Small per-step LLM cost; negligible bandwidth; permission checks are manual
- **security:** Requires sensitive permissions (screen recording, accessibility). Data stays local. Pixel data is used transiently only during the loop, not stored or sent externally without consent.
- **missing:** Accessibility permission trust for AI Pendant Agent; Screen recording permission grant for AI Pendant Agent; Vision upload and use consent from owner; User interface for owner to grant and revoke permissions easily; Robust fallback to accessibility-only control if permissions denied

### "Provide a reversible receipt and undo function for every Mac vision loop or pixel screen action taken, with instant feedback to the owner."
- **useful because:** This builds user trust and safety by making all pixel-based GUI interactions transparent, auditable, and revertible, preventing unwanted or mistaken changes.
- **path:** mac-vision → mac-planner → relay-realtime → unified
- **model tier:** realtime
- **latency:** Within 500ms per action for feedback and undo availability.
- **cost:** Moderate due to tracking all actions and potential reversions, but mostly local.
- **security:** Actions and receipts data is locally stored; undo commands guarded to prevent abuse.
- **missing:** Full implementation of typed action receipts and undo for pixel-level actions; UI for easily reviewing and undoing actions

### "Enable safe and privacy-preserving pixel-level GUI automation on the Mac through the AI Pendant Agent."
- **useful because:** This unlocks full visual UI navigation and control that APIs and accessibility alone cannot provide, enabling more complex and natural task automation for the owner.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** realtime
- **latency:** 200ms per step; batch to 25 steps per loop
- **cost:** Moderate per-step LLM cost; negligible bandwidth; requires permission grants and owner consent
- **security:** Requires screen recording and accessibility permissions, with owner control and clear privacy safeguards.
- **missing:** Accessibility permission trust for AI Pendant Agent; Screen recording permission grant; Vision upload consent from owner; User onboarding flows to grant and manage permissions; Reversible receipt and undo for pixel actions

### "Allow the AI Pendant to conduct priority-based, non-UI background monitoring of key Mac applications' file and data changes, reporting only significant events to the owner."
- **useful because:** This provides a privacy-preserving, low-impact way to keep the owner informed about critical changes and events on their Mac without opening full UI automation or screen capture, complementing vision loop capabilities.
- **path:** mac-planner → relay-realtime → unified
- **model tier:** background
- **latency:** Minutes to hours acceptable since non-urgent.
- **cost:** Low incremental cost; relies on existing file and system event hooks.
- **security:** Must comply with privacy policies; events filtered to avoid sensitive exposure.
- **missing:** Background file and event monitoring hooks; Priority-based filtering logic; Secure and user-friendly notification interface


## Changes it proposed to its own stack

### `integration` — Implement a permission onboarding assistant integrated into the AI Pendant Mac Local Agent that guides the owner step-by-step to grant Accessibility and Screen Recording permissions, and consent to vision upload, with explanations of why each is needed and privacy assurances.
- **owner gets:** Smoothes and speeds up the difficult manual setup process for enabling the full Mac vision loop, reducing owner frustration and improving trust and transparency.
- effort: Medium: requires building UI flows in mac-planner and mac-vision agent, plus system prompts and documentation.  ·  risk: Minimal risk; failure only delays full vision loop enablement. Could frustrate owner if poorly designed.
- cost: Negligible server cost. Mostly local UI and logic.  ·  latency: None in normal operation.
- security: No additional risk beyond current permission usage. Improves user control and awareness.
- depends on: mac-vision permission state reporting; owner consent UI in mac-planner

### `hardware` — Add a dedicated hardware security LED on the AI Pendant Mac Local Agent device that lights up visibly whenever the screen recording or vision capture mode is active, to provide a clear real-time privacy indicator to the owner.
- **owner gets:** Provides physical assurance and transparency that sensitive visual capture is occurring, increasing trust and reducing accidental privacy breaches.
- effort: Low to medium; requires minor hardware modification and firmware update to control the LED, plus coordination with software to toggle it appropriately.  ·  risk: Low risk; hardware modification required. Failure mode: LED not lighting up correctly, mitigated by fallback software warnings.
- cost: Small increase in hardware manufacturing cost and power usage, negligible overall.  ·  latency: None.
- security: No data impact; purely informational.
- depends on: firmware update capabilities; integration with computerUse vision state

### `model-routing` — Develop a dedicated vision interaction model tier optimized for low-latency pixel-based UI understanding and action on the Mac version, integrated closely with mac-vision and mac-planner agents to route pixel UI inputs and action requests efficiently.
- **owner gets:** Enables real-time, responsive, and precise visual UI automation on Mac that blends pixel and accessibility data, overcoming API limitations and enabling complex task progressions.
- effort: High; requires model training or fine-tuning, infrastructure for routing, and integration with multiple agents.  ·  risk: Medium; model failures could cause incorrect actions but reversibility mechanisms can mitigate.
- cost: Moderate per inference cost at real-time speed.  ·  latency: Latency critical but needs careful engineering to stay under 200ms per step.
- security: Requires careful data handling and privacy protection since it processes screen pixels.
- depends on: access to Mac screen pixel data; vision upload consent; integration with mac-vision agent; integration with mac-planner routing

### `firmware` — Update the pendant firmware to allow local real-time pixel pre-processing for privacy-preserving feature extraction before sending any screen capture data to the cloud or Mac agents. This includes cropping, downsampling, and obfuscation as configured.
- **owner gets:** Increases privacy by reducing sensitive data sent out, allowing safe use of pixel vision while minimizing user exposure.
- effort: Medium to high; requires firmware updates, testing, integration with cloud and Mac agents.  ·  risk: Medium; errors in preprocessing could degrade performance or incorrectly obfuscate needed info.
- cost: Minor increase in pendant CPU usage and power draw during active vision use.  ·  latency: Small; adds preprocessing delay but still compatible with real-time operation.
- security: Enhances privacy and security by shrinking data exposure.
- depends on: firmware update tools; integration with mac-vision and relay pipeline

### `dashboard-ux` — Create a dedicated Mac vision usage and permission dashboard in the owner’s AI Pendant dashboard that shows real-time status of vision loop enablement, permission states, recent vision actions taken, and privacy indicators.
- **owner gets:** Gives the owner transparent visibility into vision operations, permission status, and usage logs all in one place, increasing trust and enabling quick troubleshooting or consent withdrawal.
- effort: Low to medium; primarily UI development and backend data integration.  ·  risk: Low; no critical systems affected.
- cost: Negligible.  ·  latency: None.
- security: Stores and displays usage and permission data securely.
- depends on: backend telemetry collection from mac-vision; dashboard integration; permission reporting from mac-vision

### `hardware` — Add a dedicated hardware privacy LED on the AI Pendant Mac Local Agent device to visibly indicate when pixel-level screen capture is active.
- **owner gets:** Provides a clear, unspoofable physical signal of sensitive visual capture activity, increasing owner trust and privacy awareness.
- effort: Low to medium; hardware modification and firmware update required.  ·  risk: Low; failure mode mitigated.
- cost: Small additional hardware cost and power usage.  ·  latency: None.
- security: Informational only; no data impact.
- depends on: firmware update capabilities; integration with vision state


## What it asked for

_Nothing._
