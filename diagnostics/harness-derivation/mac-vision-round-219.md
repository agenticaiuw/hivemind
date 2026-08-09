# Harness derivation — mac-vision — round 219

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide the mac-vision agent with the ability to validate multi-step work by comparing claimed UI states with real-time accessibility tree state on the Mac, reporting divergences and probable failures in interactive workflows."
- **useful because:** Currently, there is no mechanism to check if the mac-vision agent's claimed UI interactions actually resulted in the expected changes on screen. This would improve robustness of delegated multi-step workflows, detect failures early, and enable reliable recovery or retries.
- **path:** mac-vision → mac-delegate
- **model tier:** background
- **latency:** seconds
- **cost:** Low CPU and memory to compare accessibility snapshots and cached claims
- **security:** UI state can contain sensitive information visible on screen; ensure strict access control and local-only processing without exfiltration.
- **missing:** A way to store and compare cached claimed UI states for a work context; API endpoint to fetch and diff live versus claimed UI state; Integration with the existing workbench context tracking system

### "Enable mac-vision agent to autonomously pick next computer interaction steps based on multi-step workflows open in the workbench context, filling in ambiguity and selecting UI controls to press using the accessibility tree without pixel capture or focus shift."
- **useful because:** This uses the full power of accessibility API to navigate multi-step UI workflows on Mac without disturbing the owner or needing the riskier pixel-level actions. It leverages an existing infrastructure of workflow contexts to get tasks, and would make mac-vision an operational autonomous UI agent.
- **path:** mac-vision → mac-delegate
- **model tier:** realtime
- **latency:** sub-second
- **cost:** Low CPU; uses accessibility tree data already cached at the agent
- **security:** Requires trustworthy accessibility permissions and careful handling of sensitive UI elements, no data exfiltration through this.
- **missing:** Better integration between workbench contexts and mac-vision loop to enable automatic continuum of workflows

### "Improve mac-vision's safety by adding an adaptive confirmation mechanism that requests user approval only for high-impact Mac UI actions, distinguished by action classification, minimizing interruptions but maximizing security."
- **useful because:** Reducing unnecessary confirmation requests while preserving safety would improve user experience with mac-vision. It aligns with the owner's policy for maximum access but adds observability and selective confirmation for sensitive actions like sending mail or deleting files.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** Very low CPU, mostly local policy enforcement
- **security:** Misclassifying a dangerous action could cause harm; must be auditable and overrideable by the owner.
- **missing:** Action classification mechanism integrated with mac-vision action preparation; User approval UI that is minimal and integrated with the pendant or Mac

### "Provide a capability for mac-vision to send a tactile or auditory confirmation prompt to the owner via the pendant when an unpredictable or high-risk UI action is about to be executed, allowing owner to approve or abort via a simple physical gesture on the pendant."
- **useful because:** This creates a robust safety layer aligned with the owner's policy, leveraging the unique hardware pendant input channel to confirm high-risk commands before execution, without disrupting the Mac or relying solely on software permissions.
- **path:** mac-vision → pendant
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** Moderate due to hardware interaction and real-time feedback loop
- **security:** Security of input channel on pendant is critical to prevent spoofing or accidental approval; privacy of action context must be preserved.
- **missing:** Integration between mac-vision action pipeline and pendant hardware input; Protocol to define which actions require prompt and how approval is communicated; Failsafe timeout and abort mechanism

### "Enable the mac-vision agent to synthesize short, natural language summaries of changes in Mac UI state after an action, by reading accessibility tree diffs, and speak or display these to the owner for feedback and confirmation."
- **useful because:** This feedback improves transparency and allows the owner to monitor what mac-vision did without needing to watch the screen or guess from indirect cues. Useful especially for multi-step or background workflows.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** Moderate, involving diff calculation and natural language generation
- **security:** Summarized UI state can expose sensitive info; outputs must be carefully vetted and access-controlled.
- **missing:** Component to diff accessibility trees before/after an action; Natural language generation model tuned for UI description; Output channel integration to speak or display summaries

### "Build a shared interruption and assistance policy store that all agents including mac-vision can read and update to coordinate when and how to interrupt the owner with notifications or requests during Mac UI workflows, preserving owner focus and safety."
- **useful because:** Currently, there is no cross-agent policy coordination about interruptions or assistance requests. A shared policy store would allow mac-vision and other agents to respect owner preferences, coordinate multi-agent communication, and reduce disruptive interruptions.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Low CPU, some persistent storage
- **security:** Policy data is sensitive; must be write-protected and access controlled to prevent misuse or unwanted interruptions.
- **missing:** Cross-agent policy API compatible with all surfaces; User interface to configure interruption preferences; Integration points in agents to consult and update policies

### "Allow mac-vision to detect and handle login challenges such as 2FA prompts, password dialogs, and captchas on Mac UI using accessibility tree analysis, interacting with controls to guide the owner or automate standard steps safely."
- **useful because:** Login challenges block some workflows and require delicate handling. Automation here speeds task completion and reduces frustration, while ensuring owner control by only acting on recognized and safe UI elements.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds
- **cost:** Moderate, due to complex UI and security considerations
- **security:** Highly sensitive info handled; strict permission and data handling needed; false positives must be minimized to avoid security issues.
- **missing:** Specialized UI detection models for login challenges; Safe interaction protocols for authentication UI elements

### "Enable mac-vision to monitor system and app-level notifications on the Mac UI by reading accessibility notifications or UI elements, categorizing them for urgency and type, and proactively reporting or acting on them according to owner policy."
- **useful because:** The owner can miss important notifications or be overwhelmed by noise. A filtering and reporting agent improves focus and ensures critical alerts are acted upon or communicated promptly.
- **path:** mac-vision
- **model tier:** background
- **latency:** minutes
- **cost:** Low CPU, mostly reading and classification
- **security:** Notifications can include sensitive info, so privacy and access control must be carefully managed.
- **missing:** Access to notification UI or accessibility events; Classification models for notification importance and type

### "Provide mac-vision with the ability to visually detect, interpret, and interact with complex data visualizations and graphs in Mac applications by analyzing the accessibility tree and suggesting next interaction steps or data summaries."
- **useful because:** Many Mac apps present complex charts and graphs which are hard to interact with programmatically and require visual interpretation. This capability enables mac-vision to assist with these workflows, improving utility in data-heavy applications.
- **path:** mac-vision
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Moderate due to complexity of visual data interpretation and interaction planning
- **security:** Visual data might include sensitive info; must ensure local processing and careful data handling.
- **missing:** Specialized model or heuristic for interpreting visualization structures in accessibility tree; Interaction patterns for graph elements

### "A continuous, fully autonomous mac-vision agent workflow executor that can pick up any multi-step task from an open workbench context, perform all UI interactions via accessibility without pixels or focus stealing, validate each step by comparing live UI state to claimed state, handle errors by retry or graceful recovery, and report live progress to the owner via synthesized natural language summaries."
- **useful because:** Today, mac-vision can plan and do atomic UI actions but cannot fully automate complex multi-step workflows robustly or recover from errors. Making mac-vision a truly autonomous UI executor with verification and feedback would drastically increase owner productivity, trust, and agent usefulness.
- **path:** mac-vision → mac-delegate → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** Moderate, involving real-time accessibility tree processing, natural language generation, and error handling
- **security:** Requires strict permission and transparency; errors could cause disruptions if unchecked; privacy of UI state must be guaranteed.
- **missing:** Full implementation of /vision-loop/* accessibility API for tree snapshots and interaction; Persistent storage and read/write of workbench contexts with claimed vs actual UI state; Integration of natural language generation for UI state summaries; Error detection and recovery mechanisms based on UI state diffs; User confirmation flow integrated with pendant hardware


## Changes it proposed to its own stack

### `integration` — Create and standardize a cross-agent context and policy coordination service that allows mac-vision, mac-planner, relay-realtime, and other agents to share, update, and respect interruption policies, owner preferences, and task priorities in real time.
- **owner gets:** Currently, agent coordination is fragmented, leading to possible redundant or conflicting interruptions and unaligned priorities. A unified context and policy service would make the owner's experience smooth, respectful of their focus and preferences, and more predictable.
- effort: Medium; requires cross-agent protocol design and implementation across multiple surfaces and agents.  ·  risk: Potential misalignment if policy data becomes corrupted or unsynchronized; careful design of conflict resolution and security is needed.
- cost: Low operational cost beyond data storage and messaging overhead.  ·  latency: Near real-time synchronization needed but not ultra-low latency.
- security: Sensitive preference and policy data needs strict access control and encryption in transit and at rest.

### `model-routing` — Deploy a specialized LLM model fine-tuned for interpreting Mac accessibility tree diffs and generating concise, owner-friendly natural language summaries of UI changes after each mac-vision action step.
- **owner gets:** Currently, the owner must guess what automated UI actions did or visually verify. Synthesized summaries improve transparency, trust, and situational awareness, especially for multi-step workflows running without close supervision.
- effort: Medium; requires dataset creation, fine-tuning, and integration into the mac-vision loop.  ·  risk: Potential inaccuracies in summarization may confuse the owner if not properly validated or allow leakage of sensitive UI info if not sanitized.
- cost: Increased API or compute cost for runtime model use.  ·  latency: Moderate, must balance summary length and generation speed for smooth user experience.
- security: Sensitive UI information must be carefully filtered before summarization.
- depends on: GET /vision-loop/* accessible UI snapshots


## What it asked for

_Nothing._
