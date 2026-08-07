# Harness derivation — mac-vision — round 61

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Automated, typed, reversible multi-step UI tasks on the Mac driven by vision and accessibility, with undo"
- **useful because:** Owners can delegate complex UI workflows involving multiple conditional steps and apps safely, with confidence that any mistakes can be undone fully, boosting productivity by automating repetitive or complex GUI tasks.
- **path:** mac-vision → mac-planner → faculty-action → relay-realtime
- **model tier:** gpt-4.1-mini for detailed vision work, gpt-5.6-luna for planning and action
- **latency:** Moderate latency due to multi-step planning, but with partial immediate feedback
- **cost:** Higher API usage due to multi-step reasoning and undo log storage
- **security:** Reversible typed actions are mandatory, with strict postcondition checks after each step, action receipt logs stored securely, and undo fully supported by cross-surface coordination.
- **missing:** Typed structured action workflow patterns not currently implemented; Undo and rollback supported by durable logs and cross-agent coordination; Vision-to-action verification step to detect UI changes and state consistency after each step


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure enclave chip on the MacBook to store and manage vision upload consents, accessibility and screen recording authorization tokens, and action receipts securely, accessible by the AI Pendant Agent only.
- **owner gets:** Enables trustable, verifiable and tamper-proof enforcement of permissions and consent specifically for the AI Pendant Agent's computer-use loop, making activation and ongoing use provably safe and under the owner's control.
- effort: Medium engineering effort involving firmware and driver updates with new hardware integration.  ·  risk: Hardware integration complexity, increased device cost, potential delays in OS and driver support.
- cost: Moderate increase in device cost; no direct API cost impact.  ·  latency: Negligible latency impact on computer-use loop operations.
- security: Strong improvement in security posture, reduces risk of unauthorized or accidental activation or data leakage.

### `firmware` — Implement a microscopic audit and control firmware layer that mediates and logs all UI automation commands from the AI Pendant Agent's mac-vision loop, to enforce typed preconditions, limit step counts, and provide immediate rollback or halt on errors.
- **owner gets:** This firmware layer ensures that all automated UI actions are constrained, reversible, and accountable before affecting the Mac, enabling a trustworthy and safe autonomous computer-use experience.
- effort: High firmware development effort with tight OS integration and coordination with AI Pendant Agent software.  ·  risk: Firmware bugs could cause spurious blocking or failure modes; rollback and fail-safe design are essential.
- cost: No direct API cost, but engineering effort is substantial.  ·  latency: Small latency added to each UI action for security checks and logging.
- security: Major security and safety enhancement, preventing unauthorized or excessive UI automation.
- depends on: hardware secure enclave chip proposal

### `dashboard-ux` — Create an owner dashboard interface specifically for monitoring and controlling the autonomous mac-vision loop activity, including detailed action logs, pre/postcondition states, manual intervention controls, and consent management for vision data uploads.
- **owner gets:** Gives the owner transparent visibility and direct control over the autonomous UI automation happening on their Mac, empowering informed decisions, trust building, and quick intervention if needed.
- effort: Moderate frontend and backend development effort to expose detailed loop data and controls in a user-friendly manner.  ·  risk: If poorly designed, could overwhelm the owner or cause confusion; must be simple and clear.
- cost: Modest ongoing API usage to fetch and display logs and states.  ·  latency: Minimal impact; dashboard operates asynchronously.
- security: Improves trust and security by exposing real-time information and controls to the owner visually.
- depends on: integration cross-surface sync

### `model-routing` — Establish a model tiering and routing strategy where low-latency, lightweight vision-driven UI parsing and accessibility queries run on a small model (gpt-4.1-mini) on the Mac (mac-vision), while heavy planning, disambiguation, and multi-step task orchestration run on a larger model (gpt-5.6-luna) on the Mac or relay, with clear boundaries and data pipelines.
- **owner gets:** Optimizes cost and latency by balancing fast local UI vision control and heavy remote planning and coordination, enabling responsive and efficient autonomous computer use.
- effort: Moderate engineering to partition tasks and data flows between model tiers, plus API orchestration.  ·  risk: Potential latency spikes if routing misfires; requires monitoring and fallback.
- cost: Reduces expensive model calls on heavier endpoints; overall cost optimized.  ·  latency: Improves responsiveness and throughput for typical UI tasks.
- security: Improves system robustness and reduces attack surface by minimizing heavy model exposure on the device.
- depends on: firmware UI control and logging layer; integration cross-surface sync


## What it asked for

_Nothing._
