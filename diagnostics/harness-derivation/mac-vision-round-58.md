# Harness derivation — mac-vision — round 58

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a trusted UI and screen capture permission gateway on the Mac for mac-vision to see screens and UI elements reliably."
- **useful because:** The owner would be able to delegate any desktop GUI task that cannot be done through APIs to the mac-vision agent, which can see the exact screen or UI element contexts and take safe pixel or accessibility-based actions. This unlocks full computer control in the AI collective's Mac surface without sacrificing security or reliability.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini
- **latency:** sub-second to seconds depending on action complexity
- **cost:** minimal in CPU, moderate in human consent and security engineering to build a trust gateway
- **security:** Requires careful gating so mac-vision only acts with full owner approval and trusted screen/input capture to avoid privacy or security breaches. Trust boundary must be enforced at OS level.
- **missing:** Machine-level accessibility and screen recording permissions accessible to AI agents with audit logs; Cross-surface event coordination for UI input synthesis and feedback; Owner control UI for permissions and manual overrides

### "Allow mac-vision to perform safe previewing of UI actions before executing them, including dry runs on synthetic UI snapshots or cached screens."
- **useful because:** The owner can review and confirm complex UI interactions that mac-vision plans to perform on their behalf, reducing risk of errant or harmful actions. This preview capability combined with approval gating increases trust and safety for fully autonomous UI control.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds to a few tens of seconds for previews
- **cost:** Moderate cost in compute for UI simulation and contextual reasoning.
- **security:** Previews must not leak sensitive UI data. Preview results must be transient and secured. Owner approval must be explicitly required before any real action.
- **missing:** UI snapshot caching and synthetic replay engine; Integration with judgement and action facets for multi-step approval workflows

### "A unified cross-surface action broker that seamlessly orchestrates Mac GUI control (mac-vision), browser control (browser-extension), and shell commands (mac-terminal) under a single coherent AI-driven plan."
- **useful because:** The owner can issue complex multi-environment commands combining desktop UI, browser, and shell actions without needing to fragment requests or handle cross-modal context switching. The AI mind manages the dependencies and fault handling across surfaces for seamless user experience.
- **path:** mac-vision → browser-extension → mac-terminal → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes depending on complexity
- **cost:** Moderate to high depending on number of surfaces involved and complexity of flow coordination.
- **security:** Requires strong authorization and auditing on all surfaces to avoid dangerous combined commands, and recovery mechanisms for faults or partial executions.
- **missing:** Cross-surface state sharing and event routing; Action sequencing and rollback on failures; Unified user approval interface

### "A permission management dashboard on the Mac that lets the owner review, grant, revoke, and audit AI agent access to accessibility, screen recording, shell commands, and browser sessions in one place."
- **useful because:** Gives the owner transparent control over what each AI surface can see and do, improving trust and safety. Allows easy adjustment and auditing of permissions and access history for mac-vision and other components.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** sub-second interaction
- **cost:** Low hardware cost, moderate software and UX development cost.
- **security:** Must securely store and verify permissions and audit logs; UI must avoid spoofing or accidental permission grants.
- **missing:** Unified permission and audit backend; User-friendly mac GUI for AI permission control


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure hardware enclave on the Mac for trusted AI screen capture and UI input mediation. This enclave manages all screen recording permissions, keyboard and mouse event injection, and logs every action securely with user audit access.
- **owner gets:** Provides a hardware-rooted trust boundary so the AI mac-vision agent can safely operate with full screen and UI input powers, greatly expanding automation capabilities without risking unauthorized input or screen leaks.
- effort: High engineering effort across firmware, OS, and AI software layers.  ·  risk: Complex security risks if enclave is compromised; mitigated by rigorous hardware-rooted trust and logging.
- cost: Moderate cost to Mac hardware unit cost and power for secure enclave.  ·  latency: Negligible latency impact on UI event flow.
- security: Significant positive impact by isolating AI input/screen controls; reduces attack surface if properly designed.
- depends on: trusted UI and screen capture permission gateway proposal; OS support for secure enclave integration

### `model-routing` — Implement specialized routing that prioritizes mac-vision for desktop GUI tasks that require pixel or accessibility context, delegating API and shell tasks to other surfaces automatically.
- **owner gets:** Automatically routes commands to the best surface able to fulfill them, increasing efficiency and success rates without owner needing to specify the modality. Mac-vision gets invoked only when pixel/UI context is essential.
- effort: Moderate development effort in routing logic and context classification.  ·  risk: Misclassification could cause inappropriate attempts to run unavailable UI actions, controlled by fallback mechanisms.
- cost: Small additional compute cost in routing decision evaluations.  ·  latency: Minor added latency to command dispatch.
- security: Neutral impact, routing is internal logic.
- depends on: stable and trusted mac-vision loop

### `integration` — Create a shared privacy-aware event and context bus connecting mac-vision, browser-extension, mac-terminal, and relay-realtime for real-time ownership verification and coordinated multi-surface execution feedback loops.
- **owner gets:** Ensures trusted state and consent provenance across all AI surfaces controlling or observing the owner's MacBook and browser. Enables safe, auditable, and user-controllable multi-surface task flows with live error reporting and intervention.
- effort: High coordination effort across software layers and surfaces.  ·  risk: Complexity may introduce synchronization bugs, mitigated by rigorous testing and fallback.
- cost: Moderate computing and network bandwidth costs for event streaming and coordination.  ·  latency: Adds minimal latency due to near real-time updates.
- security: Strong positive, improves surface trust and auditability.
- depends on: cross-surface orchestration primitives; secure message passing; trusted UI gateway


## What it asked for

_Nothing._
