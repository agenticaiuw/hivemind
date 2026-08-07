# Harness derivation — mac-vision — round 134

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable real-time vision-based Mac UI navigation and interaction via the worn pendant's camera and the Mac-vision agent."
- **useful because:** This would allow the owner to give natural voice or gesture commands and have the AI visually locate and operate UI elements on the Mac screen, enabling truly hands-free computer use with high precision and context awareness.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** realtime
- **latency:** sub-second response to UI changes and commands
- **cost:** moderate API usage dominated by real-time vision processing
- **security:** Camera data is sensitive; all processing should be on-device or end-to-end encrypted; explicit owner consent required for every session; no screen recording without permission.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; real-time UI hierarchy snapshot or event stream; mac-vision artifact supporting pixel-level UI element location

### "A multi-app workflow delegation system that can use vision to understand context and orchestrate complex tasks on the Mac across apps automatically."
- **useful because:** Owners often need to perform complex workflows involving multiple apps that require visual context (for apps without API or scriptable interfaces). This would automate repeated sequences and reduce friction on multitasking.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** minutes for multi-step workflows
- **cost:** higher due to multi-app orchestration and vision analysis
- **security:** Requires storing workflow state and partial screen data temporarily; encryption and permission management critical.
- **missing:** computerUse.loopEnabled permission; visionUploadConsented permission; enhanced mac_delegate tooling; UI event capture hooks

### "A real-time UI element locator and accessibility enhancer that integrates vision and accessibility data to precisely target UI elements on the Mac for assistive interaction."
- **useful because:** Many Mac apps have complex or non-standard UI elements not fully exposed via accessibility APIs. Combining vision with accessibility data would vastly improve accuracy of UI targeting for assistive AI agents like mac-vision, enabling more reliable automation and interaction.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** sub-second to a few seconds
- **cost:** moderate. Vision processing and data fusion are intensive but localized.
- **security:** Vision data is privacy-sensitive, must be processed or encrypted securely; accessibility data permission managed carefully.
- **missing:** visionUploadConsented permission; computerUse.loopEnabled permission; fusion algorithm for vision and accessibility UI element correlation; accessibility event hooks

### "Context-aware adaptive Mac UI assistant that anticipates needed actions by monitoring device status, app usage, and recent owner commands to proactively suggest shortcuts or automate frequent tasks."
- **useful because:** The owner can save time and reduce effort by receiving intelligent suggestions and partial automation in daily computer use, customized by real-time context and learned preferences.
- **path:** mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds to a minute
- **cost:** moderate, mostly model inference and context processing
- **security:** Sensitive usage data; requires encrypted storage and explicit owner control over learning and suggestions.
- **missing:** comprehensive device status and app usage monitoring; integrated context modeling and prediction; permission to monitor usage data


## Changes it proposed to its own stack

### `hardware` — Integrate an on-pendant neural inference accelerator specialized for real-time vision processing to offload the Mac and reduce latency in UI understanding and interaction.
- **owner gets:** Improves responsiveness and privacy by processing pendant camera data locally, reducing data sent to the Mac or cloud, enabling always-on vision-based control without draining the Mac's resources.
- effort: Significant firmware and hardware engineering effort to design, prototype, and integrate accelerator.  ·  risk: Hardware bugs or integration failures could degrade overall pendant function temporarily; recovery via firmware update is possible.
- cost: High initial hardware cost; moderate increase in pendant power draw.  ·  latency: Substantial latency improvement for real-time tasks.
- security: Data privacy improved through local processing; must ensure secure enclave for sensitive data.
- depends on: permissions for visionUploadConsented and computerUse.loopEnabled


## What it asked for

_Nothing._
