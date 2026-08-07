# Harness derivation — mac-vision — round 82

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the Mac computer-use loop with safe and privacy-preserving vision upload consent to perform complex UI tasks based on screen analysis."
- **useful because:** The owner should be able to delegate complex interactive Mac workflows that APIs cannot handle, such as interacting with apps with no API or inaccessible UI elements, with the comfort that privacy and safety risks are minimized.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for vision loop decisions, gpt-5.6-luna for planning and judgement
- **latency:** Low latency on the Mac for UI actions; moderate latency on relay for voice confirm
- **cost:** Moderate per invocation due to screenshot upload, privacy filtering, and local UI state fetch
- **security:** Sensitive screen content needs strict privacy filters and explicit owner consent before upload; strict limits on actions allowed without owner confirmation; audit logs and undo receipts must be mandatory; continuous monitoring by judgement and perception facets to detect unsafe behavior
- **missing:** Privacy-filtered screenshot capture and upload pipeline integrated with explicit owner consent UI; Continuous UI state snapshot and accessibility tree integration to minimize screenshot needs; Typed action brokering with confirmation prompts for high-impact UI operations; Audit and undo receipts fully integrated into computerUse loop; Policy and guardrails driven by judgement and perception surfaces for safe activation

### "Provide a real-time visual debugging interface for the mac-vision agent that lets the owner see what UI elements are detected, what actions are planned or blocked, and history of UI interactions visually, with privacy controls and live feedback."
- **useful because:** The owner can understand and guide the AI-driven UI interaction process on their Mac in real-time, improving trust, transparency, and fine-tuning of the automation.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna for UI presentation and explanation
- **latency:** Interactive latency acceptable within half a second for updates.
- **cost:** Moderate, mainly cloud rendering and context analysis costs.
- **security:** Must securely mask or exclude sensitive visual data and only show owner-specific UI contexts with explicit consent.
- **missing:** Real-time UI element identification and logging in mac-vision; Secure streaming and rendering pipeline to mac-planner and relay-realtime; User interface for owner to review and interact with logs and current UI state visually


## Changes it proposed to its own stack

### `hardware` — Add a local privacy-preserving hardware module on the MacBook that intercepts and anonymizes screenshots and sensitive UI data before they leave the device, ensuring visionUploadConsented mode can be enabled with minimal owner privacy risk.
- **owner gets:** The owner can enable advanced AI vision capabilities and automation on their Mac with strong built-in privacy controls, encouraging trust and adoption for sensitive screen content.
- effort: Medium to high, requires kernel level hooking or system integration for screen data capture and anonymization, plus firmware development.  ·  risk: Potential for application crashes or degraded performance if hooks are poorly implemented; fallback to offline mode required. Privacy failure would be critical, so rigorous testing and audits needed.
- cost: Moderate for hardware development and maintenance; negligible ongoing cost after deployment.  ·  latency: Minimal added latency for screen capture anonymization due to local processing.
- security: Improves security by preventing unfiltered screen data from leaving the device; reduces risk of private data exposure.
- depends on: computerUse.loopEnabled; visionUploadConsented


## What it asked for

_Nothing._
