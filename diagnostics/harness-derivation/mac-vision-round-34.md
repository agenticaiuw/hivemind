# Harness derivation — mac-vision — round 34

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Turn on the full computer-use loop on the Mac, with reliable and trustworthy visual UI automation"
- **useful because:** The owner would gain the ability to have the AI agent perform complex UI tasks on the Mac involving pixel-level control and interactions that APIs cannot achieve, such as clicking on arbitrary screen elements that are not addressable through accessibility alone. This would greatly enhance automation and task completion efficiency.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** gpt-4.1-mini for immediate perception and judgement, with fallback to gpt-5.6-luna for complex planning
- **latency:** Low latency (under 1 second) for perception/action cycles
- **cost:** Moderate API use dominated by repeated visual processing of screenshots and UI tree parsing
- **security:** Would require explicit macOS system permissions for Screen Recording and Accessibility trusted by the AI agent binary, plus fallback typed action approval workflow or post-action receipt checking to avoid silent failures and user confusion.
- **missing:** macOS Screen Recording permission and Accessibility permission granted and aligned with agent binary; Robust UI action receipt and verification system that guarantees action took real effect; Typed action policy wrapper to classify and gate or confirm high-risk UI mutations; Better integration with other surfaces for fallback when pixel-level automation is not possible

### "Enable a robust typed action broker on the Mac to classify computer actions as read-only, reversible mutations, or high-impact mutations, with optional owner confirmation for risky actions"
- **useful because:** This would allow safe and semantically rich computer control by the AI, limiting risks from unintentional or damaging automated effects. It allows observability, control, and owner peace of mind for powerful automation.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for judgement and planning, with gpt-4.1-mini for real-time UI perception
- **latency:** Moderate latency acceptable for judgement and confirmation (seconds)
- **cost:** Low API cost, mostly planning and classification
- **security:** Requires implementation of precise typed action schema and binding to underlying UI actions; approval logic must be transparent and auditable.
- **missing:** Typed action specification and schema; Typed action enforcement and broker system; User interface for action confirmation and review

### "Allow the agent to perform limited pixel-free UI navigation and interaction purely via macOS accessibility APIs with fallback verification from UI tree state"
- **useful because:** This enables safer, less intrusive automation of many UI tasks on the Mac when full Screen Recording permission is not granted. It expands the range of automatable tasks without compromising privacy or security.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** gpt-4.1-mini for immediate UI navigation, gpt-5.6-luna for fallback judgement
- **latency:** Low to moderate latency (sub-second to a few seconds)
- **cost:** Low cost, mostly logical tree-based operations
- **security:** Lower risk than pixel-based automation as it avoids screen recording and sensitive data capture.
- **missing:** Improved robust UI tree state parsing and action receipt for accessibility-only mode; Fallback error-handling and state re-synchronization mechanisms


## Changes it proposed to its own stack

### `hardware` — Add a dedicated, secure, and user-consented hardware-level Screen Recording permission mechanism and UI action event receipt system in the Mac pendant or bridge chip that can override macOS limitations and provide verified UI automation action outcomes.
- **owner gets:** This hardware-level integration would allow the AI to reliably perform and confirm pixel-based interactions on the Mac despite normal OS restrictions, enabling high-trust automation of complex tasks without relying solely on the operating system's permissions model.
- effort: High engineering effort involving firmware, hardware interface design, and OS integration.  ·  risk: Possibly invasive if misused, but mitigated by user consent and hardware isolation.
- cost: Moderate component and firmware development cost; negligible power impact on the pendant or bridge.  ·  latency: Minimal, operating at the hardware interface layer.
- security: Requires strict access control and user consent mechanisms.

### `integration` — Integrate the typed action broker tightly with the owner-facing interface on the pendant and macOS agent to provide real-time confirmation prompts and action receipts, leveraging existing low-latency relay-realtime and faculty-action components.
- **owner gets:** The owner can safely and confidently delegate complex, multi-step computer tasks to the AI with a clear, low-latency interaction loop and visible receipt of actions taken, reducing the risks of unintended changes.
- effort: Medium, mainly software engineering and UI/UX work across multiple nodes.  ·  risk: Risk of increased latency or interaction complexity; mitigated by good UX design.
- cost: Moderate API and processing cost due to real-time confirmations.  ·  latency: Increased latency in confirmation but acceptable in typical conversational scenarios.
- security: Requires secure communication and verification protocols.
- depends on: Typed action broker implementation


## What it asked for

_Nothing._
