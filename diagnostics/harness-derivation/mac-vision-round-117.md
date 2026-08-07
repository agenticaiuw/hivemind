# Harness derivation — mac-vision — round 117

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable smart, consented computer use loop on MacBook for seamless task automation"
- **useful because:** The owner should be able to delegate complex computer tasks to the AI assistant that requires pixel-level screen analysis and interaction, enabling fully autonomous workflows beyond simple API calls or scripts. This would transform the MacBook into a truly intelligent assistant that can handle multi-step, ambiguous, or visual tasks while respecting privacy and consent.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-judgement → faculty-perception → faculty-action
- **model tier:** gpt-4.1-mini for mac-vision, gpt-5.6-luna for higher level planning and judgement
- **latency:** Low-latency for mac-vision loop (100-300 ms per action step), background or scheduled work for long workflows
- **cost:** Moderate to high due to frequent vision processing and interaction steps; cost dominated by API calls to models and vision analysis
- **security:** Full privacy and security review required. Vision data must only be uploaded with explicit owner consent. Actions must be logged and auditable. High-risk potential if malicious or erroneous commands are made, thus strict preconditions and opt-in are needed.
- **missing:** Explicit owner consent framework for vision upload and computer use loop; Privacy and security review and technical implementation on device and server; Typed action policy for safe and observable execution; Hardware or OS level support for stable pixel-based accessibility interaction without false clicks or data leaks; Robust UI snapshot and state management for decision making without interfering with user focus; Fallback and recovery for failed or ambiguous UI actions

### "Multimodal contextual Mac task execution combining vision, UI state, and voice commands"
- **useful because:** The owner should be able to initiate and guide complex Mac workflows by speaking naturally and pointing visually, while the AI combines screen analysis and UI structure understanding to execute precise steps across multiple applications, improving efficiency and ease of use.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-judgement → faculty-perception → faculty-action
- **model tier:** gpt-4.1-mini for vision and immediate UI, gpt-5.6-luna for planning and judgement
- **latency:** Interactive low latency for visual and voice inputs, with background planning for complex multi-step tasks
- **cost:** Moderate due to combined multimodal inference and voice processing
- **security:** Requires robust consent and privacy controls for vision and microphone data, plus secure action execution policies.
- **missing:** Integrated multimodal input processing pipeline; Seamless interaction between voice, vision, and UI action surfaces; Context maintenance across modalities to resolve ambiguity and confirm intent


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure vision processing chip on the MacBook that can analyze screen pixels locally without sending raw screen data off the device, enabling smart computer use loop functionality with privacy guarantees.
- **owner gets:** This allows the smart computer use loop AI (mac-vision) to operate in real time with pixel analysis while guaranteeing that screenshots and visual data never leave the device without explicit consent, increasing privacy and security.
- effort: Medium to high, requiring hardware design and firmware integration with macOS and AI software stack.  ·  risk: May introduce hardware bugs or delays if not properly integrated; fallback to software vision analysis required.
- cost: Additional hardware cost and power draw expected; offsets cloud and manual workload costs.  ·  latency: Improves latency for vision tasks significantly; essential for real-time interaction.
- security: Strong positive impact on security by localizing sensitive visual data and reducing upload risk.
- depends on: Operating system support for dedicated vision chip integration; API and software stack updates to utilize the new hardware

### `integration` — Implement a typed action policy and audit trail across the AI agent system to classify all Mac UI manipulations and keep real-time observability with reversible control for safety and debugging.
- **owner gets:** This prevents accidental or malicious irreversible actions on the Mac, supports audit, rollback, and allows the owner to understand and control the AI assistant's real interactions with their computer.
- effort: Medium; involves backend updates, agent code changes, and new UI for logs and control.  ·  risk: Complexity in classification may cause blocking or false positives; requires thorough testing and owner education.
- cost: Backend storage and API usage for logging and audit; small latency impact due to added checks.  ·  latency: Low for normal operations; may add slight delays during decision points.
- security: Strong positive security improvement by providing transparency and accountability.
- depends on: Existing action execution framework (mac_run_actions, mac_delegate); Audit log storage and retrieval APIs


## What it asked for

_Nothing._
