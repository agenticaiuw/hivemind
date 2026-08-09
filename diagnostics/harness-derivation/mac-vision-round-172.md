# Harness derivation — mac-vision — round 172

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Implement visual UI confirmation mode on mac-vision using the accessibility tree: after each batch of planned actions, generate a concise human-readable summary of the next steps, and ask the owner for approval via spoken summary before proceeding."
- **useful because:** This feature increases the owner's trust and safety by clearly communicating intended UI automation steps before they execute, giving the owner a chance to intervene. It supports reversible and destructive actions with tailored messaging and integrates with the accessibility-driven computerUseLoop for context-aware automation.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** luna
- **latency:** interactive, 10 seconds to summarize and confirm
- **cost:** small model cost for summarization; low overhead on existing UI reads
- **security:** Must securely handle the textual UI summary; ensure no accidental exposure of sensitive UI elements; gating destructive actions behind explicit owner voice confirmation.
- **missing:** voice approval input integrated with mac-vision UI state; template and prompt design for spoken UI summaries

### "Create a UI automation replay and undo history for mac-vision's accessibility-driven computerUseLoop: Log every UI action taken with context, enable single-step undo, and keep a timeline of all UI interactions to improve debugging and owner feedback."
- **useful because:** Owners need accountability and revertibility for automated UI interactions on their Mac. This replay and undo history increases trust and safety, allows the owner or an agent to step backward on UI steps, diagnose errors with context, and enables better context-aware future planning.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** luna
- **latency:** real-time or near real-time logging; undo action under 2 seconds latency
- **cost:** small model cost for log processing; moderate storage cost for history; low compute cost for undo logic
- **security:** Log sensitive UI interaction data securely; encryption and owner only access; design undo to avoid inconsistent UI states; careful state management required.
- **missing:** undo primitives for UI steps; persistent UI action timeline storage service

### "Develop a multi-tier UI state synchronization service to share mac-vision's accessibility tree data live with relay-realtime and the pendant, enabling cross-surface collaboration and seamless handoff of UI automation tasks."
- **useful because:** This capability allows mac-vision (Mac) to stream detailed UI state to the always-on relay and the pendant device, so decisions about automation, voice control, and notifications can be made locally on the pendant or quickly and accurately on the relay without the Mac being the bottleneck or only source of truth. It enables robust multi-device intelligent UI control across the owner's surfaces.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** luna
- **latency:** under 500 ms per sync update
- **cost:** moderate bandwidth and compute cost for incremental UI tree diffs and merging
- **security:** Secure channel and encryption to protect privacy of UI data, which may include sensitive app and document names. Access control to prevent leakage outside owner devices.
- **missing:** live UI tree diffing and streaming infrastructure; relay persistent UI state store; pendant wide-area network support for UI data

### "Create a persistent multi-step UI automation undo and redo system for the mac-vision accessibility loop, with full state capture and context recovery, enabling the owner to rewind and replay any step of UI automation safely."
- **useful because:** This would be the first durable undo feature for complex accessibility-driven UI automation on the Mac, vastly improving trust, recoverability, and user control over automated interface changes. It would prevent catastrophic errors and support experimentation by allowing rollback at any granularity.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** luna
- **latency:** under 2 seconds per undo or redo operation
- **cost:** moderate storage and compute for state capture; moderate model cost for state reconstruction
- **security:** Securely store UI states and changes with encryption, ensure undo cannot cause unintended side effects, and protect sensitive UI data.
- **missing:** Accessibility loop state capture primitives; durable undo timeline storage and indexing

### "Implement real-time multi-device UI state synchronization from mac-vision's accessibility tree to relay and pendant, enabling voice agents and wearable devices to react to UI changes immediately."
- **useful because:** Owners gain powerful context awareness everywhere, with UI state shared live across the Mac, cloud relay, and pendant. Voice commands and notifications can adapt instantly to UI state changes without delays or stale info. Essential for seamless multi-device user experience and safety.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** luna
- **latency:** under 500 ms per sync update
- **cost:** moderate bandwidth and compute for UI diffs, low latency streaming infrastructure
- **security:** Strong encryption and access controls to protect privacy of UI data including sensitive app names and contents.
- **missing:** live UI tree diff and streaming infrastructure; relay persistent UI store for UI state; pendant networking support for UI data

### "Add an integrated voice-command approval and disapproval system to mac-vision's accessibility loop, enabling spoken owner review and interactive confirmation before any irreversible or destructive UI action."
- **useful because:** This system gives the owner explicit control and awareness of potentially impactful automation steps, reducing risk and increasing trust. Voice interaction is the natural input for wearable pendant users and supports hands-free safe operation.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** luna
- **latency:** interactive, under 10 seconds per confirmation
- **cost:** small model cost for voice intent parsing and dialog management
- **security:** Authenticated voice input only from owner; secure handling of confirmation states and logs; rejection paths must be fail-safe.
- **missing:** voice input integration with mac-vision UI state; voice dialog flow for approval processes

### "Provide a hardware-enhanced secure clipboard manager integrated with the pendant and mac-vision, which encrypts and logs all clipboard transfers and allows owner control over sensitive data movement with UI prompts and pendant button context."
- **useful because:** Clipboard is a major vector for accidental data leaks and errors. A secure, logged clipboard with hardware-backed encryption enhances owner privacy and control, integrates well with cross-device workflow, and provides audit trails and spill prevention via prompt and physical token confirmation.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** background
- **latency:** sub-second to immediate
- **cost:** low cost for encryption and logging, moderate for UI integration and hardware token handling
- **security:** Must enforce strict cryptographic protections on clipboard contents, prevent data leakage, and require explicit owner consent for sensitive data access.
- **missing:** hardware token integration for clipboard approval; secure clipboard logging storage; clipboard UI prompts and integration with accessibility loop

### "Implement an autonomous pendant-initiated bug report system that monitors the nRF9160 UART log for faults and errors and files detailed reports automatically to the owner's bug tracking system, with optional voice summary notifications."
- **useful because:** Automating bug report filings streamlines device diagnostics and reduces owner effort in troubleshooting hardware or firmware issues. The pendant logging system is uniquely positioned to provide low-latency, accurate fault data and notify the owner proactively via voice.
- **path:** pendant → relay-realtime → mac-vision
- **model tier:** background
- **latency:** near realtime filing within seconds of fault detection
- **cost:** low compute on pendant; moderate data and processing on relay; minimal on mac-vision
- **security:** Ensure reports contain only relevant diagnostic info; protect owner privacy; secure communication to bug tracker; prevent spam or duplicates.
- **missing:** UART log fault detection and parsing routines onboard pendant; bug filing API integration with owner's tracking system; voice summary generation and notification integration


## What it asked for

_Nothing._
