# Harness derivation — mac-vision — round 169

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Diagnostic commands to reliably inspect and list open browser tabs and inspect loaded web pages via browser_run_actions, with error handling and retries."
- **useful because:** The owner repeatedly requested tab and page inspections but current attempts fail. Robust commands to list tabs and inspect pages would allow the system to reliably observe browser state and content for browsing tasks and planning.
- **path:** mac-vision → browser-extension → relay-realtime
- **model tier:** realtime
- **latency:** 300ms
- **cost:** Low API calls cost, existing browser extension
- **security:** Reading browser tabs and page content requires browser extension permissions; owner control and explicit scope limitations apply.
- **missing:** Improved error detection and recovery in browser_run_actions tool.

### "Deliver an end-to-end pipeline for the 24 kHz superwideband audio path on the pendant, from firmware through Mac integration, to radio uplink and playback, with a monitoring and diagnostics UI on the Mac."
- **useful because:** This is a unique technical feature requested by the owner that leverages the full hardware and software stack; it demonstrates the pendant's advanced capabilities and is a flagship integration that requires orchestration of firmware, DSP, encoding, network, and Mac software.
- **path:** pendant → mac-vision → relay-realtime → dashboard
- **model tier:** background
- **latency:** seconds to minutes, offline resilient
- **cost:** Moderate computing cost on pendant for Opus codec and resampling; moderate API and network usage to transmit and monitor; dashboard UI rendering cost.
- **security:** Audio data privacy must be maintained; pipeline must safeguard any personal or sensitive information; owner consent needed for continuous audio streaming.
- **missing:** A stable and complete firmware implementation of 24 kHz superwideband audio capture and playback pipeline; Reliable Mac agent endpoints for telemetry and control of the audio path; Real-time monitoring UI on Mac and web dashboard for diagnostics and manual override

### "Allow the pendant's single button to act as a physical transaction approval latch for complex or destructive Mac UI actions initiated by mac-vision."
- **useful because:** Physical confirmation from the pendant of sensitive or destructive actions on the Mac prevents accidental or unintended state changes, improving safety and owner trust in automation. It can reduce reliance on verbal confirmations and offer a tangible control.
- **path:** pendant → mac-vision
- **model tier:** realtime
- **latency:** 100ms to 500ms
- **cost:** Minimal hardware cost; some firmware and mac agent integration work.
- **security:** The latch must only approve intended actions; spoofing or mistaken button presses could cause undesired effects; firmware and software must enforce strict usage policies.
- **missing:** Firmware support for button press latching and event signaling to Mac agent; Mac agent software to listen and enforce confirmation on sensitive actions

### "Enable mac-vision to autonomously detect complex multi-window workflows and context switches on the Mac by combining accessibility tree snapshots with time-series UI event streams, for proactive task continuity and interruption management."
- **useful because:** The owner often switches between multiple apps and windows to accomplish tasks. Detecting workflow changes and interruptions autonomously would let mac-vision anticipate context, pre-load resources, and avoid lost productivity from context switching costs.
- **path:** mac-vision → dashboard → relay-realtime
- **model tier:** realtime
- **latency:** 1000ms
- **cost:** Moderate API and model cost for analysis of event stream and UI snapshots.
- **security:** Extensive UI state monitoring requires owner trust and explicit permission; data handling must respect privacy.
- **missing:** Real-time UI event stream capture and storage; Algorithms to correlate event streams with accessibility tree snapshots; Dashboard UI for visualization and intervention

### "Give the owner granular control to define and customize safety and confirmation policies for mac-vision triggered Mac UI actions, including risk classification and action-specific confirmation dialogs on the pendant."
- **useful because:** Currently, all destructive or sensitive actions require a uniform confirmation from the owner. Allowing customizable safety policies per action type or risk class would let the owner balance automation speed and safety according to personal preference.
- **path:** mac-vision → pendant → dashboard
- **model tier:** realtime
- **latency:** 300ms
- **cost:** Low to moderate software complexity, UI and state management costs.
- **security:** Flexible confirmation policies increase UI complexity; must ensure policies cannot be bypassed unintentionally and that override flows are secure.
- **missing:** UI and API support for defining and enforcing safety policies; Integration with pendant button and audio confirmation systems

### "Implement a dynamic on-Mac knowledge context graph visualization and editing tool for the owner to navigate, annotate, and refine task and project relationships in real time."
- **useful because:** The owner currently has disparate fragmented memory and task stores. A visual knowledge graph would let them understand their current work context holistically, refine task connections, and guide the agent's prioritization and planning by manual input.
- **path:** mac-vision → dashboard
- **model tier:** background
- **latency:** interactive, under 500ms response
- **cost:** Moderate UI and backend engineering effort for graph rendering and live updates.
- **security:** Data privacy for owner’s task and memory data must be preserved; visualization must handle sensitive info carefully.
- **missing:** Live linkage between agent memory, context graph API, and UI editor; Graph rendering UI components with interactive editing


## Changes it proposed to its own stack

### `integration` — Add a combined cross-surface goal and task store that integrates hand-typed owner tasks, calendar/reminders (from dayPlan), briefing priorities, and live computer tasks, exposed as a unified ranked task queue to all agents.
- **owner gets:** Owner currently has only scattered task input methods, causing limited coordination and unclear priorities. A unified goal store ranked by priority will let the owner express what is important and coordinate agent action across Mac, browsing, briefing, and pendant surfaces.
- effort: Moderate engineering to merge existing stores and build ranking logic and query API, plus UI support across surfaces.  ·  risk: Complexity in ranking logic may cause suboptimal priorities initially; can be iterated; data loss risk low as all sources already exist.
- cost: Additional lightweight queries to unified API, minimal runtime cost.  ·  latency: Small extra latency for task queries.
- security: Does not increase permissions, just data aggregation.
- depends on: memoryService task writes; dayPlan read; briefing queues


## What it asked for

_Nothing._
