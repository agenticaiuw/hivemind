# Harness derivation — mac-vision — round 102

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow mac-vision to automate and verify multi-step Mac workflows that require combining accessibility insights, screenshots, and app state to handle ambiguous situations, interruptions, and error recovery"
- **useful because:** Owners often need automation not just of single UI steps but entire multi-app workflows involving decision points, UI feedback loops, and recovery from failure. Mac-vision today is limited as it is not enabled or integrated fully. Enabling this capability would provide robust, resilient automation that adapts dynamically.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** seconds for multi-step decision making; quick reaction for UI state changes
- **cost:** Moderate API and compute cost to maintain state, model interaction, and image processing
- **security:** Requires persistent local state, extensive accessibility permissions, and possibly user confirmation prompts on unclear actions to prevent errors or destructive changes
- **missing:** A practical Mac UI workflow orchestrator combining pixel and accessibility inputs; Capability to pause and resume multi-step workflows dynamically; Stateful error recognition and recovery policies; Explicit user consent for persistent UI control with feedback loop; Integration of typed action control with the vision and UI snapshot data for safe execution

### "Integrate mac-vision's pixel- and accessibility-based UI understanding with the owner's Mac habits learned by mac-planner and relay-realtime to proactively offer UI shortcuts and task suggestions tailored to context and history"
- **useful because:** The owner would get predictive Mac UI assistance that anticipates their next needed actions, reducing friction and repetitive work, while dynamically adapting to context changes detected visually and by accessibility data.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background with realtime alerts
- **latency:** sub-second for suggestions; background learning over hours/days
- **cost:** Low to moderate, mostly background model usage and periodic UI snapshot analyses
- **security:** Requires sharing user interaction and habit data across multiple services and devices; must be encrypted and privacy-preserving
- **missing:** A context history store correlating UI states from vision and accessibility with executed actions and user feedback; A model or system to generate predictive UI shortcuts and suggestions; Seamless low-latency data exchange and control coordination between mac-vision, mac-planner, and relay-realtime

### "Provide a realtime visual error detection and alerting system for mac-vision that detects UI states indicating failures or errors during multi-step workflows and proactively notifies the owner or pauses automation"
- **useful because:** Prevents unintended destructive actions or status confusion by automatically detecting common UI error signals like modal dialogs, error banners, or unexpected navigation, improving reliability and safety of automation
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-second detection and alerting
- **cost:** Moderate due to continuous vision monitoring and model inference
- **security:** May involve persistent screen content analysis and pattern detection; requires owner consent and privacy safeguards
- **missing:** Image classification models trained on error states; Integration with mac-vision action cancellation and pausing logic; User notification and confirmation interface


## Changes it proposed to its own stack

### `integration` — Create a real-time context synchronization and action coordination system between mac-vision, mac-planner, and relay-realtime to fuse visual UI state, planning context, and live voice commands for seamless proactive Mac task assistance
- **owner gets:** Integrates distinct data streams and capabilities into a unified assistant that can see, plan, and act with full context and responsiveness
- effort: Medium engineering effort across multiple agents and relay backend  ·  risk: Complex coordination bugs or latency could degrade user experience, but can be mitigated with staged rollout and monitoring
- cost: Moderate due to increased RPC and state synchronization overhead  ·  latency: Critical to keep sub-second responsiveness
- security: Requires careful encryption and user consent for data streams and commands
- depends on: mac-vision with loop enabled and full permissions; relay-realtime with robust voice and event handling; mac-planner with planning and local state persistence

### `hardware` — Add a dedicated low-latency vision coprocessor and secure screen capture hardware in the Mac or pendant to accelerate UI image processing and enable fast, battery-efficient live visual analysis for mac-vision
- **owner gets:** Greatly improves performance, responsiveness, and battery life for real-time UI vision tasks, enabling seamless full visual automation with minimal delay
- effort: High: requires hardware design, firmware, and OS integration work  ·  risk: Hardware integration issues or delays; increased power draw if not optimized; requires secure trusted computing environment to protect sensitive screen data
- cost: Increased hardware cost; amortized over product lifecycle  ·  latency: Significant latency reduction in visual processing pipeline
- security: Must ensure screen data is locally encrypted and access controlled
- depends on: Firmware that supports low-latency screen capture; OS support for secure hardware-assisted image processing


## What it asked for

### `c8-llz6` (context) — ui_hierarchy_snapshot
- why: To understand current UI state for mac-vision to decide next actions by accessibility tier
- would change: Allows reasoning about screen elements without needing raw screenshots

### `c9-e3xc` (context) — pending_goals
- why: To know pending semantic goals/tasks that mac-vision might act on
- would change: Helps focus actions on highest priority tasks

