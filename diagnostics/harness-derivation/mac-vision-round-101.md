# Harness derivation — mac-vision — round 101

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision's full computer-use loop for autonomous, safe, pixel-level UI interaction on the Mac"
- **useful because:** The owner currently cannot have an AI that autonomously interacts with the Mac's UI at the pixel level to complete complex tasks that no API can handle, enabling seamless multitasking and highly context-aware computer control.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for the mac-vision loop due to the need for visual reasoning and decision-making; gpt-5.6-luna for planning and judgement for higher-level task management and orchestrating multi-surface collaboration
- **latency:** Low latency for mac-vision loop to keep UI smooth and responsive; medium latency for planning and judgement layers to allow thoughtful task management
- **cost:** Moderate cost for continuous visual processing; occasional higher-cost cloud calls for complex decision facilitation
- **security:** Full pixel-level UI control exposes risk of unintended destructive actions or privacy leaks; strict action confirmation protocols and action auditing are required. Keeping loop disabled until explicit owner consent is given and ongoing monitoring for abnormal behavior is necessary.
- **missing:** Permission to enable computerUse.loopEnabled and visionUploadConsented; UI accessibility snapshot that mac-vision can reliably use for non-pixel fallback control; Typed action policy for observability and mutable action classification integrated with the loop; Action confirmation UI or voice prompts for destructive actions; Continuous context feed including user intent, app context, and visual state

### "Provide a continuous visual and context feed from the Mac to the AI Pendant and mac-vision for real-time shared situational awareness and decision aiding"
- **useful because:** Currently the mac-vision loop is isolated and disabled. A continuous feed of UI state, pixel changes, and app context would allow both the mac-vision agent on the Mac and the AI Pendant worn by the owner to collaborate better, allowing voice commands on the pendant to leverage mac-vision's detailed UI understanding for seamless task execution.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** gpt-4.1-mini for continuous visual processing; gpt-5.6-luna for high-level planning and coordination
- **latency:** Very low latency for pixel feed and UI changes to enable responsive control; medium latency for coordinated decision-making.
- **cost:** Higher running cost due to continuous video or image stream processing, plus backend orchestration.
- **security:** Exposing full continuous UI and pixel feed increases privacy risks. Requires strict encryption, owner consent, selective data masking, and federated processing wherever possible.
- **missing:** Permission for visionUploadConsented; Robust real-time image capture, compression, and streaming pipeline; Efficient visual and UI context extraction and event detection; Multi-agent coordination protocols for distributed AI modules to consume and act on the live context feed.

### "Implement a real-time multi-agent coordination protocol for shared understanding and decision-making between mac-vision, relay-realtime (AI Pendant), faculty-perception, faculty-judgement, and faculty-action"
- **useful because:** Currently these AI agents operate mostly in isolation or with limited connectivity. A robust protocol for sharing context, intentions, plans, and execution feedback in real-time will enable seamless synergy, making autonomous computer control on the Mac safe, context-aware, and collaborative with the owner's wearable AI.
- **path:** mac-vision → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna or equivalent for reliability and complex multi-agent coordination
- **latency:** Low latency communication required to align real-time operations with user expectations and minimize latency in task execution.
- **cost:** Moderate cost due to continuous low-latency messaging and model inferencing for coordination.
- **security:** Ensuring integrity and confidentiality of shared data streams and commands is critical. Must prevent desynchronization or malicious injection of commands. Strong authentication and encrypted channels needed.
- **missing:** Multi-agent state sync protocols; Shared context representation formats; Conflict resolution and consensus mechanisms; Event sourcing and task receipt integration


## What it asked for

### `c7-ykc7` (context) — ui_hierarchy_snapshot
- why: To understand the accessible UI elements mac-vision can interact with for safe computer use loop operation
- would change: It directs what mac-vision can see and operate on without screenshots, allowing me to consider turning on loop or recommending new capabilities.

