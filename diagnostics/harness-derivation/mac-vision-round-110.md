# Harness derivation — mac-vision — round 110

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a full typed action broker that mediates all interactions from the mac-vision loop with confirmation policies"
- **useful because:** Today, the mac-vision loop lacks any typed action broker that can classify each UI interaction by impact, confirm high-risk actions with the owner or judgement faculty, and provide an effective governance layer to prevent unexpected destructive actions or undesired mutations on the Mac UI. This governance is essential for safe and trustworthy operation when vision-based interactions are enabled.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for judgement, gpt-4.1-mini for action classification
- **latency:** Sub-second for classification and gating to avoid UX delays
- **cost:** Low to moderate, mostly model cost on server and some local compute for action classification
- **security:** This broker handles sensitive control decisions and must never leak private data. Policies must be clear, owner-approved, and stored locally if possible.
- **missing:** Typed action classification model for UI interactions; Confirmations workflow integrated with judgement faculty; Policy storage and configurable parameters for gating; Integration hooks into mac-vision’s action issuing

### "Provide a multi-surface collaborative context shuttle that merges visual UI state, typed action status, and owner intentions for all surfaces to use consistently"
- **useful because:** Currently, each surface and tool works in relative isolation with partial context. A unified context-shuttle that passes merged UI hierarchy snapshots, ongoing typed actions states, and spoken/typed owner intents cross-surfaces will improve accuracy, reduce errors, and enable more fluid delegation between surfaces.
- **path:** mac-vision → faculty-perception → faculty-judgement → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-5.6-luna for orchestration and merging
- **latency:** Sub-second to 1 second to keep interactions fluid
- **cost:** Moderate due to frequent merging and contextualization
- **security:** Must handle sensitive UI and intent data securely with end-to-end encryption and access controls
- **missing:** Context merge mechanism and protocol; Cross-surface incremental UI and intent sync; APIs for typed action state sharing


## Changes it proposed to its own stack

### `integration` — Build seamless integration between the typed action broker capability and existing mac_run_actions and mac_delegate tools, including a unified interface for action classification, owner/judgement confirmation, and action logging with receipts.
- **owner gets:** This change would make the typed action governance broker fully operational by connecting it directly to the existing execution tools, enabling safe and trusted Mac UI automation with oversight.
- effort: Medium, involves bridging existing tools, adding UI/UX for confirmation, and backend processing for logs and receipts.  ·  risk: If not implemented carefully, it could cause delays or block valid actions. Recovery involves fallbacks to manual intervention and detailed logging for audit.
- cost: Low to moderate from server compute and potential slight latency increase.  ·  latency: Minimal if optimized well, sub-second expected for gating.
- security: Increases control and auditability, reduces risk of unauthorized actions.
- depends on: Typed action broker capability proposed above

### `hardware` — Enhance the wearable pendant hardware with low-power dedicated vision processing chip and secure enclave for privacy-preserving real-time UI interaction approval prompts and consent confirmation.
- **owner gets:** This upgrade would allow the owner to quickly approve or deny Mac UI actions proposed by the visual AI loop without breaking their workflow or exposing sensitive information to network or external devices.
- effort: Significant hardware design and integration effort.  ·  risk: Hardware bugs or delays in consent might impact AI usability; fallback software consent needed.
- cost: Increased component and manufacturing cost, added power consumption.  ·  latency: Near-instant feedback on wearable pendant, reducing perceived lag.
- security: Improves privacy and control by limiting data exposure off-device.
- depends on: Typed action broker capability; Consent and privacy policy enforcement


## What it asked for

_Nothing._
