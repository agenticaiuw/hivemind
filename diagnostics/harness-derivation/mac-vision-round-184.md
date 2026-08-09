# Harness derivation — mac-vision — round 184

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "The owner should be able to give natural language commands to the Mac that understand and interact with complex multi-app workflows, with the AI managing interface navigation invisibly and safely, even when no direct API exists for the task."
- **useful because:** Many complex tasks require sequences of UI actions spread across multiple apps, which the owner currently cannot automate or delegate naturally. This capability would make the Mac a truly responsive assistant capable of understanding high-level goals and executing them precisely and unobtrusively.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to a minute
- **cost:** Moderate API calls with some Mac local compute for UI understanding and action planning
- **security:** Needs strict controls to prevent incorrect or dangerous UI actions, requires owner permission for accessibility features
- **missing:** Full macOS Accessibility permission for AI Pendant Agent binary; Advanced UI understanding models integrating with mac-vision; Safe, reversible action execution framework

### "The owner should have a dynamic, prioritized task and goal management system integrated deeply with reminders, calendar, and manual inputs, allowing AI to suggest, adjust, and visually indicate the highest priority actionable item across all devices and surfaces."
- **useful because:** Today the owner’s tasks are fragmented and hand-typed without priority or dependencies. Such a system would give real-time, cross-device situational awareness and decision support, streamlining owner productivity.
- **path:** mac-planner → unified → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** Low to moderate, mostly local data synchronization and ranking
- **security:** Needs careful privacy handling for sensitive tasks and integration data
- **missing:** Unified task repository with priority and dependency support; Cross-surface synchronization and presentation; User feedback and manual adjustment UI

### "The owner should be able to use the pendant's single hardware button with multiple physical gestures (single tap, double tap, long press) uniquely mapped to different Mac or system actions, with dynamic configuration and immediate feedback from the Mac."
- **useful because:** Physical buttons afford a powerful direct interaction modality that complements voice and GUI. Mapping multiple gestures to distinct actions enhances the device's utility and owner's control without needing extra hardware.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds
- **cost:** Minimal firmware changes for gesture recognition and software to handle mapping and feedback
- **security:** Gesture recognition must be robust to avoid unintended actions; requires safety guardrails and owner confirmation for sensitive commands
- **missing:** Firmware support for gesture recognition on the single button; Software framework for dynamic mapping and feedback; User configuration UI

### "The owner should have AI-driven multi-app context awareness on their MacBook, allowing the system to proactively detect, interpret, and assist with workflows that span several applications or web pages, dynamically suggesting next best steps or automations that can be triggered with minimal owner input."
- **useful because:** Owners often juggle complex work across multiple applications and browser tabs. AI understanding this context holistically would save time, reduce cognitive load, and anticipate needs without explicit commands.
- **path:** mac-vision → mac-planner → browser-extension → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** Moderate, requiring local state synchronization and AI model inference
- **security:** Requires strong privacy filtering for sensitive document content and web sessions. Needs owner control over what contexts are shared and used.
- **missing:** Cross-app context integration framework; Advanced AI models for workflow understanding; UI hooks or APIs for proactive suggestions

### "The owner should be able to instruct the system to automatically triage incoming notifications, emails, and alerts based on learned preferences and context awareness, surfacing only the most urgent and relevant with a quiet summary via the pendant or Mac, while deferring or silencing less important interruptions."
- **useful because:** This would reduce distraction, preserve focus, and let the owner trust the system to manage peripheral information intelligently, improving productivity and well-being.
- **path:** mac-planner → relays-realtime → pendant → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes
- **cost:** Moderate, requiring continuous learning and contextual understanding
- **security:** Must respect privacy of communications and provide transparent control and override ability to owner.
- **missing:** Notification context ingestion and classification pipeline; Owner preference learning and adaptation; Cross-device alert delivery and suppression

### "The owner should be able to control and monitor long-running or complex Mac automation tasks that span multiple steps and might require user decisions mid-flow, with the system providing real-time status updates, undo options, and the ability to pause or cancel at any point."
- **useful because:** Complex workflows often fail or need human intervention. This capability would provide transparency and control, reducing frustration and increasing trust in automated Mac actions.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes per update
- **cost:** Moderate, requiring stateful job tracking, UI for status and control, and integration with mac_run_actions and mac_delegate.
- **security:** Needs secure authorization and safe undo capabilities to prevent harmful actions and unauthorized control.
- **missing:** Stateful job controller and tracker; User interface for monitoring and control; Undo and cancel support in mac_run_actions


## What it asked for

_Nothing._
