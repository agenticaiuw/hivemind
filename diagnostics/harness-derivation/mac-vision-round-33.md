# Harness derivation — mac-vision — round 33

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision live UI interaction loop to perform precise computer UI tasks through accessibility layer without stealing focus or needing full screenshots"
- **useful because:** Today, mac-vision is disabled and hence cannot actively operate the Mac's UI in a fine-grained way. Enabling this loop with proper safeguards would allow the pendant AI system to perform tasks natively in the Mac UI, such as clicking buttons, typing, and navigating complex app interfaces, without breaking user experience or relying on brittle image recognition. This would combine the low-latency device interaction capability with Mac's strong accessibility APIs for powerful yet safe active control.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-judgement → faculty-perception → faculty-action
- **model tier:** gpt-4.1-mini for latency-sensitive decision-making on Mac, gpt-5.6-luna for planning and higher-order judgement in the cloud
- **latency:** Low (<1 second) for UI event response, total task orchestration can be higher
- **cost:** Moderate model calls for interactive control, low data transfer since accessibility data is text-based
- **security:** Allowing live UI interaction requires strong verification to avoid unintended destructive actions; logs and confirmation for high-impact changes needed.
- **missing:** Permissions for mac-vision loopEnabled and visionUploadConsented; UI hierarchy snapshot context from the Mac for non-visual interaction; Typed action gateway enforcing allowed actions and confirmations; Policy and telemetry for action receipts, undo, and user override

### "Seamless cooperative orchestration of tasks between mac-vision, browser-extension, and mac-terminal to handle complex workflows involving app UIs, browser web content, and shell commands without owner context switching"
- **useful because:** Currently, the different Mac facets like mac-vision (UI automation), browser-extension (web automation), and mac-terminal (shell tasks) operate more or less independently, so the owner must manually coordinate complex workflows. If they could seamlessly delegate parts of a multi-step task to the most suitable facet and have the AI coordinate, the owner's efficiency would greatly improve with minimal manual control or interruption.
- **path:** mac-vision → browser-extension → mac-terminal → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for complex planning and coordination, gpt-4.1-mini for responsive local action
- **latency:** Moderate overall; low latency on local UI actions, higher latency for complex orchestration
- **cost:** Higher due to multi-model coordination and broader context exchange
- **security:** Cross-facet coordination must ensure task boundaries are respected to avoid security or privacy leaks; logs and audit mechanisms essential to trace multi-step operations.
- **missing:** API or protocol for orchestration coordination; Unified task context and state sharing among facets; Enhanced permission model for cross-facet delegation

### "Context-aware typed UI action suggestions from the mac-vision accessibility layer that adapt dynamically to the current app and screen state, without owner interruption"
- **useful because:** Currently, mac-vision cannot interact or propose UI actions dynamically because its loop is disabled and it lacks context snapshots of the UI. Having typed UI action suggestions that adapt live to the app context would allow smart and safe autonomous computer operation, improving efficiency and reducing manual intervention.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for real-time interaction with accessory AI, gpt-5.6-luna for background context analysis and coordination
- **latency:** Low latency for interaction, longer for background processing
- **cost:** Moderate, balancing local and cloud costs for model calls and context processing
- **security:** Must restrict UI action suggestions to non-destructive or owner-approved actions to prevent misuse or error; auditing and rollback crucial.
- **missing:** UI hierarchy snapshot context from Mac; Live access to accessibility tree for mac-vision; Typed action model for UI action proposals


## Changes it proposed to its own stack

### `hardware` — Add a local hardware switch or button combo on the pendant to enable/disable mac-vision's live UI control loop with physical confirmation by the owner.
- **owner gets:** Provides a quick manual physical fallback kill switch for mac-vision's active control loop, increasing trust and safety. The owner can instantly abort any unintended actions or temporarily pause the AI control if needed, without requiring voice or app commands.
- effort: Low to moderate, requires hardware design and firmware update for the button and its integration.  ·  risk: Improper button wiring or firmware bugs could accidentally disable the system or create confusion; mitigated by clear physical design and feedback LEDs.
- cost: Low incremental hardware cost and power usage.  ·  latency: None, physical switch instant state change.
- security: Improves security by restoring owner control.

### `integration` — Implement a typed action broker specifically for the mac-vision agent that enforces access control, verifies action safety, and manages confirmations for high-impact or destructive UI actions before execution.
- **owner gets:** Ensures that mac-vision cannot perform harmful or unintended actions on the Mac, providing the owner with increased trust and transparency. It also structures computer control actions into approved types, reducing errors and enabling audit trails and potential undo support.
- effort: Moderate: requires significant engineering in the mac vision control stack and surrounding infrastructure for typed actions and policy enforcement.  ·  risk: Could add latency or occasional false positives blocking legitimate actions; requires good tuning and fallback plans.
- cost: Low to moderate compute cost due to action validation and logging overhead.  ·  latency: Slight increase due to action verification steps.
- security: Significantly improves security by controlling the action flow and adding pre-execution checks.
- depends on: Enable mac-vision live UI interaction loop

### `model-routing` — Route computer-use related requests requiring UI understanding and interaction to a combined mac-vision plus faculty-perception facet setup, ensuring UI context is shared and decisions are coordinated for more intelligent computer use.
- **owner gets:** Currently, UI interaction and perception are separated, limiting effectiveness. Routing these tasks to a coordinated group of models specialized in perception and action enables more robust and context-aware computer control, improving task success and user satisfaction.
- effort: Moderate, requires infrastructure changes for model routing and context sharing.  ·  risk: Complexity in coordinating models may add errors or latency; requires good monitoring and fallbacks.
- cost: Moderate increase due to multi-model coordination.  ·  latency: Slight increase due to coordination overhead.
- security: Must safeguard context sharing against leaks and enforce access controls.
- depends on: Enable mac-vision live UI loop; UI hierarchy snapshot context


## What it asked for

_Nothing._
