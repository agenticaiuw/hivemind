# Harness derivation — mac-vision — round 139

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A pendant-based vision consent and status skill for the owner to grant and revoke screen capture permissions easily."
- **useful because:** This gives the owner immediate, clear, and physical control over the vision capture permissions that enable advanced Mac visual automation, improving trust and transparency.
- **path:** pendant → relay-realtime
- **model tier:** realtime
- **latency:** instantaneous response
- **cost:** minimal
- **security:** Sensitive user permission management; must clearly warn about privacy.
- **missing:** pendant firmware skill for vision consent UI and status; integration with Mac agent permissions

### "A combined multi-modal UI context broker that merges accessibility data with pixel-based vision and planner context to provide a rich UI state representation for mac-vision."
- **useful because:** This would enable mac-vision to make accurate, context-aware decisions about UI navigation and actions, overcoming limitations of either accessibility-only or pixel-only approaches.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate due to vision and context processing
- **security:** Access to detailed user interface information requires strong privacy controls.
- **missing:** multi-surface synch pipeline; advanced context integration models

### "Enable the mac-vision agent to proactively detect and recover from visual UI failures during complex Mac tasks, by invoking fallback strategies such as keyboard shortcuts, accessibility actions, or requesting help from the pendant."
- **useful because:** Visual interactions with Mac apps can be fragile due to changing UI layouts or unexpected popups. This capability would improve robustness and reduce owner frustration by adapting dynamically to UI anomalies.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate
- **security:** Must be cautious about fallback actions to avoid unintended destructive inputs and respect user privacy.
- **missing:** visual anomaly detection in UI automation; fallback strategy decision-making models

### "Enable owner-customizable visual UI automation macros that the mac-vision agent can record, edit, and replay on the Mac UI."
- **useful because:** Allows the owner to define and repeatedly execute complex sequences of UI interactions without deep technical knowledge, enabling personal automation workflows to save time and reduce errors.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** realtime
- **latency:** seconds to minutes depending on macro length
- **cost:** moderate due to storage and replay logic
- **security:** Macros can contain sensitive commands; must be carefully permissioned and editable by the owner only.
- **missing:** visual UI macro recording and replay system; user-friendly editing interface


## What it asked for

_Nothing._
