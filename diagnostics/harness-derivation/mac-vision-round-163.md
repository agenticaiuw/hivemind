# Harness derivation — mac-vision — round 163

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full mac-vision autonomous computer use on the owner's Mac with programmatic UI control of apps and browser using accessibility tree, safe from focus theft, and with action confirmation for destructive commands."
- **useful because:** This unlocks mac-vision's ability to drive the Mac UI directly without degrading to pixel clicks or stealing focus, enabling seamless multi-step workflows, error recovery, and rapid task completion with owner trust.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** realtime
- **latency:** 1 second per UI action step
- **cost:** Low API cost but requires macOS Accessibility permission and computing for UI parsing and action planning.
- **security:** Needs explicit macOS Accessibility permission granted by owner; must confirm destructive actions; UI tree-based only, no screenshots sent without separate consent.
- **missing:** macOS Accessibility permission for running binary; computerUse.loopEnabled and visionUploadConsented granted

### "Maintain a unified goal and task memory for the owner's current work items and priorities, integrated cross-device and cross-application, with top critical and due soon items surfaced."
- **useful because:** Currently owner intent is fractured and sparse; a unified, ranked task memory enables focus on the right work and coordination across all agent surfaces and devices.
- **path:** mac-planner → relay-realtime → mac-vision → browser-extension
- **model tier:** background
- **latency:** seconds to see updated priorities
- **cost:** Moderate API cost for memory read/write and ranking algorithms.
- **security:** Requires secure storage and owner control over what is stored and prioritized.
- **missing:** Cross-surface goal coordination; Automatic task priority estimation

### "Allow the owner to specify a task or goal in natural language which mac-vision can break down into substeps and execute through the appropriate devices and software apps, including web browser and system UIs."
- **useful because:** Simplifies owner requests for complex workflows that span multiple apps, making the agent a truly effective assistant for real-world computer tasks.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** seconds to plan and begin execution
- **cost:** Higher API cost due to planning and multi-step coordination.
- **security:** Must handle sensitive data carefully; destructive actions require confirmation.
- **missing:** Multi-step Mac delegate orchestration; Deep app and browser UI knowledge

### "Enable the pendant hardware button to trigger specific mac-vision controlled Mac actions or sequences, with context-aware queries and secure confirmation for destructive steps."
- **useful because:** Physical button on pendant is a convenient, low-friction interface to initiate computer control sequences or commands, integrating wearable and Mac agent interplay seamlessly.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** realtime
- **latency:** milliseconds to seconds based on command complexity
- **cost:** Minimal to moderate depending on action complexity; mostly local device to Mac network communications.
- **security:** Need secure button-action mapping to avoid accidental destructive behavior; explicit owner configurable payloads.
- **missing:** mac-vision handler for pendant moment bookmarks and physical_transaction_approval_latch

### "Seamless cross-device personal context sharing and recall that supports switching tasks between Mac, pendant, and mobile app with no loss of information or interruption."
- **useful because:** The owner can start a task on one device and continue it on another seamlessly, preserving context, notes, and progress, improving productivity and experience.
- **path:** mac-vision → pendant → relay-realtime → mobile
- **model tier:** background
- **latency:** seconds to sync context state across devices
- **cost:** Moderate API and storage cost for syncing and access.
- **security:** Requires secure end-to-end encryption and owner consent for context sharing.
- **missing:** Cross-storage synchronization and context graph merging

### "Proactive actionable notifications on the pendant for important Mac or system events, including reminders, calendar alerts, and critical messages, with the ability to respond via simple voice or button commands."
- **useful because:** The owner is alerted immediately on their wearable to crucial upcoming events or system states, reducing missed communications and improving responsiveness without needing to check the Mac.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** few seconds from event to notification
- **cost:** Low to moderate for event detection and delivery systems.
- **security:** Notifications must be privacy-respecting; no leak of sensitive info without explicit consent.
- **missing:** Event filtering and delivery infrastructure; Wearable voice and button command responder integration

### "Integrated multichannel voice command system that allows the owner to control Mac, browser, and wearable pendant features from any device with natural language, including fallback and contextual disambiguation."
- **useful because:** Provides a unified, natural, and flexible voice interface across all devices owned, increasing ease of use and accessibility, and reducing latency or interruptions in interaction.
- **path:** mac-vision → pendant → browser-extension → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to few seconds per command
- **cost:** Moderate API cost for voice processing and intent routing.
- **security:** Voice input must be processed securely; commands that can trigger destructive actions require explicit confirmation.
- **missing:** Unified voice intent model and command routing across devices; Contextual disambiguation logic

### "A secure ad-hoc local wireless communication protocol between pendant and Mac for high-bandwidth, low-latency data transfer that supplements LTE and USB connections, enabling richer real-time interactions and sensor data sharing."
- **useful because:** Improves reliability and range of communication between wearable pendant and Mac, enabling new use cases like continuous health monitoring, local audio processing, and synchronized multimodal assistance with minimal latency.
- **path:** pendant → mac-vision
- **model tier:** background
- **latency:** sub-second local link latency
- **cost:** Hardware and firmware development cost; low ongoing API usage cost.
- **security:** Wireless link must be encrypted, authenticated, and resistant to spoofing or eavesdropping.
- **missing:** Low-latency, secure local wireless protocol implementation on pendant and Mac bridge


## Changes it proposed to its own stack

### `memory` — Implement a robust cross-surface persistent task memory system with owner-configurable priorities, deadlines, and statuses, integrated with existing facts.json and dayPlan but extended for agent action coordination.
- **owner gets:** The owner gets a consistent, unified view and management of tasks and priorities across Mac, pendant, and relay, enabling better focus and automated action.
- effort: Medium engineering effort over multiple agent layers and storage subsystems.  ·  risk: Data loss or inconsistency during migration; mitigated by fallback and backup.
- cost: Moderate; involves additional storage and API usage for reads and writes.  ·  latency: Minimal; mostly background synchronization.
- security: Needs secure storage and access controls.

### `interaction` — Design a model-triggered multimodal confirmation and progress report system for mac-vision actions initiated via pendant or voice, with user-acknowledged checkpoints before destructive or irreversible UI operations.
- **owner gets:** Prevents accidental destructive actions and keeps owner informed of progress through complex UI workflows, increasing trust and safety.
- effort: Medium; involves UI design, messaging protocols, and integration with existing action plans.  ·  risk: Potential delays in execution waiting for confirmation; mitigated with timeout and override procedures.
- cost: Low; mainly UI and messaging traffic.  ·  latency: Moderate for actions requiring explicit confirmations.
- security: High; confirmation UI must be tamper-proof and visibly secure to owner.
- depends on: computerUse.loopEnabled

### `hardware` — Upgrade the pendant hardware from Nordic nRF9160 DK to a custom SoC with significantly more RAM, multiple physical buttons, and dedicated secure UI feedback elements (small screen or LEDs) to enable richer, multi-gesture physical interactions and local context display.
- **owner gets:** Allows richer physical interactions for context switching, local notifications, and secure confirmation without relying solely on voice or Mac screen, enhancing wearability and independent use.
- effort: High; requires hardware design, firmware, and OS integration.  ·  risk: Delays and cost in hardware redesign; requires new firmware and software ecosystem support.
- cost: High capital and component cost increase for custom hardware.  ·  latency: No impact on system latency; improves local responsiveness.
- security: Improved security by local UI confirmation; needs secure hardware design to prevent spoofing.


## What it asked for

_Nothing._
## Its own summary

Discovered hardware specs, agent capabilities/mac actions, owner permissions, devices, and routes. Key proposals: Enable mac-vision autonomous UI control with macOS Accessibility permission and computerUse.loopEnabled; unified cross-surface task memory with priority; pendant button to trigger mac-vision actions with confirmation; interaction layer for confirmation and progress feedback; multi-agent workflow orchestration enhancements. Biggest unknown: owner granting macOS Accessibility permission and enabling computerUse.loopEnabled, the critical gate to safe advanced UI automation.

**Biggest unknown:** Whether the owner will grant macOS Accessibility permission to the running binary and explicitly enable computerUse.loopEnabled, enabling mac-vision's full autonomous UI interaction.

