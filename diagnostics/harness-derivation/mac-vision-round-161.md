# Harness derivation — mac-vision — round 161

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable fully autonomous computer control on the Mac through mac-vision, without needing screen recording consent, by obtaining just the macOS Accessibility grant for the AI Pendant Agent binary, so mac-vision can read the accessibility tree and safely manipulate the UI in a reversible way."
- **useful because:** Today the computer-use loop on Mac is disabled and cannot act. Granting macOS Accessibility specifically to the AI Pendant Agent binary enables full screen-independent UI automation, allowing the system to perform complex multitasking on the owner's Mac without focus theft or pixel captures, dramatically enhancing productivity and safety.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-4.1-mini
- **latency:** Live low-latency feedback and action in seconds.
- **cost:** Negligible API call cost; main cost is engineering and user onboarding for permission grant; no ongoing compute cost.
- **security:** The Accessibility grant allows deep UI automation. Requires owner trust and explicit user consent via macOS security settings UI. Does not share screen pixels externally, maintains privacy, and falls back to no action if the grant is revoked.
- **missing:** Owner manually granting Accessibility permission to "AI Pendant Agent" binary.; Policy UI or onboarding flow to guide owner through macOS Accessibility grant process.

### "Provide a unified task management and prioritization framework that aggregates hand-typed task facts, live reminders, calendar events, and briefs, ranks them by topical priority and deadline sensitivity, and surfaces them actively to the owner via all surfaces including mac-vision."
- **useful because:** Currently, the system lacks integrated understanding of what the owner truly wants done. By unifying different task stores into a live, rankable task list with priorities and timelines, agents can focus actions on the most important work, and the owner receives concise, relevant prompts across devices.
- **path:** mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** Mixed, mostly background ranking and real-time fetching for active use.
- **cost:** Moderate API call cost for ranking and aggregation; models can batch decisions efficiently.
- **security:** Task data contains sensitive personal information. Requires strong local encryption and user control over sharing and deletion.
- **missing:** Cross-surface task store integration.; Automatic task extraction from memos, emails, and briefs.; Ranking algorithm tuning and owner preference input.

### "Implement a fine-grained, transparent UI action classification and confirmation system integrated with mac-vision, mac-planner, and relay-realtime, that classifies every attempted computer action as read-only, reversible local mutation, or high-impact mutation, and requires explicit owner approval only for the high-impact mutations using the pendant button's physical_transaction_approval_latch."
- **useful because:** This system would provide strong safety guarantees that protect the owner from unintended harmful actions by the AI agents while maintaining seamless automation for safe actions. It balances maximum access with owner control and trust.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second for classification and staged approval before execution.
- **cost:** Low to moderate, mostly engineering complexity; adds small user interaction overhead; use existing button gestures for confirmation.
- **security:** Explicit owner approval for high-impact actions secures the system. Risk is mitigated by strict classification and ability to undo reversible actions.
- **missing:** Detailed UI action taxonomy and classification map.; Integration hooks in mac-vision and mac-planner for pre-execution classification and prompt.; User UI flow for informing owner during approval stages.

### "Create a multi-modal, multi-tier context sharing protocol across mac-vision, relay-realtime, mac-planner, browser-extension, and pendant to share UI state, user intents, task focus, and memory graph updates securely and in real-time, enabling seamless collaboration of all agents on the owner's current goal."
- **useful because:** Currently, context sharing is limited and fragmented across surfaces, reducing coordination quality and forcing redundant work or guesswork. A unified protocol with tiered fidelity (e.g., accessibility trees on Mac, briefs on relay, browser tabs state) enables precise shared understanding, task handoff, and richer contextual assistance.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Real-time or near real-time for active session contexts; background sync allowed for memory graphs.
- **cost:** Moderate ongoing API and engineering cost; network and CPU overhead balanced by selective fidelity and caching.
- **security:** Highly sensitive data transmitted; must use strong encryption, strict access control, owner consent for upload and storage, and minimal external exposure.
- **missing:** A common context data schema supporting UI, intent, task, and memory facts.; Middleware to translate and sync data across heterogeneous surfaces and layers.; Owner controls on data sharing granularity and revocation.

### "Create a local ephemeral UI hierarchy snapshot service on the Mac that integrates with the mac-vision loop, giving other agents and the owner non-pixel, detailed UI state insights for better decision making, accessibility commands, and presentation of pending tasks, without requiring screen recording consent."
- **useful because:** This would provide rich UI context without privacy-invasive screen captures, enabling better automation, debugging, and accessibility interventions. It respects user privacy while unlocking powerful gaze-free computer operation and UI awareness.
- **path:** mac-vision → mac-planner → dashboard
- **model tier:** gpt-4.1-mini
- **latency:** Sub-second response to interactive requests.
- **cost:** Negligible API cost; local compute and memory usage limited by accessibility API performance.
- **security:** Does not capture pixels, minimizing privacy risk; requires macOS Accessibility grant specifically for the AI Pendant Agent binary.
- **missing:** Permanent enablement of macOS Accessibility grant.; UI hierarchy snapshot and event streaming APIs.; Security review and privacy policy documentation.


## Changes it proposed to its own stack

### `hardware` — Design and build a second user button on the pendant to provide a richer and dedicated physical gesture vocabulary, which is currently limited to a single button with only simple press/end press semantics.
- **owner gets:** The single button on the pendant limits the ability to assign different physical gestures and triggers for diverse commands and confirmation sequences. A second button would enable more natural and varied interactions, improving usability, reliability, and reducing gesture conflicts.
- effort: Medium hardware and firmware engineering effort to redesign the pendant enclosure, PCB, and firmware changes to support and safely multiplex interrupts from two buttons.  ·  risk: Additional button could increase power consumption slightly and add one more physical failure point; firmware complexity increase; must maintain backward compatibility and user education.
- cost: Moderate increase in BOM cost and power draw.  ·  latency: Negligible impact on latency.
- security: No direct impact, but permits richer physical security gestures or confirmations.


## What it asked for

_Nothing._
## Its own summary

Proposed six major capabilities and one hardware change to enhance the owner's experience: enabling mac-vision loop with macOS Accessibility grant for safe UI control; unified task management with ranking; a second physical pendant button for richer gestures; a typed action broker for UI action classification and approval; a multi-modal context sharing protocol across agents; a local ephemeral UI hierarchy snapshot service for privacy-friendly UI state access.

**Biggest unknown:** Implementation and owner adoption of macOS Accessibility grant for the AI Pendant Agent binary is the single biggest unknown that gates many advanced computer use loop capabilities.

