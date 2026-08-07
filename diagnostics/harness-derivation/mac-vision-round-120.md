# Harness derivation — mac-vision — round 120

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Automatically detect when a Mac UI element changes context or becomes unreliable for mac-vision automation, and gracefully switch to alternative workflows or ask for owner confirmation to proceed."
- **useful because:** This feature would make mac-vision's automation more resilient and trustworthy by avoiding broken or dangerous interactions caused by UI changes, preventing errors or data loss.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Realtime GPT-4.1 mini for detection, GPT-5.6 layers for planning fallback strategies.
- **latency:** Near real-time detection desirable, with short recovery time for failover.
- **cost:** Moderate, mostly model inference and tracking overhead.
- **security:** Failsafe behavior avoids unsafe actions; transparent prompts and audit logs ensure owner control; no new data exposure beyond existing.
- **missing:** UI element change detection capabilities integrated with mac-vision loop.; Fallback workflow management protocols for automation continuity.; Owner confirmation interaction protocols for exception handling.


## Changes it proposed to its own stack

### `hardware` — Add dedicated hardware-grade secure video capture with local encryption on the Mac to allow real-time pixel-level UI state streaming to mac-vision without exposing raw screenshots to other apps or stores.
- **owner gets:** The owner gains full visual automation of Mac tasks with strong privacy, enabling new kinds of AI-assisted workflows that cannot be done with current APIs or accessibility tools alone, while protecting sensitive screen data.
- effort: High; requires low-level operating system and hardware integration, secure enclave use, and dedicated silicon or GPU support.  ·  risk: Increased attack surface for screen data capture; damage mitigated by hardware security and strict access control; fails safe by disabling capture if permissions or consent are revoked.
- cost: Significant hardware development and integration cost, plus modest power usage increase during active capture.  ·  latency: Low latency streaming supports real-time UI interactions as required by mac-vision loop.
- security: High security demands; requires multi-layer encryption, secure enclave disambiguation, and user consent enforcement.
- depends on: system-level privacy policy enhancements; User consent management for vision data; mac-vision software supporting the new video feed

### `integration` — Implement a guided owner consent workflow integrated between the mac-planner, pendant UI, and mac-vision to obtain and revoke visionUploadConsented status with full transparency and control over privacy and data use.
- **owner gets:** Provides clear, user-friendly control over the sensitive permission to capture and upload mac-vision screenshots, enabling safe use of the powerful automation capabilities while respecting privacy.
- effort: Medium; requires UI design across devices, software integration, audit logs, and a standardized consent protocol implemented in the agent and pendant software.  ·  risk: If consent controls are unclear or buggy, the owner may accidentally overshare sensitive data or disable useful functions; mitigated by iterative testing and user feedback.
- cost: Minimal software development cost, no hardware changes.  ·  latency: None; consent workflow happens asynchronously.
- security: Increased privacy protection; audit trails reduce risk of misuse or unintentional disclosure.
- depends on: mac-vision enabled with appropriate permissions; pendant UI capable of displaying clear consent dialogs; agent layers able to track and enforce consent state


## What it asked for

_Nothing._
