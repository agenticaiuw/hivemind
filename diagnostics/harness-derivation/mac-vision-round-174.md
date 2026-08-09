# Harness derivation — mac-vision — round 174

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a structured, ranked owner task store that mac-vision can query live to know the owner's current active goals and prioritize them for action."
- **useful because:** Currently, no live ranked or prioritized task list exists accessible to mac-vision; this forces it to guess or seek redundant input. A real-time ranked task list enables contextually relevant, goal-driven Mac control and planning.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** moderate server cost for data management, low latency
- **security:** Tasks might expose personal or private info; access control and encryption are essential.
- **missing:** task priority schema, API, UI for owner input

### "Expand the pendant user button interface to support multiple explicit interaction payloads or gestures to mac-vision for control confirmation, cancellation, and task triggering."
- **useful because:** Single button currently is multiplexed for conversation start/end only. More explicit payloads support better direct owner control over mac-vision automated actions without requiring the voice assistant or external device.
- **path:** pendant → mac-vision → unified
- **model tier:** realtime
- **latency:** milliseconds
- **cost:** negligible firmware cost
- **security:** Physical button multiplexing risks gesture ambiguity and timing errors; careful design needed.
- **missing:** firmware gesture recognition beyond edge detection, owner UI for configuration

### "Enable the MacVision agent to autonomously identify and organize open application windows by task context, and switch focus intelligently without requiring direct owner commands."
- **useful because:** Owners often have many applications and windows open simultaneously, leading to cognitive overload and inefficient task switching. MacVision could improve productivity by recognizing which windows belong to an active task and managing focus to optimize the owner's workflow.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** low latency, seconds
- **cost:** moderate compute for UI state parsing and decision making
- **security:** Requires broad macOS Accessibility permission, possibly raises privacy concerns from window content analysis; must be opt-in and transparent.
- **missing:** Enhanced accessibility tree analysis, task inference models, contextual memory linking UI and task definitions

### "Implement proactive multimodal status briefing from MacVision, combining real-time Mac application and system state, active reminders, calendar events, and physical pendant signals, to provide the owner a concise context-aware update without needing to ask."
- **useful because:** Owners benefit from timely context summaries that alert them to relevant upcoming deadlines, active tasks, and system state changes, without interrupting their workflow or requiring manual queries. This improves situational awareness and reduces cognitive load.
- **path:** mac-vision → pendant → mac-planner → unified
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate compute and integration cost
- **security:** Requires comprehensive data access permissions, careful design to avoid information overload and maintain privacy.
- **missing:** Aggregator for multimodal data inputs, concise briefing generation models, pendant signal input expansions

### "Create an AI-driven Mac vision task assistant that visually verifies user intentions before automating UI actions, through a secure chooser overlay on the screen, reducing errors and accidental command execution."
- **useful because:** Direct UI automation risks unintended actions due to UI changes or misinterpretation. A visible confirmation overlay allows the owner to verify exactly what the MacVision agent plans to do before executing, greatly increasing trust and safety.
- **path:** mac-vision → mac-planner → unified → pendant
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate compute and UI overlay development
- **security:** Overlay must be secure, prevent spoofing, and protect privacy; requires accessibility permissions and safe UI injection practices.
- **missing:** Secure overlay rendering capability, intent preview builder, enhanced owner interaction channels


## What it asked for

_Nothing._
