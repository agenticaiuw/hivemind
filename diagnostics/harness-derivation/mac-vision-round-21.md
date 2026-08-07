# Harness derivation — mac-vision — round 21

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable seamless multi-tiered UI automation on the Mac using a combination of accessibility mode, pixel-based actions, and real-time feedback, safely and without interfering with the owner's focus unless explicitly allowed."
- **useful because:** The owner gains robust automation capabilities that can handle any app or task on the Mac, including those requiring complex UI interactions not accessible via APIs alone, without any disruptive effects on their active work or privacy.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Low latency for immediate UI actions, background for monitoring and preparation
- **cost:** Moderate due to blending real-time accessibility queries with occasional pixel captures and multi-agent coordination
- **security:** Must ensure owner consent is obtained; pixel captures must be scoped tightly and encrypt stored data; strict fallback to purely accessibility-based operation unless pixel access is explicitly granted.
- **missing:** Fine-grained owner consent and policy management for UI interaction tiers; Robust error recovery and undo capabilities for UI automation; Tightly integrated multi-agent communication protocols for collaboration; Local privacy-preserving pixel capture mechanisms

### "Provide a dynamic context-sharing and task delegation system that automatically decides whether mac-vision, browser-extension, mac-planner, or pendant performs each step of a task, optimizing for speed, privacy, and reliability."
- **useful because:** The owner benefits from seamless task execution that uses the best surface available based on task requirements and current system state, maximizing efficiency and minimizing interruptions or privacy risks.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Real-time decision for each step but allows some background processing for complex workflows
- **cost:** Moderate due to real-time coordination and AI decision-making
- **security:** Must safeguard sensitive data between surfaces; require consent for any data sharing beyond minimal necessary context; operate enforceably within owner's policies.
- **missing:** Unified protocol for cross-surface communication and delegation; Intelligent task analysis and surface selection engine; Secure context encapsulation and sharing mechanism


## Changes it proposed to its own stack

### `hardware` — Equip the MacBook and pendant with a local trusted execution environment (TEE) dedicated to secure pixel capture and UI event logging that allows mac-vision to perform pixel-based analysis without risking privacy breaches or exposure of sensitive content.
- **owner gets:** This change enables pixel-level UI automation critical for complex tasks, while guaranteeing privacy through hardware-enforced isolation and data encryption, building owner trust and consent.
- effort: High engineering effort due to hardware design, firmware, and software integration required.  ·  risk: Could introduce new hardware bugs or performance overhead; mitigated by extensive testing and fallback modes.
- cost: Increased hardware cost and power consumption; justified by security and capability benefits.  ·  latency: Minimal latency added since processing is local to TEE.
- security: Substantially enhances security and privacy controls for visual data capture.
- depends on: capability to enable pixel-based UI automation with scoped consent

### `model-routing` — Develop a coordinated multi-agent task routing layer that dynamically selects mac-vision, mac-planner, browser-extension, or relay-realtime model instances based on task complexity, context freshness, and latency requirements, ensuring the owner gets optimal performance and privacy assurance with minimal redundant computation.
- **owner gets:** The owner receives faster, context-aware, privacy-conscious AI assistance tailored for each specific task and surface capabilities, improving user experience and trust.
- effort: Medium complexity in AI orchestration and routing logic development, integration with current cluster and context services.  ·  risk: Potential misrouting causing delays or privacy leaks, mitigated by robust monitoring, fallback, and auditing.
- cost: Moderate due to AI model inference distribution.  ·  latency: Improves overall perceived latency by optimized routing.
- security: Improves security through tighter context and surface-specific policies.
- depends on: Unified cross-surface communication and secure context management, policies for model-tier selection

### `integration` — Build a comprehensive integrated feedback system that collects and correlates signals from the owner's pendant device, MacBook sensors, browser activity, and voice commands to infer owner preferences, task urgency, and cognitive load, adjusting AI assistance style accordingly in real-time.
- **owner gets:** This system makes AI interaction more natural and less intrusive by adapting to the owner's current context, reducing annoyance and increasing effectiveness.
- effort: High effort due to multi-modal signal integration, machine learning model training, and real-time adaptation logic.  ·  risk: Misinterpretations could lead to degraded user experience; fallback to manual modes and user override is necessary.
- cost: High due to signal processing and continuous model inference.  ·  latency: Some latency due to sensor fusion but managed by asynchronous processing.
- security: Requires stringent privacy protections for multi-modal data collection and storage.
- depends on: Sensor data availability from pendant and MacBook; Multi-agent communication channel; Privacy-preserving data handling

### `dashboard-ux` — Create a unified dashboard UI for the owner that consolidates AI agent activity logs, automation suggestions, pending approvals, and context snapshots, giving full transparency and control over AI actions on the Mac, browser, and pendant devices.
- **owner gets:** The owner can understand, manage, and override AI-generated actions easily, improving trust and reducing accidental or undesired changes.
- effort: Medium effort integrating logs and state from multiple agents with secure authentication.  ·  risk: Potential information overload mitigated by thoughtful UI/UX design prioritizing simplicity and clarity.
- cost: Moderate due to additional UI and backend integration work.  ·  latency: Minimal; mostly a read-only interface updated asynchronously.
- security: Improves security posture by enabling owner oversight and control.
- depends on: Centralized logging and state aggregation; Cross-agent communication; Secure authentication and authorization


## What it asked for

_Nothing._
