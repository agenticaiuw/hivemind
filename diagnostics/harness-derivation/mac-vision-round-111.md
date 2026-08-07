# Harness derivation — mac-vision — round 111

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision computer-use loop with safe, user-friendly, automated system permission handling and privacy assurances."
- **useful because:** This capability would let the owner have a fully autonomous and low-latency AI assistant on their Mac that can interact at the UI level, take screenshots, and perform complex multi-app workflows natively and visually, tasks that are impossible today without manual intervention.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second for UI control, conversation latency under 3 seconds
- **cost:** primarily model inference cost for guiding and responding, plus lightweight OS event watches; minimal continuous API calls unless actively running a task
- **security:** This requires explicit user consent to enable Accessibility and Screen Recording permissions, with transparent local-only processing and no data leaving the device without approval. A permission gate and audit trail should be included to prevent abuse and maintain trust.
- **missing:** OS-level automation for system permissions dialogs; A permission onboarding flow integrated with the pendant and Mac UI; A privacy and consent audit log for all mac-vision actions involving privacy-sensitive APIs

### "Seamless multi-modal handoff and coordination between mac-vision (pixel/UI control), mac-planner (planning and typed actions), mac-terminal (shell), and browser-extension for fluid, context-aware Mac task execution."
- **useful because:** Today, these separate capabilities exist but do not smoothly cooperate or escalate tasks between each other based on current UI state, complexity, or input mode. The owner cannot delegate a complex task and have it automatically fall through the best-suited surface for fast, reliable execution involving GUI, shell, browser, and planning layers, without manual switching or redundant input.
- **path:** mac-vision → mac-planner → mac-terminal → browser-extension → unified
- **model tier:** gpt-5.6-luna
- **latency:** latency-driven for UI actions (<1s), planning backgrounded under 5s, shell and browser control near real-time
- **cost:** higher due to cross-surface context synchronization and multiplexed model calls to handle different task modes and states
- **security:** Requires secure and trusted context bridging to preserve permissions and protect user data across different interaction modalities and browser vs OS boundaries. Consent must be continuous and in-the-moment where needed.
- **missing:** High-fidelity, real-time context synchronization across surfaces, including UI and shell states; A routing and escalation protocol for passing tasks automatically between surfaces with minimal friction; A shared state and history memory for task continuity across surfaces

### "Instant, low-latency contextual UI error detection and correction for Mac applications using combined pixel and accessibility-based vision from mac-vision, with real-time feedback on fixes."
- **useful because:** Currently, if a UI automation or control action fails due to unexpected layout changes or errors, the owner must manually intervene. The owner cannot have immediate AI help that visually detects UI errors or inconsistencies and proposes or tries corrective UI actions automatically, enhancing reliability and reducing frustration.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** <1 second feedback loops for error detection and correction
- **cost:** moderate due to image processing plus model inference for UI understanding and error recovery
- **security:** Requires continuous vision and UI state monitoring only with owner permission and offline/local processing where possible to protect privacy.
- **missing:** Robust UI error state detection models combining pixel and UI hierarchy data; Automated UI action retry and adaptation layer; Real-time error feedback and control loop integration with the agent stack

### "Enable full visual multi-application workflow automation that uses screen content analysis, UI hierarchy interpretation, and application state synchronization to seamlessly control diverse apps on the Mac as if human-operated across pixels and accessibility layers."
- **useful because:** Today, no system can reliably automate complex tasks that span multiple applications and require interpreting visual content, application states, and GUI elements combined. The owner should have AI assistance that understands what is on the screen, how apps relate, and coordinates actions across app boundaries to achieve goals quickly and intuitively.
- **path:** mac-vision → mac-planner → mac-terminal → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to a few seconds depending on task complexity
- **cost:** high due to multi-model fusion, continuous vision inference, and state synchronization
- **security:** Requires rigorous permission management, transparency about AI actions, and robust privacy protection due to deep UI and app access.
- **missing:** Cross-application state sharing and synchronization API; Fused visual+accessibility model for UI understanding across apps; A workflow engine that interprets multi-modal inputs and orchestrates cross-app actions


## What it asked for

_Nothing._
