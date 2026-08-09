# Harness derivation — mac-vision — round 223

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A durable, prioritized, owner-editable task list for mac-vision to read and act on, including priorities and deadlines."
- **useful because:** Currently mac-vision has no actionable task list or priority queue; such a list enables smart, goal-driven automation on the Mac interface, ensuring the most important work is done first and workflows can be tracked reliably.
- **path:** owner → mac-vision → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** background or scheduled execution
- **cost:** low per update; storage and query cost
- **security:** Must respect owner privacy and edits; self-authored tasks by agents must be clearly marked and separated from owner-entered tasks.
- **missing:** an owner-edit interface or API to submit tasks to the list; priority, deadline, and dependency metadata on tasks; integration with existing memory/facts and routines stores

### "A mac-vision feature to track and log each step's actual UI state post-interaction, allowing the owner to debug and audit complex multi-step workflows on the Mac UI."
- **useful because:** Owners using mac-vision for multi-step workflows need trust that each step was performed correctly. Detailed UI state logging allows diagnosing where a workflow broke and aids recovery or re-run logic, providing better transparency and reliability for automation on the Mac.
- **path:** mac-vision → faculty-judgement → faculty-perception
- **model tier:** gpt-4.1-mini
- **latency:** background logging with low latency impact on main interactions
- **cost:** low to moderate storage and compute per workflow run
- **security:** Logs may contain sensitive UI data; must be securely stored and access-controlled; provide opt-in/opt-out for logging levels.
- **missing:** secure local log storage with owner access controls; UI data minimization and redaction tools; UI state snapshot differencing and timeline replay capability

### "A context-aware proactive helper on mac-vision that tracks live Mac user activity, UI states, and goals to suggest next actions or automation opportunities with minimal owner input."
- **useful because:** Such a helper would enhance owner productivity by anticipating needs, surfacing useful shortcuts, and automating repetitive tasks through Mac UI interaction, while respecting owner preference and control, making the Mac-vision assistant more intelligent and helpful beyond reactive command execution.
- **path:** mac-vision → faculty-judgement → facult-perception → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** low to moderate for real-time suggestions; background for analysis.
- **cost:** moderate compute cost for context processing and output generation.
- **security:** Needs fine-grained control to avoid intrusive or unwanted automation; all data processing remains local to protect privacy; suggestions must be owner-approvable.
- **missing:** real-time access to detailed UI state changes and user activity events; learning model integration for user preference prediction; feedback loop from owner approval or rejection of suggestions


## Changes it proposed to its own stack

### `integration` — Integrate claimed versus actual UI state checking for mac-vision to verify success of each UI interaction step and enable robust workflow resumes or error detection.
- **owner gets:** Ensures reliability and robustness of computer-use workflows by detecting divergence from expected UI states and allowing error recovery or retries, improving trust and reducing frustration from broken automations.
- effort: medium engineering effort to track and compare accessibility trees at each step, implement reporting and handling strategies.  ·  risk: Possible performance overhead and complexity; requires careful UI state snapshot and diff logic.
- cost: moderate increased compute during UI interaction sessions.  ·  latency: small increase per interaction step.
- security: No new data leaves device; all comparison is local.
- depends on: mac-vision enabled; computerUse.loopEnabled granted

### `integration` — Build a feedback pipeline from mac-vision's real-time UI interaction actions back into faculty-judgement and faculty-perception to learn from owner responses and improve suggestion and automation quality on the Mac over time.
- **owner gets:** Allows the system to adapt automation strategies based on actual success and owner approval, making Mac UI automation more personalized, reliable, and less disruptive over time.
- effort: medium to high engineering and machine learning effort to capture and interpret feedback, update models, and route data.  ·  risk: Potential privacy risks if feedback data is not fully local; owner control and transparency must be prioritized.
- cost: moderate compute and storage for feedback processing and model retraining.  ·  latency: mostly background; minimal effect on real-time interaction.
- security: Critical to keep all feedback data local and encrypted; access strictly controlled.
- depends on: mac-vision real-time interaction capability; faculty-judgement access to adapt strategies; faculty-perception for state reading

### `interaction` — Provide a safe undo and manual override interface accessible from the pendant for mac-vision's UI automation steps on the Mac, allowing the owner to quickly halt, rewind, or adjust ongoing workflows.
- **owner gets:** Gives the owner immediate control over powerful automation in case of errors or undesired actions, preventing accidents and building trust in the system's autonomy.
- effort: medium engineering for UI, integration between pendant and mac-vision, and state rollback capabilities.  ·  risk: Undo consistency can be complex with multi-app interactions; must be designed to avoid partial undos causing corrupt states.
- cost: low software; no hardware cost.  ·  latency: low latency required for responsive override.
- security: Must securely authenticate undo commands to prevent misuse.
- depends on: mac-vision enabled workflow control


## What it asked for

_Nothing._
