# Harness derivation — mac-vision — round 100

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision computer-use loop for safe, privacy-aware, fine-grained UI control and interaction on the MacBook"
- **useful because:** The owner can have an always-available AI assistant that can observe UI changes, respond to multi-step and ambiguous tasks, click and type on the real UI screen without stealing focus, and complement the Mac agent's high-level action capabilities for apps without APIs. This capability is uniquely enabled by the synergy of a worn device, a Mac, a relay, and browser extension working together with an always-awake loop that respects privacy and safety.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for vision/UI loop; gpt-5.6-luna for higher-layer judgement and coordination
- **latency:** Low-latency for UI interaction cycles, up to 25 steps per user turn; other layers operate asynchronously
- **cost:** CPU and memory cost for limited pixel access and UI snapshots; token cost for model usage in low-latency tier; token cost dominated by multi-layer collaboration
- **security:** Must strictly enforce user consent and privacy controls to prevent leaking sensitive screen data; user must opt-in to visionUploadConsented and loopEnabled; mitigating risks of mis-clicks or intrusive behavior by limiting mutations initially; logging and receipts for all UI mutations.
- **missing:** Real-time UI hierarchy snapshot accessible to mac-vision; User-consent-based enabling flag for visionUploadConsented and computerUse.loopEnabled; Fine-grained typed action policy for UI loop actions with optionally confirmed destructive interactions; Robust coordination with judgement and perception layers for task prioritization and safety; Integration with screen privacy modes and sensitive app detection

### "Enable continuous and reliable multi-agent coordination for intelligent delegation of ambiguous or multi-step Mac computer tasks among mac-vision, mac-planner, mac-terminal, and browser-extension"
- **useful because:** The owner gains a seamless AI hive mind that intelligently assigns tasks to the right agent and surface, reducing friction, automating complex workflows, and improving the overall user experience by trusting the system to handle interactions across multiple apps and modalities.
- **path:** mac-vision → mac-planner → mac-terminal → browser-extension → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for judgement and delegation logic
- **latency:** Medium latency acceptable for complex task planning and delegation
- **cost:** Model compute cost driven by judgement and planner agents, minimal overhead on mac-vision tier
- **security:** Delegation must respect user consent boundaries and never access apps beyond granted permissions; transparent logs and undo options for delegated tasks; trust boundary clearly defined
- **missing:** Robust intent resolution and task planning between agents; Cross-surface state synchronization and shared memory contexts; Undo and receipt protocols coordination; Policy for delegation permission and fallback; Dynamic workload balancing among agents

### "Provide a secure, user-transparent UI mutation receipt and undo system integrated with the mac-vision computer-use loop, mac-run-actions, and delegation agents"
- **useful because:** The owner can confidently allow AI to perform UI actions knowing that every change has a transparent record and can be undone if unwanted, improving safety and trust in AI-driven computer control.
- **path:** mac-vision → mac-planner → faculty-action
- **model tier:** gpt-5.6-luna for action management and receipt generation
- **latency:** Low latency for immediate receipt generation and undo readiness
- **cost:** Storage and token cost for receipt logs; compute for validating and triggering undo actions
- **security:** Ensure receipt logs are private and tamper-resistant; undo actions must be safe and confirmed; no action performed without proper consent and logging
- **missing:** Low-level integration of UI mutation tracking hooks; Secure storage for action receipts linked to each UI step; Undo orchestration protocols with failback safety; User interface for viewing and managing receipt history

### "Enable intelligent privacy-aware scheduling and batching of UI snapshot captures and vision data uploads between the MacBook and pendant to minimize network use and maximize user privacy"
- **useful because:** The owner retains control over when and how UI data is shared and processed, reducing privacy risks and battery/network consumption while allowing the computer-use loop to function effectively with minimal interruptions.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** gpt-5.6-luna for scheduling and privacy policy decisions
- **latency:** Flexible; non-real-time batching acceptable
- **cost:** Minimal compute overhead on device; network usage savings reduce operational cost
- **security:** Ensure all data transfers are encrypted and consented; provide user feedback and controls for scheduling preferences and emergency override
- **missing:** Cross-device communication protocol optimized for privacy and efficiency; User interface for consent and scheduling configuration; Local AI component on pendant for batching decisions


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure enclave or TPM-like hardware module to the MacBook and wearable pendant for encrypted storage and processing of sensitive UI snapshots and action receipts, to enhance privacy and security of the computer-use loop data.
- **owner gets:** Ensures that all sensitive screen data and AI agent action records are encrypted at rest and in transit and only accessible to authorized components under user consent, enhancing trust and security of AI-assisted computer control.
- effort: Significant hardware design and validation effort, plus OS and firmware integration; multi-year horizon but aligned with next device refresh cycles.  ·  risk: Hardware security module bugs or backdoors could compromise device; recovery requires hardware replacement or secure firmware updates.
- cost: Increase in device BOM cost; minimal power impact since security module optimized for low power.  ·  latency: Negligible latency impact for normal UI loop operations, added encryption/decryption overhead is minimal.
- security: Strong positive security impact by isolating sensitive data from main OS and applications.
- depends on: computerUse.loopEnabled; visionUploadConsented


## What it asked for

_Nothing._
