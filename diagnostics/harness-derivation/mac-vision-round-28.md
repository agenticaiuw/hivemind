# Harness derivation — mac-vision — round 28

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to operate fully with pixel-level screen capture and interaction to automate any Mac UI task visually when APIs or accessibility are insufficient."
- **useful because:** This capability would allow the owner to delegate complex, multi-step, visual GUI tasks on their Mac that cannot be done via APIs or accessibility alone, saving time and effort and extending automation reach.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** under 2 seconds per decision
- **cost:** moderate API cost for real-time vision model usage; hardware read/write minimal increase
- **security:** Requires owner's explicit consent for screen capture and interaction to avoid privacy breaches; clear indicators and audit logs needed.
- **missing:** ui_hierarchy_snapshot context access; consented and enabled pixel capture and input loop; safe access control mechanisms for visual input automation

### "Have the mac-vision agent generate detailed, human-readable explanations of each UI automation step taken, with the ability to replay or undo them on demand."
- **useful because:** This would boost owner confidence and understanding, making complex automated workflows transparent and correctable and facilitating debugging and learning.
- **path:** mac-vision → mac-planner → web-dashboard
- **model tier:** realtime
- **latency:** under 2 seconds to generate explanation per step
- **cost:** low to moderate additional cost per step for explanation generation and storage
- **security:** Explanations must be locally stored and protected to avoid leak of sensitive UI context.
- **missing:** Action history logging integrated with explainability generation; UI for playback and undo of past automation steps


## Changes it proposed to its own stack

### `hardware` — Upgrade the MacBook wearable pendant hardware to include a dedicated low-power edge TPU or neural engine optimized for real-time vision processing of Mac screen captures and UI element detection locally on the pendant before sending info to the Mac agent.
- **owner gets:** This hardware enhancement would allow low-latency, real-time UI analysis and decision support even when the Mac is under heavy load or offline, and reduce cloud API usage and latency by offloading vision processing to the pendant.
- effort: Moderate hardware redesign and software integration effort.  ·  risk: Increased power consumption could reduce battery life; risk of delayed integration and testing resources.
- cost: Moderate increase in component cost and power draw on the pendant; cost offset by reduced cloud usage.  ·  latency: Lower latency for vision tasks, from multiple seconds down to milliseconds locally on the pendant.
- security: Local processing protects privacy better by avoiding raw screen data transmission; however, stronger hardware security required to prevent local data leaks.
- depends on: Complete pixel-level screen capture and input loop capability on Mac; Improved vision models tuned for UI detection on the pendant

### `mac-harness` — Develop a typed, capability-based action broker for the mac-vision agent that classifies all UI automation actions into read-only, reversible local mutations, or high-impact mutations with explicit one-time confirmation paths as fallback.
- **owner gets:** This improves safety and user trust in the mac-vision agent by preventing unintentional destructive actions and providing transparency with undo and confirmation mechanisms.
- effort: Significant engineering effort to implement classification and broker logic with user-facing confirmation UI.  ·  risk: Owner resistance to frequent confirmations could reduce utility; balancing automation and control is delicate.
- cost: Low to moderate developer time and additional UI complexity without significant runtime cost.  ·  latency: Minimal added latency, mostly in UI confirmation dialogs.
- security: Enhances security by gating high-impact changes, reducing accidental or malicious destructive actions.
- depends on: Full control over UI action classification from accessibility and pixel-level input layers

### `relay` — Add robust multi-agent coordination protocols in the relay to synchronize state, share UI context and partial results, and orchestrate layered action plans between mac-vision, mac-planner, browser-extension, and pendant in real time.
- **owner gets:** This would enable seamless collaboration across agents on different devices and platforms, improving reliability, responsiveness, and task completion capability beyond isolated agents.
- effort: Substantial development for real-time messaging, state sharing, and conflict resolution.  ·  risk: Increased system complexity and potential for synchronization bugs, latency spikes.
- cost: Higher cloud compute and bandwidth usage for coordination messages.  ·  latency: Potentially slightly higher coordination latency but better overall task flow.
- security: Requires strong authentication and encryption to prevent interception or spoofing.
- depends on: Common protocol definition for UI and task state; Enhanced relay infrastructure support

### `memory` — Create a compact, typed context projection system that filters and prioritizes live and historical Mac UI states, task goals, and permissions per mac-vision job, optimizing prompt token usage and response relevance.
- **owner gets:** Improves response quality and efficiency by supplying only relevant context to mac-vision's model at execution time, reducing overload and irrelevant detail.
- effort: Moderate engineering to adapt context compiler and projection for UI automation domain.  ·  risk: Incorrect context filtering risks missing critical info or confusing the model.
- cost: Some computational overhead for filtering but overall cost saved on model input tokens.  ·  latency: Reduced prompt construction latency, faster model responses.
- security: Must carefully handle permission scoping and sensitive context data.
- depends on: Typed context service implementation; Integration with mac-vision prompt builder


## What it asked for

_Nothing._
