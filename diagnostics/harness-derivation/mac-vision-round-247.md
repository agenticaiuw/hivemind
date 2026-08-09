# Harness derivation — mac-vision — round 247

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow seamless UI state reconciliation against claimed multi-step Mac workflows to enable true recovery and delegation of partial UI tasks."
- **useful because:** Currently, mac-vision can claim multi-step UI workflows but cannot match them accurately with the actual UI state due to lack of availability of real-time UI state projection and reconciliation. This capability would let the system robustly resume, delegate, and audit partial Mac UI workflows without error or duplication.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate (mostly model computation)
- **security:** Requires exposing live UI accessibility tree state and correlating it with workflows, which may reveal private UI contents. Needs strict local processing and opt-in permission.
- **missing:** a real-time API or data model that maps accessibility UI state to claimed workflows; enhanced durable state tracking inside mac-vision and workbench context store; improved privacy and access controls for accessibility data

### "Enable the Mac-vision agent to autonomously detect and recover from partial UI workflow failures by comparing accessibility tree states before and after each action and applying corrective steps."
- **useful because:** Currently, the agent cannot reliably know if a UI step actually succeeded or partially failed without direct state feedback, making robust automation brittle. This capability adds resilience and reduces owner intervention for multistep tasks.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low to moderate computational cost
- **security:** Requires detailed local UI state capture and retention temporarily; must enforce strict permissioning and data lifecycle control.
- **missing:** UI snapshot diffing and state change detection logic; workflow recovery action framework in mac-vision

### "Provide mac-vision with a live privacy audit capability that flags potentially sensitive fields in the accessibility tree before any operation is performed, and requests owner consent."
- **useful because:** To ensure the owner retains control over what UI data is accessed or acted upon by the automation, especially for fields that might expose private data, thus maintaining trust and preventing accidental privacy breaches.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low computational cost
- **security:** Privacy enforcement is critical; any failure could expose sensitive fields. Consent collection also needs secure and unambiguous flow.
- **missing:** Field classification model for privacy sensitivity in accessibility tree; Consent UI and gating mechanism; Integration with mac-vision control loop

### "Provide mac-vision with a predictive UI navigation and shortcut suggestion system that anticipates owner intentions based on context, history, and partial task inputs."
- **useful because:** This system would reduce manual effort by predicting and offering shortcuts to complex sequences of UI actions the owner commonly performs or is likely to want next, speeding workflows and improving user satisfaction.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate computational and storage cost
- **security:** Privacy of usage data; prediction accuracy and unwanted automation must be controlled to prevent errors or annoyance.
- **missing:** Contextual history capture and model training pipeline; Integration with mac-vision workflows and UI access APIs; Owner override and feedback loop mechanisms

### "Enable seamless voice command interleaving for controlling Mac UI and other devices (like iPhone) with context-aware switching and confirmation to avoid errors or confusion."
- **useful because:** When the owner switches between using voice commands for the Mac UI (via mac-vision) and for connected devices like the iPhone, this capability smoothly switches the control context to reduce friction and mistakes, preserving task continuity and user satisfaction.
- **path:** mac-local-agent → ios-control
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low to moderate
- **security:** Context switching vulnerabilities could cause commands to be sent to the wrong device or unintended action; confirmation gating is necessary.
- **missing:** Context management and switch detection across voice/command surfaces; Stateful session tracking and user feedback mechanisms; Integration between mac-vision and ios-control agents


## Changes it proposed to its own stack

### `mac-harness` — Add selective UI snapshot streaming and secure batching for the mac-vision accessibility loop, preserving privacy through on-device filtering and redaction before any off-machine upload.
- **owner gets:** This enables longer-term contextual awareness for interrupted workflows, anomaly detection, and friendly debugging without exposing entire screen contents, which protects privacy while enabling richer Mac automation.
- effort: Medium - requires filter engine development and protocol changes for streaming and batching.  ·  risk: Potential leakage of sensitive UI elements unless filtering and controls are bulletproof; recovery possible by disabling streaming and audit logs.
- cost: Moderate compute and storage costs for filtering and streaming batching.  ·  latency: Low if done asynchronously.
- security: High - strong encryption and permission gating needed to prevent data leaks.
- depends on: fully granted accessibility permission; mac-vision permission to access and process UI tree data


## What it asked for

_Nothing._
## Its own summary

Recorded six new capabilities and one hardware change proposal that significantly extend the mac-vision agent and pendant usability beyond current limitations: 1) UI state versus workbench context reconciliation, 2) prioritized Mac UI task queue, 3) selective UI snapshot streaming and privacy filtering, 4) UI workflow failure detection and recovery, 5) live privacy audit of UI fields, 6) predictive UI navigation and shortcut suggestion, and 7) a next-gen pendant design with a second button and gesture input. These address core gaps in automation, recovery, user input range, and privacy. No restatements included. No further discovery tools available this round.

**Biggest unknown:** Whether the workbench context and UI snapshot APIs exist or can be further developed to support the critical reconciliation and state recovery capabilities for mac-vision.

