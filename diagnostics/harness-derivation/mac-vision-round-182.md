# Harness derivation — mac-vision — round 182

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a durable, persistent browser job runner with retry and state streaming to the Mac agent planner, supporting both authenticated Safari sessions and the Cloudflare Browser Run for public pages."
- **useful because:** This will allow reliable and resumable browser automation jobs that continue after disconnections or restarts, correctly handle owner-private authenticated pages, and enable smoother multi-surface coordination.
- **path:** mac-planner → browser-extension → relay-realtime
- **model tier:** background
- **latency:** minutes
- **cost:** low HTTP and storage cost, amortized
- **security:** Authenticated browsing data must remain on the owner's device and not leak; retries must respect session cookies and tokens; privacy boundary enforced by the Safari bridge extension.
- **missing:** durable job runner implementation with local persistence; job result streaming and retry logic; voice path access to serverBrowser module

### "Create and maintain an authoritative prioritized goal store for the Mac-vision agent by writing 'task' kind facts to the memory service, allowing the owner and agents to state what should be done next with priority information."
- **useful because:** Currently, there is no reliable mechanism for the Mac-vision or other agents to know what the owner most wants done now. This would allow planners to make informed decisions and coordinate multi-step workflows across surfaces.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** minimal (HTTP storage calls)
- **security:** All task facts are owner-generated or agent-suggested with transparency; no sensitive data leaks as these are high-level goals; owner controls what is prioritized.
- **missing:** UI or voice input path for adding and updating tasks; policy or heuristic for task prioritization if desired

### "Implement end-to-end context-aware audio path management integrated with the nRF9160 pendant and the ESP32 audio bridge, supporting the owner's request to ship a 24 kHz superwideband audio streaming capability."
- **useful because:** This gives the owner high-quality real-time audio streaming with the pendant hardware, enabling clearer communication, voice commands, and feedback with minimal latency and artifact.
- **path:** pendant → bridge → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate embedded compute and system integration cost
- **security:** Handling raw audio securely to avoid unintended data leaks; ensuring integrity of audio transcoding and transmission; local on-device mixing and buffering reduces risk.
- **missing:** firmware and driver support to fully enable the 24 kHz superwideband path; software integration in the Mac agent to use and monitor the new audio path

### "Integrate the pendant's UART log file bug reporting into the system so the pendant can autonomously file bug reports from its own logs to aid owner troubleshooting and system reliability."
- **useful because:** This will allow proactive and automated bug diagnosis from the pendant device itself, helping the owner quickly identify issues and enabling more effective maintenance without manual log inspection.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** background
- **latency:** minutes
- **cost:** low storage and upload cost
- **security:** Logs must be sanitized or encrypted to avoid leaking sensitive information; owner control over when bug reports are sent; reliable handling of intermittent network connectivity.
- **missing:** firmware support for autonomous bug report generation and storage; relay and Mac agent ingestion and analysis pipelines

### "Develop an active confirmation gesture system using the pendant's existing single button to confirm high-impact or destructive actions initiated by the Mac-vision agent, avoiding false positives or delays."
- **useful because:** This leverages the physical button as a secure explicit approval method for critical commands, preserving the device's simplicity while improving safety and owner control over Mac UI automation.
- **path:** pendant → mac-vision
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** minimal firmware update cost
- **security:** Clear mapping of button press patterns to confirmation actions; avoid interfering with the existing conversation start/stop behavior; prevent accidental confirmations; preserve tactile feedback.
- **missing:** firmware support for multi-press or press-and-hold pattern recognition; integration with Mac-vision command authorization pipeline

### "Create a cross-surface task dependency and notification system that allows agents on the pendant, Mac, browser, and relay to coordinate multi-step workflows, notify the owner when work is blocked or completed, and recover from disconnections."
- **useful because:** This improves the reliability and intelligence of the entire AI hive mind by enabling agents to share stateful progress information, avoid duplicated effort, and bring coherent task status and next-action prompts to the owner regardless of which device they are using.
- **path:** pendant → mac-vision → browser-extension → relay-realtime
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low HTTP state sync and notification cost
- **security:** Strong consistency and conflict resolution needed to avoid task duplicates; respecting owner privacy in notifications; data encrypted and authenticated across devices.
- **missing:** a shared task state and event sync storage backend; agent coordination protocol and messaging enhancements

### "Allow the Mac-vision agent to perform fully reversible UI automation in background apps without focus theft or screen redraw, with zero reliance on pixel capture, through an advanced macOS Accessibility integration and custom AppleScript fallback for legacy apps."
- **useful because:** This capability would enable seamless, non-intrusive automation of macOS tasks in the background without disturbing the owner, avoiding the pitfalls of fallback clicks that steal focus or rely on fragile pixel operations.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds
- **cost:** none beyond development effort
- **security:** Requires strict macOS Accessibility permissions tightly scoped to preserve owner privacy and control. Fallback must not increase risk or break owner workflow.
- **missing:** Enhanced macOS Accessibility integration beyond the current AI Pendant Agent baseline; Fallback AppleScript scripts tailored for legacy or non-AX-compatible apps

### "Implement a smart context snapshot sharing system where the pendant captures accessibility tree snapshots alongside agent intent markers and syncs them to the Mac agent in real time, enabling more precise UI understanding and multi-agent collaboration without screen recording permission."
- **useful because:** This innovation avoids privacy-invasive screen recording while allowing richer UI context sharing needed for complex interaction, improving task accuracy and multi-agent coordination across devices.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** low network and storage
- **security:** Must enforce strict access control around sensitive UI data and agent intents; all data encrypted in transit and at rest; owner control over data sharing.
- **missing:** Real-time pendant to Mac context sync infrastructure; Agent intent marker APIs; Security and privacy model enhancements for UI data


## Changes it proposed to its own stack

### `hardware` — Add a small, dedicated physical gesture recognition chip or co-processor on the pendant to decode multiple user button press patterns (single, double, long press) without sacrificing mic powering or responsiveness.
- **owner gets:** This would enable a richer physical interaction vocabulary on the pendant without latency or power penalties, unlocking safer and more flexible control gestures for approval and mode switching.
- effort: medium firmware and hardware design effort  ·  risk: Manufacturing complexity and additional power draw; must safeguard against false positives and battery impact
- cost: moderate hardware cost increase  ·  latency: none or improved for gesture detection
- security: Improved security by offloading confirmation input and reducing risk of spurious commands


## What it asked for

_Nothing._
