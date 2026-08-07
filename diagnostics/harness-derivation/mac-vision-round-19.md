# Harness derivation — mac-vision — round 19

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe and privacy-preserving mac-vision interaction on Mac using accessibility APIs only, without pixel screenshots or focus stealing"
- **useful because:** The owner can get meaningful computer control and AI agent assistance through UI automation that respects privacy and does not interfere with their current work or screen content
- **path:** mac-vision → relay-realtime → mac-planner → pendant
- **model tier:** realtime
- **latency:** low-latency (under 500 ms per action)
- **cost:** low cost, mostly model inference for UI understanding and command generation; no image upload or heavy pixel processing
- **security:** No visual data leaves the device reducing privacy risk; minimal escalation as only accessibility APIs are used; must ensure actions are reversible or safely constrained
- **missing:** Full accessibility trust and enablement on Mac agent; A UI hierarchy snapshot context accessible to mac-vision; A defined low-risk action policy limiting mac-vision to only non-focus-stealing, non-pixel actions

### "Perform robust UI element identification and interaction through multi-modal combining accessibility tree parsing and localized computer vision on the Mac without uploading images"
- **useful because:** Enhances mac-vision agent's ability to understand complex or custom UI elements not fully exposed through accessibility APIs alone, improving accuracy and task success
- **path:** mac-vision → mac-planner
- **model tier:** realtime with background refinement
- **latency:** sub-second for interaction; async refinement for accuracy
- **cost:** Moderate, depends on vision model complexity and compute resources used locally
- **security:** No user screen images leave the Mac; only derived signals stored transiently
- **missing:** Combined accessibility and pixel data processing skill; Vision model embedded for local use on Mac; UI element mapping models for custom or complex app controls


## Changes it proposed to its own stack

### `hardware` — Add a local vision processing hardware accelerator to the AI Pendant device to enable real-time image processing and vision model inference on the device itself without uploading images to the cloud or the Mac
- **owner gets:** This would enable privacy-preserving, instant visual understanding and interaction assistance from the pendant device itself, bypassing the need for risky upload consent or reliance on Mac resources for vision tasks
- effort: Medium hardware development effort plus firmware and software integration  ·  risk: Minimal since no image data leaves device; recovery via fallback to cloud vision if needed
- cost: Moderate due to specialized chip; low ongoing power cost with efficient design  ·  latency: Greatly reduced latency for visual tasks, near-instant feedback
- security: High privacy due to local processing and storage, reducing external data exposure
- depends on: Enhanced device firmware; Vision model integration at hardware level; New mac-vision skills to coordinate pendant vision with Mac actions

### `integration` — Build a secure policy and audit framework to mediate and log all mac-vision loop interactions, including a typed action classification system with owner review of high-impact or irreversible commands
- **owner gets:** This allows turning on the full mac-vision computerUse loop safely with owner confidence, maintaining transparency and control over the AI agent's actions on their Mac, preventing mistakes or abuses
- effort: Medium software effort to integrate action brokering, logging, policy enforcement, and user interface for owner review/override  ·  risk: If improperly designed, could add latency or fail to catch all risky actions; mitigated by thorough testing and stepwise rollout
- cost: Small additional compute cost for policy checking and logging  ·  latency: Some slight latency increase for safety checks, acceptable within human reaction time
- security: Strongly improved security posture with audit trail and owner governance
- depends on: Full control mode of mac-vision; Access to all relevant mac agent telemetry and action intents

### `interaction` — Implement a graduated permission and confirmation system for mac-vision actions including contextual prompts, undo options, and time-limited elevated privileges to reduce risk of accidental harmful mutations
- **owner gets:** Provides a smooth, owner-centric experience that balances automation and safety, letting the owner build trust and confidence in the AI assistant while retaining ultimate control
- effort: Medium UX and logic effort across pendant, Mac UI, and relay platforms  ·  risk: If UX is poor could annoy or confuse the owner; mitigated by user testing and iterative improvement
- cost: Low to moderate based on number and complexity of confirmation dialogs across platforms  ·  latency: Marginal impact, should be minimal with good design
- security: Improves safety by preventing unwanted or mistaken command execution
- depends on: Full multi-node integration; Capability to receive real-time prompts and owner responses

### `model-routing` — Develop a dynamic routing system that assigns tasks to the most appropriate model or device (pendant, Mac, cloud) based on latency, privacy, and capability requirements in real-time
- **owner gets:** Optimizes the owner's experience balancing speed, privacy, and capability, automatically leveraging the best resource for each interaction, seamlessly from the owner's perspective
- effort: High system design and engineering effort for robust routing and fallback handling  ·  risk: If routing is incorrect, user experience may suffer; needs careful monitoring and adjustment
- cost: Variable depending on cloud usage; reduces unnecessary expensive calls  ·  latency: Reduces overall latency by using closest or best resource
- security: Improves privacy by keeping sensitive data local when possible
- depends on: Full multi-device integration; Realtime telemetry and context sharing

### `memory` — Integrate short-term visual and interaction context memory for the mac-vision agent to track UI states and user intents across steps without re-querying the accessibility tree or taking new snapshots constantly
- **owner gets:** Increases efficiency and responsiveness during complex multi-step interactions by remembering previous UI states and actions, reducing redundant queries and improving coherence
- effort: Medium software effort for memory management and integration across vision and UI parsing modules  ·  risk: If memory is stale or incorrect, actions may be misguided; mitigated by policy resets or refresh triggers
- cost: Low relative to overall system cost  ·  latency: Improves perceived latency by reducing round-trips for repeated info
- security: Minimal, as memory is local and ephemeral
- depends on: UI snapshot access; Reliable state change detection

### `dashboard-ux` — Create a dedicated mac-vision control dashboard accessible on Mac and via the pendant to monitor, review, and manage vision loop activity, permissions, and safety logs in real time
- **owner gets:** Allows the owner to trust and control mac-vision interaction more intuitively and transparently, with direct feedback on what the AI is seeing and doing
- effort: Medium UI design and integration effort across devices  ·  risk: If UX is poor, the owner may misunderstand or ignore important safety info; careful design needed
- cost: Low  ·  latency: None on interaction latency
- security: Improves security and trust with real-time monitoring and auditability
- depends on: Live data feed from mac-vision processes; User authentication and session management


## What it asked for

### `c4-o9kf` (context) — ui_hierarchy_snapshot
- why: To understand the current UI structure and state for enabling safe and effective mac-vision agent actions
- would change: With UI snapshot I can reason about what elements exist, where focus is, and what the owner is interacting with

