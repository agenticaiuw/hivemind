# Harness derivation — mac-vision — round 123

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make mac-vision a safe, privacy-respecting computer-use loop that can visually understand the Mac desktop and assist with GUI tasks."
- **useful because:** It would allow visual understanding and proactive assistance for complex tasks that do not have an API, improving fluidity and efficiency.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini
- **latency:** real-time or near real-time for interactive control
- **cost:** moderate per invocation dominated by vision and state processing
- **security:** Requires owner consent for screenshots and UI data for privacy, local sandbox for image processing without network leaks.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; UI hierarchy snapshots; image processing pipeline integrated with Mac events

### "Combine mac-vision computer use loop with live Mac status (battery, wifi, volume, front app) to preemptively adjust system settings or apps."
- **useful because:** This integrated awareness would allow the Mac to proactively help maintain comfort and productivity, e.g., lowering volume when on a call, or suggesting app switches.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** seconds
- **cost:** low to moderate per invocation
- **security:** Local state only, no remote transmission without explicit consent.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission

### "Enable multi-surface multi-app workflows that use mac-vision's visual input, browser-extension's browser control, and mac-planner's overview for complex tasks."
- **useful because:** Certain workflows, such as research or content creation, need seamless interaction across apps and browsers, coordinated visually and contextually.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** minutes for complex workflows
- **cost:** moderate due to multi-surface coordination
- **security:** Data shared only within trusted local surfaces, user control and audit logs required.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; cross-surface context synchronization

### "Enable mac-vision to visually monitor error messages, dialogs, or warnings in the Mac UI and proactively alert the owner or take corrective action."
- **useful because:** This would improve the owner's situational awareness and reduce frustration by handling or highlighting issues promptly through visual detection beyond system APIs.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** seconds
- **cost:** low to moderate depending on visual frequency and complexity
- **security:** Only local vision data is processed; no external sharing without explicit consent; alerting is optional and under owner control.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; UI text recognition feed integrated with Mac event streams

### "Allow mac-vision to autonomously navigate and execute repetitive but complex GUI sequences (e.g., form filling, dialog handling) using visual input and recorded UI steps."
- **useful because:** Automating repetitive manual UI tasks saves time and mental effort for the owner, especially when no API exists for these workflows.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** asynchronous, up to minutes for step sequences
- **cost:** moderate depending on frequency and sequence length
- **security:** Requires strict local sandboxing for vision data and stored sequences; no external sharing without consent.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; persistent UI interaction recording and replay infrastructure

### "Enable mac-vision to monitor system focus changes and offer context-aware suggestions and shortcuts visually based on the current app and window contents."
- **useful because:** This would provide owners quick access to relevant commands and automate common next steps based on visual context, enhancing productivity and reducing friction.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** seconds
- **cost:** low to moderate depending on frequency of context changes
- **security:** This involves only local context data; no external sharing without owner control.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; real-time UI context analysis pipeline

### "Enable mac-vision to autonomously and privately run a full computer use loop on the Mac, including low-latency pixel-based vision, real mouse and keyboard control, and screenshot analysis with local-only processing."
- **useful because:** This would unlock true visual navigation and control of the Mac desktop and apps, enabling complex multi-step GUI workflows that no API can reach and proactive assistance with visual cues.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini
- **latency:** real-time or near real-time interaction
- **cost:** moderate due to vision processing and input output latency
- **security:** Requires strict local processing of vision data with no external upload by default, owner control of permissions and data sharing, and fail safes to avoid unintended input.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; local vision processing pipeline; local screenshot storage and ephemeral analysis; hardware support for secure input control

### "Provide a persistent, encrypted local store on the pendant or Mac for mac-vision to record and replay complex UI interaction sequences visually, including timing and error handling."
- **useful because:** Owners could automate and replay repetitive complex GUI workflows without exposing sensitive data externally, increasing productivity and reducing manual error.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** asynchronous; sequences replayed as needed
- **cost:** low to moderate depending on sequence complexity and storage size
- **security:** Store must be encrypted and only locally accessible; data must not leak externally; owner must have full control over sequence management.
- **missing:** local persistent encrypted storage on pendant or Mac; UI interaction recording and replay infrastructure; integration with vision loop


## Changes it proposed to its own stack

### `interaction` — Add fine-grained permission controls and owner approval workflows to safely enable computerUse.loopEnabled and visionUploadConsented for mac-vision, with clear UI explanations and emergency abort options.
- **owner gets:** This would unblock the powerful visual computer control loop while maintaining transparency, control, and safety for the owner, addressing privacy and security concerns realistically.
- effort: Moderate engineering and UX effort to add permission dialogs, audit logs, and safe mode recovery.  ·  risk: Incorrect permission handling might expose privacy; mitigations include thorough testing, explicit user dialogs, fail safes, and escalation paths.
- cost: Minimal API cost; mostly engineering time.  ·  latency: No runtime latency impact after enabling.
- security: Significant positive impact by improving trust and consent.

### `hardware` — Add hardware-level secure input and screenshot control features to the pendant and Mac bridge chips, enabling mac-vision to run an effective and safe computerUse loop with local vision processing, input injection, and screen capture under strict owner control.
- **owner gets:** This hardware support would provide secure, low-latency, and tamper-resistant capabilities for visual computer control on the Mac, improving responsiveness and privacy beyond software alone.
- effort: Significant; requires hardware firmware development and testing.  ·  risk: Hardware bugs or vulnerabilities could compromise privacy or input security; mitigations include review, secure design, and recovery modes.
- cost: Medium hardware development cost and marginal power draw increase.  ·  latency: Improves latency by offloading critical tasks locally.
- security: Enhances security with dedicated hardware protections.
- depends on: computerUse.loopEnabled permission; visionUploadConsented permission


## What it asked for

_Nothing._
