# Harness derivation — mac-vision — round 178

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the AI Pendant to autonomously navigate and control any Mac application UI without screen recording, relying fully on the macOS Accessibility API with fine-grained action classification for safety."
- **useful because:** The owner gains true hands-free Mac control with observability and undo capability, avoiding intrusive screen capture and focus theft, enabling seamless multi-app workflows.
- **path:** mac-vision → mac-planner → relay-realtime → unified
- **model tier:** gpt-4o-mini
- **latency:** 200ms per UI action
- **cost:** Low API call cost; main cost is engineer time and testing.
- **security:** Needs macOS Accessibility permission granted specifically to the agent binary; requires strict typed action gating to prevent destructive mistakes.
- **missing:** macOS Accessibility permission to agent binary; Typed action broker for UI actions; Undo and recovery infrastructure

### "Create an integrated, persistent, ranked multi-surface task and goal store that aggregates owner intent from reminders, notes, voice snippets, browser tabs, calendar events, and open tasks."
- **useful because:** The owner can see and prioritize all meaningful pending work regardless of where it originated or which device/surface created it, enabling better planning and delegation across devices.
- **path:** mac-planner → unified → relay-realtime
- **model tier:** gpt-5o-luna
- **latency:** 1s for sync and ranking; background update acceptable
- **cost:** Cloud or Mac RAM/disk usage and periodic computation for ranking all inputs.
- **security:** Data privacy to owner only; sensitive data must never leak externally and must be encrypted at rest and in transit.
- **missing:** Cross-surface intent synthesis; Robust fact/task merging and ranking algorithms; Writable memory store that can be observed by all surfaces

### "Allow cross-surface AI-powered context-aware Mac command orchestration that integrates visionLoop UI actions, terminal commands, and browser interactions into seamless, recoverable multi-step workflows."
- **useful because:** The owner can delegate complex tasks spanning multiple applications and environments on the Mac, with AI oversight handling failures, retries, and undo steps, saving time and reducing errors.
- **path:** mac-vision → mac-terminal → browser-extension → mac-planner → unified
- **model tier:** gpt-5o-luna
- **latency:** sub-second for single steps, minutes for complex workflows
- **cost:** Moderate to high computational cost depending on workflow complexity.
- **security:** Execution gating and confirmation needed for high-impact steps; history and undo are critical to avoid mistakes.
- **missing:** Integrated state and control APIs across Mac and browser surfaces; Middleware to coordinate distributed multi-step workflows; Comprehensive undo infrastructure spanning all surfaces

### "Provide a physical transaction approval system via the second pendant button, dedicated to sensitive AI-assisted Mac control confirmations and multi-step workflow authorizations."
- **useful because:** The owner retains physical, immediate control over any high-impact AI-driven actions on the Mac, preventing accidental or unauthorized operations while maintaining fluid voice and UI workflows.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** gpt-4o-mini
- **latency:** instant on button press
- **cost:** Minimal hardware and software cost as it extends current pendant button capabilities.
- **security:** Must securely isolate the approval channel and properly link requests to responses to prevent spoofing or replay attacks.
- **missing:** Firmware support for a dedicated approval button event; Integration with orchestration layers to require physical confirmation for sensitive actions


## Changes it proposed to its own stack

### `browser-harness` — Add a robust authenticated browser session manager and page-watch service capable of capturing user-selected text and UI state, with explicit liveness, leasing, and recovery across Safari extension, Mac agent, relay, and pendant bridge.
- **owner gets:** The owner gains trusted, persistent, private web session observability and mediated automated interaction, enabling advanced portal automations and seamless UI bridging.
- effort: Significant engineering and testing over multiple components and platforms.  ·  risk: Complexity means potential latency and edge case failures in syncing; requires secure storage and handling of authentication tokens.
- cost: Moderate server and client resources for session state and event monitoring.  ·  latency: Milliseconds to low seconds per event; should be asynchronous and batch processed.
- security: Must handle private user credentials securely; user consent and strict privacy policies needed.
- depends on: browser-run-actions capability; relay job and device leasing mechanisms


## What it asked for

_Nothing._
## Its own summary

Proposed five new capabilities and changes that would dramatically enhance the owner's experience by enabling autonomous, safe, and reversible AI-driven Mac UI control without screen recording, a unified multi-surface task and goal store, authenticated browser session management for private portals, orchestrated cross-surface command workflows, and a physical transaction approval button on the pendant. These require macOS Accessibility permissions, new middleware coordination layers, enhanced browser harness, and firmware support for dedicated button events.

**Biggest unknown:** Whether the owner will grant the macOS Accessibility permission to the agent binary to unlock full visionLoop automation and enable safe UI control without pixel capture.

