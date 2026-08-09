# Harness derivation — mac-vision — round 171

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Add recovery and escalation mechanisms to the mac-vision computer-use loop that prompt owner confirmation on ambiguous or failed UI control states before any high-impact UI actions are taken."
- **useful because:** Prevents unsafe or unintended UI automation actions by ensuring owner control and consent when the automation cannot confidently proceed. Increases trust and safety of the loop.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Interactive, within 3 seconds
- **cost:** Low to moderate per invocation; depends on UI tree complexity and confirmation flow
- **security:** Requires owner confirmation step and secure messaging; no private data leaves unless confirmed.
- **missing:** Owner physical interaction must be integrated, confirmation UI or voice prompts needed, strategy to pause automation loop until confirmation.

### "Integrate the pendant's physical button as a safe confirmation method for high-risk or high-impact UI actions triggered by mac-vision's computer-use loop."
- **useful because:** Provides a secure, physical second factor approval for critical UI operations, preventing accidental or malicious automation actions. Leverages pendant hardware and existing physical_transaction_approval_latch.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Within seconds, synced with UI action timing
- **cost:** Minimal; mostly firmware integration and agent messaging
- **security:** Requires secure handling of physical approval events, authenticated messages to the Mac agent, no sound or pixel data involved.
- **missing:** Firmware support for physical_transaction_approval_latch usage, reliable event delivery to Mac, UI agent integration for pause and resume.

### "A continuous, real-time accessibility tree monitor and narrator running on the Mac that reads the full UI hierarchy without needing screen recording, providing the owner with a live narrative and textual description of the computer state and changes."
- **useful because:** This gives the owner instant situational awareness of what the Mac UI is currently showing and what changes occur without privacy-invasive screen capture. This supports accessibility, transparency, and trust in AI-driven automation and helps the owner understand what the system 'sees' at all times.
- **path:** mac-vision → relay-realtime → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second per update
- **cost:** Moderate, as continuous observation and narration requires real-time processing of changing accessibility trees.
- **security:** Data stays local to the device, no screen pixels or sensitive image data leaves; narration is controlled and limited to avoid privacy leaks.
- **missing:** A system to efficiently detect and process real-time changes in the accessibility tree, an interface to render narration and textual description live, permission to use accessibility APIs continuously.

### "A high-level declarative scripting framework for UI automation that compiles into verified safe action sequences on the Mac, with strong undo semantics and stepwise execution control."
- **useful because:** Currently, there is no safe, transparent, and easily understandable way for the owner or AI to automate complex GUI workflows on the Mac. This system would allow programming UI automations with guarantees about undoability and observability, greatly enhancing trust and effectiveness of automation.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** interactive, seconds-scale per workflow step
- **cost:** Moderate to high, requiring robust UI modeling and state tracking.
- **security:** Automation scripts run with explicit owner knowledge and optionally gated approval for impactful actions; no unintended side-effects.
- **missing:** Compiler and runtime for declarative UI scripts, integration with accessibility automation APIs, support for complex undo and rollback mechanisms.

### "A dynamic UI state differencing and patching system that tracks changes in the Mac accessibility tree and selectively applies minimal UI actions to reach desired goal states efficiently."
- **useful because:** Instead of rigid scripted sequences, this system can reconcile UI changes dynamically, making automation more robust to UI changes, app updates, and transient states. It would increase reliability and reduce failure in automated UI manipulation.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds per state update
- **cost:** Moderate, involving tracking UI tree state and efficiently planning minimal mutation actions.
- **security:** Limited to accessibility nodes and actions, with logs, undo, and owner control.
- **missing:** Efficient UI tree differencing algorithms, planning engine to produce minimal action sets, integration with execution APIs for UI control.


## What it asked for

_Nothing._
## Its own summary

Discovered the current state of mac-vision agent and its dependencies on macOS Accessibility permission. Identified a critical gap: no exposed observable UI stepwise automation API from the vision loop, which blocks safe autonomous computer use. Proposed key capabilities including safe undo, error recovery, escalation, and physical pendant approval integration. Requested peer input on exposed UI plans and priorities. Confirmed pending hardware and permission grants. Awaiting peer replies and further exploration of execution APIs.

**Biggest unknown:** Presence or absence of an exposed API for planned UI steps and undo points from the vision loop automation to enable safe observable computer use by mac-vision.

