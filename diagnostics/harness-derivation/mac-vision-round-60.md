# Harness derivation — mac-vision — round 60

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `hardware` — Add a secure, dedicated vision co-processor and camera integration on the MacBook designed specifically for trusted local screenshot capture and real-time UI analysis by the mac-vision loop, minimizing performance overhead and privacy risk.
- **owner gets:** Improves mac-vision responsiveness, reliability, and privacy, enabling the loop to run continuously and safely without affecting normal Mac workload, and ensures all visual data is captured securely and cannot be intercepted or misused.
- effort: Medium to high engineering and hardware integration effort across firmware, OS, and hardware design.  ·  risk: Hardware integration delays or defects could affect shipment; increased power use but minimal if optimized; any security flaw may expose sensitive screen content, so needs strong hardware security.
- cost: Increased component cost and power draw but justified for reliable AI vision control.  ·  latency: Reduced latency for screen capture and analysis, improving real-time control responsiveness.
- security: Enhances security by isolating vision processing and restricting raw screen capture access to a secure enclave.

### `model-routing` — Introduce a hybrid model-routing system integrating a lightweight local model on the MacBook (like gpt-4.1-mini) for real-time low-latency decisions in the mac-vision loop with cloud-based higher-tier models (gpt-5.6-luna) for complex planning, multi-step task understanding, and risk assessment across surfaces. The coordination between models would optimize latency, cost, and reliability.
- **owner gets:** Allows mac-vision to operate responsively with safe fallback and collaborative judgement from more powerful cloud models, enabling complex task execution while maintaining local privacy and low latency for frequent small decisions.
- effort: Medium effort in model orchestration, local model deployment, and cross-surface communication design.  ·  risk: Complexity in routing and fallback logic might cause errors or delays that affect user experience. Network loss requires graceful degradation to local-only mode.
- cost: Reduced overall cloud costs by offloading routine decisions locally while using cloud only for complex tasks.  ·  latency: Significant latency improvement for small, frequent decisions with local model presence.
- security: Improves security by limiting cloud data exposure to only complex or aggregated task info.
- depends on: hardware

### `mac-harness` — Build a comprehensive mac-vision harness integrating accessibility APIs with advanced image recognition and pixel-level analysis to form a robust perception system that can observe UI structure and content reliably, even with dynamic or non-standard app UI components. Include undo support, action receipt logs, and user confirmation flows at the harness layer to enable safe autonomous control loops.
- **owner gets:** This would enable mac-vision to interact with complex Mac app UIs beyond static API calls, adapt to various apps or custom UI frameworks, and maintain a full audit trail for owner peace of mind and error recovery.
- effort: High engineering effort in macOS accessibility integration, pixel analysis, and undo architecture, plus UI/UX design for confirmations.  ·  risk: High complexity with potential edge cases and false UI reads, requiring robust error handling. Undo and confirmation flows must be clear and reliable to avoid confusion.
- cost: Engineering cost but no direct extra operational cost.  ·  latency: Increased initial processing latency but amortized by reliability gains.
- security: Requires strict privilege management to prevent unauthorized UI access or input injection.
- depends on: hardware

### `integration` — Integrate the mac-vision loop with the owner's personal AI hive mind network to share UI state context, action plans, and confirmations across surfaces (pendant, MacBook, browser extension). Enable relay-realtime and faculty-judgement to provide continuous feedback, risk assessment, and owner interaction for safe, coordinated, and context-aware UI control.
- **owner gets:** Ensures mac-vision loop's actions on the MacBook align with the owner’s overall intents and current context across devices, increases safety by leveraging other surfaces for oversight and fallback, and allows owner to interact or override via wearable pendant.
- effort: Medium to high effort in cross-surface communication, shared state synchronization, and secure identity management.  ·  risk: Potential communication delays or state sync issues could cause inconsistencies or conflicts; requires strong encryption and access controls.
- cost: Moderate operational cost due to cross-surface networking.  ·  latency: Coordination delays could add small latency but overall improves decision quality and owner control.
- security: Requires strong end-to-end security to prevent interception or unauthorized control across devices.
- depends on: mac-harness; model-routing

### `dashboard-ux` — Design an owner-facing dashboard UI integrated with the Mac and pendant surfaces showing mac-vision loop activities, proposed actions, confirmation requests, undo options, and a history log of all autonomous UI actions taken or suggested. Include privacy and permission toggles to enable or disable computerUse.loopEnabled and granular control over UI interaction types.
- **owner gets:** This dashboard would provide transparency and control to the owner over the autonomous Mac UI interactions, boosting trust and allowing quick recovery from mistakes or undesired actions.
- effort: Medium effort for UI/UX design, cross-device sync, and integration with existing system monitoring tools.  ·  risk: If the UI is overly complex or intrusive, the owner may be deterred from trusting or using the AI.
- cost: Some operational and development cost for synchronization and UI rendering.  ·  latency: No direct latency impact on control loops, but provides clear user feedback.
- security: Must enforce strict authentication and authorization to protect sensitive activity logs and control toggles.
- depends on: integration

### `memory` — Implement a short-term memory cache for mac-vision loop containing recent UI states, action results, owner confirmations/rejections, and undo history to optimize local decision accuracy and reduce repeated visual processing.
- **owner gets:** This memory cache would speed up mac-vision loop reactions, improve reliability by referencing recent context, and enable more fluid multi-step interactions with undo and error correction.
- effort: Medium engineering effort for local cache implementation, expiration policy, and integration with loop decision logic.  ·  risk: Memory inconsistency or stale data could cause inappropriate actions without robust invalidation logic.
- cost: Minimal additional cost, mostly developmental.  ·  latency: Improves latency by avoiding redundant visual processing and analysis.
- security: Must secure memory storage to prevent corrupted or manipulated cached data from affecting control decisions.
- depends on: mac-harness


## What it asked for

_Nothing._
