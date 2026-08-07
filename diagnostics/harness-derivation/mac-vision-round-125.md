# Harness derivation — mac-vision — round 125

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent computer-use loop with live UI hierarchy snapshots and controlled typed action execution to autonomously operate Mac apps and UI when direct API control or browser automation is insufficient."
- **useful because:** This capability would let the owner delegate complex visual and UI-driven computer tasks to the AI, speeding workflows, reducing manual repetition, and enabling powerful automation beyond API limits, truly leveraging wearable AI assistant power on the Mac.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** Real-time to a few seconds (for single step actions or queries)
- **cost:** Moderate API calls for UI hierarchy snapshots and action execution, model inference cost for vision and control logic.
- **security:** Full typed action control requires permission and careful control to prevent unintended destructive actions. Visual data processed locally or encrypted in transit. Consent needed for screen capture. Logs and receipts required for audit.
- **missing:** Permission computerUse.loopEnabled; Permission visionUploadConsented; Context ui_hierarchy_snapshot for Mac UI structure

### "Seamlessly delegate multi-step, ambiguous, or extended Mac workflows from natural language goals via the mac_delegate tool, bridging complex tasks across multiple applications and contexts."
- **useful because:** Owners often encounter workflows that can't be expressed as single or few actions but require contextual understanding and orchestration across apps. This capability unlocks broad automation potential and makes the AI a true assistant rather than a simple tool executor.
- **path:** mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Minutes (for multi-step planning and execution)
- **cost:** Higher due to longer model runtime, context integration, and multi-step orchestration.
- **security:** Requires trusted environment, audit logs, and possibly owner interaction confirmation for high-impact steps.
- **missing:** 

### "Provide live Mac device state readings on battery, wifi, volume, and focused app on demand with low latency, via get_mac_status tool, enabling the owner to make informed decisions remotely or hands-free."
- **useful because:** Knowing device status instantly is critical for owner decision-making, task planning, and error recovery, especially when away from the Mac or using voice-only interfaces.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** Sub-second to 1 second
- **cost:** Low API call volume, minimal compute cost.
- **security:** Non-mutating read-only data, no major concerns aside from safe access enforcement.
- **missing:** 

### "Grant the AI Pendant and Mac agent the ability to capture and upload screen images securely for visual analysis to enable enhanced visual understanding and pixel-level control of applications, while maintaining owner privacy and data security."
- **useful because:** Visual capture enables capabilities beyond API and accessibility layers, such as interpreting unstructured UI, identifying visual changes, performing pixel-perfect interactions, and improving assistance quality with visual context.
- **path:** mac-vision → relay-realtime → faculty-perception
- **model tier:** gpt-4.1-mini
- **latency:** Seconds to enable near-real-time feedback loops
- **cost:** Moderate to high depending on upload frequency and image complexity.
- **security:** Screen capture leaks private data. Must be opt-in only with clear privacy controls, encrypted transmission, local preprocessing to filter sensitive content, and strong access auditing.
- **missing:** Permission visionUploadConsented; Secure encrypted upload mechanism; Local image preprocessing

### "Integrate voice command and feedback loop across wearable pendant and Mac agent to enable seamless multimodal interaction for hands-free Mac control and task management."
- **useful because:** Combining voice and visual computer use loop lets the owner interact naturally through spoken commands and get real-time feedback on screen states or task progress, improving accessibility and efficiency.
- **path:** relay-realtime → mac-vision → faculty-perception → faculty-action
- **model tier:** gpt-realtime-2.1
- **latency:** Real-time conversational latency under 1 second
- **cost:** Moderate to high compute cost combined from voice recognition, speech generation, and visual feedback integration.
- **security:** Voice data is sensitive. Requires local processing or encrypted transmission with strict access controls and explicit owner permissions.
- **missing:** Permission computerUse.loopEnabled; Permission visionUploadConsented; Integration with voice relay systems


## What it asked for

_Nothing._
