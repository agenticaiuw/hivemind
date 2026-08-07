# Harness derivation — mac-vision — round 135

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Add typed action classification and policy layer for mac-vision computer use loop actions with reversible, read-only, and high-impact flags, plus action receipts and confirmations."
- **useful because:** To safely enable and monitor AI computer control with strict action visibility and user confirmation for high-impact commands, protecting against errors or misuse.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini for mac-vision policy enforcement
- **latency:** milliseconds for action classification
- **cost:** Low API cost for classification; infrastructure cost for logging and confirmation UI.
- **security:** Ensures safety by preventing harmful actions without user consent; all high-impact actions require explicit confirmation.
- **missing:** typed action broker implementation; action receipt infrastructure; confirmation prompt mechanisms for mac-vision

### "Proactive real-time focused application and UI hierarchy monitoring to anticipate user intents and enable preemptive AI assistance on the MacBook."
- **useful because:** Knowing exactly which app and UI elements are active in real-time allows AI to predict and proactively offer relevant assistance, speeding workflows and improving responsiveness.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna for comprehensive UI context analysis and prediction
- **latency:** sub-second for context updates
- **cost:** Moderate due to frequent UI snapshot processing and interpretation
- **security:** Requires access to live UI information, so must be transparent to user with privacy controls.
- **missing:** real-time UI snapshot feed; high-frequency access to accessibility APIs; integration with mac-vision and mac-planner for action planning

### "A comprehensive AI-driven Mac accessibility controller that actively integrates visual UI analysis, keyboard/mouse event synthesis, and context from the wearable's voice assistant to seamlessly automate complex multi-application workflows with natural language intent."
- **useful because:** The owner gains a deeply intelligent and adaptable Mac assistant that understands their voice commands in context, watches the visual UI for state changes, and orchestrates interaction across apps with high precision and minimal user friction.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-4.1-mini on mac-vision for UI events, gpt-5.6-luna on mac-planner and relay-realtime for command and voice integration
- **latency:** under 1 second for UI context updates and action responses
- **cost:** Moderate; real-time UI processing and voice context fusion with secure typed controlled actions
- **security:** Requires full vision loop and typed action broker enabled with strict logging, reversible actions, and user confirmation for high-impact commands.
- **missing:** Permission computerUse.loopEnabled for mac-vision; Permission visionUploadConsented for screen capture; A typed action policy layer for automated controlling and logging; Deep integration of voice assistant context with UI and action planning; A distributed context system spanning pendant, Mac and relay for synchronized real-time state awareness

### "An offline-capable, privacy-first natural language interface on the pendant itself that can understand and execute a predefined, extensible set of complex Mac control workflows without requiring continuous cloud connection."
- **useful because:** This grants the owner hands-free, instant control of their Mac and environment even in offline or low-connectivity situations, preserving privacy and reducing latency by processing essential intents locally on the pendant.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** Compact on-device models for intent recognition on the pendant (tiny transformer or keyword spotting), full models on Mac for action planning and execution.
- **latency:** Sub-second response times for critical voice command recognition on the pendant, seconds for local execution plan preparation on the Mac.
- **cost:** Moderate; requires embedded model development and synchronization, plus software infrastructure for reliably synchronizing local and remote state.
- **security:** The pendant runs trusted but potentially sensitive models locally; must guard against unintended activations and ensure private data never leaves the device without consent.
- **missing:** Local lightweight natural language understanding and intent recognition on the pendant; Reliable surrogate action execution coordination between pendant and Mac; Fallback and sync mechanisms for offline to online transitions


## Changes it proposed to its own stack

### `hardware` — Design and build a next-generation wearable pendant with expanded sensors including a small high-resolution camera, inertial measurement unit (IMU), and haptics, plus enhanced compute and memory to locally analyze UI context and provide tactile feedback.
- **owner gets:** This would allow the pendant itself to visually assist its AI mind with local image processing of the environment, enabling faster, more accurate UI state readings and haptic user notifications independent of the Mac.
- effort: High; requires hardware design, firmware development, and integration with existing system.  ·  risk: Hardware complexity increases power draw and size; development time and iteration risk are significant.
- cost: Significant additional manufacturing cost per unit and device power draw increase.  ·  latency: Local processing reduces latency for UI context partial pre-processing before Mac vision loop ingestion.
- security: Increased attack surface requiring robust security design; on-device compute reduces sensitive data exposure over network.
- depends on: Permissions computerUse.loopEnabled and visionUploadConsented for Mac loop enablement; Software infrastructure for typed action classification and logging

### `integration` — Develop a low-latency real-time context synchronization framework that merges voice input, wearable sensor data, Mac UI state, and browser context into a single, coherent awareness graph accessible by all agents for highly reactive and proactive multi-surface assistance.
- **owner gets:** This creates a seamless AI mind that can anticipate and support owner goals across devices and interaction modalities with minimal delay or confusion.
- effort: Medium to high; requires cross-surface protocol design, synchronization algorithms, and shared memory or database with strong consistency guarantees.  ·  risk: Complex distributed system with potential for transient state inconsistencies; needs robust failover and fallback mechanisms.
- cost: Increased backend infrastructure resource use and operational complexity.  ·  latency: Improves real-time awareness and responsiveness across surfaces.
- security: Requires strict access control and encryption to protect user privacy, especially across voice and UI data channels.
- depends on: Permissions for all context feeds; Reliable network connectivity between pendant, Mac, and relay


## What it asked for

_Nothing._
## Its own summary

Proposed a tightly integrated multi-surface AI-driven Mac UI controller leveraging visual, voice, and sensor data; a next-gen pendant with enhanced local sensing and processing; a real-time multi-agent context synchronization system; and an offline pendant-based NLP interface for Mac control. All require new permissions, typed action infrastructure, hardware upgrades, or advanced integration not currently available.

**Biggest unknown:** The owner's immediate priorities among these transformative changes and what current workflows must be preserved or improved first.

