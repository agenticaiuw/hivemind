# Harness derivation — faculty-action — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Before you do this risky thing, show me exactly how I can undo it, and only proceed if I approve.""
- **useful because:** The owner gets a trustworthy preview of consequences and a tested escape hatch instead of discovering after the fact that an apparently reversible Mac action was not. This is especially valuable for file cleanup, bulk edits, messages, and browser submissions.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-terminal → faculty-perception → relay-realtime
- **model tier:** background for impact analysis and undo-plan generation; realtime only for the owner's short approval conversation
- **latency:** Under 3 seconds for a preview on local Mac state; approval execution may take longer but must stream stage status
- **cost:** Usually one cheap local planning call plus one verification call; roughly <$0.02 excluding any large model reasoning. Dominant cost is file/UI inspection, not generation.
- **security:** The preview must redact secrets and message bodies, operate on copies or transaction logs where possible, and never claim reversibility without a concrete rollback artifact. Physical approval remains required for irreversible or externally visible steps. Data inspected leaves the Mac only as minimal hashes/summaries.
- **missing:** A first-class rollback-plan receipt that records the exact inverse operations and retention window; Mac adapters for transactional snapshots of common file and browser actions; Policy data specifying which action classes require this preview

### ""If I start moving around while you're answering, pause at a clean sentence and let me continue when I'm still again.""
- **useful because:** The pendant becomes usable while walking or doing chores: it stops wasting audio when attention is unavailable, resumes without replaying a paragraph, and avoids forcing the owner to grab the device or repeat a question.
- **path:** pendant → relay-realtime → faculty-perception → faculty-action → mac-planner
- **model tier:** Realtime model only for turn segmentation and a short resume cue; IMU classification and buffering are firmware/rule based
- **latency:** Detect movement within 300 ms, stop at the next 20–60 ms audio frame boundary, and resume within 500 ms of stable attention
- **cost:** Near-zero model increment; local IMU features and existing audio buffering dominate. Occasional resume-summary generation is <$0.005 per interruption.
- **security:** Raw motion stays on the pendant; only coarse states (attentive, moving, unknown) are sent. Do not infer location, gait, health, or identity. A deliberate button press must always override the automatic pause.
- **missing:** Firmware motion-context state machine using the owned LSM6DSOX (enable i2c2); A downlink audio pause/resume cursor coordinated with existing delivery ACKs; A relay policy that treats movement as a delivery condition, not as owner intent

### ""Put this link or file on my pendant so I can ask you about it later, even after I close the browser.""
- **useful because:** The owner can bridge a fleeting Mac/browser discovery into a durable, voice-addressable handoff. The pendant can later say what was handed off and why, without keeping a browser session open or exposing credentials to the device.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-action → pendant
- **model tier:** Cheap background model extracts a short title and intent; realtime answers follow-up questions only when asked
- **latency:** Create the handoff in under 2 seconds; later retrieval should be immediate from the relay index
- **cost:** <$0.01 per handoff for title/metadata extraction; dominant cost is optional page text indexing, which should be opt-in and capped
- **security:** Default payload is URL, title, source app, timestamp, and owner note—not page contents or cookies. Private/secret pages require explicit confirmation and should be represented by a redacted label. Signed expiry and deletion controls are mandatory.
- **missing:** A typed relay-to-pendant inbox item for external-reference handoffs; Browser/Mac command to create a handoff from the current tab or selected file without copying secrets; Voice query resolution against handoff IDs and expiry-aware deletion

### ""Before you send anything, tell me exactly which personal facts will leave my Mac, let me remove any of them with the pendant, then send only the approved subset.""
- **useful because:** The owner gets a practical data-loss boundary at the moment it matters: not a global privacy setting, but a field-level redaction step before an email, form, upload, or browser action. This makes the system useful for sensitive work without requiring blind trust in the planner.
- **path:** faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime → pendant → faculty-perception
- **model tier:** A cheap local classifier extracts candidate fields and sensitivity labels; realtime is used only to explain the short diff and collect the owner's decision
- **latency:** Candidate disclosure list in under 1 second for local text and under 3 seconds for a page/form; execution starts only after the pendant decision arrives
- **cost:** <$0.01 per action when classification stays local; the dominant cost is page/file inspection, which must remain bounded
- **security:** Raw secrets and page contents must not be sent to the relay or pendant. The pendant receives opaque field IDs, labels, and lengths, never values. The action executor must cryptographically bind the approved field set to the exact draft and reject any post-approval mutation.
- **missing:** A field-level disclosure manifest and digest bound to the action draft; A pendant UI/gesture for allow-all, deny-all, and selective redaction using the coming wheel/second button; Browser and Mac executors that can submit an approved projection rather than the original full object

### ""When I am in a meeting, let me hand a question to the system without interrupting anyone; bring me the answer privately when it is ready, and discard the meeting context afterward.""
- **useful because:** The owner can use the pendant as a silent research assistant in real time: a discreet gesture marks the question, the Mac/browser researches it in the background, and the answer returns as private audio or a short haptic signal without broadcasting meeting audio or retaining it indefinitely.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Background model for research and synthesis; realtime only for the owner's private follow-up and interruption-safe notification
- **latency:** Capture intent in under 1 second; notify when ready, with a 30-second target for a web-backed answer and immediate acknowledgement via haptic/audio cue
- **cost:** <$0.05 per researched question depending on web depth; browsing and page extraction dominate, not the acknowledgement
- **security:** No open microphone or ambient meeting recording. The pendant transmits only an explicit spoken/typed question after the owner's gesture. Research context is ephemeral with an owner-selected expiry; logged-in browser pages require confirmation and provenance is returned with the answer.
- **missing:** An explicit gesture mode that marks only the next utterance as a private research task; Ephemeral research context with automatic deletion and provenance receipt; A notification channel that can signal readiness without interrupting downlink speech


## Changes it proposed to its own stack

### `firmware` — Integrate the owned LSM6DSOX and DRV2605L on i2c2 into a local attention-and-outcome controller: classify only coarse motion epochs, gate downlink playback at Opus frame boundaries, and render the existing signed action outcome states as distinct haptic patterns while preserving the single LED as fallback. Persist only a tiny state byte, cursor, and event ID; never raw IMU traces.
- **owner gets:** Answers remain intelligible while the owner moves, and action results are felt rather than missed in a noisy room or pocket. It uses parts already bought instead of requiring another gadget.
- effort: Medium firmware work: devicetree and driver integration, a bounded classifier, audio-player hooks, and bench validation against the existing 24 kHz acceptance scripts.  ·  risk: False movement pauses or missed cues; recover by manual button override and timeout to normal playback. Haptic patterns must not imply success without the signed outcome event.
- cost: No new hardware; negligible model/API cost. Adds a few KB flash/RAM and brief I2C activity; motor current is the only meaningful power increase during a cue.  ·  latency: <=300 ms motion response and frame-boundary pause; haptic cue begins within roughly 100 ms of a verified event.
- security: Raw motion remains local. Haptic output is driven only by authenticated outcome envelopes; no action authorization is created by motion.
- depends on: motion_context_safety_gate request resolution; existing tactile_action_outcome_beacon firmware behavior; audio_delivery_ack_queue cursor semantics; i2c2 wiring confirmation on the bench


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-surface capabilities: (1) reversible-action preview with a tested rollback artifact before physical approval, (2) motion-aware interruption/resumption of downlink speech using coarse local IMU state, and (3) browser/file handoff to a durable, voice-addressable pendant reference. Also recorded a firmware integration change, though the recorder flagged it as close to an existing haptic-outcome idea, so it should be treated as an amendment rather than a separate feature. I checked the named /prepare, /approve, and /execute routes via the current describe path; each returned the route's GET 404, so I still need a POST-specific contract check before relying on them.

**Biggest unknown:** The remaining blockers are implementation contracts, not product ideas: the exact POST schemas/receipts for prepare-approve-execute and rollback, firmware access to i2c2/LSM6DSOX/DRV2605L on the bench, and a typed relay inbox item for browser/file handoffs. The browser handoff is connective work across existing routes, but no agent has established the durable typed item or voice lookup semantics.

