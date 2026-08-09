# Harness derivation — mac-vision — round 251

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Prioritized, context-aware Mac task manager with dynamic goal updates and multi-step execution tracking."
- **useful because:** The owner has no durable, ranked Mac task list that integrates with their live goals and workbench contexts, limiting productivity and automation potential. This would allow proactive Mac work planning, prioritization, and coordination to efficiently handle tasks and interruptions.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** seconds to minutes depending on task complexity
- **cost:** Moderate API usage on Mac agent due to dynamic context reads and updates; low compute on pendant.
- **security:** Requires store access to owner tasks and goals, coordination on task execution states; no external data leaves device without permission.
- **missing:** A live owner task prioritization and ranking store for Mac tasks.; Integration of task updates with workbench contexts to track multi-step progress.; Capability for the Mac agent to execute new task plans with intent state persistence and undo capabilities.

### "Seamless Mac UI state verification and sync for workbench contexts during multi-step delegated workflows using accessibility tree snapshot comparisons."
- **useful because:** Currently, the Mac delegate and workbench can track claimed multi-step work but have no way to confirm the real UI state matches the claimed work state, making fault detection and recovery difficult. Adding live UI state verification increases reliability and enables more trustworthy automation.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** seconds
- **cost:** Low to moderate; mainly reads from accessibility trees via mac-vision and cross-validates with workbench contexts.
- **security:** Requires trust and privacy assurances as UI state can contain sensitive information; data stays within local Mac agent unless explicitly authorized.
- **missing:** API on Mac vision loop to snapshot accessibility tree state and compare with claimed workbench context states.; Integration layers between workbench context manager and mac-vision agent.; Workflow for sync, alert, and recovery when mismatches are found.

### "Context-aware smart reminder creation and update synced between natural language voice commands via the pendant and macOS Reminders with actionable task state."
- **useful because:** The owner can create and update reminders via voice on the pendant, keeping them synced and actionable in macOS Reminders and available instantly for Mac agent workflow planning. This smooths task management and reduces friction between voice and desktop task modalities.
- **path:** mac-local-agent → pendant
- **model tier:** realtime
- **latency:** seconds
- **cost:** Low API and compute usage; uses existing mac_run_actions and voice input pipeline.
- **security:** Requires permission to interact with Reminders; all voice commands processed locally or in owner-controlled environment.
- **missing:** A unified task and reminder sync API between macOS Reminders, voice input pipeline, and Mac agent.; Natural language understanding optimized for task creation and updates from voice input.; Trust and privacy policies around task sync and updates.


## Changes it proposed to its own stack

### `mac-harness` — Implement a Mac-side persistent task and goal management service exposing an API for other agents and surfaces. It should rank, prioritize, and update owner tasks real-time, fuse inputs from owner memory, routines, reminders, and workbench contexts, and support querying progress and interruption handling.
- **owner gets:** The owner currently has no centralized task manager that is fully integrated with their digital work environment. This would unify and orchestrate all their active and pending work for the Mac surface, enabling smarter automation and better user experience.
- effort: High software engineering effort; requires changes across Mac agent, memory service, and multi-agent coordination.  ·  risk: Complexity in merging multiple data sources, risk of inconsistent state if badly implemented.
- cost: Moderate API and compute cost on Mac agent; no hardware impact.  ·  latency: Improved responsiveness in task queries and prioritizations.
- security: Requires access control around owner task memory and state transition.
- depends on: memoryService; workbench contexts; mac_run_actions; mac_delegate

### `integration` — Develop a low-latency data-sharing protocol between the pendant's audio capture pipeline and the Mac agent to enable real-time audio processing and contextual Mac automation triggers.
- **owner gets:** Currently, the pendant captures audio separately and resamples on the ESP32 bridge with limited integration into Mac-side automation. A more integrated pipeline allows audio cues (voice commands, environment sounds) to dynamically trigger Mac actions or workflows, improving responsiveness and utility without latency bottlenecks.
- effort: Significant firmware and Mac agent integration work, plus network stack tuning.  ·  risk: Increased system complexity and possible synchronization issues; must ensure privacy and security for audio data.
- cost: Increased usage of CPU and memory resources on pendant and Mac; potential battery impact on pendant.  ·  latency: Reduces audio-to-action latency, improving user experience.
- security: Requires strong encryption and access control for audio data exchange to safeguard privacy.
- depends on: bridge audio pipeline; mac_local_agent


## What it asked for

_Nothing._
