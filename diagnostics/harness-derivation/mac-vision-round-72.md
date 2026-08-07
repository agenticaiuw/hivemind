# Harness derivation — mac-vision — round 72

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a fully autonomous Mac control loop with integrated vision for seamless UI interaction and multi-step workflows"
- **useful because:** The owner will gain hands-free, reliable Mac control that can perform complex workflows not possible through APIs alone, such as interacting with arbitrary app UIs, desktop elements, and system dialogs. This would drastically enhance productivity and accessibility, allowing the AI to proactively assist or complete complex tasks without manual input.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** advanced low-latency vision model with reinforced learning and context integration
- **latency:** sub-second interaction responsiveness with pipelined background task management for longer workflows
- **cost:** moderate to high due to vision processing and multi-agent coordination, dominated by GPU usage and network relay costs
- **security:** Requires explicit owner consent for vision uploads and pixel control; must integrate privacy-preserving protocols and ensure all actions are reversible or confirmable before execution. Risk of unintended changes or data exposure must be minimized.
- **missing:** Owner consent to enable vision upload and pixel control; Reliable UI hierarchy snapshot provisioning to complement pixel vision and prevent blind clicks; Robust error recovery and fallback mechanisms in case of UI state changes or failures; Typed action classification and pre-execution validation in the vision loop


## Changes it proposed to its own stack

### `model-routing` — Incorporate explicit model tiering and routing for mac-vision's tasks, delegating low-latency real-time UI perception to a specialized lightweight model and offloading complex multi-step planning to a higher-tier model. This improves efficiency and makes cost scalable while maintaining responsiveness.
- **owner gets:** The owner gains a responsive and cost-effective AI assistant that quickly understands UI context for immediate actions, while delegating more complex reasoning to a background process. This enhances user experience with minimal lag or wasted resources.
- effort: Moderate engineering effort in model orchestration, testing and integration  ·  risk: Mis-routing may cause slow response or failure to handle edge cases, mitigated with fallback mechanisms
- cost: Lower high-tier model usage cost by splitting workload, some increase in coordination overhead  ·  latency: Improved overall latency for routine UI interactions, background tasks tolerate slower pace
- security: No direct impact but may complicate auditing and require robust logs
- depends on: Reliable UI hierarchy snapshot provisioning; Model access improvement

### `hardware` — Add a dedicated low-power AI coprocessor to the MacBook Air for continuous vision processing and UI awareness without waking the main CPU. This coprocessor directly accesses screen pixels and accessibility APIs, enabling privacy-aware local vision analysis and reducing the need to upload screenshots to the cloud.
- **owner gets:** The owner benefits from continuous, low-latency, always-on computer vision assistance from the Mac that is privacy-preserving and power-efficient, enabling a reliable computer-use loop with vision that can operate even when the Mac is nominally asleep or engaged in other tasks.
- effort: High engineering and hardware design effort, would require Mac hardware vendor collaboration and OS integration  ·  risk: Hardware integration risks, potential privacy concerns if coprocessor is compromised, mitigated by strict sandboxed firmware design and encrypted communication
- cost: Upfront hardware cost increase, long-term savings on cloud compute and latency cost  ·  latency: Significant latency reduction for vision-driven UI control tasks
- security: Requires secure enclave or similar to protect vision data and processing
- depends on: Ongoing firmware/driver support; OS-level APIs exposure to coprocessor

### `interaction` — Implement an interactive approval and fallback protocol in the computer-use loop where potentially unsafe or irreversible UI actions require explicit owner consent via the pendant or Mac notification, while safe reversible actions proceed automatically. Allow the loop to fall back to purely accessibility-based actions when no vision permission is granted.
- **owner gets:** Ensures owner control and trust by preventing unintended destructive changes, while maintaining automation benefits where possible. Matches owner's policy of maximum access with minimal gating by using contextual approval only for high-risk actions.
- effort: Moderate implementation effort in interaction design and integration with pendant and Mac notifications  ·  risk: Risk of interrupting flow if approval requests are too frequent; mitigated by careful classification and batching
- cost: Minimal  ·  latency: Some delay for approval requests, offset by safer automation
- security: Improves security by preventing accidental harmful actions
- depends on: Typed action classification; Pendant notification and input APIs


## What it asked for

_Nothing._
