# Harness derivation — mac-vision — round 216

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to use the pendant's single button as a multi-mode interaction switch to control complex Mac UI workflows interactively with the mac-vision accessibility loop, enabling stateful command sequences, undo/redo, and user confirmations without requiring additional hardware buttons or gestures."
- **useful because:** The owner can directly and safely control multi-step Mac tasks via the pendant, leveraging the existing accessibility loop and preserving the interruptibility and safety of the interaction. This turns the pendant into an expressive remote control for the Mac, enhancing productivity and accessibility without new device complexity.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** under 1 second per step
- **cost:** moderate; mostly local compute and some relay signaling
- **security:** Controls complex UI but requires the accessibility grant and verified consent; states and confirmations require careful handling to avoid accidental destructive actions.
- **missing:** Multi-step stateful interaction model for mac-vision's accessibility loop; Command sequencing and undo/redo management; Pendant button multi-mode interaction software in firmware and mac-vision harness

### "Enable mac-vision to verify actual Mac UI state by comparing the accessibility tree with planned workflow steps, ensuring exact task completion and enabling intelligent error recovery steps when UI state mismatches occur."
- **useful because:** It would provide robust workflow execution with error detection, prevent silent failures, and allow guided retries or alternative strategies to complete complex multi-step workflows reliably.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** seconds for verification between steps
- **cost:** moderate; requires local accessibility tree snapshots and comparison logic with planned state
- **security:** Requires access to accessibility tree and memory of workflow state, careful handling of privacy and data storage.
- **missing:** Workflow state machine and UI accessibility state diff and verifier; Integration with mac-vision planned steps and execution feedback

### "Provide the owner with a continuously updated prioritized list of Mac UI tasks and goals by integrating the mac-vision accessibility loop observations with the owner's current task facts, day plan, and workflows from workbench contexts, displayed dynamically on the pendant and Mac surfaces."
- **useful because:** The owner gains real-time awareness of what work is ready, critical, or waiting on their Mac, helping them prioritize and decide what to do next with minimal manual task management overhead.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** background
- **latency:** seconds to minutes for updates
- **cost:** moderate due to background polling and processing
- **security:** Task data is sensitive; must handle personal data securely and respect privacy preferences.
- **missing:** Aggregation of mac-vision UI observations, memory service task facts, day plan, and workbench contexts into a unified prioritized list; Dynamic display / notification system on pendant and Mac; Task ranking logic combining structural priority and topical urgency

### "Allow the owner to voice control and confirm Mac UI interactions using the pendant's microphone and earbuds in an end-to-end encrypted manner, combining the pendant's real-time audio uplink with the Mac vision loop and relay infrastructure for secure, low-latency voice command execution and feedback."
- **useful because:** Voice control supplemented by visual verification and feedback on the Mac greatly enhances accessibility and hands-free control for the owner, enabling efficient and confident computer use in many contexts where typing or clicking is inconvenient or impossible.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to seconds latency
- **cost:** high due to real-time audio processing and secure relay
- **security:** Requires strong encryption and user consent management to protect privacy and prevent unauthorized voice command injection.
- **missing:** Real-time secure audio streaming and command recognition pipeline; Integration with mac-vision accessibility control pipeline for command execution; Audio feedback loop to pendant earbuds

### "Create a system where the mac-vision agent can automatically detect, highlight, and offer to fix UI permission issues or common accessibility errors causing failures in Mac automation workflows, improving reliability and owner understanding without manual diagnosis."
- **useful because:** It instantly surfaces reasons why multi-step UI workflows fail—often due to permission denial or UI changes—and offers guided fixes or explanations, reducing frustration and downtime for the owner.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** low to moderate, mostly logic and UI overlay
- **security:** Reads accessibility and permission status, must carefully respect owner privacy and consent.
- **missing:** Permission status introspection integration; Accessibility error detection heuristics; Owner-facing notification and repair interface


## Changes it proposed to its own stack

### `hardware` — Design and build a new pendant device iteration with at least two physical buttons to allow more expressive direct physical triggers for command confirmation, mode switching, and fallback interaction alongside the existing single-button and LED.
- **owner gets:** Increased physical control improves safety and expressiveness of interactions with mac-vision and other system facets, reducing reliance on ambiguous button gestures and increasing confidence in command execution.
- effort: Significant hardware development, firmware updates, and software integration across all surfaces.  ·  risk: Mismatches in firmware and harness software require careful deployment; more buttons can increase accidental presses without good mapping.
- cost: Higher device manufacturing cost and slightly increased power consumption.  ·  latency: None expected.
- security: No direct impact; more controls increase attack surface if not properly handled.
- depends on: firmware button driver support; mac-vision interaction software updates


## What it asked for

_Nothing._
