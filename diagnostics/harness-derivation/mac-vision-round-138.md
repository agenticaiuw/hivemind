# Harness derivation — mac-vision — round 138

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a pendant device skill for physical triggers to assist Mac-vision's visual interaction on MacBook, allowing non-verbal control and confirmation gestures."
- **useful because:** This creates a new wearable+computer synergy enabling the owner to interact with the Mac visual control without interrupting their workflow vocally or manually at the Mac.
- **path:** pendant → mac-vision
- **model tier:** realtime
- **latency:** 50ms per trigger event
- **cost:** Minimal compute cost; uses pendant input hardware.
- **security:** Requires careful mapping and consent of physical triggers to avoid accidental commands.
- **missing:** pendant input event APIs; integration with computerUse loop

### "Integrate browser_run_actions with Mac-vision's computer use loop to seamlessly switch between browser extension control and desktop UI visual control depending on context in workflows."
- **useful because:** This ensures the most efficient and effective method is used for web+desktop hybrid workflows, improving owner productivity and avoiding duplicated effort.
- **path:** mac-vision → browser-extension
- **model tier:** realtime
- **latency:** 200ms per context switch decision
- **cost:** Moderate API cost for state detection and switching
- **security:** Needs to securely handle browser extension permissions and desktop UI access, and respect user privacy.
- **missing:** Context sharing between browser extension and Mac-vision loop; Dynamic decision logic capabilities

### "Provide fine-grained UI element state context and event monitoring to Mac-vision for proactive visual assistance, beyond just static accessibility snapshots."
- **useful because:** Enables Mac-vision to track live changes in UI and respond appropriately without relying solely on repeated polling or static snapshots.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 50ms event delivery
- **cost:** Low API cost for event-based updates
- **security:** Needs strict filtering to avoid sensitive data leakage in UI events.
- **missing:** UI event subscription APIs; event filtering logic

### "Add a Mac agent API and framework for UI element event subscription and filtering to allow Mac-vision to receive live UI change notifications and react proactively."
- **useful because:** This capability enables Mac-vision to offer proactive visual assistance based on real-time UI changes, reducing polling and improving responsiveness.
- **path:** mac-planner → mac-vision
- **model tier:** realtime
- **latency:** 50ms per event delivery
- **cost:** Low, event-driven
- **security:** Must carefully filter and redact sensitive UI data to protect privacy.
- **missing:** New event subscription API supporting UI element changes and filters.; Event delivery infrastructure and privacy controls.

### "Create a secure shared context bridge between the browser extension and Mac-vision for seamless hybrid task workflows involving browser and desktop UI control."
- **useful because:** Allows Mac-vision and browser extension to share state and coordinate their actions intelligently for complex multi-app tasks, enhancing owner productivity.
- **path:** mac-vision → browser-extension
- **model tier:** realtime
- **latency:** 100ms context sync
- **cost:** Moderate due to state synchronization
- **security:** Requires trusted handshake and encryption to protect session data and user privacy.
- **missing:** Secure shared context bridge APIs.; Browser extension integration for context publishing.

### "Expand pendant input hardware to include multiple buttons or sensors to enable richer physical interaction for controlling Mac-vision and other system nodes."
- **useful because:** Multiple input methods on the pendant allow faster, more nuanced, and context-aware physical controls, reducing reliance on voice or keyboard/mouse for complex workflows.
- **path:** pendant → mac-vision
- **model tier:** realtime
- **latency:** 50ms per input processing
- **cost:** Hardware upgrade cost plus minimal runtime API cost.
- **security:** Physical inputs must be securely mapped to authorized commands to avoid unintended actions.
- **missing:** Hardware redesign and integration of additional sensors or buttons on the pendant.; Firmware changes to support multi-input processing.

### "Enable privacy-preserving real pixel screenshot capture and streaming to Mac-vision with owner-controlled permissions for high-fidelity visual assistance."
- **useful because:** Pixel screenshots complement accessibility hierarchy data for complex visual tasks that require precise visual context, increasing Mac-vision's usefulness for tasks involving images, graphics, or custom UI.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100ms per screenshot or stream update
- **cost:** Moderate bandwidth and storage costs for image data.
- **security:** Strict consent and filtering to prevent leakage of sensitive screen content; owner controls initiation and stopping of capture.
- **missing:** Hardware and OS support for controlled screen capture and streaming.; Privacy controls and UI for owner permission management.

### "Provide real-time multi-application UI and context merging for Mac-vision to deliver a holistic understanding of the owner's entire desktop environment."
- **useful because:** Mac-vision today sees discrete apps individually. Merging contexts visually and semantically from multiple sources lets it plan and act on complex workflows crossing app boundaries like file browsers, editors, browsers, and communication tools.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 150ms per context update
- **cost:** Moderate compute and network cost for data merging and inference.
- **security:** Must handle privacy sensitively as this involves combining multiple sensitive UI contexts.
- **missing:** Cross-application UI context merger and inference logic.; APIs to provide simultaneous multi-app snapshots with alignment.


## Changes it proposed to its own stack

### `integration` — Build a typed action broker and policy layer that mediates all computer control actions across Mac-vision, browser-extension, mac-run_actions, and mac_delegate to ensure safety, observability, reversibility, and policy compliance.
- **owner gets:** This provides the single most useful capability because it makes all complex cross-application automations safe, trackable, and manageable by the owner, enabling confident delegation and global coordination.
- effort: Large engineering effort across multiple subsystems and coordination with OS-level permissions.  ·  risk: Technical and usability risks in managing action conflicts and latency.
- cost: Additional computation and network overhead for action brokering.  ·  latency: Slight increase in latency due to mediation layer.
- security: Improves security by enforcing policies and logging.
- depends on: Typed classification of all computer actions; Unified policy definitions; Cross-agent communication protocols for action coordination


## What it asked for

### `p8-ldkt` (permission) — computerUse.loopEnabled
- why: To enable the Mac-vision's visual interaction loop, allowing it to see UI accessibility hierarchy and assist the owner through visual computer interactions.
- risk it sees: Enabling loop allows reading UI state and potentially interacting with apps; owner limits apply.

### `p9-8a5t` (permission) — visionUploadConsented
- why: To allow Mac-vision to process visual UI data including screenshots to provide better visual assistance and improve action planning, essential for activating its loop.
- risk it sees: Processing visual data may reveal sensitive screen content; privacy controls required.

### `s3-tgq8` (skill) — pendant-mac-vision-triggers
- does: Provides physical button trigger input events from the pendant to the Mac-vision agent to enable non-verbal control and confirmation of complex Mac UI tasks.
- must be on-device because: Requires local physical button hardware interaction that only the pendant can provide, and immediate low-latency response to owner input.
- trigger: button press (single, double, long press)
- storage: Stores trigger configuration and usage counters on the pendant flash; small (~1 KB)
- RAM budget: 8192 B

## Its own summary

Proposed enhancing Mac-vision and the wearable pendant integration with a physical trigger device skill, live UI event subscription in Mac accessibility APIs, and a secure shared context bridge between browser extension and Mac-vision for hybrid workflows. Identified missing event subscription APIs, expanded pendant inputs, privacy-controlled pixel screenshot sharing, and a typed action broker policy as important future needs.

**Biggest unknown:** Whether orchestrator grants computerUse.loopEnabled and visionUploadConsented permissions, enabling the Mac-vision visual interaction loop to be activated and fully useful.

