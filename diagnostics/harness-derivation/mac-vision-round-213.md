# Harness derivation — mac-vision — round 213

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide live Mac UI state verification during delegated workflows using accessibility tree snapshots."
- **useful because:** This capability ensures the Mac UI automation tools can verify actual on-screen states and controls, preventing errors and mismatches during multi-step workflows. It raises Mac automation safety and reliability significantly.
- **path:** mac-vision → mac-planner → mac-terminal
- **model tier:** realtime
- **latency:** 200ms
- **cost:** low API usage, moderate model usage to parse UI state
- **security:** Live UI state contains window titles and control labels but no pixel-level screenshot. User consent required for accessibility data. No data leaves device without consent.
- **missing:** An API route exposing accessibility trees for mac-vision in real-time; Model logic to interpret accessibility trees and verify workflow progress

### "Create a durable Mac UI task list surface combining owner-stated tasks, workbench contexts, and live Mac UI state."
- **useful because:** Currently, there is no consolidated Mac task list that reflects owner priorities and actual Mac-side work in progress. This would guide automation at scale, improve task prioritization and decision making across devices.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** 2s
- **cost:** moderate API usage, low model usage
- **security:** Task data contains owner priorities and UI context, sensitive but contained on local Mac. No external sharing without explicit consent.
- **missing:** Aggregation service combining memory projections, workbench contexts and live Mac UI state; Storage and querying mechanism for consolidated task list

### "Implement robust multi-step Mac UI workflow execution coordinating mac-run-actions, browser-run-actions, mac_delegate, and live UI verification."
- **useful because:** This unifies all Mac interaction tools into scalable, safe workflows that can handle complex tasks reliably. Prevents errors by actively verifying UI states and resuming failed steps correctly.
- **path:** mac-vision → mac-planner → mac-terminal
- **model tier:** realtime
- **latency:** 5s
- **cost:** higher API and model usage due to multi-step planning and verification
- **security:** Requires access to Mac UI control and state, potentially sensitive. Must enforce user consent and careful data handling.
- **missing:** Orchestration layer unifying mac action tools with UI state verification; Stateful execution engine with rollback and resume capabilities

### "A UI verification capability that can read the live accessibility tree on the Mac during workflows to confirm screen state matches task progress."
- **useful because:** This would be the single most useful addition to Mac automation: it would turn blind scripted actions into verifiable, context-aware interactions that reduce errors and false assumptions.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 200ms
- **cost:** low token usage, moderate local computation
- **security:** Requires accessibility permission; UI state contains textual labels, potentially sensitive; data stays on device unless explicitly shared.
- **missing:** API exposing accessibility tree snapshots for mac-vision; Model logic for interpreting UI state to verify action success or failure

### "A multi-step Mac UI workflow orchestrator that safely combines mac-run-actions, browser-run-actions, mac_delegate and UI verification to complete complex tasks reliably and resume after interruptions."
- **useful because:** This orchestration layer would make Mac automation robust and scalable, enabling genuinely useful delegated workflows instead of brittle scripts or one-off actions.
- **path:** mac-vision → mac-planner → mac-terminal
- **model tier:** realtime
- **latency:** 5s
- **cost:** higher token and API usage due to planning and execution overhead
- **security:** Requires elevated Mac UI control permissions; safeguard user data and consent.
- **missing:** Stateful orchestration engine with rollback and resume support; Integration with UI verification for real-time feedback

### "A secure sandbox environment for experimental Mac UI automation workflows that can be tested without affecting live data or applications."
- **useful because:** Allows safe trial and error testing of Mac automation scripts and workflows without risk to the owner's real data or system state, enabling confident development and iteration.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** Variable depending on scope
- **cost:** Moderate API and resource usage due to sandbox environment management
- **security:** Sandboxed data may contain personal info; must ensure perfect isolation and no leakage to live environment without explicit consent.
- **missing:** Sandbox containerization for Mac UI and filesystem state; Mechanisms to clone or simulate live environment for testing

### "Capability for the Mac-vision agent to read and verify visually rendered error messages or notifications on the Mac screen during workflow execution, to retry or escalate intelligently."
- **useful because:** Automated workflows often fail due to transient errors displayed on screen. Detecting and responding to these visually presented messages can increase automation robustness, help decide when to retry or escalate to user intervention.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** 500ms
- **cost:** Moderate token usage for natural language processing of error messages
- **security:** Error messages may contain sensitive info; data stays local unless explicit sharing consent.
- **missing:** Enhanced OCR or accessibility tree parsing focused on error/notification regions; Model logic to classify and propose automated recovery steps

### "A continuous learning system for the Mac-vision agent that observes repeated UI workflows and suggests optimizations or automation templates to the owner."
- **useful because:** This would let the agent improve its efficiency and reliability autonomously over time by learning frequent patterns and proposing safer, faster workflows tailored to the owner's habits.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** Minutes to hours
- **cost:** Low to moderate model usage, higher storage for workflow logs
- **security:** Observations of UI actions may contain private data; data processed locally with opt-in for sharing improvement patterns.
- **missing:** Workflow logging infrastructure; Learning algorithms to mine patterns and propose workflow optimizations


## What it asked for

_Nothing._
