# Harness derivation — mac-vision — round 129

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision's computerUse loop with safe, privacy-respecting permissions to allow proactive UI automation on the Mac."
- **useful because:** This capability will make the system uniquely powerful by letting the wearable AI pendant and Mac agent collaboratively automate GUI tasks for apps without disturbing the owner, performing routine tasks, and responding quickly to voice or context cues.
- **path:** pendant → mac-planner → mac-vision → browser-extension
- **model tier:** realtime
- **latency:** 100ms to 1s per discrete-step action
- **cost:** Low to moderate API costs, dominated by context processing; no heavy video or image generation costs.
- **security:** Requires careful handling of accessibility and screen recording permissions. Must respect owner privacy by limiting which apps and UI elements can be automated. Uploading UI snapshots only with explicit consent. Always visible audit log and undo capability.
- **missing:** Trusted macOS Accessibility permission enabled for AI Pendant agent; Screen Recording permission granted to AI Pendant agent; consent UI for vision data upload and usage; Safe typed action broker to classify actions as read-only, reversible, or high-impact mutation; Policy to limit UI automation to approved apps and workflows

### "Create seamless multi-device chore workflows that combine wearable pendant input, Mac GUI automation, and browser extension actions."
- **useful because:** This would let the owner use voice or button on the pendant to trigger complex chore flows that run across apps and devices without manual switching. For example, taking a photo on the pendant, uploading on the Mac, then posting in a browser tab, all coordinated automatically.
- **path:** pendant → mac-vision → browser-extension
- **model tier:** realtime
- **latency:** 1-3 seconds per multi-step chore
- **cost:** Moderate API cost to track multi-device state and coordinate steps; low cost per discrete automation step.
- **security:** Requires secure passing of credentials and task status across devices. Must prevent unintended actions or data leaks. Must require explicit owner trigger for start.
- **missing:** Unified multi-device choreography framework; Multi-step typed action broker across surfaces; Cross-device secure session and state sharing

### "Provide live assistant help via the pendant by real-time synopsis and summarization of currently active Mac screen and browser tabs."
- **useful because:** This capability provides instant contextual help and summary of content found in active Mac applications and browser tabs, accessible via voice from the pendant, without needing manual reading or searching by the owner.
- **path:** pendant → mac-vision → browser-extension
- **model tier:** realtime
- **latency:** 500ms to 2s for summary response
- **cost:** Moderate API cost dominated by text extraction, summarization, and context updates.
- **security:** Requires access to screen content and browser tabs, which must be consented by the owner. Summaries must be ephemeral, no permanent storage without explicit consent.
- **missing:** Real-time screen content extraction with privacy controls; Live sync of browser tab content with summarization; Low-latency summarization model implementation

### "Implement a privacy-first selective UI snapshot and content extraction framework for mac-vision that only captures minimal UI portions necessary for a task with owner-configurable filters and redactions."
- **useful because:** This allows mac-vision to operate safely by reducing sensitive data exposure, enabling owner control over what UI and data are seen by the AI, increasing trust and practical deployment possibilities.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100ms to 500ms per extraction step
- **cost:** Low cost as most computations are local; API cost scales with amount of data extracted.
- **security:** Must strictly enforce owner filters and redactions, ensure no unintended data leakage, and provide audit logs.
- **missing:** Selective UI snapshot APIs; Owner-configurable filters and redaction rules; Local minimal content extraction tools

### "Develop a continuous, adaptive UI and app state monitoring service on mac-vision that learns owner routines and preferences to proactively suggest or trigger relevant actions or reminders without explicit prompting."
- **useful because:** Reduces owner cognitive load and effort by anticipating needs and automating frequent workflows based on learned habits and context.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** background
- **latency:** Near realtime, but emphasis on background adaptation and minimal interruption.
- **cost:** Moderate ongoing cost for state monitoring, learning, and inference.
- **security:** Must respect privacy, avoid unwanted interruptions, and provide easy override or disable options.
- **missing:** Real-time adaptive learning models; Context-sensitive UI and app state extraction; Owner feedback loop mechanisms for adaptation


## Changes it proposed to its own stack

### `hardware` — Add an integrated low-power AI vision co-processor on the wearable pendant capable of pre-processing and extracting semantic UI elements and user interaction context locally, without uploading raw screen pixels to the cloud or Mac.
- **owner gets:** Provides privacy-preserving local UI understanding and context extraction, enabling real-time assistance and automation without exposing private screen content and reducing latency.
- effort: High - requires custom hardware design, firmware, and integration with mac-vision and pendant software stacks.  ·  risk: Complex integration, potential bugs or delays in vision processing; fallback plan is to disable local semantic extraction and rely on current systems.
- cost: Significant hardware cost and power draw increase but justified by privacy and responsiveness benefits.  ·  latency: Low latency as processing is local on pendant.
- security: Improves privacy by limiting data sharing; requires secure firmware and data pipelines.


## What it asked for

_Nothing._
