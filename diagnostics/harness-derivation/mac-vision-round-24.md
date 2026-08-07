# Harness derivation — mac-vision — round 24

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a smart computer vision-driven assistant on my Mac that can physically interact with any app UI element by taking screenshots, combining pixel data with accessibility insights, and deciding the safest and most effective UI action in complex tasks."
- **useful because:** Many Mac apps lack comprehensive APIs, and even accessibility layers may be incomplete. This assistant would fill the gap by visually interpreting the screen combined with accessibility, solving tasks that currently require manual effort. It could automate workflow sequences involving multiple apps and GUI elements that no current API-based automation can handle.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime low-latency model on mac-vision and relay for immediate response and decision making, with background mac-planner support for task orchestration
- **latency:** Under 3 seconds for recognition and action decision
- **cost:** Moderate per invocation due to image processing and model inference
- **security:** Screen images are sensitive; strict user consent for vision upload and local processing with no external sharing must be enforced.
- **missing:** Enable visionUploadConsented and computerUse.loopEnabled with tight safeguards; Improved screen capture and pixel + accessibility hybrid data pipeline; Policy to limit UI actions to low-risk ones unless explicitly permitted; Advanced model integration for pixel analysis jointly with accessibility trees


## Changes it proposed to its own stack

### `interaction` — Implement a tiered UI interaction control framework that segments UI actions into safe read-only, low-impact reads without cursor movement, safe clicks, and high-impact mutations with explicit owner confirmation overlays shown on the pendant before execution. This framework integrates with accessibility and pixel-based vision to dynamically adjust the safety constraints of the computer use loop.
- **owner gets:** It increases the owner's confidence and control about when and how the AI interacts with the Mac UI in a way that will not disrupt work or cause unintended changes, enabling safe activation of mac-vision loop capabilities.
- effort: Medium to high engineering effort to design, implement, and test across multiple apps and interaction modes.  ·  risk: Complexity may introduce bugs that momentarily break interaction; damage is limited since actions requiring confirmation can be prevented from executing automatically.
- cost: Minimal impact on API cost but some increased CPU for real-time decision framework during UI interaction.  ·  latency: Minimal additional latency as checks happen parallel or before UI action decision.
- security: Improves security and trust by requiring explicit user consent and multi-modal verification before high-impact actions.
- depends on: computerUse.loopEnabled; visionUploadConsented; integration of pixel and accessibility data for UI state understanding

### `firmware` — Add a dedicated onboard UI verification coprocessor on the pendant that can independently verify computer-generated UI actions before they occur by analyzing partial screen captures, cursor locations, and UI events. This coprocessor will have a small embedded model specialized in anomaly detection for UI actions potentially disruptive to the owner.
- **owner gets:** This hardware layer adds an independent, real-time safety check that prevents accidental damaging or privacy-breaking actions by the Mac vision loop, allowing the owner to safely enable the assistant with greater trust.
- effort: High hardware and firmware development effort, including designing, debugging, and integrating with existing pendant sensors and Mac connection protocols.  ·  risk: Hardware bugs could cause false positives blocking legitimate actions or false negatives missing dangerous actions; firmware updates can mitigate these issues.
- cost: Increased manufacturing cost of pendant; negligible ongoing CPU cost on Mac.  ·  latency: Minimal added latency as real-time checks are lightweight.
- security: Enhances security by introducing hardware-level control and auditability of UI interactions.
- depends on: pendant hardware upgrade availability; security and firmware update pipeline for pendant

### `model-routing` — Create a collaborative real-time multi-agent model routing strategy where mac-vision handles real-time pixel and accessibility fusion, relay-realtime processes conversational context and owner voice commands, mac-planner schedules multi-step UI automation tasks, and browser-extension acts on web session insights, with continuous context synchronization ensuring all agents have up-to-date UI and intent state.
- **owner gets:** This seamless collaboration enables complex tasks involving multiple apps, web sessions, and user commands to be executed efficiently and correctly, which no single agent can achieve alone.
- effort: Medium to high development effort to build real-time synchronization protocols, context sharing, and role assignment among agents.  ·  risk: Synchronization bugs or context mismatches could cause inappropriate UI actions; fallback and rollback mechanisms required.
- cost: Increased networking and computational cost due to frequent context updates and model handoffs.  ·  latency: Designed to minimize latency by routing requests appropriately and caching context.
- security: Complex multi-agent communication requires strong authentication and encryption to protect owner data.
- depends on: real-time context sharing infrastructure; robust multi-agent communication protocols

### `dashboard-ux` — Design a transparent UI activity dashboard for the owner, accessible on the Mac and pendant, showing real-time and recent mac-vision loop activities, including screenshots or descriptions of actions taken or planned, confidence levels, and option for immediate pause or rollback.
- **owner gets:** This transparency builds trust, enabling the owner to understand and control the AI's actions on their Mac in real time, reducing anxiety about unintended changes.
- effort: Medium UI and backend telemetry effort.  ·  risk: Dashboard bugs could misrepresent activity; data privacy controls required for sensitive screenshots.
- cost: Modest storage and UI rendering cost.  ·  latency: Negligible latency impact on core functionality.
- security: Requires strong access controls and encryption for dashboards to protect owner privacy.
- depends on: telemetry hooks in mac-vision loop; secure UI frameworks for the dashboard

### `memory` — Implement contextual memory caching that retains recent UI states, actions taken, and owner corrections, enabling the mac-vision loop to learn from mistakes and adapt actions proactively in ongoing sessions.
- **owner gets:** This memory allows the AI to build context over sessions, reduce repetitive mistakes, and improve personalization and efficiency of UI automation over time.
- effort: Medium engineering effort to design memory models, storage, and retrieval mechanisms with appropriate security controls.  ·  risk: Memory corruption or privacy leaks are risks; robust encryption and auditing mitigate these risks.
- cost: Increased storage and computation costs proportional to session length.  ·  latency: Minimal impact with caching and indexing optimizations.
- security: Strong encryption and access control needed for private user data.
- depends on: secure persistent storage; privacy policy enforcement

### `integration` — Develop a unified API abstraction layer that merges mac-vision pixel and accessibility input with other agents' contextual insights and commanding capabilities, enabling cohesive multi-agent task execution workflows that look like a single intelligent assistant from the owner's perspective.
- **owner gets:** This integration hides complexity and ensures all agents act consistently and efficiently, delivering a smooth user experience and powerful automation capabilities across diverse app ecosystems and devices.
- effort: High engineering effort to design a flexible, fault-tolerant, and extensible API gateway with comprehensive context synchronization.  ·  risk: Implementation errors could cause desynchronized or conflicting actions; extensive testing and rollback capabilities required.
- cost: Moderate increased computational cost for API orchestration and synchronization.  ·  latency: Potential latency overhead mitigated by caching and optimized routing.
- security: Critical security design needed to prevent data leaks and unauthorized actions across agents.
- depends on: multi-agent communication; robust context sharing protocols


## What it asked for

_Nothing._
