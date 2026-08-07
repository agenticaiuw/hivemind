# Harness derivation — mac-vision — round 74

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `integration` — Introduce a seamless multi-agent orchestration layer that allows mac-vision to hand off complex multi-step, multi-application workflows to mac-planner and browser-extension, while receiving feedback and progress updates in real time.
- **owner gets:** The owner gains a powerful composite assistant that can break down complex tasks involving multiple apps and browser sessions into manageable steps, collaborating between agents to complete workflows efficiently and reliably.
- effort: Moderate engineering effort to define protocols, state sharing, and error recovery across agents.  ·  risk: Potential for synchronization bugs and state mismatch between agents; needs robust error handling and fallback.
- cost: Low to moderate additional API usage and CPU cost from orchestration logic.  ·  latency: Small increase in latency due to communication between agents but focused on user-perceived progress updates.
- security: Requires secure inter-agent communication channels and clear boundaries for data sharing, respecting owner's privacy preferences.
- depends on: Enabling mac-vision full computerUse loop; Access to UI hierarchy snapshot context

### `hardware` — Add a custom secure co-processor on the pendant or bridge that can locally process UI screenshots and do lightweight image recognition and anonymization before sending data to the Mac-vision or relay agent, minimizing privacy-risk of raw screenshots leaving the device.
- **owner gets:** Enhances privacy and security by preprocessing and filtering screen data locally, allowing richer UI interaction capabilities without exposing sensitive visual information unnecessarily.
- effort: High, involving hardware design, firmware development, and integration.  ·  risk: Delays in processing pipeline, hardware cost, and complexity in maintaining co-processor firmware updates.
- cost: Additional hardware and development cost, small increase in pendant power consumption.  ·  latency: Potentially reduces latency for image processing by offloading from main CPU.
- security: Significantly increases privacy safeguards by localizing sensitive image data processing.
- depends on: Access to raw UI screenshots; Full computer-use loop enabled

### `interaction` — Design a user-confirmation and feedback interaction layer that is persistent across devices (pendant, Mac, browser) to notify the owner of impending destructive or sensitive UI actions initiated by mac-vision, requiring explicit voice or tactile approval before execution.
- **owner gets:** Prevents accidental destructive actions on the Mac, builds owner trust in AI's control, and provides clear communication of AI intentions with easy overrides from multiple user surfaces.
- effort: Moderate engineering in UI design, cross-device communication, and prompt timing.  ·  risk: Potential friction or annoyance if confirmations are too frequent; needs tuning for minimal disruption.
- cost: Low additional API and compute cost.  ·  latency: Minimal impact on UI responsiveness; confirmation gating is user-paced.
- security: Improves security by explicitly involving the owner in critical decisions.
- depends on: Full computer-use loop enabled; Reliable cross-device communication channels

### `memory` — Create a short-term memory buffer on the Mac-vision agent for tracking recent UI states, user actions, and AI decisions, enabling contextual undo, recovery from UI errors, and better flow in multi-step interaction sequences.
- **owner gets:** Improves robustness and user experience by allowing the system to backtrack or correct mistakes without needing full re-initialization, making AI interactions smoother and less error-prone.
- effort: Moderate software engineering to define state capture and rollback primitives.  ·  risk: State desynchronization or stale context needing recovery mechanisms.
- cost: Low additional storage and compute usage locally.  ·  latency: Minimal impact since memory management can be asynchronous.
- security: Must ensure privacy of stored UI state, encrypted and limited in retention.
- depends on: Full computer-use loop enabled

### `context` — Implement a context fusion layer that aggregates UI state from accessibility snapshots, pixel screenshots, running app statuses, and browser sessions into a unified live model for mac-vision to query and act on.
- **owner gets:** Provides a comprehensive and current understanding of what the owner sees and what apps are active, enabling precise and coherent AI control and reducing errors or unnecessary interactions.
- effort: Significant effort to integrate diverse data sources and keep the fused model live and efficient.  ·  risk: Complexity in keeping the context consistent and synchronized; latency in updates may cause temporary mismatches.
- cost: Moderate additional compute for fusion and synchronization.  ·  latency: Small added latency in sensing phase; improves action accuracy.
- security: Must handle privacy carefully as it combines multiple sensitive data streams.
- depends on: Access to accessibility UI snapshots; Full computer-use loop enabled; Screenshots and app status feeds


## What it asked for

_Nothing._
