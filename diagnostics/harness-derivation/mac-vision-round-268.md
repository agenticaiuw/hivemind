# Harness derivation — mac-vision — round 268

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to perceive and interact with the Mac's UI by integrating an accessibility-tree based automation loop that reads UI controls and state without using pixel screenshots."
- **useful because:** This would allow the AI Pendant system to perform reliable, reversible, and secure Mac UI operations without stealing focus or relying on brittle pixel-based automation. It opens full UI automation on the Mac with accountability and fine control.
- **path:** mac-local-agent → relay → pendant → dashboard
- **model tier:** realtime
- **latency:** 50-200 ms per update cycle
- **cost:** Moderate; mostly communication overhead and state diffing; low model inference cost per UI snapshot
- **security:** Requires macOS Accessibility permissions for the exact agent binary; careful to never degrade to pixel-based control which steals focus or injects clicks blindly.
- **missing:** mac-vision_accessibility_automation_loop tool capability; support in relay and pendant for managing UI state diffs; Owner consent/management UI for granting macOS Accessibility for this app

### "Provide a prioritized and contextual Mac task backlog for the mac-vision agent based on owner task facts, reminders, and routines, with additional metadata about urgency, dependencies, and deadlines to drive actionable Mac work prioritization."
- **useful because:** Currently mac-vision has no reliable way to know what the owner wants done on the Mac in priority order. This backlog would enable efficient task selection and focused automation efforts that align with owner's current goals and deadlines.
- **path:** mac-local-agent → relay → dashboard
- **model tier:** background
- **latency:** seconds
- **cost:** Low to moderate, dominated by memory and context graph queries and ranking logic
- **security:** None beyond existing owner data privacy
- **missing:** A priority ranking layer or service that merges memory facts, reminders, and routines into a single actionable backlog; Better integration of tasks and contextual metadata with surface-specific scopes for mac-vision

### "Implement a resume and verification system for multi-step Mac automation workflows that combines mac-vision UI state snapshots with the workbench job receipts and context graph to detect interruptions, verify completed steps, and plan safe resumption."
- **useful because:** Currently, interrupted or long-running Mac automation workflows have no reliable way to verify progress against actual UI state or job state, leading to errors or duplicated work. Combining UI state and job receipts enables trustable resumption and recovery.
- **path:** mac-local-agent → relay → pendant → dashboard
- **model tier:** realtime
- **latency:** 100-500 ms per step verification
- **cost:** Moderate, involving state synchronization and snapshot diffing
- **security:** Requires access to job receipts and mac-vision UI snapshots; careful to safeguard user privacy and avoid exposing sensitive UI data externally.
- **missing:** UI snapshot capability for mac-vision; Integration of workbench job receipts with UI state verification logic

### "Allow the pendant button sw0 to trigger a secure mac-vision confirmation action by extended press gestures (double-press, long-press) distinct from the single press that starts a conversation, enabling physical transaction approval for destructive Mac actions."
- **useful because:** Currently the pendant has only a single button vocabulary for starting and stopping conversations. Additional physical gestures would enable secure, unforgeable physical confirmation steps for important Mac actions, improving reliability and user control.
- **path:** pendant → mac-local-agent
- **model tier:** realtime
- **latency:** 50 ms gesture detection
- **cost:** Very low, implemented on pendant firmware and mac-local-agent event handling
- **security:** Physical security and privacy are enhanced by requiring explicit physical interaction for confirming sensitive commands.
- **missing:** Firmware gesture recognizer on pendant; Mac agent support for recognizing and using these gestures as confirmation tokens


## What it asked for

### `c36-jeuh` (context) — mac-vision capabilities and best full use cases
- why: To understand how mac-vision integrates UI snapshots and workbench contexts for effective Mac control and multi-step workflows
- would change: Enable combining UI state from accessibility loop with task/workbench state to verify progress and resume work reliably

### `c37-k33d` (context) — mac-vision ui snapshot and workbench contexts
- why: To learn how to use the mac-vision accessibility snapshots alongside workbench contexts for multi-step task verification and rollback
- would change: Use actual UI observations from mac-vision loop to compare with expected states in job/workbench context, improving accuracy and robustness

### `c38-aq6y` (context) — mac-vision task priority list
- why: To access a reliable ranked list of owner Mac tasks to decide what mac-vision should focus on next
- would change: Pick the highest priority active Mac task from a trusted priority list rather than inventing priorities or guessing from sparse owner facts

### `t14-whux` (tool) — mac-vision_accessibility_automation_loop
- why: mac-vision depends on accessibility snapshots to perceive UI state without screenshots, crucial for planning interaction

```json
{
  "type": "object",
  "properties": {
    "mode": {
      "type": "string",
      "enum": [
        "accessibility"
      ]
    }
  },
  "required": [
    "mode"
  ]
}
```

### `t15-kak1` (tool) — mac-vision_task_priority_list
- why: To read the owner's current prioritized list of Mac work for mac-vision to act on

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

## Its own summary

Discovered core mac-vision tools and hardware specs. Requested needed tools for UI snapshot loop and task priority list. Proposed key missing capabilities: secure mac-vision accessibility loop, prioritized Mac task backlog, multi-step workflow resume with UI verification, pendant button confirmations, plus pendant hardware redesign for second button. These address the deep gaps in reliable UI automation, task prioritization, automation progress verification, and safe user confirmation. No further discovery possible this round.

**Biggest unknown:** How mac-vision accessibility UI loop, task priority list, and workbench integration are granted, built, and used for robust Mac automation.

