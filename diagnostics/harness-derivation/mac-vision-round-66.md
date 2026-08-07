# Harness derivation — mac-vision — round 66

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `interaction` — Build a transparent, real-time, multi-agent supported UI interaction telemetry and explanation system that logs every mac-vision UI automation step with human-readable reasoning, allows users to inspect and query this history, and supports collaborative corrections or undo actions across the system surfaces (mac-vision, mac-planner, relay-realtime, unified). This system would expose clear audit trails for trust and safe debugging, empowering the owner to understand and control AI-driven Mac automations comprehensively.
- **owner gets:** The owner can fully trust and control the AI automation on their Mac by seeing exactly what was done, why, and when, and can intervene or rollback at any step. This transparency turns complex automation into a cooperative tool rather than an opaque black box, improving ownership and safety without sacrificing power or convenience.
- effort: High - requires building distributed telemetry infrastructure, UI history logs tied to multi-agent collaboration, real-time querying, and user-facing inspection tools.  ·  risk: Complex to coordinate actions and logs across multiple agents and surfaces. Potential for partial data loss or delay must be mitigated. Requires robust privacy controls to protect context and action data.
- cost: Moderate ongoing cost in telemetry storage, query services, and UI rendering; initial engineering overhead significant.  ·  latency: Low impact on latency if telemetry is asynchronously written and queried.
- security: Requires strong encryption and access control to prevent unauthorized inspection or tampering.
- depends on: cap-a4c0ec8d accessibility interaction loop; context service providing UI snapshots; mac_run_actions tool

### `model-routing` — Develop dynamic model routing logic that coordinates tasks between the wearable pendant (relay-realtime), Mac surfaces (mac-vision, mac-planner), browser-extension, and server-side models to optimize latency, privacy, and cost. This routing should contextually decide when to run vision-based UI interactions on the Mac, delegate browser tasks to browser-extension, handle voice and reinforcement learning on the pendant, and deploy background knowledge synthesis on servers. It must support fallback and smooth state sync.
- **owner gets:** Maximizes owner's experience by blending the strengths of each device and model resource, ensuring fast responses, minimal privacy exposure, and cost efficiency. This prevents unnecessary usage of expensive or privacy-sensitive components and maintains a cohesive user experience.
- effort: Medium to high, requires telemetry, integration testing, and fine-grained orchestration policies.  ·  risk: Incorrect routing could delay responses or expose data unnecessarily. Complex implementation requires careful fail-safe design.
- cost: Potentially reduces overall system cost by optimizing model execution location; incurs engineering cost to build.  ·  latency: Significant latency reduction in most cases if working well.
- security: Must maintain strict data compartmentalization and access control.
- depends on: live status and capabilities reporting from all surfaces; operational context sharing service

### `hardware` — Add a dedicated low-power AI co-processor inside the wearable pendant optimized for continuously running lightweight vision and voice models locally, without needing to offload to the Mac or servers. This co-processor would also have secure enclave features for user privacy, local data storage for episodic memory, and direct sensor fusion inputs (microphone, IMU).
- **owner gets:** Allows real-time, offline, and private processing of context-relevant sensor data and vision processing directly on the pendant, improving responsiveness and privacy without draining the main battery rapidly. It supports seamless augmentative AI experiences even without constant Mac or cloud connectivity.
- effort: High - requires hardware design, firmware integration, and model optimization specific to new co-processor architecture.  ·  risk: Hardware development risks, potential delays, and added cost. Integration challenges with existing pendant and ecosystem.
- cost: Significant one-time hardware development plus marginal cost increase per unit; reduces cloud and Mac resource use.  ·  latency: Greatly reduced inference latency for on-body vision and voice understanding.
- security: Improves security by limiting external data transmission and centralizing trusted execution locally.
- depends on: firmware updates to pendant; model coverage and optimization for new processor

### `memory` — Implement a multimodal episodic memory system that integrates inputs from wearable pendant sensors, Mac context snapshots, browser session histories, and voice conversation logs into a unified indexed memory store. This memory would be searchable and context-aware by the owner and AI agents, supporting recall of past interactions, locations, and events with temporal and situational context.
- **owner gets:** Enables seamless continuity of experience and assistance across devices and modalities. The owner can ask about or use past info without manual record-keeping, with AI that better understands ongoing context and habits.
- effort: Medium to high, requiring integration of various input streams and development of a robust indexing and retrieval system.  ·  risk: Data synchronization complexity, privacy risk needing strict access controls and user consent management.
- cost: Moderate storage and compute costs related to indexing and retrieval.  ·  latency: Mostly background; latency for query responses must be managed properly.
- security: High sensitivity; requires encryption, compartmentalization, and secure access protocols.
- depends on: device sensor data streams; context graph and knowledge base services

### `integration` — Develop proactive adaptive task collaboration protocols among the pendant, Mac surfaces, browser, and cloud backend that dynamically assign subtasks based on current device capabilities, user presence, urgency, and privacy requirements. This integration would use real-time status, context sharing, and AI mediation to balance workload and optimize user experience across devices seamlessly.
- **owner gets:** Ensures the owner's intentions are executed efficiently by the best-suited device or agent in the hive mind, reducing latency, power use, and unnecessary data exposure. It creates a fluid, context-aware assistant that adapts automatically to changing conditions and user states.
- effort: High complexity in developing coordination algorithms and protocols with robust fallback and privacy controls.  ·  risk: Coordination failures could cause task delays or inconsistent state. Privacy leaks if controls are inadequate.
- cost: Increases system complexity and coordination compute costs.  ·  latency: Improves latency through optimal resource use.
- security: Requires robust authentication, encryption, and least-privilege design.
- depends on: real-time device status and capability reporting; secure context-sharing protocol

### `firmware` — Enhance the pendant firmware to support offline voice command recognition and local execution of common command patterns, reducing reliance on network connectivity and cloud processing. Add event-triggered sensor-based wakeup (motion, tap patterns) to activate voice interface efficiently without draining battery.
- **owner gets:** Allows the owner to interact naturally with the AI system even when offline or network is poor, and prolongs pendant battery life through smarter wakeup schemes. It also supports private, instantaneous voice command processing locally.
- effort: Medium firmware and model optimization work, plus sensor integration and power profiling.  ·  risk: Firmware bugs or suboptimal patterns could reduce battery life or command accuracy.
- cost: Low additional firmware complexity and testing cost.  ·  latency: Reduces perceived latency for voice command interactions when offline.
- security: Requires secure handling of local voice data and commands to prevent spoofing or leakage.
- depends on: pendant hardware capabilities; local lightweight voice models


## What it asked for

_Nothing._
