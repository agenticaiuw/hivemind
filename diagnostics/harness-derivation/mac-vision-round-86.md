# Harness derivation — mac-vision — round 86

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a multi-modal perception system integrating accessibility data and pixel-based screen captures for robust, fallback-capable UI state understanding."
- **useful because:** Owner currently cannot have fully reliable UI perception due to lack of either accessibility permissions or pixel-based vision. A hybrid system leveraging both modalities can gracefully degrade and enable continuous operation even if some permissions are refused or temporarily revoked.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** Mixed local and cloud models
- **latency:** Real-time or near real-time for UI understanding
- **cost:** Moderate, involves updating perception service and training hybrid models
- **security:** Pixel captures require strict privacy handling; accessibility data less sensitive but still controlled
- **missing:** Integration of accessibility and pixel data into a unified perception model; Fallback and recovery mechanisms per modality

### "Enable owner-driven undo and audit trail interface for all autonomous Mac UI actions taken by the AI vision loop"
- **useful because:** Because the autonomous UI loop can make mistakes or unwanted changes, having a clear undo and audit interface empowers the owner to review and revert any undesired changes, increasing trust and safety.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** Low-latency small models for interaction, bigger ones for classification and summarization
- **latency:** Undo queries and commands should be near real-time
- **cost:** Low to moderate; dominated by query processing and storage
- **security:** Audit data contains sensitive activity logs and must be stored securely with controlled access
- **missing:** UI action receipt and reversible command framework; User interface for undo and audit

### "Integrate the mac-vision agent with the browser-extension agent for seamless cross-app workflows involving web browsing and local app control"
- **useful because:** The owner cannot currently have tightly integrated workflows that combine web browsing automation with local Mac GUI actions. Enabling this integration would allow more sophisticated task completion like data extraction from web pages followed by local app processing.
- **path:** mac-vision → browser-extension → mac-planner → faculty-judgement → faculty-action
- **model tier:** Real-time models on mac-vision for UI, browser models for web context
- **latency:** Seconds for data handoff and action sequencing
- **cost:** Moderate due to multi-agent communication and model coordination
- **security:** Cross-agent data transfer must be controlled to avoid leaking sensitive info
- **missing:** Inter-agent communication protocols for task handoff; Unified state representation across Mac UI and browser contexts


## Changes it proposed to its own stack

### `hardware` — Add a secure enclave coprocessor on the Mac to handle vision privacy and real-time UI capture locally, enabling pixel-level screen understanding without transmitting raw screen data outside the device.
- **owner gets:** This hardware change would allow visual UI loops to operate with privacy and security guaranteed by hardware, making owner consent and trust easier to obtain and reducing risk of sensitive data leaks.
- effort: Medium to high, requiring hardware design and OS integration  ·  risk: Hardware and OS integration bugs could cause lockouts or data leakage if mishandled, mitigated by thorough testing and fail-safe modes
- cost: Increased device cost by a moderate amount, negligible impact on power draw  ·  latency: Improves latency by localizing screen processing
- security: Significantly increases security and privacy for screen capture and visual UI analysis

### `interaction` — Implement a context-sensitive owner approval interface that dynamically prompts the owner only for high-impact or irreversible computer UI actions during autonomous use loops, minimizing friction but maintaining control.
- **owner gets:** The owner needs to trust that the AI won't perform undesired destructive actions. Having an intelligent gating system that only interrupts for critical operations reduces annoyance and increases acceptance of autonomous control.
- effort: Moderate, requires AI integration with UI action classification and a seamless permission interface  ·  risk: Potential to misclassify actions and frustrate owner or miss urgent approvals, mitigated by logs and fallback manual override
- cost: Minimal  ·  latency: Low latency impact as prompts can be asynchronous
- security: Enhances overall trustworthiness and safety of the system
- depends on: Enable full visual UI loop on Mac for autonomous multi-step computer use and interface control

### `model-routing` — Develop an AI model composition and routing framework that dynamically allocates tasks between local Mac-based agents for fast UI actions and cloud-based agents for complex reasoning and long-term planning, optimizing latency, cost and security trade-offs.
- **owner gets:** The owner benefits from seamless, efficient, and secure AI assistance with the system selecting the best computation placement for each task transparently and automatically.
- effort: High, requires advanced model orchestration and routing infrastructure integrated with all agent surfaces  ·  risk: Increased system complexity and potential points of failure mitigated by robust monitoring and fallback mechanisms
- cost: Cost reduction via optimized cloud usage; increased initial development cost  ·  latency: Improves responsiveness by offloading lightweight tasks locally
- security: Can be designed to minimize data exposure by localizing sensitive tasks

### `dashboard-ux` — Build an owner-facing dashboard interface that lets the owner monitor, approve, review, and undo autonomous UI actions taken by mac-vision in real time, with rich visual logs and explanations.
- **owner gets:** Currently the owner has no way to oversee or control what the AI agents do on their Mac proactively. A dashboard with transparency and direct control improves trust, safety, and usability.
- effort: Moderate, requires UI/UX design and integration with existing mac-vision action receipts and telemetry  ·  risk: Potential overwhelm of owner if not well-designed, mitigated by progressive disclosure and summarization
- cost: Low to moderate  ·  latency: None on core loop, as this is mostly passive interface
- security: Must securely authenticate the owner and audit all actions shown
- depends on: Enable owner-driven undo and audit trail interface for all autonomous Mac UI actions taken by the AI vision loop


## What it asked for

_Nothing._
