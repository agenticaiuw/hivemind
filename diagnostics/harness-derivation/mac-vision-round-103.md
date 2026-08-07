# Harness derivation — mac-vision — round 103

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full computer UI automation with intelligent typed action control for Mac use"
- **useful because:** The owner should be able to ask the Mac-vision agent to perform complex Mac tasks by combining pixel-based UI automation, accessibility UI queries, and typed action classification. This would unlock the full power of the Mac while ensuring safety by classifying every action as read-only, reversible, or high-impact with proper confirmations for destructive actions. The owner cannot have this today because the computer use loop is disabled and no typed action control layer exists.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** realtime low-latency
- **latency:** sub-second response for UI queries, few seconds for multi-step workflows
- **cost:** moderate API cost dominated by multiple action executions and UI snapshots
- **security:** actions potentially change device state; must require approval for destructive actions; visual data uploads require user consent
- **missing:** computer use loop enabled; vision upload consent; typed action classification and enforcement; UI hierarchy live snapshots; action confirmation prompts

### "Enable seamless multi-application workflows on the Mac by combining typed UI actions, vision-based recognition, and browser automation"
- **useful because:** The owner should be able to initiate workflows that span multiple applications (like copying data from a spreadsheet app to a web form, or extracting info from mail to create reminders) that require both screen understanding and diverse UI actions beyond a single tool's scope. This is not currently feasible due to isolated tool capabilities and lack of integrated vision.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** realtime low-latency
- **latency:** multi-second to minutes for longer workflows
- **cost:** high API cost, dominated by multiple action plans, UI snapshots, and vision processing
- **security:** Requires vision upload permission and strict typed action controls to prevent unintended damage; cross-app data handling must respect privacy and security
- **missing:** integrated vision and UI action coordination across Mac and browser; typed action classification and confirmation; multi-step workflow orchestration spanning different apps and tools


## What it asked for

_Nothing._
