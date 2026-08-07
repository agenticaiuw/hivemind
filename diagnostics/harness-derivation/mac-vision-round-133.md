# Harness derivation — mac-vision — round 133

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a safe, fully autonomous Mac computer-use loop that watches screen and UI state and performs complex interactions on the owner's MacBook with full contextual awareness."
- **useful because:** This would provide the single most useful augmentation of Mac productivity, automating computer tasks by real-time screen and UI analysis so the owner can delegate detailed control without manual scripting or API limits.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-4.1-mini
- **latency:** Under 1 second response for simple UI interactions, longer for complex workflows.
- **cost:** Moderate API cost dominated by vision analysis and context updates via mac-vision, plus background macrophage from mac-planner.
- **security:** Full Mac control and vision data leaves the device within the owner's trusted system boundary; caution needed to prevent accidental destructive actions. Strict logging and action receipts mandatory.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; fine-grained UI snapshot context; expanded UI action primitives

### "Combine Mac desktop UI context with browser session state to enable seamless cross-application workflows controlled by the owner via natural language."
- **useful because:** Enables powerful multi-app workflows where desktop apps and browser tabs interact fluidly, avoiding context switching and manual data transfers.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** Seconds for simple cross-app tasks, longer for complex workflows.
- **cost:** Significant due to multi-surface APIs and context fusion.
- **security:** Requires careful session management and access control; user confirmation for impactful actions.
- **missing:** UI context APIs that link desktop and browser states; enhanced session awareness APIs

### "Create a always-on intelligent assistant on Mac that monitors live system status (battery, network, app focus) and provides proactive suggestions or steps to improve productivity or fix issues."
- **useful because:** Helps the owner stay informed and ahead of system issues or optimizations without manual checks, blending proactive system awareness with contextual suggestions.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second updates for system events, minutes for suggestion computations.
- **cost:** Modest cost focused on status telemetry and lightweight analysis.
- **security:** Minimal, as no destructive actions occur autonomously; all suggestions are opt-in and user-controlled.
- **missing:** live event stream of hardware status updates; integration with Mac status APIs

### "Enable real-time joint contextual awareness between mac-vision and relay-realtime to synthesize visual UI states with spoken conversations for contextual assistant actions."
- **useful because:** Allows the system to understand and anticipate owner intentions by integrating what they see on screen with what they say, enabling more relevant and timely interventions and automation.
- **path:** mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second integration for interactive conversation with state, longer for task planning.
- **cost:** Moderate due to combined real-time visual and voice processing.
- **security:** Voice and screen information are sensitive; all data must be processed locally or with strong encryption and user control.
- **missing:** Shared real-time context API between pendant speech and Mac vision model; Data fusion mechanisms to correlate visual and audio streams for task inference

### "Enable fully autonomous Mac desktop UI operation by mac-vision, including pixel-level screen capture and interaction combined with accessibility APIs, for complex task automation beyond API control."
- **useful because:** The owner can delegate rich, adaptive UI control and workflow automation that no other AI or script can perform, executing exactly the interactions needed on screen even in apps without APIs or scripting support.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** Under one second for simple UI actions, longer for multi-step workflows.
- **cost:** Moderate, dominated by continuous vision analysis and UI context processing.
- **security:** Full screen capture raises privacy concerns and risk of accidental destructive commands, so strict permission gating, action confirmation, and transparency logs are required.
- **missing:** Permission computerUse.loopEnabled and visionUploadConsented to enable screen capture and control; Expanded UI snapshot and pixel-level input APIs; Robust typed action schema for multi-step UI workflows including pixel target interaction

### "Provide an intelligent multi-agent orchestration layer that dynamically routes wide open commands and complex workflows to the most capable surface (e.g., mac-vision, relay, browser) based on modality, context, and task type, optimizing performance and user experience."
- **useful because:** This capability would allow the owner to give any command or workflow without needing to know which surface or tool can best execute it, benefiting from a seamless, integrated AI system.
- **path:** unified → mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second routing for simple tasks, longer for complex workflows.
- **cost:** Moderate to high due to multi-agent decision complexity and context fusion.
- **security:** Requires transparent routing policies and logging to avoid unintended data exposure and misuse.
- **missing:** Cross-surface live context sharing and decision API; Smart dynamic intent classification and orchestration logic

### "Create a real-time multimodal assistant capability that fuses visual UI state from mac-vision with voice commands and context from the pendant's relay-realtime agent to anticipate and prepare assistance before explicit commands."
- **useful because:** Such fusion enables anticipatory AI actions, reducing latency and friction in workflows by understanding both what the owner sees and says, enabling preemptive preparation or suggestion.
- **path:** mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second for integration, seconds for anticipatory suggestion generation.
- **cost:** Moderate due to continuous context fusion and concurrent model runs.
- **security:** Both visual and voice data are highly sensitive; must ensure local processing or very tight encryption and access controls.
- **missing:** Cross-surface live context API; Data fusion mechanisms for visual+voice streams; New model architectures for multimodal anticipation


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure local hardware encryption module to the pendant to safeguard AI model context and action commands locally, enabling cryptographic trust boundaries for Mac UI control and sensitive workflow data.
- **owner gets:** Protects the owner's sensitive interaction context and AI decisions from remote attacks or tampering, increasing trust for autonomous UI actions from mac-vision and related agents.
- effort: High engineering and verification effort in pendant firmware and cryptography stack integration.  ·  risk: Firmware bugs or integration flaws could lock out the owner or expose data; requires careful security review and recovery mechanisms.
- cost: Moderate increase in hardware bill of materials, power draw, and development cost.  ·  latency: Negligible latency impact since cryptographic operations are hardware-accelerated.
- security: Significantly raises local security and data integrity, reducing risk of misuse in sensitive autonomous operations.


## What it asked for

_Nothing._
