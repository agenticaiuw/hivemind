# Harness derivation — mac-vision — round 52

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable trusted, reliable, and safe computerUse loop on Mac to allow full AI-driven UI control and automation including screenshots, clicks, typing, and app control without user focus loss."
- **useful because:** The owner can delegate complex and multi-step computer tasks to AI with confidence, greatly boosting productivity and reducing manual input effort, while ensuring actions are safe, reversible, and auditable.
- **path:** pendant → mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** sub-second for interactive control, up to a few seconds for UI confirmation steps
- **cost:** medium API cost due to frequent minimal screenshot uploads and UI interpretation; mostly compute and bandwidth
- **security:** Requires explicit Accessibility and Screen Recording permissions granted by owner to AI Pendant Agent app; potential for misoperation or privacy leak if permissions are abused; must retain user control to disable or confirm high-impact actions
- **missing:** Accessibility and Screen Recording permission onboarding and validation flow; Allowlist of safe shell commands for mac_run_actions; Robust mechanism for permissions verification and failover; Explicit user consent for highly sensitive actions; Local UI hierarchy snapshot capability without visual intrusion, aligned with granted permissions

### "Transparent allowlist of safe shell commands for mac_run_actions to inform owner and enforce AI task safety."
- **useful because:** Owner understands what shell commands AI can run, improving trust and security. Allows safe expansion of shell capabilities with clear boundaries.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** instantaneous response for command validation
- **cost:** minimal, software-only
- **security:** Prevents arbitrary code execution, limits attack surface and accidental harm.
- **missing:** UI or voice interface for owner to review and suggest shell commands additions; Safe command parsing and validation enforcement


## Changes it proposed to its own stack

### `model-routing` — Introduce an improved action classification and routing system that dynamically selects between reversible typed actions, multi-step delegation, and browser-based controls based on real-time UI and permission context, enabling fail-safe fallbacks if permissions are missing or revoked.
- **owner gets:** Allows AI to provide optimal control over the full Mac environment by choosing safe, effective methods given current permissions and UI accessibility, reducing failure and improving trust in automation.
- effort: Medium engineering effort to implement routing logic, testing, and integration with permission state management.  ·  risk: Misrouting could cause delays or incomplete task execution; requires thorough testing and monitoring to catch regressions.
- cost: Slight increase in processing overhead to evaluate routing conditions.  ·  latency: Negligible added latency; mostly done in logic steps before action.
- security: Improves security by avoiding actions when permissions are insufficient, preventing unauthorized control.
- depends on: Accessibility and Screen Recording permission validation infrastructure

### `hardware` — Add a dedicated hardware security module and user interface indicator LED to the AI Pendant device to confirm when sensitive permissions like Accessibility and Screen Recording are active and being used by the AI loop, and to allow owner-initiated emergency disabling of all active UI control actions.
- **owner gets:** Provides physical, trustable indication and control over highly sensitive permissions and actions, improving owner's confidence and ability to intervene quickly in case of error or unwanted behavior.
- effort: Medium hardware redesign and firmware update plus physical assembly change.  ·  risk: Adds complexity and cost; requires careful design to avoid false positives or negatives.
- cost: Increased hardware cost and power consumption due to added security module and LED circuitry.  ·  latency: None on software latency.
- security: Greatly enhances security by giving owner direct physical assurance and control over AI enabled capabilities.
- depends on: Permission management and AI loop integration

### `dashboard-ux` — Create a comprehensive permissions and automation dashboard on the owner's Mac and pendant, showing current AI agent statuses, granted permissions, pending permission requests, descriptions of required permissions, and convenient controls to enable/disable AI control loops and permission usage.
- **owner gets:** Empowers the owner with clear visibility and control over AI capabilities and permissions, increases transparency, and facilitates troubleshooting permission-related issues quickly and confidently.
- effort: Medium engineering effort for UI/UX design, backend integration, and testing across Mac and pendant platforms.  ·  risk: If poorly designed, could overwhelm owner or create confusion; must be very clear and accessible.
- cost: Minimal software cost; mostly dev time.  ·  latency: None on real-time actions, occasional on dashboard updates.
- security: Enhances security by providing direct control and visibility, reducing accidental permission grant consequences.
- depends on: Mac agent permission state reporting; Pendant UI integration

### `integration` — Implement a seamless onboarding workflow between mac-vision, mac-planner, and faculty-perception that guides the owner through granting, verifying, and maintaining Accessibility and Screen Recording permissions, with automated checks and clear user prompts to restart or reauthenticate as needed.
- **owner gets:** Ensures owners can enable the AI control loop and vision features smoothly without confusion or failed attempts, reduces support burden, and maximizes feature adoption.
- effort: Medium development effort across multiple components and UI flows, plus testing.  ·  risk: Workflow complexity might frustrate users if not designed well.
- cost: Moderate, spread across components and UI touches.  ·  latency: Negligible for action latency.
- security: Improves secure permission management by integrating guidance and verification into AI onboarding.
- depends on: Dashboard UX; Permission validation infrastructure

### `memory` — Add persistent memory to retain permission grant status history, permission usage logs, and remediation instructions to avoid repeating failed permission states on mac-vision and linked agents.
- **owner gets:** Provides continuity and context awareness across sessions, speeding up issue resolution and avoiding repeated permission problems or agent disablements.
- effort: Medium engineering for persistent storage, logging, and integration with permission and agent status systems.  ·  risk: Memory bloat if logs not pruned; privacy considerations for stored logs.
- cost: Low storage and compute cost.  ·  latency: None on real-time actions, only on startup or querying.
- security: Requires secure storage; must encrypt sensitive data.
- depends on: Permission validation and reporting

### `interaction` — Develop user interaction patterns and voice prompts that clearly indicate when AI is attempting high-impact or irreversible commands on the Mac, requiring explicit owner confirmation via the pendant before proceeding.
- **owner gets:** Prevents accidental destructive actions by requiring owner's deliberate consent, balancing automation power with safety and control.
- effort: Medium effort to design UX flows, voice prompts, and integration with command routing systems.  ·  risk: May annoy or delay the owner if overused, needs tuning of confirmation triggers.
- cost: Moderate due to additional runtime checks and confirmations.  ·  latency: Adds confirmation latency only on high-impact commands.
- security: Significantly improve security and trust by reducing unintended actions.
- depends on: model-routing; dashboard-ux


## What it asked for

_Nothing._
