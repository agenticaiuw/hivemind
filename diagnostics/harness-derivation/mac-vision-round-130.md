# Harness derivation — mac-vision — round 130

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a safe typed-action controlled computer use loop on the Mac that can interact with apps, UI controls, and desktop to fulfill goals reliably and reversibly."
- **useful because:** This lets the system become a full personal AI assistant that can operate the Mac autonomously on behalf of the owner with observability and fallback safety, not just read status or run short scripts.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** real-time conversation scale, <500ms
- **cost:** low per invocation, dominated by typed action classification and scheduling
- **security:** Requires careful typed action enforcement to prevent destructive or blind actions. Data stays local unless owner consents. Confirmation gating recommended for high-impact actions.
- **missing:** computerUse.loopEnabled permission; full accessibility and screen recording permission; visionUploadConsented

### "Coordinated multi-surface complex workflow orchestration that combines mac_delegate for Mac desktop, browser_run_actions for browser tasks, and relay-realtime for voice commands through the wearable pendant."
- **useful because:** Allows the owner to speak complex goals that span many apps and surfaces, letting the system decide where to act and coordinate action steps to fullfill high-level ambitions.
- **path:** mac-planner → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes depending on workflow complexity
- **cost:** medium, depends on orchestration complexity and surface APIs invoked
- **security:** Limits to authorized multi-step goals only. Logging and user overriding essential to prevent misuse or runaway workflows.
- **missing:** authorization for multi-step delegation; context snapshots from all surfaces

### "Prompt the owner for vision data upload consent and enable UI hierarchy snapshots for better context understanding without screen recording permission."
- **useful because:** Enables better computer vision understanding and UI context without intrusive screen recording, yielding better accuracy with fewer privacy concerns.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** seconds
- **cost:** very low
- **security:** Strictly opt-in for vision data upload. Data encrypted and processed locally when possible. UI snapshots anonymized and sanitized.
- **missing:** visionUploadConsented; full accessibility permissions

### "Allow the Mac vision loop to autonomously observe and interpret the Mac desktop UI via pixel vision, integrating typed and reversible actions, enabling natural voice-driven control of desktop apps beyond API-level commands."
- **useful because:** This would unlock truly fluid and powerful personal assistant capabilities for the owner, bridging natural language with visual context for actions impossible through APIs alone.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** real-time, sub-second
- **cost:** moderate per invocation due to vision analysis
- **security:** Requires consented vision data upload and tight typed safety enforcement to avoid destructive actions.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented; full accessibility permissions; screen recording permissions

### "Provide a secure cross-surface multi-step workflow orchestrator that coordinates mac_delegate for complex desktop tasks, browser_run_actions for web tasks, and relay-realtime for voice command input with continuous state tracking and owner override."
- **useful because:** This would let the owner delegate intricate workflows spanning multiple applications and platforms with a single spoken or typed goal, greatly enhancing productivity.
- **path:** mac-planner → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes based on complexity
- **cost:** medium, dominated by coordination and state management
- **security:** Must include thorough audit logging, owner approval gates, and safeguards against runaway workflows.
- **missing:** authorization for multi-step delegation; context snapshots from all surfaces to maintain accurate state


## Changes it proposed to its own stack

### `interaction` — Implement an owner-controlled vision and UI data consent framework that dynamically adjusts which vision data (screenshots, UI hierarchy) can be collected and processed, balancing privacy with capability.
- **owner gets:** Gives the owner control over what visual and UI data is shared, enabling capabilities to improve when allowed but protecting privacy firmly when not.
- effort: Medium, involves UI, security design, and system integration.  ·  risk: Misconfiguration could lead to over-sharing or under-enabling features, recovered by explicit consent reset dialogs.
- cost: Low  ·  latency: Minimal
- security: Improves security by explicit consent controls.


## What it asked for

_Nothing._
