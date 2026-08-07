# Harness derivation — mac-vision — round 121

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full computer use loop on the Mac for vision-guided GUI control and interaction."
- **useful because:** This allows the system to see the Mac screen and interact with the UI elements directly using AI vision and planning, facilitating complex workflows and automations that no single modality can achieve alone.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** gpt-4.1-mini for vision, gpt-5.6-luna for planning and control
- **latency:** Real-time low latency for UI interaction
- **cost:** Moderate API usage dominated by vision model and plan iterations
- **security:** Requires strong privacy and consent controls due to screen capture and UI interaction capabilities; user must explicitly consent to loop enable and vision upload; must guard against accidental destructive actions; local control over when loop is active.
- **missing:** permission computerUse.loopEnabled; permission visionUploadConsented; full accessibility trust for AI Pendant Agent; screen recording permission

### "Enable multimodal Mac task orchestration across voice, computer use vision, browser extension, and shell agents."
- **useful because:** This creates a seamless integration of multiple AI agents on the Mac, dynamically delegating tasks to the appropriate modality for maximum efficiency and usability.
- **path:** unified → mac-vision → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna orchestrator with gpt-4.1-mini vision for UI understanding
- **latency:** Moderate latency acceptable for orchestration and multi-step workflows
- **cost:** Higher due to cross-agent coordination and multiple model calls
- **security:** Cross-agent protocol security, privacy protection when sharing context; requires trusted pathways
- **missing:** cross-agent coordination protocols; enhanced orchestration logic in unified agent

### "Enhance UI snapshot analysis and memory linking to preserve context of Mac visual state across sessions and tasks."
- **useful because:** Maintaining rich UI context history enables better personalized assistance, faster task resumption, and memory-augmented interaction across multimodal sessions.
- **path:** mac-vision → faculty-perception → mac-planner
- **model tier:** gpt-5.6-luna for memory indexing and reasoning
- **latency:** Background processing for memory building; fast retrieval when needed
- **cost:** Storage and processing costs for UI snapshot indexing and memory management
- **security:** Storage of UI state and user data requires privacy safeguards and encryption
- **missing:** memory indexing and persistence of UI snapshots; linking UI states to goals and outcomes in persistent memory

### "Enable UI hierarchy snapshot capture on Mac for precise UI element state and context analysis."
- **useful because:** Detailed UI hierarchy snapshots allow AI agents to understand and manipulate UI elements specifically and reliably, supporting advanced interaction and automation beyond simple screen images.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini for vision and UI parsing
- **latency:** Quick capture and analysis within seconds
- **cost:** Low to moderate, dominated by UI tree serialization and analysis
- **security:** Requires accessibility trust and careful permissioning; UI state may contain sensitive info; must restrict data sharing and retention
- **missing:** UI hierarchy snapshot capture tooling and API

### "Enable dynamic permission management UI on the Mac agent for user control over accessibility, screen recording, loop enablement, and vision upload consent."
- **useful because:** Empowers the owner to safely grant or revoke sensitive permissions needed for vision and computer use in a transparent and manageable way, increasing trust and control over the AI capabilities.
- **path:** mac-planner
- **model tier:** GPT-5.6-luna for UI automation and dialog management
- **latency:** Interactive, low latency for UI response
- **cost:** Low, mostly automation and monitoring
- **security:** Must securely handle permissions and user inputs; protect against spoofing and accidental grants
- **missing:** Permission management UI and integration with system permissions APIs

### "Enable AI vision-guided autonomous computer control on the MacBook with pixel-level screen understanding when accessibility APIs and screen recordings are restricted or unavailable."
- **useful because:** This unlocks full autonomy for the owner to control any Mac app or UI element visually without relying solely on accessibility or automation permissions, enhancing power and flexibility.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** gpt-4.1-mini for visual parsing, GPT-5.6-luna for planning and control
- **latency:** Real-time low latency is critical for fluid interaction
- **cost:** Higher compute cost due to pixel-level vision model and increased interaction steps
- **security:** Requires explicit owner consent for screen capture; local-only processing preferred; must minimize accidental destructive actions
- **missing:** low-level pixel capture and filtering hardware and API on Mac pendant side, enhanced AI models for pixel UI parsing, adaptation to limited accessibility data

### "Create a seamless AI-assisted Mac task orchestration system that integrates the AI pendant's vision, voice, browser, and terminal agents to handle complex workflows with dynamic modality switching."
- **useful because:** This gives the owner a powerful assistant that coordinates multiple AI agents for the Mac to complete tasks intelligently by using the best available modality at each step, increasing productivity and reducing manual effort.
- **path:** unified → mac-vision → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna for orchestration with gpt-4.1-mini for visual UI understanding
- **latency:** Moderate latency acceptable for complex orchestration
- **cost:** Higher cost due to multi-agent interaction and planning
- **security:** Cross-agent data sharing, privacy, and command verification protocols required
- **missing:** cross-agent orchestration protocols and APIs, enhanced multi-agent coordination logic in unified agent


## What it asked for

_Nothing._
## Its own summary

Discovered the state of AI Pendant Mac integration with full control mode enabled but mac-vision loop disabled due to missing permissions (loopEnabled, visionUploadConsented, accessibility trust, screen recording). Proposed enabling full vision-guided UI control loop, a unified multi-agent orchestration system for Mac task automation, and a hardware change for low-latency pixel capture and vision model acceleration on the Mac pendant. These unlock the owner's ability to fully control and automate their Mac with advanced AI-driven vision and multimodal integration beyond current capabilities.

**Biggest unknown:** Exact availability and integration of UI snapshot or accessibility tree capture APIs and progress on granting required permissions for computerUse.loopEnabled and visionUploadConsented.

