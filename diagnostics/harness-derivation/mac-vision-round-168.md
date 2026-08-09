# Harness derivation — mac-vision — round 168

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A persistent, prioritized goal and task management system integrated with memoryService on the Mac that can ingest owner stated tasks, calendar reminders, and routines, and dynamically rank and present them for autonomous agent use."
- **useful because:** Currently the owner has only sparse free-text tasks and calendar reminders with no prioritization or integration, limiting autonomous agent effectiveness. A unified prioritization system would enable intelligent, goal-driven computer use and task execution.
- **path:** mac-planner → mac-vision → unified
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Low API and lightweight compute cost on Mac and cloud
- **security:** Owner task data is sensitive and must be stored and used only locally or encrypted in transit.
- **missing:** Task priority and dependency model; UI or voice interface for owner task input and adjustment; real-time sync with existing memoryService and calendar

### "Real-time event-driven task update notifications and triggers to the mac-vision agent when owner tasks or goals change in memoryService or routines."
- **useful because:** This avoids inefficient polling and enables the mac-vision agent to immediately plan and act on new or updated goals and tasks, improving responsiveness and autonomy.
- **path:** mac-vision → relay-realtime → unified
- **model tier:** realtime
- **latency:** milliseconds to 1 second
- **cost:** Low API call cost, mostly local event monitoring
- **security:** Secure event transport with authentication and owner control to prevent flooding or false triggers.
- **missing:** Event subscription and push mechanism from memoryService and routines to agents; Event routing and filtering logic

### "A collaborative multi-agent goal planning system that integrates inputs from mac-vision, mac-planner, relay-realtime, and browser-extension, allowing for cross-surface task negotiation, priority arbitration, and unified execution plans for the owner."
- **useful because:** Currently, individual agents operate mostly in isolation on tasks seen on their surface. A shared multi-agent planning system would enable seamless task division, reduce duplicate work, and optimize execution paths across devices and surfaces for the owner.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension → unified
- **model tier:** background
- **latency:** seconds for plan convergence and arbitration
- **cost:** Moderate API and compute cost; requires orchestration of multiple agents and surface data.
- **security:** Must ensure data privacy across agents and secure message passing. Tasks and priorities are owner-sensitive data.
- **missing:** Inter-agent communication and negotiation protocols; Shared persistent cross-surface goal store with versioning and conflict resolution; Unified plan formation and distribution mechanism


## Changes it proposed to its own stack

### `integration` — Add a secure event subscription and push mechanism from memoryService and routines stores to the mac-vision agent and other interested agents, enabling real-time notification of task and goal changes without polling.
- **owner gets:** This improves system responsiveness and autonomy by allowing immediate reaction to owner task updates and scheduling changes.
- effort: Medium engineering effort on server and agent communication layers.  ·  risk: Event floods or loss must be mitigated; authentication and rate limits required.
- cost: Minimal additional network and processing cost; mostly on local systems.  ·  latency: Significant reduction in task update reaction latency (milliseconds vs seconds or more).
- security: Requires secure event channel; potential data leakage if compromised, mitigated by encryption and authentication.
- depends on: memoryService API extension; routines API extension


## What it asked for

_Nothing._
