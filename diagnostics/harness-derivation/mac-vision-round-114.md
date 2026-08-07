# Harness derivation — mac-vision — round 114

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full Mac UI control with safety and privacy safeguards"
- **useful because:** The owner should be able to ask the Mac vision agent to perform complex multi-step UI interactions on the Mac, such as navigating menus, clicking buttons, typing text, and running scripts that cannot be done through APIs alone, enabling complete hands-free computer use. This includes enabling the computerUse loop and uploading vision data with stringent user consent and confirmation for all consequential actions.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini onboard with gpt-5.6-luna for planning and judgment coordination
- **latency:** Real-time interactive latency of under 2 seconds for direct UI actions; background multi-step workflows can be slower
- **cost:** Moderate API usage cost with occasional background planning; primarily dominated by vision data processing and orchestration
- **security:** Vision data must be encrypted and stored minimally; actions must require explicit owner confirmation before state-changing or sensitive commands; accessibility and screen recording permissions must be explicitly granted by the owner, and any failure should immediately disable the loop to protect privacy.
- **missing:** A secure toggle for computerUse.loopEnabled managed through explicit owner consent and messaging; A privacy-preserving vision upload consent system integrating the pendant and Mac; Explicit OS permission gating and automated detection for Accessibility and Screen Recording rights; A fail-safe confirmation and revert system for any high-impact UI actions; Contextual live UI hierarchy snapshots with history to enable reliable UI navigation without pixel data

### "Provide AI-guided visual confirmation and correction for Mac UI actions"
- **useful because:** The owner should be able to request the AI to show them predicted UI changes before making irreversible interactions on the Mac. This would mitigate mistakes due to UI drift or unexpected side effects by letting the owner approve or correct actions at a visual level using AI-annotated screenshots or UI state summaries.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-judgement
- **model tier:** gpt-5.6-luna for detailed visual and UI reasoning with gpt-4.1-mini assisting on Mac
- **latency:** Under 5 seconds for generating visual predictions and confirmation prompts
- **cost:** Moderate API calls due to image understanding and AI interaction loops
- **security:** Screenshots must be transient and encrypted; confirmation prompts must require explicit owner approval; no irreversible actions before approval.
- **missing:** Capability to capture and analyze UI screenshots in real-time; AI module for predictive UI action simulation and visual annotation; User interaction surface on both the pendant and Mac for approval and corrections

### "Seamless multi-agent coordination for complex Mac workflows combining visual UI control and browser interaction"
- **useful because:** The owner should be able to initiate complex workflows that span multiple applications including desktop and browser environments, with coordination among mac-vision (UI control), browser-extension (browser automation), mac-planner (planning), and relay-realtime (voice interaction) agents. This makes the system truly integrative and responsive across the entire computing environment.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → faculty-judgement
- **model tier:** Primarily gpt-5.6-luna for orchestration and planning, with gpt-4.1-mini support for fine UI actions.
- **latency:** Workflow orchestration under 3 seconds for initial commands; longer workflows allowed more time.
- **cost:** Moderate, dominated by planning and multi-agent coordination API calls.
- **security:** Secure cross-agent communication channels must be authenticated and encrypted; agent roles and scopes strictly enforced to avoid privilege escalation; sensitive data sharing minimized and logged.
- **missing:** Robust inter-agent messaging and state management protocols; Unified workflow specification language understood by all agents; Dedicated orchestration agent or framework to manage agent collaboration

### "Integrated confirmation and rollback manager for Mac UI actions"
- **useful because:** The owner should be able to request that any multi-step or high-impact UI action sequence executed by mac-vision or delegate agents can be confirmed before final commitment, with built-in rollback mechanisms to undo any undesirable changes automatically or manually. This would greatly increase trust and safety of automated UI control.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for monitoring and management, with gpt-4.1-mini assistance for low-latency UI feedback and queries.
- **latency:** Real-time updates under 2 seconds for confirmation prompts; rollback may vary based on task complexity.
- **cost:** Low to moderate API usage for state tracking and rollback commands.
- **security:** Rollback state must be securely stored and access controlled; confirmation prompts require explicit owner authentication; no irreversible changes allowed without approval.
- **missing:** State snapshot and change tracking for all UI actions; User interaction surfaces for confirmation on pendant and Mac; Automated rollback command generation and execution framework


## What it asked for

_Nothing._
