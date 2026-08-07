# Harness derivation — mac-vision — round 40

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe and privacy-preserving computer use loop with pixel-free accessibility UI control"
- **useful because:** The owner should be able to have an always-on, autonomous Mac control loop that performs complex computer tasks without relying on pixel screenshots, thus preserving privacy and avoiding interference with user focus and workflow.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → relay-realtime → mac-planner
- **model tier:** gpt-4.1-mini for mac-vision with gpt-5.6-luna supporting perception, judgement, and action
- **latency:** low latency for interaction steps, background support for task planning
- **cost:** Low API cost dominated by perception and judgement model usage; minimal network overhead
- **security:** No screenshot or pixel data leaves the Mac or pendant; only accessibility-derived UI structure data is used; actions are reversible or confirmed by judgements.
- **missing:** Full UI accessibility hierarchy capture and reliable interpretation; Policy gating and preferences on autonomous mutation versus confirmation; Improved mac-run-actions and mac-delegate APIs integrating semantic UI state from accessibility framework

### "Multimodal semantic UI understanding and predictive action planning across Mac and browser"
- **useful because:** The owner should be able to instruct the system with high-level intents that combine state from the Mac native apps and browser sessions, including partially observed UI contexts, to get predictive, context-aware suggestions and multi-step automated workflows with rich feedback.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-perception → faculty-action
- **model tier:** gpt-5.6-luna for planning with gpt-4.1-mini for visual UI semantic understanding
- **latency:** medium latency acceptable for complex planning
- **cost:** Moderate cost dominated by multimodal contextual interpretation
- **security:** Requires secure sharing of UI state between surfaces; owner approvals for workflows; robust rollback and audit logs.
- **missing:** Cross-surface prompt integration for multimodal context; Tools for semantic UI feature extraction from accessibility plus pixel data; Robust multi-step action orchestrator with fallback heuristics


## Changes it proposed to its own stack

### `hardware` — Design a next-generation wearable AI pendant with enhanced CPU, memory, and native camera sensors with privacy-controlled local processing for rich context capture and low-latency AI inference.
- **owner gets:** This would provide continuous multimodal data capture (audio, visual, environmental) locally and enable more powerful, private, and responsive AI assistance that currently cannot be supported by the prototype Nordic nRF9160 pendant hardware.
- effort: High engineering effort to design, prototype, and certify new hardware; involves embedded system design, AI silicon integration, and privacy engineering.  ·  risk: Development risks include hardware complexity, power consumption, latency, and user acceptance, recoverable by incremental prototyping and user testing.
- cost: Significant component and design cost impact; increased power draw versus current prototype.  ·  latency: Greatly improved latency for multimodal inference by local processing.
- security: Local processing reduces data upload needs, improving privacy and attack surface control.

### `integration` — Create a cross-device secure context-sharing protocol that allows the pendant, Mac, browser, and relay to exchange semantically rich UI and task context in real-time with end-to-end encryption and user control.
- **owner gets:** This would enable seamless collaboration across surfaces, allowing the AI collective to leverage their unique hardware and software strengths to complete complex user tasks without redundant context gathering or privacy breaches.
- effort: Medium effort for protocol design, implementation on all devices, and UI for user permissions and context sharing controls.  ·  risk: Security risks if protocol is improperly implemented; mitigated by strong encryption and user control interfaces.
- cost: Moderate engineering cost; network overhead minimal with efficient context encodings.  ·  latency: Negligible latency impact; designed for low-overhead real-time updates.
- security: Strong end-to-end encryption and user control reduce privacy risks.
- depends on: hardware next-gen pendant with local inference; software support on all surfaces for context management

### `model-routing` — Develop dynamic model routing that chooses specialized variants for computer vision tasks, natural language planning, and real-time conversational voice interaction, switching transparently between surfaces and models for optimal cost and latency.
- **owner gets:** The owner benefits from efficient use of computational resources, low-latency responses when needed, and high-fidelity task understanding and execution by picking the best model for each step in workflows spanning Mac, pendant, browser, and relay.
- effort: Medium engineering work to integrate model selection strategies, allocate workloads, and manage context synchronization across models and devices.  ·  risk: Potential consistency issues if model outputs diverge; risk mitigated by unified system orchestration and fallback policies.
- cost: Improved overall cost-efficiency by avoiding overuse of heavy models where unnecessary.  ·  latency: Lower mean latency by localizing light tasks and offloading heavy tasks appropriately.
- security: No direct impact but improves robustness and predictability of system.
- depends on: multi-surface context sharing; model selection APIs; robust orchestration framework

### `interaction` — Develop a flexible and adaptive Mac UI interaction library that combines accessibility API and subtle pixel analysis to enable robust computer vision based control without intrusive screen grabs or focus theft, tuned to ongoing user context and preferences.
- **owner gets:** This would let the owner have reliable autonomous Mac control by AI, even in complex or unusual app UIs, without sacrificing privacy or interrupting normal computer use, improving utility of the mac-vision loop.
- effort: Moderate to high effort: requires UI research, adaptive heuristics, user preference learning, and fail-safe modes.  ·  risk: Risk of UI interruptions or user confusion mitigated by reversible actions and graceful degradation to manual modes.
- cost: Moderate implementation and maintenance cost.  ·  latency: Designed for real-time responsiveness with minimal interference.
- security: Privacy-sensitive design reduces risk from pixel data.
- depends on: accessibility framework enhancements; pixel analysis tools

### `memory` — Integrate a persistent semantic memory store for Mac UI and user interaction history that feeds into the mac-vision agent's contextual understanding and action prediction, enabling long-term learning of user preferences and habits.
- **owner gets:** The owner gains a personalized AI agent that adapts to their unique workflows and preferences over time, enhancing efficiency and reducing repetitive instructions for similar tasks.
- effort: Moderate effort to build a robust semantic memory system and integrate with vision and planning agents.  ·  risk: Risk of privacy concerns mitigated by encryption, user control over memory retention and deletion.
- cost: Cost associated with storage and indexing, plus model usage for retrieval and update.  ·  latency: Minor latency impact, mostly offline or background processing.
- security: Requires strong access controls and encryption to protect sensitive user data.
- depends on: cross-surface context sharing; model support for semantic memory


## What it asked for

_Nothing._
