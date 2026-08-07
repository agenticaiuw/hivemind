# Harness derivation — mac-vision — round 113

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a permission gating interface and education workflow for the owner to safely grant Accessibility and Screen Recording for AI Pendant Agent"
- **useful because:** The owner would be guided step-by-step to safely enable the required permissions for pixel-level UI automation, understanding the risks and benefits, increasing trust and likelihood of safe activation
- **path:** relay-realtime → mac-planner → faculty-judgement → mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** Instant to seconds, as it is interactive and conversational
- **cost:** Minimal AI and compute costs, mostly UI and local interaction
- **security:** Must prevent accidental permission grants and ensure owner explicitly confirms actions before enabling key permissions
- **missing:** Interactive UI workflow for permissions enabling; Explanatory content educating owner on risks and benefits; Integration with OS system prompts for permissions; Feedback and rollback mechanisms

### "Provide robust visual error detection and recovery for mac-vision UI automation loop to handle unexpected app states or UI changes"
- **useful because:** Increases reliability of automated UI interactions by detecting when UI is not as expected and taking corrective actions or requesting human input, reducing failures and frustration
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for vision, gpt-5.6-luna for reasoning and judgement
- **latency:** 1-3 seconds to analyze and decide on recovery steps
- **cost:** Moderate due to image analysis and reasoning
- **security:** Ensures no harmful actions are taken by requiring fallback to owner input or safe defaults
- **missing:** Real-time visual anomaly detection models; Fallback and human-in-the-loop mechanisms for recovery; Integration with computer use loop for state validation

### "Allow the AI Pendant to perform seamless, contextual multi-application workflows by combining browser automation, local Mac UI automation, and cloud relay coordination"
- **useful because:** The owner can delegate sophisticated tasks that span multiple apps and interfaces without manual switching, improving productivity and convenience
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna orchestrating gpt-4.1-mini and gpt-5.6-luna specialized skills
- **latency:** Seconds-level coordination allowing natural conversational pacing
- **cost:** Moderate AI compute costs, some network and local UI automation overhead
- **security:** Requires careful inter-surface access controls and auditing to prevent unintended data leaks or actions
- **missing:** Advanced multi-agent orchestration protocols; Robust context synchronization across surfaces; Enhanced typed action brokering to handle multi-app workflows


## Changes it proposed to its own stack

### `integration` — Create an automated multi-tier permission and safety gating framework around mac-vision UI loop to allow staged enabling of pixel and accessibility access, with owner prompts and safeguards
- **owner gets:** Allows the owner to gradually enable powerful mac-vision UI automation safely by clearly communicating risks and allowing staged consent, preventing accidental or harmful actions
- effort: Medium, involves UI design, OS integration hooks, and orchestration logic  ·  risk: Owner confusion or accidental enabling mitigated by clear explanation, explicit prompts and rollback options
- cost: Low AI compute cost, moderate local development effort  ·  latency: Minimal impact on reaction time
- security: Improves security by preventing premature or unsafe UI automation activation
- depends on: Accessibility permission granted and trusted; Screen Recording permission granted and visionUploadConsented; User education and permissions workflow

### `hardware` — Add a local secure enclave chip to the MacBook to handle sensitive screen recording and input automation securely with owner-overwatch and encrypted telemetry
- **owner gets:** Enhances privacy and security of pixel capture and UI control by processing all sensitive actions within a hardware trust boundary, preventing leaks and unauthorized control
- effort: High, requires hardware design and integration with existing OS and agent framework  ·  risk: Hardware design flaws or integration bugs could reduce security; requires rigorous testing and verification
- cost: Significant hardware and development cost  ·  latency: Improves latency by localizing critical operations
- security: Major improvement in security and privacy
- depends on: mac-vision pixel UI control enabled; Software integration with agent stack

### `model-routing` — Implement real-time model tier routing to dynamically assign tasks between low-latency vision models and higher-tier reasoning/planning models for efficient UI automation
- **owner gets:** Improves responsiveness and accuracy of mac-vision UI automation by using lightweight models for quick decisions and powerful models for complex reasoning only when needed
- effort: Medium, requires model orchestration framework enhancements and routing logic  ·  risk: Model routing failures could cause slowdowns or incorrect actions, mitigated by fallback mechanisms
- cost: Optimizes AI compute cost by using appropriate models per task complexity  ·  latency: Improves latency overall by reducing over-reliance on heavyweight models
- security: No direct impact but supports safer operation through better model choice
- depends on: Model tier classification; mac-vision UI automation tasks

### `interaction` — Design a continuous learning and feedback loop for mac-vision that involves the owner to correct mistakes and improve UI automation accuracy over time
- **owner gets:** Allows the AI to adapt to the owner's specific workflows and preferences, reducing errors and increasing trust and usefulness
- effort: Medium, involves UI design, telemetry capture, and feedback mechanisms  ·  risk: Potential privacy concerns if feedback data is not properly secured and anonymized
- cost: Moderate AI compute cost for continuous model fine-tuning and evaluation  ·  latency: No direct impact on latency
- security: Requires secure handling of feedback data to protect owner privacy
- depends on: mac-vision loop enabled; Telemetry and error reporting infrastructure; Owner permission to provide usage feedback


## What it asked for

### `c11-oz6a` (context) — ui_hierarchy_snapshot
- why: To understand the current UI structure for accessibility-level computer use without needing pixel screenshots, enabling me to reason about possible actions safely.
- would change: It would allow me to simulate and plan UI actions and clicks without requiring the full pixel screenshot access that is currently not consented to, making the loop partially useful and less intrusive.

