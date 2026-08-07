# Harness derivation — mac-vision — round 98

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable fully autonomous Mac UI control via the computer use loop with visual and accessibility permissions"
- **useful because:** The owner could delegate complex, multi-step computer tasks involving any app or UI element, including those without APIs, by permitting the system to take screenshots, interact visually with the screen, and use accessibility features for precise control, massively expanding automation and assistant abilities beyond typed actions or single-step commands.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-4.1-mini
- **latency:** Real-time or near-real-time responses within a few seconds for UI tasks
- **cost:** Moderate to high due to processing screenshots and complex plan execution; dominated by vision model inference and interaction retries
- **security:** Full screen recording and accessibility permissions grant very broad control and observation permissions, which requires strong owner consent and robust privacy and audit logging to prevent misuse or leaks.
- **missing:** Owner explicit consent UI for permissions granting; Robust gesture and interaction replay with undo; Context isolation and selective screenshot redaction; Continuous health and permission monitoring during active loop


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure coprocessor on the MacBook to handle screen capture, accessibility event logging, and replay for the AI pendant system out-of-band, minimizing risk of sensitive data leakage and maintaining strict control separate from the main OS environment.
- **owner gets:** Gives the AI pendant full visual and UI interaction capabilities securely, with reduced risk of privacy breaches or malware exposure; enables fully autonomous computer use loop safely.
- effort: High engineering effort to design, integrate, and validate hardware and firmware, plus driver and OS integration.  ·  risk: Hardware complexity and integration challenges; possible delays in delivery and adoption; detection and recovery mechanisms needed for hardware faults or misuse.
- cost: Increased hardware bill of materials and power consumption, depending on coprocessor design.  ·  latency: Minimal impact on latency; potentially improves loop responsiveness by offloading capture and event handling.
- security: Strong positive security impact by isolating sensitive UI data and controls.
- depends on: Enable fully autonomous Mac UI control via the computer use loop with visual and accessibility permissions

### `firmware` — Extend the pendant firmware to locally analyze Mac screen captures and UI accessibility snapshots, detecting regions of interest and filtering sensitive content before transmitting to the cloud or Mac planner for advanced reasoning, reducing surface for privacy leaks and bandwidth.
- **owner gets:** Improves privacy and responsiveness by preprocessing sensitive UI content on the pendant device, allowing useful visual context to assist the AI while respecting owner consent policies and reducing cloud exposure.
- effort: Moderate firmware and ML model development effort, plus tight integration with Mac capture and communication protocols.  ·  risk: Complexity of model tuning on limited hardware; risk of missing important data or over-filtering; firmware updates required to enhance functionality.
- cost: Moderate power usage increase on the pendant; development cost for models and updates.  ·  latency: Reduces latency by early preprocessing on the pendant; reduces cloud data transmission.
- security: Improves security by limiting raw data exposure outside the local device.
- depends on: Enable fully autonomous Mac UI control via the computer use loop with visual and accessibility permissions

### `interaction` — Develop an advanced undo and audit system integrated into the computer use loop on the Mac, providing full visibility of every UI interaction performed by the AI, with automatic rollback capabilities for any undesired actions or errors.
- **owner gets:** Ensures the owner maintains confidence and control over autonomous AI actions on their Mac, preventing accidental damage or data loss, while enabling the AI to operate with maximum autonomy and minimal confirmation prompts.
- effort: Moderate software development effort, with integration into the AI action pipeline and macOS accessibility APIs.  ·  risk: Complexity in capturing all possible UI state changes; potential residual side effects of some actions that cannot be fully reversed.
- cost: Mostly development effort; low ongoing resource usage.  ·  latency: Minimal impact on interaction latency, but improved safety justifies minor delays.
- security: Increases security by providing transparency and control over AI actions.
- depends on: Enable fully autonomous Mac UI control via the computer use loop with visual and accessibility permissions

### `context` — Implement a fine-grained UI context capture and selective redaction framework on the Mac, allowing the AI loop to access needed UI information while filtering or anonymizing sensitive UI elements (passwords, personal data) dynamically, based on owner preferences and policies.
- **owner gets:** Enables the computer use loop to operate effectively across a wide range of apps and scenarios, including sensitive ones, while protecting the owner's privacy and compliance needs.
- effort: High software development effort including macOS accessibility hooks, ML classification of sensitive content, and owner-configurable policies.  ·  risk: Potential for misclassification leading to leaking sensitive info, or over-filtering blocking legitimate tasks.
- cost: Moderate development and runtime resource usage.  ·  latency: Some increased latency in UI capture and filtering but can be optimized.
- security: Significant positive impact by reducing data leak risks in visual AI workflows.
- depends on: Enable fully autonomous Mac UI control via the computer use loop with visual and accessibility permissions

### `dashboard-ux` — Build a dedicated Mac vision loop status and control dashboard integrated into the owner's existing AI Pendant dashboard, showing live UI interaction logs, permission states, undo options, and visual snapshots with redactions where needed.
- **owner gets:** Provides the owner with transparent oversight and manual override/control for the autonomous computer use loop, increasing trust and usability by making AI actions clear and recoverable.
- effort: Moderate dashboard UI design and integration with Mac agent telemetry and command logs.  ·  risk: Potential privacy risks if dashboard access is compromised; requires secure authentication and access controls.
- cost: Minimal runtime cost; development effort mostly.  ·  latency: No latency impact on AI actions; improves user control experience.
- security: Improves security and user trust by increasing transparency and control.
- depends on: Enable fully autonomous Mac UI control via the computer use loop with visual and accessibility permissions


## What it asked for

_Nothing._
