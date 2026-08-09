# Harness derivation — mac-vision — round 272

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a live prioritized task list of Mac-specific work items curated for computer automation and UI control."
- **useful because:** The owner currently has no task list tailored to what mac-vision should automate on the Mac. Such a prioritized list would allow mac-vision to know what to act on, report progress, and follow up autonomously, vastly improving value and autonomy.
- **path:** mac-local-agent → mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** few seconds
- **cost:** low, mainly model cost
- **security:** Tasks are private to the owner, so must be stored securely and not leaked. Requires user consent to curate tasks specifically for Mac automation.
- **missing:** A writable task queue in memory specialized for mac-vision with owner input or AI curation.; A policy for prioritizing and updating this task list based on owner feedback and completed work.; Integration to mac-vision for reactive loop to pick next task from this list.

### "Establish live, fine-grained coordination between mac-planner and mac-vision agents to delegate UI-level computer tasks and manage retries, undo, and failure detection robustly."
- **useful because:** This would enable seamless execution of complex workflows split between planning and UI control layers. Owners will get smoother, more reliable automation without manual intervention in failures or retries.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** whole workflow minutes but short step latencies
- **cost:** moderate due to orchestration overhead and state tracking
- **security:** Must control access to UI control and task data carefully to avoid misuse or leaks.
- **missing:** A protocol or API for mac-planner to issue commands and receive status updates from mac-vision in real-time or near real-time.; Durable storage for retry queues and undo logs linked to UI actions.; Ability for mac-vision to report UI state contradictions back to planner and request guidance.

### "Provide a physical user confirmation mechanism on the pendant for high-risk or destructive UI actions initiated by mac-vision, integrated directly into the computer use loop."
- **useful because:** Owner safety and control strongly demand manual confirmation for irreversible or dangerous actions such as deleting files, sending emails, or buying. Integrating this with the pendant's hardware offers a seamless secure confirmation path distinct from touchscreen or software UI.
- **path:** pendant → mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second to acknowledge
- **cost:** minimal hardware, minor firmware update
- **security:** The confirmation must be delivered securely and with clear user feedback to avoid accidental acceptance or denial. No leaks of pending actions.
- **missing:** Harnessing the existing pendant button input with a new confirmation protocol keyed to mac-vision's action queue.; Firmware skill on pendant to capture and relay button press confirmations as atomic transaction approvals.; Modification of mac-vision loop to pause pending high-risk commands until pendant confirmation.; UI and voice feedback to convey pending confirmation state to the owner.

### "Enable the mac-vision agent to recognize when an accessibility-based UI action falls back to a simulated mouse event causing undesirable UI focus and provide safe alternative strategies or user warnings."
- **useful because:** The existing accessibility UI automation silently falls back to real mouse clicks when native accessibility actions fail, which can cause the owner's focus to be stolen and disrupt their workflow. Detecting and mitigating this would improve safety and user experience.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second detection
- **cost:** minimal model usage, mostly local monitoring
- **security:** Must carefully distinguish simulated input failure events without false positives. No new privacy risks.
- **missing:** Instrumentation in mac-vision loop to detect when ui_click degrades to real mouse click on background window.; Alternative UI automation strategies to avoid focus theft, such as text-based interactions or warning dialogs.; User settings for when to allow or block fallback mouse clicks.; Reporting and logging for such events for owner review.

### "Provide an advanced UI action broker within the mac-vision agent that classifies every proposed UI manipulation as read-only, reversible, or high-impact destructive before execution, with optional user confirmations for high-risk actions."
- **useful because:** Currently, mac-vision runs all actions with maximum access and no gate. Adding classification and selective confirmation would greatly reduce unintended destructive UI manipulations and build owner trust in autonomous UI control.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** milliseconds to sub-second
- **cost:** low additional cost for classification logic
- **security:** The classification system must be robust and transparent. Confirmations must be foolproof and not bypassed. No leakage of pending commands.
- **missing:** UI action classification schema integrated with mac_run_actions and mac_delegate.; User-configurable policy for which actions require confirmation.; Mechanism to hold execution pending confirmation and replay or undo if declined.; Logging of all high-impact action attempts and results.


## What it asked for

_Nothing._
## Its own summary

Established that the mac-vision agent has full accessibility-based UI control capability enabled and permissions granted, but lacks any live task queue or UI snapshot integration today. Proposed several novel capabilities including: a prioritized task list for Mac automation work, live linkage of UI snapshots to workbench context for error recovery, real-time coordination between mac-planner and mac-vision for workflow execution, physical pendant-based user confirmation for high-risk UI actions, detection and mitigation of fallback mouse-click focus theft in UI automation, and a fine-grained UI action broker with classification and selective confirmation to improve owner safety and trust. Each proposal respects the current system state and fills critical capability gaps with clear implementation needs.

**Biggest unknown:** Whether and how UI snapshot and accessibility tree live data integration can be added to enable true resume and error handling in mac-vision's computer use loop, as currently no such routes or tools exist in the system.

