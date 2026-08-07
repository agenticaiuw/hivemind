# Harness derivation — mac-vision — round 131

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Real-time AI-driven computer-use loop on the owner's MacBook for physical interaction with the UI, including instant clicks, typing, app launches, and multi-step complex workflows."
- **useful because:** This would allow the owner to control and automate any application or UI scenario in real-time through an AI assistant that understands both the pixel-level and accessibility-level state of the Mac UI, vastly improving productivity and reducing manual effort.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** gpt-4.1-mini for immediate loop responsiveness and gpt-5.6-luna for planning complex workflows
- **latency:** Sub-second to low seconds for UI interaction actions, minutes for multi-step workflows
- **cost:** API costs mainly from the AI models running locally and on the relay; energy costs on Mac hardware; minimal network traffic costs
- **security:** Requires careful permissions and policy enforcement to prevent destructive or accidental actions; sensitive UI interactions and data seen by the AI; needs explicit user consent
- **missing:** permission computerUse.loopEnabled; permission visionUploadConsented; real-time UI snapshot granting; integration with the Mac accessibility APIs for deeper state understanding

### "Hybrid Mac assistant combining mac-vision real-time UI state and mac-planner multi-step goal planning for complex workflows spanning multiple apps."
- **useful because:** Enables the owner to initiate high-level goals and have them fulfilled with real-time feedback and adjustments based on UI state, making complex, multi-application tasks feasible and seamless.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna for planning, gpt-4.1-mini for vision loop component
- **latency:** Seconds to minutes for planning and execution cycles
- **cost:** Model execution costs for planning and vision; minor API calls for Mac state and actions
- **security:** Complex workflow execution needs safeguards and clear action logging to avoid errors or unwanted side effects
- **missing:** permission computerUse.loopEnabled; integration API or real-time data link between mac-vision and mac-planner; UI state synchronization mechanisms

### "Cross-surface authored browser interactions coordinated between mac-vision UI reading, browser-extension controlling browsing actions, and mac-planner managing goal state."
- **useful because:** Streamlines browser-based workflows by allowing natural language goals to be executed with seamless handoffs between UI reading, browser command execution, and planning, thus removing friction from multi-step online tasks.
- **path:** mac-vision → browser-extension → mac-planner
- **model tier:** gpt-4.1-mini for vision loop, gpt-5.6-luna for browser and planner coordination
- **latency:** Sub-second for UI state reads and browser actions, seconds for planner coordination
- **cost:** AI model processing mostly, some network calls to local hosts; low energy overhead
- **security:** Involves access to sensitive browsing data and sites; must respect privacy and user consent
- **missing:** permission computerUse.loopEnabled; integration between surfaces; browser session context synchronization


## Changes it proposed to its own stack

### `model-routing` — Create a hybrid routing model architecture that routes real-time, low-latency UI interaction queries to mac-vision's smaller model, and routes complex planning and multi-step workflows to mac-planner's more powerful model, dynamically switching based on query context and system load.
- **owner gets:** This makes interaction fluid and responsive, saving time and reducing friction by leveraging the best capabilities of each model tier without user intervention.
- effort: Medium software engineering effort to develop routing framework and integrate context-sensitive routing criteria.  ·  risk: Potential routing misclassifications may cause delays or suboptimal responses, recoverable by fallback mechanisms.
- cost: Saves API costs and improves efficiency by optimizing model usage.  ·  latency: Generally reduces latency for interactive UI steps while maintaining depth for complex tasks.
- security: No additional security risk beyond existing model usage.
- depends on: mac-vision; mac-planner

### `integration` — Develop a tightly integrated UI context sharing protocol between mac-vision's accessibility and pixel UI reads and mac-planner's high-level goal planner to enable seamless real-time cooperation and feedback loops between low-level UI state and high-level plan execution.
- **owner gets:** This would enable a smooth user experience where UI context changes inform planner adjustments instantly, and planned actions reflect back on UI state to adjust behavior dynamically.
- effort: Medium to high software engineering effort across surfaces; requires defining context schemas, messaging protocols and synchronization mechanisms.  ·  risk: Complex synchronization bugs or delays might cause inconsistent state perception; fallback and retry mechanisms needed.
- cost: Moderate API usage and network overhead for synchronization, but overall efficiency gains.  ·  latency: Potentially improved execution and responsiveness due to better context sharing.
- security: Ensuring secure and privacy-respecting transmission of UI state is essential.
- depends on: mac-vision; mac-planner

### `interaction` — Implement a user-controllable, context-aware confirmation and veto layer for mac-vision loop actions, enabling the owner to confirm, modify or cancel sensitive or irreversible UI actions before they are executed.
- **owner gets:** This gives the owner control and peace of mind over potentially destructive or unintended actions taken by the AI loop, balancing automation with trusted oversight.
- effort: Medium software effort to design UI/UX flow for confirmations, veto UI, and state tracking.  ·  risk: If overly intrusive, may annoy the user; if overly lax, may allow unwanted actions. Requires tuning with user feedback.
- cost: Negligible API or compute cost increase.  ·  latency: Adds slight delay for actions needing confirmation but maintains seamless flow otherwise.
- security: Significantly improves security and trustworthiness of AI-driven control.
- depends on: computerUse.loopEnabled


## What it asked for

_Nothing._
