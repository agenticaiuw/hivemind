# Harness derivation — mac-vision — round 59

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, reliable mac-vision loop for full UI-based control and observation on the Mac, combining accessibility and pixel tiers with minimal owner disruption."
- **useful because:** The owner should be able to automate complex, multi-step, UI- and pixel-dependent workflows on the Mac that APIs and browser extensions cannot reach today. This capability would combine the deep system knowledge of the Mac surface with the pendant voice control and always-on relay to orchestrate and observe every step, including fallback paths when UI elements move or states change.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** expensive low-latency model on mac-vision for UI interpretation and action, with lighter models on relay and Mac planner for orchestration and fallback
- **latency:** Real-time or near real-time reaction (under 1 second) to UI changes and voice commands
- **cost:** Moderate to high, bounded by UI interpretative complexity and frequency of use. Real-time pixel capture and analysis are dominant costs.
- **security:** High exposure: full screen recording and input control risks. Must have encrypted streams, strict logs, non-interference with owner typing except when explicitly requested, and owner review of action receipts. Accessibility and screen recording permissions required with fallback safe modes.
- **missing:** Full and reliable Accessibility and Screen Recording permissions enabled with owner-granted trust; A typed gating or audit layer for actions combined with transparent receipts without interruptive prompts; A mechanism to combine accessibility UI tree info and pixel screenshots for resilient, robust action decisions; Hardware or software features to virtually sandbox mac-vision scope during active use, preventing accidental destructive actions


## Changes it proposed to its own stack

### `hardware` — Add a dedicated camera or sensor on the MacBook chassis or nearby to capture screen images for the mac-vision agent without relying on software screen recording APIs. This hardware would enable pixel analysis while minimizing privacy impact and software trust risks.
- **owner gets:** This would allow mac-vision to operate with real-time visual input independent of macOS permissions and security restrictions, providing robust UI understanding and control without invasive software-level screen recording.
- effort: Moderate hardware design and firmware integration, plus system software to route secure camera feed to mac-vision securely.  ·  risk: Hardware failure or compromise could expose visual data, mitigated by encrypted transport and physical tamper evidence.
- cost: Additional component cost and power draw on the MacBook board estimated to be low to moderate.  ·  latency: Minimal latency impact; camera feed would be streamed directly to mac-vision process.
- security: Requires strict hardware-based encryption and isolation to ensure visual data confidentiality.

### `model-routing` — Implement a split model routing approach where the mac-vision loop uses a high-capacity computer vision and UI understanding model on the Mac for low-latency interactions, while offloading heavier reasoning, planning, and context enrichment tasks to the relay-realtime and mac-planner models.
- **owner gets:** This distributed model approach ensures efficient, fast, and responsive UI control locally, while leveraging cloud or more powerful Mac-based planning for complex workflows without overwhelming local resources.
- effort: Moderate software engineering to enable seamless context flow and model delegation among devices.  ·  risk: Potential synchronization issues or delay in context sharing; fallback needed for offline or degraded network scenarios.
- cost: Moderate increase in computational cost split across devices.  ·  latency: Improves latency at local UI-interaction while enabling richer processing remotely.
- security: Requires secure context sharing protocols and encrypted communication.
- depends on: Enable mac-vision loop for safe, fully accessible computer UI interaction

### `interaction` — Design a continuous owner feedback and override interface via the pendant that gives real-time summaries of mac-vision's planned UI actions and allows instant verbal or button override or correction before any destructive step.
- **owner gets:** This keeps the owner in control and informed without breaking flow, avoiding surprises or mistakes by allowing quick interventions, especially for sensitive or destructive actions.
- effort: Medium UI/UX design and integration with pendant voice and tombol interface; linking with mac-vision action receipts.  ·  risk: Owner might find frequent confirmations annoying; needs tuned defaults and learning from owner preferences.
- cost: Low to moderate, mostly software on pendant and Mac.  ·  latency: Minimal latency added by owner interaction steps.
- security: Improves security by preventing unauthorized or mistaken destructive actions.
- depends on: Enable mac-vision loop for safe, fully accessible computer UI interaction

### `context` — Expand and optimize real-time UI context sharing between mac-vision and relay-realtime to include rich semantic annotations of UI elements and current app tasks, enabling the owner to query or command the Mac through natural voice by referencing UI state explicitly.
- **owner gets:** This enables highly accurate voice control and understanding of complex UI-driven workflows and tasks, making Mac interaction seamless and intuitive even for deeply nested or dynamic app states.
- effort: Medium software development for UI semantic extraction, context serialization, and voice interface integration.  ·  risk: Context overload or stale state if synchronization breaks down; requires robust updating and error handling.
- cost: Moderate due to continuous semantic context extraction and transmission.  ·  latency: Needs careful tuning to keep voice interactions immediate and fluid.
- security: Sensitive UI state info requires encryption and access control.
- depends on: Enable mac-vision loop for safe, fully accessible computer UI interaction

### `firmware` — Develop firmware capabilities on the pendant to preprocess and summarize UI and interaction data streams from mac-vision before sending to relay or Mac-planner, reducing bandwidth and latency for UI state feedback and voice control loops.
- **owner gets:** This enables faster, more efficient communication between devices, allowing more responsive and reliable voice and UI interaction control with less power and data use on the wearable pendant.
- effort: Moderate embedded firmware development and integration work.  ·  risk: Firmware bugs could degrade experience or cause partial data loss, mitigated by robust testing and fallback strategies.
- cost: Minimal hardware cost, mostly engineering effort.  ·  latency: Reduces latency in multi-device coordination.
- security: Must ensure data is processed securely and private info is not leaked.
- depends on: Enable mac-vision loop for safe, fully accessible computer UI interaction

### `integration` — Create an integration layer that synchronizes and coordinates UI automation intents and results between mac-vision, browser-extension, mac-planner, and relay-realtime, ensuring consistent task state and avoiding duplicated or conflicting actions across Mac UI, browser, and voice surfaces.
- **owner gets:** This integration makes multi-surface, multi-device workflows seamless, so the owner can transition fluidly between voice commands, UI automation, and browser tasks without losing context or causing errors.
- effort: Medium to high software engineering effort to build a robust synchronization protocol and conflict resolution system.  ·  risk: Potential state drift or conflicts if synchronization fails; requires strong consistency and recovery mechanisms.
- cost: Moderate compute and development cost spread across devices.  ·  latency: Requires low-latency sync to maintain smooth interaction experience.
- security: Sensitive task state data must be protected and access-controlled.
- depends on: Enable mac-vision loop for safe, fully accessible computer UI interaction


## What it asked for

_Nothing._
