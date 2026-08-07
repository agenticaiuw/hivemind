# Harness derivation — mac-vision — round 63

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Context-aware UI assistance that can interpret and interact with the Mac UI elements using accessibility APIs, without interrupting the owner’s workflow or requiring visual screen capture."
- **useful because:** This allows detailed task automation and assistance while respecting user privacy and focus, enabling the owner to get help on complex tasks seamlessly.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini for UI understanding and inference
- **latency:** real-time to a few seconds interaction
- **cost:** Low to moderate, depends on the number of UI queries and interactions
- **security:** Strict privacy controls to prevent unauthorized UI data access or actions
- **missing:** high-resolution and reliable accessibility snapshots; advanced UI interpretation models


## Changes it proposed to its own stack

### `hardware` — Upgrade the pendant hardware to support local vision processing with low-power AI chips, enabling offline UI snapshotting and safe pixel capture to assist mac-vision without risk to privacy or delay from cloud roundtrips.
- **owner gets:** This gives mac-vision a safe source of up-to-date screen pixels for fine-grained UI understanding and action without privacy risks or latency of current cloud-based image processing.
- effort: Significant, hardware development and integration plus firmware changes  ·  risk: Device complexity and power consumption increase; fallback needed if feature fails
- cost: Moderate increase in component cost and power draw  ·  latency: Decrease in end-to-end UI action latency due to local processing
- security: Improves privacy by keeping pixels local

### `firmware` — Implement a secure, consent-driven toggle and policy enforcement mechanism in the pendant and Mac agent firmware that controls when mac-vision loop and pixel upload are enabled, incorporating explicit user approval flows and detailed audit trails for transparency.
- **owner gets:** This ensures owner trust and compliance with privacy preferences, enabling powerful mac-vision automation only when the owner explicitly consents and can review activity.
- effort: Moderate firmware and software development  ·  risk: Increased complexity in UX and failure modes if user denies consent or toggling misbehaves
- cost: Minimal  ·  latency: Negligible
- security: Strong positive impact on privacy and security


## What it asked for

_Nothing._
