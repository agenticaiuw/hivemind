# Harness derivation — mac-vision — round 31

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, responsive UI interaction loop on the Mac using accessibility interface only, without requiring screen capture permission"
- **useful because:** The owner wants natural and continuous computer interaction assistance for apps without the privacy and consent barriers that block screen capture usage. This would allow the mac-vision agent to assist by reading UI state fully through the accessibility tree and performing precise UI actions, without intruding on raw screen pixels or requiring visual consent.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** 100ms to 1s per UI observation/action step
- **cost:** Low API cost as most work is local actions with compact UI data rather than full images or models
- **security:** Keeps user privacy strong by never requiring raw visual data or screen capture approvals; relies only on authorized OS accessibility APIs with user consent. Avoids any accidental exposure of sensitive screen content.
- **missing:** Complete and current accessibility UI hierarchy snapshots from faculty-perception and permission to run the loop with this data only

### "Allow multi-modal macro scripting combining browser, Mac UI, shell commands, and voice control in a seamless single agent workflow"
- **useful because:** The owner could issue a complex task once, and the unified agent would orchestrate the right actions distributed across browser, Mac apps, shell, and voice interactions. This would automate and simplify deeply integrated workflows, saving time and mental load.
- **path:** mac-planner → browser-extension → mac-terminal → relay-realtime → faculty-judgement → faculty-action
- **model tier:** realtime and background mix, with realtime for owner conversation and background for complex coordination
- **latency:** seconds to minutes for full multi-step workflows, realtime for interactive parts
- **cost:** Moderate, due to multi-model use and cross-surface communication
- **security:** Complexity increases risk of unwanted state changes; requires robust auditing, action receipts, and owner override ability
- **missing:** Fine-grained action APIs allowing cross-surface orchestration with consistent state; Persistent shared workflow memory and state graph across surfaces and time; Unified model routing logic to combine verbal and typed/shell commands dynamically


## Changes it proposed to its own stack

### `mac-harness` — Add a high-fidelity hybrid UI understanding layer that combines real-time accessibility tree snapshots with lightweight selective pixel analysis to handle apps with complex or non-accessible UI elements, enabling robust UI automation without full screen capture.
- **owner gets:** This would greatly enhance the accuracy and reliability of UI interaction automation on the Mac, especially for apps that do not fully expose accessibility trees, improving the owner experience with automation and assistance.
- effort: High, involves OS integration, accessibility API enhancements, and pixel analysis tooling.  ·  risk: Complex integration may cause intermittent failures; fallback strategies needed; privacy concerns carefully managed by limiting pixel data.
- cost: Moderate computational cost; minimal API cost beyond local device usage.  ·  latency: Adds slight latency to UI observations but improves overall action success rate.
- security: Pixel data collection minimized and controlled; no raw screen recordings stored or transmitted.
- depends on: accessibility UI snapshot infrastructure; owner permission to run enhanced UI observation

### `model-routing` — Implement a dynamic model router that routes owner intents to the optimal model for the task — realtime vision/interaction models for UI actions, background models for planning and orchestration, and separate browsing and shell models — with state sharing across them.
- **owner gets:** This would make the overall system more efficient and context-aware, allowing faster interaction responses on the Mac while offloading heavy-lift reasoning and orchestration to background models, improving responsiveness and reliability.
- effort: Medium, requires infrastructure improvements and model API coordination.  ·  risk: Incorrect routing might cause small delays; requires robust fallback mechanisms.
- cost: Potentially reduces overall API costs by optimizing expensive model invocations.  ·  latency: Improves perceived latency by prioritizing realtime models for interaction steps.
- security: Routing is internal; must ensure no exposure of private data in transitions.
- depends on: local context graph access; agent session coordination

### `hardware` — Equip the pendant device with a secure UI interaction companion chip that can perform local accessibility queries and provide token-gated UI context snapshots to the Mac vision agent, enabling offloading of sensitive UI data collection from the Mac itself.
- **owner gets:** This ensures privacy-sensitive UI state data can be collected securely and efficiently without burdening the Mac or exposing raw screen captures, enabling continuous, privacy-respecting UI assistance.
- effort: High, involves hardware design, firmware, and integration with OS accessibility APIs.  ·  risk: Hardware design complexity and integration challenges; potential for usability friction if not seamless.
- cost: Additional hardware cost and power consumption.  ·  latency: Improves UI data freshness and offloads workload from Mac.
- security: Enhanced security and privacy through hardware gating and token access control.
- depends on: hardware integration with Mac and agent; firmware to handle accessibility queries

### `interaction` — Develop a continuous micro-feedback loop between the AI pendant (relay-realtime) and mac-vision agent, where the pendant provides contextual priority signals (owner attention, urgency) to the Mac automation loop, and the Mac agent reports back operation progress and requests for clarification.
- **owner gets:** This bidirectional interaction enhances the efficiency and relevance of UI interactions by aligning computer automation with the owner's real-time attention and priorities, improving overall user experience and reducing mistakes or delays.
- effort: Medium, involves protocol design, message routing, and UI signaling implementation.  ·  risk: Latency or message loss could reduce responsiveness; must degrade gracefully.
- cost: Negligible API cost, local message routing primarily.  ·  latency: Improves perceived system responsiveness and alignment with owner intent.
- security: Messages must be encrypted and authenticated to prevent spoofing or leakage.
- depends on: reliable agent relay infrastructure; contextual signal extraction on pendant


## What it asked for

_Nothing._
## Its own summary

Proposed six new capabilities and changes to enable privacy-safe, responsive Mac UI interaction using accessibility interfaces rather than screen capture, multimodal macro orchestration, hybrid UI understanding, dynamic model routing, pendant hardware augmentation, and feedback loops for prioritized automation. These advance the owner's ability to interact naturally and safely with the Mac through a distributed, privacy-aware agent system.

**Biggest unknown:** Exact UI hierarchy and accessibility snapshot details and owner priorities for interaction automation.

