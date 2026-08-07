# Harness derivation — mac-vision — round 126

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision computer-use loop with safe autonomous UI interaction on the Mac to complete everyday tasks without explicit commands."
- **useful because:** Turn the Mac into an intelligent assistant that can autonomously interact with app UIs, click buttons, type text, and complete multi-step workflows without manual intervention.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** sub-second for simple UI steps, seconds for multi-step workflows
- **cost:** Moderate API cost due to continuous UI state processing and reasoning
- **security:** Must ensure no private data leakage; user control over autonomous actions with opt-in and real-time override; strict safety policies required.
- **missing:** Permissions computerUse.loopEnabled and visionUploadConsented; UI hierarchy and app context richer live streams; Integration support from relay and browser surfaces for cross-app workflows

### "Create composite multi-surface workflows combining Mac UI control, browser automation, and voice pendant for seamless user assistance across apps and devices."
- **useful because:** Leverages the unique strengths of multiple surfaces working as a single intelligent assistant, enabling complex task execution that no one surface can do alone.
- **path:** mac-vision → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes depending on workflow complexity
- **cost:** Higher API cost due to cross-surface coordination and session management
- **security:** Must safeguard authenticated sessions and data privacy; user control on bridging surfaces needed.
- **missing:** Robust cross-surface orchestration infrastructure; Synchronized context sharing protocols; Secure authenticated browser session management

### "Implement typed Mac actions with structured receipts and reversible undo for safe exploratory automation with user trust."
- **useful because:** Provides trust and observability for broad Mac automation rights by allowing user to review and reverse actions easily, boosting confidence in autonomous interventions.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds per action
- **cost:** Low to moderate cost dominated by local bookkeeping and relay syncing.
- **security:** Strong action auditing required to prevent misuse; undo limited to reversible commands only.
- **missing:** Full typed action receipt infrastructure; Undo command pattern enforcement; Relay support for receipt queries

### "Provide a natural language interface on the Mac that integrates local screen content recognition, app command execution, and contextual follow-up, allowing fluid spoken or typed conversation with the Mac as an assistant with memory of recent interaction."
- **useful because:** Enables the owner to interact with complex Mac applications, perform data entry, navigation, and information retrieval through conversational language, reducing the friction of manual tasks and switching focus.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** sub-second for simple commands, seconds for multistep or contextual conversations
- **cost:** Moderate due to realtime context analysis, dialogue management, and command execution.
- **security:** Must safeguard sensitive screen content and user data; require controls on command execution; manage conversational context securely.
- **missing:** Full mac-vision loop capability and permissions; Conversational context management engine; Integration of screen mocking and command capabilities


## Changes it proposed to its own stack

### `integration` — Develop a seamless multi-channel context synchronization and sharing protocol that enables all surfaces (Mac, browser extension, pendant relay, terminal) to share live UI state, user goals, and assistant reasoning context with minimal latency and bandwidth.
- **owner gets:** Unifies the distributed AI assistant experience across devices and input modalities so the owner receives consistent, context-aware help without repeated authentication or lost context.
- effort: Moderate software development with cross-surface protocol design, data serialization optimization, and synchronization conflict resolution.  ·  risk: Synchronization bugs and data leaks could harm usability or privacy; requires careful encryption and access control design.
- cost: Minimal cloud API cost, some local CPU and network usage; amortized by better assistant efficiency and reduced repeated queries.  ·  latency: Low latency needed for smooth user experience, especially during handoffs between devices.
- security: Strong authentication and encryption essential to protect sensitive user context.
- depends on: Existing APIs on all surfaces for status and commands; Permission to share and store context data securely


## What it asked for

_Nothing._
