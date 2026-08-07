# Harness derivation — mac-vision — round 93

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide intelligent fallback management when mac-vision cannot complete pixel-based UI actions"
- **useful because:** Sometimes pixel-based UI actions fail due to dynamic app states or unexpected UI changes. An intelligent fallback system would detect failure modes and retry or escalate via typed mac_run_actions or ask for human guidance, ensuring task success.
- **path:** mac-vision → mac-planner → faculty-judgement
- **model tier:** gpt-4.1-mini and gpt-5.6-luna
- **latency:** High priority retries within seconds, escalations asynchronously
- **cost:** Moderate system and compute usage for fallback logic.
- **security:** Fallback actions must be carefully authorized to prevent unintended side effects or privilege escalation.
- **missing:** Failure detection and reporting in mac-vision loop; Escalation paths to typed actions or human review; Integration with judgement and planner layers for decision making


## Changes it proposed to its own stack

### `integration` — Integrate mac-vision's pixel-based UI action loop with relay-realtime's live voice conversation and mac-planner's task planning to enable voice-directed UI automation across apps that have no API, with shared context and fallback to typed actions.
- **owner gets:** The owner can issue voice commands that trigger pixel-accurate UI operations on the Mac indefinitely, for apps and workflows lacking API support, all coordinated with planning and judgement layers for smart fallback and recovery.
- effort: Medium engineering effort to ensure robust, low-latency handoff and synchronization between surfaces and models.  ·  risk: Potential mismatch or overload of voice to UI actions causing unexpected UI state; mitigated by staged rollouts, monitoring, and undo capabilities.
- cost: Increased backend usage and networking for synchronization; moderate.  ·  latency: Low latency required for the UI loop; higher latency acceptable for planning and fallback.
- security: Increased attack surface for UI actions controlled by voice; requires secure authorization and monitoring.
- depends on: computerUse.loopEnabled=true; visionUploadConsented=true; undo and veto infrastructure; ui hierarchy snapshot context available

### `interaction` — Develop an assistive simulation mode for mac-vision that lets the owner observe and approve a sandboxed UI action plan before actual execution, reducing errors and building trust in pixel-based automation without immediate live action.
- **owner gets:** The owner can safely preview and adjust or veto pixel-level UI actions, increasing confidence in automation before any actual manipulation occurs, addressing safety concerns effectively.
- effort: Medium software engineering effort to build sandbox UI state replay and interactive confirmation workflows.  ·  risk: The simulation may differ from real UI state due to dynamic app content; mitigated by frequent context refresh and fallback options.
- cost: Moderate API and compute usage due to simulation environment.  ·  latency: Increased for actions but acceptable given safety gains.
- security: No additional security risk; simulation is read-only until confirmed execution.
- depends on: computerUse.loopEnabled=true; visionUploadConsented=true

### `context` — Enable continuous live UI hierarchy snapshot context streaming to mac-vision and mac-planner, allowing pixel-based and accessibility-based UI understanding to operate with the latest app state and reduce errors in action decisions.
- **owner gets:** Fresh UI context lets the mac-vision loop and planner make informed, accurate decisions on where and what to click or type, improving automation reliability and reducing mistaken actions.
- effort: Medium engineering effort to build efficient snapshot streams and integration.  ·  risk: Higher CPU and memory usage causing battery drain or performance issues; mitigated by throttling and selective snapshots.
- cost: Moderate resource consumption on device and backend.  ·  latency: Low latency needed for stream effectiveness.
- security: UI context contains sensitive data; must ensure encrypted and authorized access only.
- depends on: computerUse.loopEnabled=true


## What it asked for

_Nothing._
