# Harness derivation — mac-vision — round 260

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a prioritised task list on the Mac surface that the owner wants done, integrated with multi-step workflows and ranking by owner's preferences and deadlines."
- **useful because:** The Mac-vision agent now knows no task list exists but has visibility into owner-stated priorities and workbench workflows. A prioritised real task list would focus attention and provide a clear queue to act on.
- **path:** mac-local-agent → mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** low CPU, no special API calls
- **security:** Tasks reflect the owner's confidential intentions. Only the owner and their trusted agents should read or modify.
- **missing:** Integration with workbench open contexts and handoff data for multi-step workflow segmentation.; A ranking algorithm respecting event deadlines, overdue state, and owner preferences.; A durable task store that agents like mac-vision can query.

### "Create an intelligent router in mac-vision to choose between mac_run_actions, browser_run_actions, and mac_delegate for different task types based on task complexity, urgency, and permission risk."
- **useful because:** Currently mac-vision only knows the capabilities but not how best to pick which tool to use for a given computer task. An intelligent router would automate appropriate tool choice for efficient and safe execution.
- **path:** mac-vision → mac-local-agent
- **model tier:** background
- **latency:** under a second for routing decision
- **cost:** minimal compute, no special APIs
- **security:** Must respect owner permissions and preferences strictly. Router must not escalate permissions.
- **missing:** Policy knowledge base or training data mapping task types and complexity to tools.; Integration with owner preferences and risk scoring for confirmation.; Integration with task list or workbench context to understand task scope.

### "Enhance mac-vision with visual UI verification to compare accessibility-based planned UI states to actual visual pixels or screenshots, providing a claim-versus-actual verification for UI changes."
- **useful because:** The workbench contexts verify claim vs actual on file system changes but lack UI state verification. This would reduce errors or mismatches in UI automation by mac-vision and increase robustness.
- **path:** mac-vision → mac-local-agent
- **model tier:** background
- **latency:** seconds
- **cost:** moderate due to image processing
- **security:** Visual data is sensitive and must remain on-device or encrypted to prevent privacy leaks.
- **missing:** UI screenshot capture integrated with accessibility tree; Image comparison models capable of identifying UI discrepancies; Secure handling and storage of visual data for claims verification.

### "Implement a smarter confirmation system integrated into mac-vision that only interrupts the owner for high-risk destructive actions but allows all read and non-destructive confirmation-free actions to proceed transparently."
- **useful because:** The owner has preferences to confirm destructive actions but allow reading and non-destructive actions without asking. Current mac-vision executes all actions with equal opacity or needs manual selection.
- **path:** mac-vision
- **model tier:** background
- **latency:** milliseconds to a second
- **cost:** low compute
- **security:** Must never accidentally suppress confirmation for truly destructive actions or escalate privileges illegally.
- **missing:** A risk scoring framework mapping mac-vision actions to destructive or nondestructive categories.; A confirmation dialog or pendant approval protocol integrated into the UI loop.; Integration with owner preference store for trust boundaries.

### "Add a facility in the Mac-vision agent to log detailed UI interaction failures, including computed accessibility actions, expected UI states, and side effects, so that developers and the owner can debug automation errors effectively."
- **useful because:** Automations on Mac UI via mac-vision can fail quietly or with unclear reasons. A detailed failure log with UI snapshot states and interaction metadata would greatly speed debugging and increase reliability.
- **path:** mac-vision
- **model tier:** background
- **latency:** seconds for detailed logging
- **cost:** moderate compute and storage
- **security:** Logs contain detailed UI and interaction data and must be secured to prevent leakage of sensitive visual or textual info.
- **missing:** Structured logging infrastructure for action and UI state events.; UI snapshot integration and storage.; Error classification and categorization for quick filtering.

### "Enable mac-vision to autonomously generate, schedule, and prioritize multi-step workflows on the Mac using all three action tools, integrated with memory and owner preferences, without human intervention in creating tasks."
- **useful because:** Currently mac-vision can only react to existing tasks but cannot create or prioritize multi-step workflows proactively. Autonomous workflow generation would multiply productivity by anticipating and managing complex Mac work automatically.
- **path:** mac-vision → mac-local-agent
- **model tier:** background
- **latency:** minutes for planning large workflows
- **cost:** moderate compute with callouts to language models
- **security:** Workflows may include sensitive commands and data; strict permission control and owner review features required.
- **missing:** An advanced workflow planning engine able to generate multi-step plans from natural language goals.; Full integration with memory facts, owner preferences, and local agent capabilities.; Secure review and approval methods for autonomous task creation.

### "Provide a visual reconciliation system for mac-vision, which records both accessibility tree states and pixel-based screenshots, to automatically detect, diagnose, and recover from UI automation mismatches or regressions."
- **useful because:** Current automation relies heavily on accessibility tree which may desync or degrade over time. This reconciliation improves robustness and reduces failures by cross-validating visual and semantic UI states and auto-correcting or alerting owner when desyncs occur.
- **path:** mac-vision → mac-local-agent
- **model tier:** background
- **latency:** seconds to minutes depending on UI complexity
- **cost:** moderate compute and storage for image processing and history storage
- **security:** Stored UI screenshots are visually sensitive and must be encrypted and carefully access-controlled.
- **missing:** Integration of screen capture with accessibility state recording.; Image processing models for UI recognition and difference detection.; Recovery protocols from detected UI mismatches.


## Changes it proposed to its own stack

### `hardware` — Add a second physical button to the pendant to enable richer contextual controls and gesture mappings without delaying single-button actions.
- **owner gets:** Currently the pendant has only one button limiting possible input gestures, which constrains quick multifactor input. A second button allows simultaneous or sequence inputs, enabling shortcuts, confirmations, and mode switches naturally without delay.
- effort: Medium engineering effort to redesign pendant enclosure and firmware for dual-button input.  ·  risk: Minimal risk, mainly related to button debounce and power consumption increases, easily mitigated with proper design.
- cost: Small increase in BOM cost and power draw per added button.  ·  latency: No latency impact on main CPU cycles.
- security: None significant; input remains local and owner authenticated.


## What it asked for

_Nothing._
