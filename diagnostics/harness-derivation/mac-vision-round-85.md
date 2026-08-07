# Harness derivation — mac-vision — round 85

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to safely and proactively operate the computer-use loop on the MacBook with pixel and accessibility actions"
- **useful because:** The owner gets genuine hands-free, AI-driven computer control including multi-step UI workflows that are inaccessible today. This is vital for seamless workflow automation and task completion that requires visual scene understanding and interaction beyond simple actions.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-4.1-mini for mac-vision with gpt-5.6-luna for planning and judgement
- **latency:** low latency interaction suitable for real-time UI feedback and decision loops (~100-500ms per step).
- **cost:** Moderate API cost for multi-step visual reasoning and UI interaction planning; dominated by model queries and UI state capture.
- **security:** Pixel-level access and mutating computer control raise privacy and safety concerns. Requires strong permission gating and on-device safeguards including reversible action logs and transparency. User confirmation or undo must be easy and immediate.
- **missing:** A typed action broker that integrates mac-vision actions with the system pipeline for observability and safety (without blocking); A local device skill for secure, low-level UI observation and pixel capture that respects privacy, runs offline, and signals when pixel access is granted or denied; A robust safety and trust framework for ui_* and pixel actions including timing, context validation, and approval heuristics; Better integration and status sharing between mac-vision, mac-run-actions, and mac-delegate to coordinate short and multi-step workflows; A hardware or system consent mechanism that allows explicit user granting and revocation of pixel-level screenshot and screen control consent

### "Enable layered approval and undo framework for mac-vision's mutating actions with optional user confirmation and forensic action receipts"
- **useful because:** The owner can safely allow mac-vision to control the computer UI and perform system actions, yet retain immediate undo, review, and contextual approval options to avoid accidental damage or unwanted changes.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna for judgement and planning, gpt-4.1-mini for mac-vision action execution
- **latency:** Expected interactive latency in seconds for most actions; immediate for undo and confirmation prompts.
- **cost:** Low to moderate API cost mainly from interaction with judgement and planner models to classify and enforce action approval policies.
- **security:** Undo and approval must be secure and private. Receipt logs must be tamper-proof and accessible only to the owner. Potential risk of temporary denial-of-service if approval gates malfunction.
- **missing:** Typed action classification and broker middleware that enriches actions with metadata for approval, receipt, and undo capabilities; User interface and interaction flows that prompt for consent only when necessary and enable immediate undo with minimal friction; Persistent, tamper-evident action receipts that record context, time, and outcome for each executed action; Integration into existing mac-vision and mac-run-actions pipelines for seamless enforcement of the framework

### "Enable situationally adaptive UI action policy enforcement in mac-vision based on real-time context and risk metrics"
- **useful because:** The owner will benefit from a system that dynamically adjusts mac-vision's permissions and action limits based on the current device state, user context, and recent history to balance automation efficiency with safety.
- **path:** mac-vision → faculty-judgement → relay-realtime
- **model tier:** gpt-5.6-luna for real-time judgement and risk assessment, gpt-4.1-mini for action execution on mac-vision
- **latency:** Sub-second to a few seconds for policy adaptation and enforcement to keep interactions fluid but safe.
- **cost:** Moderate API cost for continuous context analysis and policy decision modeling.
- **security:** Requires secure context sources to avoid manipulation. Incorrect policy adjustments could either block needed actions or allow unsafe ones. Logs and audit trails needed for transparency.
- **missing:** Contextual awareness framework feeding real-time device, user, and environment signals to judgement models; Rule and policy engine integrated with mac-vision’s action broker to enforce adaptive action constraints; Interfaces for manual override and learning from owner feedback to improve policy decisions over time


## What it asked for

_Nothing._
