# Harness derivation — mac-vision — round 107

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `firmware` — Add local encrypted image buffer and real-time vision accelerator coprocessor on the pendant to allow offloading screen pixel analysis with zero cloud leakage and minimal latency for mac-vision UI loops.
- **owner gets:** Enables fast, privacy-preserving, local image processing for complex UI automation on the Mac without exposing screen captures to the cloud or causing delays that break interaction timing.
- effort: Significant hardware design and firmware development effort requiring new chip integration and system software support.  ·  risk: Hardware or firmware bugs could lead to missed or incorrect UI actions; mitigated by fallback to accessibility API and extensive testing.
- cost: Increased hardware cost by approximately $30-$50 per pendant unit; minimal extra power draw due to efficient accelerator design.  ·  latency: Reduces end-to-end UI interaction latency by 50-70% compared to cloud-based processing.
- security: Improves security by never transmitting raw screen pixels outside local device and encrypting image buffer at rest and in transit internally.
- depends on: Permission to enable computerUse.loopEnabled; Permission for visionUploadConsented; Software support for mac-vision image and UI context integration

### `integration` — Develop a typed UI interaction model integration layer that combines accessibility API snapshots, pixel-based UI image analysis, and mac-vision intent reasoning for precise, safe, and context-aware UI control on the MacBook.
- **owner gets:** The owner gains a reliable and intelligent UI control system that bridges API-only limitations and raw pixels, allowing complex automation and interaction with modern and legacy Mac applications.
- effort: Moderate to high software engineering effort to combine multiple data sources, train and validate UI intent models, and build robust error handling.  ·  risk: Misinterpretation of UI states or intent can cause incorrect or disruptive actions; mitigated by layered fallback and confirmation policies.
- cost: Mostly engineering cost; potentially moderate cloud or local compute costs for model inference.  ·  latency: May add slight processing delay but remains under acceptable real-time interaction thresholds.
- security: Requires careful handling of UI data with user consent, encryption, and minimizing data retention.
- depends on: computerUse.loopEnabled permission; visionUploadConsented permission; firmware support for image processing on device

### `context` — Establish comprehensive, real-time context sharing among pendant, MacBook, browser extension, and relay agents to synchronize UI state, user intent, and confirmation dialogs for seamless multi-surface computer control.
- **owner gets:** Allows intelligent delegation of UI control tasks to the best-suited agent surface, enabling fluid transitions between wearable, Mac, and browser environments with consistent user experience and error handling.
- effort: Moderate development effort to design context schema, synchronization protocols, and implement real-time updates with conflict resolution.  ·  risk: Incorrect or stale context could cause UI action errors or conflicting commands; requires robust validation and rollback mechanisms.
- cost: Mainly software development cost; minimal run-time resource impact due to event-driven context updates.  ·  latency: Minimal latency impact with efficient protocols.
- security: Sensitive context data must be encrypted and access-controlled; user consent required for cross-device sharing.
- depends on: Permissions for context sharing; Underlying communication and synchronization infrastructure


## What it asked for

_Nothing._
