# Harness derivation — mac-vision — round 99

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision agent's pixel-level computer use loop on the Mac for real visual understanding and direct control."
- **useful because:** The owner could have real-time visual UI understanding and more flexible, accurate computer control including clicking and typing that accounts for the actual screen state. This is not achievable with current text or accessibility-only control tools.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** realtime
- **latency:** sub-second typical for interactions; a few seconds for complex visual analysis
- **cost:** Moderate API and computation costs for image capture, processing, and real-time decision making. Pixel processing dominates budget.
- **security:** Visual data contains sensitive UI content; requires explicit owner consent (visionUploadConsented). Control must be gated to prevent unwanted destructive actions.
- **missing:** Permission for computerUse.loopEnabled and visionUploadConsented needs to be granted; Typed action policy distinguishing levels of mutation for safety and confirmation; Robust UI snapshot and pixel capture integration for mac-vision to process; Pixel delivery and mouse/keyboard action capability without focus stealing

### "Allow mac-vision to combine accessibility-based UI hierarchy exploration with pixel-level visual recognition for the Mac UI, without stealing focus or interfering with owner usage."
- **useful because:** This allows mac-vision to intelligently understand and manipulate the Mac UI using both semantic accessibility data and pixel-based visual cues simultaneously. The owner gets powerful autonomous UI interactions that are robust even when pure accessibility is insufficient and pixel control alone is disruptive.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** realtime
- **latency:** sub-second to a few seconds depending on UI complexity and needed visual analysis
- **cost:** Moderate, includes cost of pixel image capture and AI model processing with occasional fallback to accessibility navigation.
- **security:** Requires fine-grained permissions for pixel capture and accessibility data. Visual data includes personal UI content; owner consent mandatory.
- **missing:** Integration layer to merge pixel-level vision with accessibility hierarchy snapshot; New loop software to run on Mac combining both input modes; Better control policies for mouse and keyboard to avoid interfering with owner when not actively in use


## Changes it proposed to its own stack

### `hardware` — Equip the MacBook Air or equivalent device with a low-latency, high-resolution dedicated camera designed and integrated for continuous screen capture for AI vision processing with minimal power and thermal cost.
- **owner gets:** Provides the mac-vision agent and the AI system with high-quality, real-time visual data of the Mac UI and screen elements for precise decision making and action.
- effort: High, requires hardware design and manufacturing changes in future Mac iterations or use of special external devices.  ·  risk: Hardware integration or malfunction could affect overall Mac performance or security if visually captured data leaks.
- cost: Moderate hardware cost increase, low additional power draw if optimized.  ·  latency: Reduces latency compared to screen capture software solutions by offloading capture to dedicated hardware.
- security: Needs strong encryption and access control to prevent unauthorized access to video stream.

### `model-routing` — Route appropriate UI interpretation, pixel analysis, and computer use loop decision making to specialized models optimized for visual understanding and ephemeral UI state tracking.
- **owner gets:** Allows the owner to benefit from highly accurate, specialized AI vision capabilities on the mac-vision surface while offloading general language and control work to more efficient dedicated models, improving latency and reliability.
- effort: Moderate software architecture and integration work  ·  risk: Increased system complexity could introduce routing errors or latency spikes
- cost: Reduces API costs by using cheaper specialized models for pixel-level tasks, potentially increasing costs slightly for effective routing and fallback mechanisms.  ·  latency: Improves latency and responsiveness for visual tasks
- security: Requires careful data handling to prevent vision data exposure outside allowed models.
- depends on: computerUse.loopEnabled; visionUploadConsented

### `interaction` — Develop a seamless owner authorization and confirmation interface for mac-vision pixel-level control actions that balances safety, user control, and minimal disruption, adaptable for varied owner preferences and contexts.
- **owner gets:** Allows the owner to grant or deny potentially impactful UI actions with minimal friction, increasing trust and comfort in giving mac-vision the ability to act in their computer UI while avoiding unintended or disruptive operations.
- effort: Medium effort for UI/UX design, policy specification, and integration into interaction flow  ·  risk: Poor design could lead to owner frustration or inadvertent permission grants
- cost: Low to moderate, mainly UX design and runtime code  ·  latency: Minimal effect on system latency
- security: Improves security by ensuring owner control and visibility over pixel-level UI actions
- depends on: computerUse.loopEnabled


## What it asked for

_Nothing._
