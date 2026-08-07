# Harness derivation — mac-vision — round 80

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Add real-time visual task validation and recovery to the computer-use loop on MacBook to detect UI inconsistencies or errors and adapt actions accordingly."
- **useful because:** The owner benefits from a more resilient AI assistant that can recognize when UI states deviate from expectations, automatically try alternate flows, or safely pause and ask for help, reducing failed operations and frustration.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** 100 ms per validation step during action sequences, with occasional longer pauses to retry or ask.
- **cost:** Moderate due to increased visual processing and decision loops.
- **security:** Requires additional screenshot access and real-time processing, highlighting the need for tight data privacy controls and owner oversight on any intervention requests.
- **missing:** Real-time UI state comparison and exception detection models; Integration of error handling logic into mac-vision action loops; UI snapshot sharing infrastructure to relay and other cognitive surfaces; Owner interaction model for fallback or escalation requests

### "Enable continuous multimodal task context retention and handoff across surfaces (MacBook, pendant, browser, relay) to improve seamless task resumption and proactive assistance without repeating information."
- **useful because:** The owner can start a complex task on one device or modality and continue it seamlessly on another, with the system remembering state, progress, and partial results, reducing cognitive load and time waste.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second for local context switches, longer for deep recalls or cross-device sync.
- **cost:** Medium to high due to frequent context saves, recall, and synchronization.
- **security:** Requires secure encrypted storage and transmission of personal task state and context; ensures all devices share the context only with owner approval.
- **missing:** Unified context architecture for multimodal data (text, vision, audio, actions) with rapid update and recall; Persistence layer accessible by all surfaces; Task segmentation and state serialization protocols; Inter-surface coordination protocols

### "Allow safe zoomable screen capture and replay on the MacBook to review past UI states for troubleshooting and learning purposes."
- **useful because:** The owner can visually review exact past screen states linked to AI actions or errors, facilitating diagnosis, debugging, and improving understanding of what the AI did or tried to do.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** Display and load of captures within 1-2 seconds; capture storage asynchronous.
- **cost:** Moderate for storage and occasional retrieval of screenshots.
- **security:** Screenshots contain sensitive information; must be encrypted and access tightly controlled by owner.
- **missing:** UI screenshot archival and browsing system; Integration of timestamped captured screenshots with AI action logs; Zoomable image viewer UI component on Mac surface


## Changes it proposed to its own stack

### `integration` — Create a seamless integration protocol between mac-vision and browser-extension to handle mixed workflows involving local Mac apps and web applications with cross-context visual and action handoff.
- **owner gets:** Allows the owner to execute complex tasks that span native Mac applications and web apps without losing context or requiring redundant commands, boosting productivity and reducing friction.
- effort: Moderate software engineering across agent boundaries and shared state management.  ·  risk: Synchronization issues could lead to inconsistent states or errors; robust error handling required.
- cost: Moderate due to cross-surface communication overhead.  ·  latency: Slight increase in some actions due to cross-agent negotiation.
- security: Must ensure secure context sharing with strict permissioning and data minimization.
- depends on: Unified context architecture; Reliable agent communication protocols


## What it asked for

_Nothing._
