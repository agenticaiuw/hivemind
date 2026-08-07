# Harness derivation — mac-vision — round 30

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable invisible, non-interfering automation loop on the Mac to perform complex GUI tasks and multi-app workflows automatically, with safety and undo support."
- **useful because:** The owner can have more powerful, seamless automation for desktop apps that respects their focus and input control, reducing manual repetitive tasks without disrupting their work. Undo and transparency features build trust and safety.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** 100-250ms per action
- **cost:** Moderate; mainly on realtime model usage for quick loop decision making
- **security:** Automation requires careful permission gating to avoid accidental harmful inputs and privacy protections to avoid reading sensitive info without consent. Undo history mitigates risk.
- **missing:** Permission to enable computerUse.loopEnabled for mac-vision; Up-to-date UI accessibility hierarchy exposure service; Undo and action history tracking system integrated with mac-vision; Human-readable action explanation generator; Runtime gating on destructive or irreversible actions requiring explicit approval

### "Create an integrated browser account monitoring and response drafting system that automatically monitors all logged-in web accounts for urgent updates, summarizes them, and drafts replies that the owner can review before sending."
- **useful because:** The owner saves time and gains confidence by only seeing summarized important messages needing attention and by having draft replies prepared automatically, preventing missed or delayed actions.
- **path:** browser-extension → relay-realtime → mac-planner → faculty-judgement
- **model tier:** background
- **latency:** minutes per update
- **cost:** Moderate to high, as it involves continuous page watching, extraction, NLP summarization, and drafting models
- **security:** Requires deep authenticated browser access and secure storage of drafts; drafts should never send without explicit owner approval; data privacy and correct handling of session states critical.
- **missing:** Full registry and enumeration of logged-in web accounts automatically; Urgency scoring models for web page text content; Automatic reply draft generation from page content; Draft storage and management system with safe review workflow; Authenticated page-watch orchestration service with API


## Changes it proposed to its own stack

### `integration` — Build a typed action orchestrator that accepts structured UI and web interaction requests, classifies each as read-only, reversible mutation, or high-impact mutation, and routes them automatically to mac-vision (for UI), browser-extension (for web), or mac-planner (for broader system control). Include a user-approvable queue for high-impact mutations and integrated undo support across surfaces.
- **owner gets:** The owner gets safe, dependable automation over multiple surfaces controlled as a unified system, avoiding accidental data loss or improper automation while simplifying complex workflows.
- effort: High engineering effort across stack layers for typed action schemas, routing logic, and consistent undo support.  ·  risk: Incorrect classification could cause undesired effects; mitigated by approval gating and undo capability.
- cost: Medium server and realtime model costs for classification and orchestration, moderate development time.  ·  latency: Low additional latency; mainly routing overhead.
- security: Centralized control reduces attack surface and facilitates audit; needs best practice for approval flow.
- depends on: Permission for mac-vision loop enable; Up-to-date UI and browser context APIs

### `hardware` — Add a privacy-preserving hardware module to the MacBook specifically designed to support secure, local UI event logging and replay for automation, with end-to-end encryption and tamper evidence, enabling auditability of all automated interactions without exposing raw screen content.
- **owner gets:** The owner gains transparency and accountability for all automated actions performed by the AI, increasing trust and enabling debugging without risking privacy breaches or screen content leaks.
- effort: Significant hardware and firmware design required, plus integration with mac-vision and audit systems.  ·  risk: Possible complexity and cost increase; mitigated by strong encryption and UI feedback.
- cost: High hardware development and integration cost; potential increased power usage.  ·  latency: Negligible on user interactions; background audit process.
- security: Strongly increases security and privacy guarantees; requires secure key storage and firmware validation.
- depends on: mac-vision loop enable; Automation action logging and audit system

### `new-surface` — Develop a wearable pendant-based voice interaction surface tightly integrated with mac-vision's screen content and UI state awareness, enabling hands-free contextual command refinement and approval for automated Mac GUI tasks.
- **owner gets:** The owner can seamlessly authorize or modify in-progress automation tasks vocally without switching focus to the Mac, making automation safer and more natural for mobile or multitasking contexts.
- effort: Moderate to high integration effort for real-time UI state sharing and voice interface design; dynamic context handoff needed.  ·  risk: Voice misrecognition risks mitigated by confirmation UI; requires robust privacy controls for audio processing.
- cost: Moderate ongoing compute and model usage costs for voice and UI inference.  ·  latency: Moderate latency constraints for real-time interaction responsiveness.
- security: Need strong protection on voice data and integration channel; local processing favored.
- depends on: mac-vision loop enable; Pendant hardware voice input and processing capability; Low-latency UI state sharing system

### `model-routing` — Implement an intelligent model routing system that dynamically assigns parts of multi-step automation or web interaction tasks to the most appropriate model instance (mac-vision realtime loop, background browser analysis, relay real-time voice, or mac-planner agent) based on latency, capability, and cost efficiency.
- **owner gets:** The owner benefits from optimized use of compute resources, reduced cost, and faster responses by leveraging the strengths of each tier and surface without manual switching or redundant work.
- effort: Moderate development effort for dynamic routing heuristics and load balancing.  ·  risk: Routing mistakes could cause delays or suboptimal results but can be monitored and corrected.
- cost: Potential cost savings by leveraging slower cheaper models for heavy background tasks.  ·  latency: Reduced latency for interactive steps due to dynamic routing.
- security: Routing system should respect data locality and privacy boundaries.
- depends on: Defined capability and latency profiles of models; Cross-surface communication protocols

### `memory` — Create a long-term contextual memory system that stores fragmented, compacted UI interaction histories, action outcome data, and user correction feedback, enabling mac-vision and other surfaces to learn from past actions to improve reliability and personalize behaviors.
- **owner gets:** The owner experiences progressively smarter and more reliable automation that adapts to their workflow patterns, reducing repeated mistakes and improving task completion success over time.
- effort: High effort involving data storage design, retrieval algorithms, and integration into action planning and evaluation.  ·  risk: Memory errors or stale data could cause automation flaws; mitigated by decaying confidence and user correction channels.
- cost: Moderate storage and model inference cost; mainly background processes.  ·  latency: Minimal impact on interaction latency; mainly offline processing.
- security: Memory data must be encrypted and access controlled to protect privacy.
- depends on: Typed context and action result schemas; User feedback and correction interfaces

### `dashboard-ux` — Develop a unified automation control dashboard that displays real-time mac-vision loop actions, browser account monitoring summaries, automation queue status, undo history, and contextual explanations of what the AI is doing or proposing, with easy manual override and editing.
- **owner gets:** The owner gains full visibility and control over all ongoing and planned automations, reducing uncertainty and increasing trust while enabling efficient manual intervention when desired.
- effort: Moderate UI/UX engineering effort plus backend integration across all automation surfaces.  ·  risk: Complex UI could overwhelm users; mitigated by progressive disclosure and customization.
- cost: Mainly frontend development cost; low runtime cost apart from data aggregation.  ·  latency: No impact on automation latency; dashboard is informational.
- security: Dashboard must be secured with authentication and encrypted communication.
- depends on: Centralized logging and action history system; Cross-surface status reporting protocols


## What it asked for

### `p3-p2ab` (permission) — computerUse.loopEnabled
- why: Enable mac-vision's accessibility-mode UI interaction loop to automate GUI tasks on the Mac without taking over screen or keyboard focus, enhancing automation and productivity safely.
- risk it sees: Allowing the loop enables UI interaction automation, which could mistakenly trigger unwanted UI actions or changes if bugs occur. However, the loop uses the accessibility tier designed to avoid screen focus and cursor disturbance, mitigating risk.

