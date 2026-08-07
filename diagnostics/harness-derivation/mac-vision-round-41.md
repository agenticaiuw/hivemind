# Harness derivation — mac-vision — round 41

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe autonomous Mac GUI interaction by mac-vision with full visual, accessibility, and confirmation context"
- **useful because:** The owner currently cannot safely enable mac-vision loop for autonomous computer use due to lack of screen recording consent, trusted accessibility snapshots, and UI hierarchy context. Enabling these would allow mac-vision to interpret screen pixels, UI structure, and take reversible GUI actions, vastly improving the owner's ability to delegate Mac control tasks that cannot be done via API or browser. This capability transforms low-level interaction into a cooperative, safe, high-precision agent.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** gpt-4.1-mini and gpt-5.6-luna collaborative loop
- **latency:** Real-time or near real-time interaction with sub-second UI feedback loops
- **cost:** Moderate API usage due to frequent visual and UI snapshot processing; heavier compute on Mac for screen capture and accessibility tree processing
- **security:** Screen recording and accessibility trust require clear owner consent and secure data handling to avoid privacy breaches. Confirmation gating must be enforced for destructive or irreversible actions.
- **missing:** Owner granted screen recording consent and accessibility trust; UI hierarchy snapshot context accessible to mac-vision; A robust confirmation gating system integrated with the action loop; More granular action classification and reversibility checks to minimize risk

### "Provide AI-augmented multi-modal situation understanding for mac-vision using combined pixel screenshots, accessibility tree, UI hierarchy snapshot, and voice context from pendant"
- **useful because:** Combining these multiple modalities at once, mac-vision can build a more complete, accurate, and robust mental model of the Mac's GUI state and user intent in real time. This would overcome individual technology limitations such as missing pixels, partial accessibility, or ambiguous voice commands, enabling more precise and context-aware automatic or semi-automatic GUI control.
- **path:** mac-vision → faculty-perception → relay-realtime → mac-planner → faculty-judgement
- **model tier:** GPT-5.6-luna for integration and decision making supported by GPT-4.1-mini for the vision tasks
- **latency:** Near real-time processing within a few hundred milliseconds per UI update cycle
- **cost:** Higher cost due to combined heavy processing from multiple inputs and integration but amortized by precision gains and reduced user corrections
- **security:** Sensitive visual and contextual data processing requires strong encryption and owner-controlled data retention. Voice and UI data must be handled with privacy in mind.
- **missing:** Unified multi-modal integration pipeline between vision, voice, and UI context; Hardware or OS capability to capture synchronized pixel, accessibility, and UI snapshot data streams; AGI-layer decision maker to reconcile conflicting modality data and produce robust situational understanding


## Changes it proposed to its own stack

### `hardware` — Upgrade MacBook and pendant hardware to allow zero-latency, encrypted, on-device pre-processing of pixel screenshots and accessibility trees, sending only high-value, filtered context to the cloud and local AI agents.
- **owner gets:** The owner benefits from privacy-preserving, faster, and more responsive GUI interaction and understanding without raw image data leaving devices, reducing latency and data costs while improving security.
- effort: Significant hardware and firmware redesign and engineering effort including chipset upgrades and sensor firmware changes.  ·  risk: High complexity and risk if hardware optimizations break current systems; requires careful testing and fallback modes.
- cost: High component and development cost; reduces cloud API usage cost by smarter pre-processing; minor power draw increase.  ·  latency: Significant latency reduction for GUI context processing.
- security: Improved data security by minimizing raw data exposure.
- depends on: Owner permission for screen recording and accessibility trust; Software pipeline to utilize pre-processed data

### `interaction` — Implement dynamic, context-aware visual confirmation and undo interface on the pendant and Mac for all mac-vision GUI actions, supporting reversible, auditable user control over autonomous actions.
- **owner gets:** This allows the owner to feel safe enabling autonomous GUI control on the Mac by having clear, immediate, and interactive feedback on every mac-vision action, preventing unintended destructive effects and facilitating quick reversals or corrections.
- effort: Moderate development on pendant UI, Mac UI, and agent communication protocols.  ·  risk: If the confirmation interface is not clear or responsive, the owner may misunderstand actions; requires thorough UX testing.
- cost: Minor computational and UI update cost; negligible API cost.  ·  latency: Adds slight latency for user interaction but improves trust and safety.
- security: Increases security by preventing unauthorized or malicious actions without owner acknowledgement.
- depends on: mac-vision vision loop permission and hardware capabilities; Integration with mac_run_actions or similar tools

### `model-routing` — Create a dedicated specialized AI model ensemble routing system that dynamically switches between vision, accessibility, voice, and UI action models on mac-vision surfaces depending on real-time confidence and context signals.
- **owner gets:** Optimizes accuracy, speed, and reliability of Mac autonomous control by using the best model or combination of models for each situation, reducing errors and maximizing effective assistance.
- effort: Medium effort to build routing logic, context detection modules, and interface between models.  ·  risk: Increased system complexity could cause routing errors or latency spikes if not well-tested.
- cost: Potentially higher API usage as multiple models may be queried; offset by reducing error-caused rework.  ·  latency: Careful optimization needed to avoid increased latency; expected to improve overall responsiveness in steady state.
- security: No major new concerns beyond current multi-model setups.
- depends on: Multiple AI models in place for vision, voice, UI actions; Real-time context and confidence signal availability

### `firmware` — Add secure local caching and ephemeral state management in the pendant firmware for mac-vision loop intermediate UI states and action confirmations.
- **owner gets:** Reducing dependency on network round-trips by caching transient UI states and pending approvals locally enables lower latency and higher reliability, improving the responsiveness and reliability of the autonomous interaction loop.
- effort: Moderate firmware development including secure storage and state sync protocols with the Mac and cloud relay.  ·  risk: Must handle state synchronization errors gracefully to avoid action confusion.
- cost: Minimal to moderate firmware memory and processing increase; no API cost change.  ·  latency: Significantly reduces interactive latency in low connectivity scenarios.
- security: Needs strong encryption and access control to maintain security of cached states.
- depends on: Pendant hardware support for additional secure storage; Software integration on mac-vision and relay sides

### `memory` — Implement persistent visual interaction memory on the Mac which tracks UI elements that were previously interacted with by mac-vision, including timestamps, outcomes, and owner feedback where available.
- **owner gets:** This memory allows mac-vision to build a historical context of UI interactions, helping to avoid repeated mistakes, customize future interactions for better precision, and provide explanations or revert actions based on past states.
- effort: Moderate software effort involving local databases and event logging on the Mac agent.  ·  risk: Potential data privacy concerns if memory leaks or is accessed improperly; requires secure storage.
- cost: Minor storage and processing costs on the Mac; no significant API cost.  ·  latency: No direct latency impact; improves interaction quality over time.
- security: Must be encrypted and access-controlled to prevent unauthorized access.
- depends on: Access to detailed UI interaction data from mac-vision; Owner consent for storing historical interaction data

### `dashboard-ux` — Develop an integrated dashboard interface that visualizes ongoing mac-vision activities, showing current UI state, planned actions, and past interactions with undo options.
- **owner gets:** This gives the owner transparent real-time insight into what mac-vision is doing on the Mac, builds trust through visibility and control, and enables corrections or undoing actions before they cause issues.
- effort: Moderate development effort involving frontend UI design and backend data integration.  ·  risk: UI overload risk if too much information is displayed; requires good UX design to remain clear and actionable.
- cost: Minor increase in local processing and network traffic; no additional API cost.  ·  latency: No latency impact on core interaction, but dashboard updates should be smooth and fast.
- security: Requires secure authentication and access controls to prevent unauthorized monitoring or control.
- depends on: Access to mac-vision action streams and states; Owner device capable of running the dashboard interface


## What it asked for

_Nothing._
