# Harness derivation — mac-vision — round 70

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Owner-guided AI spotlight mode on Mac GUI for just-in-time help and insights"
- **useful because:** Today the owner cannot selectively highlight parts of the Mac UI or request focused help on a particular app window or UI element easily. An 'AI Spotlight' feature would allow them to point or indicate UI areas to get explanations, command suggestions, or automated workflows, improving productivity and reducing friction.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** moderate per invocation due to UI analysis and language model inference
- **security:** Needs strong UI privacy protections and transparent user controls to avoid unwanted UI inspection.
- **missing:** Fine-grained UI element selection and explanation facility; Real-time contextual UI understanding with language model integration

### "AI-driven smart multitasking and app Interaction Orchestration on Mac"
- **useful because:** Currently, the owner cannot have the AI seamlessly coordinate multiple Mac apps with GUI automation, delegation, and context sharing to accomplish complex chores with minimal manual intervention. Smart orchestration would enhance productivity and reduce cognitive load.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate to high depending on multitasking complexity
- **security:** Needs strict data flow and permission controls between apps; transparent orchestration logs are required.
- **missing:** Inter-app context sharing and synchronization mechanism; Advanced multi-app UI delegation workflows with error recovery; Session continuity across surfaces and sessions


## Changes it proposed to its own stack

### `integration` — Add a secure and transparent permissions gate in the pendant and Mac agent to enforce progressive enablement of the mac-vision loop based on explicit user consents for accessibility, screen recording, and vision upload. Include UI indicators and logs for all permission and loop state changes so the owner retains full observability and control. This gate would allow initial low-risk accessibility-only actions followed by phased enablement of pixel-level control and screen uploads as the owner authorizes.
- **owner gets:** The owner gains a clear, controlled path to enable advanced AI-driven computer use on their Mac with full transparency and control over privacy and automation scope. This avoids unsafe or surprising automation and builds trust over time.
- effort: Medium to large; requires collaboration between pendant firmware, Mac agent, and user interface components.  ·  risk: Permissions and UI indicators might interact complexly; incorrect state publication or UI bugs could confuse the owner. Careful testing and fallback needed.
- cost: Small CPU/network cost; mostly development effort.  ·  latency: None to minor.
- security: Improves security by enforcing explicit consent and observability.
- depends on: permissions system updates; UI for visibility and controls

### `hardware` — Upgrade pendant hardware to include a secure, dedicated trust enclave chip to store user permissions and consents locally and enforce privacy policies on screen capture upload and loop activation. This chip could provide cryptographic attestation of granted permissions and loop state to ensure integrity and prevent unauthorized escalation.
- **owner gets:** Owner gains enhanced privacy and control guarantees, reducing risk that sensitive screen contents or automation privileges could be accessed or escalated without their knowledge. Trust on a hardware root limit increases confidence in AI automation capabilities.
- effort: Significant hardware design and validation effort, plus firmware and software integration.  ·  risk: Hardware and firmware bugs or manufacturing defects could create locks or insecurities; mitigations needed.
- cost: Moderate increase in device cost and power draw.  ·  latency: None.
- security: Substantial increase by providing hardware root of trust for permissions.
- depends on: firmware to interface with trust enclave; OS and mac agent modifications

### `model-routing` — Implement a specialized vision model routing layer that dynamically chooses between running vision inference locally on the pendant or offloading to cloud models, based on current consent, bandwidth, privacy needs, and task complexity. This model router would manage encrypted transmission of screen images and ensure minimal data leave the owner's environment unless strictly permitted.
- **owner gets:** Provides a flexible tradeoff to meet the owner's privacy and latency needs while enabling powerful vision-based UI understanding and automation. The owner can control where and how their screen data is processed, aligning with their trust level and network conditions.
- effort: Medium to high; requires coordination between pendant software, relay, cloud models, and mac agent.  ·  risk: Complexity could introduce bugs or inconsistencies. Data leakage risks if encryption and policy enforcement fail.
- cost: Variable cloud compute costs.  ·  latency: Improves latency by locally running simple vision tasks, offloading heavier ones.
- security: Enhances security by strict routing and encryption of vision data.
- depends on: firmware/pendant updates; relay and cloud model coordination; consent gates

### `memory` — Create a persistent, fine-grained UI interaction memory cache for the mac-vision loop that records UI contexts, actions, outcomes, and errors with timestamps. This memory enables the agent to learn from repeated tasks, streamline interaction flows, and improve error recovery during multitasking and automation orchestration.
- **owner gets:** The owner benefits from smoother, personalized computer use automation with fewer repetitive corrections, quicker recovery from failures, and better adaptation to UI changes over time.
- effort: Medium software development effort across mac-vision agent and backend synchronization.  ·  risk: Memory corruption or stale data could cause erratic automation behavior, so robust validation and fallback are needed.
- cost: Modest storage and compute overhead.  ·  latency: Negligible if designed well.
- security: Requires encryption and access controls to protect memory privacy.
- depends on: mac-vision loop enabled; backend storage and sync


## What it asked for

_Nothing._
