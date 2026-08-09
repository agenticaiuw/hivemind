# Harness derivation — mac-vision — round 145

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the AI Pendant Agent on the Mac to perform full accessibility-tree driven UI automation without stealing focus or causing the mouse to jump, safely and transparently."
- **useful because:** This enables powerful context-aware multi-step computer tasks fully automated, with no focus disruption or guesswork, greatly extending what Mac automation can do for the user.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** 100–500 ms per UI step
- **cost:** Low to medium API cost dominated by the number of UI actions, no extra hardware cost.
- **security:** Requires owner-granted macOS Accessibility permission explicitly for the AI Pendant Agent binary; must ensure no inadvertent input or focus theft; needs detailed logs and undo capability for safety.
- **missing:** macOS Accessibility grant for the AI Pendant Agent binary; robust undo and logging layer in the automation loop; owner consent UI for granting and revoking the permission

### "A unified, persistent, prioritized task and goal management system spanning all user devices, readable and actionable by all agents including the Mac vision loop."
- **useful because:** Currently, no coherent store of what the owner actually wants actively done exists; this prevents focused, high-impact automation and prioritization.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** background
- **latency:** Seconds to minutes for task updates; realtime query under 500 ms.
- **cost:** Medium cost due to synchronization and query complexity across devices.
- **security:** Task data is sensitive and must be protected; user control over what agents see and act on is critical.
- **missing:** Bidirectional sync layer across devices; Task ranking and priority schema; UI for task intake and review

### "Enable a privacy-preserving consent flow fully integrated on the Mac and pendant to grant, monitor, and revoke macOS Accessibility and loop permissions safely and transparently."
- **useful because:** Currently, granting macOS Accessibility requires manual system dialogs and potentially gives all-or-nothing controls; a fine-grained, user-friendly consent UI empowers the owner to control precisely what the AI Pendant Agent can automate.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** background
- **latency:** Seconds to respond to permission changes, real-time status updates under 1s.
- **cost:** Medium due to UI work and system integration complexities.
- **security:** Critical security point for user trust; must be robust against spoofing, unintentional grants, and ensure user transparency.
- **missing:** System-level hooks to query and apply macOS Accessibility and Automation TCC settings; Inter-device communication for consent state; Clear user UI designs for consent management

### "Create a flexible human-in-the-loop approval and undo system for all Mac UI automation actions executed by mac_vision and mac_run_actions."
- **useful because:** To avoid any unintended destructive changes or mistakes from automated UI control, the owner can approve actions before they happen and undo them easily afterward, ensuring safety and trust.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** Under 1 second for approval/undo requests and responses.
- **cost:** Moderate API cost for rapid confirmation dialogs and state rollback.
- **security:** Must securely verify that approval requests come from the authorized owner and that undo operations cannot be abused.
- **missing:** UI dialog framework for action approval on the Mac and pendant; State checkpointing and rollback mechanisms for UI automation actions; Integration with existing mac_run_actions and mac_delegate workflow

### "Enable mac-vision to reliably infer complex contextual state changes on the Mac UI by combining accessibility tree snapshots with lightweight event streams, for anticipatory action planning."
- **useful because:** This builds richer machine understanding of the Mac UI environment beyond static snapshots, enabling smooth multi-step automation that can adapt to dynamic UI changes and recover from interruptions.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100-300 ms per event snapshot and inference cycle.
- **cost:** Moderate API cost for continuous event processing and inference.
- **security:** Ensures no personal data leaks in event streams, maintains user privacy and data minimization.
- **missing:** Lightweight local event streaming infrastructure; Inference algorithms for UI change and context state; Integration with existing mac-vision accessibility snapshot capabilities


## Changes it proposed to its own stack

### `integration` — Add a layered interplay between get_mac_status, mac_run_actions, mac_delegate, and the new accessibility-driven UI automation capability, orchestrated by mac-vision to fully automate complex multi-step Mac workflows without user focus disruption.
- **owner gets:** This will deliver a uniquely powerful AI assistant experience on the Mac that can visually comprehend and interact with the UI in context, execute tasks fluently, and recover from partial failures all without disrupting the owner's workflow.
- effort: High effort requiring coordination of several components and extensive testing.  ·  risk: Complexity and bugs could cause undesired UI actions or data loss; must have robust logging, undo, and owner approval workflows.
- cost: Medium API cost mainly from automation steps; negligible hardware cost.  ·  latency: Improves latency by fusing multiple data sources and action methods for smooth UI control.
- security: Increased attack surface needing strong safeguards; must restrict actions to owner-approved scopes.
- depends on: macOS Accessibility grant; new task management store; computerUse.loopEnabled

### `firmware` — Extend pendant firmware with a capability to store and transmit structured UI automation context fingerprints on button presses, encoding current UI state or task markers securely for cross-device coordination.
- **owner gets:** This leverages the physical pendant buttons as direct, low-latency UI and task triggers that can be safely handled by the Mac vision agent, enhancing the system's multi-node synergy and reliability even offline.
- effort: Moderate firmware development and validation.  ·  risk: Low risk; storage and transmission must be secure and power efficient.
- cost: Minimal — uses existing capabilities with little extra cost.  ·  latency: Very low latency signaling from physical to Mac agent.
- security: Must ensure data cannot be spoofed or intercepted; requires encryption and authentication.
- depends on: currently existing pendant button hardware and store


## What it asked for

_Nothing._
