# Harness derivation — mac-vision — round 122

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a safe, user-consented Mac screen understanding and interaction loop with non-intrusive accessibility-based UI snapshots when pixel capture or full focus is forbidden."
- **useful because:** Allows mac-vision to assist the owner with UI automation and interaction locally on the Mac without disturbing workflow, safeguarding privacy by avoiding screen pixels unless expressly allowed.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** gpt-4.1-mini
- **latency:** interactive, 1–3 seconds response
- **cost:** low API cost, mostly local processing
- **security:** User consent management, strict focus and data access policies to prevent private data leakage
- **missing:** UI snapshot richness documentation; mac-vision loop continuous control policies; owner consent UX

### "Perform multi-application coordinated task workflows on the Mac by seamless data and command sharing between mac-vision, mac-planner, and browser-extension."
- **useful because:** Enables complex workflows that involve multiple apps to be orchestrated efficiently, leveraging the strengths of each surface for planning, browser automation, and UI interaction.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes depending on task complexity
- **cost:** moderate, mostly cloud and local API calls
- **security:** Authorizations for inter-surface data sharing, task goal privacy
- **missing:** Defined inter-surface protocols and data contracts

### "Enable mac-vision to analyze UI context in real-time for adaptive interface control and enhanced automation suggestions."
- **useful because:** Leverages mac-vision's unique local screen and UI knowledge to provide context-aware actions and proactive help based on screen state changes.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** gpt-4.1-mini
- **latency:** interactive, sub-second to a few seconds
- **cost:** low to moderate, mostly local compute
- **security:** Continuous local screen monitoring requires strict user control and opt-in
- **missing:** Reliable real-time UI context extraction methods; User opt-in and control mechanisms

### "Enable the mac-vision loop to take periodic low-impact UI snapshots using Mac Accessibility APIs without any pixel capture or focus stealing, and upload anonymized metadata for centralized context building."
- **useful because:** This allows continual, privacy-conscious understanding of the Mac UI environment to enable context-aware assistance, without disturbing the owner's active work or revealing sensitive screen pixels.
- **path:** mac-vision → faculty-perception → unified
- **model tier:** gpt-4.1-mini
- **latency:** under 5 seconds per update
- **cost:** low, mostly local compute and small metadata upload
- **security:** Strict user consent, metadata anonymization, and access control to prevent privacy leaks
- **missing:** Periodic Accessibility API snapshot scheduler in mac-vision loop; Metadata anonymization and upload pipeline

### "Allow mac-vision to assist in real-time multi-modal diagnostics on Mac by combining accessibility UI states, system status, and logs for proactive troubleshooting."
- **useful because:** This provides advanced help features that can detect and suggest fixes for problems across apps and system layers by leveraging multiple data sources in real time.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** instant to few seconds
- **cost:** moderate cloud and local compute
- **security:** Sensitive logs and system states require controlled access and user approval
- **missing:** Unified diagnostic data model and event stream merging; Permission to access logs and system states in real time

### "Allow mac-vision to generate spoken summaries of complex Mac and browser UI states on demand, helping the owner understand current tasks without needing screen viewing."
- **useful because:** Improves accessibility and owner situational awareness by converting detailed UI state information into concise voice briefings, useful during multitasking or screen unavailability.
- **path:** mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** a few seconds
- **cost:** low, mostly local compute and relay API cost
- **security:** UI state data privacy; controlled local processing and transmission
- **missing:** Text-to-speech integration with relay; UI state summarization models tuned for Mac and browser UIs

### "Enable mac-vision to gesture and control the Mac UI in an augmented reality (AR) overlay visible only to the owner through wearable AR glasses, creating a private interactive control layer."
- **useful because:** This would empower the owner to perform complex UI manipulations without disturbing others or exposing screen contents, using natural hand gestures with immediate visual feedback in an AR context.
- **path:** mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** sub-second to 2 seconds
- **cost:** moderate, requiring local fast processing and relay integration
- **security:** Strict AR data isolation and secure gesture processing to prevent spoofing or leakage
- **missing:** AR glasses integration; AR overlay UI framework; gesture recognition tied to mac-vision control

### "Allow mac-vision to dynamically modify Mac UI themes, layouts, and accessibility settings based on user context and preferences detected by wearable sensors and environment conditions."
- **useful because:** Adaptive UI personalization would reduce eye strain, enhance usability, and optimize focus by tuning visual appearance and interaction modes on the fly.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** seconds
- **cost:** low to moderate compute and local system API usage
- **security:** Permission gating for system UI modifications; privacy of sensor data
- **missing:** Wearable sensor data integration; System UI settings API for dynamic changes

### "Provide mac-vision with cross-application AI document summarization that visually highlights key insights and actions within native Mac apps like Preview, TextEdit, and Mail."
- **useful because:** This allows the owner to quickly understand large documents without leaving their current app or workflow, improving productivity and focus.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** a few seconds
- **cost:** moderate, requiring local AI inference and app UI integration
- **security:** Document content privacy; local processing preferred
- **missing:** Native app UI annotation APIs; Document content extraction and summarization integration

### "Enable mac-vision to generate interactive visual macros for repetitive complex UI workflows on the Mac, allowing the owner to record, edit, and replay UI interaction sequences with adaptation to UI changes."
- **useful because:** This empowers the owner to automate tedious tasks without coding, enhancing productivity and integrating AI-driven error recovery and adaptation.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds for recording/editing; realtime for replay
- **cost:** moderate, requiring local UI state modeling and storage
- **security:** Recorded macros privacy; safe operation to prevent unintended destructive actions
- **missing:** UI interaction recording and replay API; UI change detection and macro adaptation


## Changes it proposed to its own stack

### `interaction` — Enable a lightweight accessibility-driven UI interaction mode for mac-vision that runs continuously without taking keyboard, mouse, or screen focus. This mode takes incremental UI snapshots and operates asynchronously with the owner present, preserving privacy and comfort.
- **owner gets:** Allows the system to assist with UI automation and contextual actions on demand while the user actively works, without disruption or privacy concerns related to pixel capture.
- effort: Moderate engineering to build incremental UI snapshotter, refine non-intrusive interaction model, and UX for session control and consent.  ·  risk: Potential privacy leakage if strict controls and anonymization are not enforced; user discomfort if interaction is intrusive; can be mitigated by opt-in, observable mode, and immediate off switch.
- cost: Low ongoing compute and data bandwidth. No large storage or API cost.  ·  latency: Sub-second to few seconds latency for UI state updates.
- security: Requires strict sandboxing and permission gating to avoid leak or misuse of UI data.
- depends on: computerUse.loopEnabled; visionUploadConsented; ui_hierarchy_snapshot

### `hardware` — Add a dedicated hardware security module on the pendant to securely store user consent tokens and biometric confirmations for sensitive Mac control and screen reading, minimizing risk of unauthorized access and enabling safer mac-vision loop activation.
- **owner gets:** Provides a trusted and user-friendly hardware root of trust for privacy-sensitive features, allowing seamless but secure activation of mac-vision capabilities that interact deeply with user's Mac UI.
- effort: High hardware and firmware development effort plus integration with current pendant MCU environment.  ·  risk: Potential hardware bugs or defects causing lockout or failure to authorize; mitigated by fallback software workflows.
- cost: Moderate hardware component cost and minor increase in pendant power draw.  ·  latency: Negligible on user experience, as consent is asynchronous.
- security: Significantly improves security posture by isolating consent and biometric data.
- depends on: pendant secure element design; firmware updates

### `model-routing` — Route specialized visual and UI context understanding tasks from mac-planner to mac-vision to leverage its local accessibility snapshot capabilities for accurate UI state extraction and action planning.
- **owner gets:** Combines strengths of mac-vision's local UI access with mac-planner's higher-level reasoning for more precise and efficient multi-application task handling on the Mac.
- effort: Moderate engineering to define APIs and task delegation protocols between mac-planner and mac-vision models.  ·  risk: Potential delay or failure in inter-model communication; falls back to individual operation.
- cost: Minimal additional API calls; mostly software design.  ·  latency: Small increase in communication latency offset by higher task success rate.
- security: Requires careful permission management for UI data shared between models.
- depends on: ui_hierarchy_snapshot; mac_run_actions; mac_delegate


## What it asked for

_Nothing._
