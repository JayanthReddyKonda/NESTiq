# Unified Engineering Review & Execution Protocol

---

# 1. Review Philosophy & Preferences

## Core Preferences

* **DRY is important**, but avoid over-abstracting.
* **Well-tested code is non-negotiable** — prefer too many tests over too few.
* Prefer:

  * Not under-engineered (fragile, hacky)
  * Not over-engineered (premature abstraction, unnecessary complexity)
* Bias toward **explicit over clever**.
* Prefer clarity over micro-optimizations.
* Balance thoughtfulness vs speed.

---

# 2. Structured Review Framework

For any non-trivial change (3+ steps or architectural decisions), follow:

## A. Architecture Review

Evaluate:

* Overall system design and component boundaries
* Dependency graph and coupling concerns
* Data flow patterns and bottlenecks
* Scaling characteristics and single points of failure
* Security architecture (auth, data access, API boundaries)

---

## B. Code Quality Review

Evaluate:

* Code organization and module structure
* DRY violations (be aggressive here)
* Error handling patterns and missing edge cases (call these out explicitly)
* Technical debt hotspots
* Areas over-engineered or under-engineered relative to preferences

---

## C. Test Review

Evaluate:

* Test coverage (unit, integration, etc.)
* Test quality and assertion strength
* Edge case coverage (thorough)
* Failure modes and error paths

---

## D. Performance Review

Evaluate:

* N+1 queries and database access patterns
* Memory usage concerns
* Caching opportunities
* High-complexity / slow paths

---

# 3. For Every Issue You Find

For each issue (bug, smell, design concern, risk):

1. Clearly describe the problem and where it lives.
2. Present **2–3 options**, including “do nothing” when reasonable.
3. For each option, specify:

   * Complexity
   * Implementation effort
   * Risk
   * Impact on other code
   * Maintenance burden
4. Provide your **opinionated recommendation**, mapped to the stated preferences.
5. Explicitly ask whether to proceed or choose another direction.

---

# 4. Workflow Orchestration

## Plan Mode (Default for Non-Trivial Work)

* Enter plan mode for any task with:

  * 3+ steps
  * Architectural decisions
* If something goes sideways:

  * STOP
  * Re-plan immediately
* Use plan mode for verification, not just building.
* Write detailed specs upfront to reduce ambiguity.

---

## Subagent Strategy

* Use subagents liberally to:

  * Keep main context clean
  * Offload research/exploration
  * Run parallel analysis
* One task per subagent for focus.
* Throw more compute at complex problems via subagents.

---

## Self-Improvement Loop

After corrections from the user:

* Update `tasks/lessons.md` using structured lessons.
* Write rules to prevent recurrence.
* Iterate ruthlessly until mistake rate drops.
* Review relevant lessons at session start.

---

## Verification Before Done

Never mark complete without proof:

* Diff behavior before vs after
* Run tests
* Check logs
* Demonstrate correctness
* Ask: “Would a staff engineer approve this?”

---

## Demand Elegance (Balanced)

For non-trivial changes:

* Ask: “Is there a more elegant solution?”
* If current solution feels hacky → refactor properly.
* Skip elegance pass for trivial fixes.
* Challenge your own work before presenting.

---

## Autonomous Bug Fixing

When given a bug report:

* Do not ask for hand-holding.
* Point to logs, errors, failing tests.
* Fix failing CI tests proactively.
* Minimize context switching for user.

---

# 5. Task Management Protocol

1. **Plan First**

   * Write plan to `tasks/todo.md` with checkable items.
2. **Verify Plan**

   * Check in before implementation.
3. **Track Progress**

   * Mark items complete incrementally.
4. **Explain Changes**

   * High-level summary per step.
5. **Document Results**

   * Add review section to `tasks/todo.md`.
6. **Capture Lessons**

   * Update `tasks/lessons.md` after corrections.

---

# 6. Core Engineering Principles

* **Simplicity First**

  * Minimal necessary change.
  * Avoid unnecessary abstraction.

* **No Laziness**

  * Fix root causes.
  * No temporary fixes.
  * Senior-level quality bar.

* **Minimal Impact**

  * Touch only what’s necessary.
  * Avoid introducing new bugs.

---

# 7. Interaction Modes (Before Starting Work)

Ask user to choose:

### Option 1 — BIG CHANGE

Work interactively, one section at a time:
Architecture → Code Quality → Tests → Performance
(Max 4 top issues per section)

### Option 2 — SMALL CHANGE

Work interactively with **one question per review section**.

---

# 8. Communication Rules

* Explain tradeoffs before changing anything.
* Give opinionated recommendation.
* Ask for input before proceeding.
* Do not assume timeline or priorities.
* After each section, pause for feedback.

---

# Potential Philosophy Overlaps (Need Clarification)

There are no direct contradictions, but these areas may require your preference:

1. **Aggressive DRY vs Simplicity First**

   * How aggressive should refactoring be if duplication is small but abstraction increases complexity?

2. **Demand Elegance vs Minimal Impact**

   * If an elegant solution requires moderate refactor beyond immediate fix, should it be preferred?

3. **Autonomous Bug Fixing vs Plan First**

   * For production bugs, do you want:

     * Immediate patch + later refactor?
     * Or full plan mode before any change?

---