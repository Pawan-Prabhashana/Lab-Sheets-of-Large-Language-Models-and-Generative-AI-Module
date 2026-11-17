# Discussion Summary

This activity was about using an LLM as a development partner, so the discussion was as much about *how* we worked with the model as about the product itself.

## How we used the LLM as a development partner

- **Problem framing.** We did not start by asking the LLM to design an app. We first made it pressure-test the Busy Student problem until we had three concrete failure points: capture friction, no sense of how long tasks really take, and plans that break the moment one thing goes wrong. Naming those failure points kept the rest of the work focused.
- **Idea generation and pruning.** We used the model to brainstorm a wide set of features and product names, then cut aggressively. An early idea for a social study leaderboard was dropped because it solved a motivation problem rather than the time-management problem in the brief.
- **Microcopy and framing.** The LLM was useful for drafting and tightening the short text shown in the mock-up, such as the morning brief and the at-risk message.

## What we decided, and what the LLM decided

The product decisions were ours. The LLM made the exploration faster and the wording sharper, but the final cut of features, the core Brain-dump, Plan, Adapt loop, and the decision to keep deterministic logic in charge of the timetable and reminders were human choices.

## Key discussion point: where the LLM belongs

The most valuable part of the discussion was deciding where the model should and should not run. The conclusion was that the LLM proposes (parsing, scheduling, explaining) while deterministic code holds the truth (timetable, done state, reminder timing). That boundary is what keeps the product trustworthy, because a hallucinated deadline would be worse than no plan at all.

## Challenges

- Scope creep. The first draft had far too many features, and the discipline was asking of each feature whether it solved the brief's problem.
- Making the prototype show reasoning. We wanted the mock-up to communicate the thinking the LLM does, so we showed concrete artefacts of it, parsed task chips, an at-risk flag, and an explained morning brief, rather than generic placeholder UI.
