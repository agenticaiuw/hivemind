# Harness derivation — mac-vision — round 83

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a typed action broker on the Mac that can accept structured UI operations for Mac apps with classification of read-only, reversible local mutation, or high-impact mutation actions, and enable observability without blocking owner actions."
- **useful because:** This enables fine-grained, safe, and auditable control of the Mac with better monitoring and classification of actions. It also eases integration of multi-app workflows by making each step clear and reversible when possible, while providing transparency to the owner.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for action planning and classification with gpt-4.1-mini mac-vision integration
- **latency:** Low latency for single or multiple action classification, with slightly longer times for multi-step workflows and reconciliation.
- **cost:** API cost moderate, mostly from action classification and integration with existing tools.
- **security:** Classification filter observes and logs actions but does not block. Owner must be able to audit action logs. Actions marked high-impact require explicit owner confirmation through pendant or UI prompt.
- **missing:** Action classification schema and policy definitions; Integration with existing mac_run_actions and mac_delegate; Owner-facing audit logs and confirmation UI


## Changes it proposed to its own stack

### `hardware` — Add a dedicated lightweight local vision processing co-processor on the MacBook or pendant to enable high-speed image recognition and screen understanding for the mac-vision agent without excessive latency or power cost.
- **owner gets:** Allows real-time visual UI interaction and intelligent navigation on the Mac, unlocking fully autonomous vision-driven control without relying on slow cloud or main CPU processing. Improves responsiveness and accuracy while preserving battery life.
- effort: Moderate hardware design and firmware integration effort; requires coordination with mac-vision software and security policies.  ·  risk: Potential hardware bugs or integration issues could disrupt Mac or pendant operation temporarily; fallback to non-vision control possible.
- cost: Moderate component cost increase, marginal additional power consumption due to dedicated chip.  ·  latency: Significant reduction in processing latency for vision tasks, enabling near-instant UI updates and interaction decisions.
- security: Vision data remains local and private on device, reducing cloud data exposure risk.
- depends on: Enable computerUse.loopEnabled; Integration of mac-vision with vision data from this chip

### `model-routing` — Implement a specialized model routing mechanism that dynamically routes vision-related UI analysis queries from the Mac-vision agent to lightweight local models on the pendant or Mac, while forwarding complex reasoning and planning to powerful cloud-based models.
- **owner gets:** Optimizes latency, cost, and privacy by ensuring vision processing is done locally and fast, while leveraging stronger cloud models only when needed for complex multi-step planning and judgement. This hybrid model routing enhances responsiveness and capability robustness for interactive Mac control.
- effort: Medium implementation effort in model routing infrastructure and transparent model handoff protocols.  ·  risk: Model mismatch or routing errors could degrade user experience temporarily; fallback to cloud-only or local-only processing should be ensured.
- cost: Possible API cost reduction by offloading some inference to local device hardware; some engineering overhead in maintaining routing logic.  ·  latency: Improved latency for simple vision tasks through local processing, maintaining low-latency visual feedback.
- security: Sensitive visual input need not leave local device except when explicitly routed, enhancing privacy.
- depends on: Dedicated vision co-processor on Mac or pendant; Integration of local and cloud model pipeline


## What it asked for

_Nothing._
