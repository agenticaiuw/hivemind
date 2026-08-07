# Harness derivation — mac-vision — round 54

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a safe, privacy-respecting mac-vision UI automation loop for accessibility-mode computer control without screen capture or focus stealing."
- **useful because:** Currently the mac-vision computer-use loop is disabled due to missing permissions and privacy concerns. Enabling it in an accessibility tier that never steals focus or sends screen capture can unlock powerful automation of GUI tasks that are otherwise impossible or fragile via short scripted actions or APis. This would allow the owner to delegate complex multi-app workflows and repetitive GUI inputs safely and privately.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** sub-second to a few seconds per UI action decision
- **cost:** Low API cost dominated by UI decision model calls; moderate engineering cost to implement gating and permission checking
- **security:** Access to automate UI without stealing focus or screen capture still risks disruption; requires explicit user enabling of Accessibility and Screen Recording permissions; no screen data leaves device without consent; must include undo and confirmation safeguards for destructive actions
- **missing:** Accessibility permission enabling flow for AI Pendant Agent; Screen Recording permission enabling flow; Owner vision upload consent mechanism; Gating and confirmation logic for high-impact UI actions; Detailed allowed action list and limits in accessibility mode


## Changes it proposed to its own stack

### `interaction` — Implement multi-layer gating and user consent dialogs for mac-vision loop activation, including explicit owner prompts to enable Accessibility and Screen Recording permissions, clear privacy consent for screen capture and vision upload, and a live 'pause/stop' button on the pendant during automation loop runs.
- **owner gets:** Owner gains fine-grained control over when the powerful but potentially disruptive mac-vision GUI automation is enabled, improving trust and safety while maintaining privacy.
- effort: Medium engineering effort to create gating UI, consent mechanisms, and pendant controls.  ·  risk: If gating is not clear or too complex, owner might enable it accidentally or not enable at all, missing benefits or creating disruption; mitigated by design iteration and clear feedback.
- cost: Minor backend API cost for state tracking and payer notifications; negligible runtime CPU cost.  ·  latency: Negligible effect on loop latency as gating is mostly frontloaded to activation time.
- security: Reduces risk by ensuring explicit owner control and stopping disruptive automation quickly.
- depends on: Accessibility permission enabling flow; Screen Recording permission enabling flow; Owner vision upload consent mechanism

### `model-routing` — Introduce a specialized model routing layer that selects between local mac_run_actions execution and mac-vision pixel-based UI automation based on task complexity, permission state, and visual grounding needs, with fallback to mac_delegate for ambiguous workflows.
- **owner gets:** This enables optimal use of AI resources and permissions, giving fast, safe command execution for simple actions and only using complex pixel-based UI automation when necessary, improving efficiency, reliability, and user experience.
- effort: Medium engineering and development effort to implement model selection logic and integrate signals about permissions and task type.  ·  risk: Incorrect routing might lead to failed or suboptimal UI actions; mitigated by layered fallback strategies and logs.
- cost: Adds modest runtime routing decision cost; saves cost by not always using expensive vision-based automation.  ·  latency: Potentially reduces perceived latency by avoiding vision analysis when unnecessary.
- security: Improves security by reducing overuse of pixel-level automation; confines high-privilege operations to explicit needs.
- depends on: Visibility of real-time permission states; Definition of task complexity heuristics

### `hardware` — Add a hardware button or touch gesture on the pendant specifically dedicated to emergency stop/pause of ongoing mac-vision UI automation, with visual/audible feedback and secure communication to the Mac agent.
- **owner gets:** Gives the owner immediate, trusted physical control to halt potentially disruptive or mistaken UI automation actions in real time, enhancing safety and trust in mac-vision automation.
- effort: Low to medium hardware and firmware implementation effort and Mac agent protocol integration.  ·  risk: Risk of accidental presses can be mitigated by requiring hold or double press gestures; loss of function if pendant battery dies or is out of range.
- cost: Minor hardware and firmware cost; no major power impact as button is low-energy.  ·  latency: Negligible latency impact; improves safety by enabling fast intervention.
- security: Increases security by providing a physical assertive override of software automation.
- depends on: Pendant firmware update support; Mac agent communication protocol updates

### `memory` — Implement enduring memory storage of user preferences regarding mac-vision loop permissions, gating states, and frequently used or disallowed UI automation actions, with quick recall to reduce redundant prompts.
- **owner gets:** Improves user experience by remembering prior consent decisions and preferred settings, reducing friction and unnecessary prompts while maintaining owner control.
- effort: Medium engineering effort to extend existing context graph or local storage with these new states and preferences.  ·  risk: If memory is corrupted or lost, consent state might be forgotten; mitigate by backup and integrity checks.
- cost: Minimal increase in storage and retrieval cost.  ·  latency: Negligible impact on latency; improves smoothness of user interaction.
- security: Memory must be protected with access controls to prevent leaking owner preferences or spoofing.
- depends on: Context graph storage capabilities; Secure local storage on Mac agent

### `dashboard-ux` — Create a dedicated dashboard panel that shows mac-vision loop status, recent automation action history with undo options, permission state summary, and quick toggles for enabling/disabling the loop and related permissions.
- **owner gets:** Owner can easily monitor, control, and audit mac-vision automation activity and permissions, building trust and enabling quick corrective actions without command-line or config file editing.
- effort: Medium engineering effort for UI design and integration with Mac agent backend.  ·  risk: If UI is cluttered or confusing, owner might misunderstand status or inadvertently change settings; mitigate by user testing and simple design.
- cost: Moderate frontend and backend resource cost for UI and data syncing.  ·  latency: No direct impact on loop latency; improves overall user experience.
- security: Must ensure only authorized user can access and change dashboard settings to prevent misuse.
- depends on: Backend logging and state reporting; Access control for dashboard


## What it asked for

_Nothing._
## Its own summary

Proposed six new capabilities and changes to enable safe, privacy-conscious mac-vision UI automation in accessibility mode. These include permission enabling flows, gating and consent dialogs, a model routing layer for action selection, pendant emergency control hardware, memory of owner preferences, and a dashboard UI for status and control. These address key missing features and risks blocking mac-vision loop activation today and unlock powerful Mac GUI task automation with owner trust and control.

**Biggest unknown:** Exact list and enforcement of allowed UI accessibility actions in accessibility loop mode, and detailed owner interaction flow for gating and emergency stop.

