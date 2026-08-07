# Harness derivation — mac-vision — round 141

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask you to do something that takes time, keep working after I leave and tell me exactly what happened when it’s done."
- **useful because:** Allows long-running tasks on the Mac or browser to continue after the owner stops actively watching, improving productivity and reducing the need for constant supervision.
- **path:** mac-planner → relay-realtime
- **model tier:** background
- **latency:** minutes to hours depending on task size
- **cost:** Moderate to high, depending on task complexity and duration; backend resources needed for durable job tracking.
- **security:** Ensure task outcomes are securely reported and owner-approved before any actions with side effects; limit scope and access to prevent unwanted persistent processes.
- **missing:** Durable job queue infrastructure; Notification when tasks complete; Owner approval workflow for task results

### "Allow mac-vision to safely take pixel-based screenshots and use computer vision to understand any UI element when accessibility APIs are insufficient, enabling robust automation of visually complex or custom UI elements."
- **useful because:** Accessibility APIs sometimes cannot reach custom or complex UI components. Pixels and computer vision can bridge this gap, allowing mac-vision to help automate all UI tasks practically and reliably.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 500ms
- **cost:** Higher cost due to vision model usage and pixel processing
- **security:** Screenshots and visual data must be carefully guarded to respect privacy; vision processing should happen locally or with strong encryption; explicit owner consent must be required.
- **missing:** Permission for visionUploadConsented; Integration of vision model usage and pixel UI element recognition into mac-vision loop

### "Provide a detailed human-readable and machine-verifiable audit log of every automated UI action mac-vision takes, with undo and redo support, accessible to the owner at any time."
- **useful because:** This gives the owner confidence and control over automation by allowing them to review what the AI did, understand it, and revert any unwanted changes safely.
- **path:** mac-vision → mac-planner → dashboard
- **model tier:** realtime
- **latency:** under 1 second per query
- **cost:** Moderate, requires storage and processing to maintain logs and support undo/redo
- **security:** Logs must be secure and private; undo must not cause data loss or corruption; audit logs must have tamper resistance.
- **missing:** Infrastructure to create, store, and query detailed action audit logs; Undo/redo system integrated with mac-vision automation

### "Automatically detect context switches in the Mac UI and pause or adjust mac-vision's behavior accordingly to avoid accidental inputs or interference."
- **useful because:** This capability would prevent mac-vision from automating UI actions during times when the owner is actively using the Mac for unrelated tasks, preserving user control and reducing errors.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 100ms
- **cost:** Low operating cost, mostly local event monitoring
- **security:** Must only observe UI state without capturing sensitive data; no data leaves the device for this purpose.
- **missing:** Event-driven UI context awareness and integration with mac-vision's automation loops

### "Create a secure personal knowledge graph on the Mac that maps UI elements, their states, and relationships over time to enable mac-vision to reason more effectively about UI automation and avoid repetitive or conflicting actions."
- **useful because:** A knowledge graph would provide persistent memory and reasoning support for mac-vision, enabling more intelligent, context-aware and less error-prone automation of the Mac's UI.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds for updates, realtime for queries
- **cost:** Moderate due to data storage and graph maintenance
- **security:** Data must be securely stored and encrypted, accessible only by authorized processes; respect privacy by limiting UI element data to controls only.
- **missing:** UI state extraction tools, persistent knowledge graph storage and query engine integration


## Changes it proposed to its own stack

### `hardware` — Add a dedicated AI vision coprocessor to the pendant or Mac device to enable low-latency, private computer vision processing for mac-vision automation without relying on cloud or the main CPU.
- **owner gets:** It would allow mac-vision to process UI visuals efficiently and privately in real time, enabling pixel-based automation even if the main system is offline or busy, improving responsiveness and privacy.
- effort: Major engineering and hardware design effort, including chip development and integration.  ·  risk: Hardware delays or malfunction could impact AI responsiveness; hardware could become obsolete; requires good fallback to software vision.
- cost: Significant upfront hardware cost but low operational cost after deployment.  ·  latency: Greatly reduced latency for vision tasks compared to cloud or main CPU.
- security: Improved privacy by localizing vision processing; introduces physical hardware security considerations.


## What it asked for

_Nothing._
