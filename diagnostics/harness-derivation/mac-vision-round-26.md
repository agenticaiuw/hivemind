# Harness derivation — mac-vision — round 26

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a safe and privacy-respecting AI vision control loop on my Mac for complex UI tasks."
- **useful because:** The owner would be able to delegate complex or multi-step Mac UI tasks that aren't available through APIs, including contextual interactions with apps that only exposing accessibility UI elements or vision can solve. This would extend AI help far beyond current static API capability, enabling proactive, hands-free assistance that otherwise requires manual control.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** realtime
- **latency:** sub-second to few seconds for confident UI reads and decisions
- **cost:** Moderate, dominated by real-time vision processing and interaction decision-making on device/server
- **security:** Privacy of screen pixel data; user confirmation for destructive actions; limit to reversible or read-only actions unless explicitly approved; UI observation limited to owner's Mac only; logs and transcripts must be stored securely; explicit opt-in for vision data upload or processing off-device.
- **missing:** ComputerUse loop must be enabled with visionUploadConsent from the owner; A robust typed action gating policy for all mac-vision UI interactions; Improved screen UI hierarchy snapshot access integrated with vision for fallback and confirmatory info; A hybrid computing pipeline combining vision and accessibility tiers dynamically according to task; Real-time state context awareness shared from mac-planner and relay-realtime agents


## Changes it proposed to its own stack

### `hardware` — Add a dedicated onboard neural vision processor in the MacBook hardware specifically optimized for real-time UI context analysis and gesture recognition at low power and high privacy.
- **owner gets:** Enables continuous AI vision tasks without draining battery or sending sensitive pixel data off-device, enabling always-on assistive UI capability with minimal latency and privacy risk.
- effort: High engineering and hardware design effort; requires collaboration with hardware manufacturers and OS-level integration.  ·  risk: Hardware cost increase and power consumption, potential delays due to design complexity, security risks if not properly sandboxed.
- cost: Significant hardware cost plus ongoing power usage, offset by efficiency gains in vision processing.  ·  latency: Improves to millisecond range for UI-related vision tasks.
- security: Enhances privacy by localizing vision processing; must be integrated with strong security controls.
- depends on: mac-vision software loop enabled with visionUploadConsent; OS APIs for dedicated vision hardware access

### `model-routing` — Implement a hybrid AI routing system that dynamically assigns UI understanding tasks between a lightweight local model on the Mac (mac-vision) for low-latency and privacy and a more powerful cloud model for complex visual context and natural language planning when network and consent permit.
- **owner gets:** Balances privacy, latency, and capability by keeping routine UI interactions local and offloading complex interpretations and long-term planning remotely only when needed and with consent.
- effort: Moderate software architecture and integration effort.  ·  risk: Potential latency spikes and privacy considerations if cloud fallback is not carefully controlled.
- cost: Overall cost balanced by efficient use of each model tier.  ·  latency: Improves responsiveness for routine tasks; cloud fallback increases latency only for rare complex analysis.
- security: Requires robust data handling policies and encrypted communication.
- depends on: mac-vision loop enabled and vision upload consent; cloud infrastructure for advanced vision and language reasoning

### `mac-harness` — Integrate typed action policy enforcement and transparent logging into the mac_run_actions executor in the Mac harness, to safely support reversible and irreversible UI actions with detailed receipts.
- **owner gets:** Ensures that any automated UI interactions initiated by the AI are auditable, controlled, and can be rolled back when supported, improving trust and safety for the owner to delegate sensitive tasks.
- effort: Moderate development effort to extend mac_run_actions and the action receipt system with typed classification and rollback hooks.  ·  risk: Complexity may introduce bugs; rollback support must be carefully implemented to avoid inconsistent states.
- cost: Small additional compute for logging and state management.  ·  latency: Minimal impact on action execution speed.
- security: Improves security posture by increasing transparency and control of automated actions.
- depends on: Existing mac_run_actions infrastructure; chg-5fc73ce3 for receipts system

### `integration` — Build seamless cross-agent context sharing for UI state, vision snapshots, and action outcomes between mac-vision, mac-planner, relay-realtime, and browser-extension agents.
- **owner gets:** Enables a collaborative multiperspective AI that can jointly interpret complex tasks and perform them safely and efficiently across devices and UI surfaces, overcoming single-agent limitations.
- effort: High integration and synchronization effort across multi-agent system and communication protocols.  ·  risk: Synchronization bugs, data consistency challenges, increased complexity in debugging and monitoring.
- cost: Higher network and compute costs due to context sharing and synchronization.  ·  latency: Some tasks may incur slight delay waiting for cross-agent confirmation or context updates.
- security: Requires robust encryption and access controls to protect context data in transit and at rest.
- depends on: Reliable network connectivity between agents; Shared schemas and protocols for UI and action context APIs

### `dashboard-ux` — Create a dedicated Mac AI control dashboard that surfaces mac-vision live UI context, planned/recent UI actions, and allows owner direct intervention, confirmation, or override.
- **owner gets:** Gives the owner transparency and control over AI-driven UI interactions, improving trust and reducing mistakes by providing clear feedback and manual override options.
- effort: Moderate front-end and back-end development effort.  ·  risk: UI complexity could overwhelm or confuse owner; must be designed for clarity and simplicity.
- cost: Minimal additional compute cost for dashboard rendering and data aggregation.  ·  latency: None to user actions, dashboard is passive control surface.
- security: Must be carefully access-controlled to prevent unauthorized use or exposure of sensitive data.
- depends on: mac-vision context sharing; mac-run_actions execution logs; integration cross-agent context APIs

### `memory` — Implement episodic memory tagging and recall for mac-vision to remember prior UI states, owner preferences, and common task sequences for faster context re-creation and personalized interaction.
- **owner gets:** Speeds up repetitive tasks, personalizes AI assistance based on learned owner preferences and historical context, reducing redundant UI navigation and improving efficiency.
- effort: Moderate software development for memory management and integration with vision loop.  ·  risk: Memory bloat or stale context interfering with fresh tasks; privacy concerns about stored visual data.
- cost: Incremental storage and compute costs for memory maintenance and retrieval.  ·  latency: Minimal, memory fetch is background-optimized.
- security: Sensitive visual and preference data must be encrypted and securely access-controlled.
- depends on: mac-vision loop enabled; Secure storage subsystems


## What it asked for

_Nothing._
