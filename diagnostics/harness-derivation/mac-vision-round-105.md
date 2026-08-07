# Harness derivation — mac-vision — round 105

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, real-time computer use loop on Mac to perform multi-step UI workflows with fallback between accessibility control and pixel interaction"
- **useful because:** Owner could get seamless computer control on their Mac for tasks involving complex UI workflows, including apps with no API, inaccessible system dialogs, and dynamic browser content; this bridges the gap between typed actions and manual UI interaction for fluent, adaptive automation and voice control.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-perception → faculty-action
- **model tier:** gpt-4.1-mini for mac-vision loop, gpt-5.6-luna for coordination surfaces to plan and supervise
- **latency:** sub-second local UI reads and action executions, with asynchronous multi-step coordination over seconds to minutes for complex workflows
- **cost:** main cost in repeated UI snapshot processing and verification; low cost for typed action dispatch; background relay for coordination
- **security:** Require strict typed action policy with irreversible action confirmation; privacy sensitive screen data handled only locally with no upload unless explicitly consented; fallback to accessibility controls ensuring no pixel capturing where disallowed
- **missing:** Policy and permission model for computerUse.loopEnabled and visionUploadConsented; Typed action classification and reversible action policy enforcement; Robust local pixel + accessibility fallback control combined in one loop; Inter-surface protocol for multi-step UI task delegation and recovery

### "Context-aware mixed modal UI interaction capability combining accessibility and pixel data for mac-vision loop"
- **useful because:** Some Mac apps and system controls expose partial accessibility APIs but also require pixel-level interaction for full control, e.g., canvas apps, terminals, or legacy apps. A combined mode using accessibility where possible, falling back to pixel-based actions when necessary, would make the AI much more capable and resilient.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini for mac-vision loop, gpt-5.6-luna for planning and fallback coordination
- **latency:** Mixed fast accessibility interactions and slightly slower pixel fallback; under 2 seconds typical
- **cost:** Higher than pure accessibility, but avoids full manual pixel usage; trades off in fewer failed UI interactions and retries
- **security:** Pixel data exposure requires visionUploadConsented; fallbacks use accessibility only to minimize pixel use; needs careful permission gating and local-only pixel data persistence
- **missing:** Fine-grained coordination of fallback between accessibility and pixel modes; Heuristics to detect accessibility failure and trigger pixel fallback; Unified UI model for both interaction modes


## Changes it proposed to its own stack

### `interaction` — Implement an integrated typed action broker and policy enforcer for mac-vision loop to classify every proposed action as read-only, reversible mutation, or high-impact irreversible mutation; require one-use owner confirmation for irreversible types; interlock with typed tools get_mac_status, mac_run_actions, browser_run_actions, and mac_delegate for multi-step workflows.
- **owner gets:** This change enables safe and auditable control of the Mac from the AI loop, preventing accidental destructive actions while allowing fluid automated control for complex tasks with confirmation gating only where necessary.
- effort: Medium engineering effort, mainly in policy development, UI for confirmation, and integration with existing typed action endpoints.  ·  risk: Incorrect classification risks owner data or system state; mitigated by fallback confirmation. Policy UI UX must not block or annoy for read-only and reversible actions.
- cost: Low ongoing API cost, some initial dev cost; no hardware impact.  ·  latency: Minimal latency added only during confirmation steps.
- security: Improves security by limiting destructive commands and auditing; requires secure confirmation mechanism.
- depends on: Fully enabled computerUse.loopEnabled and visionUploadConsented to capture UI context safely

### `hardware` — Add a local dedicated AI coprocessor in the MacBook hardware to run mac-vision's pixel-level computer use loop offline securely, avoiding any necessity to upload screen pixels or sensitive UI data to external servers.
- **owner gets:** This coprocessor improves privacy and latency for real-time UI understanding and control, enabling the mac-vision agent to operate with full vision support while keeping all sensitive screen content local and unexposed to network risks.
- effort: High hardware and firmware development effort, requires macOS support for offloading UI capture and AI inference tasks.  ·  risk: Delayed hardware availability; need for driver and OS integration; fallback needed for non-supported hardware.
- cost: Significant initial hardware and development costs; reduces cloud processing cost for pixel analysis.  ·  latency: Significantly lowers latency for vision processing on the Mac device.
- security: Strongly increases security and privacy by localizing pixel data and AI inference.
- depends on: Fully enabled computerUse.loopEnabled and visionUploadConsented to access UI and pixel data safely


## What it asked for

_Nothing._
