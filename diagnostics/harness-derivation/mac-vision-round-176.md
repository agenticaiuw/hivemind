# Harness derivation — mac-vision — round 176

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable and use mac-vision's accessibility-tree computer control loop with full macOS Accessibility permission granted for AI Pendant Agent binary."
- **useful because:** This unlocks mac-vision's ability to read and interact with the Mac UI in a fine-grained way without screen recording or pixel capture, enabling rapid, safe, and reversible control of computer applications through the owned pendant interface. It avoids focus stealing or keyboard/mouse jank and scales better than raw pixel methods.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** real-time, < 1 second
- **cost:** Moderate, mostly LLM inference for accessibility tree parsing and action planning.
- **security:** Requires owner explicit macOS Accessibility grant; all mouse and keyboard actions are reversible or require confirmation; no pixel capture; no focus theft. Sensitive UI data never leaves local device unless permitted by visionUploadConsent.
- **missing:** owner explicit macOS Accessibility permission grant for AI Pendant Agent binary

### "A prioritized, current goal/task store on the Mac accessible via API to all local agents and surfaces, where the owner and agents can add, rank, mark done, and set dependencies on tasks/goals."
- **useful because:** Today, the system lacks a durable, cross-surface prioritized goal store. Having one would enable mac-vision and other agents to pick concrete user goals to advance with coordinated computer and voice actions, improving autonomy and responsiveness.
- **path:** mac-planner → mac-vision → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** background, seconds
- **cost:** Low per call, mostly local datastore and small LLM summarization or ranking.
- **security:** Requires user trust for task content and metadata. Data never leaves local device without permission.
- **missing:** New persistent goal/task datastore and API routes; UI for goal management; Goal priority model

### "Enable mac-vision to collaborate with browser-extension to visually verify and confirm multi-step web workflows initiated by voice commands before execution."
- **useful because:** This leverages the unique strengths of mac-vision's UI accessibility reading and browser-extension's direct browser control to achieve safer, reliable, and containable web automation workflows spanning voice and GUI interaction.
- **path:** mac-vision → browser-extension → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 1-3 seconds
- **cost:** Moderate to high due to coordination and UI reading steps.
- **security:** Requires approval for browser control and macOS accessibility permissions. Data exchange limited to workflow state and UI metadata.
- **missing:** Inter-agent communication protocols for real-time collaboration; UI event confirmation protocols; Browser extension control telemetry durability

### "Context-aware pendant button press triggers to launch mac-vision UI workflows tailored to the active app and user intent, with fallback to voice initiation."
- **useful because:** This would maximize the effectiveness of the single pendant button by making actions adaptive to context (active app, current goal). It reduces user friction, error, and cognitive load by launching exactly the needed interaction without manual app switching or commands.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** <1 second
- **cost:** Low, mostly local context matching and command dispatch.
- **security:** Requires trust in context data and correct user intent parsing; button events are physical triggers only.
- **missing:** Real-time context inference system; Routine triggering and mapping system

### "Enable the pendant's single physical button to trigger multi-modal real-time confirmation workflows: combining button presses, voice commands, and live mac-vision UI feedback to safely approve or reject sensitive computer actions."
- **useful because:** This creates a powerful, safe, and intuitive physical input mechanism to confirm or cancel complex tasks or transactions without requiring multiple buttons or complex gestures, mitigating the current gesture budget limitation.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** sub-second to seconds
- **cost:** Moderate due to multi-modal coordination and real-time UI reading
- **security:** Requires strict owner control and consent on what can be confirmed or cancelled; only local UI state is read; voice and button inputs are trusted with physical presence constraints.
- **missing:** Complex event state machine for button + voice + UI feedback fusion; macOS Accessibility permission for real-time UI reading

### "A persistent, encrypted, cross-device contextual memory and task graph that can incorporate signals from mac-vision, voice, browser, and calendar, accessible for planning and prioritization across all agent surfaces."
- **useful because:** The owner currently lacks any durable cross-device memory that can unify goals, tasks, context, and observations from different inputs, enabling agents to work consistently and predictably over time.
- **path:** mac-planner → mac-vision → relay-realtime → browser-extension → unified
- **model tier:** gpt-5.6-luna
- **latency:** background, seconds
- **cost:** Moderate storage and compute; mostly on Mac and relay; seamless syncing with encryption.
- **security:** Private owner data requires strong encryption in transit and at rest; strict owner consent required for syncing and sharing.
- **missing:** New encrypted cross-device memory infrastructure and sync protocols; Unified API for multi-agent memory read/write


## Changes it proposed to its own stack

### `hardware` — Add a second physical user button on the pendant hardware for explicit secondary actions, gesture confirmations, or modal switching to expand input vocabulary beyond currently single-button primary voice control.
- **owner gets:** Having a second dedicated button unlocks many patented interaction modes without delaying primary button responsiveness, enabling more nuanced control and safer multi-step confirmation flows on the pendant.
- effort: Medium: mechanical redesign, firmware update for button debounce, integration with existing button event queue.  ·  risk: Minimal risk; hardware change may require new enclosure and manufacturing run. Software changes are backward-compatible.
- cost: Low incremental BOM cost; marginal power impact negligible.  ·  latency: None for main interaction paths.
- security: No new attack surface; physical button input as today.

### `hardware` — Redesign the pendant hardware to include a capacitive touch and gesture sensor panel on the device surface to vastly expand input vocabulary beyond the single mechanical button with no delay or added complexity to the existing button.
- **owner gets:** This allows rich physical interactions such as swipes, multi-finger taps, long presses, and patterns without compromising the existing primary button's responsiveness, enabling safer and more nuanced control.
- effort: Significant: PCB redesign, firmware updates, power management, and usability testing.  ·  risk: Medium: new hardware introduces complexity and potential bugs but would be thoroughly tested before deployment.
- cost: Moderate increase in BOM cost and power consumption due to sensor.  ·  latency: Negligible impact on response times, input detected locally and processed by the pendant firmware.
- security: Potential new attack surface if sensor input is spoofed, mitigated with hardware debouncing and physical presence checks.


## What it asked for

_Nothing._
