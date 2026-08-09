# Harness derivation — mac-vision — round 191

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide the Mac-vision agent capability to read the current on-screen UI controls and plan an accessibility-driven interaction loop for Mac applications."
- **useful because:** It lets the system interact with any Mac app's UI without relying on pixel recognition or screen captures, leveraging accessibility APIs for precise and less intrusive control. This enables powerful, context-aware computer use that respects the owner's privacy and minimizes disturbance.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** less than 1 second to read and plan a UI action sequence
- **cost:** low to moderate token usage, dominated by planning rather than reading
- **security:** Requires macOS Accessibility API permission granted to the exact running binary; does not involve pixel capture or screen recording; safe but sensitive because it can read/control other apps.
- **missing:** a UI state store that records actual control states vs. intended states for reconciliation after action; progress and error feedback integration between this loop and the rest of the system; a way to verify and undo UI actions through the accessibility API

### "Create a live prioritized task list for the mac-vision agent based on the owner's current interests, open workflows, and reminders."
- **useful because:** The system can focus on what the owner really wants done next on the Mac, enhancing productivity and relevance of automation. Avoids wasted effort by focusing on true priorities rather than unstructured or unrelated tasks.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** under 2 seconds including fetching and filtering tasks
- **cost:** very low, mostly local filtering and simple ranking
- **security:** Exposes only what the owner has already granted the system to know; no new permissions needed.
- **missing:** a system to store and update task priorities beyond clock-based routines and raw reminders; integration with multi-surface goal stores, including memory facts and workbench context tracking

### "Create a soft undo system for mac-vision accessibility actions that reconciles actual UI state with claimed state after each step."
- **useful because:** When mac-vision interacts with Mac apps using accessibility API, UI states may drift or actions may fail silently. A soft undo and reconciliation system ensures consistent and reliable interaction, improving trust and workflow continuity.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** under 3 seconds to check states and decide rollback
- **cost:** low to moderate, mainly API calls and state comparisons
- **security:** This system interacts directly with UI controls; undo needs careful scope and confirmation controls to avoid unwanted state changes.
- **missing:** UI state difference detection over the accessibility tree; Undo command patterns for accessibility actions; Integration with workbench contexts for resumed workflows

### "Enable the mac-vision agent to track and verify multi-step computer tasks by reading actual UI state versus expected progress from the workbench context system."
- **useful because:** This provides resilience and reliability in complex multi-step workflows by allowing the agent to catch and recover from mismatches between what it planned and what actually happened on screen, ensuring continuity and correctness.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** under 5 seconds to compare UI state and context, reroute if needed
- **cost:** moderate, due to complexity of UI state reading and context reconciliation
- **security:** Requires continuous accessibility API permission and state comparison, risk of repeated sensitive UI reads; ensure strict data handling and owner consent.
- **missing:** way to represent expected UI states for workflow steps; system to compare expected versus actual accessibility tree states; integration with workbench context diffs and job handoff data

### "Have the mac-vision agent provide transparent, natural-language, detailed reports on what it is about to do on the Mac UI before acting, for owner approval."
- **useful because:** This increases owner trust and control by explaining planned UI interactions verbally, letting the owner confirm or cancel actions before they happen, reducing errors and surprises.
- **path:** mac-vision → pendant
- **model tier:** realtime
- **latency:** under 2 seconds for explanation generation
- **cost:** low, mostly prompt engineering and UI flow
- **security:** Needs to limit exposure of sensitive UI data in spoken content; must respect privacy guidelines.
- **missing:** dialogue coordination between mac-vision and pendant for confirmation; UI representation suitable for natural language summarization

### "Allow the mac-vision agent to record and replay verified UI interaction scripts for recurring multi-step tasks as a safe, auditable macro system."
- **useful because:** Owners can automate complex workflows that require exact UI interactions, replaying them reliably without manual repetition, saving time and reducing errors.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 5 seconds to debug and replay a script
- **cost:** Moderate, as script storage and verification need storage and some computation.
- **security:** Recorded UI scripts hold sensitive workflows; must be encrypted and can only run with owner explicit approval.
- **missing:** UI command script capture and replay engine; verification of UI states between steps; safe error recovery and manual override; storage for scripts linked to identity

### "Enable mac-vision to autonomously adjust and personalize the desktop UI layout and settings for accessibility and productivity based on owner preferences and habits."
- **useful because:** Owners benefit from a dynamically optimized workspace that reduces friction and increases efficiency, tailored to their usage patterns and preferences.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 3 seconds for layout adjustment decisions
- **cost:** Moderate due to analysis and state change operations.
- **security:** Requires deep system access; must be strictly controlled and transparent to owner to avoid unwanted changes.
- **missing:** user preference capture and modeling; UI state reading and writeback on layout settings; policy layer for safe and reversible UI adjustments


## Changes it proposed to its own stack

### `integration` — Build a coordinated owner-agent dialogue framework that pairs mac-vision's UI state reading and action planning with the pendant's voice interface to enable fluent spoken confirmations and cancellations before UI interaction steps.
- **owner gets:** The owner gets a conversational, understandable interaction model for computer control, reducing accidental actions and increasing confidence in automation.
- effort: Significant, requires linking live UI state, voice synthesis/recognition, and conversational state tracking across devices.  ·  risk: New points of failure in voice-agent synchronization and dialogue coherence; fallback needed.
- cost: Moderate API usage for voice interaction and UI state processing.  ·  latency: Adds interaction latency but within conversational limits.
- security: Sensitive UI data handled in voice transcripts; requires strict access control and owner consent.
- depends on: /vision-loop/* accessibility-reading and planning; pendant voice interface integration


## What it asked for

_Nothing._
