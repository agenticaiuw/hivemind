# Harness derivation — mac-vision — round 157

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to read and interact with the Mac UI via accessibility APIs without focus theft or visual disruption, given the necessary macOS Accessibility permission for the AI Pendant Agent binary."
- **useful because:** This is the foundational capability enabling the system to automate and assist with complex multitasking, task execution, and UI interactions safely and robustly without pixel captures or focus stealing.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100-300 ms per interaction
- **cost:** Very low API cost, mostly computation for UI tree parsing and decision making.
- **security:** Needs explicit owner grant and macOS TCC Accessibility permissions for safety; must prevent unintended inputs or clicks; all actions logged with confirmations for destructive changes.
- **missing:** macOS Accessibility grant for AI Pendant Agent binary; computerUse.loopEnabled set to true; Safety confirmation UI for destructive actions

### "Create a structured goal and task manager surfaced jointly across all agents and the owner, with programmatic APIs to read, add, update, and prioritize tasks and goals, integrated with daily routines and the day plan."
- **useful because:** Currently, the system only has hand-typed or read-only tasks and routines. A shared structured goal manager enables coherent multi-agent coordination, prioritization, and proactive action planning.
- **path:** mac-planner → mac-vision → relay-realtime → unified
- **model tier:** background
- **latency:** seconds for syncing and updates
- **cost:** Moderate API use to sync and update tasks, mostly data management cost.
- **security:** Proper access controls to prevent accidental or unauthorized edits; task data privacy.
- **missing:** Full task goal manager service; Cross-agent synchronization protocol; UI and voice integration for task management

### "Allow the mac-vision agent to create, read, and edit notes and draft documents in the owner's VS Code environment, integrated with voice and UI control capabilities."
- **useful because:** The owner's preferred editor is VS Code, and enabling voice-controlled or automated note and draft management directly in VS Code would streamline workflows and reduce switching context.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** sub-second to a few seconds for editing and retrieval
- **cost:** Low to moderate, mostly local file IO and UI automation cost.
- **security:** Editing files automatically risks data loss or corruption; must have undo, confirm before deleting or overwriting.
- **missing:** VS Code UI automation integration with voice agents; File backend hooks for notes/drafts

### "Integrate a seamless, high-fidelity 24kHz audio path end to end between the pendant and the Mac for superwideband audio recording and playback, usable by all relevant agents for audio capture and playback."
- **useful because:** The owner has a task to 'ship the 24kHz superwideband audio path end to end on the pendant.' This capability would realize that task, enabling much higher quality audio for voice interaction and recording.
- **path:** pendant → mac-planner → relay-realtime → audio
- **model tier:** background
- **latency:** low-latency audio streaming
- **cost:** Hardware supported, low CPU overhead with some realtime network or USB streaming cost
- **security:** Ensure privacy and security of audio streams; protect against unauthorized recording.
- **missing:** Complete superwideband audio drivers and paths on pendant firmware; Mac side driver and API integration; Cross-agent coordination for audio streaming

### "A proactive, continuous Mac UI automation and assistance agent that uses real-time accessibility tree reading and selectable partial automation: it can suggest next clicks and keystrokes contextually and ask for confirmation or manual override before making changes. It never steals focus or relies on pixel-based screenshots, preserving user control and privacy while being deeply useful."
- **useful because:** This would provide real, non-intrusive Mac UI automation for complex multitasking, allowing the owner to offload repetitive or error-prone tasks with explicit control and safety.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100-300 ms per action decision
- **cost:** Low API cost for accessibility reads, moderate ML compute for next-step prediction and dialogue.
- **security:** Needs strict macOS Accessibility permission, owner confirmation for destructive actions, clear UI/voice feedback for automation steps.
- **missing:** Full macOS Accessibility permission granted to AI Pendant Agent binary; computerUse.loopEnabled permanently enabled; Integration with local undo history and action reversal.

### "A cross-surface, multi-agent task and goal manager with priority scoring, deadline tracking, and dependency graph support that integrates calendar, reminders, voice notes, and project memory. It provides APIs for agents and the owner to collaboratively refine and update goals and next actions in real-time."
- **useful because:** Today the owner lacks a unified machine-readable workspace for what they want done now, causing missed context and suboptimal assistance. This system would ensure multi-agent alignment and proactive action towards meaningful outcomes.
- **path:** unified → mac-planner → mac-vision → relay-realtime
- **model tier:** background
- **latency:** seconds for updates and syncing
- **cost:** Moderate API usage and data storage, common in task management apps.
- **security:** Access control to prevent unauthorized edits; privacy of sensitive task data must be enforced.
- **missing:** Cross-agent synchronization protocols; Shared persistent task and goal storage; UI and voice surfaces to view and edit tasks

### "An integrated multimodal document and note management system that tightly couples the owner's voice commands, mac-vision UI control, and VS Code editor APIs to create, manage, and navigate code drafts and notes without breaking the owner's workflow or requiring manual context switching."
- **useful because:** Voice-driven document editing and drafting in the owner's preferred editor reduces friction and enables rapid idea capture and iteration, enhancing productivity and creativity.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** sub-second to a few seconds response time
- **cost:** Low compute and file IO costs; primarily integration and UI control overhead.
- **security:** File safety with robust undo, no unwanted overwrites; clear confirmation for destructive edits.
- **missing:** VS Code APIs accessible to agent; Voice control integration with mac-vision computerUseLoop; File system integration for notes and drafts

### "A private, encrypted audio streaming and processing pipeline that routes 24kHz superwideband audio from the pendant hardware to the Mac and relay in real time, enabling high-fidelity voice commands, noise suppression, and offline processing."
- **useful because:** This realizes the owner's task to ship a full end-to-end very high quality audio pipeline. It improves voice command accuracy, personal audio capture, and supports advanced audio-based features.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** background
- **latency:** low-latency audio streaming
- **cost:** Some CPU and memory needed for coding and real-time data streaming, plus radio and USB bandwidth
- **security:** Strong encryption and privacy controls essential; must prevent unauthorized recording and leaks.
- **missing:** Fully implemented 24kHz audio drivers and firmware on pendant; Real-time audio routing and driver integration on Mac and relay; Cross-agent audio stream sharing framework


## What it asked for

_Nothing._
## Its own summary

Discovered that mac_run_actions enables mac UI operations; accessibility-driven mac-vision loop is blocked on macOS Accessibility grant; current task state is hand-typed and lacks structure; proposed enabling mac-vision loop, structured task manager, VS Code note integration, and end-to-end 24kHz audio path. Key need is the macOS Accessibility grant to unlock UI control.

**Biggest unknown:** When or whether the owner will grant the macOS Accessibility permission to enable the mac-vision computerUseLoop for safe UI automation.

