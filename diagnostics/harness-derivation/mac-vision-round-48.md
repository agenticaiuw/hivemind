# Harness derivation — mac-vision — round 48

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, fully autonomous Mac UI interaction for complex tasks beyond simple actions"
- **useful because:** The owner currently cannot have truly autonomous visual UI control on their Mac for complex workflows that require understanding and interacting with the UI dynamically. This would fundamentally advance their productivity by enabling complex multi-step computer usage that cannot be scripted with simple action calls or delegated to basic typed commands.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-5.6-luna for planning complex workflows, gpt-4.1-mini (mac-vision) for low-latency vision control
- **latency:** Low latency for screen observation and reactive control (sub 500 ms), background model planning can be higher latency
- **cost:** Moderate per invocation dominated by vision processing and multi-step planning
- **security:** High due to autonomous UI control permissions; must have strict consent, action vetting, and undo capability with full observability
- **missing:** firm consent and policy frameworks for autonomous UI control; secure and private vision upload consent; robust, incremental UI snapshot and state context delivery; typed, reversible UI manipulation actions with full receipts; failure recovery and undo workflows integrated with the Mac surface


## Changes it proposed to its own stack

### `hardware` — Add a dedicated MacBook accessory camera and sensor suite optimized for rapid, private, high fidelity UI state capture at the screen level without interrupting owner workflow.
- **owner gets:** This hardware would provide real-time visual context for the mac-vision system without needing to degrade user experience by capturing full screenshots or relying only on the accessibility API, which is inherently limited.
- effort: Medium, involving hardware design and integration with MacBook OS and AI system pipelines.  ·  risk: Physical compatibility or privacy concerns if not handled properly; requires secure data handling and explicit owner approval.
- cost: Moderate hardware cost but amortized over multiple AI features; no meaningful latency impact.  ·  latency: Improves latency for UI state capture, aiding real-time AI interactions.
- security: Needs end-to-end encryption and strict access control.

### `model-routing` — Implement a specialized routing layer that can coordinate between the lightweight low-latency mac-vision model for immediate UI decisions and the powerful high-latency GPT-5.6-luna model for complex planning, delegating actions and observations effectively.
- **owner gets:** This routing balance would optimize responsiveness and capability, providing the owner with swift UI interactions for simple tasks and deep, strategic assistance for complex ones, without overloading any single model or creating latency bottlenecks.
- effort: Medium, requiring model orchestration and latency management system design.  ·  risk: Complexity might introduce occasional routing delays or misdirected tasks; fallback mechanisms required.
- cost: Increases compute costs modestly due to dual model usage per interaction.  ·  latency: Optimizes perceived latency by balancing workload.
- security: Moderate, as task routing must maintain context privacy and integrity.
- depends on: availability of both models with appropriate API endpoints

### `integration` — Develop a privacy-conscious user consent and action audit system integrated with all Mac surface interactions ensuring the owner can view, approve, revoke, and audit every autonomous Mac UI action taken by the AI, supporting undo and corrective workflows.
- **owner gets:** This system would build owner trust and safety, a critical factor for enabling full autonomous control over their Mac, by ensuring transparency and control over all AI-driven UI modifications.
- effort: Medium to high, involving UI design, backend logging, secure storage, and integration with the action execution pipeline.  ·  risk: Complexity and potential UI friction for the owner if not designed well; security obligations for log protection and privacy.
- cost: Minor relative to AI compute costs; mostly storage and UI interaction costs.  ·  latency: Minimal impact on latency for action execution.
- security: High importance; logs and consents must be protected against tampering and unauthorized access.

### `dashboard-ux` — Create an enhanced ownership dashboard on Mac-planner showing real-time autonomous task status, action history with undo, consent settings, and visual UI context snapshots from mac-vision for owner review and manual override.
- **owner gets:** This dashboard serves as the owner's central control and monitoring point, making autonomous Mac control understandable and manageable, increasing confidence and usability.
- effort: Moderate UI/UX development involving integration of mac-vision outputs, action logs, and control elements.  ·  risk: Overloading the owner with information if not designed well; requires frequent updates to reflect real-time state.
- cost: Minor ongoing compute and storage impact.  ·  latency: No direct latency impact on AI actions.
- security: Important to secure dashboard access and data to protect privacy.
- depends on: mac-vision providing usable UI context snapshots; action audit and consent system

### `memory` — Build a persistent episodic memory system that links autonomous UI interactions and outcomes with contextual owner preferences, prior approvals, and usage patterns to personalize and optimize future Mac automation actions.
- **owner gets:** This memory system allows the AI to learn the owner's habits and preferred workflows, reducing repetitive consent prompts and improving the relevance and success of autonomous UI interactions over time.
- effort: High, requiring development of memory representation, retrieval, and integration with action planning.  ·  risk: Privacy risk of long-term data storage; requires strong encryption and access controls; risk of incorrect generalization needing robust fallback.
- cost: Moderate storage and compute costs over time.  ·  latency: Minimal direct impact on real-time actions; mainly offline or background usage.
- security: High; requires careful handling to prevent leaks of sensitive user behavior data.
- depends on: secure data storage infrastructure; integration with mac_delegate and mac_run_actions


## What it asked for

_Nothing._
