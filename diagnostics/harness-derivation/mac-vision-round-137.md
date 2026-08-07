# Harness derivation — mac-vision — round 137

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to autonomously see the Mac UI visually and through accessibility APIs, then suggest the next best click or keystrokes to complete complex interactions that are not scriptable otherwise."
- **useful because:** It lets the owner complete UI-driven workflows involving apps or dialogs without needing exact API or script support, reducing manual effort and frustration.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** a few hundred milliseconds from screenshot to suggestion
- **cost:** mostly model inference cost; occasional short mac_run_actions to confirm state or execute suggestions
- **security:** Requires full UI visibility and control; sensitive screen content is processed locally on the Mac; requires permission to capture screen and control input; owner must consent to visionUploadConsented and computerUse.loopEnabled.
- **missing:** Permission for computerUse.loopEnabled and visionUploadConsented; UI hierarchy snapshot context streams; Better error recovery when vision-guided actions fail

### "A multi-step Mac agent delegation that can combine both visual UI guidance from mac-vision and concrete computer control actions, dynamically adjusting based on live UI state and owner feedback."
- **useful because:** Complex workflows often require both high-level delegation and low-level UI navigation, which a hybrid approach can handle more robustly than either alone.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** background with realtime responsiveness for critical steps
- **latency:** seconds to minutes depending on workflow complexity
- **cost:** moderate end-to-end compute cost spreading over the workflow duration
- **security:** Requires access to visual UI data and full control surface; careful permission gating and owner control needed.
- **missing:** Integration between mac_delegate and mac-vision loops; Enhanced context sharing of live UI state and intent; User confirmation or override step for risky actions

### "Automatically detect and read visible text content from arbitrary Mac UI windows and dialogs (including error messages and non-standard controls) to inform dialog handling and decision-making by the AI system."
- **useful because:** Many Mac apps use custom UI elements or modal dialogs that are not accessible via standard accessibility APIs; text recognition through vision unlocks richer context and better action planning.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** background to realtime depending on urgency
- **latency:** seconds for text extraction from screenshots
- **cost:** Moderate processing cost for OCR and semantic analysis models; mostly on Mac or pendant edge hardware.
- **security:** Requires access to screen pixels; must ensure local processing and secure handling of sensitive visual content.
- **missing:** OCR engine integration tuned for Mac UI text; UI snapshot-to-region mapping and text extraction flow; Authorization for full screen pixel access with safeguards

### "A dynamic UI action recovery feature for mac-vision where if an attempted click or keystroke has no effect or triggers unexpected UI states, the system backtracks, explores alternative actions, and retries with different strategies."
- **useful because:** UI automation can fail due to changing layouts, delays, or unexpected dialogs; robust recovery reduces the need for owner intervention and improves reliability.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime for detection and retry action generation
- **latency:** sub-second detection, seconds for retries
- **cost:** Moderate overhead for state monitoring, alternative path search, and retrying actions.
- **security:** Requires continuous UI monitoring; sensitive UI data must remain local and protected.
- **missing:** State change detection and classification for failure conditions; Automated alternative UI action plan generation; Integration with mac_run_actions and mac_delegate for retries

### "A routine-scheduling feature that triggers mac-vision powered UI navigation and task automation sequences based on time, calendar events, or detected device states (e.g., waking the Mac, connecting to a known WiFi)."
- **useful because:** Automates routine tasks that require navigating complex UIs or non-scriptable apps, reducing manual effort and enabling hands-free workflows.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** background scheduled with realtime fallback
- **latency:** varies by routine, realtime fallback under 1 second
- **cost:** Low to moderate, depending on routine complexity and frequency.
- **security:** Requires careful permission for scheduled UI interactions and control; owner must confirm and review scheduled routines.
- **missing:** Routine/event trigger hooks; Integration with mac-vision and mac-run_actions; User confirmation workflows for safety


## Changes it proposed to its own stack

### `hardware` — Add visual processing hardware accelerator on the pendant or Mac to speed up real-time computer vision tasks for the mac-vision agent, reducing latency and power consumption.
- **owner gets:** Enables seamless low-latency visual understanding and UI interaction suggestions, improving responsiveness and battery life of wearable and Mac integration.
- effort: Moderate hardware and firmware design and integration effort over several months.  ·  risk: Hardware complexity may cause design delays; failure to integrate smoothly could degrade user experience temporarily.
- cost: Increased component cost and modest additional power draw on the pendant or Mac accessory.  ·  latency: Significant latency reduction for vision tasks, improving real-time interaction quality.
- security: Sensitive screen image processing must remain local; encryption and proper access controls mandatory.
- depends on: Permission for computerUse.loopEnabled; UI hierarchy snapshot context

### `model-routing` — Route user interaction and UI state updates through a combined mac-vision/mac-planner coordination layer that balances pixel-level vision tasks with API-driven automation to optimize latency and accuracy.
- **owner gets:** Improves responsiveness and decision accuracy by using the right tool for each task and avoiding redundant or conflicting processing between vision and control layers.
- effort: Medium engineering effort to implement routing and feedback loops between components.  ·  risk: Complex interactions may cause temporary inconsistencies or feedback loops; careful design and monitoring required.
- cost: Saves compute cost by reducing duplicate effort; uses compute efficiently.  ·  latency: Improves end-to-end latency for interaction decisions.
- security: Requires secure context sharing with strict access control.
- depends on: mac-vision functionality; mac-run_actions and mac_delegate integration; UI snapshot and pixel access permissions


## What it asked for

_Nothing._
