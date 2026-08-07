# Harness derivation — mac-vision — round 128

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to fully control and understand the Mac UI using combined pixel vision, accessibility data, and UI hierarchy snapshots with typed action execution."
- **useful because:** The owner would uniquely benefit from a real-time, contextual AI assistant on their Mac that can perceive the full UI as a human does, and take precise reversible actions without relying solely on limited accessibility interfaces or rigid API calls. This capability enables complex multi-step workflows, error recovery, dynamic interaction with unpredictable UIs, and a major efficiency boost in computer use that cannot be matched by current partial approaches.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for pixel vision + gpt-5.6-luna for planning and coordination
- **latency:** Short term (seconds) for UI understanding, medium term (tens of seconds) for complex action planning and execution
- **cost:** Moderate to high due to pixel image processing and multiple model invocations; balanced by focusing pixel use only on ambiguous or critical UI states
- **security:** Vision data contains sensitive on-screen content, requiring strong privacy protections, opt-in consent, and local processing where possible to mitigate exposure risk. Typed actions with confirmation minimize unintended destructive operations.
- **missing:** computerUse.loopEnabled permission to enable pixel vision and interaction; visionUploadConsented permission for transferring screen images for AI processing; Access to comprehensive UI hierarchy snapshot context beyond accessibility-only fields

### "Provide the owner with intelligent computer use assistance that can proactively detect context changes in their Mac's UI and suggest relevant actions before they request them."
- **useful because:** This would make the owner more efficient and informed by anticipating their needs and preventing errors, such as offering shortcuts, reminders, or corrective actions exactly when and where they are needed in the Mac environment. This proactive assist is beyond current passive or reactive tooling and exploits the synergy between AI models, live app status, and real-time Mac control capabilities.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** gpt-5.6-luna for planning and proactive reasoning
- **latency:** Sub-second to few seconds for detecting changes and delivering assistance
- **cost:** Low to moderate, mostly CPU cycles on the Mac and modest cloud compute for AI reasoning
- **security:** Must only observe and suggest on-device app state and user interactions without transmitting private screen contents off-device. Explicit user consent for any data sharing.
- **missing:** computerUse.loopEnabled permission for live UI state capture; higher fidelity UI context data such as UI hierarchy snapshots

### "Allow the owner to delegate complex, ambiguous, or multi-application computer tasks to mac-vision through a flexible natural language interface, with the agent providing transparent step-by-step plans and options for confirmation or adjustment before execution."
- **useful because:** This would enable the owner to solve tasks that currently require manual workflow orchestration, such as compiling reports, multi-app data extraction and entry, or context-aware automation, all with a trusted AI assistant that communicates and confirms throughout the process to avoid mistakes.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for planning and explanation
- **latency:** Seconds to few minutes depending on task complexity
- **cost:** Moderate due to multi-step planning and execution but balanced by careful prompt engineering and incremental step confirmation
- **security:** Sensitive data handling must be protected and only proceed with user consent and explicit confirmation at key steps.
- **missing:** computerUse.loopEnabled permission to allow full interaction modalities; visionUploadConsented for better UI context capture


## Changes it proposed to its own stack

### `model-routing` — Implement a fast on-device pixel vision model routing path for mac-vision to enable real-time interpretation of Mac UI screenshots with minimal latency and privacy risk.
- **owner gets:** This would enable true real-time visual understanding of the Mac screen by mac-vision, improving complex UI interaction, error detection, and user assistance without relying entirely on accessibility data which can be incomplete or inaccurate.
- effort: Moderate. Requires developing or integrating a lightweight pixel vision model, fast local inference routing, and integration with mac-vision's existing planning models.  ·  risk: Model inaccuracies or resource contention on the Mac may degrade performance or cause delayed reactions; fallback on accessibility data is needed for reliability.
- cost: Increased CPU/GPU usage on the Mac; moderate cloud cost for AI orchestration if needed.  ·  latency: Improves latency for pixel vision inference, enabling faster responses from mac-vision.
- security: On-device processing reduces data exposure risk; must ensure no sensitive data leaks during model routing.
- depends on: computerUse.loopEnabled; visionUploadConsented

### `hardware` — Add a specialized low-power coprocessor on the pendant or nearby device dedicated to fast local pixel vision inference and UI snapshot processing to offload mac-vision AI work from the MacBook main CPU and reduce latency and power consumption.
- **owner gets:** This hardware boost would provide always-on vision assistance, enabling real-time UI understanding and interaction while preserving the MacBook's battery and responsiveness. It would also support privacy by keeping sensitive screen analysis local and isolated.
- effort: High. Requires hardware design, firmware development, software integration, and AI model optimization for the new chip.  ·  risk: Hardware design delays, integration bugs, and possible compatibility challenges.
- cost: Moderate to high upfront hardware cost; operational power savings on MacBook.  ·  latency: Significantly reduces pixel vision processing latency.
- security: Improves data security by localizing sensitive image processing.


## What it asked for

_Nothing._
