# Harness derivation — mac-vision — round 36

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision computer-use loop safely with full accessibility and pixel UI control to automate UI tasks on the MacBook"
- **useful because:** The owner can delegate complex UI interactions that cannot be done via direct APIs, improving productivity by automating Mac app workflows and browser tasks through local UI manipulation.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-4.1-mini for pixel/UI step reasoning, gpt-5.6-luna for planning and coordination
- **latency:** 200-500ms per UI action, seconds to minutes for multi-step workflows
- **cost:** Medium per invocation; pixel analysis dominates costs
- **security:** Need strict policy controls, clear action classification, and owner consent gating to prevent unintended destructive actions; sensitive UI content may be processed locally; minimal data sent to remote models.
- **missing:** Enable computerUse.loopEnabled and visionUploadConsented permissions; Access to ui_hierarchy_snapshot or equivalent for UI structure; Typed action classification and confirmation policy for mutating UI actions; Seamless integration with other surfaces (relay-realtime, browser-extension) for cross-device workflows

### "Owner-accessible audit log and replay for all mac-vision UI actions taken, searchable and exportable, with undo capability"
- **useful because:** The owner gains full transparency and control over what changes mac-vision has made on the Mac UI, strengthening trust and safety by enabling review and rollback of automated tasks.
- **path:** mac-planner → mac-vision
- **model tier:** gpt-5.6-luna for log synthesis and search
- **latency:** Seconds for log access, instant for undo requests
- **cost:** Low to moderate, mostly storage and minor compute for queries
- **security:** Logs contain sensitive UI info; must be encrypted and access-controlled.
- **missing:** Detailed recording of ui actions and their effects; Undo mechanism integration with mac_run_actions and mac_delegate


## Changes it proposed to its own stack

### `interaction` — Build an orchestrated safety and control framework for mac-vision's UI loop that classifies UI actions as read-only, reversible, or high-impact mutation; requires owner confirmation only for high-impact; logs all actions with receipts.
- **owner gets:** This ensures mac-vision can act autonomously on the MacBook UI with minimal disruptions to owner workflow while giving them control over risky changes and full transparency.
- effort: Medium, involving backend, UI, and local-agent updates  ·  risk: Misclassification of actions could lead to accidental mutations; mitigated by logging and easy undo; requires owner's attention for confirmations.
- cost: Moderate increase due to classification processing and logging; mostly backend server-side.  ·  latency: Minor, confirmation pauses are asynchronous.
- security: Increases trust through visibility; data shared per policy.
- depends on: Enable computerUse.loopEnabled and visionUploadConsented permissions; Access to ui_hierarchy_snapshot

### `hardware` — Enhance the pendant hardware with a secondary confirmation button and haptic feedback to safely confirm mac-vision's high-impact UI actions locally without requiring full screen interruptions or keyboard input.
- **owner gets:** Provides an intuitive, secure, and low-distraction method for the owner to authorize critical Mac UI actions suggested by mac-vision, improving trust and safety for automation.
- effort: Medium hardware and firmware update with companion software adjustments  ·  risk: Additional hardware could fail or add complexity, mitigated by fallback to software confirmation.
- cost: Low additional component cost, minimal added power draw.  ·  latency: Improves confirmation latency by avoiding UI pop-ups.
- security: Improves security by using physical confirmation, reducing accidental approvals.
- depends on: Enable computerUse.loopEnabled and visionUploadConsented permissions

### `integration` — Develop cross-surface collaboration protocols and shared context exchange mechanisms between mac-vision, relay-realtime, and browser-extension to coordinate multi-device task workflows involving Mac UI, voice commands, and browser state.
- **owner gets:** Enables seamless task handovers and collaborative automation across the owner's MacBook UI, wearable pendant voice interface, and browser, unlocking powerful multi-modal interaction and real-world productivity gains.
- effort: High, requiring API and protocol design, local and cloud coordination logic, and debugging.  ·  risk: Complex integration could introduce synchronization issues; mitigated by robust state management and fallback behaviors.
- cost: Moderate cloud compute and network usage increase.  ·  latency: Minimal with efficient design, mostly asynchronous coordination.
- security: Requires secure context sharing and authorization controls.
- depends on: Enable computerUse.loopEnabled and visionUploadConsented permissions


## What it asked for

_Nothing._
