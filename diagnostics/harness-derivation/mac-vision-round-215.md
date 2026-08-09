# Harness derivation — mac-vision — round 215

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the owner to have a prioritized, dynamic Mac UI automation task queue that mac-vision can read, claim, and complete with feedback."
- **useful because:** Currently, mac-vision lacks a live, ranked list of real Mac UI automation tasks to act on, limiting its usefulness. Owner goals, reminders, and small tasks exist scattered and unstructured, preventing mac-vision from performing prioritized, multi-step UI interactions. This capability would give mac-vision a structured agenda for efficient, owner-meaningful work on the Mac GUI, improving automation and contextual awareness.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Seconds for short steps, minutes for multi-step workflows
- **cost:** Low per step; mostly model compute for planning and state reconciliation
- **security:** Requires access to UI state, user goals, and ability to issue UI actions safely. Needs confirmation for destructive or privacy-sensitive tasks. Must carefully manage focus and avoid disruption.
- **missing:** A structured, persistent store of Mac UI automation tasks with priorities and states; A mechanism to claim, update, and complete tasks from mac-vision; Integration with owner input and memory to supply tasks; UI state verification and claimed-vs-actual reconciliation support

### "Add claimed-versus-actual UI state verification and reconciliation to workbench context tracking for mac-vision."
- **useful because:** Currently no system can verify that UI automation actions have truly altered the Mac's screen and controls as intended. Adding claimed-vs-actual UI state reconciliation will improve reliability, allowing mac-vision to detect and recover from screen state mismatches, increasing owner confidence and automation success rates.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Subsecond to seconds for verification; longer for recovery workflows
- **cost:** Moderate, mainly model compute and accessibility tree processing
- **security:** Requires deep UI state reading and memory of intended states, potentially exposing sensitive screen content. Must be secured and access limited to authorized agents.
- **missing:** UI state snapshot and diff comparison for claimed-vs-actual verification; Fail-safe recovery workflows or error handling for mismatches; Persistence of intended UI states as claims; Integration with workbench context APIs and mac-vision interaction loop

### "Allow the owner to assign and approve high-level Mac UI automation policies that define when mac-vision can act autonomously versus requiring explicit confirmation, including for destructive or privacy-sensitive actions."
- **useful because:** Currently, mac-vision lacks fine-grained owner control over automation autonomy, making owner trust and safety uncertain. This policy capability would enable personalized, contextual automation permissions that dynamically control when actions proceed immediately or ask for approval, increasing comfort, security, and usability.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Policy decision latency subsecond; confirmation waits on owner input.
- **cost:** Low per decision; mostly model compute and UI dialog flow cost.
- **security:** Policy data must be private and tamper-resistant. Confirmation dialogs must be secure and clearly attributed to the owner.
- **missing:** A policy framework for safety and automation autonomy; Secure user confirmation UI integrated with mac-vision loop; Dynamic context-aware policy evaluation engine

### "Enable mac-vision to integrate live Mac application UI hierarchies with browser session state and owner context to perform seamless cross-application workflows involving GUI automation on Mac and web-based actions."
- **useful because:** Current system segments Mac UI automation and browser web automation as separate. Integrating these into a unified context and workflow allows tasks that span native Mac apps and web apps to be automated fluidly, enhancing productivity and reducing context switching for the owner.
- **path:** mac-vision → browser-extension → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Seconds for each cross-app step; minutes for multi-step workflows
- **cost:** Moderate, model compute for context integration and decision making
- **security:** Requires cross-application data sharing with strong privacy controls; user consent for browser extension control; prevention of unauthorized data leaks.
- **missing:** Cross-application UI and browser state unification APIs; Context sharing protocols between mac-vision and browser-extension; Coordinated action planning and state tracking across Mac and browser


## Changes it proposed to its own stack

### `hardware` — Add a dedicated hardware UI event verification sensor on the Mac pendant to capture physical feedback from UI interactions such as tactile, audio, or visual confirmation signals from the Mac for precise action verification without screen recording or invasive software hooks.
- **owner gets:** This would give the mac-vision system a hardware-anchored, privacy-preserving, real-world verification channel for UI automation actions, ensuring the Mac actually responded to input as intended even if software state is ambiguous or erroneous. It enhances accuracy and trust without compromising privacy.
- effort: Medium complexity hardware and firmware development, plus Mac-side driver and integration work.  ·  risk: Hardware integration risks; potential delays in firmware development; fallback needed if sensor fails.
- cost: Moderate hardware cost increase; low ongoing power impact; no network cost.  ·  latency: Near real-time verification with low added latency.
- security: Privacy-preserving by design; sensor data isolated and encrypted; no screen content captured.


## What it asked for

_Nothing._
## Its own summary

I discovered the key existing Mac control tools and that mac-vision can run accessibility-driven UI automation with granted permissions. The owner lacks a prioritized, persistent UI automation task queue, claimed-versus-actual UI state validation, cross-application workflow integration, and fine-grained autonomous action policies. I proposed capabilities to deliver these as transformative features beyond the current system, plus a hardware verification sensor. These would make mac-vision genuinely useful by enabling reliable, prioritized, and safe Mac GUI automation integrated with browser actions and owner preferences.

**Biggest unknown:** How cross-agent cooperation and owner input would realistically supply and prioritize the Mac UI automation task queue and how the new capabilities would be adopted by the owner.

