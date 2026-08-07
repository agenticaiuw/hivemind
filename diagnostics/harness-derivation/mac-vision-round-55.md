# Harness derivation — mac-vision — round 55

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure co-processor in the MacBook hardware that captures, encrypts, and streams low-latency, high-resolution UI pixel data and accessibility info to the AI system without exposing raw screen data directly to any non-owner agent or user-space process.
- **owner gets:** This change enables privacy-preserving real-time visual UI feedback for mac-vision to safely perform pixel-based UI interactions, even offline and in fully trusted sessions, enhancing mac autonomy without compromising owner data security.
- effort: Significant hardware and firmware design and integration effort plus coordination with OS security model.  ·  risk: Potential hardware bugs or side-channel leaks; mitigated by strong encryption, access control, and audit logging.
- cost: Moderate hardware cost increase; negligible power draw impact if efficient design realized.  ·  latency: Minimal added latency due to dedicated hardware capture and streaming pipeline.
- security: Improved owner data security by avoiding exposing raw screen captures broadly; requires strong key management.
- depends on: OS support for co-processor access control; AI system software to decode and use encrypted stream; mac-vision loop enabled with permissions

### `model-routing` — Implement an advanced model-routing and orchestration layer to dynamically allocate tasks between mac-vision, mac-planner, faculty-perception, faculty-judgement, and relay-realtime for efficient, context-aware, multi-modal decision making and execution.
- **owner gets:** This layering allows each specialized agent to contribute optimally, enabling mac-vision to focus on pixel-level UI decisions while other agents handle planning, perception, judgement, and voice interaction, resulting in seamless, intelligent Mac control.
- effort: Medium to high engineering effort to develop robust distributed decision protocols, context sharing, and fallbacks.  ·  risk: Coordination bugs or latency spikes affecting responsiveness; mitigated by extensive testing and fallback strategies.
- cost: API and compute costs increased moderately due to multiple model invocations and communication.  ·  latency: Initial latency might increase but overall interaction flows should improve responsiveness.
- security: Requires secure, authenticated inter-agent communication.
- depends on: Secure inter-agent communication layer; Baseline permissions for UI and vision context

### `integration` — Create a unified security and permissions framework across Mac OS, the AI Pendant, and backend services that enforces session-level access to Accessibility and Screen Recording permissions with user-visible prompts, audit trails, and fine-grained revocation.
- **owner gets:** This framework would increase owner trust and safety by ensuring all UI control actions, especially destructive or privacy-sensitive ones, require explicit real-time owner consent and leave a verifiable audit trail, meeting the safety policy requirements.
- effort: Moderate engineering effort involving OS extension, pendant firmware, and backend policy enforcement changes.  ·  risk: Potential user friction if prompts are too frequent, mitigated by smart grouping and predictions.
- cost: Minimal to moderate backend and pendant firmware update costs.  ·  latency: Negligible.
- security: Significant improvement in owner security and control over AI interactions.
- depends on: OS-level permission extension support; Pendant firmware and backend support for audit and prompts

### `dashboard-ux` — Design a Mac AI control dashboard UI that visualizes the state of mac-vision automation, pending UI actions, confirmation requests, and action receipts, allowing the owner to review, modify, undo, and approve automated UI operations.
- **owner gets:** This dashboard would offer transparency, control, and confidence to the owner by making the autonomous UI manipulations visible, explainable, and interceptable, aligned with the safety policy for reversible and safe UI automation.
- effort: Moderate UI/UX design and engineering effort involving the Mac app and web dashboard integration.  ·  risk: Low risk; mainly design and usability challenges.
- cost: Minimal hardware impact, moderate backend and UI development cost.  ·  latency: None.
- security: Increased security by providing owner oversight and control.
- depends on: Backend to track and store action receipts; UI automation loop enabled


## What it asked for

_Nothing._
